"""H1 paired user bootstrap, intersection-union p-values and Holm adjustment.

The one-sided p-value is an approximate bootstrap under the null boundary mean=0:
z is centered, resampled with the shared indices, and compared with the observed mean.
"""

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

RESAMPLES = 10_000
SEED = 42
NDCG_MARGIN = 0.95


def resample_indices(users: int, resamples: int = RESAMPLES, seed: int = SEED) -> NDArray[np.int64]:
    """One shared (resamples, users) index matrix for every method and contrast."""
    if type(users) is not int or users <= 0:
        raise ValueError("The cohort must be non-empty")
    if type(resamples) is not int or resamples <= 0:
        raise ValueError("resamples must be a positive integer")
    return np.random.default_rng(seed).integers(0, users, size=(resamples, users))


def bootstrap_contrast(
    z: Sequence[float] | NDArray[Any], indices: NDArray[np.int64]
) -> dict[str, Any]:
    """Mean, linear-quantile CIs from uncentered resamples and a one-sided p for mean>0."""
    values = np.asarray(z, dtype=np.float64)
    if values.ndim != 1 or not len(values):
        raise ValueError("The contrast needs a non-empty cohort")
    if not np.isfinite(values).all():
        raise ValueError("Contrast values must be finite")
    if indices.ndim != 2 or indices.shape[1] != len(values):
        raise ValueError("Resample indices must match the cohort size")
    mean = float(values.mean())
    means = values[indices].mean(axis=1)
    if not values.any():
        p_value = 1.0
    else:
        centered = (values - mean)[indices].mean(axis=1)
        p_value = float((1 + np.count_nonzero(centered >= mean)) / (len(indices) + 1))
    return {
        "mean": mean,
        "ci95_one_sided_lower": float(np.quantile(means, 0.05, method="linear")),
        "ci95_two_sided": [
            float(np.quantile(means, 0.025, method="linear")),
            float(np.quantile(means, 0.975, method="linear")),
        ],
        "p_one_sided": p_value,
        "users": len(values),
        "resamples": len(indices),
    }


def joint_test(
    ndcg_new: Sequence[float] | NDArray[Any],
    ndcg_base: Sequence[float] | NDArray[Any],
    exposure_new: Sequence[float] | NDArray[Any],
    exposure_base: Sequence[float] | NDArray[Any],
    indices: NDArray[np.int64],
) -> dict[str, Any]:
    """Success needs mean(a-0.95b)>0 and mean(e_new-e_base)>0; p_joint=max(p_N, p_E)."""
    a, b = np.asarray(ndcg_new, dtype=np.float64), np.asarray(ndcg_base, dtype=np.float64)
    e, f = np.asarray(exposure_new, dtype=np.float64), np.asarray(exposure_base, dtype=np.float64)
    if not a.shape == b.shape == e.shape == f.shape:
        raise ValueError("All per-user arrays must be aligned on the same cohort")
    accuracy = bootstrap_contrast(a - NDCG_MARGIN * b, indices)
    exposure = bootstrap_contrast(e - f, indices)
    return {
        "ndcg_non_inferiority": accuracy,
        "exposure_superiority": exposure,
        "p_joint": max(accuracy["p_one_sided"], exposure["p_one_sided"]),
    }


def holm(p_values: Sequence[float]) -> list[float]:
    """Holm step-down adjustment, monotone and capped at 1."""
    if not all(0 <= p <= 1 for p in p_values):
        raise ValueError("p-values must lie in [0, 1]")
    order = np.argsort(p_values, kind="stable")
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(p_values) - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted
