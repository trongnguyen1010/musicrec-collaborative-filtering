"""Read-only inference adapter for genuine RecBole BPR factors."""

from collections.abc import Iterable
from pathlib import Path

import numpy as np
import torch

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.diffusion import FloatArray, IntArray


class BPRRecommender(Recommender):
    """Use externally trained factors after checking train/catalog compatibility."""

    def __init__(self, artifact: Path):
        with np.load(artifact, allow_pickle=False) as data:
            self.user_ids = data["users"].tolist()
            self.item_ids = data["items"].tolist()
            self.user_factors = torch.from_numpy(data["user_factors"].copy())
            self.item_factors = torch.from_numpy(data["item_factors"].copy())
        self.user_index = {value: i for i, value in enumerate(self.user_ids)}
        self.item_index = {value: i for i, value in enumerate(self.item_ids)}
        if (
            not torch.isfinite(self.user_factors).all()
            or not torch.isfinite(self.item_factors).all()
        ):
            raise ValueError("Nonfinite BPR factors")

    def fit(self, interactions: Iterable[Interaction]) -> "BPRRecommender":
        """Validate IDs; fitting itself is delegated to research_legacy.py/RecBole."""
        for interaction in interactions:
            if (
                interaction.user_id not in self.user_index
                or interaction.item_id not in self.item_index
            ):
                raise ValueError("Training ID absent from BPR artifact catalog")
        return self

    def score_batch(self, users: IntArray) -> FloatArray:
        """Keep native float32 matmul before returning scores to the ranker."""
        with torch.no_grad():
            scores = self.user_factors[torch.from_numpy(users)] @ self.item_factors.T
        return np.asarray(scores.numpy(), dtype=np.float64)

    def predict(self, user_id: str, item_id: str) -> float:
        return float(
            self.score_batch(np.asarray([self.user_index[user_id]], dtype=np.int64))[
                0, self.item_index[item_id]
            ]
        )

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        if k <= 0:
            raise ValueError("k must be greater than zero")
        scores = self.score_batch(np.asarray([self.user_index[user_id]], dtype=np.int64))[0]
        eligible = [
            i
            for i, item in enumerate(self.item_ids)
            if item != "[PAD]" and item not in seen_item_ids
        ]
        ranked = sorted(eligible, key=lambda i: (-float(scores[i]), self.item_ids[i]))[:k]
        return [Recommendation(self.item_ids[i], float(scores[i]), "recbole_bpr") for i in ranked]
