"""PureSVD on zero-filled train values, without centering or learned biases."""

import hashlib
import json
from collections.abc import Iterable
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, load_npz, save_npz
from scipy.sparse.linalg import svds

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender

NUMERIC_TIE_DECIMALS = 12


class PureSVDRecommender(Recommender):
    """Score R V_k V_k.T using leading right singular vectors of sparse train R.

    Observations use the 1-5 proxy, binary presence or log2(1 + count).
    Missing entries are algebraic zeros,
    not observed dislikes. Scores are association strengths, not proxy ratings.
    Unknown users have a zero profile and an explicitly marked ID-order fallback.
    """

    def __init__(
        self,
        latent_factors: int = 32,
        seed: int = 42,
        tolerance: float = 1e-10,
        max_iter: int = 10000,
        representation: str = "proxy_score",
    ) -> None:
        if type(latent_factors) is not int or latent_factors <= 0:
            raise ValueError("latent_factors must be a positive integer")
        if type(seed) is not int or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        if not isfinite(tolerance) or tolerance <= 0:
            raise ValueError("tolerance must be finite and positive")
        if type(max_iter) is not int or max_iter <= 0:
            raise ValueError("max_iter must be a positive integer")
        if representation not in ("proxy_score", "binary", "log_count"):
            raise ValueError("representation must be proxy_score, binary or log_count")
        self.latent_factors, self.seed = latent_factors, seed
        self.tolerance, self.max_iter = float(tolerance), max_iter
        self.representation = representation
        self._users: list[str] = []
        self._items: list[str] = []
        self._ratings: csr_matrix[np.float64]
        self._components: NDArray[np.float64]
        self._user_embeddings: NDArray[np.float64]
        self._singular_values: NDArray[np.float64]
        self.fit_diagnostics: dict[str, float | int] = {}

    @staticmethod
    def _id_key(value: str) -> tuple[bool, int, str]:
        return not value.isdecimal(), int(value) if value.isdecimal() else 0, value

    def _prepare(self) -> None:
        self._user_index = {user: i for i, user in enumerate(self._users)}
        self._item_index = {item: i for i, item in enumerate(self._items)}

    def fit(self, interactions: Iterable[Interaction]) -> "PureSVDRecommender":
        """Decompose canonical train CSR once; no validation fitting or SGD epochs."""
        rows = list(interactions)
        if not rows or (
            self.representation == "proxy_score" and any(row.proxy_score is None for row in rows)
        ):
            raise ValueError("PureSVD requires non-empty train interactions with proxy_score")
        if len({(row.user_id, row.item_id) for row in rows}) != len(rows):
            raise ValueError("Duplicate user-artist pair")
        self._users = sorted({row.user_id for row in rows}, key=self._id_key)
        self._items = sorted({row.item_id for row in rows}, key=self._id_key)
        if self.latent_factors >= min(len(self._users), len(self._items)):
            raise ValueError("latent_factors must be smaller than both train dimensions")
        self._prepare()
        values = np.array([row.proxy_score for row in rows], dtype=np.float64)
        if self.representation == "binary":
            values = np.ones(len(rows), dtype=np.float64)
        if self.representation == "log_count":
            counts = np.array([row.listening_count for row in rows], dtype=np.float64)
            if not np.isfinite(counts).all() or (counts <= 0).any():
                raise ValueError("Log counts require finite positive listening counts")
            values = np.log2(1.0 + counts)
        if not np.isfinite(values).all() or (values <= 0).any():
            raise ValueError("PureSVD observations must be finite and positive")
        self._ratings = csr_matrix(
            (
                values,
                (
                    [self._user_index[row.user_id] for row in rows],
                    [self._item_index[row.item_id] for row in rows],
                ),
            ),
            shape=(len(self._users), len(self._items)),
        )
        self._ratings.sort_indices()
        initial = np.random.Generator(np.random.PCG64(self.seed)).standard_normal(
            min(self._ratings.shape)
        )
        _, singular, components = svds(
            self._ratings,
            k=self.latent_factors,
            solver="arpack",
            which="LM",
            v0=initial,
            tol=self.tolerance,
            maxiter=self.max_iter,
        )
        order = np.argsort(-singular, kind="stable")
        self._singular_values = np.asarray(singular[order], dtype=np.float64)
        self._components = np.array(components[order], dtype=np.float64, order="C")
        for component in self._components:
            if component[np.argmax(np.abs(component))] < 0:
                component *= -1
        self._user_embeddings = np.asarray(self._ratings @ self._components.T)
        orthogonality = float(
            np.abs(self._components @ self._components.T - np.eye(self.latent_factors)).max()
        )
        expected = self._components.T * self._singular_values**2
        residual = float(
            np.linalg.norm(self._ratings.T @ self._user_embeddings - expected)
            / np.linalg.norm(expected)
        )
        if (
            not np.isfinite(self._user_embeddings).all()
            or not isfinite(residual)
            or residual > 1e-8
            or orthogonality > 1e-8
        ):
            raise RuntimeError("PureSVD failed numerical residual or orthogonality checks")
        self.fit_diagnostics = {
            "max_orthogonality_error": orthogonality,
            "relative_gram_residual": residual,
            "retained_frobenius_energy_fraction": float(
                np.square(self._singular_values).sum() / self._ratings.power(2).sum()
            ),
        }
        return self

    def _score_catalog(self, user_id: str) -> NDArray[np.float64]:
        if not self._users:
            raise RuntimeError("Fit PureSVD before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if user_id not in self._user_index:
            return np.zeros(len(self._items), dtype=np.float64)
        return np.asarray(self._user_embeddings[self._user_index[user_id]] @ self._components)

    def predict(self, user_id: str, item_id: str) -> float:
        """Return an unclipped association score, or zero for an unknown user profile."""
        if not self._users:
            raise RuntimeError("Fit PureSVD before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the train catalog")
        if user_id not in self._user_index:
            return 0.0
        return float(
            self._user_embeddings[self._user_index[user_id]]
            @ self._components[:, self._item_index[item_id]]
        )

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Rank unseen train items with rounded score keys and numeric mapping ties."""
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
        reason = "pure_svd" if user_id in self._user_index else "pure_svd_zero_profile_cold_start"
        return [Recommendation(self._items[i], float(scores[i]), reason) for i in ranked]

    def save(self, directory: Path) -> None:
        """Save a new numeric projection artifact without overwriting existing runs."""
        if not self._users:
            raise RuntimeError("Fit PureSVD before saving")
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "ratings.npz", self._ratings)
        np.savez_compressed(
            directory / "projection.npz",
            components=self._components,
            user_embeddings=self._user_embeddings,
            singular_values=self._singular_values,
        )
        state: dict[str, Any] = {
            "schema_version": 1,
            "model": "pure_svd",
            "numeric_tie_decimals": NUMERIC_TIE_DECIMALS,
            "config": {
                name: getattr(self, name)
                for name in [
                    "latent_factors",
                    "seed",
                    "tolerance",
                    "max_iter",
                ]
            },
            "users": self._users,
            "items": self._items,
            "fit_diagnostics": self.fit_diagnostics,
            "sha256": {
                name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in ["ratings.npz", "projection.npz"]
            },
        }
        # Keep existing proxy artifacts byte-compatible with the Step 12 control.
        if self.representation != "proxy_score":
            state["config"]["representation"] = self.representation
        with (directory / "state.json").open("x", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, allow_nan=False)
            handle.write("\n")

    @classmethod
    def load(cls, directory: Path) -> "PureSVDRecommender":
        """Restore checked saved projections without fitting or decomposing the matrix."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if (
            state.get("schema_version") != 1
            or state.get("model") != "pure_svd"
            or state.get("numeric_tie_decimals") != NUMERIC_TIE_DECIMALS
        ):
            raise ValueError("Unsupported PureSVD model schema")
        for name in ["ratings.npz", "projection.npz"]:
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
        with np.load(directory / "projection.npz", allow_pickle=False) as arrays:
            model._components = np.asarray(arrays["components"], dtype=np.float64)
            model._user_embeddings = np.asarray(arrays["user_embeddings"], dtype=np.float64)
            model._singular_values = np.asarray(arrays["singular_values"], dtype=np.float64)
        for array, shape in [
            (model._components, (model.latent_factors, len(model._items))),
            (model._user_embeddings, (len(model._users), model.latent_factors)),
            (model._singular_values, (model.latent_factors,)),
        ]:
            if array.shape != shape or not np.isfinite(array).all():
                raise ValueError("Invalid projection arrays")
        if (
            model.latent_factors >= min(len(model._users), len(model._items))
            or model._ratings.shape != (len(model._users), len(model._items))
            or not model._ratings.has_canonical_format
            or not np.isfinite(model._ratings.data).all()
            or (model._ratings.data <= 0).any()
            or (
                model.representation == "proxy_score"
                and not np.isin(model._ratings.data, [1, 2, 3, 4, 5]).all()
            )
            or (model.representation == "binary" and (model._ratings.data != 1).any())
            or (np.diff(model._ratings.indptr) == 0).any()
            or (np.asarray(model._ratings.getnnz(axis=0)) == 0).any()
            or (model._singular_values < 0).any()
            or (np.diff(model._singular_values) > 0).any()
            or not np.allclose(
                model._components @ model._components.T,
                np.eye(model.latent_factors),
                rtol=0,
                atol=1e-8,
            )
            or not np.allclose(
                model._user_embeddings,
                np.asarray(model._ratings @ model._components.T),
                rtol=0,
                atol=1e-10,
            )
        ):
            raise ValueError("Invalid train observations or projection")
        model.fit_diagnostics = state["fit_diagnostics"]
        model._prepare()
        return model
