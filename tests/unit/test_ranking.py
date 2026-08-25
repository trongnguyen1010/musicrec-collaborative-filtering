from musicrec.evaluation.ranking import precision_at_k, recall_at_k


def test_ranking_metrics_use_only_top_k() -> None:
    recommended = ["a", "b", "c"]
    relevant = {"b", "c"}

    assert precision_at_k(recommended, relevant, k=2) == 0.5
    assert recall_at_k(recommended, relevant, k=2) == 0.5
