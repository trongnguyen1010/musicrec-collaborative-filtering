"""Shared full-ranking evaluation on a train-only artist catalog."""

from collections import Counter
from itertools import combinations
from math import fsum, isfinite, log2, sqrt
from typing import Any


def _top_k(recommended_ids: list[str], k: int) -> list[str]:
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    if len(recommended_ids) != len(set(recommended_ids)):
        raise ValueError("Duplicate recommendations")
    return recommended_ids[:k]


def precision_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of the first k recommendations that are relevant."""
    return len(set(_top_k(recommended_ids, k)) & relevant_ids) / k


def recall_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of relevant items discovered in the first k results."""
    top_k = _top_k(recommended_ids, k)
    if not relevant_ids:
        return 0.0
    return len(set(top_k) & relevant_ids) / len(relevant_ids)


def ndcg_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return binary NDCG; the cohort evaluator excludes users with no targets."""
    top_k = _top_k(recommended_ids, k)
    ideal = fsum(1 / log2(rank + 2) for rank in range(min(k, len(relevant_ids))))
    dcg = fsum(1 / log2(rank + 2) for rank, item in enumerate(top_k) if item in relevant_ids)
    return dcg / ideal if ideal else 0.0


def rank_candidates(
    scores: dict[str, float], catalog: list[str], seen: set[str], k: int
) -> list[str]:
    """Rank every unseen train item, breaking ties by the train mapping order.

    Callers must supply scores for all candidates, never just sampled negatives.
    Scores for seen catalog items are allowed and masked before sorting.
    """
    _top_k(catalog, k)
    if not catalog or set(scores) - set(catalog):
        raise ValueError("Scores must belong to a non-empty train catalog")
    candidates = [item for item in catalog if item not in seen]
    if set(candidates) - scores.keys():
        raise ValueError("Full ranking requires a score for every unseen catalog item")
    if not all(isfinite(score) for score in scores.values()):
        raise ValueError("Scores must be finite")
    return sorted(candidates, key=lambda item: -scores[item])[:k]


def gini_index(frequencies: list[int]) -> float | None:
    """Return unnormalized finite-catalog Gini, including zero-exposure artists."""
    if not frequencies or any(type(value) is not int or value < 0 for value in frequencies):
        raise ValueError("Expected a non-empty catalog of non-negative integer counts")
    total, n = sum(frequencies), len(frequencies)
    if not total:
        return None
    weighted = sum(rank * value for rank, value in enumerate(sorted(frequencies), start=1))
    return 2 * weighted / (n * total) - (n + 1) / n


def proxy_rmse(actual: list[float], predicted: list[float]) -> float:
    """RMSE only for aligned predictions of the same observed 1–5 proxy target.

    The caller opts in only for a compatible model; predictions are not clipped.
    """
    if not actual or len(actual) != len(predicted):
        raise ValueError("Expected non-empty aligned targets and predictions")
    if not all(isfinite(value) and 1 <= value <= 5 for value in actual):
        raise ValueError("Targets must be finite proxy scores in [1, 5]")
    if not all(isfinite(value) for value in predicted):
        raise ValueError("Predictions must be finite")
    return sqrt(fsum((a - b) ** 2 for a, b in zip(actual, predicted, strict=True)) / len(actual))


def evaluate_ranking(
    recommendations: dict[str, list[str]],
    targets: dict[str, set[str]],
    train: dict[str, set[str]],
    *,
    ks: tuple[int, ...] = (5, 10, 20),
    split: str = "validation",
    validation: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    """Evaluate supplied lists; do not fit, refit, sample or read data files.

    All supplied users must have a list (possibly empty) and targets. Ranking
    averages include zero-return users with valid targets. Beyond-accuracy
    metrics use the same eligible cohort. ARP/Novelty pool returned positions;
    ILD averages users with at least two results and reports that denominator.
    Train determines catalog, listener counts and binary interaction cosine.
    Test additionally masks validation but never adds it to training statistics.
    """
    if not train or set(recommendations) != set(train) or set(targets) != set(train):
        raise ValueError("Train, targets and recommendation user sets must match and be non-empty")
    if not ks or len(ks) != len(set(ks)):
        raise ValueError("Expected distinct positive cutoffs")
    for k in ks:
        _top_k([], k)
    if split not in {"validation", "test"}:
        raise ValueError("Expected validation or test split")
    if split == "test":
        if validation is None or set(validation) != set(train):
            raise ValueError("Test requires validation histories for every user")
    elif validation is not None:
        raise ValueError("Validation evaluation must only mask train")

    listeners: dict[str, set[str]] = {}
    for user, history in train.items():
        if not history:
            raise ValueError("Every evaluation user must have a non-empty train history")
        for item in history:
            listeners.setdefault(item, set()).add(user)
    catalog = set(listeners)
    eligible: dict[str, set[str]] = {}
    per_user: dict[str, Any] = {}
    for user in sorted(train):
        seen = train[user] | (validation[user] if validation is not None else set())
        if validation is not None and train[user] & validation[user]:
            raise ValueError("Train and validation histories overlap")
        if targets[user] & seen:
            raise ValueError("Held-out targets overlap observed history")
        items = recommendations[user]
        _top_k(items, max(ks))
        if set(items) - catalog or set(items) & seen:
            raise ValueError("Recommendations contain out-of-catalog or seen items")
        relevant = targets[user] & catalog
        if relevant:
            eligible[user] = relevant
        per_user[user] = {
            "targets_total": len(targets[user]),
            "targets_in_catalog": len(relevant),
            "targets_outside_catalog": len(targets[user] - catalog),
            "candidate_count": len(catalog - seen),
            "eligible": bool(relevant),
            "at_k": {},
        }

    denominator = sum(len(users) + 1 for users in listeners.values())
    by_k = {}
    for k in ks:
        exposure: Counter[str] = Counter()
        precisions, recalls, ndcgs, diversities = [], [], [], []
        short, empty = 0, 0
        for user, relevant in eligible.items():
            items = recommendations[user][:k]
            precision = precision_at_k(items, relevant, k)
            recall = recall_at_k(items, relevant, k)
            ndcg = ndcg_at_k(items, relevant, k)
            distances = [
                1 - len(listeners[a] & listeners[b]) / sqrt(len(listeners[a]) * len(listeners[b]))
                for a, b in combinations(items, 2)
            ]
            ild = fsum(distances) / len(distances) if distances else None
            per_user[user]["at_k"][str(k)] = {
                "precision": precision,
                "recall": recall,
                "ndcg": ndcg,
                "returned": len(items),
                "ild": ild,
            }
            precisions.append(precision)
            recalls.append(recall)
            ndcgs.append(ndcg)
            if ild is not None:
                diversities.append(ild)
            exposure.update(items)
            short += len(items) < k
            empty += not items
        positions, n = exposure.total(), len(eligible)
        by_k[str(k)] = {
            "precision": fsum(precisions) / n if n else None,
            "recall": fsum(recalls) / n if n else None,
            "ndcg": fsum(ndcgs) / n if n else None,
            "catalog_coverage": len(exposure) / len(catalog) if n else None,
            "gini": gini_index([exposure[item] for item in catalog]),
            "arp": fsum(count * len(listeners[item]) for item, count in exposure.items())
            / positions
            if positions
            else None,
            "novelty": fsum(
                count * -log2((len(listeners[item]) + 1) / denominator)
                for item, count in exposure.items()
            )
            / positions
            if positions
            else None,
            "ild": fsum(diversities) / len(diversities) if diversities else None,
            "ild_users": len(diversities),
            "returned_positions": positions,
            "short_list_users": short,
            "empty_list_users": empty,
            "full_list_rate": (n - short) / n if n else None,
        }
    total_targets = sum(len(items) for items in targets.values())
    outside = sum(len(items - catalog) for items in targets.values())
    return {
        "split": split,
        "users_total": len(train),
        "users_eligible": len(eligible),
        "users_without_catalog_targets": len(train) - len(eligible),
        "targets_total": total_targets,
        "targets_outside_catalog": outside,
        "outside_catalog_target_rate": outside / total_targets if total_targets else None,
        "catalog_size": len(catalog),
        "at_k": by_k,
        "per_user": per_user,
    }
