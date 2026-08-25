"""Base interface that every recommender implementation must follow."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from musicrec.data.contracts import Interaction


@dataclass(frozen=True, slots=True)
class Recommendation:
    """A ranked item returned by a recommender."""

    item_id: str
    score: float
    reason: str


class Recommender(ABC):
    """Contract used by trainer, evaluator, API and UI."""

    @abstractmethod
    def fit(self, interactions: Iterable[Interaction]) -> "Recommender":
        """Fit the model using only training interactions."""

    @abstractmethod
    def predict(self, user_id: str, item_id: str) -> float:
        """Return a score for one user-item pair."""

    @abstractmethod
    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Return at most k unseen items in descending score order."""
