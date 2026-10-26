"""Train-only greedy relevance, redundancy and popularity re-ranking over a fixed pool."""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csc_matrix, load_npz, save_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


@dataclass(frozen=True)
class CandidatePool:
    """Base order and train-derived features, shared unchanged across all grid variants."""

    recommendations: list[Recommendation]
    relevance: NDArray[np.float64]
    popularity: NDArray[np.float64]
    similarity: NDArray[np.float64]


def rerank_candidates(
    pool: CandidatePool, k: int, lambda_weight: float, beta: float
) -> list[Recommendation]:
    """Select greedily; preserve base scores and break objective ties by base rank."""
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    if not isfinite(lambda_weight) or not 0 <= lambda_weight <= 1:
        raise ValueError("lambda_weight must be finite and in [0, 1]")
    if not isfinite(beta) or beta < 0:
        raise ValueError("beta must be finite and non-negative")
    if lambda_weight == 1 and beta == 0:
        return pool.recommendations[:k]
    n = len(pool.recommendations)
    selected: list[int] = []
    redundancy = np.zeros(n, dtype=np.float64)
    available = np.ones(n, dtype=bool)
    fixed = lambda_weight * pool.relevance - beta * pool.popularity
    for _ in range(min(k, n)):
        utility = np.round(fixed - (1 - lambda_weight) * redundancy, 12)
        utility[~available] = -np.inf
        index = int(np.argmax(utility))
        selected.append(index)
        available[index] = False
        redundancy = np.maximum(redundancy, pool.similarity[:, index])
    return [
        Recommendation(
            pool.recommendations[i].item_id,
            pool.recommendations[i].score,
            f"m1_lambda={lambda_weight:g}_beta={beta:g};score=raw_base;"
            f"base={pool.recommendations[i].reason}",
        )
        for i in selected
    ]


