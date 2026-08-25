"""Deterministic top-K ranking metrics."""


def precision_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of the first k recommendations that are relevant."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    top_k = recommended_ids[:k]
    if not top_k:
        return 0.0
    return len(set(top_k) & relevant_ids) / len(top_k)


def recall_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of relevant items discovered in the first k results."""
    if k <= 0:
        raise ValueError("k must be greater than zero")
    if not relevant_ids:
        return 0.0
    return len(set(recommended_ids[:k]) & relevant_ids) / len(relevant_ids)
