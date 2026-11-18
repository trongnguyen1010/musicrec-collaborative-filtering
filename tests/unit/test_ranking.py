import hashlib
import json
import subprocess
import sys
from math import log2, sqrt
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import ndcg_score

from musicrec.evaluation.ranking import (
    evaluate_ranking,
    gini_index,
    ndcg_at_k,
    precision_at_k,
    proxy_rmse,
    rank_candidates,
    recall_at_k,
)


def test_ranking_metrics_use_only_top_k() -> None:
    recommended = ["a", "b", "c"]
    relevant = {"b", "c"}

    assert precision_at_k(recommended, relevant, k=2) == 0.5
    assert recall_at_k(recommended, relevant, k=2) == 0.5


def test_thesis_hand_calculations_and_short_lists() -> None:
    assert precision_at_k(["b", "a", "c"], {"a", "c"}, 3) == pytest.approx(2 / 3)
    assert recall_at_k(["b", "a", "c"], {"a", "c"}, 3) == 1
    assert ndcg_at_k(["b", "a", "c"], {"a", "c"}, 3) == pytest.approx(0.6934264036172708)
    assert ndcg_at_k(["a", "c", "b"], {"a", "c"}, 3) == 1
    assert precision_at_k(["a", "b", "c"], {"a", "c"}, 5) == 0.4
    assert ndcg_at_k(["a"], {"a", "b"}, 5) == pytest.approx(1 / (1 + 1 / log2(3)))
    for metric in [precision_at_k, recall_at_k, ndcg_at_k]:
        assert metric([], {"a"}, 5) == 0
        assert metric(["b"], {"a"}, 5) == 0
        assert metric(["a"], set(), 5) == 0
        with pytest.raises(ValueError, match="Duplicate"):
            metric(["a", "a"], {"a"}, 1)
        for k in [0, -1, True, 1.5]:
            with pytest.raises(ValueError):
                metric([], set(), k)


def test_ndcg_matches_independent_sklearn_for_multiple_targets_and_cutoffs() -> None:
    rng = np.random.default_rng(42)
    for _ in range(20):
        truth = rng.integers(0, 2, size=8)
        scores = rng.permutation(8).astype(float)
        order = [str(i) for i in np.argsort(-scores)]
        relevant = {str(i) for i, label in enumerate(truth) if label}
        for k in [1, 3, 8, 10]:
            assert ndcg_at_k(order, relevant, k) == pytest.approx(
                ndcg_score(truth[None, :], scores[None, :], k=k, ignore_ties=True)
            )


def test_full_ranking_masks_seen_and_uses_mapping_order_for_ties() -> None:
    catalog = ["2", "10", "30"]
    assert rank_candidates({"30": 1, "10": 1, "2": 1}, catalog, set(), 5) == catalog
    assert rank_candidates({"2": 100, "10": 1, "30": 2}, catalog, {"2"}, 2) == ["30", "10"]
    assert rank_candidates({}, catalog, set(catalog), 5) == []
    with pytest.raises(ValueError, match="every unseen"):
        rank_candidates({"2": 1}, catalog, set(), 1)
    with pytest.raises(ValueError, match="catalog"):
        rank_candidates({"unknown": 1}, catalog, set(), 1)
    for score in [float("nan"), float("inf"), -float("inf")]:
        with pytest.raises(ValueError, match="finite"):
            rank_candidates({"2": score, "10": 1, "30": 2}, catalog, set(), 1)


def test_cohort_metrics_keep_empty_recommendations_and_report_excluded_users() -> None:
    train = {"u1": {"a", "b"}, "u2": {"b", "c"}, "u3": {"d", "e"}, "u4": {"c", "f"}}
    targets = {"u1": {"c", "e", "z"}, "u2": {"d"}, "u3": {"z"}, "u4": {"a"}}
    recommendations = {"u1": ["c", "d", "e"], "u2": ["d"], "u3": ["a", "b"], "u4": []}
    result = evaluate_ranking(recommendations, targets, train, ks=(3, 5))
    assert result["users_eligible"] == 3
    assert result["users_without_catalog_targets"] == 1
    assert result["targets_outside_catalog"] == 2
    assert result["outside_catalog_target_rate"] == pytest.approx(2 / 6)
    metrics = result["at_k"]["3"]
    assert metrics["precision"] == pytest.approx(1 / 3)
    assert metrics["recall"] == pytest.approx(2 / 3)
    assert metrics["ndcg"] == pytest.approx(((1 + 0.5) / (1 + 1 / log2(3)) + 1) / 3)
    assert metrics["catalog_coverage"] == 0.5
    assert metrics["gini"] == pytest.approx(7 / 12)
    assert metrics["arp"] == 1.25
    assert metrics["novelty"] == pytest.approx((log2(14 / 3) + 3 * log2(7)) / 4)
    assert metrics["ild"] == pytest.approx(2 / 3)
    assert metrics["ild_users"] == 1
    assert metrics["returned_positions"] == 4
    assert metrics["short_list_users"] == 2
    assert metrics["empty_list_users"] == 1
    assert metrics["full_list_rate"] == pytest.approx(1 / 3)
    assert result["per_user"]["u3"]["at_k"] == {}
    assert result["at_k"]["5"]["precision"] == pytest.approx(0.2)


