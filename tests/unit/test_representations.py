"""Check train-only thresholds, boundary ties, mappings and immutable CLI inputs."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.sparse import load_npz

from musicrec.data.representations import prepare_representations


def sample_splits() -> tuple[dict[str, pd.DataFrame], dict[str, dict[str, int]]]:
    """Use train log-counts 1..6 and one artist absent from the train catalog."""

    def frame(items: list[str], counts: list[int]) -> pd.DataFrame:
        result = pd.DataFrame(
            {"user_id": ["1"] * len(items), "item_id": items, "listening_count": counts}
        )
        result["user_index"] = 0
        result["item_index"] = pd.array(
            [int(item) - 1 if int(item) <= 6 else None for item in items], dtype="Int64"
        )
        return result

    splits = {
        "train": frame([str(i) for i in range(1, 7)], [1, 3, 7, 15, 31, 63]),
        "validation": frame(["7"], [1023]),
        "test": frame(["8"], [1]),
    }
    mappings = {
        "user_id_to_index": {"1": 0},
        "item_id_to_index": {str(i): i - 1 for i in range(1, 7)},
    }
    return splits, mappings


def test_train_only_thresholds_and_sparse_roundtrip() -> None:
    splits, mappings = sample_splits()
    original = {name: frame.copy(deep=True) for name, frame in splits.items()}
    tables, matrices, summary = prepare_representations(splits, mappings)
    assert summary["transform"]["thresholds"] == [2, 3, 4, 5]
    assert tables["train"].proxy_score.tolist() == [1, 1, 2, 3, 4, 5]
    assert tables["validation"].proxy_score.tolist() == [5]
    assert tables["test"].proxy_score.tolist() == [1]
    for name, frame in tables.items():
        pd.testing.assert_frame_equal(frame[original[name].columns], original[name])
        pd.testing.assert_frame_equal(splits[name], original[name])
        assert frame.binary.eq(1).all()
    assert tables["validation"].item_index.isna().all()
    for name, matrix in matrices.items():
        assert matrix.shape == (1, 6)
        assert matrix.nnz == 6
        column = "listening_count" if name == "raw_count" else name
        np.testing.assert_array_equal(matrix.toarray()[0], tables["train"][column])
    splits["validation"]["listening_count"] = 2**62
    splits["test"]["listening_count"] = 999999
    changed, _, changed_summary = prepare_representations(splits, mappings)
    assert changed_summary["transform"] == summary["transform"]
    pd.testing.assert_frame_equal(changed["train"], tables["train"])


def test_linear_interpolation_and_repeated_thresholds() -> None:
    splits, mappings = sample_splits()
    splits["train"]["listening_count"] = [1, 1, 1, 1, 3, 7]
    tables, _, summary = prepare_representations(splits, mappings)
    assert summary["transform"]["thresholds"] == [1, 1, 1, 2]
    assert tables["train"].proxy_score.tolist() == [1, 1, 1, 1, 4, 5]
    splits["train"]["listening_count"] = [1, 1, 1, 3, 7, 7]
    # A five-row sample puts the quantile positions between observed log-counts.
    splits["train"] = splits["train"].iloc[:5].copy()
    mappings["item_id_to_index"].pop("6")
    _, _, summary = prepare_representations(splits, mappings)
    np.testing.assert_allclose(summary["transform"]["thresholds"], [1, 1, 1.4, 2.2])


@pytest.mark.parametrize("count", [0, -1, 1.5, float("nan")])
def test_reject_invalid_counts(count: float) -> None:
    splits, mappings = sample_splits()
    splits["train"]["listening_count"] = count
    with pytest.raises(ValueError):
        prepare_representations(splits, mappings)


def test_reject_invalid_mapping() -> None:
    splits, mappings = sample_splits()
    splits["validation"]["item_index"] = pd.array([0], dtype="Int64")
    with pytest.raises(ValueError, match="indices do not match"):
        prepare_representations(splits, mappings)


def test_cli_hash_validation_and_no_overwrite(tmp_path: Path) -> None:
    splits, mappings = sample_splits()
    source = tmp_path / "split"
    source.mkdir()
    for name, frame in splits.items():
        frame.to_parquet(source / f"{name}.parquet", index=False)
    (source / "id_mappings.json").write_text(json.dumps(mappings), encoding="utf-8")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source.iterdir()}
    (source / "metrics.json").write_text(
        json.dumps({"step": 4, "seed": 42, "output_sha256": hashes}), encoding="utf-8"
    )
    root = Path(__file__).resolve().parents[2]
    out = tmp_path / "inputs"
    command = [
        sys.executable,
        "-B",
        str(root / "scripts/prepare_inputs.py"),
        "--split-run",
        str(source),
        "--config",
        str(root / "configs/base.yaml"),
        "--output-dir",
        str(out),
    ]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (out / "id_mappings.json").read_bytes() == (source / "id_mappings.json").read_bytes()
    assert load_npz(out / "train_raw_count.npz").nnz == 6
    assert json.loads((out / "transform.json").read_text())["thresholds"] == [2, 3, 4, 5]
    repeated = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert repeated.returncode != 0
    assert "new directory" in repeated.stderr
    assert all(
        hashlib.sha256((source / name).read_bytes()).hexdigest() == value
        for name, value in hashes.items()
    )
    with (source / "validation.parquet").open("ab") as handle:
        handle.write(b"tampered")
    command[-1] = str(tmp_path / "tampered_output")
    tampered = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert tampered.returncode != 0
    assert "checksum mismatch" in tampered.stderr
    assert not Path(command[-1]).exists()
