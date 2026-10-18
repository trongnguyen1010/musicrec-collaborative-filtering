"""Stable data contracts shared by offline and online layers."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class Interaction:
    """One implicit-feedback interaction after validation."""

    user_id: str
    item_id: str
    listening_count: float

    def __post_init__(self) -> None:
        if not self.user_id.strip() or not self.item_id.strip():
            raise ValueError("user_id and item_id must be non-empty")
        if not isfinite(self.listening_count) or self.listening_count <= 0:
            raise ValueError("listening_count must be finite and greater than zero")
