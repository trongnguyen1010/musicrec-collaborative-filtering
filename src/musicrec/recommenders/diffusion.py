"""Sparse LastFM reproduction of Deng (2022), equations 1, 2 and code equation 5.

The author's active cosine/max-min+mean branch is the reference for AIProbS.
Catalogs may include RecBole's padding at index zero. No held-out edge is fitted.
"""

from collections.abc import Iterable, Sequence
from typing import Any, Literal, cast

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
Variant = Literal["pure_dhc", "probs", "aiprobs"]


def dhc_features(adjacency: sparse.csr_matrix) -> FloatArray:
    """Synchronous H-index updates, excluding the repeated converged column."""
    current = np.asarray(adjacency.sum(axis=1)).ravel().astype(np.float64)
    features = [current]
    while True:
        updated = np.zeros_like(current)
        for node in range(adjacency.shape[0]):
            neighbors = adjacency.indices[adjacency.indptr[node] : adjacency.indptr[node + 1]]
            values = np.sort(current[neighbors])[::-1]
            updated[node] = np.count_nonzero(values >= np.arange(1, len(values) + 1))
        if np.array_equal(updated, current):
            return np.stack(features, axis=1)
        features.append(updated)
        current = updated


def normalize_edges(weights: sparse.csr_matrix, axis: int) -> sparse.csr_matrix:
    """Author's min-max then sum normalization, including implicit zeros."""
    coordinates = weights.tocoo(copy=True)
    indices = coordinates.col if axis == 0 else coordinates.row
    minimum = weights.min(axis=axis).toarray().ravel()
    maximum = weights.max(axis=axis).toarray().ravel()
    span = maximum - minimum
    valid = span[indices] != 0
    coordinates.data[valid] = (coordinates.data[valid] - minimum[indices[valid]]) / span[
        indices[valid]
    ]
    normalized = coordinates.tocsr()
    totals = np.asarray(normalized.sum(axis=axis)).ravel()
    inverse = np.divide(1.0, totals, out=np.zeros_like(totals), where=totals != 0)
    if axis == 0:
        return sparse.csr_matrix(normalized @ sparse.diags(inverse))
    return sparse.csr_matrix(sparse.diags(inverse) @ normalized)


class DiffusionRecommender(Recommender):
    """Pure-DHC, ProbS or AIProbS with an explicit, fixed evaluation catalog."""

    def __init__(self, variant: Variant, user_ids: Sequence[str], item_ids: Sequence[str]):
        if variant not in {"pure_dhc", "probs", "aiprobs"}:
            raise ValueError(f"Unknown diffusion variant: {variant}")
        if len(set(user_ids)) != len(user_ids) or len(set(item_ids)) != len(item_ids):
            raise ValueError("Catalog IDs must be unique")
        self.variant = variant
        self.user_ids = list(user_ids)
        self.item_ids = list(item_ids)
        self.user_index = {value: i for i, value in enumerate(user_ids)}
        self.item_index = {value: i for i, value in enumerate(item_ids)}
        self.matrix: sparse.csr_matrix | None = None
        self.features: FloatArray | None = None
        self.w_user: sparse.csr_matrix | None = None
        self.w_item: sparse.csr_matrix | None = None

    def fit(self, interactions: Iterable[Interaction]) -> "DiffusionRecommender":
        pairs = [(self.user_index[x.user_id], self.item_index[x.item_id]) for x in interactions]
        if not pairs:
            raise ValueError("Training interactions must not be empty")
        coordinates = np.asarray(pairs, dtype=np.int64)
        matrix = sparse.csr_matrix(
            (np.ones(len(pairs)), coordinates.T), shape=(len(self.user_ids), len(self.item_ids))
        )
        matrix.data[:] = 1.0
        return self.fit_matrix(matrix)

    def fit_matrix(self, matrix: sparse.csr_matrix) -> "DiffusionRecommender":
        """Fit an already validated binary matrix in the supplied catalog order."""
        if matrix.shape != (len(self.user_ids), len(self.item_ids)):
            raise ValueError("Training matrix does not match catalog")
        if not np.isfinite(matrix.data).all() or not (matrix.data == 1).all():
            raise ValueError("Expected a finite binary adjacency")
        self.matrix = matrix.astype(np.float64).tocsr(copy=True)
        if self.variant == "probs":
            rows = np.asarray(self.matrix.sum(axis=1)).ravel()
            cols = np.asarray(self.matrix.sum(axis=0)).ravel()
            r_inv = np.divide(1.0, rows, out=np.zeros_like(rows), where=rows != 0)
            c_inv = np.divide(1.0, cols, out=np.zeros_like(cols), where=cols != 0)
            self.w_user = (sparse.diags(r_inv) @ self.matrix).tocsr()
            self.w_item = (self.matrix @ sparse.diags(c_inv)).tocsr()
            return self
        blocks: list[list[sparse.spmatrix[Any] | None]] = [
            [None, self.matrix],
            [self.matrix.T, None],
        ]
        graph = cast(sparse.csr_matrix, sparse.bmat(blocks, format="csr"))
        self.features = dhc_features(graph)
        if self.variant == "aiprobs":
            edge = self.matrix.tocoo()
            user = self.features[edge.row]
            item = self.features[len(self.user_ids) + edge.col]
            similarity = np.einsum("ij,ij->i", user, item)
            similarity /= np.linalg.norm(user, axis=1) * np.linalg.norm(item, axis=1) + 1e-24
            weights = sparse.csr_matrix((similarity, (edge.row, edge.col)), shape=matrix.shape)
            self.w_user = normalize_edges(weights, axis=1)
            self.w_item = normalize_edges(weights, axis=0)
        return self

    def score_batch(self, users: IntArray) -> FloatArray:
        """Score at most one user batch without allocating an item-item matrix."""
        if self.matrix is None:
            raise RuntimeError("Model has not been fitted")
        if self.variant == "pure_dhc":
            assert self.features is not None
            user = self.features[users]
            item = self.features[len(self.user_ids) :]
            return np.asarray(
                (user @ item.T)
                / (
                    np.linalg.norm(user, axis=1)[:, None] * np.linalg.norm(item, axis=1)[None, :]
                    + 1e-24
                ),
                dtype=np.float64,
            )
        assert self.w_user is not None and self.w_item is not None
        return np.asarray(
            ((self.matrix[users] @ self.w_item.T) @ self.w_user).toarray(), dtype=np.float64
        )

    def predict(self, user_id: str, item_id: str) -> float:
        users = np.asarray([self.user_index[user_id]], dtype=np.int64)
        return float(self.score_batch(users)[0, self.item_index[item_id]])

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        if k <= 0:
            raise ValueError("k must be greater than zero")
        scores = self.score_batch(np.asarray([self.user_index[user_id]], dtype=np.int64))[0]
        eligible = [
            i
            for i, item in enumerate(self.item_ids)
            if item != "[PAD]" and item not in seen_item_ids
        ]
        ranked = sorted(eligible, key=lambda i: (-float(scores[i]), self.item_ids[i]))[:k]
        return [Recommendation(self.item_ids[i], float(scores[i]), self.variant) for i in ranked]
