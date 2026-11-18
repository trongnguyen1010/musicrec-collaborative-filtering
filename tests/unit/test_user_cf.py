import hashlib
import json
import subprocess
import sys
from math import sqrt
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.user_cf import UserCFRecommender


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
            ("4", "5", 2),
        ]
    ]


def test_hand_example_means_full_cosine_unclipped_scores_and_global_neighbor_selection() -> None:
    rows = sample_rows()
    model = UserCFRecommender().fit(rows)
    assert model.predict("1", "3") == pytest.approx(6)
    assert model.predict("1", "4") == pytest.approx(2)
    assert model.predict("1", "5") == 4
    assert model.predict("4", "1") == 2  # No shared artists with other users.
    full = model.recommend("1", 10, set())
    assert [item.item_id for item in full] == ["3", "5", "4"]
    assert [item.reason for item in full] == ["user_cf", "user_cf_user_mean_fallback", "user_cf"]
    assert model.recommend("1", 1, set()) == full[:1]
    assert model.recommend("1", 10, {"3", "unknown"}) == full[1:]
    assert model.recommend("1", 10, {"1", "2", "3", "4", "5"}) == []
    for item in full:
        assert model.predict("1", item.item_id) == item.score
    changed_counts = [
        Interaction(row.user_id, row.item_id, 99999, row.proxy_score) for row in reversed(rows)
    ]
    assert UserCFRecommender().fit(changed_counts).recommend("1", 10, set()) == full
    # With L=1 the closer user 3 is chosen globally. User 2 cannot replace them for item 3.
    one = UserCFRecommender(neighbors=1).fit(rows)
    assert one.predict("1", "3") == 4
    assert one.predict("1", "4") == pytest.approx(2)
    shrunk = UserCFRecommender(shrinkage=10).fit(rows)
    assert shrunk.predict("1", "3") == pytest.approx(6)
    cold = model.recommend("unknown", 10, {"1"})
    assert [item.item_id for item in cold] == ["2", "3", "4", "5"]
    assert all(item.score == pytest.approx(28 / 9) for item in cold)
    assert all(item.reason == "user_cf_global_mean_cold_start" for item in cold)


