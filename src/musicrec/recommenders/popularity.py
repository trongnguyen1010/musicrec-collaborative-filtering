"""Popularity baseline used as the mandatory reference model."""

import json
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class PopularityRecommender(Recommender):
    """Ranks items by distinct training listeners, independent of listening intensity."""

    def __init__(self) -> None:
        self._scores: dict[str, float] = {}

    def fit(self, interactions: Iterable[Interaction]) -> "PopularityRecommender":
        listeners: defaultdict[str, set[str]] = defaultdict(set)
        for interaction in interactions:
            listeners[interaction.item_id].add(interaction.user_id)
        if not listeners:
            raise ValueError("Cannot fit Popularity on empty training data")
        self._scores = {item: float(len(users)) for item, users in listeners.items()}
        return self

    def save(self, path: Path) -> None:
        """Persist exact listener scores without overwriting a previous artifact."""
        with path.open("x", encoding="utf-8") as stream:
            json.dump(
                {"format": "listener_popularity_v1", "scores": self._scores}, stream, sort_keys=True
            )

    @classmethod
    def load(cls, path: Path) -> "PopularityRecommender":
        """Load a trusted JSON artifact after validating its schema and counts."""
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("format") != "listener_popularity_v1":
            raise ValueError("Unsupported popularity artifact")
        model = cls()
        from math import isfinite

        for item, score in data["scores"].items():
            if (
                not item
                or isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not isfinite(score)
                or score < 1
                or int(score) != score
            ):
                raise ValueError("Invalid listener count")
        if not data["scores"]:
            raise ValueError("Empty popularity artifact")
        model._scores = data["scores"]
        return model

    def predict(self, user_id: str, item_id: str) -> float:
        del user_id
        return self._scores.get(item_id, 0.0)

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        del user_id
        if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
            raise ValueError("k must be greater than zero")
        ranked = sorted(self._scores.items(), key=lambda pair: (-pair[1], pair[0]))
        return [
            Recommendation(item_id=item_id, score=score, reason="popular_with_all_users")
            for item_id, score in ranked
            if item_id not in seen_item_ids
        ][:k]
