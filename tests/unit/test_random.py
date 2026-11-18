import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.random import RandomRecommender


def test_repeatable_ranking_predict_prefix_seen_and_count_independence() -> None:
    interactions = [Interaction("1", item, 1) for item in ["1", "2", "3", "10", "20", "30"]]
    model = RandomRecommender().fit(interactions)
    full = model.recommend("1", 10, set())
    assert [item.item_id for item in full] == ["3", "10", "1", "2", "20", "30"]
    assert [item.score for item in full] == [6, 5, 4, 3, 2, 1]
    assert model.recommend("1", 2, set()) == full[:2]
    assert model.recommend("1", 3, {"3", "2", "99"}) == [full[1], full[2], full[4]]
    for item in full:
        assert model.predict("1", item.item_id) == item.score
        assert item.reason == "uniform_random"
    model.recommend("2", 4, {"1"})
    assert model.recommend("1", 10, set()) == full
    assert model.recommend("1", 5, {item.item_id for item in full}) == []
    reversed_counts = [
        Interaction(row.user_id, row.item_id, 9999) for row in reversed(interactions)
    ]
    assert RandomRecommender().fit(reversed_counts).recommend("1", 10, set()) == full
    assert RandomRecommender(43).fit(interactions).recommend("1", 10, set()) != full
    cold = model.recommend("unknown", 3, {"1"})
    assert len({item.item_id for item in cold}) == 3
    assert all(item.reason == "uniform_random_cold_start" and item.item_id != "1" for item in cold)


def test_random_rejects_invalid_input_and_clears_catalog_on_refit() -> None:
    for seed in [-1, True, 1.5]:
        with pytest.raises(ValueError, match="seed"):
            RandomRecommender(seed)
    with pytest.raises(RuntimeError, match="Fit"):
        RandomRecommender().recommend("1", 1, set())
    for item in ["0", "01", "a", "-1"]:
        with pytest.raises(ValueError):
            RandomRecommender().fit([Interaction("1", item, 1)])
    with pytest.raises(ValueError):
        RandomRecommender().fit([])
    model = RandomRecommender().fit([Interaction("1", "1", 1)])
    for k in [0, -1, True, 1.5]:
        with pytest.raises(ValueError, match="k"):
            model.recommend("1", k, set())
    with pytest.raises(ValueError, match="user_id"):
        model.recommend("", 1, set())
    with pytest.raises(ValueError, match="outside"):
        model.predict("1", "99")
    model.fit([Interaction("2", "2", 1)])
    assert [item.item_id for item in model.recommend("2", 2, set())] == ["2"]
    assert model.recommend("1", 1, set())[0].reason == "uniform_random_cold_start"


def test_validation_cli_reproducibility_checksums_no_test_read_and_no_overwrite(
    tmp_path: Path,
) -> None:
    source = tmp_path / "split"
    source.mkdir()
    mappings = {
        "user_id_to_index": {"1": 0, "2": 1},
        "item_id_to_index": {str(i): i - 1 for i in range(1, 7)},
    }
    for name, users, items in [
        ("train", ["1", "1", "2", "2", "2", "2"], ["1", "2", "3", "4", "5", "6"]),
        ("validation", ["1", "1", "2"], ["3", "99", "1"]),
    ]:
        frame = pd.DataFrame({"user_id": users, "item_id": items, "listening_count": 1})
        frame["user_index"] = frame.user_id.map(mappings["user_id_to_index"]).astype("Int64")
        frame["item_index"] = frame.item_id.map(mappings["item_id_to_index"]).astype("Int64")
        frame.to_parquet(source / f"{name}.parquet", index=False)
    (source / "id_mappings.json").write_text(json.dumps(mappings), encoding="utf-8")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source.iterdir()}
    (source / "metrics.json").write_text(
        json.dumps({"step": 4, "seed": 42, "output_sha256": hashes}),
        encoding="utf-8",
    )
    # A missing test file is intentional: this step must not open it, even for hashing.
    root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        "-B",
        str(root / "scripts/run_random.py"),
        "--split-run",
        str(source),
        "--config",
        str(root / "configs/models/random.yaml"),
        "--evaluation-config",
        str(root / "configs/evaluation.yaml"),
        "--output-dir",
        str(tmp_path / "first"),
    ]
    outputs = [tmp_path / "first", tmp_path / "second"]
    for out in outputs:
        command[-1] = str(out)
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        assert metrics["step"] == 7
        assert metrics["test_file_read"] is False
        assert metrics["users_total"] == metrics["users_eligible"] == 2
        assert metrics["targets_outside_catalog"] == 1
        for name, expected in metrics["output_sha256"].items():
            assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected
        assert metrics["input_sha256"] == hashes
    for name in [
        "recommendations.csv",
        "metrics.csv",
        "evaluation.json",
        "model.json",
        "id_mappings.json",
    ]:
        assert (outputs[0] / name).read_bytes() == (outputs[1] / name).read_bytes()
    before = (outputs[1] / "metrics.json").read_bytes()
    again = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert again.returncode != 0
    assert "new directory" in again.stderr
    assert (outputs[1] / "metrics.json").read_bytes() == before
    command[-1] = str(source / "nested")
    nested = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert nested.returncode != 0
    assert not Path(command[-1]).exists()
    seed_command = command[:-2] + ["--model-seed", "43", "--output-dir", str(tmp_path / "seed43")]
    seeded = subprocess.run(seed_command, cwd=root, capture_output=True, text=True)
    assert seeded.returncode == 0, seeded.stderr
    seed_metrics = json.loads((tmp_path / "seed43/metrics.json").read_text(encoding="utf-8"))
    assert seed_metrics["step"] == 14 and seed_metrics["seed"] == 43
    assert seed_metrics["input_sha256"] == hashes  # Split still comes from seed 42.
    assert seed_metrics["config"]["seed"] == 43 and seed_metrics["test_file_read"] is False
    seed_command[seed_command.index("--model-seed") + 1] = "99"
    invalid_seed = subprocess.run(seed_command, cwd=root, capture_output=True, text=True)
    assert invalid_seed.returncode != 0 and "invalid choice" in invalid_seed.stderr
    with (source / "validation.parquet").open("ab") as handle:
        handle.write(b"tampered")
    command[-1] = str(tmp_path / "tampered")
    bad = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert bad.returncode != 0
    assert "checksum mismatch" in bad.stderr
    assert not Path(command[-1]).exists()
