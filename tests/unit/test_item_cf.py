"""Hand examples, sparse orientation and persistence checks for Step 10 ItemCF."""

from math import sqrt
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from scipy.sparse import load_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.item_cf import ItemCFRecommender


def sample_rows() -> list[Interaction]:
    return [
        Interaction(user, item, 100, score)
        for user, item, score in [
            ("1", "1", 3),
            ("1", "2", 5),
            ("2", "1", 1),
            ("2", "2", 3),
            ("2", "3", 5),
            ("3", "1", 5),
            ("3", "2", 3),
            ("3", "4", 1),
            ("4", "5", 2),
        ]
    ]


def test_hand_cosines_weighted_mean_fallback_masks_and_count_independence(tmp_path: Path) -> None:
    model = ItemCFRecommender().fit(sample_rows())
    a, b = 1 / sqrt(35), 3 / sqrt(43)
    assert model.predict("1", "3") == pytest.approx((3 * a + 5 * b) / (a + b))
    a, b = 5 / sqrt(35), 3 / sqrt(43)
    assert model.predict("1", "4") == pytest.approx((3 * a + 5 * b) / (a + b))
    assert model.predict("1", "5") == 4
    full = model.recommend("1", 20, set())
    assert [item.item_id for item in full] == ["3", "5", "4"]
    assert [item.reason for item in full] == ["item_cf", "item_cf_user_mean_fallback", "item_cf"]
    assert model.recommend("1", 1, set()) == full[:1]
    assert model.recommend("1", 20, {"3", "missing"}) == full[1:]
    assert model.recommend("1", 20, {"1", "2", "3", "4", "5"}) == []
    for item in full:
        assert model.predict("1", item.item_id) == item.score
    changed = [
        Interaction(row.user_id, row.item_id, 99999, row.proxy_score)
        for row in reversed(sample_rows())
    ]
    assert ItemCFRecommender().fit(changed).recommend("1", 20, set()) == full
    cold = model.recommend("unknown", 20, {"1"})
    assert [item.item_id for item in cold] == ["2", "3", "4", "5"]
    assert all(item.score == pytest.approx(28 / 9) for item in cold)
    assert all(item.reason == "item_cf_global_mean_cold_start" for item in cold)
    model.save(tmp_path / "model")
    weights = load_npz(tmp_path / "model/neighbors.npz").toarray()
    assert weights[2, 0] == pytest.approx(1 / sqrt(35))
    assert weights[2, 1] == pytest.approx(3 / sqrt(43))
    assert not np.diag(weights).any()
    shrunk = ItemCFRecommender(shrinkage=10).fit(sample_rows())
    shrunk.save(tmp_path / "shrunk")
    shrunk_weights = load_npz(tmp_path / "shrunk/neighbors.npz").toarray()
    assert shrunk_weights[0, 1] == pytest.approx(33 / sqrt(35 * 43) * 3 / 13)
    assert shrunk_weights[2, 1] == pytest.approx(weights[2, 1] / 11)


def test_global_target_neighbors_then_history_intersection_not_source_expansion() -> None:
    rows = sample_rows() + [Interaction("5", "1", 100, 1), Interaction("5", "5", 100, 5)]
    model = ItemCFRecommender(neighbors=1).fit(rows)
    # Target 3 globally chooses item 2. User 5 cannot replace it with item 1.
    assert model.predict("5", "3") == 3
    rec = next(item for item in model.recommend("5", 20, set()) if item.item_id == "3")
    assert rec.reason == "item_cf_user_mean_fallback"
    assert model.predict("1", "3") == 5
    assert model.predict("1", "4") == pytest.approx(3)


def test_numeric_ties_block_boundary_and_reload_without_fit(tmp_path: Path) -> None:
    rows = [Interaction("1", str(i), 100, 3) for i in range(1, 260)]
    model = ItemCFRecommender(neighbors=1).fit(rows)
    model.save(tmp_path / "model")
    weights = load_npz(tmp_path / "model/neighbors.npz")
    # Identical cosine at both sides of the 256-item block boundary uses numeric IDs.
    assert weights.getrow(0).indices.tolist() == [1]
    assert weights.getrow(1).indices.tolist() == [0]
    assert weights.getrow(258).indices.tolist() == [0]
    assert weights[258, 258] == 0
    with patch.object(ItemCFRecommender, "fit", side_effect=AssertionError("load must not fit")):
        restored = ItemCFRecommender.load(tmp_path / "model")
    for user in ["1", "unknown"]:
        assert restored.recommend(user, 20, set()) == model.recommend(user, 20, set())
    assert [item.item_id for item in restored.recommend("unknown", 3, set())] == ["1", "2", "3"]
    with pytest.raises(FileExistsError):
        model.save(tmp_path / "model")
    with (tmp_path / "model/neighbors.npz").open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        ItemCFRecommender.load(tmp_path / "model")


def test_equal_cosines_round_before_neighbor_selection_and_empty_neighborhoods(
    tmp_path: Path,
) -> None:
    # Exact 0.15 cosines with different column norms must tie numerically.
    rows = [Interaction(str(u), "1", 100, 5) for u in range(1, 41)]
    rows += [Interaction(str(u), "2", 100, 5) for u in [*range(1, 7), *range(41, 75)]]
    rows += [Interaction(str(u), "10", 100, 2) for u in [*range(1, 4), *range(75, 82)]]
    model = ItemCFRecommender(neighbors=1).fit(rows)
    model.save(tmp_path / "model")
    weights = load_npz(tmp_path / "model/neighbors.npz")
    assert weights.getrow(0).indices.tolist() == [1]
    result = model.recommend("75", 2, set())
    assert ItemCFRecommender(neighbors=1).fit(reversed(rows)).recommend("75", 2, set()) == result
    isolated = ItemCFRecommender().fit(
        [Interaction("1", "1", 100, 4), Interaction("2", "2", 100, 2)]
    )
    assert isolated.recommend("1", 1, set())[0].reason == "item_cf_user_mean_fallback"
    assert isolated.predict("1", "2") == 4


def test_item_cf_rejects_invalid_or_missing_train_state() -> None:
    for value in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            ItemCFRecommender(neighbors=value)
    for value in [-1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            ItemCFRecommender(shrinkage=value)
    for rows in [[], [Interaction("1", "1", 100)], [sample_rows()[0]] * 2]:
        with pytest.raises(ValueError):
            ItemCFRecommender().fit(rows)
    with pytest.raises(RuntimeError):
        ItemCFRecommender().predict("1", "1")
    model = ItemCFRecommender().fit(sample_rows())
    for k in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            model.recommend("1", k, set())
    with pytest.raises(ValueError, match="user_id"):
        model.predict("", "1")
    with pytest.raises(ValueError, match="outside"):
        model.predict("1", "99")
