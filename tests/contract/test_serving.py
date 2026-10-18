from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from scipy import sparse

from musicrec.api.main import create_app
from musicrec.configuration import sha256, write_json
from musicrec.pipeline import interactions_from_frame
from musicrec.recommenders.extensions import ColdStartModel, Reranker
from musicrec.recommenders.models import ItemCFRecommender, make_model
from musicrec.serving.service import RecommendationService


@pytest.fixture
def release(tmp_path: Path) -> Path:
    folder = tmp_path / "release"
    folder.mkdir()
    train = pd.DataFrame(
        [
            (u, i, float(j + 1))
            for u, items in [("u1", ["a", "b"]), ("u2", ["a", "c"]), ("u3", ["b", "d", "e"])]
            for j, i in enumerate(items)
        ],
        columns=["user_id", "item_id", "listening_count"],
    )
    rows = interactions_from_frame(train)
    base = make_model("pure_svd", {"factors": 2, "seed": 42}).fit(rows)
    base.save(folder / "base.npz")
    item_cf = ItemCFRecommender(neighbors=4, shrinkage=0)
    item_cf.fit(rows)
    cold = ColdStartModel(
        item_cf,
        sparse.csr_matrix([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [1.0, 0.0]]),
        threshold=1,
    )
    cold.save(folder / "m2")
    train.to_parquet(folder / "train.parquet", index=False)
    write_json(folder / "artist_names.json", {i: "Artist " + i for i in base.items})
    write_json(folder / "rerank.json", {"candidates": 100, "weight": 1.0, "penalty": 0.0})
    write_json(
        folder / "manifest.json",
        {
            "schema": "musicrec_release_v1",
            "model_version": "fixture-v1",
            "git_sha": "fixture",
            "data_version": "fixture",
            "run_id": "fixture",
            "config_hash": "fixture",
            "test_lock_sha256": "fixture",
            "files": {
                str(p.relative_to(folder)).replace("\\", "/"): sha256(p)
                for p in folder.rglob("*")
                if p.is_file()
            },
        },
    )
    return folder


def test_api_real_artifact_known_new_guest_and_invalid_inputs(release: Path) -> None:
    with TestClient(create_app(release)) as client:
        assert client.get("/health").status_code == 200
        known = client.post("/recommend", json={"user_id": "u1", "k": 10}).json()
        assert known["model_version"] == "fixture-v1" and not known["fallback_used"]
        assert not {"a", "b"} & {r["item_id"] for r in known["recommendations"]}
        assert len(known["recommendations"]) == 3
        assert all(r["name"].startswith("Artist") for r in known["recommendations"])
        assert client.post("/recommend", json={}).json()["fallback_used"]
        new = client.post(
            "/recommend",
            json={"user_id": "new", "history": [{"item_id": "a", "listening_count": 3}]},
        ).json()
        assert new["fallback_used"] and "a" not in [r["item_id"] for r in new["recommendations"]]
        for payload in [
            {"k": 0},
            {"k": True},
            {"history": [{"item_id": " ", "listening_count": 1}]},
            {"history": [{"item_id": "a", "listening_count": "Infinity"}]},
        ]:
            assert client.post("/recommend", json=payload).status_code == 422


def test_missing_or_corrupt_model_is_not_ready(release: Path, tmp_path: Path) -> None:
    with TestClient(create_app(tmp_path / "missing")) as client:
        assert client.get("/health").status_code == 503
        assert client.post("/recommend", json={}).status_code == 503
    (release / "artist_names.json").write_text("{}")
    with pytest.raises(ValueError, match="checksum"):
        RecommendationService.from_release(release)


def test_online_offline_and_parallel_profiles(release: Path) -> None:
    service = RecommendationService.from_release(release)
    from musicrec.recommenders.models import MatrixModel

    loaded = MatrixModel.load(release / "base.npz")
    expected = Reranker(loaded, 100, 1, 0).recommend("u1", 3, {"a", "b"})
    assert service.recommend_profile("u1", None, 3).recommendations == expected

    def request(item: str):
        return service.recommend_profile(None, [{"item_id": item, "listening_count": 1}], 3)

    sequential = {item: request(item) for item in ["a", "b", "c", "d", "e"]}
    with ThreadPoolExecutor(max_workers=4) as executor:
        parallel = list(executor.map(request, ["a", "b", "c", "d", "e"] * 4))
    for item, result in zip(["a", "b", "c", "d", "e"] * 4, parallel, strict=True):
        assert result == sequential[item]
