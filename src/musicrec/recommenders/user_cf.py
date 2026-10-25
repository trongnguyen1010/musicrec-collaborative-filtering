"""Mean-centered UserCF predictions with full-vector cosine on train proxy scores."""

import hashlib
import json
from collections.abc import Iterable
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, load_npz, save_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender

NUMERIC_TIE_DECIMALS = 12


class UserCFRecommender(Recommender):
    """Keep global top-L positive neighbors, then intersect with each item's listeners.

    Cosine uses full uncentered proxy rows with missing positions zero-filled.
    Means use observed train scores only; no contribution falls back to the
    user's mean, or the global mean for an unknown user. Scores are not clipped.
    """

    def __init__(self, neighbors: int = 40, shrinkage: float = 0.0) -> None:
        if type(neighbors) is not int or neighbors <= 0:
            raise ValueError("neighbors must be a positive integer")
        if not isfinite(shrinkage) or shrinkage < 0:
            raise ValueError("shrinkage must be finite and non-negative")
        self.neighbors = neighbors
        self.shrinkage = float(shrinkage)
        self._users: list[str] = []
        self._items: list[str] = []
        self._ratings: csr_matrix[np.float64]
        self._weights: csr_matrix[np.float64]

    @staticmethod
    def _id_key(value: str) -> tuple[bool, int, str]:
        return not value.isdecimal(), int(value) if value.isdecimal() else 0, value

    def _prepare(self) -> None:
        """Build inference views from persisted ratings without relearning neighbors."""
        self._user_index = {user: index for index, user in enumerate(self._users)}
        self._item_index = {item: index for index, item in enumerate(self._items)}
        counts = np.diff(self._ratings.indptr)
        self._means = np.asarray(self._ratings.sum(axis=1)).ravel() / counts
        self._global_mean = float(self._ratings.data.mean())
        self._binary = self._ratings.copy()
        self._binary.data = np.ones_like(self._binary.data)
        self._centered = self._ratings.copy()
        self._centered.data -= np.repeat(self._means, counts)
        self._centered.eliminate_zeros()

    def fit(self, interactions: Iterable[Interaction]) -> "UserCFRecommender":
        """Fit only explicit proxy_score values, retaining raw counts separately."""
        rows = list(interactions)
        if not rows or any(row.proxy_score is None for row in rows):
            raise ValueError("UserCF requires non-empty train interactions with proxy_score")
        pairs = {(row.user_id, row.item_id) for row in rows}
        if len(pairs) != len(rows):
            raise ValueError("Duplicate user-artist pair")
        self._users = sorted({row.user_id for row in rows}, key=self._id_key)
        self._items = sorted({row.item_id for row in rows}, key=self._id_key)
        user_index = {user: index for index, user in enumerate(self._users)}
        item_index = {item: index for index, item in enumerate(self._items)}
        self._ratings = csr_matrix(
            (
                np.array([row.proxy_score for row in rows], dtype=np.float64),
                (
                    [user_index[row.user_id] for row in rows],
                    [item_index[row.item_id] for row in rows],
                ),
            ),
            shape=(len(self._users), len(self._items)),
            dtype=np.float64,
        )
        self._ratings.sort_indices()
        self._prepare()
        norms = np.sqrt(np.asarray(self._ratings.power(2).sum(axis=1)).ravel())
        normalized = csr_matrix(self._ratings.multiply(1 / norms[:, None]))
        similarity = csr_matrix(normalized @ normalized.T)
        similarity.data = np.clip(similarity.data, 0, 1)
        if self.shrinkage:
            common = csr_matrix(self._binary @ self._binary.T)
            common.data /= common.data + self.shrinkage
            similarity = csr_matrix(similarity.multiply(common))
        similarity.setdiag(0)
        similarity.eliminate_zeros()
        neighbor_rows, neighbor_columns, weights = [], [], []
        for user in range(len(self._users)):
            start, end = similarity.indptr[user : user + 2]
            columns, values = similarity.indices[start:end], similarity.data[start:end]
            order = np.lexsort((columns, -np.round(values, NUMERIC_TIE_DECIMALS)))[: self.neighbors]
            for index in order:
                if values[index] > 0:
                    neighbor_rows.append(user)
                    neighbor_columns.append(int(columns[index]))
                    weights.append(float(values[index]))
        self._weights = csr_matrix(
            (weights, (neighbor_rows, neighbor_columns)),
            shape=(len(self._users), len(self._users)),
            dtype=np.float64,
        )
        return self

    def _score_catalog(self, user_id: str) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
        if not self._users:
            raise RuntimeError("Fit UserCF before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if user_id not in self._user_index:
            return np.full(len(self._items), self._global_mean), np.zeros(
                len(self._items), dtype=bool
            )
        user = self._user_index[user_id]
        weights = self._weights.getrow(user)
        numerator = csr_matrix(weights @ self._centered).toarray().ravel()
        denominator = csr_matrix(weights @ self._binary).toarray().ravel()
        supported = denominator > 0
        scores = np.full(len(self._items), self._means[user])
        scores[supported] += numerator[supported] / denominator[supported]
        return scores, supported

    def predict(self, user_id: str, item_id: str) -> float:
        """Predict a proxy target, including explicit mean fallback without clipping."""
        # ponytail: scalar predict scores the catalog; add batching if pair scoring becomes hot.
        scores, _ = self._score_catalog(user_id)
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the train catalog")
        return float(scores[self._item_index[item_id]])

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Rank the full unseen train catalog, breaking ties by numeric mapping order."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        scores, supported = self._score_catalog(user_id)
        excluded = {self._item_index[item] for item in seen_item_ids if item in self._item_index}
        if user_id in self._user_index:
            excluded.update(self._ratings.getrow(self._user_index[user_id]).indices)
        candidates = np.array([i for i in range(len(self._items)) if i not in excluded], dtype=int)
        ranked = candidates[
            np.argsort(-np.round(scores[candidates], NUMERIC_TIE_DECIMALS), kind="stable")[:k]
        ]
        fallback = (
            "user_cf_user_mean_fallback"
            if user_id in self._user_index
            else "user_cf_global_mean_cold_start"
        )
        return [
            Recommendation(
                self._items[i], float(scores[i]), "user_cf" if supported[i] else fallback
            )
            for i in ranked
        ]

    def save(self, directory: Path) -> None:
        """Save a new JSON/NPZ model directory without overwriting existing artifacts."""
        if not self._users:
            raise RuntimeError("Fit UserCF before saving")
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "ratings.npz", self._ratings)
        save_npz(directory / "neighbors.npz", self._weights)
        state = {
            "schema_version": 1,
            "numeric_tie_decimals": NUMERIC_TIE_DECIMALS,
            "neighbors": self.neighbors,
            "shrinkage": self.shrinkage,
            "users": self._users,
            "items": self._items,
            "user_means": self._means.tolist(),
            "global_mean": self._global_mean,
            "sha256": {
                name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in ["ratings.npz", "neighbors.npz"]
            },
        }
        with (directory / "state.json").open("x", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, allow_nan=False)
            handle.write("\n")

    @classmethod
    def load(cls, directory: Path) -> "UserCFRecommender":
        """Restore numeric state and neighbors without calling fit or recomputing similarities."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if (
            state.get("schema_version") != 1
            or state.get("numeric_tie_decimals") != NUMERIC_TIE_DECIMALS
        ):
            raise ValueError("Unsupported UserCF model schema")
        for name in ["ratings.npz", "neighbors.npz"]:
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != state["sha256"][name]:
                raise ValueError(f"Model checksum mismatch: {name}")
        model = cls(state["neighbors"], state["shrinkage"])
        model._users, model._items = state["users"], state["items"]
        for ids in [model._users, model._items]:
            if (
                not ids
                or any(not isinstance(value, str) or not value for value in ids)
                or len(ids) != len(set(ids))
                or ids != sorted(ids, key=cls._id_key)
            ):
                raise ValueError("Invalid model ID mappings")
        model._ratings = csr_matrix(load_npz(directory / "ratings.npz"), dtype=np.float64)
        model._weights = csr_matrix(load_npz(directory / "neighbors.npz"), dtype=np.float64)
        if (
            model._ratings.shape != (len(model._users), len(model._items))
            or not model._ratings.has_canonical_format
            or not np.isin(model._ratings.data, [1, 2, 3, 4, 5]).all()
            or (np.diff(model._ratings.indptr) == 0).any()
            or model._weights.shape != (len(model._users), len(model._users))
            or not model._weights.has_canonical_format
            or not np.isfinite(model._weights.data).all()
            or (model._weights.data <= 0).any()
            or (model._weights.data > 1).any()
            or (model._weights.diagonal() != 0).any()
            or (np.diff(model._weights.indptr) > model.neighbors).any()
        ):
            raise ValueError("Invalid model matrices")
        model._prepare()
        if (
            not np.allclose(model._means, state["user_means"], rtol=0, atol=1e-12)
            or model._global_mean != state["global_mean"]
        ):
            raise ValueError("Invalid stored train means")
        return model
