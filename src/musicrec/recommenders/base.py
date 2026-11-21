"""Giao diện chung mà mọi mô hình khuyến nghị phải tuân theo.

Nhờ dùng chung giao diện, bộ đánh giá, API và giao diện gọi mọi mô hình theo cùng một cách,
nên phép so sánh giữa các mô hình nhất quán.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

from musicrec.data.contracts import Interaction


@dataclass(frozen=True, slots=True)
class Recommendation:
    """Một nghệ sĩ được gợi ý: mã nghệ sĩ, điểm xếp hạng và lý do gợi ý."""

    item_id: str
    score: float
    reason: str


class Recommender(ABC):
    """Hợp đồng dùng chung cho bước huấn luyện, bộ đánh giá, API và giao diện."""

    @abstractmethod
    def fit(self, interactions: Iterable[Interaction]) -> "Recommender":
        """Huấn luyện mô hình chỉ từ tương tác của tập huấn luyện."""

    @abstractmethod
    def predict(self, user_id: str, item_id: str) -> float:
        """Trả điểm cho một cặp người dùng–nghệ sĩ."""

    @abstractmethod
    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Trả tối đa k nghệ sĩ chưa nghe, xếp theo thứ tự của mô hình, kèm điểm."""
