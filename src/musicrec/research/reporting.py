"""Build evidence-gated research findings from completed, source-labelled runs."""

import json
from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd

from musicrec.research.io import OUT, ROOT, sha256, track, write_json
from musicrec.research.runner import PUBLISHED, summarize

matplotlib.use("Agg")
import matplotlib.pyplot as plt

TARGET = ROOT / "docs/research"
EXPECTED = {
    ("aiprobs-original", model, index)
    for model in ["pure_dhc", "probs", "aiprobs", "bpr"]
    for index in range(30)
} | {("recbole-bpr-benchmark", "bpr", index) for index in [2020, 2021, 2022]}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def acceptance(records: list[dict[str, Any]]) -> dict[str, Any]:
    """A partial count or stale verification can never report complete reproduction."""
    completed = {
        (r["protocol"], r["model"], r["split_id"]): r
        for r in records
        if r.get("status") == "completed" and r.get("mlflow_run_id")
    }
    metrics = read_json(OUT / "metric_verification.json")
    verified = {
        (r["protocol"], r["model"], r["split_id"]): r.get("mlflow_run_id")
        for r in metrics.get("records", [])
    }
    gates = {
        "all_123_evaluations": set(completed) == EXPECTED,
        "all_123_native_metric_checks": metrics.get("status") == "passed"
        and set(verified) == EXPECTED
        and all(verified.get(key) == r["mlflow_run_id"] for key, r in completed.items()),
        "tiny_reference": read_json(OUT / "tiny_reference_verification.json").get("status")
        == "passed",
        "full_reference": read_json(OUT / "full_reference_verification.json").get("status")
        == "passed",
        "33_split_integrity_checks": len(read_json(OUT / "split_validation.json")) == 33,
        "dataset_analyzed": bool(read_json(OUT / "dataset_analysis.json").get("zip_sha256")),
        "quality_checks": read_json(OUT / "quality_checks.json").get("status") == "passed",
        "repeatability": read_json(OUT / "repeatability.json").get("status") == "passed",
        "bpr_checkpoint_recovery": read_json(OUT / "checkpoint_verification.json").get("status")
        == "passed",
    }
    return {
        "status": "completed" if all(gates.values()) else "incomplete",
        "completed_evaluations": len(completed),
        "required_evaluations": len(EXPECTED),
        "gates": gates,
        "missing": [list(key) for key in sorted(EXPECTED - set(completed))],
    }


