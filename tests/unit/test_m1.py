"""Hand-computed M1 features, greedy ablations, export and validation selection checks."""

from pathlib import Path

import numpy as np
import pytest

from musicrec.data.contracts import Interaction
from musicrec.evaluation.m1 import select_full_variant, within_drop
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.m1 import CandidatePool, M1Recommender, rerank_candidates


class FrozenBase(Recommender):
    """A deterministic base that must never be fitted by the reranker."""

    def fit(self, interactions):
        raise AssertionError("M1 must not fit its base")

    def predict(self, user_id, item_id):
        return {"a": 10.0, "b": 9.0, "c": 8.0, "d": 6.0}[item_id]

    def recommend(self, user_id, k, seen_item_ids):
        return [
            Recommendation(i, self.predict(user_id, i), "frozen_base")
            for i in ["a", "b", "c", "d"]
            if i not in seen_item_ids
        ][:k]


def train_rows():
    return [
        Interaction("u1", "a", 1),
        Interaction("u1", "b", 9),
        Interaction("u2", "a", 999),
        Interaction("u2", "b", 3),
        Interaction("u3", "c", 1),
        Interaction("u4", "d", 1),
    ]


def test_train_features_identity_masking_and_prefix():
    model = M1Recommender(FrozenBase(), candidate_size=4).fit(train_rows())
    pool = model.prepare_candidates("new", set())
    np.testing.assert_allclose(pool.relevance, [1, 0.75, 0.5, 0])
    np.testing.assert_allclose(
        pool.popularity, [1, 1, np.log(2) / np.log(3), np.log(2) / np.log(3)]
    )
    np.testing.assert_allclose(
        pool.similarity, [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    )
    assert model.recommend("new", 4, set()) == pool.recommendations
    assert [r.item_id for r in model.recommend("u1", 4, {"d"})] == ["c"]
    # After a, b has utility -0.125; c has 0.25. The third pick is d (0 > -0.125).
    diverse = rerank_candidates(pool, 4, 0.5, 0)
    assert [r.item_id for r in diverse] == ["a", "c", "d", "b"]
    assert [r.score for r in diverse] == [10, 8, 6, 9]
    assert rerank_candidates(pool, 2, 0.5, 0) == diverse[:2]
    assert model.predict("new", "b") == 9
    # Count magnitude cannot alter any of the train-only reranker statistics.
    changed = M1Recommender(FrozenBase(), candidate_size=4).fit(
        [Interaction(r.user_id, r.item_id, 1) for r in train_rows()]
    )
    np.testing.assert_array_equal(
        changed.prepare_candidates("new", set()).similarity, pool.similarity
    )
    np.testing.assert_array_equal(
        changed.prepare_candidates("new", set()).popularity, pool.popularity
    )


def test_popularity_ablation_flat_empty_and_ties():
    recs = [Recommendation(i, 4, "flat") for i in ["a", "b", "c"]]
    pool = CandidatePool(recs, np.ones(3), np.array([1, 0.1, 0.1]), np.eye(3))
    assert [r.item_id for r in rerank_candidates(pool, 3, 1, 0.5)] == ["b", "c", "a"]
    assert rerank_candidates(pool, 3, 1, 0) == recs
    empty = CandidatePool([], np.array([]), np.array([]), np.empty((0, 0)))
    assert rerank_candidates(empty, 3, 0.5, 0.5) == []
    model = M1Recommender(FrozenBase()).fit(train_rows())
    assert model.prepare_candidates("u1", {"c", "d"}).recommendations == []
    pool_one = model.prepare_candidates("new", {"b", "c", "d"})
    np.testing.assert_array_equal(pool_one.relevance, [1])


@pytest.mark.parametrize(
    "kwargs", [{"lambda_weight": -1}, {"beta": float("nan")}, {"candidate_size": 0}]
)
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        M1Recommender(FrozenBase(), **kwargs)


def test_reject_bad_base_and_bad_context(tmp_path: Path):
    model = M1Recommender(FrozenBase(), candidate_size=4, lambda_weight=0.5, beta=0.25)
    with pytest.raises(RuntimeError):
        model.recommend("new", 2, set())
    model.fit(train_rows())
    for k in [0, 5, True]:
        with pytest.raises(ValueError):
            model.recommend("new", k, set())
    with pytest.raises(ValueError):
        model.fit(train_rows() * 2)
    directory = tmp_path / "model"
    model.save(directory)
    restored = M1Recommender.load(directory, base=FrozenBase())
    assert restored.recommend("new", 4, set()) == model.recommend("new", 4, set())
    assert restored.recommend("u1", 4, set()) == model.recommend("u1", 4, set())
    with pytest.raises(FileExistsError):
        model.save(directory)
    with (directory / "binary.npz").open("ab") as handle:
        handle.write(b"corrupt")
    with pytest.raises(ValueError, match="checksum"):
        M1Recommender.load(directory, base=FrozenBase())
    model.base.recommend = lambda *args: [Recommendation("unknown", 1, "invalid")]
    with pytest.raises(ValueError, match="catalog"):
        model.prepare_candidates("new", set())


def test_selection_bound_full_only_and_no_feasible():
    assert within_drop(0.19, 0.2)
    assert not within_drop(0.1899999, 0.2)
    assert within_drop(0, 0)
    with pytest.raises(ValueError):
        within_drop(float("nan"), 0.2)
    rows = [
        {"lambda": 1, "beta": 0.5, "ndcg": 0.2, "arp": 1, "ild": 1},
        {"lambda": 0.5, "beta": 0, "ndcg": 0.2, "arp": 1, "ild": 1},
        {"lambda": 0.5, "beta": 0.5, "ndcg": 0.189, "arp": 1, "ild": 1},
        {"lambda": 0.75, "beta": 0.25, "ndcg": 0.19, "arp": 20, "ild": 0.9},
        {"lambda": 0.75, "beta": 0.1, "ndcg": 0.195, "arp": 20, "ild": 0.8},
    ]
    assert select_full_variant(rows, 0.2) == rows[3]
    assert select_full_variant(rows[:3], 0.2) is None
