"""Regression coverage for split conservation, masks and evidence-gated completion."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from musicrec.recommenders.diffusion import DiffusionRecommender
from musicrec.research.io import Split, sha256
from musicrec.research.runner import evaluate


@pytest.fixture
def split(tmp_path: Path) -> Split:
    path = tmp_path / "fixture.npz"
    arrays = {
        "users": np.asarray(["[PAD]", "u1", "u2", "no_test"]),
        "items": np.asarray(["[PAD]", *[f"i{i}" for i in range(1, 14)]]),
        "train": np.asarray([[1, 1], [2, 2], [3, 4]]),
        "validation": np.asarray([[1, 2]]),
        "test": np.asarray([[1, 3], [2, 1]]),
        "valid_history": np.asarray([[1, 1]]),
        "test_history": np.asarray([[1, 1], [1, 2], [2, 2]]),
        "valid_users": np.asarray([1]),
        "test_users": np.asarray([1, 2]),
    }
    np.savez_compressed(path, **arrays)
    path.with_suffix(".json").write_text(json.dumps({"sha256": sha256(path)}))
    return Split.load(path)


def canonical(split: Split) -> set[tuple[str, str]]:
    return {
        (split.users[u], split.items[i])
        for u, i in np.concatenate([split.train, split.validation, split.test])
    }


def test_split_conservation_and_cold_targets(split: Split) -> None:
    result = split.validate(canonical(split))
    assert result["cold_test_interactions"] == 1
    assert result["empty_test_users"] == 1
    matrix = split.matrix()
    assert matrix[1, 2] == 0  # Validation edge must not build the graph.
    assert matrix[1, 3] == 0  # Cold test item is retained in the catalog.
    assert matrix.shape == (4, 14)


def test_split_checksum_detects_modified_input(split: Split) -> None:
    with split.path.open("ab") as stream:
        stream.write(b"corrupted")
    with pytest.raises(ValueError, match="checksum"):
        Split.load(split.path)


def test_reject_leakage_and_incorrect_mask(split: Split) -> None:
    with pytest.raises(ValueError, match="leakage"):
        replace(split, test=np.asarray([[1, 1]])).validate(canonical(split))
    with pytest.raises(ValueError, match="history mask"):
        replace(split, test_history=split.train[:2]).validate(canonical(split))
    with pytest.raises(ValueError, match="evaluation user"):
        replace(split, test_users=np.asarray([1, 2, 3])).validate(canonical(split))
    with pytest.raises(ValueError, match="canonical pairs"):
        split.validate(canonical(split) | {("u1", "i13")})


def test_full_sort_masks_padding_history_and_is_batch_invariant(split: Split) -> None:
    model = DiffusionRecommender("probs", split.users, split.items).fit_matrix(split.matrix())
    metrics, ranking = evaluate(model, split, "test", batch_size=1)
    again, repeated = evaluate(model, split, "test", batch_size=64)
    assert metrics == again
    np.testing.assert_array_equal(ranking["ranking"], repeated["ranking"])
    assert ranking["users"].tolist() == [1, 2]
    for user, ranked in zip(ranking["users"], ranking["ranking"], strict=True):
        forbidden = {0, *split.test_history[split.test_history[:, 0] == user, 1]}
        assert not forbidden & set(ranked)
        assert len(set(ranked)) == 10


def test_reject_empty_evaluation_users(split: Split) -> None:
    model = DiffusionRecommender("probs", split.users, split.items).fit_matrix(split.matrix())
    with pytest.raises(ValueError, match="No eligible"):
        evaluate(model, replace(split, test_users=np.asarray([], dtype=np.int64)), "test")


def test_partial_or_stale_evidence_cannot_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    from musicrec.research import reporting

    monkeypatch.setattr(reporting, "read_json", lambda path: {})
    assert reporting.acceptance([])["status"] == "incomplete"
    records = [
        {"protocol": p, "model": m, "split_id": s, "status": "completed", "mlflow_run_id": "new"}
        for p, m, s in reporting.EXPECTED
    ]
    audit = reporting.acceptance(records)
    assert audit["completed_evaluations"] == 123
    assert audit["gates"]["all_123_evaluations"] is True
    assert audit["gates"]["all_123_native_metric_checks"] is False
    assert audit["status"] == "incomplete"
