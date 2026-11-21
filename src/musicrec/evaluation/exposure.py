"""Độ xuất hiện phía nghệ sĩ và độ khớp mức phổ biến (H1), học từ tập huấn luyện."""

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from math import fsum
from typing import Any


@dataclass(frozen=True)
class HeadSplit:
    """Nhóm đầu: ít nghệ sĩ nhất (nhiều người nghe trước) chiếm ≥ share số cặp, kể cả hòa."""

    head: frozenset[str]
    non_head: frozenset[str]
    threshold_listeners: int
    head_pair_share: float
    total_pairs: int

    def summary(self) -> dict[str, Any]:
        """Kích thước, tỷ lệ thực và mã băm của danh sách thành viên, để ghi vào nhật ký chạy."""
        head, non_head = sorted(self.head), sorted(self.non_head)
        return {
            "rule": "shortest_prefix_by_train_distinct_listeners_with_ties_at_cut",
            "head_artists": len(head),
            "non_head_artists": len(non_head),
            "threshold_listeners": self.threshold_listeners,
            "head_pair_share": self.head_pair_share,
            "non_head_pair_share": 1 - self.head_pair_share,
            "total_pairs": self.total_pairs,
            "head_sha256": hashlib.sha256(json.dumps(head).encode()).hexdigest(),
            "non_head_sha256": hashlib.sha256(json.dumps(non_head).encode()).hexdigest(),
        }


def head_split(listeners: Mapping[str, int], share: float = 0.2) -> HeadSplit:
    """Chia nghệ sĩ thành nhóm đầu (phổ biến) và phần còn lại theo số người nghe n_i.

    M = tổng n_i là số cặp huấn luyện. Nghệ sĩ hòa với nghệ sĩ cuối của nhóm đầu cũng
    vào nhóm đầu, nên tỷ lệ thực có thể vượt mục tiêu. Nhóm còn lại có thể rỗng; bên gọi
    phải báo cáo trường hợp đó.
    """
    if not listeners or any(type(n) is not int or n <= 0 for n in listeners.values()):
        raise ValueError("Expected a non-empty catalog with positive integer listener counts")
    if not 0 < share <= 1:
        raise ValueError("share must lie in (0, 1]")
    total = sum(listeners.values())
    ordered = sorted(listeners.values(), reverse=True)
    running, threshold = 0, ordered[0]
    for count in ordered:
        running += count
        threshold = count
        if running >= share * total:
            break
    head = frozenset(i for i, n in listeners.items() if n >= threshold)
    return HeadSplit(
        head,
        frozenset(listeners) - head,
        threshold,
        sum(listeners[i] for i in head) / total,
        total,
    )


def non_head_exposure(
    recommendations: Mapping[str, list[str]],
    users: Iterable[str],
    non_head: frozenset[str],
    k: int = 10,
) -> dict[str, float]:
    """e_u = |R_u[:k] ∩ T| / k: tỷ lệ gợi ý thuộc nhóm ngoài đầu; mẫu số luôn là k."""
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    return {u: sum(i in non_head for i in recommendations[u][:k]) / k for u in users}


def popularity_alignment(
    recommendations: Mapping[str, list[str]],
    references: Mapping[str, set[str]],
    popularity: Mapping[str, float],
    users: Iterable[str],
    k: int = 10,
) -> dict[str, float | None]:
    """|trung bình p(R_u[:k]) − trung bình p(tham chiếu của u)|, mỗi nghệ sĩ cùng trọng số.

    Dùng để chia người dùng theo mức ưa chuộng nghệ sĩ phổ biến. Tham chiếu là lịch sử
    huấn luyện thì ra A_history, là đích để dành thì ra A_target. Người có danh sách rỗng
    hoặc không có tham chiếu trong danh mục nhận None, không gán độ phổ biến 0.
    """
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    result: dict[str, float | None] = {}
    for u in users:
        listed = recommendations[u][:k]
        reference = [i for i in references[u] if i in popularity]
        if not listed or not reference:
            result[u] = None
            continue
        listed_mean = fsum(popularity[i] for i in listed) / len(listed)
        result[u] = abs(listed_mean - fsum(popularity[i] for i in reference) / len(reference))
    return result


def mean_defined(values: Mapping[str, float | None]) -> dict[str, Any]:
    """Trung bình trên người dùng có giá trị xác định, kèm mẫu số."""
    defined = [v for v in values.values() if v is not None]
    return {"mean": fsum(defined) / len(defined) if defined else None, "users": len(defined)}
