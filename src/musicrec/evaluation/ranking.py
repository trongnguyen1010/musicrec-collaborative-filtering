"""Deterministic top-K ranking metrics."""

from math import log2


def precision_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of the first k recommendations that are relevant."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    top_k = recommended_ids[:k]
    if not top_k:
        return 0.0
    return len(set(top_k) & relevant_ids) / k


def recall_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of relevant items discovered in the first k results."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    if not relevant_ids:
        return 0.0
    return len(set(recommended_ids[:k]) & relevant_ids) / len(relevant_ids)


def hit_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return whether at least one relevant item occurs in the first k ranks."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    return float(bool(set(recommended_ids[:k]) & relevant_ids))


def mrr_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return reciprocal rank of the first hit, or zero if there is no hit."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    return next(
        (1.0 / rank for rank, item in enumerate(recommended_ids[:k], 1) if item in relevant_ids),
        0.0,
    )


def ndcg_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return binary NDCG with ideal length min(k, number of relevant items)."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    if not relevant_ids:
        return 0.0
    hits = set()
    dcg = 0.0
    for rank, item in enumerate(recommended_ids[:k], 1):
        if item in relevant_ids and item not in hits:
            dcg += 1.0 / log2(rank + 1)
            hits.add(item)
    ideal = sum(1.0 / log2(rank + 1) for rank in range(1, min(k, len(relevant_ids)) + 1))
    return dcg / ideal
