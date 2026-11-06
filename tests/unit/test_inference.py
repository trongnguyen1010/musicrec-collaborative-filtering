"""Hand-computed bootstrap p-values, CIs, boundary cases, p_joint and Holm."""

import numpy as np
import pytest

from musicrec.evaluation.inference import (
    bootstrap_contrast,
    holm,
    joint_test,
    resample_indices,
)


def test_hand_p_value_and_quantile_on_explicit_resamples() -> None:
    indices = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [0, 1, 2]])
    result = bootstrap_contrast([1.0, -1.0, 2.0], indices)
    # mean 2/3; centered resample means 1/3, -5/3, 4/3, 0: one of four reaches 2/3.
    assert result["mean"] == pytest.approx(2 / 3)
    assert result["p_one_sided"] == pytest.approx(2 / 5)
    # Uncentered means sorted -1, 2/3, 1, 2; linear q05 at position 0.15.
    assert result["ci95_one_sided_lower"] == pytest.approx(-1 + 0.15 * 5 / 3)


def test_zero_constant_and_invalid_contrasts() -> None:
    indices = resample_indices(4, resamples=50)
    assert bootstrap_contrast([0.0] * 4, indices)["p_one_sided"] == 1.0
    assert bootstrap_contrast([0.2] * 4, indices)["p_one_sided"] == pytest.approx(1 / 51)
    for bad in [[], [np.nan, 0, 0, 0], [np.inf, 0, 0, 0]]:
        with pytest.raises(ValueError):
            bootstrap_contrast(bad, indices)
    with pytest.raises(ValueError, match="match"):
        bootstrap_contrast([1.0, 2.0], indices)
    with pytest.raises(ValueError):
        resample_indices(0)
    np.testing.assert_array_equal(resample_indices(5, 10), resample_indices(5, 10))


def test_joint_p_is_the_larger_component_and_uses_the_margin() -> None:
    indices = resample_indices(4, resamples=200)
    result = joint_test([0.5, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5], [1, 0, 0, 0], [0] * 4, indices)
    # a - 0.95b is a constant 0.025 > 0, so its p is the minimum 1/(B+1).
    assert result["ndcg_non_inferiority"]["mean"] == pytest.approx(0.025)
    assert result["ndcg_non_inferiority"]["p_one_sided"] == pytest.approx(1 / 201)
    assert result["p_joint"] == result["exposure_superiority"]["p_one_sided"]
    with pytest.raises(ValueError, match="aligned"):
        joint_test([0.1], [0.1, 0.2], [0.1], [0.1], indices)


def test_holm_hand_values_monotone_and_capped() -> None:
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, 0.9]) == [1.0, 1.0]
    with pytest.raises(ValueError):
        holm([1.2])
