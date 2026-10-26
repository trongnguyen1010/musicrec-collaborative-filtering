"""Independent scalar SGD, checkpoint selection and inference checks for biased MF."""

import json
from math import fsum, sqrt
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.svd import SVDRecommender


def sample_rows() -> list[Interaction]:
    return [
        Interaction(user, item, 100, score)
        for user, item, score in [("1", "1", 1), ("1", "2", 5), ("2", "1", 4), ("2", "10", 2)]
    ]


def test_one_epoch_matches_scalar_simultaneous_sgd_and_objective(tmp_path: Path) -> None:
    rows = sample_rows()
    model = SVDRecommender(latent_factors=2, max_epochs=1).fit(rows)
    rng = np.random.Generator(np.random.PCG64(42))
    p = rng.normal(0, 0.1, (2, 2)).tolist()
    q = rng.normal(0, 0.1, (3, 2)).tolist()
    bu, bi = [0.0, 0.0], [0.0, 0.0, 0.0]
    entries = [(0, 0, 1), (0, 1, 5), (1, 0, 4), (1, 2, 2)]
    mean, lr, reg = 3.0, 0.005, 0.02
    for index in rng.permutation(len(entries)):
        u, i, target = entries[index]
        error = target - (
            mean + bu[u] + bi[i] + fsum(a * b for a, b in zip(p[u], q[i], strict=True))
        )
        old_p, old_q = p[u][:], q[i][:]
        bu[u] += lr * (error - reg * bu[u])
        bi[i] += lr * (error - reg * bi[i])
        for factor in range(2):
            p[u][factor] += lr * (error * old_q[factor] - reg * old_p[factor])
            q[i][factor] += lr * (error * old_p[factor] - reg * old_q[factor])
    model.save(tmp_path / "model")
    with np.load(tmp_path / "model/parameters.npz") as arrays:
        for name, expected in [
            ("user_bias", bu),
            ("item_bias", bi),
            ("user_factors", p),
            ("item_factors", q),
        ]:
            np.testing.assert_allclose(arrays[name], expected, rtol=0, atol=1e-15)
    squared, penalties = [], []
    for u, i, target in entries:
        prediction = mean + bu[u] + bi[i] + fsum(a * b for a, b in zip(p[u], q[i], strict=True))
        assert model.predict(str(u + 1), ["1", "2", "10"][i]) == pytest.approx(prediction)
        squared.append((target - prediction) ** 2)
        penalties.append(bu[u] ** 2 + bi[i] ** 2 + fsum(a * a for a in p[u] + q[i]))
    curve = model.learning_curve[0]
    assert curve["train_proxy_rmse"] == pytest.approx(sqrt(fsum(squared) / len(entries)))
    assert curve["regularized_objective"] == pytest.approx(
        0.5 * (fsum(squared) + reg * fsum(penalties))
    )
    changed = [Interaction(r.user_id, r.item_id, 99999, r.proxy_score) for r in reversed(rows)]
    other = SVDRecommender(latent_factors=2, max_epochs=1).fit(changed)
    for user in ["1", "2", "unknown"]:
        assert other.recommend(user, 20, set()) == model.recommend(user, 20, set())


def test_early_stopping_counts_ties_and_restores_first_best_epoch() -> None:
    scores = iter([0.2, 0.5, 0.5, 0.4, 0.3])
    snapshots = []

    def monitor(current: SVDRecommender) -> float:
        snapshots.append([current.predict("1", item) for item in ["1", "2", "10"]])
        return next(scores)

    model = SVDRecommender(latent_factors=2, max_epochs=10, patience=2).fit(
        sample_rows(), validation_score=monitor
    )
    assert model.best_epoch == 2
    assert len(model.learning_curve) == 4 and model.stop_reason == "patience"
    assert [row["improved"] for row in model.learning_curve] == [True, True, False, False]
    assert [model.predict("1", item) for item in ["1", "2", "10"]] == snapshots[1]
    assert snapshots[1] != snapshots[-1]
    assert model.learning_curve[1]["validation_ndcg_at_10"] == 0.5


