"""Dense-SVD references and CLI boundaries for fixed-rank representation checks."""

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
from musicrec.recommenders.pure_svd import PureSVDRecommender


def sample_rows() -> list[Interaction]:
    return [
        Interaction(user, item, 100, score)
        for user, item, score in [
            ("1", "1", 3),
            ("1", "2", 5),
            ("2", "1", 1),
            ("2", "2", 3),
            ("2", "3", 5),
            ("3", "1", 5),
            ("3", "2", 3),
            ("3", "4", 1),
            ("4", "10", 2),
        ]
    ]


def test_matches_dense_svd_without_bias_scaling_or_clipping_and_masks_seen(tmp_path: Path) -> None:
    rows = sample_rows()
    model = PureSVDRecommender(latent_factors=2).fit(rows)
    matrix = np.array([[3, 5, 0, 0, 0], [1, 3, 5, 0, 0], [5, 3, 0, 1, 0], [0, 0, 0, 0, 2.0]])
    u, singular, components = np.linalg.svd(matrix, full_matrices=False)
    expected = (u[:, :2] * singular[:2]) @ components[:2]
    item_ids = ["1", "2", "3", "4", "10"]
    for user in range(4):
        for item, item_id in enumerate(item_ids):
            assert model.predict(str(user + 1), item_id) == pytest.approx(
                expected[user, item], abs=1e-10
            )
    assert model.predict("3", "3") < 0  # An association score, never clipped into [1, 5].
    full = model.recommend("1", 20, set())
    assert [r.item_id for r in full] == ["3", "4", "10"]
    assert all(r.reason == "pure_svd" for r in full)
    for rec in full:
        assert rec.score == pytest.approx(model.predict("1", rec.item_id), abs=1e-12)
    assert model.recommend("1", 1, set()) == full[:1]
    assert model.recommend("1", 20, {"3", "missing"}) == full[1:]
    assert model.recommend("1", 20, set(item_ids)) == []
    cold = model.recommend("new", 20, {"2"})
    assert [r.item_id for r in cold] == ["1", "3", "4", "10"]
    assert all(r.score == 0 and r.reason == "pure_svd_zero_profile_cold_start" for r in cold)
    assert model.predict("new", "1") == 0
    model.save(tmp_path / "model")
    with np.load(tmp_path / "model/projection.npz") as arrays:
        np.testing.assert_allclose(arrays["singular_values"], singular[:2], rtol=0, atol=1e-10)
        np.testing.assert_allclose(
            arrays["components"] @ arrays["components"].T, np.eye(2), atol=1e-12
        )
        for component in arrays["components"]:
            assert component[np.argmax(abs(component))] >= 0


def test_reproducible_counts_independence_reload_without_decomposition_and_checksums(
    tmp_path: Path,
) -> None:
    rows = sample_rows()
    model = PureSVDRecommender(latent_factors=2).fit(rows)
    other = PureSVDRecommender(latent_factors=2).fit(
        [Interaction(r.user_id, r.item_id, 99999, r.proxy_score) for r in reversed(rows)]
    )
    model.save(tmp_path / "model")
    other.save(tmp_path / "repeat")
    for name in ["state.json", "ratings.npz", "projection.npz"]:
        assert (tmp_path / "model" / name).read_bytes() == (tmp_path / "repeat" / name).read_bytes()
    with (
        patch.object(PureSVDRecommender, "fit", side_effect=AssertionError("load must not fit")),
        patch(
            "musicrec.recommenders.pure_svd.svds",
            side_effect=AssertionError("load must not decompose"),
        ),
    ):
        restored = PureSVDRecommender.load(tmp_path / "model")
    for user in ["1", "2", "3", "4", "new"]:
        assert restored.recommend(user, 20, set()) == model.recommend(user, 20, set())
    with pytest.raises(FileExistsError):
        model.save(tmp_path / "model")
    with (tmp_path / "model/projection.npz").open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        PureSVDRecommender.load(tmp_path / "model")


