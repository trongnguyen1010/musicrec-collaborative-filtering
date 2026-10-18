"""Evaluate every model against the same train catalog and complete target sets."""

from collections.abc import Iterable
from math import isfinite, log2
from typing import Any

import numpy as np
import pandas as pd

from musicrec.evaluation.ranking import ndcg_at_k, precision_at_k, recall_at_k, validate_ranking
from musicrec.recommenders.base import Recommender


def histories(frame: pd.DataFrame) -> dict[str, set[str]]:
    """Index the observed artists of each user."""
    return {str(user): set(group.item_id) for user, group in frame.groupby("user_id", sort=True)}


def evaluate(
    model: Recommender,
    train: pd.DataFrame,
    targets: pd.DataFrame,
    ks: Iterable[int],
    extra_mask: pd.DataFrame | None = None,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    """Macro-average user metrics, retain cold misses, and audit recommendations."""
    cutoffs = sorted(set(ks))
    if not cutoffs:
        raise ValueError("At least one K is required")
    for k in cutoffs:
        validate_ranking([], k)
    catalog = sorted(set(train.item_id))
    if not catalog:
        raise ValueError("Empty train catalog")
    catalog_set = set(catalog)
    index = {item: i for i, item in enumerate(catalog)}
    seen = histories(train)
    if extra_mask is not None:
        for user, items in histories(extra_mask).items():
            seen.setdefault(user, set()).update(items)
    truth = histories(targets)
    if not truth:
        raise ValueError("No users with nonempty ground truth remain for evaluation")
    listeners = train.groupby("item_id").user_id.nunique().to_dict()
    norm = sum(listeners.values()) + len(catalog)
    artist_users = {str(item): set(group.user_id) for item, group in train.groupby("item_id")}
    user_rows: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    frequencies = {k: np.zeros(len(catalog), dtype=np.float64) for k in cutoffs}
    cold = 0
    for user, relevant in truth.items():
        mask = seen.get(user, set())
        if mask & relevant:
            raise ValueError(f"Ground truth overlaps known history for {user}")
        recs = model.recommend(user, max(cutoffs), mask)
        ids = [r.item_id for r in recs]
        validate_ranking(ids, max(cutoffs))
        if len(ids) > max(cutoffs) or set(ids) - catalog_set or set(ids) & mask:
            raise ValueError("Recommendation violates length, catalog or seen masking")
        if not all(isfinite(r.score) for r in recs):
            raise ValueError("Nonfinite recommendation score")
        cold += len(relevant - catalog_set)
        for rank, rec in enumerate(recs, 1):
            predictions.append(
                {
                    "user_id": user,
                    "rank": rank,
                    "item_id": rec.item_id,
                    "score": rec.score,
                    "reason": rec.reason,
                }
            )
        for k in cutoffs:
            top = ids[:k]
            for item in top:
                frequencies[k][index[item]] += 1
            distances = []
            for a in range(len(top)):
                for b in range(a + 1, len(top)):
                    left, right = artist_users[top[a]], artist_users[top[b]]
                    distances.append(1 - len(left & right) / np.sqrt(len(left) * len(right)))
            user_rows.append(
                {
                    "user_id": user,
                    "k": k,
                    "precision": precision_at_k(ids, relevant, k),
                    "recall": recall_at_k(ids, relevant, k),
                    "ndcg": ndcg_at_k(ids, relevant, k),
                    "arp": float(np.mean([listeners[i] for i in top])) if top else None,
                    "novelty": float(np.mean([-log2((listeners[i] + 1) / norm) for i in top]))
                    if top
                    else None,
                    "ild": float(np.mean(distances)) if distances else None,
                    "returned": len(top),
                    "full_k": len(top) == k,
                    "targets": len(relevant),
                    "cold_targets": len(relevant - catalog_set),
                    "popularity_fallback": bool(recs and "popularity" in recs[0].reason),
                }
            )
    users_frame = pd.DataFrame(user_rows)
    result: dict[str, Any] = {
        "users_evaluated": len(truth),
        "users_excluded_empty_target": 0,
        "users_without_heldout": len(set(train.user_id) - set(truth)),
        "target_interactions": len(targets),
        "cold_targets": cold,
        "cold_target_rate": cold / len(targets),
        "catalog_size": len(catalog),
        "ground_truth": "full_including_cold_misses",
        "by_k": {},
    }
    for k in cutoffs:
        rows = users_frame[users_frame.k == k]
        freq = frequencies[k]
        total = freq.sum()
        ordered = np.sort(freq)
        gini = (
            float(
                2 * np.dot(np.arange(1, len(freq) + 1), ordered) / (len(freq) * total)
                - (len(freq) + 1) / len(freq)
            )
            if total
            else None
        )
        result["by_k"][str(k)] = {
            name: float(rows[name].mean()) if rows[name].notna().any() else None
            for name in (
                "precision",
                "recall",
                "ndcg",
                "arp",
                "novelty",
                "ild",
                "returned",
                "full_k",
                "popularity_fallback",
            )
        }
        result["by_k"][str(k)].update(
            coverage=float(np.count_nonzero(freq) / len(freq)),
            gini=gini,
            ild_users=int(rows.ild.notna().sum()),
            arp_users=int(rows.arp.notna().sum()),
        )
    return result, pd.DataFrame(predictions), users_frame
