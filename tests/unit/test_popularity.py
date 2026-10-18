from pathlib import Path

import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.popularity import PopularityRecommender


def test_popularity_orders_items_and_excludes_seen_items() -> None:
    model = PopularityRecommender().fit(
        [
            Interaction("u1", "a", 2),
            Interaction("u2", "b", 5),
            Interaction("u3", "a", 4),
        ]
    )

    recommendations = model.recommend("u1", k=2, seen_item_ids={"a"})

    assert [item.item_id for item in recommendations] == ["b"]
    assert recommendations[0].reason == "popular_with_all_users"


def test_distinct_listeners_ties_and_roundtrip(tmp_path: Path) -> None:
    model = PopularityRecommender().fit(
        [
            Interaction("u1", "a", 999),
            Interaction("u1", "a", 200),
            Interaction("u1", "b", 1),
            Interaction("u2", "b", 1),
            Interaction("u2", "c", 1),
        ]
    )
    assert model.predict("u1", "a") == 1
    assert model.predict("u1", "b") == 2
    assert [r.item_id for r in model.recommend("u", 10, set())] == ["b", "a", "c"]
    path = tmp_path / "model.json"
    model.save(path)
    assert model.recommend("u", 10, {"b"}) == PopularityRecommender.load(path).recommend(
        "u", 10, {"b"}
    )
    with pytest.raises(FileExistsError):
        model.save(path)
