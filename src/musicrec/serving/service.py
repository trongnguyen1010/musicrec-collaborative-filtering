"""A small application service used by FastAPI and offline contract tests."""

from dataclasses import dataclass

from musicrec.recommenders.base import Recommendation, Recommender


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

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> RecommendationResult:
        recommendations = self._recommender.recommend(user_id, k, seen_item_ids)
        return RecommendationResult(
            model_version=self._model_version,
            recommendations=recommendations,
            fallback_used=False,
        )
