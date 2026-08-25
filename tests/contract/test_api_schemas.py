import pytest
from pydantic import ValidationError

from musicrec.api.schemas import RecommendRequest


def test_request_requires_user_or_history() -> None:
    with pytest.raises(ValidationError):
        RecommendRequest()


def test_request_accepts_a_temporary_history() -> None:
    request = RecommendRequest(history=[{"item_id": "artist_1", "listening_count": 1}])
    assert request.k == 10
