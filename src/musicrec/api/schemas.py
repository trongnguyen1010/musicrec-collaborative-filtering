"""HTTP schemas kept separate from recommendation domain objects."""

from pydantic import BaseModel, Field, field_validator


class HistoryEntry(BaseModel):
    item_id: str = Field(min_length=1)
    listening_count: float = Field(gt=0, allow_inf_nan=False)

    @field_validator("item_id")
    @classmethod
    def trim_item_id(cls, value: str) -> str:
        """Whitespace-only IDs are not artist identifiers."""
        if not value.strip():
            raise ValueError("item_id must be nonempty")
        return value.strip()


class RecommendRequest(BaseModel):
    user_id: str | None = None
    history: list[HistoryEntry] | None = None
    k: int = Field(default=10, ge=1, le=100, strict=True)

    @field_validator("user_id")
    @classmethod
    def trim_user_id(cls, value: str | None) -> str | None:
        """A missing ID represents a guest; a supplied blank ID is an input error."""
        if value is not None and not value.strip():
            raise ValueError("user_id must be nonempty when supplied")
        return value.strip() if value is not None else None


class RecommendationResponse(BaseModel):
    item_id: str
    name: str | None = None
    score: float
    reason: str


class RecommendResponse(BaseModel):
    model_version: str
    fallback_used: bool
    recommendations: list[RecommendationResponse]
