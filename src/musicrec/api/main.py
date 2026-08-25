"""Minimal FastAPI entry point; model loading will be added with release export."""

from fastapi import FastAPI

from musicrec.api.schemas import RecommendRequest, RecommendResponse, RecommendationResponse
from musicrec.data.contracts import Interaction
from musicrec.recommenders.popularity import PopularityRecommender
from musicrec.serving.service import RecommendationService

app = FastAPI(title="MusicRec API", version="0.1.0")

_baseline = PopularityRecommender().fit(
    [
        Interaction(user_id="seed_user", item_id="seed_item_a", listening_count=10),
        Interaction(user_id="seed_user", item_id="seed_item_b", listening_count=5),
    ]
)
_service = RecommendationService(_baseline, model_version="scaffold-popularity-v0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return the current service state without exposing internal implementation."""
    return {"status": "ok", "model_version": "scaffold-popularity-v0"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    """Return unseen popular items until a release model is configured."""
    seen_item_ids = {entry.item_id for entry in request.history or []}
    result = _service.recommend(request.user_id or "temporary_profile", request.k, seen_item_ids)
    return RecommendResponse(
        model_version=result.model_version,
        fallback_used=result.fallback_used,
        recommendations=[
            RecommendationResponse(item_id=item.item_id, score=item.score, reason=item.reason)
            for item in result.recommendations
        ],
    )
