"""Step 4.6: paired tests on saved test results for the pairs predeclared in lock.json.

Reads only the per-user metrics evaluate_test.py saved; never recommends or reads data.
Per pair: mean difference of per-user metric (A - B) on the shared eligible cohort,
95% and 90% percentile bootstrap CIs over users (1,000 resamples, seed 42; one index
matrix shared by every pair), two-sided Wilcoxon signed-rank p-value, matched-pairs
rank-biserial r, and Holm-adjusted p across all predeclared pairs.
"""

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from musicrec.evaluation.inference import resample_indices
from musicrec.evaluation.paired import paired_comparison

RESAMPLES = 1000
SEED = 42


def per_user(run: Path, model: str, seed: int, k: str, metric: str) -> dict[str, float]:
    """Eligible users' metric at K from one saved test evaluation."""
    path = run / model / f"seed_{seed}" / "evaluation.json"
    evaluation: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return {
        user: float(values["at_k"][k][metric])
        for user, values in evaluation["per_user"].items()
        if values["eligible"]
    }


def holm(p_values: list[float]) -> list[float]:
    """Holm step-down adjustment, monotone and capped at 1."""
    order = np.argsort(p_values)
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(p_values) - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def main() -> None:
    """Write statistics.json beside the test run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-run", type=Path, required=True)
    parser.add_argument("--metric", default="ndcg")
    parser.add_argument("--k", default="10")
    args = parser.parse_args()
    lock = json.loads((args.test_run / "lock.json").read_text(encoding="utf-8"))
    indices: np.ndarray | None = None
    rows = []
    for model_a, model_b in lock["comparison_pairs"]:
        a = per_user(args.test_run, model_a, 42, args.k, args.metric)
        b = per_user(args.test_run, model_b, 42, args.k, args.metric)
        if indices is None:
            indices = resample_indices(len(a), RESAMPLES, SEED)
        rows.append({"a": model_a, "b": model_b, **paired_comparison(a, b, indices)})
    for row, adjusted in zip(rows, holm([r["wilcoxon_p"] for r in rows]), strict=True):
        row["holm_p"] = adjusted
    result = {
        "metric": f"{args.metric}@{args.k}",
        "seed": 42,
        "bootstrap": {
            "resamples": RESAMPLES,
            "seed": SEED,
            "unit": "user",
            "indices": "shared_across_pairs",
        },
        "test": "two_sided_wilcoxon_signed_rank_zero_differences_dropped",
        "adjustment": "holm_over_predeclared_pairs",
        "pairs": rows,
    }
    out = args.test_run / f"statistics_{args.metric}_at_{args.k}.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
