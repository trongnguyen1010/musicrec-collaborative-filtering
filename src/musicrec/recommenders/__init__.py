"""Recommendation models with a shared inference contract."""

from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.popularity import PopularityRecommender

__all__ = ["PopularityRecommender", "Recommendation", "Recommender"]
