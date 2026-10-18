import pytest
from pydantic import ValidationError

from musicrec.api.schemas import RecommendRequest


def test_guest_request_is_allowed_for_popularity_fallback() -> None:
    assert RecommendRequest().history is None
    assert RecommendRequest().user_id is None


@pytest.mark.parametrize("count", [float("nan"), float("inf"), -1, 0])
def test_history_requires_finite_positive_counts(count: float) -> None:
    with pytest.raises(ValidationError):
        RecommendRequest(history=[{"item_id": "a", "listening_count": count}])


def test_request_accepts_a_temporary_history() -> None:
    request = RecommendRequest(history=[{"item_id": "artist_1", "listening_count": 1}])
    assert request.k == 10
