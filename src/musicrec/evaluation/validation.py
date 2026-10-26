"""Summarize verified validation evaluations without changing their cohorts or catalog."""

from math import fsum
from statistics import multimode, stdev
from typing import Any


def summarize_history_groups(
    evaluation: dict[str, Any], history_lengths: dict[str, int]
) -> dict[str, Any]:
    """Group by the train-only modal history length, retaining empty eligible groups.

    Reuse per-user accuracy/ILD already measured on the full train catalog.
    Evaluating a filtered train table would incorrectly change that catalog.
    """
    users = evaluation["per_user"]
    if evaluation["split"] != "validation" or set(users) != set(history_lengths):
        raise ValueError("Expected validation results for exactly the train users")
    if not history_lengths or any(type(n) is not int or n <= 0 for n in history_lengths.values()):
        raise ValueError("Expected positive integer train history lengths")
    threshold = min(multimode(list(history_lengths.values())))
    groups: dict[str, Any] = {}
    for label, members in {
        "below_mode": [u for u, n in history_lengths.items() if n < threshold],
        "at_mode": [u for u, n in history_lengths.items() if n == threshold],
        "above_mode": [u for u, n in history_lengths.items() if n > threshold],
    }.items():
        eligible = [users[u] for u in members if users[u]["eligible"]]
        at_k = {}
        for k in evaluation["at_k"]:
            values = [u["at_k"][k] for u in eligible]
            diversities = [v["ild"] for v in values if v["ild"] is not None]
            at_k[k] = {
                **{
                    metric: fsum(v[metric] for v in values) / len(values) if values else None
                    for metric in ["precision", "recall", "ndcg"]
                },
                "ild": fsum(diversities) / len(diversities) if diversities else None,
                "ild_users": len(diversities),
            }
        groups[label] = {
            "users_total": len(members),
            "users_eligible": len(eligible),
            "users_without_catalog_targets": len(members) - len(eligible),
            "targets_total": sum(users[u]["targets_total"] for u in members),
            "targets_in_catalog": sum(users[u]["targets_in_catalog"] for u in members),
            "targets_outside_catalog": sum(users[u]["targets_outside_catalog"] for u in members),
            "at_k": at_k,
        }
    return {"train_history_mode": threshold, "mode_ties": "smallest", "groups": groups}


def summarize_seeds(evaluations: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Report equal-weight seed means and sample standard deviations, never best seed."""
    if set(evaluations) != {42, 43, 44}:
        raise ValueError("Expected exactly the predeclared model seeds 42, 43 and 44")
    reference = evaluations[42]
    cohort_fields = ["eligible", "targets_total", "targets_in_catalog", "candidate_count"]
    for evaluation in evaluations.values():
        if (
            evaluation["split"] != "validation"
            or evaluation["catalog_size"] != reference["catalog_size"]
            or evaluation["at_k"].keys() != reference["at_k"].keys()
            or evaluation["per_user"].keys() != reference["per_user"].keys()
            or any(
                any(values[field] != reference["per_user"][u][field] for field in cohort_fields)
                for u, values in evaluation["per_user"].items()
            )
        ):
            raise ValueError("Seed comparison requires the same validation cohort and candidates")
    at_k = {}
    for k in reference["at_k"]:
        metrics: dict[str, Any] = {}
        for name in [
            "precision",
            "recall",
            "ndcg",
            "catalog_coverage",
            "gini",
            "arp",
            "novelty",
            "ild",
        ]:
            values = [evaluations[seed]["at_k"][k][name] for seed in [42, 43, 44]]
            if any(v is None for v in values):
                if not all(v is None for v in values):
                    raise ValueError("Metric is undefined for only some seeds")
                metrics[name] = None
            else:
                metrics[name] = {
                    "mean": fsum(values) / 3,
                    "sample_std": stdev(values),
                    "min": min(values),
                    "max": max(values),
                }
        at_k[k] = metrics
    return {"seeds": [42, 43, 44], "std_ddof": 1, "split_seed": 42, "at_k": at_k}
