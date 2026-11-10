"""E-P: Popularity ranked by distinct train listeners c_i, validation only.

The locked Popularity (sum of log2(1 + count)) is rescored too and must reproduce the
Chapter 4 validation NDCG@10; nothing is selected or locked.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_e7_topn import grouped, load_train, runtime  # noqa: E402

from musicrec.evaluation.ranking import evaluate_ranking  # noqa: E402
from musicrec.recommenders.popularity import PopularityRecommender  # noqa: E402

SOURCE = Path("outputs/chinh_thuc_cloud_20261026/chuong_3/run/representations")
METRICS = ["precision", "recall", "ndcg", "catalog_coverage", "gini", "arp", "novelty", "ild"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    interactions, histories = load_train(SOURCE)
    validation = grouped(pd.read_parquet(SOURCE / "validation.parquet"))
    targets = {u: validation.get(u, set()) for u in histories}
    users = sorted(histories, key=int)
    rows = []
    for score in ["log_count_sum", "listeners"]:
        model = PopularityRecommender(score).fit(interactions)
        lists = {u: [r.item_id for r in model.recommend(u, 20, histories[u])] for u in users}
        result = evaluate_ranking(lists, targets, histories, ks=(5, 10, 20))
        rows.append({"score": score, **{m: result["at_k"]["10"][m] for m in METRICS}})
        print(json.dumps(rows[-1]), flush=True)
    pd.DataFrame(rows).to_csv(args.output_dir / "popularity_validation.csv", index=False)
    meta = {"created_at_utc": datetime.now(UTC).isoformat(), "command": sys.argv, **runtime()}
    (args.output_dir / "metrics.json").write_text(json.dumps(meta, indent=2) + "\n", "utf-8")


if __name__ == "__main__":
    main()