def test_neighbor_cosine_and_shrinkage_state_roundtrip_without_fit(tmp_path: Path) -> None:
    model = UserCFRecommender(shrinkage=10).fit(sample_rows())
    model.save(tmp_path / "model")
    from scipy.sparse import load_npz

    weights = load_npz(tmp_path / "model/neighbors.npz").toarray()
    assert weights[0, 1] == pytest.approx(18 / sqrt(34 * 35) * 2 / 12)
    assert weights[0, 2] == pytest.approx(30 / sqrt(34 * 35) * 2 / 12)
    assert weights[0, 0] == 0
    with patch.object(UserCFRecommender, "fit", side_effect=AssertionError("load must not fit")):
        restored = UserCFRecommender.load(tmp_path / "model")
    for user in ["1", "2", "3", "4", "unknown"]:
        assert restored.recommend(user, 20, set()) == model.recommend(user, 20, set())
    with pytest.raises(FileExistsError):
        model.save(tmp_path / "model")
    with (tmp_path / "model/ratings.npz").open("ab") as handle:
        handle.write(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        UserCFRecommender.load(tmp_path / "model")


def test_numeric_neighbor_ties_and_observed_zero_deviation_still_has_support(
    tmp_path: Path,
) -> None:
    rows = [
        Interaction(u, i, 100, r)
        for u, i, r in [
            ("1", "1", 4),
            ("2", "1", 2),
            ("2", "2", 4),
            ("10", "1", 2),
            ("10", "10", 4),
        ]
    ]
    model = UserCFRecommender(neighbors=1).fit(rows)
    assert model.predict("1", "2") == 5
    assert model.predict("1", "10") == 4
    zero = UserCFRecommender().fit(
        [
            Interaction("1", "1", 100, 3),
            Interaction("2", "1", 100, 3),
            Interaction("2", "2", 100, 3),
        ]
    )
    assert zero.recommend("1", 1, set())[0].reason == "user_cf"


def test_user_cf_rejects_invalid_inputs() -> None:
    for value in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            UserCFRecommender(neighbors=value)
    for value in [-1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            UserCFRecommender(shrinkage=value)
    for value in [0, 6, 1.5, float("nan"), float("inf"), True]:
        with pytest.raises(ValueError, match="proxy_score"):
            Interaction("1", "1", 100, value)
    with pytest.raises(ValueError, match="proxy_score"):
        UserCFRecommender().fit([Interaction("1", "1", 100)])
    with pytest.raises(ValueError):
        UserCFRecommender().fit([])
    with pytest.raises(ValueError, match="Duplicate"):
        UserCFRecommender().fit([sample_rows()[0]] * 2)
    with pytest.raises(RuntimeError):
        UserCFRecommender().predict("1", "1")
    model = UserCFRecommender().fit(sample_rows())
    for k in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            model.recommend("1", k, set())
    with pytest.raises(ValueError, match="user_id"):
        model.predict("", "1")
    with pytest.raises(ValueError, match="outside"):
        model.predict("1", "99")


def test_equal_cosines_ignore_roundoff_before_global_top_l_selection() -> None:
    rows = [Interaction("1", str(i), 100, 5) for i in range(1, 41)]
    rows += [Interaction("2", str(i), 100, 5) for i in [*range(1, 7), *range(41, 75)]]
    rows += [Interaction("10", str(i), 100, 2) for i in [*range(1, 4), *range(75, 82)]]
    # Both exact cosines are 0.15: 150/sqrt(1000*1000) == 30/sqrt(1000*40).
    model = UserCFRecommender(neighbors=1).fit(rows)
    result = model.recommend("1", 1, set())[0]
    assert result.item_id == "41" and result.reason == "user_cf"
    assert UserCFRecommender(neighbors=1).fit(reversed(rows)).recommend("1", 1, set()) == [result]


@pytest.mark.parametrize(("model_name", "step"), [("user_cf", 9), ("item_cf", 10), ("svd", 11)])
def test_proxy_cf_cli_reads_step5_only_reloads_and_refuses_corruption(
    tmp_path: Path, model_name: str, step: int
) -> None:
    source = tmp_path / "representations"
    source.mkdir()
    mappings = {
        "user_id_to_index": {str(i): i - 1 for i in range(1, 5)},
        "item_id_to_index": {str(i): i - 1 for i in range(1, 6)},
    }
    train = pd.DataFrame(
        [
            {
                "user_id": r.user_id,
                "item_id": r.item_id,
                "listening_count": r.listening_count,
                "proxy_score": r.proxy_score,
            }
            for r in sample_rows()
        ]
    )
    validation = pd.DataFrame(
        {
            "user_id": ["1", "2", "3", "4"],
            "item_id": ["3", "4", "3", "99"],
            "listening_count": [99999] * 4,
            "proxy_score": [5] * 4,
        }
    )
    for name, frame in [("train", train), ("validation", validation)]:
        frame["user_index"] = frame.user_id.map(mappings["user_id_to_index"]).astype("Int64")
        frame["item_index"] = frame.item_id.map(mappings["item_id_to_index"]).astype("Int64")
        frame.to_parquet(source / f"{name}.parquet", index=False)
    (source / "id_mappings.json").write_text(json.dumps(mappings), encoding="utf-8")
    (source / "transform.json").write_text(
        json.dumps({"fit_scope": "train only"}), encoding="utf-8"
    )
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
    (source / "metrics.json").write_text(
        json.dumps({"step": 5, "seed": 42, "output_sha256": hashes})
    )
    root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        "-B",
        str(root / f"scripts/run_{model_name}.py"),
        "--representations-run",
        str(source),
        "--output-dir",
        str(tmp_path / "first"),
    ]
    for out in [tmp_path / "first", tmp_path / "second"]:
        command[-1] = str(out)
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        assert metrics["step"] == step and metrics["test_file_read"] is False
        assert metrics["supplementary"]["reload_verified_users"] == 4
        assert metrics["supplementary"]["proxy_rmse_pairs"] == 3
        if model_name == "svd":
            details = metrics["supplementary"]
            assert 1 <= details["best_epoch"] <= details["epochs_completed"] <= 100
            assert details["best_validation_ndcg_at_10"] == pytest.approx(
                metrics["at_k"]["10"]["ndcg"], abs=1e-15
            )
        for name, expected in metrics["output_sha256"].items():
            assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected
    for name in [
        "recommendations.csv",
        "metrics.csv",
        "evaluation.json",
        "model/state.json",
        "model/ratings.npz",
        "model/parameters.npz" if model_name == "svd" else "model/neighbors.npz",
        "transform.json",
    ]:
        assert (tmp_path / "first" / name).read_bytes() == (tmp_path / "second" / name).read_bytes()
    before = (tmp_path / "second/metrics.json").read_bytes()
    again = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert again.returncode != 0 and "new directory" in again.stderr
    assert (tmp_path / "second/metrics.json").read_bytes() == before
    with (source / "transform.json").open("ab") as handle:
        handle.write(b"tampered")
    command[-1] = str(tmp_path / "tampered")
    bad = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert bad.returncode != 0 and "checksum mismatch" in bad.stderr
    assert not Path(command[-1]).exists()
