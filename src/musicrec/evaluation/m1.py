"""Predeclared validation-only selection and fixed-parameter seed confirmation for M1."""

from math import isfinite


def within_drop(candidate: float, baseline: float, max_drop: float = 0.05) -> bool:
    """Apply an inclusive relative NDCG bound, including the zero-baseline case."""
    if not all(isfinite(x) for x in [candidate, baseline, max_drop]):
        raise ValueError("NDCG and bound must be finite")
    if not 0 <= candidate <= 1 or not 0 <= baseline <= 1 or not 0 <= max_drop <= 1:
        raise ValueError("NDCG and bound must lie in [0, 1]")
    return candidate >= baseline * (1 - max_drop)


def select_full_variant(
    rows: list[dict[str, float]], baseline_ndcg: float, max_drop: float = 0.05
) -> dict[str, float] | None:
    """Select only full variants by ARP, descending ILD/NDCG, then parameter order."""
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
