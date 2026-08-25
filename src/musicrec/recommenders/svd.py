"""Reserved implementation module for matrix factorization SVD."""

from typing import Iterable

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class SVDRecommender(Recommender):
    """Implement factorization and deterministic model persistence in a future change."""

    def fit(self, interactions: Iterable[Interaction]) -> "SVDRecommender":
        del interactions
        raise NotImplementedError("SVD is not implemented in the scaffold")

    def predict(self, user_id: str, item_id: str) -> float:
        del user_id, item_id
        raise NotImplementedError("SVD is not implemented in the scaffold")

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        del user_id, k, seen_item_ids
        raise NotImplementedError("SVD is not implemented in the scaffold")
