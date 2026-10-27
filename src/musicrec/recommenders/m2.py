"""Cold-user ItemCF, train-pair tag TF-IDF and popularity with explicit provided profiles."""

import hashlib
import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, load_npz, save_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.item_cf import ItemCFRecommender
from musicrec.recommenders.popularity import PopularityRecommender


@dataclass(frozen=True)
class ProfileScores:
    """Scores and availability before mixing; no profile row is added to learned matrices."""

    cf: NDArray[np.float64]
    cf_available: NDArray[np.bool_]
    content: NDArray[np.float64]
    content_available: NDArray[np.bool_]
    popularity: NDArray[np.float64]
    history_size: int


def mix_profile_scores(
    features: ProfileScores, alpha: float, history_threshold: int
) -> NDArray[np.float64]:
    """Blend available components per candidate, replacing missing components explicitly."""
    if not isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError("alpha must be finite in [0, 1]")
    if type(history_threshold) is not int or history_threshold <= 0:
        raise ValueError("history_threshold must be a positive integer")
    fallback = features.popularity.copy()
    valid = features.content_available
    fallback[valid] = alpha * features.content[valid] + (1 - alpha) * fallback[valid]
    weight = min(1, features.history_size / history_threshold) * features.cf_available
    return np.asarray(weight * features.cf + (1 - weight) * fallback)


class M2Recommender(Recommender):
    """Learn shared components once; set_profile supplies an ephemeral cold-user history."""

    def __init__(
        self, *, alpha: float = 0.5, history_threshold: int = 5, min_tag_df: int = 2
    ) -> None:
        if not isfinite(alpha) or not 0 <= alpha <= 1:
            raise ValueError("alpha must be finite in [0, 1]")
        if any(type(v) is not int or v <= 0 for v in [history_threshold, min_tag_df]):
            raise ValueError("History threshold and tag min_df must be positive integers")
        self.alpha, self.history_threshold, self.min_tag_df = alpha, history_threshold, min_tag_df
        self.item_cf = ItemCFRecommender(neighbors=40, shrinkage=0)
        self._profiles: dict[str, list[Interaction]] = {}
        self._items: list[str] = []
        self.vocabulary: list[str] = []
        self.feature_report: dict[str, Any] = {}
        self._features: csr_matrix[np.float64]
        self._raw_popularity: NDArray[np.float64]
        self.thresholds: NDArray[np.float64]
        self.idf: NDArray[np.float64]

    def _prepare(self) -> None:
        self._items = self.item_cf._items.copy()
        self._item_index = {item: n for n, item in enumerate(self._items)}
        self._popularity = self._raw_popularity / self._raw_popularity.max()
        self._popular_order = np.argsort(-self._raw_popularity, kind="stable")
        self._tagged = np.asarray(self._features.getnnz(axis=1) > 0)
        self._profiles = {}

    @property
    def catalog(self) -> list[str]:
        """Learning-catalog artists; profile artists outside it carry no CF or tag signal."""
        return self._items.copy()

    def _proxy(self, row: Interaction) -> Interaction:
        if not isfinite(row.listening_count):
            raise ValueError("Profile and train counts must be finite")
        value = np.log2(1 + row.listening_count)
        return Interaction(
            row.user_id,
            row.item_id,
            row.listening_count,
            int(1 + np.count_nonzero(value > self.thresholds)),
        )

    def fit(
        self,
        interactions: Iterable[Interaction],
        *,
        tags: Iterable[tuple[str, str, str]] = (),
    ) -> "M2Recommender":
        """Fit using learning users' train only; reject tags not on these exact pairs."""
        rows = list(interactions)
        if not rows or any(not isfinite(r.listening_count) for r in rows):
            raise ValueError("Expected non-empty finite learning interactions")
        pairs = {(r.user_id, r.item_id) for r in rows}
        if len(pairs) != len(rows):
            raise ValueError("Duplicate learning user-artist pairs")
        self.thresholds = np.quantile(
            np.log2(1 + np.array([r.listening_count for r in rows], dtype=np.float64)),
            [0.2, 0.4, 0.6, 0.8],
            method="linear",
        )
        self.item_cf.fit([self._proxy(r) for r in rows])
        self._items = self.item_cf._items.copy()
        items = {item: n for n, item in enumerate(self._items)}
        allowed: set[tuple[str, str, str]] = set()
        total, allowed_rows = 0, 0
        for user, item, value in tags:
            total += 1
            if (user, item) not in pairs:
                continue
            normalized = " ".join(value.casefold().split())
            if normalized:
                allowed_rows += 1
                allowed.add((user, item, normalized))
        tf = Counter((item, tag) for _, item, tag in allowed)
        df = Counter(tag for _, tag in tf)
        self.vocabulary = sorted(tag for tag, count in df.items() if count >= self.min_tag_df)
        columns = {tag: n for n, tag in enumerate(self.vocabulary)}
        self.idf = np.array(
            [np.log((1 + len(items)) / (1 + df[t])) + 1 for t in self.vocabulary], dtype=np.float64
        )
        retained = [(item, tag, count) for (item, tag), count in tf.items() if tag in columns]
        self._features = csr_matrix(
            (
                [count * self.idf[columns[tag]] for _, tag, count in retained],
                (
                    [items[item] for item, _, _ in retained],
                    [columns[tag] for _, tag, _ in retained],
                ),
            ),
            shape=(len(items), len(columns)),
            dtype=np.float64,
        )
        norms = np.sqrt(np.asarray(self._features.power(2).sum(axis=1)).ravel())
        inverse = np.divide(1, norms, out=np.zeros_like(norms), where=norms > 0)
        self._features = csr_matrix(self._features.multiply(inverse[:, None]))
        self._features.sort_indices()
        popularity = PopularityRecommender().fit(rows)
        self._raw_popularity = np.array([popularity.predict("offline", i) for i in self._items])
        self.feature_report = {
            "tag_rows_input": total,
            "tag_rows_allowed_nonempty": allowed_rows,
            "tag_rows_rejected_or_empty": total - allowed_rows,
            "distinct_allowed_user_artist_tag_triples": len(allowed),
            "normalized_tags_before_df_filter": len(df),
            "vocabulary_size": len(columns),
            "tagged_catalog_artists": int(np.count_nonzero(norms)),
            "untagged_catalog_artists": int(np.count_nonzero(norms == 0)),
            "learning_users": len(self.item_cf._users),
            "learning_interactions": len(rows),
        }
        self._prepare()
        return self

    def set_profile(self, user_id: str, interactions: Iterable[Interaction]) -> None:
        """Bind only supplied raw observations; never fit shared components or save profiles."""
        if not self._items:
            raise RuntimeError("Fit M2 before binding profiles")
        rows = list(interactions)
        if not user_id or any(r.user_id != user_id for r in rows):
            raise ValueError("Profile rows must belong to the specified non-empty user")
        if len({r.item_id for r in rows}) != len(rows):
            raise ValueError("Duplicate profile artist")
        self._profiles[user_id] = [self._proxy(r) for r in rows]

    def profile_scores(self, user_id: str) -> ProfileScores:
        """Compute ItemCF support and cosine from only the currently supplied observations."""
        if not self._items:
            raise RuntimeError("Fit M2 before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        rows = self._profiles.get(user_id, [])
        raw_cf, supported = self.item_cf.score_profile(rows)
        known = [r for r in rows if r.item_id in self._item_index]
        indices = [self._item_index[r.item_id] for r in known]
        weights = np.array([np.log2(1 + r.listening_count) for r in known])
        profile = np.asarray(self._features[indices].T @ weights).ravel()
        norm = float(np.linalg.norm(profile))
        content = (
            np.asarray(self._features @ (profile / norm)).ravel()
            if norm
            else np.zeros(len(self._items))
        )
        return ProfileScores(
            np.clip((raw_cf - 1) / 4, 0, 1),
            supported,
            np.clip(content, 0, 1),
            self._tagged & (norm > 0),
            self._popularity,
            len(rows),
        )

    def predict(self, user_id: str, item_id: str) -> float:
        """Return the mixed [0,1] association score, not a calibrated probability."""
        values = mix_profile_scores(
            self.profile_scores(user_id), self.alpha, self.history_threshold
        )
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the learning catalog")
        return float(values[self._item_index[item_id]])

    def rank_scores(
        self, user_id: str, scores: NDArray[np.float64], k: int, seen: set[str], *, reason: str
    ) -> list[Recommendation]:
        """Rank a component or mixture on the same full unseen catalog and profile mask."""
        if not self._items:
            raise RuntimeError("Fit M2 before ranking")
        if not user_id or type(k) is not int or k <= 0:
            raise ValueError("Expected a non-empty user and positive integer k")
        if scores.shape != (len(self._items),) or not np.isfinite(scores).all():
            raise ValueError("Expected finite scores for the full learning catalog")
        excluded = seen | {r.item_id for r in self._profiles.get(user_id, [])}
        if not self._profiles.get(user_id) or np.array_equal(scores, self._popularity):
            order = self._popular_order  # Exact Popularity item order for every N=0 branch.
        else:
            order = np.argsort(-np.round(scores, 12), kind="stable")
        chosen = [int(i) for i in order if self._items[i] not in excluded][:k]
        return [Recommendation(self._items[i], float(scores[i]), reason) for i in chosen]

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Filter only supplied history; expose CF/content availability for each result."""
        features = self.profile_scores(user_id)
        scores = mix_profile_scores(features, self.alpha, self.history_threshold)
        results = self.rank_scores(user_id, scores, k, seen_item_ids, reason="m2")
        return [
            Recommendation(
                r.item_id,
                r.score,
                "m2_popularity_empty_profile"
                if not features.history_size
                else f"m2_cf={int(features.cf_available[self._item_index[r.item_id]])}"
                f"_content={int(features.content_available[self._item_index[r.item_id]])}",
            )
            for r in results
        ]

    def save(self, directory: Path) -> None:
        """Save shared numeric components in a new directory; omit ephemeral query profiles."""
        if not self._items:
            raise RuntimeError("Fit M2 before saving")
        directory.mkdir(parents=True, exist_ok=False)
        self.item_cf.save(directory / "item_cf")
        save_npz(directory / "tags.npz", self._features)
        np.savez_compressed(
            directory / "statistics.npz",
            popularity=self._raw_popularity,
            thresholds=self.thresholds,
            idf=self.idf,
        )
        state = {
            "schema_version": 1,
            "model": "m2",
            "config": {
                "alpha": self.alpha,
                "history_threshold": self.history_threshold,
                "min_tag_df": self.min_tag_df,
            },
            "vocabulary": self.vocabulary,
            "feature_report": self.feature_report,
            "sha256": {
                p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in directory.rglob("*")
                if p.is_file()
            },
        }
        (directory / "state.json").write_text(
            json.dumps(state, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )

    @classmethod
    def load(cls, directory: Path) -> "M2Recommender":
        """Restore shared components without fitting; callers must provide profiles again."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if state.get("schema_version") != 1 or state.get("model") != "m2":
            raise ValueError("Unsupported M2 schema")
        expected_files = {
            "tags.npz",
            "statistics.npz",
            "item_cf/state.json",
            "item_cf/ratings.npz",
            "item_cf/neighbors.npz",
        }
        if set(state["sha256"]) != expected_files:
            raise ValueError("Invalid M2 component file list")
        for relative, digest in state["sha256"].items():
            if hashlib.sha256((directory / relative).read_bytes()).hexdigest() != digest:
                raise ValueError(f"M2 checksum mismatch: {relative}")
        model = cls(**state["config"])
        model.item_cf = ItemCFRecommender.load(directory / "item_cf")
        model.vocabulary, model.feature_report = state["vocabulary"], state["feature_report"]
        model._features = csr_matrix(load_npz(directory / "tags.npz"))
        with np.load(directory / "statistics.npz", allow_pickle=False) as arrays:
            model._raw_popularity, model.thresholds, model.idf = (
                arrays["popularity"],
                arrays["thresholds"],
                arrays["idf"],
            )
        n = len(model.item_cf._items)
        if (
            model.vocabulary != sorted(set(model.vocabulary))
            or model._features.shape != (n, len(model.vocabulary))
            or not model._features.has_canonical_format
            or not np.isfinite(model._features.data).all()
            or (model._features.data <= 0).any()
            or model._raw_popularity.shape != (n,)
            or not np.isfinite(model._raw_popularity).all()
            or (model._raw_popularity <= 0).any()
            or model.thresholds.shape != (4,)
            or not np.isfinite(model.thresholds).all()
            or (np.diff(model.thresholds) < 0).any()
            or model.idf.shape != (len(model.vocabulary),)
            or not np.isfinite(model.idf).all()
            or (model.idf < 1).any()
        ):
            raise ValueError("Invalid M2 shared statistics/features")
        norms = np.sqrt(np.asarray(model._features.power(2).sum(axis=1)).ravel())
        if not np.all(np.isclose(norms, 0) | np.isclose(norms, 1, rtol=0, atol=1e-12)):
            raise ValueError("M2 tag vectors must have unit norm or be empty")
        model._prepare()
        return model
