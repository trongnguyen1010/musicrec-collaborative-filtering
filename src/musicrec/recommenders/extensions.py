"""M1 sequential reranking and M2 ItemCF/tag fallback for strictly unseen users."""

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import sparse

from musicrec.configuration import write_json
from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.models import FloatArray, ItemCFRecommender, MatrixModel, top_indices

NDArrayInt = NDArray[np.int64]


def normalized(values: FloatArray) -> FloatArray:
    """Min-max normalize with a zero vector for constant inputs."""
    span = float(np.ptp(values))
    return (values - values.min()) / span if span > 0 else np.zeros_like(values)


class Reranker(Recommender):
    """Greedy relevance minus maximum redundancy and train-listener popularity."""

    def __init__(
        self, base: MatrixModel, candidates: int = 100, weight: float = 1.0, penalty: float = 0.0
    ):
        if candidates < 1 or not 0 <= weight <= 1 or penalty < 0:
            raise ValueError("Invalid M1 configuration")
        self.base = base
        self.candidates = candidates
        self.weight = weight
        self.penalty = penalty
        binary = base.raw.copy()
        binary.data = np.ones_like(binary.data)
        vectors = binary.T.tocsr()
        lengths = np.sqrt(np.asarray(vectors.multiply(vectors).sum(axis=1)).ravel())
        self.vectors = (sparse.diags(1 / np.maximum(lengths, 1e-15)) @ vectors).tocsr()
        self.pop = normalized(np.log1p(base.popularity))

    def fit(self, interactions: Iterable[Interaction]) -> "Reranker":
        """Verify the loaded base catalog; do not refit a tuned base during ablation."""
        if {r.item_id for r in interactions} != set(self.base.items):
            raise ValueError("M1 catalog mismatch")
        return self

    def predict(self, user_id: str, item_id: str) -> float:
        """Return base relevance; sequential selection scores depend on earlier choices."""
        return self.base.predict(user_id, item_id)

    def pool(
        self, user_id: str, seen: set[str], count: int | None = None
    ) -> tuple[NDArrayInt, FloatArray, FloatArray]:
        """Prepare a relevance candidate pool and fixed behavioral cosine matrix."""
        scores = self.base.scores(user_id).copy()
        if not np.isfinite(scores).all():
            raise ValueError("Nonfinite base scores")
        for item in seen:
            if item in self.base.item_index:
                scores[self.base.item_index[item]] = -np.inf
        indices = top_indices(scores, count or self.candidates)
        vectors = self.vectors[indices]
        cosine = np.clip(np.asarray((vectors @ vectors.T).toarray(), dtype=float), 0.0, 1.0)
        return indices, np.asarray(scores[indices], dtype=float), cosine

    def select(
        self, pool: tuple[NDArrayInt, FloatArray, FloatArray], k: int
    ) -> list[Recommendation]:
        """Select sequentially, resolving equal selection scores by artist ID."""
        if k <= 0:
            raise ValueError("k must be positive")
        if self.candidates < k:
            raise ValueError("M1 candidate count must be >= K")
        indices, relevance, cosine = pool
        indices = indices[: self.candidates]
        relevance = relevance[: self.candidates]
        cosine = cosine[: self.candidates, : self.candidates]
        if not len(indices):
            return []
        if self.weight == 1 and self.penalty == 0:
            return [
                Recommendation(self.base.items[int(i)], float(s), "m1_identity")
                for i, s in zip(indices[:k], relevance[:k], strict=True)
            ]
        base = normalized(relevance)
        redundancy = np.zeros(len(indices))
        available = np.ones(len(indices), dtype=bool)
        result = []
        for _ in range(min(k, len(indices))):
            score = (
                self.weight * base
                - (1 - self.weight) * redundancy
                - self.penalty * self.pop[indices]
            )
            score[~available] = -np.inf
            maximum = float(score.max())
            tied = np.flatnonzero(score == maximum)
            j = int(tied[np.argmin(indices[tied])])
            item = int(indices[j])
            available[j] = False
            result.append(
                Recommendation(self.base.items[item], float(score[j]), "m1_sequential_rerank")
            )
            redundancy = np.maximum(redundancy, cosine[:, j])
        return result

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        return self.select(self.pool(user_id, seen_item_ids), k)


