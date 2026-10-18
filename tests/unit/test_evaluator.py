import pandas as pd
import pytest

from musicrec.evaluation.evaluator import evaluate
from musicrec.pipeline import interactions_from_frame
from musicrec.recommenders.popularity import PopularityRecommender


def test_evaluator_keeps_cold_targets_and_masks_validation() -> None:
    train = pd.DataFrame(
        [("u", "a", 1), ("v", "b", 1), ("v", "c", 1)],
        columns=["user_id", "item_id", "listening_count"],
    )
    val = pd.DataFrame([("u", "b", 1)], columns=train.columns)
    targets = pd.DataFrame([("u", "c", 1), ("u", "cold", 1)], columns=train.columns)
    model = PopularityRecommender().fit(interactions_from_frame(train))
    metrics, predictions, _ = evaluate(model, train, targets, [2], extra_mask=val)
    assert predictions.item_id.tolist() == ["c"]
    assert metrics["cold_targets"] == 1
    assert metrics["by_k"]["2"]["recall"] == 0.5
    assert metrics["by_k"]["2"]["precision"] == 0.5
    assert metrics["by_k"]["2"]["coverage"] == pytest.approx(1 / 3)
    assert metrics["by_k"]["2"]["arp"] == 1
    with pytest.raises(ValueError, match="No users"):
        evaluate(model, train, targets.iloc[:0], [2])
