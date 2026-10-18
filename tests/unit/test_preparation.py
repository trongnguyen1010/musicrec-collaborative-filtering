from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from musicrec.data.contracts import Interaction
from musicrec.data.preparation import (
    fit_transform,
    split_interactions,
    split_summary,
    transform_counts,
    validate_interactions,
)


@pytest.mark.parametrize(
    "body",
    [
        "",
        "userID\tartistID\tweight\n",
        "a\tb\tc\n1\t2\t3",
        "userID\tartistID\tweight\n\t2\t3",
        "userID\tartistID\tweight\n1\t2\tNaN",
        "userID\tartistID\tweight\n1\t2\tinf",
        "userID\tartistID\tweight\n1\t2\t0",
        "userID\tartistID\tweight\n1\t2\t-1",
    ],
)
def test_invalid_source_is_rejected(tmp_path: Path, body: str) -> None:
    source = tmp_path / "input.dat"
    source.write_text(body, encoding="utf-8")
    with pytest.raises(ValueError):
        validate_interactions(source)


def test_duplicates_aggregate_counts_before_splitting(tmp_path: Path) -> None:
    source = tmp_path / "input.dat"
    source.write_text("userID\tartistID\tweight\nu1\ta\t2\nu1\ta\t3\nu2\tb\t1\n")
    frame, report = validate_interactions(source)
    assert len(frame) == 2
    assert frame.iloc[0].listening_count == 5
    assert report["duplicate_rows_merged"] == 1


def test_split_rounding_conservation_order_and_cold_targets() -> None:
    frame = pd.DataFrame(
        [
            {"user_id": str(n), "item_id": f"{n}_{i:02}", "listening_count": i + 1}
            for n in (4, 5, 10, 50)
            for i in range(n)
        ]
    )
    splits = split_interactions(frame, 42)
    expected = {4: (4, 0, 0), 5: (3, 1, 1), 10: (8, 1, 1), 50: (40, 5, 5)}
    for n, counts in expected.items():
        assert tuple(len(s[s.user_id == str(n)]) for s in splits.values()) == counts
    repeated = split_interactions(frame.sample(frac=1, random_state=123), 42)
    for name in splits:
        pd.testing.assert_frame_equal(splits[name], repeated[name])
    assert sum(len(s) for s in splits.values()) == len(frame)
    assert sum(s.listening_count.sum() for s in splits.values()) == frame.listening_count.sum()
    assert split_summary(splits)["validation"]["cold_targets"] == 7


def test_transform_is_fitted_on_train_and_preserves_raw_counts() -> None:
    train = pd.DataFrame({"listening_count": [1, 3, 7, 15, 31]})
    transform = fit_transform(train)
    assert transform["thresholds"] == pytest.approx([1.8, 2.6, 3.4, 4.2])
    other = transform_counts(pd.DataFrame({"listening_count": [1, 10**9]}), transform)
    assert other.preference_proxy.tolist() == [1, 5]
    assert other.listening_count.tolist() == [1, 10**9]
    tied = fit_transform(pd.DataFrame({"listening_count": [1, 1, 1, 1, 1]}))
    assert transform_counts(train, tied).preference_proxy.iloc[0] == 1


@pytest.mark.parametrize("count", [np.nan, np.inf, -np.inf, 0, -1])
def test_interaction_rejects_invalid_counts(count: float) -> None:
    with pytest.raises(ValueError):
        Interaction("u", "i", count)
