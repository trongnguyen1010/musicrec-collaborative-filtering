"""A small application service used by FastAPI and offline contract tests."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from musicrec.artifacts.release import verify_release
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.extensions import ColdStartModel, Reranker
from musicrec.recommenders.models import MatrixModel


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Serialized-independent inference output."""

    model_version: str
    recommendations: list[Recommendation]
    fallback_used: bool


class RecommendationService:
    """Keeps serving concerns out of HTTP route handlers."""

    def __init__(self, recommender: Recommender, model_version: str) -> None:
        self._recommender = recommender
        self._model_version = model_version
        self._cold: ColdStartModel | None = None
        self._histories: dict[str, dict[str, float]] = {}
        self.names: dict[str, str] = {}

    @classmethod
    def from_release(cls, folder: Path) -> "RecommendationService":
        """Load a validated release once; missing or corrupt models are operational errors."""
        manifest = verify_release(folder)
        base = MatrixModel.load(folder / "base.npz")
        settings = json.loads((folder / "rerank.json").read_text())
        service = cls(
            Reranker(base, settings["candidates"], settings["weight"], settings["penalty"]),
            manifest["model_version"],
        )
        service._cold = ColdStartModel.load(folder / "m2")
        service.names = json.loads((folder / "artist_names.json").read_text(encoding="utf-8"))
        train = pd.read_parquet(folder / "train.parquet")
        service._histories = {
            str(u): {
                str(row["item_id"]): float(row["listening_count"])
                for row in group.to_dict("records")
            }
            for u, group in train.groupby("user_id")
        }
        return service

    def recommend_profile(
        self, user_id: str | None, history: list[dict[str, Any]] | None, k: int
    ) -> RecommendationResult:
        """Known ID uses stored train history; supplied or new profiles use the M2 chain."""
        from math import isfinite

        known = self._histories.get(user_id or "", {})
        profile = dict(known)
        for row in history or []:
            item, count = str(row["item_id"]), float(row["listening_count"])
            if not item.strip() or not isfinite(count) or count <= 0:
                raise ValueError("Invalid supplied history")
            profile[item] = max(count, profile.get(item, 0.0))
        if known and not history and self._cold is not None and len(known) >= self._cold.threshold:
            return self.recommend(user_id or "", k, set(profile))
        if self._cold is None:
            raise RuntimeError("M2 release not loaded")
        query = "provided_profile"
        cold = ColdStartModel(
            self._cold.item_cf, self._cold.features, self._cold.alpha, self._cold.threshold
        )
        cold.profiles = {query: profile}
        recs = cold.recommend(query, k, set(profile))
        return RecommendationResult(self._model_version, recs, True)

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> RecommendationResult:
        recommendations = self._recommender.recommend(user_id, k, seen_item_ids)
        return RecommendationResult(
            model_version=self._model_version,
            recommendations=recommendations,
            fallback_used=False,
        )
