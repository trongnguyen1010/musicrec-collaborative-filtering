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
