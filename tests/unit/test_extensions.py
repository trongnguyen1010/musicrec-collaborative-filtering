from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from musicrec.extension_experiments import cold_partitions, provided_profiles
from musicrec.pipeline import interactions_from_frame
from musicrec.recommenders.extensions import ColdStartModel, Reranker, tag_features
from musicrec.recommenders.models import ItemCFRecommender, make_model


def fixture_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"user_id": f"u{u:02}", "item_id": f"i{i}", "listening_count": i + 1.0}
            for u in range(20)
            for i in range(8)
        ]
    )


def test_rerank_identity_seen_and_candidate_constraint() -> None:
    frame = fixture_frame()
    base = make_model("pure_svd", {"factors": 2}).fit(interactions_from_frame(frame))
    identity = Reranker(base, 8, 1, 0)
    assert [r.item_id for r in identity.recommend("u00", 3, {"i0"})] == [
        r.item_id for r in base.recommend("u00", 3, {"i0"})
    ]
    assert len({r.item_id for r in Reranker(base, 8, 0.75, 0.5).recommend("u00", 4, {"i0"})}) == 4
    with pytest.raises(ValueError, match="candidate"):
        Reranker(base, 2).recommend("u00", 3, set())


def test_user_holdout_and_nested_profiles() -> None:
    frame = fixture_frame()
    groups = cold_partitions(frame, frame, 42)
    assert set(groups["reference"]).isdisjoint(groups["validation"] + groups["test"])
    assert set(groups["validation"]).isdisjoint(groups["test"])
    one = provided_profiles(frame, groups["validation"], 42, 1)
    three = provided_profiles(frame, groups["validation"], 42, 3)
    five = provided_profiles(frame, groups["validation"], 42, 5)

    def pairs(f: pd.DataFrame) -> set[tuple[str, str]]:
        return set(zip(f.user_id, f.item_id, strict=True))

    assert pairs(one) <= pairs(three) <= pairs(five)
    assert provided_profiles(frame, groups["validation"], 42, 0).empty


def test_m2_tag_leakage_missing_profiles_and_roundtrip(tmp_path: Path) -> None:
    frame = fixture_frame()
    reference = frame[frame.user_id.isin(["u00", "u01"])]
    events = tmp_path / "events.dat"
    names = tmp_path / "names.dat"
    events.write_text("userID\tartistID\ttagID\nu00\ti0\t1\nu01\ti1\t1\nu19\ti0\t2\n")
    names.write_text("tagID\ttagValue\n1\tRock\n2\tHeldOutOnly\n")
    item_cf = ItemCFRecommender(neighbors=4, shrinkage=0)
    item_cf.fit(interactions_from_frame(reference))
    features, audit = tag_features(reference, item_cf.items, events, names)
    assert audit["vocabulary"] == {"rock": 0}
    assert set(audit["tag_users"]) == {"u00", "u01"}
    assert features.shape == (8, 1)
    model = ColdStartModel(item_cf, features)
    assert model.profile_scores({})[1].startswith("popularity")
    model.profiles = {"new": {"i0": 1.0}}
    recs = model.recommend("new", 5, {"i0"})
    assert all(r.item_id != "i0" and np.isfinite(r.score) for r in recs)
    model.save(tmp_path / "model")
    loaded = ColdStartModel.load(tmp_path / "model")
    loaded.profiles = model.profiles
    assert loaded.recommend("new", 5, {"i0"}) == recs
