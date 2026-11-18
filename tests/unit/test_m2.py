"""M2 train-only tag features, profile inference, missing components and cold-user evaluation."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from musicrec.data.cold_start import partition_users, profile_order
from musicrec.data.contracts import Interaction
from musicrec.evaluation.cold_start import evaluate_cold_start, select_m2_config
from musicrec.evaluation.ranking import evaluate_ranking
from musicrec.recommenders.item_cf import ItemCFRecommender
from musicrec.recommenders.m2 import M2Recommender, ProfileScores, mix_profile_scores
from musicrec.recommenders.popularity import PopularityRecommender


def rows():
    return [
        Interaction(u, i, c)
        for u, i, c in [
            ("1", "1", 1),
            ("1", "2", 3),
            ("2", "1", 7),
            ("2", "2", 15),
            ("2", "3", 31),
            ("3", "3", 63),
            ("3", "4", 127),
        ]
    ]


def tags():
    return [
        ("1", "1", " Rock  "),
        ("1", "2", "rock"),
        ("2", "1", "ROCK"),
        ("2", "3", "jazz"),
        ("3", "4", "jazz"),
        ("heldout", "1", "secret"),
        ("1", "4", "heldout_pair"),
        ("2", "2", "rare"),
    ]


def test_features_learn_from_exact_train_pairs_and_local_thresholds():
    model = M2Recommender().fit(rows(), tags=tags())
    np.testing.assert_allclose(
        model.thresholds, np.quantile(np.arange(1.0, 8), [0.2, 0.4, 0.6, 0.8])
    )
    assert model.vocabulary == ["jazz", "rock"]
    np.testing.assert_allclose(model.idf, [np.log(5 / 3) + 1] * 2)
    np.testing.assert_allclose(model._features.toarray(), [[0, 1], [0, 1], [1, 0], [1, 0]])
    assert model.feature_report["tag_rows_allowed_nonempty"] == 6
    clean = M2Recommender().fit(rows(), tags=tags()[:5] + tags()[-1:])
    np.testing.assert_array_equal(clean._features.toarray(), model._features.toarray())
    assert set(model.item_cf._users) == {"1", "2", "3"}


def test_v1_hand_example_per_candidate_missing_components():
    features = ProfileScores(
        np.array([0.8, 0.8, 0.8, 0.8]),
        np.array([True, False, True, False]),
        np.full(4, 0.6),
        np.array([True, True, False, False]),
        np.full(4, 0.2),
        2,
    )
    # V1 example: w=.4; fallback=.75*.6+.25*.2=.5; mixed=.62.
    np.testing.assert_allclose(mix_profile_scores(features, 0.75, 5), [0.62, 0.5, 0.44, 0.2])
    with pytest.raises(ValueError):
        mix_profile_scores(features, float("nan"), 5)
    with pytest.raises(ValueError):
        mix_profile_scores(features, 0.5, 0)


def test_item_cf_profile_matches_dense_frozen_neighbors():
    model = M2Recommender().fit(rows(), tags=tags())
    profile = [Interaction("query", "1", 7), Interaction("query", "unknown", 1)]
    model.set_profile("query", profile)
    saved_ratings, saved_neighbors = model.item_cf._ratings.copy(), model.item_cf._weights.copy()
    features = model.profile_scores("query")
    proxy = model._proxy(profile[0]).proxy_score
    support = model.item_cf._weights.toarray()[:, 0] > 0
    np.testing.assert_array_equal(features.cf_available, support)
    np.testing.assert_allclose(features.cf[support], (proxy - 1) / 4)
    np.testing.assert_allclose(features.content, [1, 1, 0, 0])
    assert features.history_size == 2
    assert "1" not in [r.item_id for r in model.recommend("query", 20, set())]
    assert (saved_ratings != model.item_cf._ratings).nnz == 0
    assert (saved_neighbors != model.item_cf._weights).nnz == 0
    model.set_profile("query", [Interaction("query", "unknown", 1)])
    features = model.profile_scores("query")
    assert not features.cf_available.any() and not features.content_available.any()
    np.testing.assert_array_equal(mix_profile_scores(features, 0.75, 3), features.popularity)
    assert all("cf=0_content=0" in r.reason for r in model.recommend("query", 20, set()))


def test_zero_profile_popularity_roundtrip_no_fit_or_profile_persistence(tmp_path: Path):
    model = M2Recommender(alpha=0.75, history_threshold=3).fit(rows(), tags=tags())
    base = PopularityRecommender().fit(rows())
    assert [r.item_id for r in model.recommend("new", 20, {"2"})] == [
        r.item_id for r in base.recommend("new", 20, {"2"})
    ]
    assert all(r.reason == "m2_popularity_empty_profile" for r in model.recommend("new", 20, set()))
    model.set_profile("new", [Interaction("new", "1", 7)])
    expected = model.recommend("new", 20, set())
    directory = tmp_path / "m2"
    model.save(directory)
    with patch.object(ItemCFRecommender, "fit", side_effect=AssertionError("no fit")):
        restored = M2Recommender.load(directory)
    assert restored._profiles == {}
    restored.set_profile("new", [Interaction("new", "1", 7)])
    assert restored.recommend("new", 20, set()) == expected
    for r in expected:
        assert restored.predict("new", r.item_id) == pytest.approx(r.score)
    with pytest.raises(FileExistsError):
        model.save(directory)
    with (directory / "tags.npz").open("ab") as handle:
        handle.write(b"corrupt")
    with pytest.raises(ValueError, match="checksum"):
        M2Recommender.load(directory)


def test_empty_vocabulary_and_validation():
    model = M2Recommender().fit(rows())
    model.set_profile("new", [Interaction("new", "4", 1)])
    assert not model.profile_scores("new").content_available.any()
    assert len(model.recommend("new", 20, set())) == 3
    with pytest.raises(ValueError):
        model.set_profile("new", [Interaction("different", "4", 1)])
    with pytest.raises(ValueError):
        model.set_profile("new", [Interaction("new", "4", 1)] * 2)
    with pytest.raises(ValueError):
        model.recommend("new", 0, set())
    with pytest.raises(RuntimeError):
        M2Recommender().recommend("new", 3, set())


def test_partition_and_profiles_are_reproducible_and_nested():
    users = [str(i) for i in range(1, 28)]
    roles = partition_users(users)
    assert roles == partition_users(list(reversed(users)))
    assert [len(v) for v in roles.values()] == [21, 2, 4]
    assert len(set(sum(roles.values(), []))) == 27
    ordered = profile_order("query", users)
    assert ordered == profile_order("query", list(reversed(users)))
    assert ordered[:1] == ordered[:3][:1] and ordered[:3] == ordered[:5][:3]


def test_cold_evaluator_matches_warm_formulas_without_learning_query_profiles():
    learned = {"a": {"1", "2"}, "b": {"2", "3"}}
    recs = {"q": ["2", "3"]}
    targets, profiles = {"q": {"2", "outside"}}, {"q": {"1"}}
    cold = evaluate_cold_start(recs, targets, learned, profiles, ks=(2,))
    # Identical item statistics but a distinct query ID; warm includes a with same history.
    warm = evaluate_ranking(
        {"a": ["2", "3"], "b": []},
        {"a": {"2", "outside"}, "b": set()},
        {"a": {"1"}, "b": {"2", "3"}},
        ks=(2,),
    )
    # Accuracy uses the same public primitives; hand ARP=(2+1)/2, ILD=1-1/sqrt(2).
    assert cold["at_k"]["2"]["precision"] == warm["at_k"]["2"]["precision"] == 0.5
    assert cold["at_k"]["2"]["ndcg"] == 1
    assert cold["at_k"]["2"]["arp"] == 1.5
    assert cold["at_k"]["2"]["ild"] == pytest.approx(1 - 1 / np.sqrt(2))
    empty = evaluate_cold_start({"q": []}, targets, learned, {"q": set()}, ks=(2,))
    assert empty["users_eligible"] == 1 and empty["at_k"]["2"]["ndcg"] == 0
    assert empty["at_k"]["2"]["arp"] is None
    with pytest.raises(ValueError, match="disjoint"):
        evaluate_cold_start({"a": []}, {"a": set()}, learned, {"a": set()})
    with pytest.raises(ValueError):
        evaluate_cold_start({"q": ["1"]}, targets, learned, profiles)


def test_m2_selection_equal_n_weights_and_no_best_n_picking():
    grid = [
        {"alpha": 0.75, "history_threshold": 3, "ndcg_by_n": {1: 0.6, 3: 0, 5: 0}},
        {"alpha": 0.5, "history_threshold": 5, "ndcg_by_n": {1: 0.3, 3: 0.3, 5: 0.3}},
        {"alpha": 0.25, "history_threshold": 10, "ndcg_by_n": {1: 0.3, 3: 0.3, 5: 0.3}},
    ]
    chosen = select_m2_config(grid)
    assert chosen["alpha"] == 0.25 and chosen["history_threshold"] == 10
    assert chosen["mean_ndcg_at_10"] == pytest.approx(0.3)
    with pytest.raises(ValueError):
        select_m2_config(
            [{"alpha": 0.5, "history_threshold": 5, "ndcg_by_n": {0: 1, 1: 0.3, 3: 0.3, 5: 0.3}}]
        )
