"""Repeatable Random baseline on the numeric HetRec train catalog."""

import random
from collections.abc import Iterable

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class RandomRecommender(Recommender):
    """Shuffle the full train catalog per user, then remove observed history.

    A fresh local RNG seeded with ``musicrec-random-v1:{seed}:{user_id}`` makes
    inference independent of call order, cutoff and previously seen requests.
    Scores are descending permutation ranks, not ratings or probabilities.
    """

    def __init__(self, seed: int = 42) -> None:
        if type(seed) is not int or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        self.seed = seed
        self._catalog: list[str] = []
        self._users: set[str] = set()

    def fit(self, interactions: Iterable[Interaction]) -> "RandomRecommender":
        """Learn only the train catalog and known user IDs; ignore counts."""
        items, users = set(), set()
        for interaction in interactions:
            items.add(interaction.item_id)
            users.add(interaction.user_id)
        if not items or any(not item.isdecimal() or str(int(item)) != item for item in items):
            raise ValueError("Expected a non-empty catalog of canonical positive numeric item IDs")
        if any(int(item) <= 0 for item in items):
            raise ValueError("Item IDs must be positive")
        self._catalog = sorted(items, key=int)
        self._users = users
        return self

    def _ranking(self, user_id: str) -> list[str]:
        if not self._catalog:
            raise RuntimeError("Fit the Random baseline before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        ranked = self._catalog.copy()
        random.Random(f"musicrec-random-v1:{self.seed}:{user_id}").shuffle(ranked)
        return ranked

    def predict(self, user_id: str, item_id: str) -> float:
        """Return the same rank score as recommend; reject unknown artists."""
        # ponytail: scalar predict is O(catalog); cache per request if pair scoring becomes hot.
        ranked = self._ranking(user_id)
        if item_id not in self._catalog:
            raise ValueError("Artist is outside the train catalog")
        return float(len(ranked) - ranked.index(item_id))

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Return up to k distinct unseen artists; unknown users use the same baseline."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        ranked = self._ranking(user_id)
        reason = "uniform_random" if user_id in self._users else "uniform_random_cold_start"
        results = []
        for rank, item in enumerate(ranked):
            if item not in seen_item_ids:
                results.append(Recommendation(item, float(len(ranked) - rank), reason))
                if len(results) == k:
                    break
        return results
