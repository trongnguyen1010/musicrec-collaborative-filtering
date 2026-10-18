"""FastAPI prototype loading one verified Last.fm release at startup."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response

from musicrec.api.schemas import RecommendationResponse, RecommendRequest, RecommendResponse
from musicrec.configuration import ROOT
from musicrec.serving.service import RecommendationService


def create_app(release_path: Path | None = None) -> FastAPI:
    """Create the API; absent/corrupt artifacts produce not-ready instead of fake artists."""
    folder = release_path or ROOT / os.environ.get("MUSICREC_RELEASE", "artifacts/releases/v0.2.0")
    service: RecommendationService | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        nonlocal service
        try:
            service = RecommendationService.from_release(folder)
        except (OSError, ValueError, KeyError):
            logging.getLogger(__name__).exception("Release could not be loaded")
            service = None
        yield
        service = None

    app = FastAPI(title="MusicRec API", version="0.2.0", lifespan=lifespan)

    @app.get("/health")
    def health(response: Response) -> dict[str, str]:
        if service is None:
            response.status_code = 503
            return {"status": "not_ready", "model_version": "unavailable"}
        return {"status": "ready", "model_version": service._model_version}

    @app.post("/recommend", response_model=RecommendResponse)
    def recommend(request: RecommendRequest) -> RecommendResponse:
        if service is None:
            raise HTTPException(503, "Mô hình chưa sẵn sàng")
        history = (
            [entry.model_dump() for entry in request.history]
            if request.history is not None
            else None
        )
        result = service.recommend_profile(request.user_id, history, request.k)
        return RecommendResponse(
            model_version=result.model_version,
            fallback_used=result.fallback_used,
            recommendations=[
                RecommendationResponse(
                    item_id=r.item_id,
                    name=service.names.get(r.item_id, f"Artist {r.item_id}"),
                    score=r.score,
                    reason=r.reason,
                )
                for r in result.recommendations
            ],
        )

    return app


app = create_app()
