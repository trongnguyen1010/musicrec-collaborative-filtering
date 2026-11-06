"""H1 validation development gate and lock rule on finite, real configuration points.

The gate uses point estimates from validation seed 42 only. It is not a post-selection
statistical guarantee, and epsilon is numerical tolerance, not a practical margin.
"""

from math import isfinite
from typing import Any

EPSILON = 1e-12
NDCG_MARGIN = 0.95
SPECTRAL_FAMILIES = ("global", "deviation")


def _check(point: dict[str, Any]) -> None:
    if point["family"] not in (*SPECTRAL_FAMILIES, "direct"):
        raise ValueError("Unknown configuration family")
    if not all(isfinite(point[name]) for name in ["coefficient", "ndcg", "exposure"]):
        raise ValueError("Gate points need finite coefficients and metrics")


def dominates(q: dict[str, Any], c: dict[str, Any]) -> bool:
    """q is no worse on NDCG and exposure, and better on one of them by more than epsilon."""
    return bool(
        q["ndcg"] >= c["ndcg"] - EPSILON
        and q["exposure"] >= c["exposure"] - EPSILON
        and (q["ndcg"] > c["ndcg"] + EPSILON or q["exposure"] > c["exposure"] + EPSILON)
    )


def _best(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    return min(points, key=lambda p: (-p["exposure"], -p["ndcg"], p["coefficient"]), default=None)


def apply_gate(points: list[dict[str, Any]], base: dict[str, float]) -> dict[str, Any]:
    """Apply steps 1-6 of the agreed gate and return locks plus the reason for each.

    points: {family, coefficient, ndcg, exposure}; coefficient is gamma_0 or beta.
    base: {ndcg, exposure} of the unmodified ALS checkpoint.
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
    # min() keeps the first of fully tied keys, and the global family is listed first.
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
