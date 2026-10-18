"""Sparse CF and factor baselines sharing raw-count contracts and stable ranking."""

import json
from abc import abstractmethod
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import sparse
from scipy.special import expit
from sklearn.utils.extmath import randomized_svd

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender

FloatArray = NDArray[np.float64]


def top_indices(scores: FloatArray, k: int) -> NDArray[np.int64]:
    """Stable top-K for a lexically sorted catalog, including ties at the boundary."""
    if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
        raise ValueError("k must be positive")
    eligible = np.flatnonzero(np.isfinite(scores))
    k = min(k, len(eligible))
    if not k:
        return np.asarray([], dtype=np.int64)
    threshold = np.partition(scores[eligible], -k)[-k]
    above = np.flatnonzero(scores > threshold)
    tied = np.flatnonzero(scores == threshold)[: k - len(above)]
    selected = np.concatenate([above, tied])
    return np.asarray(selected[np.lexsort((selected, -scores[selected]))], dtype=np.int64)


class MatrixModel(Recommender):
    """Common sparse input, profile inference, ranking and safe NPZ persistence."""

    kind = "base"

    def __init__(self, **params: Any):
        self.params = params
        self.monitor: Callable[[], float] | None = None
        self.history: list[dict[str, float]] = []

    def prepare(self, interactions: Iterable[Interaction]) -> None:
        """Fit proxy thresholds only on the supplied training observations."""
        rows = list(interactions)
        if not rows:
            raise ValueError("Empty training data")
        if len({(r.user_id, r.item_id) for r in rows}) != len(rows):
            raise ValueError("Models require duplicate pairs to be aggregated first")
        self.users = sorted({r.user_id for r in rows})
        self.items = sorted({r.item_id for r in rows})
        self.user_index = {u: i for i, u in enumerate(self.users)}
        self.item_index = {i: j for j, i in enumerate(self.items)}
        u = np.array([self.user_index[r.user_id] for r in rows])
        i = np.array([self.item_index[r.item_id] for r in rows])
        counts = np.array([r.listening_count for r in rows], dtype=np.float64)
        self.raw = sparse.csr_matrix((counts, (u, i)), shape=(len(self.users), len(self.items)))
        self.thresholds = np.asarray(
            np.quantile(np.log2(1 + counts), [0.2, 0.4, 0.6, 0.8], method="linear"),
            dtype=np.float64,
        )
        ratings = 1 + np.searchsorted(self.thresholds, np.log2(1 + counts), side="left")
        self.matrix = sparse.csr_matrix((ratings.astype(float), (u, i)), shape=self.raw.shape)
        self.popularity = np.asarray(self.raw.getnnz(axis=0), dtype=float)

    @abstractmethod
    def fit(self, interactions: Iterable[Interaction]) -> "MatrixModel":
        """Fit only the supplied train data."""

    @abstractmethod
    def scores(self, user_id: str) -> FloatArray:
        """Score the entire train catalog without masking."""

    def predict(self, user_id: str, item_id: str) -> float:
        """Return one score; unknown artists have no learned score."""
        if item_id not in self.item_index:
            return 0.0
        return float(self.scores(user_id)[self.item_index[item_id]])

    def fallback_for(self, user_id: str) -> bool:
        """Report when the model has no personalized scoring path."""
        return user_id not in self.user_index

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Mask seen IDs and break score ties by stable artist ID order."""
        scores = self.scores(user_id).copy()
        if not np.isfinite(scores).all():
            raise ValueError("Nonfinite model score")
        for item in seen_item_ids:
            if item in self.item_index:
                scores[self.item_index[item]] = -np.inf
        reason = "popularity_fallback" if self.fallback_for(user_id) else self.kind
        return [
            Recommendation(self.items[j], float(scores[j]), reason) for j in top_indices(scores, k)
        ]

    def save(self, path: Path) -> None:
        """Save numeric state as NPZ; loading never enables pickle execution."""
        arrays: dict[str, Any] = {
            "format": np.array("musicrec_matrix_v1"),
            "kind": np.array(self.kind),
            "params": np.array(json.dumps(self.params)),
            "users": np.array(self.users),
            "items": np.array(self.items),
            "thresholds": self.thresholds,
            "popularity": self.popularity,
        }
        for name in ("raw", "matrix", "neighbors"):
            if hasattr(self, name):
                value = getattr(self, name).tocsr()
                for part in ("data", "indices", "indptr"):
                    arrays[f"{name}_{part}"] = getattr(value, part)
                arrays[f"{name}_shape"] = np.array(value.shape)
        for name in (
            "user_factors",
            "item_factors",
            "user_bias",
            "item_bias",
            "means",
            "global_mean",
        ):
            if hasattr(self, name):
                arrays[name] = np.asarray(getattr(self, name))
        with path.open("xb") as stream:
            np.savez_compressed(stream, **arrays)

    @classmethod
    def load(cls, path: Path) -> "MatrixModel":
        """Load known model kinds and numeric arrays only."""
        with np.load(path, allow_pickle=False) as data:
            if str(data["format"]) != "musicrec_matrix_v1":
                raise ValueError("Unsupported model schema")
            model = make_model(str(data["kind"]), json.loads(str(data["params"])))
            model.users = data["users"].tolist()
            model.items = data["items"].tolist()
            model.user_index = {u: i for i, u in enumerate(model.users)}
            model.item_index = {i: j for j, i in enumerate(model.items)}
            model.thresholds = data["thresholds"].copy()
            model.popularity = data["popularity"].copy()
            for name in ("raw", "matrix", "neighbors"):
                if f"{name}_data" in data:
                    setattr(
                        model,
                        name,
                        sparse.csr_matrix(
                            (data[f"{name}_data"], data[f"{name}_indices"], data[f"{name}_indptr"]),
                            shape=tuple(data[f"{name}_shape"]),
                        ),
                    )
            for name in (
                "user_factors",
                "item_factors",
                "user_bias",
                "item_bias",
                "means",
                "global_mean",
            ):
                if name in data:
                    if not np.isfinite(data[name]).all():
                        raise ValueError("Nonfinite model artifact")
                    setattr(model, name, data[name].copy())
        return model


class NeighborhoodModel(MatrixModel):
    """Cosine neighborhoods with positive weights, shrinkage and minimum overlap."""

    def fallback_for(self, user_id: str) -> bool:
        if user_id not in self.user_index:
            return True
        user = self.user_index[user_id]
        if self.kind == "user_cf":
            return self.neighbors.getrow(user).nnz == 0
        return self.neighbors[:, self.raw.getrow(user).indices].nnz == 0

    def fit(self, interactions: Iterable[Interaction]) -> "NeighborhoodModel":
        self.prepare(interactions)
        vectors = self.matrix if self.kind == "user_cf" else self.matrix.T.tocsr()
        binary = (vectors > 0).astype(float)
        norms = np.sqrt(np.asarray(vectors.multiply(vectors).sum(axis=1)).ravel())
        normalized = sparse.diags(1 / np.maximum(norms, 1e-15)) @ vectors
        rows: list[int] = []
        cols: list[int] = []
        values: list[float] = []
        limit = int(self.params.get("neighbors", 40))
        shrink = float(self.params.get("shrinkage", 10))
        minimum = int(self.params.get("min_common", 1))
        for start in range(0, vectors.shape[0], 256):
            sim = (normalized[start : start + 256] @ normalized.T).toarray()
            common = (binary[start : start + 256] @ binary.T).toarray()
            sim *= np.divide(
                common, common + shrink, out=np.zeros_like(common), where=common + shrink > 0
            )
            sim[common < minimum] = 0
            for offset, scores in enumerate(sim):
                row = start + offset
                scores[row] = 0
                scores[scores <= 0] = -np.inf
                chosen = top_indices(scores, limit)
                rows.extend([row] * len(chosen))
                cols.extend(chosen.tolist())
                values.extend(scores[chosen].tolist())
        self.neighbors = sparse.csr_matrix(
            (values, (rows, cols)), shape=(vectors.shape[0], vectors.shape[0])
        )
        self.means = np.asarray(self.matrix.sum(axis=1)).ravel() / np.maximum(
            self.matrix.getnnz(axis=1), 1
        )
        return self

    def from_profile(self, profile: dict[str, float]) -> FloatArray:
        """Infer ItemCF scores from only the provided raw-count profile."""
        valid = [
            (self.item_index[i], count) for i, count in profile.items() if i in self.item_index
        ]
        if not valid:
            return self.popularity.copy()
        idx = np.array([i for i, _ in valid])
        counts = np.array([c for _, c in valid])
        rating = 1 + np.searchsorted(self.thresholds, np.log2(1 + counts), side="left")
        weights = self.neighbors[:, idx]
        denom = np.asarray(weights.sum(axis=1)).ravel()
        if not (denom > 0).any():
            return self.popularity.copy()
        return np.asarray(
            np.divide(weights @ rating, denom, out=np.zeros_like(denom), where=denom > 0),
            dtype=float,
        )

    def scores(self, user_id: str) -> FloatArray:
        if user_id not in self.user_index:
            return self.popularity.copy()
        user = self.user_index[user_id]
        if self.kind == "item_cf":
            raw = self.raw.getrow(user)
            return self.from_profile(
                {self.items[i]: float(c) for i, c in zip(raw.indices, raw.data, strict=True)}
            )
        neighbors = self.neighbors.getrow(user)
        if not neighbors.nnz:
            return self.popularity.copy()
        rating = self.matrix[neighbors.indices]
        observed = (rating > 0).astype(float)
        centered = rating - sparse.diags(self.means[neighbors.indices]) @ observed
        denom = np.asarray(neighbors.data @ observed).ravel()
        scores = self.means[user] + np.divide(
            np.asarray(neighbors.data @ centered).ravel(),
            denom,
            out=np.zeros_like(denom),
            where=denom > 0,
        )
        scores[denom == 0] = 0
        return np.asarray(scores, dtype=float)


class UserCFRecommender(NeighborhoodModel):
    """User cosine neighborhoods with train-only observed-rating means."""

    kind = "user_cf"


class ItemCFRecommender(NeighborhoodModel):
    """Item cosine neighborhoods supporting new raw-count histories."""

    kind = "item_cf"


class PureSVDRecommender(MatrixModel):
    """Randomized truncated SVD and projection of the proxy-rating matrix."""

    kind = "pure_svd"

    def fit(self, interactions: Iterable[Interaction]) -> "PureSVDRecommender":
        self.prepare(interactions)
        dimensions = int(self.params.get("factors", 32))
        if not 0 < dimensions < min(self.matrix.shape):
            raise ValueError("Invalid factor dimension")
        _, _, vectors = randomized_svd(
            self.matrix,
            n_components=dimensions,
            n_iter=5,
            random_state=int(self.params.get("seed", 42)),
        )
        self.item_factors = np.asarray(vectors.T, dtype=float)
        self.user_factors = np.asarray(self.matrix @ self.item_factors, dtype=float)
        return self

    def scores(self, user_id: str) -> FloatArray:
        if user_id not in self.user_index:
            return self.popularity.copy()
        return np.asarray(
            self.item_factors @ self.user_factors[self.user_index[user_id]], dtype=float
        )


class FactorModel(MatrixModel):
    """Minibatch SGD for biased observed-rating MF or pairwise binary BPR."""

    def fit(self, interactions: Iterable[Interaction]) -> "FactorModel":
        self.prepare(interactions)
        rng = np.random.default_rng(int(self.params.get("seed", 42)))
        dimensions = int(self.params.get("factors", 32))
        self.user_factors = rng.normal(0, 0.05, (len(self.users), dimensions))
        self.item_factors = rng.normal(0, 0.05, (len(self.items), dimensions))
        self.user_bias = np.zeros(len(self.users))
        self.item_bias = np.zeros(len(self.items))
        self.global_mean = float(self.matrix.data.mean())
        coo = self.matrix.tocoo()
        users = coo.row
        items = coo.col
        rating = coo.data
        if self.kind == "bpr":
            eligible = self.matrix.getnnz(axis=1) < len(self.items)
            keep = eligible[users]
            users, items, rating = users[keep], items[keep], rating[keep]
            if not len(users):
                raise ValueError("No BPR user has an unobserved train-catalog item")
        user_freq = np.maximum(self.matrix.getnnz(axis=1), 1)
        item_freq = np.maximum(self.matrix.getnnz(axis=0), 1)
        lr = float(self.params.get("learning_rate", 0.01))
        reg = float(self.params.get("regularization", 0.01))
        batch = int(self.params.get("batch_size", 256))
        patience = int(self.params.get("patience", 5))
        best = -np.inf
        wait = 0
        best_state = None
        for epoch in range(int(self.params.get("epochs", 100))):
            order = rng.permutation(len(users))
            loss = 0.0
            for start in range(0, len(order), batch):
                pos = order[start : start + batch]
                u = users[pos]
                i = items[pos]
                p = self.user_factors[u].copy()
                q = self.item_factors[i].copy()
                if self.kind == "bpr":
                    j = rng.integers(0, len(self.items), len(u))
                    occupied = np.asarray(self.matrix[u, j]).ravel() > 0
                    while occupied.any():
                        j[occupied] = rng.integers(0, len(self.items), int(occupied.sum()))
                        occupied = np.asarray(self.matrix[u, j]).ravel() > 0
                    negative = self.item_factors[j].copy()
                    margin = np.sum(p * (q - negative), axis=1)
                    gradient = expit(-margin)[:, None]
                    np.add.at(self.user_factors, u, lr * (gradient * (q - negative) - reg * p))
                    np.add.at(self.item_factors, i, lr * (gradient * p - reg * q))
                    np.add.at(self.item_factors, j, lr * (-gradient * p - reg * negative))
                    loss += float(np.logaddexp(0, -margin).sum())
                else:
                    error = rating[pos] - (
                        self.global_mean
                        + self.user_bias[u]
                        + self.item_bias[i]
                        + np.sum(p * q, axis=1)
                    )
                    np.add.at(
                        self.user_factors,
                        u,
                        lr * (error[:, None] * q - reg * p / user_freq[u, None]),
                    )
                    np.add.at(
                        self.item_factors,
                        i,
                        lr * (error[:, None] * p - reg * q / item_freq[i, None]),
                    )
                    np.add.at(
                        self.user_bias, u, lr * (error - reg * self.user_bias[u] / user_freq[u])
                    )
                    np.add.at(
                        self.item_bias, i, lr * (error - reg * self.item_bias[i] / item_freq[i])
                    )
                    loss += float(np.square(error).sum())
            if not np.isfinite(self.user_factors).all() or not np.isfinite(self.item_factors).all():
                raise ValueError("Factor optimization diverged")
            value = float(self.monitor()) if self.monitor else -loss / len(users)
            self.history.append(
                {"epoch": float(epoch + 1), "loss": loss / len(users), "validation_ndcg": value}
            )
            if value > best + 1e-12:
                best = value
                wait = 0
                best_state = tuple(
                    a.copy()
                    for a in (self.user_factors, self.item_factors, self.user_bias, self.item_bias)
                )
            else:
                wait += 1
            if self.monitor and wait >= patience:
                break
        if best_state is not None:
            self.user_factors, self.item_factors, self.user_bias, self.item_bias = best_state
        return self

    def scores(self, user_id: str) -> FloatArray:
        if user_id not in self.user_index:
            return self.popularity.copy()
        u = self.user_index[user_id]
        scores = self.item_factors @ self.user_factors[u]
        if self.kind == "svd":
            scores = scores + self.global_mean + self.user_bias[u] + self.item_bias
        return np.asarray(scores, dtype=float)


class SVDRecommender(FactorModel):
    """Biased MF on observed 1–5 preference proxies."""

    kind = "svd"


class BPRRecommender(FactorModel):
    """Binary implicit MF with one train-unobserved negative per positive."""

    kind = "bpr"


class RandomRecommender(MatrixModel):
    """Deterministic user-specific random scores on the train catalog."""

    kind = "random"

    def fallback_for(self, user_id: str) -> bool:
        return False

    def fit(self, interactions: Iterable[Interaction]) -> "RandomRecommender":
        self.prepare(interactions)
        return self

    def scores(self, user_id: str) -> FloatArray:
        import hashlib

        seed = int.from_bytes(
            hashlib.sha256(f"{self.params.get('seed', 42)}:{user_id}".encode()).digest()[:8], "big"
        )
        return np.asarray(np.random.default_rng(seed).random(len(self.items)), dtype=float)


def make_model(kind: str, params: dict[str, Any]) -> MatrixModel:
    """Instantiate one of the explicitly supported research baselines."""
    classes = {
        c.kind: c
        for c in (
            RandomRecommender,
            UserCFRecommender,
            ItemCFRecommender,
            SVDRecommender,
            PureSVDRecommender,
            BPRRecommender,
        )
    }
    if kind not in classes:
        raise ValueError(f"Unknown model: {kind}")
    return classes[kind](**params)
