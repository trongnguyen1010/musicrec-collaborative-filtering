"""Điều hướng yêu cầu tới mô hình đã ghim; dùng chung cho FastAPI, Streamlit và kiểm tra ngoại
tuyến.

Ba nhánh theo kế hoạch demo (docs/KE_HOACH_PROTOTYPE_DEMO.md, P1–P5): người dùng có sẵn
nhận PureSVD, M1 trên PureSVD hoặc ALS, loại lịch sử huấn luyện và xác thực đúng như khi
chấm tập kiểm thử; người dùng mới chọn 1–5 nghệ sĩ thì dùng M2; hồ sơ rỗng thì dùng
Popularity. Vì cùng cách loại lịch sử, danh sách trên API trùng với đánh giá ngoại tuyến.
"""

import threading
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.m1 import rerank_candidates
from musicrec.serving.release import Release

ExistingModel = Literal["pure_svd", "m1", "implicit_als"]
Branch = Literal["existing_user", "new_user", "popularity"]
MAX_PROFILE_ARTISTS = 5
# Lưới xác thực trong configs/models/m1_pure_svd.yaml; chỉ các điểm này có số liệu đánh giá.
M1_LAMBDAS = (0.5, 0.75, 1.0)
M1_BETAS = (0.0, 0.1, 0.25, 0.5)
_PROFILE_ID = "demo_new_user"


class UnknownUserError(LookupError):
    """Người dùng được yêu cầu không có trong tập huấn luyện của mô hình (API trả 404)."""


