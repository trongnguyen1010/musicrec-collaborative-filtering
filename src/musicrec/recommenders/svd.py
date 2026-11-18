"""Biased matrix factorization learned by observed-only SGD on train proxy scores."""

import hashlib
import json
from collections.abc import Callable, Iterable
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, load_npz, save_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender

NUMERIC_TIE_DECIMALS = 12


class SVDRecommender(Recommender):
    """Learn global mean + user bias + item bias + factor dot product, without clipping.

    Missing pairs are absent from the SGD objective. Validation may select an
    epoch through a read-only callback; it never supplies gradient targets.
    """

    def __init__(
        self,
        latent_factors: int = 32,
        learning_rate: float = 0.005,
        regularization: float = 0.02,
        max_epochs: int = 100,
        patience: int = 5,
        seed: int = 42,
        init_std: float = 0.1,
    ) -> None:
        for name, value in [
            ("latent_factors", latent_factors),
            ("max_epochs", max_epochs),
            ("patience", patience),
        ]:
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if type(seed) is not int or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        for name, scale in [("learning_rate", learning_rate), ("init_std", init_std)]:
            if not isfinite(scale) or scale <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not isfinite(regularization) or regularization < 0:
            raise ValueError("regularization must be finite and non-negative")
        self.latent_factors, self.max_epochs, self.patience = latent_factors, max_epochs, patience
        self.learning_rate, self.regularization = float(learning_rate), float(regularization)
        self.seed, self.init_std = seed, float(init_std)
        self._users: list[str] = []
        self._items: list[str] = []
        self._ratings: csr_matrix[np.float64]
        self._user_bias: NDArray[np.float64]
        self._item_bias: NDArray[np.float64]
        self._user_factors: NDArray[np.float64]
        self._item_factors: NDArray[np.float64]
        self.learning_curve: list[dict[str, Any]] = []
        self.best_epoch = 0
        self.stop_reason = "not_fitted"

    @staticmethod
    def _id_key(value: str) -> tuple[bool, int, str]:
        return not value.isdecimal(), int(value) if value.isdecimal() else 0, value

    def _prepare(self) -> None:
        self._user_index = {user: i for i, user in enumerate(self._users)}
        self._item_index = {item: i for i, item in enumerate(self._items)}

    def fit(
        self,
        interactions: Iterable[Interaction],
        *,
        validation_score: Callable[["SVDRecommender"], float] | None = None,
    ) -> "SVDRecommender":
        """Shuffle canonical observed pairs per epoch; restore the first best checkpoint."""
        rows = list(interactions)
        if not rows or any(row.proxy_score is None for row in rows):
            raise ValueError("SVD requires non-empty train interactions with proxy_score")
        if len({(row.user_id, row.item_id) for row in rows}) != len(rows):
            raise ValueError("Duplicate user-artist pair")
        self._users = sorted({row.user_id for row in rows}, key=self._id_key)
        self._items = sorted({row.item_id for row in rows}, key=self._id_key)
        self._prepare()
        rows.sort(key=lambda row: (self._user_index[row.user_id], self._item_index[row.item_id]))
        user_indices = np.array([self._user_index[row.user_id] for row in rows], dtype=int)
        item_indices = np.array([self._item_index[row.item_id] for row in rows], dtype=int)
        targets = np.array([row.proxy_score for row in rows], dtype=np.float64)
        self._ratings = csr_matrix(
            (targets, (user_indices, item_indices)), shape=(len(self._users), len(self._items))
        )
        self._global_mean = float(targets.mean())
        rng = np.random.Generator(np.random.PCG64(self.seed))
        self._user_bias = np.zeros(len(self._users), dtype=np.float64)
        self._item_bias = np.zeros(len(self._items), dtype=np.float64)
        self._user_factors = rng.normal(0, self.init_std, (len(self._users), self.latent_factors))
        self._item_factors = rng.normal(0, self.init_std, (len(self._items), self.latent_factors))
        parameters = (self._user_bias, self._item_bias, self._user_factors, self._item_factors)
        user_counts = np.bincount(user_indices, minlength=len(self._users))
        item_counts = np.bincount(item_indices, minlength=len(self._items))
        self.learning_curve, self.best_epoch = [], 0
        best_score, stale = -float("inf"), 0
        checkpoint: tuple[NDArray[np.float64], ...] | None = None
        self.stop_reason = "max_epochs" if validation_score else "max_epochs_no_validation"
        rate, reg = self.learning_rate, self.regularization
        for epoch in range(1, self.max_epochs + 1):
            # ponytail: sequential SGD; compile only if measured tuning cost needs it.
            for index in rng.permutation(len(rows)):
                user, item = user_indices[index], item_indices[index]
                p, q = self._user_factors[user], self._item_factors[item]
                error = targets[index] - (
                    self._global_mean + self._user_bias[user] + self._item_bias[item] + p @ q
                )
                old_p = p.copy()
                self._user_bias[user] += rate * (error - reg * self._user_bias[user])
                self._item_bias[item] += rate * (error - reg * self._item_bias[item])
                p += rate * (error * q - reg * p)
                q += rate * (error * old_p - reg * q)
            predicted = (
                self._global_mean
                + self._user_bias[user_indices]
                + self._item_bias[item_indices]
                + np.einsum(
                    "ij,ij->i", self._user_factors[user_indices], self._item_factors[item_indices]
                )
            )
            sse = float(np.square(targets - predicted).sum())
            penalty = float(
                user_counts @ (self._user_bias**2 + np.square(self._user_factors).sum(axis=1))
                + item_counts @ (self._item_bias**2 + np.square(self._item_factors).sum(axis=1))
            )
            if not isfinite(sse + penalty) or any(not np.isfinite(a).all() for a in parameters):
                raise FloatingPointError("Non-finite SGD parameters or training loss")
            score = float(validation_score(self)) if validation_score is not None else None
            if score is not None and (not isfinite(score) or not 0 <= score <= 1):
                raise ValueError("Validation NDCG@10 must be finite and in [0, 1]")
            improved = score is None or score > best_score
            if improved:
                self.best_epoch, stale = epoch, 0
                if score is not None:
                    best_score = score
                    checkpoint = tuple(array.copy() for array in parameters)
            else:
                stale += 1
            self.learning_curve.append(
                {
                    "epoch": epoch,
                    "train_proxy_rmse": float(np.sqrt(sse / len(rows))),
                    "regularized_objective": 0.5 * (sse + reg * penalty),
                    "validation_ndcg_at_10": score,
                    "improved": improved,
                }
            )
            if validation_score is not None and stale >= self.patience:
                self.stop_reason = "patience"
                break
        if checkpoint is not None:
            for array, best in zip(parameters, checkpoint, strict=True):
                array[:] = best
        return self

    def _score_catalog(self, user_id: str) -> NDArray[np.float64]:
        if not self._users:
            raise RuntimeError("Fit SVD before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        scores = self._global_mean + self._item_bias.copy()
        if user_id in self._user_index:
            user = self._user_index[user_id]
            scores += self._user_bias[user] + self._item_factors @ self._user_factors[user]
        return scores

    def predict(self, user_id: str, item_id: str) -> float:
        """Return an unclipped score; unknown users retain only mean and learned item bias."""
        if not self._users:
            raise RuntimeError("Fit SVD before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the train catalog")
        item = self._item_index[item_id]
        score = self._global_mean + self._item_bias[item]
        if user_id in self._user_index:
            user = self._user_index[user_id]
            score += self._user_bias[user] + self._user_factors[user] @ self._item_factors[item]
        return float(score)

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Rank the full unseen train catalog using rounded keys and numeric ID ties."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        scores = self._score_catalog(user_id)
        excluded = {self._item_index[item] for item in seen_item_ids if item in self._item_index}
        if user_id in self._user_index:
            excluded.update(self._ratings.getrow(self._user_index[user_id]).indices)
        candidates = np.array([i for i in range(len(self._items)) if i not in excluded], dtype=int)
        ranked = candidates[
            np.argsort(-np.round(scores[candidates], NUMERIC_TIE_DECIMALS), kind="stable")[:k]
        ]
        reason = "svd" if user_id in self._user_index else "svd_item_bias_cold_start"
        return [Recommendation(self._items[i], float(scores[i]), reason) for i in ranked]

    def save(self, directory: Path) -> None:
        """Write a new checkpoint of factors, biases, train observations and learning history."""
        if not self._users:
            raise RuntimeError("Fit SVD before saving")
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "ratings.npz", self._ratings)
        np.savez_compressed(
            directory / "parameters.npz",
            user_bias=self._user_bias,
            item_bias=self._item_bias,
            user_factors=self._user_factors,
            item_factors=self._item_factors,
        )
        state = {
            "schema_version": 1,
            "model": "svd",
            "numeric_tie_decimals": NUMERIC_TIE_DECIMALS,
            "config": {
                name: getattr(self, name)
                for name in [
                    "latent_factors",
                    "learning_rate",
                    "regularization",
                    "max_epochs",
                    "patience",
                    "seed",
                    "init_std",
                ]
            },
            "users": self._users,
            "items": self._items,
            "global_mean": self._global_mean,
            "best_epoch": self.best_epoch,
            "stop_reason": self.stop_reason,
            "learning_curve": self.learning_curve,
            "sha256": {
                name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in ["ratings.npz", "parameters.npz"]
            },
        }
        with (directory / "state.json").open("x", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, allow_nan=False)
            handle.write("\n")

    @classmethod
    def load(cls, directory: Path) -> "SVDRecommender":
        """Restore numeric state without fit, gradients or epoch selection."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if (
            state.get("schema_version") != 1
            or state.get("model") != "svd"
            or state.get("numeric_tie_decimals") != NUMERIC_TIE_DECIMALS
        ):
            raise ValueError("Unsupported SVD model schema")
        for name in ["ratings.npz", "parameters.npz"]:
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != state["sha256"][name]:
                raise ValueError(f"Model checksum mismatch: {name}")
        model = cls(**state["config"])
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
        with np.load(directory / "parameters.npz", allow_pickle=False) as arrays:
            for name in ["user_bias", "item_bias", "user_factors", "item_factors"]:
                setattr(model, f"_{name}", np.asarray(arrays[name], dtype=np.float64))
        for array, shape in [
            (model._user_bias, (len(model._users),)),
            (model._item_bias, (len(model._items),)),
            (model._user_factors, (len(model._users), model.latent_factors)),
            (model._item_factors, (len(model._items), model.latent_factors)),
        ]:
            if array.shape != shape or not np.isfinite(array).all():
                raise ValueError("Invalid model parameters")
        if (
            model._ratings.shape != (len(model._users), len(model._items))
            or not model._ratings.has_canonical_format
            or not np.isin(model._ratings.data, [1, 2, 3, 4, 5]).all()
            or (np.diff(model._ratings.indptr) == 0).any()
            or (np.asarray(model._ratings.getnnz(axis=0)) == 0).any()
            or state["global_mean"] != float(model._ratings.data.mean())
        ):
            raise ValueError("Invalid train observations or mean")
        model._global_mean = state["global_mean"]
        model.learning_curve, model.best_epoch = state["learning_curve"], state["best_epoch"]
        model.stop_reason = state["stop_reason"]
        if (
            not model.learning_curve
            or len(model.learning_curve) > model.max_epochs
            or not 1 <= model.best_epoch <= len(model.learning_curve)
            or [row["epoch"] for row in model.learning_curve]
            != list(range(1, len(model.learning_curve) + 1))
        ):
            raise ValueError("Invalid checkpoint history")
        model._prepare()
        return model
