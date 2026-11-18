"""Hand cases for the agreed H1 gate: dominance, infeasible control, ties and fallbacks."""

from musicrec.evaluation.h1_gate import apply_gate, dominates

BASE = {"ndcg": 0.2, "exposure": 0.5}


def point(family: str, coefficient: float, ndcg: float, exposure: float) -> dict:
    return {"family": family, "coefficient": coefficient, "ndcg": ndcg, "exposure": exposure}


def test_dominance_needs_a_strict_gain_beyond_epsilon() -> None:
    assert dominates(point("direct", 0.1, 0.2, 0.6), point("global", 0.1, 0.2, 0.55))
    assert not dominates(point("direct", 0.1, 0.2, 0.55), point("global", 0.1, 0.2, 0.55))
    assert not dominates(point("direct", 0.1, 0.21, 0.5), point("global", 0.1, 0.2, 0.55))


def test_all_spectral_dominated_stops() -> None:
    result = apply_gate(
        [point("global", 0.1, 0.195, 0.55), point("direct", 0.05, 0.198, 0.6)], BASE
    )
    assert result["status"].startswith("stop_all_spectral") and not result["advance"]
    assert result["locked"] == {"global": None, "deviation": None}
    assert result["direct_control"]["coefficient"] == 0.05


def test_no_feasible_direct_point_advances_with_flag_and_locks_by_e_n_gamma() -> None:
    points = [
        point("global", 0.1, 0.195, 0.6),
        point("global", 0.25, 0.195, 0.6),
        point("deviation", 0.5, 0.199, 0.6),
        point("deviation", 1.0, 0.15, 0.9),
        point("direct", 0.01, 0.18, 0.7),
    ]
    result = apply_gate(points, BASE)
    assert result["status"] == "advance_direct_control_has_no_feasible_point_in_locked_grid"
    assert not result["direct_control_has_feasible_point"]
    assert result["locked"]["global"]["coefficient"] == 0.1
    assert result["locked"]["deviation"]["coefficient"] == 0.5
    # Equal exposure: the higher NDCG of the deviation lock wins the representative slot.
    assert result["representative"]["family"] == "deviation"
    assert result["direct_control"] == {"family": "direct", "coefficient": 0.0, **BASE}


def test_full_tie_prefers_global_and_no_spectral_candidate_stops() -> None:
    tie = [point("deviation", 0.1, 0.2, 0.6), point("global", 0.1, 0.2, 0.6)]
    assert apply_gate(tie, BASE)["representative"]["family"] == "global"
    result = apply_gate([point("global", 0.1, 0.2, 0.5), point("direct", 0.1, 0.2, 0.7)], BASE)
    assert result["status"].startswith("stop_no_spectral") and result["representative"] is None
    assert result["direct_control"]["coefficient"] == 0.1
