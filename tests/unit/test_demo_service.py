"""Release integrity and demo routing: existing user, new user (M2) and Popularity fallback."""

import json
import shutil
from pathlib import Path

import pytest

from musicrec.data.contracts import Interaction
from musicrec.serving.release import load_release, verify_release
from musicrec.serving.service import DemoService, ProfileEntry, UnknownUserError


@pytest.fixture(scope="module")
def service(demo_release_dir: Path) -> DemoService:
    return DemoService(load_release(demo_release_dir))


def test_release_manifest_lists_every_file(demo_release_dir: Path) -> None:
    manifest = verify_release(demo_release_dir)
    assert manifest["release"] == "test-release"
    assert {"models/pure_svd/state.json", "models/m2/item_cf/state.json"} <= set(manifest["files"])
    assert {"data/train.parquet", "data/validation.parquet", "data/artists.json"} <= set(
        manifest["files"]
    )


def test_release_refuses_changed_or_extra_files(demo_release_dir: Path, tmp_path: Path) -> None:
    copy = tmp_path / "copy"
    shutil.copytree(demo_release_dir, copy)
    (copy / "extra.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="file set"):
        verify_release(copy)
    (copy / "extra.txt").unlink()
    artists = copy / "data" / "artists.json"
    artists.write_text(artists.read_text(encoding="utf-8").replace("Artist 1", "Changed"), "utf-8")
    with pytest.raises(ValueError, match="checksum"):
        verify_release(copy)


def test_release_does_not_overwrite(demo_release_dir: Path) -> None:
    from musicrec.serving.release import ReleaseSources, build_release

    sources = ReleaseSources({}, Path(), Path(), Path(), {})
    with pytest.raises(ValueError):
        build_release(sources, demo_release_dir, "again")
    assert json.loads((demo_release_dir / "manifest.json").read_text("utf-8"))["release"]


@pytest.mark.parametrize("model", ["pure_svd", "m1", "implicit_als"])
def test_existing_user_masks_train_and_validation(service: DemoService, model: str) -> None:
    result = service.recommend_existing("1", 3, model)  # type: ignore[arg-type]
    returned = {r.item_id for r in result.recommendations}
    assert result.branch == "existing_user" and result.model == model
    assert not result.fallback_used
    assert returned and not returned & {"1", "2", "3", "4"}


def test_existing_user_matches_direct_model_call(service: DemoService) -> None:
    release = service.release
    expected = release.pure_svd.recommend("2", 4, {"1", "2", "3", "4"})
    assert service.recommend_existing("2", 4, "pure_svd").recommendations == expected


def test_unknown_user_is_rejected(service: DemoService) -> None:
    with pytest.raises(UnknownUserError):
        service.recommend_existing("999", 3, "pure_svd")


def test_new_user_uses_m2_and_never_returns_chosen_artists(service: DemoService) -> None:
    result = service.recommend_new([ProfileEntry("1"), ProfileEntry("3", 20)], 4)
    assert (result.branch, result.model, result.fallback_used) == ("new_user", "m2", False)
    assert not {r.item_id for r in result.recommendations} & {"1", "3"}
    assert all(r.reason.startswith("m2_cf=") for r in result.recommendations)


def test_new_user_matches_direct_m2_with_default_count(service: DemoService) -> None:
    m2 = service.release.m2
    m2.set_profile("x", [Interaction("x", "2", service.default_listening_count)])
    expected = m2.recommend("x", 3, set())
    assert service.recommend_new([ProfileEntry("2")], 3).recommendations == expected


def test_default_count_gets_middle_proxy_level(service: DemoService) -> None:
    from math import log2

    low, mid_high = service.release.m2.thresholds[1], service.release.m2.thresholds[2]
    assert low <= log2(1 + service.default_listening_count) <= mid_high


def test_profile_outside_m2_catalog_is_flagged(service: DemoService) -> None:
    result = service.recommend_new([ProfileEntry("8")], 3)
    assert result.fallback_used and result.fallback_reason == "no_profile_artist_in_m2_catalog"
    assert result.ignored_item_ids == ["8"]
    assert "8" not in {r.item_id for r in result.recommendations}


def test_empty_profile_falls_back_to_popularity(service: DemoService) -> None:
    result = service.recommend_new([], 3)
    expected = [r.item_id for r in service.release.popularity.recommend("any", 3, set())]
    assert (result.branch, result.fallback_used, result.fallback_reason) == (
        "popularity",
        True,
        "empty_profile",
    )
    assert [r.item_id for r in result.recommendations] == expected


def test_profile_limits(service: DemoService) -> None:
    with pytest.raises(ValueError, match="at most"):
        service.recommend_new([ProfileEntry(str(i)) for i in range(1, 7)], 3)
    with pytest.raises(ValueError, match="Duplicate"):
        service.recommend_new([ProfileEntry("1"), ProfileEntry("1")], 3)


def test_artist_search_and_listeners(service: DemoService) -> None:
    found = service.search_artists("artist", 10)
    assert {a.item_id for a in found} == set(service.release.m2.catalog)
    assert [a.listeners for a in found] == sorted((a.listeners for a in found), reverse=True)
    assert service.artist("1").listeners == 4 and service.artist("1").name == "Artist 1"
    assert service.mean_listeners([]) is None


def test_m1_grid_point_matches_pinned_model_and_base(service: DemoService) -> None:
    pinned = service.recommend_existing("1", 3, "m1").recommendations
    assert service.recommend_existing("1", 3, "m1", (0.75, 0.5)).recommendations == pinned
    base = service.recommend_existing("1", 3, "pure_svd").recommendations
    unchanged = service.recommend_existing("1", 3, "m1", (1.0, 0.0)).recommendations
    assert [r.item_id for r in unchanged] == [r.item_id for r in base]


def test_m1_grid_rejects_points_outside_validation_grid(service: DemoService) -> None:
    with pytest.raises(ValueError, match="grid"):
        service.recommend_existing("1", 3, "m1", (0.6, 0.5))
    with pytest.raises(ValueError, match="grid"):
        service.recommend_existing("1", 3, "pure_svd", (0.75, 0.5))