class M1Recommender(Recommender):
    """Wrap an already fitted base; fit learns binary train statistics without fitting it."""

    def __init__(
        self,
        base: Recommender,
        *,
        candidate_size: int = 100,
        lambda_weight: float = 1.0,
        beta: float = 0.0,
    ) -> None:
        if type(candidate_size) is not int or candidate_size <= 0:
            raise ValueError("candidate_size must be a positive integer")
        if not isfinite(lambda_weight) or not 0 <= lambda_weight <= 1:
            raise ValueError("lambda_weight must be finite and in [0, 1]")
        if not isfinite(beta) or beta < 0:
            raise ValueError("beta must be finite and non-negative")
        self.base = base
        self.candidate_size, self.lambda_weight, self.beta = candidate_size, lambda_weight, beta
        self._users: list[str] = []
        self._items: list[str] = []
        self._binary: csc_matrix[np.float64]

    def _prepare(self) -> None:
        self._item_index = {item: i for i, item in enumerate(self._items)}
        self._user_index = {user: i for i, user in enumerate(self._users)}
        self._histories = self._binary.tocsr()
        self._listeners = np.asarray(self._binary.sum(axis=0)).ravel()
        self._popularity = np.log1p(self._listeners) / np.log1p(self._listeners.max())

    def fit(self, interactions: Iterable[Interaction]) -> "M1Recommender":
        """Ignore listening magnitude; duplicates are rejected rather than double-counted."""
        rows = list(interactions)
        if not rows or len({(r.user_id, r.item_id) for r in rows}) != len(rows):
            raise ValueError("Expected non-empty unique train user-artist pairs")
        self._users = sorted({r.user_id for r in rows})
        self._items = sorted({r.item_id for r in rows})
        users, items = (
            {u: i for i, u in enumerate(self._users)},
            {v: i for i, v in enumerate(self._items)},
        )
        self._binary = csc_matrix(
            (
                np.ones(len(rows)),
                ([users[r.user_id] for r in rows], [items[r.item_id] for r in rows]),
            ),
            shape=(len(users), len(items)),
        )
        self._prepare()
        return self

    def _require_fit(self) -> None:
        if not self._users:
            raise RuntimeError("Fit M1 train statistics before inference")

    def prepare_candidates(self, user_id: str, seen_item_ids: set[str]) -> CandidatePool:
        """Retrieve once, min-max over the full pool, and compute only its small Gram matrix."""
        self._require_fit()
        if not user_id:
            raise ValueError("user_id must be non-empty")
        seen = set(seen_item_ids)
        if user_id in self._user_index:
            seen.update(self._items[i] for i in self._histories[self._user_index[user_id]].indices)
        candidates = self.base.recommend(user_id, self.candidate_size, seen)
        ids = [r.item_id for r in candidates]
        if len(ids) > self.candidate_size or len(ids) != len(set(ids)):
            raise ValueError("Base returned duplicate or excessive candidates")
        if set(ids) & seen or set(ids) - self._item_index.keys():
            raise ValueError("Base returned seen or out-of-catalog candidates")
        scores = np.array([r.score for r in candidates], dtype=np.float64)
        if not np.isfinite(scores).all():
            raise ValueError("Base scores must be finite")
        if not len(ids):
            return CandidatePool(candidates, scores, scores.copy(), np.empty((0, 0)))
        spread = float(np.ptp(scores))
        relevance = (scores - scores.min()) / spread if spread else np.ones(len(scores))
        indices = [self._item_index[item] for item in ids]
        columns = self._binary[:, indices]
        similarity = (columns.T @ columns).toarray()
        similarity /= np.sqrt(np.outer(self._listeners[indices], self._listeners[indices]))
        return CandidatePool(candidates, relevance, self._popularity[indices], similarity)

    def predict(self, user_id: str, item_id: str) -> float:
        """Return the base relevance score; greedy utility depends on the selected prefix."""
        self._require_fit()
        return self.base.predict(user_id, item_id)

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Return greedy order with base scores; scores need not decrease after re-ranking."""
        if type(k) is not int or not 0 < k <= self.candidate_size:
            raise ValueError("k must be a positive integer no larger than candidate_size")
        return rerank_candidates(
            self.prepare_candidates(user_id, seen_item_ids), k, self.lambda_weight, self.beta
        )

    def save(self, directory: Path) -> None:
        """Save numeric train context and parameters; base checkpoint stays separately pinned."""
        self._require_fit()
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "binary.npz", self._binary)
        state = {
            "schema_version": 1,
            "model": "m1",
            "users": self._users,
            "items": self._items,
            "config": {
                "candidate_size": self.candidate_size,
                "lambda_weight": self.lambda_weight,
                "beta": self.beta,
            },
            "binary_sha256": hashlib.sha256((directory / "binary.npz").read_bytes()).hexdigest(),
        }
        (directory / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, directory: Path, *, base: Recommender) -> "M1Recommender":
        """Load context without fit; the caller supplies the matching pinned base checkpoint."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if state.get("schema_version") != 1 or state.get("model") != "m1":
            raise ValueError("Unsupported M1 schema")
        if (
            hashlib.sha256((directory / "binary.npz").read_bytes()).hexdigest()
            != state["binary_sha256"]
        ):
            raise ValueError("M1 binary context checksum mismatch")
        model = cls(base, **state["config"])
        model._users, model._items = state["users"], state["items"]
        if any(
            not ids or any(not isinstance(i, str) or not i for i in ids) or ids != sorted(set(ids))
            for ids in [model._users, model._items]
        ):
            raise ValueError("Invalid M1 mappings")
        model._binary = csc_matrix(load_npz(directory / "binary.npz"))
        if (
            model._binary.shape != (len(model._users), len(model._items))
            or not model._binary.has_canonical_format
            or not np.all(model._binary.data == 1)
            or (model._binary.getnnz(axis=0) == 0).any()
            or (model._binary.getnnz(axis=1) == 0).any()
        ):
            raise ValueError("Invalid binary train context")
        model._prepare()
        return model