@dataclass(frozen=True, slots=True)
class ArtistInfo:
    """Thông tin hiển thị một nghệ sĩ; listeners là số người nghe trong tập huấn luyện (như ARP)."""

    item_id: str
    name: str
    url: str
    picture_url: str
    listeners: int


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Kết quả của một yêu cầu, chưa phụ thuộc định dạng trả về."""

    release: str
    branch: Branch
    model: str
    fallback_used: bool
    fallback_reason: str | None
    recommendations: list[Recommendation]
    ignored_item_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ProfileEntry:
    """Một nghệ sĩ người dùng mới chọn; listening_count không bắt buộc trong demo."""

    item_id: str
    listening_count: float | None = None


class DemoService:
    """Tách việc chọn mô hình và loại lịch sử ra khỏi phần xử lý HTTP."""

    def __init__(self, release: Release) -> None:
        self.release = release
        self._existing: dict[str, Recommender] = {
            "pure_svd": release.pure_svd,
            "m1": release.m1,
            "implicit_als": release.implicit_als,
        }
        known = (
            release.train[["user_id", "item_id"]],
            release.validation[["user_id", "item_id"]],
        )
        self._masks: dict[str, set[str]] = {}
        for frame in known:
            for user, group in frame.groupby("user_id"):
                self._masks.setdefault(str(user), set()).update(group.item_id)
        self._train_users = set(release.train.user_id)
        self._listeners = release.train.groupby("item_id").user_id.nunique().to_dict()
        self._m2_catalog = set(release.m2.catalog)
        # Lượt nghe không rõ nhận mức đại diện ở giữa: log2(1 + c) nằm giữa phân vị
        # 40% và 60% của tập huấn luyện, là các ngưỡng điểm đại diện mà M2 dùng.
        low, high = release.m2.thresholds[1], release.m2.thresholds[2]
        self.default_listening_count = float(2 ** ((low + high) / 2) - 1)
        self._m2_lock = threading.Lock()

    @property
    def users(self) -> list[str]:
        """Người dùng trong tập huấn luyện, theo thứ tự mã số."""
        return sorted(self._train_users, key=lambda u: (not u.isdecimal(), len(u), u))

    def masked_items(self, user_id: str) -> set[str]:
        """Nghệ sĩ huấn luyện và xác thực của một người: đúng phần bị loại khi chấm tập kiểm thử."""
        return set(self._masks.get(user_id, set()))

    def artist(self, item_id: str) -> ArtistInfo:
        """Tên và mức phổ biến của một nghệ sĩ; nghệ sĩ không có tên thì dùng mã làm tên."""
        row = self.release.artists.get(item_id, {})
        return ArtistInfo(
            item_id,
            row.get("name", item_id),
            row.get("url", ""),
            row.get("picture_url", ""),
            int(self._listeners.get(item_id, 0)),
        )

    def search_artists(self, query: str, limit: int) -> list[ArtistInfo]:
        """Tìm nghệ sĩ theo chuỗi con trong danh mục M2, nhiều người nghe trước."""
        needle = query.casefold().strip()
        matches = [
            self.artist(item)
            for item in self._m2_catalog
            if needle in self.release.artists.get(item, {}).get("name", item).casefold()
        ]
        matches.sort(key=lambda a: (-a.listeners, a.name.casefold(), a.item_id))
        return matches[:limit]

    def recommend_existing(
        self,
        user_id: str,
        k: int,
        model: ExistingModel,
        m1_params: tuple[float, float] | None = None,
    ) -> RecommendationResult:
        """Nhánh 1: gợi ý cho người dùng có sẵn bằng một mô hình đã ghim.

        m1_params=(λ, β) tái xếp hạng cùng 100 ứng viên PureSVD với một điểm khác trong lưới
        xác thực của M1; None giữ cấu hình đã chọn.
        """
        if user_id not in self._train_users:
            raise UnknownUserError(user_id)
        if m1_params is not None:
            lambda_weight, beta = m1_params
            if model != "m1" or lambda_weight not in M1_LAMBDAS or beta not in M1_BETAS:
                raise ValueError("m1 lambda/beta must be a point of the M1 validation grid")
            m1 = self.release.m1
            if k > m1.candidate_size:
                raise ValueError("k must not exceed the M1 candidate size")
            pool = m1.prepare_candidates(user_id, self.masked_items(user_id))
            recommendations = rerank_candidates(pool, k, lambda_weight, beta)
        else:
            recommendations = self._existing[model].recommend(
                user_id, k, self.masked_items(user_id)
            )
        return RecommendationResult(
            self.release.version, "existing_user", model, False, None, recommendations
        )

    def recommend_popular(self, k: int, reason: str, seen: set[str]) -> RecommendationResult:
        """Nhánh 3: Popularity trên tập huấn luyện, đánh dấu là dự phòng kèm lý do."""
        recommendations = self.release.popularity.recommend(_PROFILE_ID, k, seen)
        return RecommendationResult(
            self.release.version, "popularity", "popularity", True, reason, recommendations
        )

    def recommend_new(self, profile: Sequence[ProfileEntry], k: int) -> RecommendationResult:
        """Nhánh 2: M2 trên mọi nghệ sĩ đã chọn, đúng như lúc đánh giá; hồ sơ rỗng thì dùng
        Popularity.

        Nghệ sĩ ngoài danh mục M2 vẫn được tính vào độ dài hồ sơ (như khi chấm M2) nhưng
        không mang tín hiệu; nếu không có nghệ sĩ nào đã biết, M2 chỉ còn thành phần phổ
        biến và kết quả được đánh dấu là dự phòng.
        """
        if len(profile) > MAX_PROFILE_ARTISTS:
            raise ValueError(f"A new-user profile holds at most {MAX_PROFILE_ARTISTS} artists")
        if len({entry.item_id for entry in profile}) != len(profile):
            raise ValueError("Duplicate profile artist")
        if not profile:
            return self.recommend_popular(k, "empty_profile", set())
        ignored = [entry.item_id for entry in profile if entry.item_id not in self._m2_catalog]
        rows = [
            Interaction(
                _PROFILE_ID,
                entry.item_id,
                entry.listening_count or self.default_listening_count,
            )
            for entry in profile
        ]
        with self._m2_lock:
            self.release.m2.set_profile(_PROFILE_ID, rows)
            try:
                recommendations = self.release.m2.recommend(_PROFILE_ID, k, set())
            finally:
                self.release.m2.set_profile(_PROFILE_ID, [])
        degenerate = len(ignored) == len(profile)
        return RecommendationResult(
            self.release.version,
            "new_user",
            "m2",
            degenerate,
            "no_profile_artist_in_m2_catalog" if degenerate else None,
            recommendations,
            ignored,
        )

    def mean_listeners(self, recommendations: Sequence[Recommendation]) -> float | None:
        """Số người nghe trung bình của một danh sách, tức ARP của riêng một người dùng."""
        if not recommendations:
            return None
        return float(np.mean([self._listeners.get(r.item_id, 0) for r in recommendations]))
