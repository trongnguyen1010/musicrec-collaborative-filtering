"""Mô hình cơ sở Popularity, mốc so sánh bắt buộc cho mọi mô hình cá nhân hóa."""

from collections import defaultdict
from collections.abc import Iterable
from math import fsum, isfinite, log2

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class PopularityRecommender(Recommender):
    """Xếp hạng theo tổng log2(1 + lượt nghe) trên tập huấn luyện, công thức (3.4).

    Hòa điểm thì xét mã nghệ sĩ dạng số. Điểm thể hiện cường độ nghe tổng hợp, không phải
    số người nghe hay điểm dự đoán. Mọi người dùng nhận cùng một danh sách (không cá nhân
    hóa), nên mô hình này cũng là phương án dự phòng khi lịch sử rỗng.
    """

    def __init__(self, score: str = "log_count_sum") -> None:
        """score='log_count_sum' (mặc định, đã khóa) hoặc 'listeners' (số người nghe c_i)."""
        if score not in ("log_count_sum", "listeners"):
            raise ValueError("score must be 'log_count_sum' or 'listeners'")
        self.score = score
        self._scores: dict[str, float] = {}
        self._ranked: list[str] = []
        self._users: set[str] = set()

    def fit(self, interactions: Iterable[Interaction]) -> "PopularityRecommender":
        """Biến đổi từng lượt nghe rồi cộng theo nghệ sĩ; không phụ thuộc thứ tự dòng."""
        values: defaultdict[str, list[float]] = defaultdict(list)
        pairs: set[tuple[str, str]] = set()
        for interaction in interactions:
            if not isfinite(interaction.listening_count) or interaction.listening_count <= 0:
                raise ValueError("Raw listening counts must be finite and positive")
            pair = (interaction.user_id, interaction.item_id)
            if pair in pairs:
                raise ValueError("Duplicate user-artist pair")
            pairs.add(pair)
            # log2 làm giảm ảnh hưởng của vài người nghe một nghệ sĩ hàng nghìn lần.
            values[interaction.item_id].append(log2(1 + interaction.listening_count))
        if not values:
            raise ValueError("Expected non-empty training interactions")
        self._scores = {
            item: float(len(counts)) if self.score == "listeners" else fsum(sorted(counts))
            for item, counts in values.items()
        }
        self._ranked = sorted(
            self._scores,
            key=lambda item: (
                -self._scores[item],
                not item.isdecimal(),
                int(item) if item.isdecimal() else 0,
                item,
            ),
        )
        self._users = {user for user, _ in pairs}
        return self

    def predict(self, user_id: str, item_id: str) -> float:
        """Trả điểm phổ biến toàn cục; từ chối nghệ sĩ ngoài danh mục huấn luyện."""
        del user_id
        if not self._scores:
            raise RuntimeError("Fit Popularity before inference")
        if item_id not in self._scores:
            raise ValueError("Artist is outside the train catalog")
        return self._scores[item_id]

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Lọc danh sách đã xếp sẵn, bỏ nghệ sĩ đã nghe, lấy k nghệ sĩ đầu."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        if not self._scores:
            raise RuntimeError("Fit Popularity before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        reason = "popular_with_all_users"
        if user_id not in self._users:
            reason += "_cold_start"
        results = []
        for item in self._ranked:
            if item not in seen_item_ids:
                results.append(Recommendation(item, self._scores[item], reason))
                if len(results) == k:
                    break
        return results
