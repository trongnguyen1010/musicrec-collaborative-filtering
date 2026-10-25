"""Popularity baseline used as the mandatory reference model."""

from collections import defaultdict
from collections.abc import Iterable
from math import fsum, isfinite, log2

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class PopularityRecommender(Recommender):
    """Rank by sum of log2(1 + raw count) on train, with numeric ID tie-breaking.

    Scores express aggregate listening intensity, not distinct listener counts
    or predicted ratings. Unseen users receive the same non-personalized list.
    """

    def __init__(self) -> None:
        self._scores: dict[str, float] = {}
        self._ranked: list[str] = []
        self._users: set[str] = set()

    def fit(self, interactions: Iterable[Interaction]) -> "PopularityRecommender":
        """Transform each observed raw count once; sum independently of row order."""
        values: defaultdict[str, list[float]] = defaultdict(list)
        pairs: set[tuple[str, str]] = set()
        for interaction in interactions:
            if not isfinite(interaction.listening_count) or interaction.listening_count <= 0:
                raise ValueError("Raw listening counts must be finite and positive")
            pair = (interaction.user_id, interaction.item_id)
            if pair in pairs:
                raise ValueError("Duplicate user-artist pair")
            pairs.add(pair)
            values[interaction.item_id].append(log2(1 + interaction.listening_count))
        if not values:
            raise ValueError("Expected non-empty training interactions")
        self._scores = {item: fsum(sorted(counts)) for item, counts in values.items()}
        self._ranked = sorted(
            self._scores,
            key=lambda item: (
                -self._scores[item],
                not item.isdecimal(),
                int(item) if item.isdecimal() else 0,
                item,
            ),
        )
        self._users = {user for user, _ in pairs}
        return self

    def predict(self, user_id: str, item_id: str) -> float:
        """Return a global log-count score; reject artists outside train."""
        del user_id
        if not self._scores:
            raise RuntimeError("Fit Popularity before inference")
        if item_id not in self._scores:
            raise ValueError("Artist is outside the train catalog")
        return self._scores[item_id]

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Filter the full pre-ranked train catalog without filling from held-out items."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        if not self._scores:
            raise RuntimeError("Fit Popularity before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        reason = "popular_with_all_users"
        if user_id not in self._users:
            reason += "_cold_start"
        results = []
        for item in self._ranked:
            if item not in seen_item_ids:
                results.append(Recommendation(item, self._scores[item], reason))
                if len(results) == k:
                    break
        return results
