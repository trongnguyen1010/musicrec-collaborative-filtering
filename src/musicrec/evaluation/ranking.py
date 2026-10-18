"""Binary relevance metrics using complete held-out targets, including cold misses."""

from math import log2


def validate_ranking(recommended_ids: list[str], k: int) -> None:
    """Reject invalid K and duplicate recommendations consistently for all metrics."""
    if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer")
    if len(set(recommended_ids)) != len(recommended_ids):
        raise ValueError("Duplicate recommendation IDs")


def precision_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of the first k recommendations that are relevant."""
    validate_ranking(recommended_ids, k)
    top_k = recommended_ids[:k]
    if not top_k:
        return 0.0
    return len(set(top_k) & relevant_ids) / k


def recall_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return the fraction of relevant items discovered in the first k results."""
    validate_ranking(recommended_ids, k)
    if not relevant_ids:
        raise ValueError("Empty ground truth; exclude and count this user before averaging")
    return len(set(recommended_ids[:k]) & relevant_ids) / len(relevant_ids)


def ndcg_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Return normalized discounted gain with binary target labels."""
    validate_ranking(recommended_ids, k)
    if not relevant_ids:
        raise ValueError("NDCG requires nonempty ground truth")
    dcg = sum(
        1 / log2(rank + 2) for rank, item in enumerate(recommended_ids[:k]) if item in relevant_ids
    )
    ideal = sum(1 / log2(rank + 2) for rank in range(min(k, len(relevant_ids))))
    return dcg / ideal