class ColdStartModel(Recommender):
    """Reference-only ItemCF and tag TF-IDF; query users provide only allowed profiles."""

    def __init__(
        self,
        item_cf: ItemCFRecommender,
        features: Any,
        alpha: float = 0.5,
        threshold: int = 5,
        mode: str = "combined",
    ):
        if not 0 <= alpha <= 1 or threshold < 1:
            raise ValueError("Invalid M2 configuration")
        self.item_cf = item_cf
        self.features = features.tocsr()
        self.alpha = alpha
        self.threshold = threshold
        if mode not in ("combined", "content", "cf", "popularity"):
            raise ValueError("Invalid M2 component mode")
        self.mode = mode
        self.profiles: dict[str, dict[str, float]] = {}
        self.pop = normalized(item_cf.popularity)

    def fit(self, interactions: Iterable[Interaction]) -> "ColdStartModel":
        """Fit the reference ItemCF model; feature construction is a separate train-only step."""
        self.item_cf.fit(interactions)
        return self

    def profile_scores(self, profile: dict[str, float]) -> tuple[FloatArray, str]:
        """Use exactly the supplied history; unavailable components are not treated as zeros."""
        valid = {i: c for i, c in profile.items() if i in self.item_cf.item_index}
        if not valid or self.mode == "popularity":
            return self.item_cf.popularity.copy(), "popularity_empty_or_unknown_history"
        indices = np.array([self.item_cf.item_index[i] for i in valid], dtype=np.int64)
        counts = np.array(list(valid.values()), dtype=float)
        if not np.isfinite(counts).all() or (counts <= 0).any():
            raise ValueError("Invalid profile counts")
        weights = np.log2(1 + counts)
        profile_vector = np.asarray(weights @ self.features[indices]).ravel()
        norm = float(np.linalg.norm(profile_vector))
        content = (
            normalized(np.asarray(self.features @ profile_vector / norm, dtype=float))
            if norm > 0
            else None
        )
        fallback = (
            self.pop if content is None else self.alpha * content + (1 - self.alpha) * self.pop
        )
        collaborative = None
        if self.item_cf.neighbors[:, indices].nnz:
            collaborative = normalized(self.item_cf.from_profile(valid))
        if self.mode == "content":
            return (
                (content, "m2_content_only")
                if content is not None
                else (self.pop.copy(), "popularity_no_tags")
            )
        if self.mode == "cf":
            return (
                (collaborative, "m2_cf_only")
                if collaborative is not None
                else (self.pop.copy(), "popularity_no_cf")
            )
        if collaborative is None and content is None:
            return self.item_cf.popularity.copy(), "popularity_no_cf_or_tags"
        omega = min(1, len(valid) / self.threshold) if collaborative is not None else 0.0
        scores = (
            omega * collaborative + (1 - omega) * fallback
            if collaborative is not None
            else fallback
        )
        reason = f"m2_cf_{int(collaborative is not None)}_content_{int(content is not None)}"
        return np.asarray(scores, dtype=float), reason

    def predict(self, user_id: str, item_id: str) -> float:
        if item_id not in self.item_cf.item_index:
            return 0.0
        return float(
            self.profile_scores(self.profiles.get(user_id, {}))[0][self.item_cf.item_index[item_id]]
        )

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        scores, reason = self.profile_scores(self.profiles.get(user_id, {}))
        scores = scores.copy()
        for i in seen_item_ids:
            if i in self.item_cf.item_index:
                scores[self.item_cf.item_index[i]] = -np.inf
        return [
            Recommendation(self.item_cf.items[j], float(scores[j]), reason)
            for j in top_indices(scores, k)
        ]

    def save(self, folder: Path) -> None:
        """Persist global reference artifacts; do not store query histories in the release."""
        folder.mkdir(exist_ok=False, parents=True)
        self.item_cf.save(folder / "item_cf.npz")
        sparse.save_npz(folder / "tag_features.npz", self.features)
        write_json(
            folder / "params.json",
            {"alpha": self.alpha, "threshold": self.threshold, "mode": self.mode},
        )

    @classmethod
    def load(cls, folder: Path) -> "ColdStartModel":
        import json

        params = json.loads((folder / "params.json").read_text())
        item_cf = MatrixModel.load(folder / "item_cf.npz")
        if not isinstance(item_cf, ItemCFRecommender):
            raise ValueError("M2 requires ItemCF")
        return cls(item_cf, sparse.load_npz(folder / "tag_features.npz"), **params)


def tag_features(
    reference: pd.DataFrame,
    items: list[str],
    tags_file: Path,
    names_file: Path,
    encoding: str = "latin-1",
) -> tuple[Any, dict[str, Any]]:
    """Build vocabulary/IDF using only tag events of observed reference-user artist pairs."""
    events = pd.read_csv(tags_file, sep="\t", dtype=str, keep_default_na=False)
    names = pd.read_csv(names_file, sep="\t", dtype=str, keep_default_na=False, encoding=encoding)
    if not {"userID", "artistID", "tagID"}.issubset(events.columns) or not {
        "tagID",
        "tagValue",
    }.issubset(names.columns):
        raise ValueError("Invalid tag schema")
    pairs = set(zip(reference.user_id, reference.item_id, strict=True))
    keep = [(u, i) in pairs for u, i in zip(events.userID, events.artistID, strict=True)]
    used = events.loc[keep].copy()
    tags = {str(r.tagID): " ".join(str(r.tagValue).casefold().split()) for r in names.itertuples()}
    used["tag"] = used.tagID.map(tags)
    used = used[used.tag.notna() & used.tag.ne("")]
    frequencies = used.groupby("tag").artistID.nunique()
    vocab = {str(t): i for i, t in enumerate(sorted(frequencies[frequencies >= 2].index))}
    artist_index = {item: i for i, item in enumerate(items)}
    counts = used.groupby(["artistID", "tag"]).size()
    rows = []
    cols = []
    values = []
    for row in counts.reset_index(name="count").to_dict("records"):
        artist, tag, count = row["artistID"], row["tag"], row["count"]
        if artist in artist_index and tag in vocab:
            rows.append(artist_index[artist])
            cols.append(vocab[tag])
            values.append(float(count))
    features = sparse.csr_matrix((values, (rows, cols)), shape=(len(items), len(vocab)))
    norm = np.zeros(len(items))
    if vocab:
        frequency = features.getnnz(axis=0)
        features = features @ sparse.diags(np.log((1 + len(items)) / (1 + frequency)) + 1)
        norm = np.sqrt(np.asarray(features.multiply(features).sum(axis=1)).ravel())
        features = sparse.diags(1 / np.maximum(norm, 1e-15)) @ features
    return features, {
        "source_events": len(events),
        "used_events": len(used),
        "vocabulary": vocab,
        "tag_users": sorted(set(used.userID)),
        "min_artist_document_frequency": 2,
        "artists_with_features": int(np.count_nonzero(norm)),
        "feature_catalog": items,
    }
