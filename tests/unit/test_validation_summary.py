"""Toy checks for fixed-catalog subgroup and model-seed summaries."""

from copy import deepcopy

import pytest

from musicrec.evaluation.ranking import evaluate_ranking
from musicrec.evaluation.validation import (
    compare_seed_models,
    summarize_history_groups,
    summarize_seeds,
)


def example() -> dict:
    train = {"1": {"a"}, "2": {"b", "c"}, "3": {"a", "c"}, "4": {"a", "b", "c"}}
    targets = {"1": {"b"}, "2": {"a"}, "3": {"b"}, "4": {"outside"}}
    lists = {"1": ["b", "c"], "2": ["a"], "3": [], "4": []}
    return evaluate_ranking(lists, targets, train, ks=(1, 2))


def test_history_groups_keep_full_catalog_scores_zero_return_users_and_empty_groups() -> None:
    evaluation = example()
    result = summarize_history_groups(evaluation, {"1": 1, "2": 2, "3": 2, "4": 3})
    assert result["train_history_mode"] == 2
    groups = result["groups"]
    assert groups["below_mode"]["at_k"]["1"]["ndcg"] == 1
    assert groups["at_mode"]["at_k"]["1"]["ndcg"] == 0.5
    assert groups["at_mode"]["users_eligible"] == 2  # Includes an empty recommendation list.
    assert groups["above_mode"]["users_eligible"] == 0
    assert groups["above_mode"]["targets_outside_catalog"] == 1
    assert groups["above_mode"]["at_k"]["1"]["ndcg"] is None
    empty = summarize_history_groups(evaluation, {u: 2 for u in evaluation["per_user"]})
    assert empty["groups"]["below_mode"]["users_total"] == 0
    with pytest.raises(ValueError, match="exactly"):
        summarize_history_groups(evaluation, {"1": 1})


def test_seed_summary_uses_all_three_seeds_sample_std_and_rejects_cohort_drift() -> None:
    seeds = {seed: deepcopy(example()) for seed in [42, 43, 44]}
    for seed, score in [(42, 0.2), (43, 0.4), (44, 0.6)]:
        seeds[seed]["at_k"]["1"]["ndcg"] = score
    stats = summarize_seeds(seeds)["at_k"]["1"]["ndcg"]
    assert stats["mean"] == pytest.approx(0.4)
    assert stats["sample_std"] == pytest.approx(0.2)
    assert stats["max"] == 0.6
    with pytest.raises(ValueError, match="exactly"):
        summarize_seeds({42: seeds[42], 43: seeds[43]})
    seeds[44]["per_user"]["1"]["candidate_count"] += 1
    with pytest.raises(ValueError, match="cohort"):
        summarize_seeds(seeds)


def test_retention_gate_requires_higher_mean_two_positive_seeds_and_same_cohort() -> None:
    control = {seed: deepcopy(example()) for seed in [42, 43, 44]}
    for value in control.values():
        value["at_k"]["1"]["ndcg"] = 0.5
    candidate = deepcopy(control)
    for seed, score in [(42, 0.75), (43, 0.75), (44, 0.25)]:
        candidate[seed]["at_k"]["1"]["ndcg"] = score
    assert compare_seed_models(candidate, control, k=1)["passes"]
    for seed, score in [(42, 1.0), (43, 0.45), (44, 0.45)]:
        candidate[seed]["at_k"]["1"]["ndcg"] = score
    assert not compare_seed_models(candidate, control, k=1)["passes"]  # Higher mean, one win.
    assert not compare_seed_models(control, control, k=1)["passes"]
    candidate[42]["catalog_size"] += 1
    with pytest.raises(ValueError, match="cohort"):
        compare_seed_models(candidate, control, k=1)