def test_ild_uses_binary_train_cosine() -> None:
    result = evaluate_ranking(
        {"u1": ["c", "f"], "u2": [], "u3": []},
        {"u1": {"c"}, "u2": set(), "u3": set()},
        {"u1": {"a"}, "u2": {"c", "f"}, "u3": {"c"}},
        ks=(2,),
    )
    assert result["at_k"]["2"]["ild"] == pytest.approx(1 - 1 / sqrt(2))


def test_validation_and_test_masking_and_train_statistics() -> None:
    train = {"u1": {"a"}, "u2": {"b", "c", "d"}}
    validation = {"u1": {"b", "z"}, "u2": {"a"}}
    targets = {"u1": {"c"}, "u2": {"z"}}
    recommendations = {"u1": ["c", "d"], "u2": []}
    result = evaluate_ranking(
        recommendations,
        targets,
        train,
        ks=(2,),
        split="test",
        validation=validation,
    )
    assert result["per_user"]["u1"]["candidate_count"] == 2
    assert result["at_k"]["2"]["arp"] == 1
    assert result["at_k"]["2"]["novelty"] == 2
    with pytest.raises(ValueError, match="requires validation"):
        evaluate_ranking(recommendations, targets, train, split="test")
    with pytest.raises(ValueError, match="only mask train"):
        evaluate_ranking(recommendations, targets, train, validation=validation)
    with pytest.raises(ValueError, match="seen"):
        evaluate_ranking(
            {"u1": ["b"], "u2": []}, targets, train, split="test", validation=validation
        )


def test_invalid_lists_and_split_overlap_are_rejected() -> None:
    train = {"u1": {"a"}, "u2": {"b"}}
    targets = {"u1": {"b"}, "u2": {"a"}}
    for invalid in [["a"], ["z"], ["b", "b"]]:
        with pytest.raises(ValueError):
            evaluate_ranking({"u1": invalid, "u2": []}, targets, train)
    with pytest.raises(ValueError, match="user sets"):
        evaluate_ranking({"u1": []}, targets, train)
    with pytest.raises(ValueError, match="overlap"):
        evaluate_ranking({"u1": [], "u2": []}, train, train)
    with pytest.raises(ValueError, match="overlap"):
        evaluate_ranking({"u1": [], "u2": []}, targets, train, split="test", validation=train)
    with pytest.raises(ValueError):
        evaluate_ranking({"u1": [], "u2": []}, targets, train, ks=(5, 5))


def test_undefined_metrics_are_null_with_denominators() -> None:
    train = {"u1": {"a"}, "u2": {"b"}}
    recs = {"u1": [], "u2": []}
    result = evaluate_ranking(recs, {"u1": {"b"}, "u2": {"a"}}, train)
    metrics = result["at_k"]["5"]
    assert metrics["precision"] == 0
    assert metrics["catalog_coverage"] == 0
    assert metrics["gini"] is None
    assert metrics["arp"] is None
    assert metrics["novelty"] is None
    assert metrics["ild"] is None
    assert metrics["ild_users"] == 0
    result = evaluate_ranking(recs, {"u1": {"z"}, "u2": set()}, train)
    assert result["users_eligible"] == 0
    assert result["at_k"]["5"]["precision"] is None
    assert result["at_k"]["5"]["full_list_rate"] is None


def test_gini_and_proxy_rmse_hand_examples_and_validation() -> None:
    assert gini_index([2, 1, 1, 0]) == 0.375
    assert gini_index([1, 1, 1]) == 0
    assert gini_index([4, 0, 0, 0]) == 0.75
    assert gini_index([0, 0]) is None
    assert proxy_rmse([1, 3, 5], [2, 3, 4]) == pytest.approx(sqrt(2 / 3))
    assert proxy_rmse([5], [6]) == 1  # No implicit clipping of predictions.
    for values in [[], [-1], [1.5]]:
        with pytest.raises(ValueError):
            gini_index(values)
    for actual, predicted in [([], []), ([1], []), ([0], [1]), ([1], [float("nan")])]:
        with pytest.raises(ValueError):
            proxy_rmse(actual, predicted)


def test_toy_cli_is_reproducible_hashed_and_never_overwrites(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    runs = [tmp_path / "first", tmp_path / "second"]
    for run in runs:
        subprocess.run(
            [
                sys.executable,
                "-B",
                str(root / "scripts/evaluate.py"),
                "--toy-check",
                "--output-dir",
                str(run),
            ],
            cwd=root,
            check=True,
            capture_output=True,
        )
        metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
        assert metrics["step"] == 6
        assert metrics["all_hand_checks_passed"]
        for name, expected in metrics["output_sha256"].items():
            assert hashlib.sha256((run / name).read_bytes()).hexdigest() == expected
        for name, expected in metrics["code_sha256"].items():
            assert hashlib.sha256((run / "code" / name).read_bytes()).hexdigest() == expected
    for name in ["toy_inputs.json", "toy_results.json", "hand_checks.json"]:
        assert (runs[0] / name).read_bytes() == (runs[1] / name).read_bytes()
    before = (runs[0] / "metrics.json").read_bytes()
    attempt = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts/evaluate.py"),
            "--toy-check",
            "--output-dir",
            str(runs[0]),
        ],
        cwd=root,
        capture_output=True,
    )
    assert attempt.returncode != 0
    assert (runs[0] / "metrics.json").read_bytes() == before
