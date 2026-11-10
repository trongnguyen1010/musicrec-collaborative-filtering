"""Top-N 'sum' aggregation of UserCF/ItemCF (E7) against hand values and a dense reference."""

from math import log2, sqrt
from pathlib import Path

import numpy as np
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.item_cf import ItemCFRecommender
from musicrec.recommenders.user_cf import UserCFRecommender

PAIRS = [("1", "1"), ("1", "2"), ("2", "1"), ("2", "2"), ("2", "3"), ("3", "1"), ("3", "2")]
PAIRS += [("3", "4"), ("4", "5")]


def rows(counts: dict[tuple[str, str], float] | None = None) -> list[Interaction]:
    return [Interaction(u, i, (counts or {}).get((u, i), 3.0), 3) for u, i in PAIRS]


def test_user_cf_binary_sum_hand_example() -> None:
    model = UserCFRecommender(aggregation="sum", representation="binary").fit(rows())
    cosine = 2 / sqrt(6)
    assert model.predict("1", "3") == pytest.approx(cosine)
    assert model.predict("1", "4") == pytest.approx(cosine)
    assert model.predict("1", "5") == 0  # No neighbor listened: score 0, not a mean.
    recs = model.recommend("1", 10, set())
    assert [r.item_id for r in recs] == ["3", "4", "5"]  # Equal scores keep numeric order.
    assert [r.reason for r in recs] == ["user_cf", "user_cf", "user_cf_no_support"]
    cold = model.recommend("unknown", 3, set())
    assert all(r.score == 0 and r.reason == "user_cf_no_support" for r in cold)


def test_item_cf_binary_sum_hand_example() -> None:
    model = ItemCFRecommender(aggregation="sum", representation="binary").fit(rows())
    assert model.predict("1", "3") == pytest.approx(2 / sqrt(3))
    assert model.predict("1", "4") == pytest.approx(2 / sqrt(3))
    assert model.predict("1", "5") == 0
    recs = model.recommend("1", 10, set())
    assert [r.reason for r in recs] == ["item_cf", "item_cf", "item_cf_no_support"]
    with pytest.raises(ValueError):
        model.score_profile([Interaction("9", "1", 1.0, 3)])


def test_log_count_uses_log2_one_plus_count_and_needs_no_proxy() -> None:
    counts = {("2", "3"): 7.0, ("3", "4"): 1.0}
    data = [Interaction(r.user_id, r.item_id, r.listening_count) for r in rows(counts)]
    model = UserCFRecommender(aggregation="sum", representation="log_count").fit(data)
    # Row norms on log2(1 + 3) = 2, log2(8) = 3, log2(2) = 1.
    sim_12 = (2 * 2 + 2 * 2) / (sqrt(8) * sqrt(4 + 4 + 9))
    assert model.predict("1", "3") == pytest.approx(sim_12 * log2(8))
    with pytest.raises(ValueError):
        UserCFRecommender().fit(data)  # The default mean mode still needs proxy scores.


def dense_reference(matrix: np.ndarray, neighbors: int, shrinkage: float) -> np.ndarray:
    """Global top-L positive cosine neighbors of each row (ties by lower index)."""
    norms = np.sqrt((matrix**2).sum(axis=1))
    sim = np.clip(matrix @ matrix.T / np.outer(norms, norms), 0, 1)
    if shrinkage:
        common = (matrix > 0).astype(float) @ (matrix > 0).astype(float).T
        sim = sim * common / (common + shrinkage)
    np.fill_diagonal(sim, 0)
    weights = np.zeros_like(sim)
    for row in range(len(sim)):
        order = np.lexsort((np.arange(len(sim)), -np.round(sim[row], 12)))
        kept = [j for j in order[:neighbors] if sim[row, j] > 0]
        weights[row, kept] = sim[row, kept]
    return weights


@pytest.mark.parametrize("representation", ["binary", "log_count"])
@pytest.mark.parametrize("shrinkage", [0.0, 10.0])
def test_sum_scores_match_dense_reference(representation: str, shrinkage: float) -> None:
    rng = np.random.default_rng(7)
    data = []
    for user in range(1, 26):
        for item in rng.choice(np.arange(1, 31), size=int(rng.integers(2, 9)), replace=False):
            data.append(Interaction(str(user), str(item), float(rng.integers(1, 200))))
    users = sorted({r.user_id for r in data}, key=int)
    items = sorted({r.item_id for r in data}, key=int)
    x = np.zeros((len(users), len(items)))
    for r in data:
        value = 1.0 if representation == "binary" else log2(1 + r.listening_count)
        x[users.index(r.user_id), items.index(r.item_id)] = value
    user_model = UserCFRecommender(3, shrinkage, "sum", representation).fit(data)
    item_model = ItemCFRecommender(4, shrinkage, "sum", representation).fit(data)
    user_scores = dense_reference(x, 3, shrinkage) @ x
    item_scores = x @ dense_reference(x.T, 4, shrinkage).T
    for index, user in enumerate(users):
        got_u, _ = user_model._score_catalog(user)
        got_i, _ = item_model._score_catalog(user)
        np.testing.assert_allclose(got_u, user_scores[index], atol=1e-12)
        np.testing.assert_allclose(got_i, item_scores[index], atol=1e-12)


def test_sum_mode_roundtrip_and_default_state_unchanged(tmp_path: Path) -> None:
    data = rows()
    for cls in [UserCFRecommender, ItemCFRecommender]:
        model = cls(2, 10.0, "sum", "log_count").fit(data)
        model.save(tmp_path / cls.__name__)
        restored = cls.load(tmp_path / cls.__name__)
        assert (restored.aggregation, restored.representation) == ("sum", "log_count")
        for user in ["1", "2", "3", "4", "unknown"]:
            assert restored.recommend(user, 5, set()) == model.recommend(user, 5, set())
        default = cls().fit(data)
        default.save(tmp_path / f"{cls.__name__}_default")
        state = (tmp_path / f"{cls.__name__}_default/state.json").read_text(encoding="utf-8")
        assert "aggregation" not in state and "representation" not in state


def test_invalid_modes_rejected() -> None:
    with pytest.raises(ValueError):
        UserCFRecommender(aggregation="median")
    with pytest.raises(ValueError):
        ItemCFRecommender(aggregation="sum", representation="proxy")
    with pytest.raises(ValueError):
        UserCFRecommender(aggregation="mean", representation="binary")
