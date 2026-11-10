"""E-C: user-group analyses of test NDCG@10 with intervals and tests (no model is rerun).

Reads the per-user test NDCG@10 of the eight locked models (ndcg10_tung_nguoi_dung.csv,
whose aggregates match the official test file) and the locked train split.
1. History length (train artists per user): "Dưới 40" and "Từ 40 trở lên" (40 is the
   modal train length), mean NDCG@10 per model with a 95% bootstrap CI per cell.
2. Table 4.10 groups (three equal-size groups by mainstreaminess = mean train listeners
   of the user's artists, same rule as report_ch4_extras.py): 95% CI per cell and a
   Kruskal-Wallis test across the three groups per model (Holm over the eight models).
3. M1 - PureSVD within each mainstreaminess group: shared-bootstrap CI, Wilcoxon,
   rank-biserial r, Holm over the three groups (the low group is the one of interest).
Bootstrap: 1,000 resamples, seed 42, one index matrix per group shared by all models.
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
