"""Dựng lại các lần chạy xác thực đã khóa của UserCF, ItemCF và SVD trên máy này (báo cáo v17).

Lần chạy chính thức (chinh_thuc_cloud_20261026) chỉ giữ chỉ số kiểm thử tổng hợp trên máy
này. Để vẽ hình theo từng người dùng, các cấu hình đã chọn trong tuning_summary.json chính
thức được học lại ở đây với hạt giống 42 qua cùng các trình chạy. Không chọn lại gì: cấu
hình chỉ được đọc, không dò. Lần chạy SVD thứ hai với patience bằng max_epochs ghi đủ
đường học 100 vòng (Hình 4.3).
"""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from math import fsum  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tune_validation import BASE_CONFIGS, ROOT, name_of, run  # noqa: E402

from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.ranking import ndcg_at_k, proxy_rmse  # noqa: E402
from musicrec.recommenders.svd import SVDRecommender  # noqa: E402

MODELS = ["user_cf", "item_cf", "svd"]


def main() -> None:
    """Học lại từng cấu hình đã khóa, rồi đường học SVD dài, và so NDCG xác thực."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--representations-run", type=Path, required=True)
    parser.add_argument("--tuning-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-curve", action="store_true")
    parser.add_argument("--curve-only", action="store_true")
    args = parser.parse_args()
    summary = json.loads(args.tuning_summary.read_text(encoding="utf-8"))
    source, root = args.representations_run.resolve(), args.output_dir.resolve()
    report: dict[str, Any] = {}
    if args.curve_only:
        report = json.loads((root / "rebuild_report.json").read_text(encoding="utf-8"))
    for model in [] if args.curve_only else MODELS:
        base = yaml.safe_load((ROOT / BASE_CONFIGS[model]).read_text(encoding="utf-8"))
        selected = summary[model]["selected"]
        out = root / model / name_of(model, selected)
        row = run(model, {**base, **selected}, out, source, 42)
        official = summary[model]["selected_ndcg_at_10_seed42"]
        report[model] = {
            **row,
            "official_ndcg_at_10": official,
            "equal": row["ndcg_at_10"] == official,
        }
        print(json.dumps(report[model]), flush=True)
    (root / "rebuild_report.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    if not args.skip_curve:
        curve = svd_curve(source, summary["svd"]["selected"])
        out = root / "svd_curve"
        out.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(curve).to_csv(out / "learning_curve.csv", index=False, lineterminator="\n")
        official = pd.read_csv(
            root / "svd" / name_of("svd", summary["svd"]["selected"]) / "learning_curve.csv"
        )
        head = pd.read_csv(out / "learning_curve.csv").head(len(official))
        report["svd_curve_matches_patience_run"] = bool(
            (
                head.validation_ndcg_at_10.to_numpy() == official.validation_ndcg_at_10.to_numpy()
            ).all()
            and (head.train_proxy_rmse.to_numpy() == official.train_proxy_rmse.to_numpy()).all()
        )
        (root / "rebuild_report.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
        print("curve matches the patience-5 run:", report["svd_curve_matches_patience_run"])


def svd_curve(source: Path, selected: dict[str, Any]) -> list[dict[str, Any]]:
    """Học SVD đã khóa đủ 100 vòng, ghi NDCG@10 xác thực và RMSE điểm đại diện mỗi vòng.

    Cùng hàm gọi lại như run_baseline.py (NDCG@10 xác thực, chỉ loại tập huấn luyện); patience
    đặt bằng max_epochs để đường học không bị cắt. Chỉ đọc tập xác thực.
    """
    base = yaml.safe_load((ROOT / BASE_CONFIGS["svd"]).read_text(encoding="utf-8"))
    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")
    mappings = json.loads((source / "id_mappings.json").read_text(encoding="utf-8"))
    catalog = set(mappings["item_id_to_index"])
    histories = {str(u): {str(i) for i in g.item_id} for u, g in train.groupby("user_id")}
    targets = {user: set() for user in histories} | {
        str(u): {str(i) for i in g.item_id} for u, g in validation.groupby("user_id")
    }
    known = validation[validation.item_index.notna()]
    rows = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count), float(r.proxy_score))
        for r in train.itertuples(index=False)
    ]
    rmse: list[float] = []

    def callback(current: SVDRecommender) -> float:
        values = [
            ndcg_at_k([r.item_id for r in current.recommend(u, 10, histories[u])], rel, 10)
            for u in sorted(histories, key=int)
            if (rel := targets[u] & catalog)
        ]
        predicted = [current.predict(str(r.user_id), str(r.item_id)) for r in known.itertuples()]
        rmse.append(proxy_rmse(known.proxy_score.tolist(), predicted))
        score = fsum(values) / len(values)
        print(json.dumps({"epoch": len(rmse), "ndcg": score, "val_rmse": rmse[-1]}), flush=True)
        return score

    model = SVDRecommender(
        latent_factors=selected["latent_factors"],
        learning_rate=selected["learning_rate"],
        regularization=selected["regularization"],
        max_epochs=base["max_epochs"],
        patience=base["max_epochs"],
        seed=42,
        init_std=base["init_std"],
    )
    model.fit(rows, validation_score=callback)
    return [
        {**point, "validation_proxy_rmse": rmse[n]} for n, point in enumerate(model.learning_curve)
    ]


if __name__ == "__main__":
    main()
