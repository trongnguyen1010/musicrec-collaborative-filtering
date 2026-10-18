import pandas as pd
import pytest

from musicrec.final_evaluation import paired_statistics


def test_paired_bootstrap_alignment_and_zero_differences() -> None:
    left = pd.Series([0.2, 0.4], index=["a", "b"])
    right = pd.Series([0.4, 0.2], index=["b", "a"])
    result = paired_statistics(left, right, 100, 42)
    assert result["mean_difference"] == 0 and result["p_raw"] == 1
    assert result["ci95"] == [0, 0]
    with pytest.raises(ValueError, match="identical"):
        paired_statistics(left, right.iloc[:1], 100, 42)
