import numpy as np
import pytest
from scipy.stats import wilcoxon

from musicrec.evaluation.inference import resample_indices
from musicrec.evaluation.paired import (
    equivalence_test,
    mean_interval,
    paired_comparison,
    percentile_interval,
    rank_biserial,
    signed_rank_sums,
)


def test_signed_rank_sums_drop_zeros_and_average_ties() -> None:
    # |d| = 1, 1, 2 after dropping the zero -> ranks 1.5, 1.5, 3.
    plus, minus = signed_rank_sums([0.0, 1.0, -1.0, 2.0])
    assert (plus, minus) == (4.5, 1.5)


def test_signed_rank_sums_match_scipy_statistic() -> None:
    diff = np.array([0.3, -0.1, 0.0, 0.2, -0.4, 0.2, 0.05])
    plus, minus = signed_rank_sums(diff)
    assert min(plus, minus) == pytest.approx(wilcoxon(diff, zero_method="wilcox").statistic)
    nonzero = np.count_nonzero(diff)
    assert plus + minus == nonzero * (nonzero + 1) / 2


def test_rank_biserial_bounds_and_hand_value() -> None:
    assert rank_biserial([1.0, 2.0, 0.0]) == 1.0
    assert rank_biserial([-1.0, -2.0]) == -1.0
    assert rank_biserial([0.0, 1.0, -1.0, 2.0]) == pytest.approx((4.5 - 1.5) / 6)
    assert rank_biserial([0.0, 0.0]) is None


def test_tost_interval_rule() -> None:
    inside = equivalence_test(-0.004, 0.001, 0.009)
    assert inside["equivalent"] and inside["lower_test_rejects"] and inside["upper_test_rejects"]
    upper = equivalence_test(-0.004, 0.01, 0.009)
    assert not upper["equivalent"] and upper["lower_test_rejects"]
    assert not upper["upper_test_rejects"]
    # The margin is open: touching the bound is not equivalence.
    assert not equivalence_test(-0.009, 0.0, 0.009)["equivalent"]
    with pytest.raises(ValueError):
        equivalence_test(-0.1, 0.1, 0.0)
    with pytest.raises(ValueError):
        equivalence_test(0.1, -0.1, 0.2)


def test_shared_indices_make_mirrored_pairs_consistent() -> None:
    rng = np.random.default_rng(0)
    users = [str(i) for i in range(1, 41)]
    a = dict(zip(users, rng.random(40), strict=True))
    b = dict(zip(users, rng.random(40), strict=True))
    c = dict(zip(users, rng.random(40), strict=True))
    indices = resample_indices(len(users), 500, 42)
    ab = paired_comparison(a, b, indices)
    ba = paired_comparison(b, a, indices)
    assert ab["ci95_low"] == pytest.approx(-ba["ci95_high"])
    assert ab["ci90_high"] == pytest.approx(-ba["ci90_low"])
    assert ab["rank_biserial"] == pytest.approx(-ba["rank_biserial"])
    # Bootstrap means are linear in the per-user values when the indices are shared.
    ac = paired_comparison(a, c, indices)
    cb = paired_comparison(c, b, indices)
    means = lambda x, y: (np.array([x[u] - y[u] for u in users]))[indices].mean(axis=1)  # noqa: E731
    np.testing.assert_allclose(means(a, c) + means(c, b), means(a, b))
    assert ab["mean_difference"] == pytest.approx(ac["mean_difference"] + cb["mean_difference"])
    assert ab["ci90_low"] >= ab["ci95_low"] and ab["ci90_high"] <= ab["ci95_high"]


def test_shared_indices_equal_first_draw_of_legacy_generator() -> None:
    legacy = np.random.default_rng(42).integers(0, 30, size=(1000, 30))
    np.testing.assert_array_equal(resample_indices(30, 1000, 42), legacy)


def test_paired_comparison_rejects_mismatch() -> None:
    indices = resample_indices(2, 10, 42)
    with pytest.raises(ValueError):
        paired_comparison({"1": 0.1, "2": 0.2}, {"1": 0.1, "3": 0.2}, indices)
    with pytest.raises(ValueError):
        paired_comparison({"1": 0.1, "2": 0.2, "3": 0.0}, {"1": 0, "2": 0, "3": 0}, indices)


def test_mean_interval_and_percentile_level() -> None:
    indices = resample_indices(5, 200, 42)
    result = mean_interval([0.0, 0.1, 0.2, 0.3, 0.4], indices)
    assert result["mean"] == pytest.approx(0.2)
    assert result["ci95_low"] <= result["ci90_low"] <= result["ci90_high"] <= result["ci95_high"]
    with pytest.raises(ValueError):
        percentile_interval(np.array([0.0, 1.0]), 1.0)
