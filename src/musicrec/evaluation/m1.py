"""Quy tắc chọn λ, β của M1, khai báo trước và chỉ dùng tập xác thực (mục 3.7.3).

Tập kiểm thử không tham gia chọn cấu hình, nên kết quả trên tập kiểm thử không bị lạc quan.
"""

from math import isfinite


def within_drop(candidate: float, baseline: float, max_drop: float = 0.05) -> bool:
    """Kiểm tra NDCG@10 của ứng viên không giảm quá max_drop (mặc định 5%) so với mô hình nền.

    Biên tính theo tỷ lệ và có lấy dấu bằng; mô hình nền bằng 0 vẫn xử lý được.
    """
    if not all(isfinite(x) for x in [candidate, baseline, max_drop]):
        raise ValueError("NDCG and bound must be finite")
    if not 0 <= candidate <= 1 or not 0 <= baseline <= 1 or not 0 <= max_drop <= 1:
        raise ValueError("NDCG and bound must lie in [0, 1]")
    return candidate >= baseline * (1 - max_drop)


def select_full_variant(
    rows: list[dict[str, float]], baseline_ndcg: float, max_drop: float = 0.05
) -> dict[str, float] | None:
    """Chọn cấu hình M1 đầy đủ (λ < 1 và β > 0) trên tập xác thực.

    Chỉ xét cấu hình giữ NDCG@10 trong biên within_drop; trong đó chọn ARP thấp nhất,
    hòa thì ILD cao hơn, rồi NDCG cao hơn, rồi λ, β nhỏ hơn. Trả None nếu không có.
    """
    eligible = []
    for row in rows:
        if not all(isfinite(row[name]) for name in ["lambda", "beta", "arp", "ild", "ndcg"]):
            raise ValueError("Selection rows must contain finite parameters and metrics")
        if (
            0 <= row["lambda"] < 1
            and row["beta"] > 0
            and within_drop(row["ndcg"], baseline_ndcg, max_drop)
        ):
            eligible.append(row)
    return min(
        eligible,
        key=lambda r: (r["arp"], -r["ild"], -r["ndcg"], r["lambda"], r["beta"]),
        default=None,
    )
