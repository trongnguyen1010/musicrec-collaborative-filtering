"""HTTP contract of the demo API over a tiny release."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from musicrec.api.main import create_app
from musicrec.serving.release import load_release
from musicrec.serving.service import DemoService


@pytest.fixture(scope="module")
def client(demo_release_dir: Path) -> Iterator[TestClient]:
    app = create_app(lambda: DemoService(load_release(demo_release_dir)))
    with TestClient(app) as test_client:
        yield test_client


def test_health_reports_release(client: TestClient) -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["model_version"] == "test-release"
    assert body["models"]["pure_svd"] == {"latent_factors": 2}


def test_existing_user_recommendation_has_names_and_popularity(client: TestClient) -> None:
    response = client.post("/recommend", json={"user_id": "1", "k": 2, "model": "m1"})
    body = response.json()
    assert response.status_code == 200
    assert (body["branch"], body["model"], body["fallback_used"]) == ("existing_user", "m1", False)
    first = body["recommendations"][0]
    assert first["rank"] == 1 and first["name"].startswith("Artist ")
    assert body["mean_listeners"] == pytest.approx(
        sum(r["listeners"] for r in body["recommendations"]) / len(body["recommendations"])
    )


def test_unknown_user_is_404(client: TestClient) -> None:
    assert client.post("/recommend", json={"user_id": "999"}).status_code == 404
    assert client.get("/users/999/history").status_code == 404


def test_new_user_and_empty_profile_branches(client: TestClient) -> None:
    new = client.post("/recommend", json={"history": [{"item_id": "1"}], "k": 3}).json()
    assert (new["branch"], new["model"], new["fallback_used"]) == ("new_user", "m2", False)
    empty = client.post("/recommend", json={"history": [], "k": 3}).json()
    assert (empty["branch"], empty["fallback_used"], empty["fallback_reason"]) == (
        "popularity",
        True,
        "empty_profile",
    )


def test_request_validation(client: TestClient) -> None:
    assert client.post("/recommend", json={}).status_code == 422
    too_many = [{"item_id": str(i)} for i in range(1, 7)]
    assert client.post("/recommend", json={"history": too_many}).status_code == 422
    duplicate = [{"item_id": "1"}, {"item_id": "1"}]
    assert client.post("/recommend", json={"history": duplicate}).status_code == 422
    assert client.post("/recommend", json={"user_id": "1", "model": "svd"}).status_code == 422


def test_users_history_and_artist_search(client: TestClient) -> None:
    users = client.get("/users", params={"limit": 3}).json()
    assert [u["user_id"] for u in users] == ["1", "2", "3"]
    assert users[0]["history_size"] == 4
    history = client.get("/users/1/history").json()
    assert history["total"] == 4
    assert [i["split"] for i in history["items"]].count("validation") == 1
    counts = [i["listening_count"] for i in history["items"]]
    assert counts == sorted(counts, reverse=True)
    found = client.get("/artists", params={"q": "artist 1"}).json()
    assert [a["item_id"] for a in found] == ["1"]


def test_cors_allows_local_frontend(client: TestClient) -> None:
    response = client.options(
        "/recommend",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
