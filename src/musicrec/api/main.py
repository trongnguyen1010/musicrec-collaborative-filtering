"""Điểm vào FastAPI, phục vụ một gói phát hành đã kiểm tra (xem scripts/export_release.py).

Biến môi trường: MUSICREC_RELEASE_DIR (thư mục gói) và MUSICREC_CORS_ORIGINS (các nguồn,
cách nhau bằng dấu phẩy, được gọi API từ trình duyệt, ví dụ tên miền Vercel). Giao diện
chạy cục bộ trên localhost hoặc 127.0.0.1 được phép ở mọi cổng.
"""

import os
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from musicrec.api.schemas import (
    ArtistResponse,
    HealthResponse,
    HistoryItemResponse,
    RecommendationResponse,
    RecommendRequest,
    RecommendResponse,
    UserHistoryResponse,
    UserSummary,
)
from musicrec.serving.release import load_release
from musicrec.serving.service import (
    ArtistInfo,
    DemoService,
    ProfileEntry,
    RecommendationResult,
    UnknownUserError,
)

DEFAULT_RELEASE_DIR = "artifacts/releases/demo-chinh-thuc-20261026"
LOCAL_ORIGIN_REGEX = r"http://(localhost|127\.0\.0\.1)(:\d+)?"


def _load_from_environment() -> DemoService:
    return DemoService(load_release(Path(os.getenv("MUSICREC_RELEASE_DIR", DEFAULT_RELEASE_DIR))))


def _artist(info: ArtistInfo) -> dict[str, Any]:
    return asdict(info)


def create_app(load_service: Callable[[], DemoService] = _load_from_environment) -> FastAPI:
    """Tạo ứng dụng năm endpoint; gói mô hình nạp một lần lúc khởi động."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.service = load_service()
        yield

    app = FastAPI(title="MusicRec API", version="0.2.0", lifespan=lifespan)
    origins = os.getenv("MUSICREC_CORS_ORIGINS", "")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        allow_origin_regex=LOCAL_ORIGIN_REGEX,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    def service(request: Request) -> DemoService:
        loaded: DemoService = request.app.state.service
        return loaded

    def respond(svc: DemoService, result: RecommendationResult) -> RecommendResponse:
        return RecommendResponse(
            model_version=result.release,
            branch=result.branch,
            model=result.model,
            fallback_used=result.fallback_used,
            fallback_reason=result.fallback_reason,
            ignored_item_ids=result.ignored_item_ids,
            mean_listeners=svc.mean_listeners(result.recommendations),
            recommendations=[
                RecommendationResponse(
                    rank=rank,
                    score=item.score,
                    reason=item.reason,
                    **_artist(svc.artist(item.item_id)),
                )
                for rank, item in enumerate(result.recommendations, 1)
            ],
        )

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        """Phiên bản gói và cấu hình các mô hình đang phục vụ."""
        svc = service(request)
        return HealthResponse(
            status="ok",
            model_version=svc.release.version,
            models=svc.release.manifest["provenance"]["models"],
        )

    @app.get("/artists", response_model=list[ArtistResponse])
    def artists(
        request: Request, q: str = "", limit: int = Query(default=20, ge=1, le=100)
    ) -> list[ArtistResponse]:
        """Tìm nghệ sĩ cho người dùng mới chọn (danh mục M2), nhiều người nghe trước."""
        return [ArtistResponse(**_artist(a)) for a in service(request).search_artists(q, limit)]

    @app.get("/users", response_model=list[UserSummary])
    def users(
        request: Request,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=2000),
    ) -> list[UserSummary]:
        """Danh sách người dùng có sẵn kèm số nghệ sĩ trong lịch sử bị loại."""
        svc = service(request)
        return [
            UserSummary(user_id=user, history_size=len(svc.masked_items(user)))
            for user in svc.users[offset : offset + limit]
        ]

    @app.get("/users/{user_id}/history", response_model=UserHistoryResponse)
    def history(
        request: Request, user_id: str, limit: int = Query(default=20, ge=1, le=500)
    ) -> UserHistoryResponse:
        """Nghệ sĩ huấn luyện và xác thực của một người, những nghệ sĩ demo không bao giờ gợi ý."""
        svc = service(request)
        frames: list[tuple[Literal["train", "validation"], str, float]] = []
        splits: list[tuple[Literal["train", "validation"], pd.DataFrame]] = [
            ("train", svc.release.train),
            ("validation", svc.release.validation),
        ]
        for split, frame in splits:
            rows = frame[frame.user_id == user_id]
            frames.extend(
                (split, str(item), float(count))
                for item, count in zip(rows.item_id, rows.listening_count, strict=True)
            )
        if not frames:
            raise HTTPException(status_code=404, detail=f"Unknown user_id: {user_id}")
        frames.sort(key=lambda row: (-row[2], row[1]))
        return UserHistoryResponse(
            user_id=user_id,
            total=len(frames),
            items=[
                HistoryItemResponse(listening_count=count, split=split, **_artist(svc.artist(item)))
                for split, item, count in frames[:limit]
            ],
        )

    @app.post("/recommend", response_model=RecommendResponse)
    def recommend(request: Request, body: RecommendRequest) -> RecommendResponse:
        """Gợi ý: người dùng có sẵn → mô hình đã chọn; người mới → M2; hồ sơ rỗng → Popularity.

        Người dùng không tồn tại trả 404; đầu vào sai kiểu hoặc quá giới hạn trả 422.
        """
        svc = service(request)
        try:
            if body.user_id:
                params = (
                    None
                    if body.m1_lambda is None or body.m1_beta is None
                    else (body.m1_lambda, body.m1_beta)
                )
                result = svc.recommend_existing(body.user_id, body.k, body.model, params)
            else:
                profile = [
                    ProfileEntry(entry.item_id, entry.listening_count)
                    for entry in body.history or []
                ]
                result = svc.recommend_new(profile, body.k)
        except UnknownUserError as error:
            raise HTTPException(status_code=404, detail=f"Unknown user_id: {error}") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return respond(svc, result)

    return app


app = create_app()
