import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.popularity import PopularityRecommender


def test_popularity_orders_items_and_excludes_seen_items() -> None:
    model = PopularityRecommender().fit(
        [
            Interaction("u1", "a", 2),
            Interaction("u2", "b", 5),
            Interaction("u3", "a", 4),
        ]
    )

    recommendations = model.recommend("u1", k=2, seen_item_ids={"a"})

    assert [item.item_id for item in recommendations] == ["b"]
    assert recommendations[0].reason == "popular_with_all_users"


def test_log_count_hand_example_numeric_ties_prefix_and_cold_start() -> None:
    interactions = [
        Interaction("1", "2", 3),
        Interaction("2", "2", 3),
        Interaction("1", "10", 15),
        Interaction("3", "3", 7),
    ]
    model = PopularityRecommender().fit(interactions)
    assert model.predict("1", "2") == 4  # log2(4) + log2(4), not log2(7).
    assert model.predict("1", "10") == 4
    assert model.predict("1", "3") == 3
    full = model.recommend("1", 20, set())
    assert [item.item_id for item in full] == ["2", "10", "3"]
    assert model.recommend("1", 2, set()) == full[:2]
    assert model.recommend("1", 20, {"2", "99"}) == full[1:]
    assert model.recommend("1", 20, {"2", "10", "3"}) == []
    assert PopularityRecommender().fit(reversed(interactions)).recommend("1", 20, set()) == full
    for item in full:
        assert model.predict("other-user", item.item_id) == item.score
    cold = model.recommend("unknown", 20, set())
    assert [(item.item_id, item.score) for item in cold] == [
        (item.item_id, item.score) for item in full
    ]
    assert all(item.reason == "popular_with_all_users_cold_start" for item in cold)
    model.fit([Interaction("9", "90", 1)])
    assert [item.item_id for item in model.recommend("9", 20, set())] == ["90"]
    with pytest.raises(ValueError, match="outside"):
        model.predict("9", "2")


def test_popularity_rejects_duplicates_nonfinite_counts_and_invalid_requests() -> None:
    for count in [float("nan"), float("inf"), -float("inf"), 0, -1]:
        with pytest.raises(ValueError):
            PopularityRecommender().fit([Interaction("1", "2", count)])
    with pytest.raises(ValueError, match="Duplicate"):
        PopularityRecommender().fit([Interaction("1", "2", 1)] * 2)
    with pytest.raises(ValueError, match="non-empty"):
        PopularityRecommender().fit([])
    with pytest.raises(RuntimeError, match="Fit"):
        PopularityRecommender().recommend("1", 10, set())
    with pytest.raises(RuntimeError, match="Fit"):
        PopularityRecommender().predict("1", "2")
    model = PopularityRecommender().fit([Interaction("1", "2", 1)])
    for k in [0, -1, True, 1.5]:
        with pytest.raises(ValueError, match="k"):
            model.recommend("1", k, set())
    with pytest.raises(ValueError, match="user_id"):
        model.recommend("", 1, set())
    with pytest.raises(ValueError, match="outside"):
        model.predict("1", "unknown")


def test_popularity_cli_train_only_no_test_file_hashes_reproducibility_and_guards(
    tmp_path: Path,
) -> None:
    source = tmp_path / "split"
    source.mkdir()
    mappings = {
        "user_id_to_index": {"1": 0, "2": 1, "3": 2},
        "item_id_to_index": {"2": 0, "3": 1, "10": 2, "20": 3},
    }
    for name, users, items, counts in [
        ("train", ["1", "2", "1", "2", "3"], ["2", "2", "10", "3", "20"], [3, 3, 15, 7, 1]),
        ("validation", ["1", "2", "3"], ["3", "10", "99"], [999999] * 3),
    ]:
        frame = pd.DataFrame({"user_id": users, "item_id": items, "listening_count": counts})
        frame["user_index"] = frame.user_id.map(mappings["user_id_to_index"]).astype("Int64")
        frame["item_index"] = frame.item_id.map(mappings["item_id_to_index"]).astype("Int64")
        frame.to_parquet(source / f"{name}.parquet", index=False)
    (source / "id_mappings.json").write_text(json.dumps(mappings), encoding="utf-8")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source.iterdir()}
    metadata_path = source / "metrics.json"

    def write_manifest() -> None:
        metadata_path.write_text(
            json.dumps({"step": 4, "seed": 42, "output_sha256": hashes}),
            encoding="utf-8",
        )

    write_manifest()
    root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        "-B",
        str(root / "scripts/run_popularity.py"),
        "--split-run",
        str(source),
        "--config",
        str(root / "configs/models/popularity.yaml"),
        "--evaluation-config",
        str(root / "configs/evaluation.yaml"),
        "--output-dir",
        str(tmp_path / "first"),
    ]
    for out in [tmp_path / "first", tmp_path / "second"]:
        command[-1] = str(out)
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        assert metrics["step"] == 8
        assert metrics["test_file_read"] is False
        assert metrics["users_eligible"] == 2
        assert metrics["users_without_catalog_targets"] == 1
        state = json.loads((out / "model.json").read_text(encoding="utf-8"))
        assert state["scores"] == {"2": 4, "3": 3, "10": 4, "20": 1}
        for name, expected in metrics["output_sha256"].items():
            assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected
    for name in [
        "recommendations.csv",
        "metrics.csv",
        "evaluation.json",
        "model.json",
        "id_mappings.json",
    ]:
        assert (tmp_path / "first" / name).read_bytes() == (tmp_path / "second" / name).read_bytes()
    before = (tmp_path / "second/metrics.json").read_bytes()
    again = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert again.returncode != 0 and "new directory" in again.stderr
    assert (tmp_path / "second/metrics.json").read_bytes() == before
    command[-1] = str(source / "nested")
    nested = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert nested.returncode != 0 and not Path(command[-1]).exists()
    with (source / "train.parquet").open("ab") as handle:
        handle.write(b"tampered")
    command[-1] = str(tmp_path / "tampered")
    bad = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert bad.returncode != 0 and "checksum mismatch" in bad.stderr
    assert not Path(command[-1]).exists()
