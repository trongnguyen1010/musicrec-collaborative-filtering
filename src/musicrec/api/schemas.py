"""HTTP schemas kept separate from recommendation domain objects."""

from pydantic import BaseModel, Field, model_validator


class HistoryEntry(BaseModel):
    item_id: str = Field(min_length=1)
    listening_count: float = Field(gt=0)


class RecommendRequest(BaseModel):
    user_id: str | None = None
    history: list[HistoryEntry] | None = None
    k: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def has_profile(self) -> "RecommendRequest":
        if not self.user_id and not self.history:
            raise ValueError("either user_id or history is required")
        return self


class RecommendationResponse(BaseModel):
    item_id: str
    score: float
    reason: str


class RecommendResponse(BaseModel):
    model_version: str
    fallback_used: bool
    recommendations: list[RecommendationResponse]
