"""Steps 4.7-4.8 from saved outputs only: test NDCG@10 by train history group, and cost.

History groups follow summarize_history_groups: below, at and above the train-only modal
history length. Costs are read from the selected runs' metrics.json (single BLAS thread)
and the saved model directories. Nothing is refit, recommended or re-evaluated.
"""

import argparse
import json
from math import fsum
from pathlib import Path
from statistics import multimode
from typing import Any

import pandas as pd

MODELS = ["random", "popularity", "user_cf", "item_cf", "svd", "pure_svd", "m1", "implicit_als"]


def size(path: Path) -> int:
    """Total bytes of a file or directory tree."""
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def main() -> None:
    """Write history_groups.csv and cost.csv beside the test run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-run", type=Path, required=True)
    parser.add_argument("--split-run", type=Path, required=True)
    parser.add_argument("--baselines", type=Path, required=True)
    parser.add_argument("--m1-run", type=Path, required=True)
    args = parser.parse_args()
    train = pd.read_parquet(args.split_run / "train.parquet")
    lengths = {str(u): int(n) for u, n in train.groupby("user_id").size().items()}
    mode = min(multimode(lengths.values()))
    group_of = {
        u: "below_mode" if n < mode else "at_mode" if n == mode else "above_mode"
        for u, n in lengths.items()
    }
    rows: list[dict[str, Any]] = []
    for model in MODELS:
        path = args.test_run / model / "seed_42" / "evaluation.json"
        per_user = json.loads(path.read_text(encoding="utf-8"))["per_user"]
        for group in ["below_mode", "at_mode", "above_mode"]:
            values = [
                v["at_k"]["10"]["ndcg"]
                for u, v in per_user.items()
                if group_of[u] == group and v["eligible"]
            ]
            rows.append(
                {
                    "model": model,
                    "group": group,
                    "mode_history_length": mode,
                    "users_total": sum(g == group for g in group_of.values()),
                    "users_eligible": len(values),
                    "ndcg_at_10": fsum(values) / len(values) if values else None,
                }
            )
    pd.DataFrame(rows).to_csv(args.test_run / "history_groups.csv", index=False)

    lock = json.loads((args.test_run / "lock.json").read_text(encoding="utf-8"))
    cost: list[dict[str, Any]] = []
    for model in MODELS:
        if model == "m1":
            continue
        if model in ("random", "popularity"):
            run = args.baselines / model
            stored = run / "model.json"
        else:
            run = Path(lock["models"][model]["runs"]["42"]["path"])
            stored = run / "model"
        timing = json.loads((run / "metrics.json").read_text(encoding="utf-8"))["timing_seconds"]
        cost.append(
            {
                "model": model,
                "fit_seconds": timing["fit"],
                "recommend_mean_ms_per_user": timing["recommend_mean_per_user"] * 1000,
                "recommend_p95_ms_per_user": timing["recommend_p95_per_user"] * 1000,
                "model_bytes": size(stored),
            }
        )
    resources = json.loads((args.m1_run / "metrics.json").read_text(encoding="utf-8"))["resources"]
    users = len(lengths)
    cost.append(
        {
            "model": "m1",
            "fit_seconds": 0.0,
            "candidate_mean_ms_per_user": resources["42/candidates"]["mean_per_user_seconds"]
            * 1000,
            "rerank_mean_ms_per_user": resources["42/lambda_0.75_beta_0.5"]["greedy_seconds"]
            / users
            * 1000,
            "model_bytes": size(args.m1_run / "seed_42" / "selected_model"),
        }
    )
    pd.DataFrame(cost).to_csv(args.test_run / "cost.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(pd.DataFrame(cost).to_string(index=False))


if __name__ == "__main__":
    main()
