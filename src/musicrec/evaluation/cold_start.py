"""M2 validation with disjoint query users, explicit profiles and learning-only statistics."""

from collections import Counter
from itertools import combinations
from math import fsum, isfinite, log2, sqrt
from typing import Any

from musicrec.evaluation.ranking import gini_index, ndcg_at_k, precision_at_k, recall_at_k


def select_m2_config(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Select on exactly N=1/3/5 validation NDCG@10, then lower alpha/threshold."""
    if not rows:
        raise ValueError("Expected non-empty M2 grid results")
    candidates = []
    for row in rows:
        scores = row["ndcg_by_n"]
        if set(scores) != {1, 3, 5} or any(
            not isinstance(v, (int, float)) or not isfinite(v) or not 0 <= v <= 1
            for v in scores.values()
        ):
            raise ValueError("Selection requires defined NDCG for exactly N=1,3,5")
        candidates.append({**row, "mean_ndcg_at_10": fsum(scores.values()) / 3})
    return min(
        candidates, key=lambda r: (-r["mean_ndcg_at_10"], r["alpha"], r["history_threshold"])
    )


def evaluate_cold_start(
    recommendations: dict[str, list[str]],
    targets: dict[str, set[str]],
    learning_histories: dict[str, set[str]],
    profiles: dict[str, set[str]],
    *,
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, Any]:
    """Reuse ranking metric definitions while separating learned data from the query cohort.

    Unlike warm-start evaluation, profiles may be empty and mask only supplied
    artists. Query users never contribute to catalog/listeners/novelty/ILD.
    This entry point handles validation only; Step 16 never opens test.
    """
    users = set(profiles)
    if not users or set(recommendations) != users or set(targets) != users:
        raise ValueError("Profiles, recommendations and targets must share a non-empty cohort")
    if not learning_histories or users & learning_histories.keys():
        raise ValueError("Learning users and query users must be non-empty and disjoint")
    if not ks or len(ks) != len(set(ks)):
        raise ValueError("Expected distinct positive cutoffs")
    for k in ks:
        precision_at_k([], set(), k)
    listeners: dict[str, set[str]] = {}
    for user, history in learning_histories.items():
        if not history:
            raise ValueError("Learning histories must be non-empty")
        for item in history:
            listeners.setdefault(item, set()).add(user)
    catalog = set(listeners)
    eligible: dict[str, set[str]] = {}
    per_user: dict[str, Any] = {}
    for user in sorted(users):
        items, seen, relevant = recommendations[user], profiles[user], targets[user] & catalog
        if len(items) != len(set(items)) or set(items) & seen or set(items) - catalog:
            raise ValueError("Recommendations contain duplicate, supplied or unknown artists")
        if targets[user] & seen:
            raise ValueError("Validation targets overlap the supplied train profile")
        if relevant:
            eligible[user] = relevant
        per_user[user] = {
            "targets_total": len(targets[user]),
            "targets_in_catalog": len(relevant),
            "targets_outside_catalog": len(targets[user] - catalog),
            "candidate_count": len(catalog - seen),
            "profile_size": len(seen),
            "eligible": bool(relevant),
            "at_k": {},
        }
    denominator = sum(len(v) + 1 for v in listeners.values())
    by_k = {}
    for k in ks:
        exposure: Counter[str] = Counter()
        values: dict[str, list[float]] = {m: [] for m in ["precision", "recall", "ndcg", "ild"]}
        short, empty = 0, 0
        for user, relevant in eligible.items():
            items = recommendations[user][:k]
            distances = [
                1 - len(listeners[a] & listeners[b]) / sqrt(len(listeners[a]) * len(listeners[b]))
                for a, b in combinations(items, 2)
            ]
            metrics = {
                "precision": precision_at_k(items, relevant, k),
                "recall": recall_at_k(items, relevant, k),
                "ndcg": ndcg_at_k(items, relevant, k),
                "ild": fsum(distances) / len(distances) if distances else None,
            }
            per_user[user]["at_k"][str(k)] = {**metrics, "returned": len(items)}
            for metric, value in metrics.items():
                if value is not None:
                    values[metric].append(value)
            exposure.update(items)
            short += len(items) < k
            empty += not items
        positions, n = exposure.total(), len(eligible)
        by_k[str(k)] = {
            **{m: fsum(v) / len(v) if v else None for m, v in values.items()},
            "catalog_coverage": len(exposure) / len(catalog) if n else None,
            "gini": gini_index([exposure[i] for i in catalog]),
            "arp": fsum(count * len(listeners[i]) for i, count in exposure.items()) / positions
            if positions
            else None,
            "novelty": fsum(
                count * -log2((len(listeners[i]) + 1) / denominator)
                for i, count in exposure.items()
            )
            / positions
            if positions
            else None,
            "ild_users": len(values["ild"]),
            "returned_positions": positions,
            "short_list_users": short,
            "empty_list_users": empty,
            "full_list_rate": (n - short) / n if n else None,
        }
    total_targets = sum(len(v) for v in targets.values())
    outside = sum(len(v - catalog) for v in targets.values())
    return {
        "split": "validation",
        "protocol": "m2_disjoint_users_supplied_profile_only",
        "learning_users": len(learning_histories),
        "users_total": len(users),
        "users_eligible": len(eligible),
        "users_without_catalog_targets": len(users) - len(eligible),
        "targets_total": total_targets,
        "targets_outside_catalog": outside,
        "outside_catalog_target_rate": outside / total_targets if total_targets else None,
        "catalog_size": len(catalog),
        "at_k": by_k,
        "per_user": per_user,
    }
