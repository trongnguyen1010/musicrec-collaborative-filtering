"""Reserved implementation module for Item-based Collaborative Filtering."""

from typing import Iterable

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class ItemCFRecommender(Recommender):
    """Implement sparse item-neighbour scoring in a future change."""

    def fit(self, interactions: Iterable[Interaction]) -> "ItemCFRecommender":
        del interactions
        raise NotImplementedError("Item-CF is not implemented in the scaffold")

    def predict(self, user_id: str, item_id: str) -> float:
        del user_id, item_id
        raise NotImplementedError("Item-CF is not implemented in the scaffold")

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        del user_id, k, seen_item_ids
        raise NotImplementedError("Item-CF is not implemented in the scaffold")
