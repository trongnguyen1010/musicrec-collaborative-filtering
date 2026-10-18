import pytest

from musicrec.evaluation.ranking import ndcg_at_k, precision_at_k, recall_at_k


def test_ranking_metrics_use_only_top_k() -> None:
    recommended = ["a", "b", "c"]
    relevant = {"b", "c"}

    assert precision_at_k(recommended, relevant, k=2) == 0.5
    assert recall_at_k(recommended, relevant, k=2) == 0.5


def test_report_hand_calculations_and_short_lists() -> None:
    relevant = {"A", "C"}
    assert ndcg_at_k(["B", "A", "C"], relevant, 3) == pytest.approx(0.6934264036)
    assert ndcg_at_k(["A", "C", "B"], relevant, 3) == 1
    assert ndcg_at_k(["X", "B"], relevant, 3) == 0
    assert precision_at_k(["A"], relevant, 3) == 1 / 3
    assert recall_at_k(["A"], relevant, 3) == 0.5
    assert precision_at_k([], relevant, 3) == 0
    assert ndcg_at_k(["X", "X2", "A"], {"A"}, 3) == 0.5


@pytest.mark.parametrize("metric", [precision_at_k, recall_at_k, ndcg_at_k])
def test_metrics_reject_duplicates_and_invalid_k(metric) -> None:
    with pytest.raises(ValueError):
        metric(["A", "A"], {"A"}, 3)
    for k in (0, -1, True, 1.5):
        with pytest.raises(ValueError):
            metric(["A"], {"A"}, k)
