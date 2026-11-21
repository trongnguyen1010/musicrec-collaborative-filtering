"""Bảng đặt cạnh nhau kiểm định theo cặp đã khóa và bản tính lại với bootstrap dùng chung.

Tệp đã khóa lấy bootstrap riêng cho từng cặp từ một bộ sinh chạy liên tục; tệp mới lấy
mẫu lại mọi cặp của một nhóm bằng một ma trận chỉ số chung. Chênh lệch trung bình và p
Wilcoxon không phụ thuộc bootstrap nên phải khớp tuyệt đối; chỉ khoảng tin cậy được đổi.
Ghi doi_chieu_thong_ke.csv và doi_chieu_thong_ke.json vào --output-dir.
"""

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

LOCKED = Path("docs/results/chinh_thuc_cloud_20261026")
NEW = Path("outputs/chuong_4_bo_sung_2/thong_ke")
FIELDS = ["mean_difference", "wilcoxon_p", "holm_p", "ci95_low", "ci95_high"]
EXTRA = ["ci90_low", "ci90_high", "rank_biserial", "w_plus", "w_minus", "nonzero_differences"]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def table(name: str, old: list[dict[str, Any]], new: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mỗi cặp một dòng; báo lỗi nếu trường không phụ thuộc bootstrap bị lệch."""
    rows = []
    if len(old) != len(new):
        raise ValueError(f"{name}: pair count differs")
    for a, b in zip(old, new, strict=True):
        if (a["a"], a["b"], a.get("n")) != (b["a"], b["b"], b.get("n")):
            raise ValueError(f"{name}: pair order differs")
        for field in ["mean_difference", "wilcoxon_p", "holm_p"]:
            if abs(a[field] - b[field]) > 1e-12 * max(1.0, abs(a[field])):
                raise ValueError(f"{name}: {field} differs for {a['a']} - {a['b']}")
        row: dict[str, Any] = {"bang": name, "a": a["a"], "b": a["b"], "n": a.get("n")}
        row.update({f"{f}_cu": a[f] for f in FIELDS})
        row.update({f"{f}_moi": b[f] for f in FIELDS})
        row.update({f: b[f] for f in EXTRA})
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new", type=Path, default=NEW)
    parser.add_argument("--output-dir", type=Path, default=NEW)
    args = parser.parse_args()
    old_extra = load(LOCKED / "bo_sung/kiem_dinh_bo_sung.json")
    new_extra = load(args.new / "phan_tich/kiem_dinh_bo_sung.json")
    rows = (
        table(
            "4.8_khai_bao_truoc",
            load(LOCKED / "test/statistics_ndcg_at_10.json")["pairs"],
            new_extra["predeclared_pairs_recomputed"],
        )
        + table(
            "4.8_bo_sung",
            old_extra["supplementary_family_pure_svd_vs_others_holm"],
            new_extra["supplementary_family_pure_svd_vs_others_holm"],
        )
        + table(
            "4.11_bien_the_m1",
            load(LOCKED / "bo_sung/m1_kiem_dinh_bien_the.json"),
            load(args.new / "phan_tich/m1_kiem_dinh_bien_the.json"),
        )
        + table(
            "4.15_m2",
            load(LOCKED / "m2/test/statistics_ndcg_at_10.json")["pairs"],
            load(args.new / "m2_test/statistics_ndcg_at_10.json")["pairs"],
        )
    )
    intervals = []
    for model, old in old_extra["mean_ndcg10_bootstrap_ci"].items():
        new = new_extra["mean_ndcg10_bootstrap_ci"][model]
        if abs(old["mean"] - new["mean"]) > 1e-15:
            raise ValueError(f"Mean NDCG@10 differs for {model}")
        intervals.append(
            {
                "model": model,
                "mean": new["mean"],
                "ci95_low_cu": old["ci95_low"],
                "ci95_high_cu": old["ci95_high"],
                "ci95_low_moi": new["ci95_low"],
                "ci95_high_moi": new["ci95_high"],
                "ci90_low": new["ci90_low"],
                "ci90_high": new["ci90_high"],
            }
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output_dir / "doi_chieu_thong_ke.csv", index=False)
    pd.DataFrame(intervals).to_csv(args.output_dir / "doi_chieu_ci_trung_binh.csv", index=False)
    summary = {
        "bootstrap_free_fields_equal": True,
        "pairs_compared": len(rows),
        "max_abs_ci95_shift": max(
            max(
                abs(r["ci95_low_cu"] - r["ci95_low_moi"]),
                abs(r["ci95_high_cu"] - r["ci95_high_moi"]),
            )
            for r in rows
        ),
        "holm_families": new_extra["holm_families"],
        "m1_pure_svd_equivalence": new_extra["m1_pure_svd_equivalence"],
    }
    (args.output_dir / "doi_chieu_thong_ke.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
