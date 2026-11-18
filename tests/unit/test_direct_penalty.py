"""Hand-computed min-max scale, identity, flat range and frozen-range checks for the control."""

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from musicrec.data.contracts import Interaction
from musicrec.recommenders.direct_penalty import DirectPenaltyRecommender
from musicrec.recommenders.implicit_als import ImplicitALSRecommender


def toy(item_scores: list[list[float]]) -> ImplicitALSRecommender:
    """User u scores item i exactly item_scores[u][i] via one latent dimension per user."""
    scores = np.array(item_scores, dtype=np.float64)
    model = ImplicitALSRecommender(latent_factors=scores.shape[0])
    model._users = [str(u) for u in range(1, scores.shape[0] + 1)]
    model._items = [str(i) for i in range(1, scores.shape[1] + 1)]
    model._user_factors = np.eye(scores.shape[0], dtype=np.float32)
    model._item_factors = scores.T.astype(np.float32)
    # Train: user 1 has item 1; user 2 has items 2 and 4.
    model._confidence = csr_matrix(
        (np.full(3, 2.0, dtype=np.float32), ([0, 1, 1], [0, 1, 3])), shape=scores.shape
    )
    model._prepare()
    return model


def rows() -> list[Interaction]:
    return [Interaction(u, i, 1) for u, i in [("1", "1"), ("2", "2"), ("2", "4"), ("1", "3")]]


def test_identity_hand_penalty_and_frozen_range() -> None:
    base = toy([[9.0, 4.0, 2.0, 1.0], [0.0, 5.0, 3.0, 3.0]])
    # User 1 also has item 3 in train for the control; keep the checkpoint mask aligned.
    base._confidence = csr_matrix(
        (np.full(4, 2.0, dtype=np.float32), ([0, 0, 1, 1], [0, 2, 1, 3])), shape=(2, 4)
    )
    model = DirectPenaltyRecommender(base).fit(rows())
    assert model.recommend("1", 4, set()) == base.recommend("1", 4, set())
    # Listeners: items 1-4 have 1 train listener each, so p(i)=1 for every item.
    np.testing.assert_allclose(model.popularity, [1, 1, 1, 1])
    np.testing.assert_allclose(model.ranges, [[1, 4], [0, 3]])
    model.beta = 0.5
    # User 1 unseen items 2 and 4: normalized (4-1)/3=1 and 0, minus 0.5 each.
    assert [(r.item_id, r.score) for r in model.recommend("1", 4, set())] == [
        ("2", 0.5),
        ("4", -0.5),
    ]
    before = model.predict("1", "4")
    assert [r.item_id for r in model.recommend("1", 4, {"2"})] == ["4"]
    assert model.predict("1", "4") == before


def test_flat_range_uses_ones_and_ties_keep_mapping_order() -> None:
    base = toy([[0.0, 1.0, 1.0, 1.0], [0.0, 0.0, 0.0, 0.0], [5.0, 5.0, 5.0, 5.0]])
    pairs = [("1", "1"), ("1", "4"), ("2", "2"), ("2", "4"), ("3", "3")]
    train = [Interaction(u, i, 1) for u, i in pairs]
    base._confidence = csr_matrix(
        (np.full(5, 2.0, dtype=np.float32), ([0, 0, 1, 1, 2], [0, 3, 1, 3, 2])), shape=(3, 4)
    )
    model = DirectPenaltyRecommender(base, beta=0.1).fit(train)
    # Item 4 has two listeners, items 1-3 one each: p = log 2/log 3 for items 1-3.
    np.testing.assert_allclose(model.popularity, [np.log(2) / np.log(3)] * 3 + [1])
    # User 2 has a flat unseen range: all ones, then ties broken by mapping order.
    flat = model.recommend("2", 4, set())
    assert [r.item_id for r in flat] == ["1", "3"]
    assert flat[0].score == pytest.approx(1 - 0.1 * np.log(2) / np.log(3))


def test_invalid_inputs() -> None:
    base = toy([[1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0]])
    with pytest.raises(ValueError):
        DirectPenaltyRecommender(base, beta=-1)
    with pytest.raises(RuntimeError):
        DirectPenaltyRecommender(base).recommend("1", 2, set())
    with pytest.raises(ValueError, match="checkpoint"):
        DirectPenaltyRecommender(base).fit(rows()[:2])
