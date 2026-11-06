"""Hand-computed head/non-head boundaries, exposure denominators and alignment values."""

import pytest

from musicrec.evaluation.exposure import (
    head_split,
    mean_defined,
    non_head_exposure,
    popularity_alignment,
)


def test_shortest_prefix_ties_at_cut_and_empty_non_head() -> None:
    split = head_split({"a": 5, "b": 3, "c": 3, "d": 1, "e": 1})
    # M=13, target 2.6: the first artist already reaches it.
    assert split.head == {"a"} and split.non_head == {"b", "c", "d", "e"}
    assert split.threshold_listeners == 5 and split.head_pair_share == pytest.approx(5 / 13)
    tied = head_split({"a": 3, "b": 3, "c": 3, "d": 1})
    # M=10, target 2: the cut lands on a tie, so all artists with 3 listeners join the head.
    assert tied.head == {"a", "b", "c"} and tied.head_pair_share == pytest.approx(0.9)
    empty = head_split({"a": 1, "b": 1})
    assert empty.non_head == frozenset() and empty.summary()["non_head_artists"] == 0
    assert split.summary()["head_sha256"] != tied.summary()["head_sha256"]
    for bad in [{}, {"a": 0}, {"a": 1.5}]:
        with pytest.raises(ValueError):
            head_split(bad)


def test_exposure_denominator_is_k_for_short_lists() -> None:
    lists = {"u": ["a", "x", "y"], "v": [], "w": ["x"] * 12}
    exposure = non_head_exposure(lists, ["u", "v", "w"], frozenset({"x", "y"}), k=10)
    assert exposure == {"u": 0.2, "v": 0.0, "w": 1.0}


def test_alignment_hand_values_and_undefined_cases() -> None:
    popularity = {"a": 1.0, "b": 0.5, "c": 0.0}
    lists = {"u": ["a", "b"], "v": ["c"], "w": []}
    references = {"u": {"c"}, "v": {"outside"}, "w": {"a"}}
    values = popularity_alignment(lists, references, popularity, ["u", "v", "w"])
    assert values == {"u": 0.75, "v": None, "w": None}
    assert mean_defined(values) == {"mean": 0.75, "users": 1}
    assert mean_defined({"u": None}) == {"mean": None, "users": 0}
