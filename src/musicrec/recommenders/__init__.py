"""Các mô hình khuyến nghị dùng chung một giao diện suy luận."""

from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.popularity import PopularityRecommender

__all__ = ["PopularityRecommender", "Recommendation", "Recommender"]
