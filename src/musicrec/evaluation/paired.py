"""Paired per-user comparisons on one shared bootstrap index matrix.

Every pair of one cohort is resampled with the same (resamples, users) user-index matrix
(musicrec.evaluation.inference.resample_indices), so all intervals of one table come from
the same bootstrap replicates. Per pair: mean difference (A - B), 95% and 90% percentile
bootstrap intervals, two-sided Wilcoxon signed-rank p (zero differences dropped) and the
matched-pairs rank-biserial correlation r_rb = (W+ - W-) / (W+ + W-) on the same nonzero
differences. Equivalence (TOST at level 0.05) holds when the 90% interval lies strictly
inside (-delta, delta).
"""

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.stats import rankdata, wilcoxon


def aligned(a: Mapping[str, float], b: Mapping[str, float]) -> tuple[list[str], NDArray[Any]]:
    """Users sorted by integer id and the per-user difference A - B on that order."""
    if a.keys() != b.keys():
        raise ValueError("Paired methods must share the eligible cohort")
    users = sorted(a, key=int)
    return users, np.array([a[u] - b[u] for u in users], dtype=np.float64)


def signed_rank_sums(diff: Sequence[float] | NDArray[Any]) -> tuple[float, float]:
    """W+ and W- of the Wilcoxon signed-rank statistic after dropping zero differences.

    Ties in |d| receive average ranks, matching scipy's zero_method='wilcox'.
    """
    values = np.asarray(diff, dtype=np.float64)
    nonzero = values[values != 0]
    if not len(nonzero):
        return 0.0, 0.0
    ranks = rankdata(np.abs(nonzero), method="average")
    return float(ranks[nonzero > 0].sum()), float(ranks[nonzero < 0].sum())


def rank_biserial(diff: Sequence[float] | NDArray[Any]) -> float | None:
    """Matched-pairs rank-biserial correlation (W+ - W-)/(W+ + W-); None if all d = 0."""
    plus, minus = signed_rank_sums(diff)
    total = plus + minus
    return None if total == 0 else (plus - minus) / total


def percentile_interval(means: NDArray[Any], level: float) -> tuple[float, float]:
    """Two-sided percentile interval of bootstrap means at the given level."""
    if not 0 < level < 1:
        raise ValueError("level must lie in (0, 1)")
    tail = 100 * (1 - level) / 2
    return float(np.percentile(means, tail)), float(np.percentile(means, 100 - tail))


def bootstrap_means(values: NDArray[Any], indices: NDArray[np.int64]) -> NDArray[Any]:
    """Mean of each bootstrap replicate drawn with the shared index matrix."""
    if indices.ndim != 2 or indices.shape[1] != len(values):
        raise ValueError("Resample indices must match the cohort size")
    means: NDArray[Any] = np.asarray(values[indices].mean(axis=1), dtype=np.float64)
    return means


def mean_interval(
    values: Sequence[float] | NDArray[Any], indices: NDArray[np.int64]
) -> dict[str, Any]:
    """Mean of one model's per-user metric with 95% and 90% shared-bootstrap intervals."""
    array = np.asarray(values, dtype=np.float64)
    means = bootstrap_means(array, indices)
    low95, high95 = percentile_interval(means, 0.95)
    low90, high90 = percentile_interval(means, 0.90)
    return {
        "mean": float(array.mean()),
        "ci95_low": low95,
        "ci95_high": high95,
        "ci90_low": low90,
        "ci90_high": high90,
    }


def paired_comparison(
    a: Mapping[str, float], b: Mapping[str, float], indices: NDArray[np.int64]
) -> dict[str, Any]:
    """Mean difference, shared-bootstrap 95%/90% CIs, Wilcoxon p and rank-biserial r."""
    users, diff = aligned(a, b)
    means = bootstrap_means(diff, indices)
    low95, high95 = percentile_interval(means, 0.95)
    low90, high90 = percentile_interval(means, 0.90)
    nonzero = int(np.count_nonzero(diff))
    plus, minus = signed_rank_sums(diff)
    return {
        "users": len(users),
        "nonzero_differences": nonzero,
        "positive_differences": int((diff > 0).sum()),
        "negative_differences": int((diff < 0).sum()),
        "mean_a": float(np.mean([a[u] for u in users])),
        "mean_b": float(np.mean([b[u] for u in users])),
        "mean_difference": float(diff.mean()),
        "ci95_low": low95,
        "ci95_high": high95,
        "ci90_low": low90,
        "ci90_high": high90,
        "wilcoxon_p": float(wilcoxon(diff, zero_method="wilcox").pvalue) if nonzero else 1.0,
        "w_plus": plus,
        "w_minus": minus,
        "rank_biserial": rank_biserial(diff),
    }


def equivalence_test(ci90_low: float, ci90_high: float, delta: float) -> dict[str, Any]:
    """TOST decision by the interval rule: equivalent iff -delta < CI90 low and high < delta."""
    if not delta > 0:
        raise ValueError("delta must be positive")
    if ci90_low > ci90_high:
        raise ValueError("Interval bounds are reversed")
    return {
        "delta": float(delta),
        "margin": [-float(delta), float(delta)],
        "ci90": [float(ci90_low), float(ci90_high)],
        "lower_test_rejects": bool(ci90_low > -delta),
        "upper_test_rejects": bool(ci90_high < delta),
        "equivalent": bool(-delta < ci90_low and ci90_high < delta),
        "rule": "tost_alpha_0.05_via_90pct_bootstrap_interval_inside_open_margin",
    }