def test_invalid_parameters_missing_proxy_rank_and_inference_inputs() -> None:
    with pytest.raises(ValueError, match="representation"):
        PureSVDRecommender(representation="raw_count")
    for name in ["latent_factors", "max_iter"]:
        for value in [0, -1, True, 1.5]:
            with pytest.raises(ValueError):
                PureSVDRecommender(**{name: value})
    for value in [-1, True, 1.5]:
        with pytest.raises(ValueError):
            PureSVDRecommender(seed=value)
    for value in [0, -1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            PureSVDRecommender(tolerance=value)
    for rows in [[], [Interaction("1", "1", 100)], [sample_rows()[0]] * 2]:
        with pytest.raises(ValueError):
            PureSVDRecommender(latent_factors=1).fit(rows)
    with pytest.raises(ValueError, match="dimensions"):
        PureSVDRecommender().fit(sample_rows())
    with pytest.raises(RuntimeError):
        PureSVDRecommender().predict("1", "1")
    model = PureSVDRecommender(latent_factors=2).fit(sample_rows())
    for k in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            model.recommend("1", k, set())
    with pytest.raises(ValueError, match="user_id"):
        model.predict("", "1")
    with pytest.raises(ValueError, match="outside"):
        model.predict("1", "unknown")


@pytest.mark.parametrize("representation", ["binary", "log_count"])
def test_binary_and_log_match_dense_svd_and_reload_without_proxy(
    tmp_path: Path,
    representation: str,
) -> None:
    rows = [
        Interaction(row.user_id, row.item_id, float(7**index + 3))
        for index, row in enumerate(sample_rows())
    ]
    model = PureSVDRecommender(latent_factors=1, representation=representation).fit(rows)
    expected = np.zeros((4, 5))
    items = ["1", "2", "3", "4", "10"]
    for row in rows:
        expected[int(row.user_id) - 1, items.index(row.item_id)] = (
            1 if representation == "binary" else np.log2(1 + row.listening_count)
        )
    _, _, vectors = np.linalg.svd(expected, full_matrices=False)
    expected = expected @ vectors[:1].T @ vectors[:1]
    model.save(tmp_path / "model")
    with patch.object(PureSVDRecommender, "fit", side_effect=AssertionError("load must not fit")):
        restored = PureSVDRecommender.load(tmp_path / "model")
    assert restored.representation == representation
    for user in range(4):
        for item, item_id in enumerate(items):
            assert restored.predict(str(user + 1), item_id) == pytest.approx(
                expected[user, item], abs=1e-10
            )
    if representation == "log_count":
        for value in [float("nan"), float("inf")]:
            with pytest.raises(ValueError, match="finite positive"):
                model.fit([Interaction("1", "1", value), *rows[1:]])


@pytest.mark.parametrize("representation", ["proxy_score", "binary", "log_count"])
def test_cli_32_dimensions_validation_only_no_rmse_reloads_repeats_and_rejects_corruption(
    tmp_path: Path,
    representation: str,
) -> None:
    source = tmp_path / "representations"
    source.mkdir()
    users, items = [str(i) for i in range(1, 35)], [str(i) for i in range(1, 41)]
    mappings = {
        "user_id_to_index": {u: i for i, u in enumerate(users)},
        "item_id_to_index": {item: i for i, item in enumerate(items)},
    }
    train_rows, validation_rows = [], []
    for user in users:
        u = int(user) - 1
        history = {str((u + j * 7) % 40 + 1) for j in range(5)}
        train_rows.extend(
            {
                "user_id": user,
                "item_id": item,
                "listening_count": 100,
                "proxy_score": (u + int(item)) % 5 + 1,
            }
            for item in sorted(history, key=int)
        )
        target = next(item for item in items if item not in history) if user != "34" else "999"
        validation_rows.append(
            {"user_id": user, "item_id": target, "listening_count": 100, "proxy_score": 5}
        )
    for name, frame in [
        ("train", pd.DataFrame(train_rows)),
        ("validation", pd.DataFrame(validation_rows)),
    ]:
        frame["user_index"] = frame.user_id.map(mappings["user_id_to_index"]).astype("Int64")
        frame["item_index"] = frame.item_id.map(mappings["item_id_to_index"]).astype("Int64")
        frame["binary"] = 1
        frame["log_count"] = np.log2(1.0 + frame.listening_count.to_numpy(dtype=float))
        frame.to_parquet(source / f"{name}.parquet", index=False)
    (source / "id_mappings.json").write_text(json.dumps(mappings), encoding="utf-8")
    (source / "transform.json").write_text(
        json.dumps({"fit_scope": "train only"}), encoding="utf-8"
    )

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    (source / "metrics.json").write_text(
        json.dumps(
            {"step": 5, "seed": 42, "output_sha256": {p.name: sha(p) for p in source.iterdir()}}
        ),
        encoding="utf-8",
    )
    root = Path(__file__).resolve().parents[2]
    suffix = {"proxy_score": "", "binary": "_binary", "log_count": "_log"}[representation]
    command = [
        sys.executable,
        "-B",
        str(root / "scripts/run_pure_svd.py"),
        "--representations-run",
        str(source),
        "--config",
        str(root / f"configs/models/pure_svd{suffix}.yaml"),
        "--output-dir",
        str(tmp_path / "first"),
    ]
    for out in [tmp_path / "first", tmp_path / "second"]:
        command[-1] = str(out)
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        metadata = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        assert metadata["step"] == (12 if representation == "proxy_score" else 13)
        assert metadata["test_file_read"] is False
        assert metadata["users_eligible"] == 33 and metadata["users_without_catalog_targets"] == 1
        assert metadata["supplementary"]["reload_verified_users"] == 34
        assert "proxy_rmse" not in metadata["supplementary"]
        assert "best_epoch" not in metadata["supplementary"]
        assert not (out / "learning_curve.csv").exists()
        assert PureSVDRecommender.load(out / "model").representation == representation
        assert all(sha(out / name) == value for name, value in metadata["output_sha256"].items())
    assert all(
        sha(tmp_path / "first" / name) == sha(tmp_path / "second" / name)
        for name in metadata["output_sha256"]
    )
    before = (tmp_path / "second/metrics.json").read_bytes()
    again = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert again.returncode != 0 and "new directory" in again.stderr
    assert (tmp_path / "second/metrics.json").read_bytes() == before
    if representation != "proxy_score":
        wrong = pd.read_parquet(source / "train.parquet")
        wrong.loc[0, representation] += 1
        wrong.to_parquet(source / "train.parquet", index=False)
        provenance = json.loads((source / "metrics.json").read_text(encoding="utf-8"))
        provenance["output_sha256"]["train.parquet"] = sha(source / "train.parquet")
        (source / "metrics.json").write_text(json.dumps(provenance), encoding="utf-8")
        command[-1] = str(tmp_path / "wrong-transform")
        wrong_result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        assert wrong_result.returncode != 0 and "agreed transform" in wrong_result.stderr
        assert not Path(command[-1]).exists()
    with (source / "transform.json").open("ab") as handle:
        handle.write(b"tampered")
    command[-1] = str(tmp_path / "tampered")
    bad = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert bad.returncode != 0 and "checksum mismatch" in bad.stderr
    assert not Path(command[-1]).exists()
