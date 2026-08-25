"""Popularity baseline used as the mandatory reference model."""

from collections import defaultdict
from typing import Iterable

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class PopularityRecommender(Recommender):
    """Ranks items by aggregate listening count."""

    def __init__(self) -> None:
        self._scores: dict[str, float] = {}

    def fit(self, interactions: Iterable[Interaction]) -> "PopularityRecommender":
        totals: defaultdict[str, float] = defaultdict(float)
        for interaction in interactions:
            totals[interaction.item_id] += interaction.listening_count
        self._scores = dict(totals)
        return self

    def predict(self, user_id: str, item_id: str) -> float:
        del user_id
        return self._scores.get(item_id, 0.0)

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        del user_id
        if k <= 0:
            raise ValueError("k must be greater than zero")
        ranked = sorted(self._scores.items(), key=lambda pair: (-pair[1], pair[0]))
        return [
            Recommendation(item_id=item_id, score=score, reason="popular_with_all_users")
            for item_id, score in ranked
            if item_id not in seen_item_ids
        ][:k]