def build_report() -> dict[str, Any]:
    """Create tables/figures, then track the exact report and its acceptance evidence."""
    summary = summarize()
    frame = pd.read_csv(TARGET / "results-per-split.csv")
    records = [read_json(path) for path in sorted((OUT / "runs").rglob("result.json"))]
    audit = acceptance(records)
    costs = []
    for result in records:
        if result.get("status") != "completed":
            continue
        native = (
            read_json(
                OUT / "bpr" / result["protocol"] / f"split_{result['split_id']:02}" / "result.json"
            )
            if result["model"] == "bpr"
            else {}
        )
        if native:
            import mlflow

            native_dir = OUT / "bpr" / result["protocol"] / f"split_{result['split_id']:02}"
            if native["factors_sha256"] != sha256(native_dir / "factors.npz"):
                raise ValueError("Native BPR factors changed after training")
            mlflow.set_tracking_uri("sqlite:///" + (OUT / "mlflow.db").as_posix())
            with mlflow.start_run(run_id=result["mlflow_run_id"]):
                mlflow.log_metrics(
                    {
                        "native_bpr_training_and_evaluation_seconds": native["seconds"],
                        "native_bpr_last_epoch": native["last_epoch"],
                    }
                )
                for name in [
                    "result.json",
                    "effective_config.json",
                    "environment.json",
                    "training_source.py.txt",
                    "factors.npz",
                ]:
                    mlflow.log_artifact(str(native_dir / name), artifact_path="native-bpr")
        costs.append(
            {
                "protocol": result["protocol"],
                "model": result["model"],
                "split_id": result["split_id"],
                "fit_or_load_seconds": result["fit_seconds"],
                "native_bpr_training_and_evaluation_seconds": native.get("seconds"),
                "test_seconds": result["test_seconds"],
                "rss_after_evaluation_bytes": result["rss_bytes"],
                "last_epoch": native.get("last_epoch"),
            }
        )
    pd.DataFrame(costs).to_csv(TARGET / "runtime-per-split.csv", index=False)
    supplementary = frame.groupby(["protocol", "model"])[
        ["coverage_all", "coverage_train", "arp", "novelty_smoothed"]
    ].agg(["mean", "std"])
    supplementary.columns = ["_".join(column) for column in supplementary.columns]
    supplementary.reset_index().to_csv(TARGET / "supplementary-metrics.csv", index=False)

    figures = TARGET / "figures"
    figures.mkdir(exist_ok=True)
    metrics = ["recall@10", "mrr@10", "ndcg@10"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout="constrained")
    common = frame[frame.protocol == "aiprobs-original"]
    order = [m for m in ["pure_dhc", "probs", "aiprobs", "bpr"] if m in set(common.model)]
    for ax, metric in zip(axes, metrics, strict=True):
        values = [common.loc[common.model == model, metric] for model in order]
        ax.bar(
            order,
            [v.mean() for v in values],
            yerr=[v.std(ddof=1) for v in values],
            capsize=4,
            color=["#888888", "#4477AA", "#228833", "#CC6677"][: len(order)],
        )
        for index, model in enumerate(order):
            if model != "bpr":
                ax.scatter(index, PUBLISHED[model][metric], marker="x", color="black", zorder=5)
        ax.set_title(metric)
        ax.tick_params(axis="x", rotation=25)
        ax.set_ylim(bottom=0)
    fig.suptitle("Author splits: mean +/- sample SD; x = Deng (2022) Table 2")
    fig.savefig(figures / "reproduction-metrics.png", dpi=180)
    plt.close(fig)

    report = TARGET / "reproduction-report.md"
    lines = [
        "",
        "## Kiểm chứng và điều kiện nghiệm thu",
        "",
        f"Trạng thái nghiệm thu: **{audit['status']}**. "
        f"Có {audit['completed_evaluations']}/123 lượt đánh giá hoàn tất.",
        "",
        "| Kiểm tra | Đạt |",
        "|---|---|",
        *[f"| {name} | {'Có' if passed else 'Chưa'} |" for name, passed in audit["gates"].items()],
        "",
        "![Kết quả trên split tác giả](figures/reproduction-metrics.png)",
        "",
        "Thanh sai số là độ lệch chuẩn mẫu giữa các split, không phải khoảng tin cậy "
        "của 30 dataset độc lập. Dấu x là số xuất bản, có độ chính xác ba chữ số thập phân.",
        "",
        "## Sai khác với số công bố",
        "",
        "| Giao thức | Mô hình | Metric | Công bố | Chạy lại | Chênh lệch |",
        "|---|---|---|---:|---:|---:|",
    ]
    for _, row in summary.dropna(subset=["published"]).iterrows():
        lines.append(
            f"| {row.protocol} | {row.model} | {row.metric} | {row.published:.4f} "
            f"| {row['mean']:.6f} | {row.absolute_gap:+.6f} |"
        )
    lines += [
        "",
        "Các chênh lệch được giữ nguyên. Không chọn siêu tham số bằng test để ép khớp bài báo.",
    ]
    selected = summary[(summary.protocol == "aiprobs-original") & summary.published.notna()]
    if len(selected) == 9 and (selected.runs == 30).all():
        matches = int((selected["mean"].round(3) == selected.published).sum())
        lines += [
            f"Cả ba mô hình đã đủ 30 split; {matches}/9 số trung bình metric chính "
            "khớp số công bố khi làm tròn ba chữ số. Đây là bằng chứng ở mức bảng "
            "kết quả; kiểm chứng thuật toán/evaluator được thực hiện riêng."
        ]
    paired = common.pivot(index="split_id", columns="model", values="ndcg@10")
    if {"aiprobs", "probs"} <= set(paired.columns):
        delta = (paired["aiprobs"] - paired["probs"]).dropna()
        lines += [
            f"Trên {len(delta)} split chung, AIProbS − ProbS có NDCG@10 trung bình "
            f"{delta.mean():+.6f}, độ lệch chuẩn {delta.std(ddof=1):.6f}; "
            f"AIProbS cao hơn trên {int((delta > 0).sum())} split."
        ]
    if {"aiprobs", "bpr"} <= set(paired.columns):
        delta = (paired["aiprobs"] - paired["bpr"]).dropna()
        lines += [
            f"Trên {len(delta)} split chung, AIProbS − BPR có NDCG@10 trung bình "
            f"{delta.mean():+.6f}, độ lệch chuẩn {delta.std(ddof=1):.6f}; "
            f"AIProbS cao hơn trên {int((delta > 0).sum())} split."
        ]
    benchmark = summary[summary.protocol == "recbole-bpr-benchmark"]
    if len(benchmark) == 5 and (benchmark.runs == 3).all():
        lines += [
            "",
            "**Mức xác nhận BPR benchmark:** đã chạy đủ ba seed theo giao thức khôi phục, "
            "nhưng các số mới không khớp bảng công bố. Split, thứ tự ID và lock môi trường "
            "gốc chưa được cung cấp đầy đủ; chưa xác nhận tái hiện chính xác bảng benchmark. "
            "Trạng thái `completed` ở đây xác nhận đủ khối lượng chạy/kiểm chứng đã chốt. "
            "Cần bằng chứng split và môi trường gốc để xác định nguyên nhân chênh lệch. "
            "Không diễn giải điểm cao hơn thành cải tiến thuật toán BPR.",
        ]
    lines += [
        "",
        "## Chi phí và phân tích bổ sung",
        "",
        "[Chi phí từng lượt](runtime-per-split.csv) tách thời gian nạp factor của adapter "
        "khỏi thời gian huấn luyện và đánh giá RecBole. Không dùng thời gian nạp factor để "
        "kết luận BPR huấn luyện nhanh hơn diffusion. RSS được đo sau đánh giá, không phải "
        "peak RAM; giới hạn này được giữ trong tên cột.",
        "Thời gian native BPR là thời gian invocation cuối. Nếu có lượt tiếp tục, "
        "thời gian invocation trước được ghi riêng trong "
        "`outputs/research/resume_events.json`, không cộng ngầm vào cột này.",
        "",
        "[Coverage, ARP, novelty](supplementary-metrics.csv) được tính trên cùng ranking "
        "và popularity của train. Coverage có hai mẫu số: catalog đầy đủ và item có train. "
        "Novelty dùng làm trơn cộng một; không phải metric công bố của Deng (2022).",
        "",
        "| Giao thức | Mô hình | Coverage catalog | ARP | Novelty (bit) |",
        "|---|---|---:|---:|---:|",
        *[
            f"| {row['protocol']} | {row['model']} | {row['coverage_all_mean']:.2%} | "
            f"{row['arp_mean']:.2f} | {row['novelty_smoothed_mean']:.3f} |"
            for _, row in supplementary.reset_index().iterrows()
        ],
        "",
        "Coverage là độ phủ catalog, chưa đo đa dạng ngữ nghĩa trong từng danh sách. "
        "ARP thấp hoặc novelty cao cần được đọc cùng Recall/NDCG: Pure-DHC có ít hit "
        "dù ARP thấp. Các đối chứng đã chạy cung cấp căn cứ thiết kế trade-off cho M1.",
        "",
        "## Đề xuất cập nhật khóa luận",
        "",
        "1. Giữ ProbS/AIProbS và BPR làm đối chứng đã kiểm chứng cho artist Top-N. "
        "Pure-DHC hữu ích như ablation, độ chính xác thấp không đủ làm baseline mạnh.",
        "2. Thống nhất giao thức thesis 80/10/10 trong ADR trước khi thay scaffold "
        "leave-one-out; báo cáo rõ warm-start, catalog và user bị loại.",
        "3. M1 nên đo đồng thời NDCG/Recall, coverage và ARP trên cùng split; "
        "không áp item-min-5 rồi diễn giải long-tail như dữ liệu gốc.",
        "4. M2 phải xử lý artist ID tag không có metadata và giới hạn 68,81% độ phủ "
        "tag trong catalog. Timestamp tag không cung cấp lịch sử nghe theo thời gian. "
        "Tránh sử dụng tag phát sinh sau mốc train khi giao thức tương lai có mốc thời gian.",
        "5. Kiểm tra nhóm lịch sử ngắn bằng thiết kế thí nghiệm rõ ràng: 1.829/1.892 user "
        "đã có đúng 50 artist; các kết luận cold-user từ dữ liệu tự nhiên sẽ rất hạn chế.",
        "",
        "Bản DOCX gốc được giữ nguyên. Pipeline ứng dụng, M1/M2 và các baseline "
        "thesis còn lại không nằm trong nghiệm thu tái hiện lần này.",
    ]
    resume_events = read_json(OUT / "resume_events.json")
    if isinstance(resume_events, list):
        for event in resume_events:
            lines += [
                "",
                f"Tiếp tục thực tế: {event['protocol']}/split {event['split_id']} "
                f"từ checkpoint epoch {event['checkpoint_epoch']}; invocation trước "
                f"đã ghi nhận {event['prior_invocation_reported_seconds']:.2f} giây.",
            ]
    hardware = read_json(OUT / "hardware.json")
    if hardware:
        lines += [
            "",
            f"Máy chạy CPU: {hardware['cpu_physical']} core vật lý, "
            f"{hardware['cpu_logical']} luồng logic, "
            f"{hardware['ram_bytes'] / 2**30:.2f} GiB RAM; Torch dùng 4 luồng. "
            "Lock môi trường chính: `uv.lock`; môi trường legacy: "
            "`requirements/legacy-reproduction.txt`.",
        ]
    report.write_text(
        report.read_text(encoding="utf-8") + "\n".join(lines) + "\n", encoding="utf-8"
    )
    write_json(OUT / "acceptance.json", audit)
    run_id = track(
        "research-report",
        {"status": audit["status"], "required_evaluations": 123},
        {"completed_evaluations": float(audit["completed_evaluations"])},
        [
            report,
            TARGET / "results-summary.csv",
            TARGET / "results-per-split.csv",
            TARGET / "runtime-per-split.csv",
            TARGET / "supplementary-metrics.csv",
            figures / "reproduction-metrics.png",
            OUT / "acceptance.json",
            ROOT / "uv.lock",
            ROOT / "requirements/legacy-reproduction.txt",
        ],
    )
    audit.update({"mlflow_run_id": run_id, "report_sha256": sha256(report)})
    write_json(OUT / "acceptance.json", audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return audit
