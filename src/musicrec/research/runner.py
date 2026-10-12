"""Shared full-catalog evaluator, resumable runs and source-labelled result tables."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
import psutil
import torch

from musicrec.evaluation.ranking import (
    hit_at_k,
    mrr_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)
from musicrec.recommenders.bpr import BPRRecommender
from musicrec.recommenders.diffusion import DiffusionRecommender, Variant
from musicrec.research.dataset import canonical_pairs
from musicrec.research.io import OUT, ROOT, SPLITS, Split, provenance, sha256, track, write_json

METRIC_FUNCTIONS = {
    "recall@10": recall_at_k,
    "mrr@10": mrr_at_k,
    "ndcg@10": ndcg_at_k,
    "hit@10": hit_at_k,
    "precision@10": precision_at_k,
}
PUBLISHED = {
    "pure_dhc": {"recall@10": 0.004, "mrr@10": 0.006, "ndcg@10": 0.003},
    "probs": {"recall@10": 0.170, "mrr@10": 0.308, "ndcg@10": 0.166},
    "aiprobs": {"recall@10": 0.184, "mrr@10": 0.340, "ndcg@10": 0.183},
    "bpr": {
        "recall@10": 0.1761,
        "mrr@10": 0.3026,
        "ndcg@10": 0.1674,
        "hit@10": 0.5573,
        "precision@10": 0.0858,
    },
}


def evaluate(
    model: DiffusionRecommender | BPRRecommender,
    split: Split,
    part: Literal["validation", "test"],
    batch_size: int = 64,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Use the native torch.topk tie policy on full scores and exported native masks."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    users = split.valid_users if part == "validation" else split.test_users
    history = split.valid_history if part == "validation" else split.test_history
    positives = split.validation if part == "validation" else split.test
    truth = {int(user): set(positives[positives[:, 0] == user, 1].tolist()) for user in users}
    seen = {int(user): history[history[:, 0] == user, 1] for user in users}
    if len(users) == 0:
        raise ValueError("No eligible evaluation user")
    rankings = []
    for start in range(0, len(users), batch_size):
        batch = users[start : start + batch_size]
        scores = model.score_batch(batch)
        if not np.isfinite(scores).all():
            raise ValueError("Nonfinite scores before history masking")
        scores[:, 0] = -np.inf
        for row, user in enumerate(batch):
            scores[row, seen[int(user)]] = -np.inf
        if (np.isfinite(scores).sum(axis=1) < 10).any():
            raise ValueError("Fewer than ten eligible candidates")
        top = torch.topk(torch.from_numpy(scores), 10, dim=-1).indices.numpy()
        rankings.append(top)
    ranking = np.concatenate(rankings)
    per_user = np.asarray(
        [
            [
                function([str(x) for x in ranked], {str(x) for x in truth[int(user)]}, 10)
                for function in METRIC_FUNCTIONS.values()
            ]
            for user, ranked in zip(users, ranking, strict=True)
        ]
    )
    result = {
        name: float(value)
        for name, value in zip(METRIC_FUNCTIONS, per_user.mean(axis=0), strict=True)
    }
    popularity = np.asarray(split.matrix().sum(axis=0)).ravel()
    unique = np.unique(ranking)
    trained = popularity > 0
    result.update(
        {
            "coverage_all": len(unique) / (len(split.items) - 1),
            "coverage_train": float(trained[unique].sum() / trained.sum()),
            "arp": float(popularity[ranking].mean()),
            "novelty_smoothed": float(
                -np.log2((popularity[ranking] + 1) / (len(split.users))).mean()
            ),
        }
    )
    return result, {
        "users": users,
        "ranking": ranking,
        "per_user_metrics": per_user,
        "metric_names": np.asarray(list(METRIC_FUNCTIONS)),
        "ground_truth_count": np.asarray([len(truth[int(user)]) for user in users]),
    }


def run(protocol: str, model_name: str, split_id: int, batch_size: int = 64) -> dict[str, Any]:
    """Run one fixed configuration, logging validation then a single test evaluation."""
    if protocol not in {"aiprobs-original", "recbole-bpr-benchmark"}:
        raise ValueError("Thesis experiments are not part of the reproduction")
    if model_name not in {"pure_dhc", "probs", "aiprobs", "bpr"}:
        raise ValueError("Unknown model")
    if protocol == "recbole-bpr-benchmark" and model_name != "bpr":
        raise ValueError("The secondary report target is BPR only")
    torch.set_num_threads(4)
    path = SPLITS / protocol / f"split_{split_id:02}.npz"
    destination = OUT / "runs" / protocol / model_name / f"split_{split_id:02}"
    destination.mkdir(parents=True, exist_ok=True)
    result_path = destination / "result.json"
    signature_files = [
        ROOT / "src/musicrec/recommenders/diffusion.py",
        ROOT / "src/musicrec/recommenders/bpr.py",
        ROOT / "src/musicrec/evaluation/ranking.py",
        ROOT / "src/musicrec/research/runner.py",
        ROOT / "configs/reproduction.yaml",
    ]
    signature = hashlib.sha256(
        json.dumps(
            {str(p.relative_to(ROOT)): sha256(p) for p in signature_files}, sort_keys=True
        ).encode()
    ).hexdigest()
    if result_path.exists():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if (
            result.get("status") == "completed"
            and result["split_sha256"] == sha256(path)
            and result.get("implementation_sha256") == signature
            and result.get("mlflow_run_id")
        ):
            return dict(result)
    split = Split.load(path)
    diagnostics = split.validate(canonical_pairs())
    config = {
        "protocol": protocol,
        "model": model_name,
        "split_id": split_id,
        "seed": split_id if protocol == "recbole-bpr-benchmark" else 2020,
        "k": 10,
        "batch_size": batch_size,
        "binary": True,
        "filter": None,
        "ranking": "full catalog; torch.topk CPU; author ID order; padding excluded",
        "test_history": "train+validation",
        "refit_train_validation": False,
    }
    write_json(destination / "config.json", config)
    source = provenance()
    write_json(destination / "provenance.json", source)
    started = time.perf_counter()
    model: DiffusionRecommender | BPRRecommender
    if model_name == "bpr":
        bpr_dir = OUT / "bpr" / protocol / f"split_{split_id:02}"
        trained = json.loads((bpr_dir / "result.json").read_text(encoding="utf-8"))
        if trained["status"] != "completed" or trained["split_sha256"] != sha256(path):
            raise ValueError("BPR artifact has not completed training on this split")
        if trained.get("factors_sha256") != sha256(bpr_dir / "factors.npz"):
            raise ValueError("BPR factor checksum mismatch")
        model = BPRRecommender(bpr_dir / "factors.npz")
        if model.user_ids != split.users or model.item_ids != split.items:
            raise ValueError("BPR catalog mismatch")
    else:
        variant: Variant = model_name  # type: ignore[assignment]
        model = DiffusionRecommender(variant, split.users, split.items).fit_matrix(split.matrix())
    fit_seconds = time.perf_counter() - started
    validation, _ = evaluate(model, split, "validation", batch_size)
    test_started = time.perf_counter()
    metrics, ranking = evaluate(model, split, "test", batch_size)
    np.savez_compressed(destination / "ranking.npz", **ranking)
    result = {
        "status": "evaluated",
        "implementation_sha256": signature,
        **config,
        "split_sha256": sha256(path),
        "dataset_sha256": sha256(ROOT / "data/raw/hetrec2011-lastfm-2k.zip"),
        "validation": validation,
        "test": metrics,
        "diagnostics": diagnostics,
        "fit_seconds": fit_seconds,
        "test_seconds": time.perf_counter() - test_started,
        "total_seconds": time.perf_counter() - started,
        "rss_bytes": psutil.Process().memory_info().rss,
        "source_provenance": source,
    }
    write_json(result_path, result)
    run_id = track(
        f"{protocol}/{model_name}/{split_id}",
        {
            **config,
            "split_sha256": result["split_sha256"],
            "git_sha": source["git_sha"],
            "code_sha256": source["code_sha256"],
        },
        {**metrics, "fit_seconds": fit_seconds, "test_seconds": result["test_seconds"]},
        [
            result_path,
            destination / "config.json",
            destination / "provenance.json",
            destination / "ranking.npz",
            Path(source["source_snapshot"]),
        ],
    )
    result["mlflow_run_id"] = run_id
    result["status"] = "completed"
    write_json(result_path, result)
    print(f"COMPLETE {protocol}/{model_name}/{split_id}: {metrics}", flush=True)
    return result


def summarize() -> pd.DataFrame:
    """Generate honest partial/completed tables and publication gaps without pooling protocols."""
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((OUT / "runs").rglob("result.json"))
    ]
    flat = [
        {
            "protocol": r["protocol"],
            "model": r["model"],
            "split_id": r["split_id"],
            "mlflow_run_id": r.get("mlflow_run_id"),
            "total_seconds": r["total_seconds"],
            **r["test"],
        }
        for r in records
        if r["status"] == "completed"
    ]
    if not flat:
        raise ValueError("No completed experiment")
    frame = pd.DataFrame(flat)
    target = ROOT / "docs/research"
    target.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target / "results-per-split.csv", index=False)
    rows = []
    for (protocol, model), group in frame.groupby(["protocol", "model"]):
        for metric in METRIC_FUNCTIONS:
            published = PUBLISHED[str(model)].get(metric)
            if protocol == "aiprobs-original" and model == "bpr":
                published = None
            value = group[metric].mean()
            rows.append(
                {
                    "protocol": protocol,
                    "model": model,
                    "metric": metric,
                    "runs": len(group),
                    "mean": value,
                    "std": group[metric].std(ddof=1),
                    "published": published,
                    "absolute_gap": value - published if published is not None else None,
                    "relative_gap": (value / published - 1) if published else None,
                }
            )
    summary = pd.DataFrame(rows)
    summary.to_csv(target / "results-summary.csv", index=False)
    lines = [
        "# Báo cáo tái hiện HetRec LastFM",
        "",
        "Tái hiện một phần thực nghiệm LastFM trong Deng (2022), gồm Pure-DHC, "
        "ProbS và AIProbS trên 30 split công khai; đối chứng BPR dựa trên benchmark "
        "RecBole-GNN. Trạng thái thực tế được xác định bởi số lượt hoàn tất dưới đây.",
        "",
        "Nguồn chính: [Deng (2022), Bảng 2](https://doi.org/10.1038/s41598-022-21607-4). "
        "Nguồn BPR: [benchmark LastFM](https://github.com/RUCAIBox/RecBole-GNN/blob/"
        "9092ac4452224c9c1754d8c4b89b4eb2abaaf71f/results/social/lastfm.md).",
        "",
        "| Giao thức | Mô hình | Hoàn tất / yêu cầu | Recall@10 | MRR@10 | NDCG@10 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    complete = True
    for protocol, model in [
        ("aiprobs-original", m) for m in ["pure_dhc", "probs", "aiprobs", "bpr"]
    ] + [("recbole-bpr-benchmark", "bpr")]:
        group = frame[(frame.protocol == protocol) & (frame.model == model)]
        expected = 3 if protocol == "recbole-bpr-benchmark" else 30
        complete &= len(group) == expected
        values = [
            f"{group[m].mean():.6f} ± {group[m].std(ddof=1):.6f}" if len(group) else "—"
            for m in ["recall@10", "mrr@10", "ndcg@10"]
        ]
        lines.append(
            f"| {protocol} | {model} | {len(group)}/{expected} | " + " | ".join(values) + " |"
        )
    lines += [
        "",
        "**Trạng thái: "
        + (
            "đủ 123 lượt đánh giá đã chọn."
            if complete
            else "chưa tái hiện hoàn tất; còn thiếu các lượt trong bảng."
        )
        + "**",
        "",
        "Số công bố, độ lệch tuyệt đối/tương đối và độ lệch chuẩn được xuất trong "
        "`results-summary.csv`; `results-per-split.csv` truy tới MLflow run từng lượt. "
        "Không gộp hai giao thức hoặc coi 30 split là 30 dataset độc lập.",
        "",
        "## Giới hạn và điều chỉnh",
        "",
        "- AIProbS dùng nhánh DHC/cosine/max-min+mean của mã tác giả. Công thức (4) "
        "in trong bài và phép chia trọng số cho tổng trong code khác nhau; phép chia "
        "trong mã được giữ làm chuẩn tái hiện code.",
        "- Python/PyTorch hiện đại và lưu trữ thưa thay thế cấp phát ma trận đồ thị đặc. "
        "Kiểm chứng tham chiếu được lưu riêng; không gọi bản vá bộ nhớ là chạy nguyên bản.",
        "- BPR benchmark dùng split mới từ dữ liệu chính thức, seed 2020/2021/2022. "
        "Không có hash split hoặc môi trường đầy đủ của kết quả công bố để xác nhận "
        "tái hiện bit-for-bit.",
        "- Coverage, ARP và novelty là phân tích bổ sung. ARP dùng số người nghe trong "
        "train; novelty = mean[-log2((listeners+1)/(users+1))], loại padding khỏi users.",
        "- Đồng điểm dùng torch.topk CPU trên thứ tự ID nguồn trong thí nghiệm; "
        "API recommend dùng thứ tự ID ổn định để phục vụ ứng dụng.",
        "",
        "## Liên hệ với khóa luận",
        "",
        "Các kết quả này kiểm chứng nền tảng đánh giá implicit Top-N. Giai đoạn M1 "
        "cần so sánh độ chính xác cùng coverage/ARP và M2 cần kiểm soát rò rỉ tag. "
        "Không chuyển đổi trực tiếp số bài báo sang giao thức min-user-5, proxy rating "
        "hoặc warm-start của khóa luận. Bản DOCX hiện tại được giữ nguyên.",
    ]
    (target / "reproduction-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary
