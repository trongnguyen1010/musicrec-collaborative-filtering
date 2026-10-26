"""Dense weighted-normal-equation checks and boundaries for the first ALS configuration."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.implicit_als import ImplicitALSRecommender


def rows() -> list[Interaction]:
    return [
        Interaction(u, i, count, 3)
        for u, i, count in [
            ("1", "1", 1),
            ("1", "2", 4),
            ("2", "2", 9),
            ("2", "10", 16),
            ("3", "1", 25),
            ("3", "10", 36),
        ]
    ]


def test_one_native_cg_epoch_matches_dense_equations_and_full_weighted_loss() -> None:
    model = ImplicitALSRecommender(latent_factors=2, max_epochs=1).fit(rows())
    counts = np.array([[1.0, 4, 0], [0, 9, 16], [25, 0, 36]])
    confidence = np.where(counts > 0, (1 + np.log1p(counts)).astype(np.float32), 1.0)
    preference = (counts > 0).astype(float)
    rng = np.random.default_rng(42)
    rng.random((3, 2), dtype=np.float32)  # User initialization precedes item initialization.
    initial_items = rng.random((3, 2), dtype=np.float32) * 0.01
    for u in range(3):
        y = initial_items.astype(float)
        expected = np.linalg.solve(
            y.T @ np.diag(confidence[u]) @ y + 0.1 * np.eye(2),
            y.T @ (confidence[u] * preference[u]),
        )
        np.testing.assert_allclose(model._user_factors[u], expected, rtol=2e-5, atol=1e-5)
    x = model._user_factors.astype(float)
    for item in range(3):
        expected = np.linalg.solve(
            x.T @ np.diag(confidence[:, item]) @ x + 0.1 * np.eye(2),
            x.T @ (confidence[:, item] * preference[:, item]),
        )
        np.testing.assert_allclose(model._item_factors[item], expected, rtol=2e-5, atol=1e-5)
    prediction = x @ model._item_factors.astype(float).T
    numerator = (confidence * (preference - prediction) ** 2).sum() + 0.1 * (
        (x * x).sum() + (model._item_factors.astype(float) ** 2).sum()
    )
    assert model.learning_curve[0]["normalized_training_loss"] == pytest.approx(
        numerator / confidence.sum(), abs=1e-6
    )
    for u in range(3):
        for i, item in enumerate(["1", "2", "10"]):
            assert model.predict(str(u + 1), item) == pytest.approx(prediction[u, i], abs=1e-12)
    recs = model.recommend("1", 20, set())
    assert [r.item_id for r in recs] == ["10"] and recs[0].reason == "implicit_als"
    assert model.recommend("1", 20, {"10"}) == []
    cold = model.recommend("new", 20, {"2"})
    assert [r.item_id for r in cold] == ["1", "10"]
    assert all(r.score == 0 and r.reason == "implicit_als_zero_profile_cold_start" for r in cold)


def test_earliest_best_checkpoint_patience_and_reload_without_fit(tmp_path: Path) -> None:
    captured = []
    scores = iter([0.5, 0.6, 0.6, 0.55])

    def monitor(model: ImplicitALSRecommender) -> float:
        captured.append((model._user_factors.copy(), model._item_factors.copy()))
        return next(scores)

    model = ImplicitALSRecommender(latent_factors=2, max_epochs=10, patience=2).fit(
        rows(), validation_score=monitor
    )
    assert (
        model.best_epoch == 2 and len(model.learning_curve) == 4 and model.stop_reason == "patience"
    )
    np.testing.assert_array_equal(model._user_factors, captured[1][0])
    np.testing.assert_array_equal(model._item_factors, captured[1][1])
    model.save(tmp_path / "model")
    with patch(
        "implicit.cpu.als.AlternatingLeastSquares.fit",
        side_effect=AssertionError("load must not fit"),
    ):
        restored = ImplicitALSRecommender.load(tmp_path / "model")
    assert restored.recommend("1", 20, set()) == model.recommend("1", 20, set())
    with pytest.raises(FileExistsError):
        model.save(tmp_path / "model")
    with (tmp_path / "model/factors.npz").open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        ImplicitALSRecommender.load(tmp_path / "model")


def test_reproducible_order_proxy_independence_and_invalid_inputs() -> None:
    a = ImplicitALSRecommender(latent_factors=2, max_epochs=2).fit(rows())
    b = ImplicitALSRecommender(latent_factors=2, max_epochs=2).fit(
        [Interaction(r.user_id, r.item_id, r.listening_count, 5) for r in reversed(rows())]
    )
    np.testing.assert_array_equal(a._item_factors, b._item_factors)
    np.testing.assert_array_equal(a._user_factors, b._user_factors)
    for name in ["latent_factors", "max_epochs", "patience"]:
        with pytest.raises(ValueError):
            ImplicitALSRecommender(**{name: 0})
    for name in ["regularization", "confidence_scale"]:
        with pytest.raises(ValueError):
            ImplicitALSRecommender(**{name: float("nan")})
    for data in [[], rows() + rows()[:1], [Interaction("1", "1", float("nan"))]]:
        with pytest.raises(ValueError):
            a.fit(data)
    with pytest.raises(RuntimeError):
        ImplicitALSRecommender().predict("1", "1")
    with pytest.raises(ValueError):
        b.recommend("1", 0, set())
    with pytest.raises(ValueError, match="outside"):
        b.predict("1", "missing")
    with pytest.raises(ValueError, match="Validation"):
        ImplicitALSRecommender(max_epochs=1).fit(rows(), validation_score=lambda _: float("nan"))


def test_cli_fixed_config_hashes_checkpoint_reload_and_no_test_or_rmse(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    train = pd.DataFrame(
        [
            {
                "user_id": r.user_id,
                "item_id": r.item_id,
                "listening_count": r.listening_count,
                "proxy_score": 3,
            }
            for r in rows()
        ]
    )
    val = pd.DataFrame(
        [
            {"user_id": u, "item_id": i, "listening_count": 1, "proxy_score": 1}
            for u, i in [("1", "10"), ("2", "1"), ("3", "2")]
        ]
    )
    mappings = {
        "user_id_to_index": {u: i for i, u in enumerate(["1", "2", "3"])},
        "item_id_to_index": {v: i for i, v in enumerate(["1", "2", "10"])},
    }
    for name, frame in [("train", train), ("validation", val)]:
        frame["user_index"] = frame.user_id.map(mappings["user_id_to_index"]).astype("Int64")
        frame["item_index"] = frame.item_id.map(mappings["item_id_to_index"]).astype("Int64")
        frame.to_parquet(source / f"{name}.parquet", index=False)
    (source / "id_mappings.json").write_text(json.dumps(mappings), encoding="utf-8")
    (source / "transform.json").write_text("{}", encoding="utf-8")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    (source / "metrics.json").write_text(
        json.dumps({"step": 5, "seed": 42, "output_sha256": hashes}), encoding="utf-8"
    )
    root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        "-B",
        str(root / "scripts/run_implicit_als.py"),
        "--representations-run",
        str(source),
        "--output-dir",
        str(tmp_path / "run"),
    ]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    metadata = json.loads((tmp_path / "run/metrics.json").read_text(encoding="utf-8"))
    assert metadata["step"] == "extension_als_first" and not metadata["test_file_read"]
    assert metadata["supplementary"]["reload_verified_users"] == 3
    assert metadata["supplementary"]["process_peak_working_set_bytes"] > 0
    assert "proxy_rmse" not in metadata["supplementary"]
    assert metadata["at_k"]["10"]["ndcg"] == metadata["supplementary"]["best_validation_ndcg_at_10"]
    assert all(
        hashlib.sha256((tmp_path / "run" / name).read_bytes()).hexdigest() == value
        for name, value in metadata["output_sha256"].items()
    )
    repeated = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert repeated.returncode != 0 and "new directory" in repeated.stderr