def test_full_ranking_numeric_ties_masks_cold_bias_and_no_clipping() -> None:
    rows = [Interaction(str(u), i, 100, 3) for u, i in [(1, "10"), (2, "2"), (3, "1")]]
    model = SVDRecommender(latent_factors=2, max_epochs=1, init_std=1e-100).fit(rows)
    full = model.recommend("unknown", 20, set())
    assert [item.item_id for item in full] == ["1", "2", "10"]
    assert all(item.score == 3 and item.reason == "svd_item_bias_cold_start" for item in full)
    assert model.recommend("unknown", 1, set()) == full[:1]
    assert [item.item_id for item in model.recommend("1", 20, set())] == ["1", "2"]
    assert model.recommend("1", 20, {"1", "2", "missing"}) == []
    # Controlled parameters make the decomposition and absence of clipping explicit.
    model._user_bias[0] = 0.2
    model._item_bias[0] = -0.3
    model._user_factors[0] = [0.1, 0.9]
    model._item_factors[0] = [0.2, 0.8]
    assert model.predict("1", "1") == pytest.approx(3.64)
    assert model.predict("unknown", "1") == pytest.approx(2.7)
    model._item_bias[0] = 10
    assert model.predict("1", "1") > 5
    result = model.recommend("1", 1, set())[0]
    assert result.item_id == "1" and result.reason == "svd"
    assert result.score == pytest.approx(model.predict("1", "1"))


def test_model_roundtrip_without_fit_checks_hashes_and_history(tmp_path: Path) -> None:
    model = SVDRecommender(latent_factors=2, max_epochs=2).fit(sample_rows())
    model.save(tmp_path / "model")
    with patch.object(SVDRecommender, "fit", side_effect=AssertionError("load must not fit")):
        restored = SVDRecommender.load(tmp_path / "model")
    for user in ["1", "2", "unknown"]:
        assert restored.recommend(user, 20, set()) == model.recommend(user, 20, set())
    assert restored.best_epoch == 2 and restored.learning_curve == model.learning_curve
    with pytest.raises(FileExistsError):
        model.save(tmp_path / "model")
    state_file = tmp_path / "model/state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state["best_epoch"] = 3
    state_file.write_text(json.dumps(state), encoding="utf-8")
    with pytest.raises(ValueError, match="history"):
        SVDRecommender.load(tmp_path / "model")
    state["best_epoch"] = 2
    state_file.write_text(json.dumps(state), encoding="utf-8")
    with (tmp_path / "model/parameters.npz").open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        SVDRecommender.load(tmp_path / "model")


def test_invalid_parameters_missing_proxy_and_invalid_validation_scores() -> None:
    for name in ["latent_factors", "max_epochs", "patience"]:
        for value in [0, -1, True, 1.5]:
            with pytest.raises(ValueError):
                SVDRecommender(**{name: value})
    for name in ["learning_rate", "init_std"]:
        for value in [0, -1, float("nan"), float("inf")]:
            with pytest.raises(ValueError):
                SVDRecommender(**{name: value})
    for value in [-1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            SVDRecommender(regularization=value)
    for value in [-1, True, 1.5]:
        with pytest.raises(ValueError):
            SVDRecommender(seed=value)
    for rows in [[], [Interaction("1", "1", 100)], [sample_rows()[0]] * 2]:
        with pytest.raises(ValueError):
            SVDRecommender(max_epochs=1).fit(rows)
    with pytest.raises(RuntimeError):
        SVDRecommender().predict("1", "1")
    model = SVDRecommender(max_epochs=1).fit(sample_rows())
    for k in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            model.recommend("1", k, set())
    with pytest.raises(ValueError, match="user_id"):
        model.predict("", "1")
    with pytest.raises(ValueError, match="outside"):
        model.predict("1", "99")
    for value in [-1, 2, float("nan"), float("inf")]:
        with pytest.raises(ValueError, match="NDCG"):
            SVDRecommender(max_epochs=1).fit(
                sample_rows(), validation_score=lambda _, result=value: result
            )
