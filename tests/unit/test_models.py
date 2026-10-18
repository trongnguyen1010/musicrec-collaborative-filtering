from pathlib import Path

import numpy as np
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.models import MatrixModel, make_model, top_indices

ROWS = [
    Interaction(u, i, c)
    for u, i, c in [
        ("u1", "a", 1),
        ("u1", "b", 2),
        ("u2", "a", 3),
        ("u2", "c", 5),
        ("u3", "b", 8),
        ("u3", "c", 13),
        ("u3", "d", 21),
    ]
]


@pytest.mark.parametrize("kind", ["user_cf", "item_cf", "pure_svd", "svd", "bpr", "random"])
def test_models_mask_persist_and_reproduce(kind: str, tmp_path: Path) -> None:
    params = {
        "factors": 2,
        "epochs": 3,
        "neighbors": 2,
        "shrinkage": 0,
        "seed": 42,
        "batch_size": 3,
    }
    model = make_model(kind, params).fit(ROWS)
    recs = model.recommend("u1", 10, {"a", "b"})
    assert len(recs) == 2 and {r.item_id for r in recs} == {"c", "d"}
    assert np.isfinite([r.score for r in recs]).all()
    model.save(tmp_path / "model.npz")
    loaded = MatrixModel.load(tmp_path / "model.npz")
    assert loaded.recommend("u1", 10, {"a", "b"}) == recs
    repeated = make_model(kind, params).fit(ROWS)
    assert repeated.recommend("u1", 10, {"a", "b"}) == recs


def test_stable_top_k_boundary_and_exhausted_catalog() -> None:
    assert top_indices(np.array([3.0, 2.0, 2.0, 2.0, 1.0]), 3).tolist() == [0, 1, 2]
    assert top_indices(np.array([-np.inf, -np.inf]), 5).tolist() == []


def test_item_cf_cosine_and_new_profile() -> None:
    model = make_model("item_cf", {"neighbors": 3, "shrinkage": 0, "min_common": 1}).fit(ROWS)
    vectors = model.matrix.T.toarray()
    expected = float(
        vectors[0] @ vectors[1] / (np.linalg.norm(vectors[0]) * np.linalg.norm(vectors[1]))
    )
    assert model.neighbors[0, 1] == pytest.approx(expected)
    raw = {"a": 1.0, "b": 2.0}
    assert np.allclose(model.from_profile(raw), model.scores("u1"))


def test_bpr_rejects_no_available_negatives() -> None:
    with pytest.raises(ValueError, match="unobserved"):
        make_model("bpr", {"factors": 2}).fit([Interaction("u", "a", 1)])


def test_bpr_uses_binary_positives_and_learns_pairwise_order() -> None:
    rows = [Interaction("u1", "a", 1), Interaction("u2", "b", 1)]
    params = {
        "factors": 4,
        "epochs": 60,
        "batch_size": 1,
        "learning_rate": 0.05,
        "regularization": 0.001,
        "seed": 42,
    }
    model = make_model("bpr", params).fit(rows)
    other = make_model("bpr", params).fit([Interaction("u1", "a", 1000), Interaction("u2", "b", 5)])
    assert np.array_equal(model.user_factors, other.user_factors)
    assert np.array_equal(model.item_factors, other.item_factors)
    assert model.predict("u1", "a") > model.predict("u1", "b")
    assert model.predict("u2", "b") > model.predict("u2", "a")


def test_user_cf_hand_example_with_constant_observed_proxies() -> None:
    rows = [
        Interaction(u, i, 1)
        for u, items in [("u1", ["a", "b"]), ("u2", ["a", "c"]), ("u3", ["b", "d"])]
        for i in items
    ]
    model = make_model("user_cf", {"neighbors": 2, "shrinkage": 0, "min_common": 1}).fit(rows)
    recs = model.recommend("u1", 2, {"a", "b"})
    assert [r.item_id for r in recs] == ["c", "d"]
    assert [r.score for r in recs] == pytest.approx([1.0, 1.0])
