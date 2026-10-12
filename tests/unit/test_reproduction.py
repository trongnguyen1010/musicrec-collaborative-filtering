"""Hand-derived metrics, train-only graph kernels and data boundary regressions."""

import math
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

from musicrec.data.contracts import Interaction
from musicrec.evaluation.ranking import hit_at_k, mrr_at_k, ndcg_at_k, precision_at_k
from musicrec.recommenders.diffusion import DiffusionRecommender, dhc_features, normalize_edges


def test_metric_hand_examples() -> None:
    ranked, relevant = ["miss", "a", "b"], {"a", "b", "c"}
    assert precision_at_k(["a"], relevant, 10) == 0.1
    assert mrr_at_k(ranked, relevant, 3) == 0.5
    assert hit_at_k(ranked, relevant, 1) == 0
    expected = (1 / math.log2(3) + 1 / math.log2(4)) / (1 + 1 / math.log2(3) + 1 / math.log2(4))
    assert ndcg_at_k(ranked, relevant, 3) == pytest.approx(expected)
    assert ndcg_at_k([], set(), 10) == 0
    assert mrr_at_k([], relevant, 10) == 0
    assert ndcg_at_k(["a", "a"], {"a"}, 2) == 1
    for function in [precision_at_k, mrr_at_k, ndcg_at_k, hit_at_k]:
        with pytest.raises(ValueError):
            function([], relevant, 0)


@pytest.mark.parametrize("weight", [float("nan"), float("inf"), -1, 0])
def test_reject_invalid_listening_count(weight: float) -> None:
    with pytest.raises(ValueError):
        Interaction("u", "i", weight)


def test_dhc_path_converges_and_isolated_node_stays_zero() -> None:
    graph = sparse.csr_matrix(np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]]))
    np.testing.assert_array_equal(dhc_features(graph), [[1, 1], [2, 1], [1, 1], [0, 0]])


def test_normalization_includes_zeros_and_constant_vectors() -> None:
    weights = sparse.csr_matrix(np.array([[2.0, 4.0, 0.0], [0.0, 0.0, 0.0], [2.0, 2.0, 2.0]]))
    normalized = normalize_edges(weights, axis=1).toarray()
    np.testing.assert_allclose(normalized, [[1 / 3, 2 / 3, 0], [0, 0, 0], [1 / 3, 1 / 3, 1 / 3]])


def test_diffusion_train_only_and_unseen_recommendations() -> None:
    model = DiffusionRecommender("aiprobs", ["[PAD]", "u", "cold"], ["[PAD]", "a", "b", "c"])
    model.fit([Interaction("u", "a", 5), Interaction("u", "b", 20)])
    assert model.predict("cold", "a") == 0
    assert model.predict("u", "c") == 0
    assert [x.item_id for x in model.recommend("u", 3, {"a", "b"})] == ["c"]
    with pytest.raises(KeyError):
        model.predict("unknown", "a")


def test_author_dense_reference_when_downloaded() -> None:
    if not Path("outputs/research/download_manifest.json").exists():
        pytest.skip("Pinned author inputs are downloaded separately")
    from musicrec.research.reference import verify_tiny_reference

    assert verify_tiny_reference()["status"] == "passed"
