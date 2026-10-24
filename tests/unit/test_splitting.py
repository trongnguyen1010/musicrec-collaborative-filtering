"""Protect holdout conservation, train-only IDs and immutable run outputs."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from musicrec.data.splitting import split_interactions
from scripts.split_data import main


def test_split_conserves_pairs_counts_and_rounding_and_ignores_source_row_order() -> None:
    frame = pd.DataFrame(
        [
            (str(user), str(item), item * 13)
            for user, n in [(2, 5), (10, 9), (11, 10), (12, 19), (13, 20), (14, 50)]
            for item in range(1, n + 1)
        ],
        columns=["user_id", "item_id", "listening_count"],
    )
    original = frame.copy(deep=True)
    tables, mappings, _ = split_interactions(frame)
    repeated, repeated_ids, _ = split_interactions(frame.sample(frac=1, random_state=71))
    assert mappings == repeated_ids
    assert mappings["user_id_to_index"] == {
        str(u): i for i, u in enumerate([2, 10, 11, 12, 13, 14])
    }
    pairs = []
    for name in ["train", "validation", "test"]:
        pd.testing.assert_frame_equal(tables[name], repeated[name])
        pairs.extend(
            tables[name][["user_id", "item_id", "listening_count"]].itertuples(
                index=False, name=None
            )
        )
    assert len(pairs) == len(set(pairs)) == len(frame)
    assert set(pairs) == set(frame.itertuples(index=False, name=None))
    per_user = tables["user_split_counts"].set_index("user_id")
    assert per_user.validation.tolist() == [1, 1, 1, 1, 2, 5]
    assert per_user.test.tolist() == [1, 1, 1, 1, 2, 5]
    assert per_user.train.tolist() == [3, 7, 8, 17, 16, 40]
    different, _, _ = split_interactions(frame, seed=43)
    assert not tables["validation"].equals(different["validation"])
    pd.testing.assert_frame_equal(frame, original)


def test_holdout_only_artists_are_preserved_but_never_enter_train_mapping() -> None:
    frame = pd.DataFrame(
        [("7", str(i), i) for i in range(1, 6)],
        columns=["user_id", "item_id", "listening_count"],
    )
    tables, mappings, summary = split_interactions(frame)
    assert set(mappings["item_id_to_index"]) == set(tables["train"].item_id)
    assert sorted(mappings["item_id_to_index"].values()) == [0, 1, 2]
    for name in ["validation", "test"]:
        assert len(tables[name]) == 1 and tables[name].item_index.isna().all()
        assert summary["targets"][name]["outside_catalog"] == 1
        assert summary["targets"][name]["users_without_valid_targets"] == 1


@pytest.mark.parametrize("kind", ["duplicate", "short", "count", "missing", "id"])
def test_invalid_cleaning_input_is_rejected_without_silent_filtering(kind: str) -> None:
    frame = pd.DataFrame(
        [("1", str(i), i) for i in range(1, 6)],
        columns=["user_id", "item_id", "listening_count"],
    )
    if kind == "duplicate":
        frame = pd.concat([frame, frame.iloc[:1]], ignore_index=True)
    elif kind == "short":
        frame = frame.iloc[:2]
    elif kind == "count":
        frame.loc[0, "listening_count"] = 0
    elif kind == "missing":
        frame.loc[0, "item_id"] = None
    else:
        frame.loc[0, "user_id"] = "01"
    with pytest.raises(ValueError):
        split_interactions(frame)


def test_cli_verifies_source_hash_and_never_overwrites_a_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, out = tmp_path / "cleaning", tmp_path / "split"
    source.mkdir()
    path = source / "interactions.parquet"
    pd.DataFrame(
        [("1", str(i), i) for i in range(1, 6)], columns=["user_id", "item_id", "listening_count"]
    ).to_parquet(path, index=False)
    original = path.read_bytes()
    (source / "metrics.json").write_text(
        json.dumps({"step": 3, "output_sha256": {path.name: hashlib.sha256(original).hexdigest()}}),
        encoding="utf-8",
    )
    monkeypatch.setattr("sys.argv", ["split", "--clean-run", str(source), "--output-dir", str(out)])
    main()
    metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["inputs_unchanged"] and path.read_bytes() == original
    for name, expected in metrics["output_sha256"].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected
    before = (out / "metrics.json").read_bytes()
    with pytest.raises(ValueError, match="new directory"):
        main()
    assert (out / "metrics.json").read_bytes() == before
    path.write_bytes(original + b"modified")
    monkeypatch.setattr(
        "sys.argv",
        ["split", "--clean-run", str(source), "--output-dir", str(tmp_path / "new_split")],
    )
    with pytest.raises(ValueError, match="checksum mismatch"):
        main()
    assert not (tmp_path / "new_split").exists()
