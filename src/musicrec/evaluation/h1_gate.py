"""Cổng phát triển H1 trên tập xác thực và quy tắc khóa cấu hình cho các điểm cấu hình thực.

Cổng chỉ dùng ước lượng điểm của tập xác thực với hạt giống 42. Đây không phải bảo đảm
thống kê sau khi chọn; epsilon là dung sai số học, không phải biên có ý nghĩa thực tế.
"""

from math import isfinite
from typing import Any

EPSILON = 1e-12
NDCG_MARGIN = 0.95
SPECTRAL_FAMILIES = ("global", "deviation")


def _check(point: dict[str, Any]) -> None:
    # Chặn họ cấu hình lạ và giá trị không hữu hạn.
    if point["family"] not in (*SPECTRAL_FAMILIES, "direct"):
        raise ValueError("Unknown configuration family")
    if not all(isfinite(point[name]) for name in ["coefficient", "ndcg", "exposure"]):
        raise ValueError("Gate points need finite coefficients and metrics")


def dominates(q: dict[str, Any], c: dict[str, Any]) -> bool:
    """q trội hơn c: không kém về NDCG lẫn độ xuất hiện, và hơn hẳn (quá epsilon) ở ít nhất một."""
    return bool(
        q["ndcg"] >= c["ndcg"] - EPSILON
        and q["exposure"] >= c["exposure"] - EPSILON
        and (q["ndcg"] > c["ndcg"] + EPSILON or q["exposure"] > c["exposure"] + EPSILON)
    )


def _best(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    # Ưu tiên độ xuất hiện cao, rồi NDCG cao, rồi hệ số nhỏ.
    return min(points, key=lambda p: (-p["exposure"], -p["ndcg"], p["coefficient"]), default=None)


def apply_gate(points: list[dict[str, Any]], base: dict[str, float]) -> dict[str, Any]:
    """Áp dụng sáu bước của cổng đã thống nhất, trả cấu hình được khóa và lý do.

    points: {family, coefficient, ndcg, exposure}; coefficient là gamma_0 hoặc beta.
    base: {ndcg, exposure} của mô hình ALS gốc chưa điều chỉnh.
    """
    for point in points:
        _check(point)
    bound = NDCG_MARGIN * base["ndcg"]
    base_point = {"family": "base", "coefficient": 0.0, **base}
    spectral = [
        p
        for p in points
        if p["family"] in SPECTRAL_FAMILIES
        and p["coefficient"] > 0
        and p["ndcg"] >= bound
        and p["exposure"] > base["exposure"] + EPSILON
    ]
    feasible_direct = [
        p for p in points if p["family"] == "direct" and p["coefficient"] > 0 and p["ndcg"] >= bound
    ]
    controls = [base_point, *feasible_direct]
    undominated = [c for c in spectral if not any(dominates(q, c) for q in controls)]
    if not spectral:
        status = "stop_no_spectral_configuration_within_bound_and_raising_exposure"
    elif not feasible_direct:
        status = "advance_direct_control_has_no_feasible_point_in_locked_grid"
    elif not undominated:
        status = "stop_all_spectral_configurations_dominated_by_direct_control"
    else:
        status = "advance_undominated_spectral_configuration"
    advance = status.startswith("advance")
    locks = {f: _best([c for c in undominated if c["family"] == f]) for f in SPECTRAL_FAMILIES}
    if not advance:
        locks = dict.fromkeys(SPECTRAL_FAMILIES)
    # min() giữ phần tử đầu khi hòa hoàn toàn, và họ "global" được liệt kê trước.
    representative = _best([c for c in locks.values() if c is not None])
    raising = [p for p in feasible_direct if p["exposure"] > base["exposure"] + EPSILON]
    direct = _best(raising) or {"family": "direct", "coefficient": 0.0, **base}
    return {
        "status": status,
        "advance": advance,
        "ndcg_bound": bound,
        "spectral_candidates": spectral,
        "feasible_direct_controls": feasible_direct,
        "undominated_spectral": undominated,
        "locked": locks,
        "representative": representative,
        "direct_control": direct,
        "direct_control_has_feasible_point": bool(feasible_direct),
    }
