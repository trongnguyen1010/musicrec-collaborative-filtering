"""H1 control: per-user min-max ALS scores minus a direct train-popularity penalty."""

from collections.abc import Iterable
from math import isfinite

import numpy as np
from numpy.typing import NDArray

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.implicit_als import ImplicitALSRecommender


class DirectPenaltyRecommender(Recommender):
    """s_direct = s_norm - beta * p(i), with s_norm min-max over the train-unseen catalog.

    The min/max pair of every user is learned once from the checkpoint and train, so a
    later validation mask never refits the scale. A flat range normalizes to ones.
    """

    def __init__(self, base: ImplicitALSRecommender, *, beta: float = 0.0) -> None:
        if not isfinite(beta) or beta < 0:
            raise ValueError("beta must be finite and non-negative")
        self.base, self.beta = base, float(beta)
        self._fitted = False

    def fit(self, interactions: Iterable[Interaction]) -> "DirectPenaltyRecommender":
        """Learn binary listener counts and per-user score ranges; never fit ALS."""
        base = self.base
        rows = list(interactions)
        if not rows or len({(r.user_id, r.item_id) for r in rows}) != len(rows):
            raise ValueError("Expected non-empty unique train user-artist pairs")
        if {r.user_id for r in rows} != set(base._users) or {r.item_id for r in rows} != set(
            base._items
        ):
            raise ValueError("Train pairs must match the checkpoint users and catalog")
        listeners = np.zeros(len(base._items), dtype=np.int64)
        for r in rows:
            listeners[base._item_index[r.item_id]] += 1
        self.popularity = np.log1p(listeners) / np.log1p(listeners.max())
        ranges = np.empty((len(base._users), 2), dtype=np.float64)
        for u, user in enumerate(base._users):
            mask = np.ones(len(base._items), dtype=bool)
            mask[base._confidence.getrow(u).indices] = False
            if not mask.any():
                raise ValueError("Every user needs at least one train-unseen artist")
            unseen = base._score_catalog(user)[mask]
            ranges[u] = unseen.min(), unseen.max()
        self.ranges = ranges
        self._fitted = True
        return self

    def _require_fit(self) -> None:
        if not self._fitted:
            raise RuntimeError("Fit the direct-penalty context before inference")

    def _scores(self, user_id: str) -> NDArray[np.float64]:
        low, high = self.ranges[self.base._user_index[user_id]]
        scores = self.base._score_catalog(user_id)
        spread = high - low
        normalized = (scores - low) / spread if spread else np.ones_like(scores)
        adjusted: NDArray[np.float64] = normalized - self.beta * self.popularity
        return adjusted

    def predict(self, user_id: str, item_id: str) -> float:
        """Return the penalized normalized score; beta=0 keeps the raw base score."""
        self._require_fit()
        if self.beta == 0 or user_id not in self.base._user_index:
            return self.base.predict(user_id, item_id)
        if item_id not in self.base._item_index:
            raise ValueError("Artist is outside the train catalog")
        return float(self._scores(user_id)[self.base._item_index[item_id]])

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Mask exactly like the base; beta=0 returns the base call unchanged."""
        self._require_fit()
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        base = self.base
        if self.beta == 0 or user_id not in base._user_index:
            return base.recommend(user_id, k, seen_item_ids)
        scores = self._scores(user_id)
        mask = np.ones(len(base._items), dtype=bool)
        mask[[base._item_index[i] for i in seen_item_ids if i in base._item_index]] = False
        mask[base._confidence.getrow(base._user_index[user_id]).indices] = False
        candidates = np.flatnonzero(mask)
        ranked = candidates[np.argsort(-np.round(scores[candidates], 12), kind="stable")[:k]]
        reason = f"direct_penalty_beta={self.beta:g};base=implicit_als"
        return [Recommendation(base._items[i], float(scores[i]), reason) for i in ranked]
