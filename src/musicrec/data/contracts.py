"""Stable data contracts shared by offline and online layers."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Interaction:
    """One implicit-feedback interaction after validation."""

    user_id: str
    item_id: str
    listening_count: float
    proxy_score: float | None = None

    def __post_init__(self) -> None:
        if not self.user_id or not self.item_id:
            raise ValueError("user_id and item_id must be non-empty")
        if self.listening_count <= 0:
            raise ValueError("listening_count must be greater than zero")
        if self.proxy_score is not None and (
            type(self.proxy_score) is bool or self.proxy_score not in (1, 2, 3, 4, 5)
        ):
            raise ValueError("proxy_score must be an observed integer score from 1 to 5")
