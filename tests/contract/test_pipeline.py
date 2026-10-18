import json
from pathlib import Path

import pandas as pd
import pytest

from musicrec import pipeline
from musicrec.configuration import read_config


def test_configured_pipeline_reproducibility_and_no_overwrite(tmp_path: Path, monkeypatch) -> None:
    rows = [f"u{u}\ti{i}\t{i + 1}" for u in range(3) for i in range(10)]
    (tmp_path / "interactions.dat").write_text("userID\tartistID\tweight\n" + "\n".join(rows))
    (tmp_path / "artists.dat").write_text(
        "id\tname\n" + "\n".join(f"i{i}\tName {i}" for i in range(10))
    )
    config = read_config()
    config["source"].update(
        interactions="interactions.dat", artists="artists.dat", interaction_sha256=None
    )
    config["output"]["runs_dir"] = "runs"
    monkeypatch.setattr(pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(
        pipeline, "git_state", lambda: {"git_sha": "fixture", "code_hash": "fixture"}
    )
    first, second = pipeline.run(config, "first"), pipeline.run(config, "second")
    for name in (
        "train.parquet",
        "validation.parquet",
        "test.parquet",
        "validation_predictions.parquet",
    ):
        pd.testing.assert_frame_equal(pd.read_parquet(first / name), pd.read_parquet(second / name))
    assert (first / "validation_metrics.json").read_bytes() == (
        second / "validation_metrics.json"
    ).read_bytes()
    manifest = json.loads((first / "manifest.json").read_text())
    assert manifest["status"] == "completed" and not manifest["test_evaluated"]
    assert "config_hash" in manifest and "interactions" in manifest
    with pytest.raises(FileExistsError):
        pipeline.run(config, "first")
