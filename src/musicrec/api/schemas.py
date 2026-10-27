"""HTTP schemas kept separate from recommendation domain objects."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from musicrec.serving.service import MAX_PROFILE_ARTISTS


class HistoryEntry(BaseModel):
    item_id: str = Field(min_length=1)
    listening_count: float | None = Field(default=None, gt=0)


class RecommendRequest(BaseModel):
    """user_id selects an existing user; otherwise history (0-5 artists) is a new user."""

    user_id: str | None = None
    history: list[HistoryEntry] | None = Field(default=None, max_length=MAX_PROFILE_ARTISTS)
    k: int = Field(default=10, ge=1, le=100)
    model: Literal["pure_svd", "m1", "implicit_als"] = "pure_svd"

    @model_validator(mode="after")
    def has_profile(self) -> "RecommendRequest":
        if not self.user_id and self.history is None:
            raise ValueError("either user_id or history is required")
        return self


class ArtistResponse(BaseModel):
    item_id: str
    name: str
    url: str
    picture_url: str
    listeners: int


class RecommendationResponse(ArtistResponse):
    rank: int
    score: float
    reason: str


class RecommendResponse(BaseModel):
    model_version: str
    branch: Literal["existing_user", "new_user", "popularity"]
    model: str
    fallback_used: bool
    fallback_reason: str | None
    ignored_item_ids: list[str]
    mean_listeners: float | None
    recommendations: list[RecommendationResponse]


class HistoryItemResponse(ArtistResponse):
    listening_count: float
    split: Literal["train", "validation"]


class UserHistoryResponse(BaseModel):
    user_id: str
    total: int
    items: list[HistoryItemResponse]


class UserSummary(BaseModel):
    user_id: str
    history_size: int


class HealthResponse(BaseModel):
    status: str
    model_version: str
    models: dict[str, dict[str, object]]
