"""E-C: phân tích NDCG@10 kiểm thử theo nhóm người dùng, kèm khoảng tin cậy và kiểm định
(không chạy lại mô hình).

Đọc NDCG@10 kiểm thử theo người dùng của tám mô hình đã khóa (ndcg10_tung_nguoi_dung.csv,
có tổng hợp khớp tệp kiểm thử chính thức) và tập huấn luyện đã khóa.
1. Độ dài lịch sử (số nghệ sĩ huấn luyện mỗi người): "Dưới 40" và "Từ 40 trở lên" (40 là
   giá trị mốt), NDCG@10 trung bình từng mô hình kèm KTC bootstrap 95% mỗi ô.
2. Ba nhóm bằng nhau theo mức ưa chuộng phổ biến (số người nghe trung bình của nghệ sĩ
   người đó nghe, cùng quy tắc với report_ch4_extras.py): KTC 95% mỗi ô và kiểm định
   Kruskal–Wallis giữa ba nhóm cho từng mô hình (Holm trên tám mô hình).
3. M1 − PureSVD trong từng nhóm: KTC bootstrap chung, Wilcoxon, r_rb, Holm trên ba nhóm
   (nhóm thấp là nhóm cần quan tâm).
Bootstrap: 1.000 lần lấy mẫu, hạt giống 42, mỗi nhóm một ma trận chỉ số dùng chung cho
mọi mô hình.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import kruskal

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_e7_topn import runtime  # noqa: E402

from musicrec.evaluation.inference import holm, resample_indices  # noqa: E402
from musicrec.evaluation.paired import mean_interval, paired_comparison  # noqa: E402

TRAIN = Path("outputs/chinh_thuc_cloud_20261026/chuong_3/run/representations/train.parquet")
PER_USER = Path("outputs/chuong_4_bo_sung_2/thong_ke/phan_tich/ndcg10_tung_nguoi_dung.csv")
LOCKED_GROUPS = Path("docs/results/chinh_thuc_cloud_20261026/bo_sung/nhom_uu_pho_bien.csv")
GROUPS = ["Thấp", "Trung bình", "Cao"]


def cells(frame: pd.DataFrame, members: dict[str, list[str]]) -> list[dict[str, Any]]:
    rows = []
    for label, users in members.items():
        indices = resample_indices(len(users), 1000, 42)
        for model in frame.columns:
            rows.append(
                {
                    "nhom": label,
                    "so_nguoi": len(users),
                    "mo_hinh": model,
                    **mean_interval(frame.loc[users, model].to_numpy(), indices),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(PER_USER, dtype={"user_id": str}).set_index("user_id")
    eligible = list(frame.index)
    train = pd.read_parquet(TRAIN)
    train["user_id"] = train.user_id.astype(str)
    length = train.groupby("user_id").size()

    history = {
        "Dưới 40": [u for u in eligible if length[u] < 40],
        "Từ 40 trở lên": [u for u in eligible if length[u] >= 40],
    }
    pd.DataFrame(cells(frame, history)).to_csv(out / "nhom_lich_su_ci.csv", index=False)

    listeners = train.groupby("item_id").user_id.nunique()
    mainstream = train.assign(n=train.item_id.map(listeners)).groupby("user_id").n.mean()
    scores = mainstream.loc[eligible]
    group = pd.qcut(scores.rank(method="first"), 3, labels=GROUPS)
    members = {label: [u for u in eligible if group[u] == label] for label in GROUPS}
    locked = pd.read_csv(LOCKED_GROUPS)
    for label in GROUPS:
        row = locked[locked.nhom == label].iloc[0]
        if len(members[label]) != row.so_nguoi or any(
            abs(frame.loc[members[label], m].mean() - row[m]) > 1e-12 for m in frame.columns
        ):
            raise RuntimeError(f"Group {label} does not reproduce Table 4.10")
    pd.DataFrame(cells(frame, members)).to_csv(out / "bang_4_10_ci.csv", index=False)
    kw = []
    for model in frame.columns:
        result = kruskal(*[frame.loc[members[g], model] for g in GROUPS])
        kw.append({"mo_hinh": model, "H": float(result.statistic), "p": float(result.pvalue)})
    for row, adjusted in zip(kw, holm([r["p"] for r in kw]), strict=True):
        row["holm_p"] = adjusted
    pd.DataFrame(kw).to_csv(out / "bang_4_10_kruskal_wallis.csv", index=False)

    tests = []
    for label in GROUPS:
        users = members[label]
        a = {u: float(frame.loc[u, "M1"]) for u in users}
        b = {u: float(frame.loc[u, "PureSVD"]) for u in users}
        tests.append(
            {
                "nhom": label,
                "a": "M1",
                "b": "PureSVD",
                **paired_comparison(a, b, resample_indices(len(users), 1000, 42)),
            }
        )
    for row, adjusted in zip(tests, holm([r["wilcoxon_p"] for r in tests]), strict=True):
        row["holm_p"] = adjusted
    meta = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "command": sys.argv,
        "per_user_source": str(PER_USER),
        "history_threshold": 40,
        "history_group_sizes": {k: len(v) for k, v in history.items()},
        "mainstream_groups_reproduce_table_4_10": True,
        "m1_minus_pure_svd_by_group_holm_over_3": tests,
        "runtime": runtime(),
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2) + "\n", "utf-8")


if __name__ == "__main__":
    main()
