"""Protect the distinction between duplicate, conflicting and invalid feedback."""

import pandas as pd

from scripts.eda import interaction_quality


def test_quality_counts_conflicts_and_invalid_values_without_mutating() -> None:
    frame = pd.DataFrame(
        [
            ("u", "a", "1"),
            ("u", "a", "1"),
            ("u", "a", "2"),
            ("v", "b", "0"),
            ("v", "c", "-1"),
            ("v", "d", "inf"),
            ("v", "e", "bad"),
            ("", "f", "3"),
        ],
        columns=["userID", "artistID", "weight"],
    )
    original = frame.copy(deep=True)
    result, valid = interaction_quality(frame)
    assert result["exact_duplicate_extra_rows"] == 1
    assert result["duplicate_pair_extra_rows"] == 2
    assert result["pairs_with_conflicting_valid_counts"] == 1
    assert result["nonpositive_finite_weight"] == 2
    assert result["infinite_weight"] == 1
    assert result["nonnumeric_or_missing_weight"] == 1
    assert result["rows_with_blank_id"] == 1
    assert valid.tolist() == [True, True, True, False, False, False, False, False]
    pd.testing.assert_frame_equal(frame, original)
