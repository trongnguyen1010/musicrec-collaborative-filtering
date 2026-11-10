from pathlib import Path

import pytest
import yaml

from scripts.evaluate_m2_test import given_n_targets
from scripts.run_e7_topn import grid_points, run_name


def test_given_n_legacy_targets_are_test_pairs_only() -> None:
    targets = given_n_targets(
        "test_pairs", ["1"], {"1": {"a"}}, {"1": {"t"}}, {"1": {"a", "b", "t", "v"}}
    )
    assert targets == {"1": {"t"}}


def test_given_n_all_but_profile_removes_only_supplied_artists() -> None:
    all_items = {"1": {"a", "b", "v", "t"}, "2": {"c", "d"}}
    provided = {"1": {"a"}, "2": set()}
    targets = given_n_targets("all_but_profile", ["1", "2"], provided, {}, all_items)
    assert targets == {"1": {"b", "v", "t"}, "2": {"c", "d"}}
    with pytest.raises(ValueError):
        given_n_targets("all_but_profile", ["2"], {"2": {"x"}}, {}, all_items)
    with pytest.raises(ValueError):
        given_n_targets("unknown", ["1"], provided, {}, all_items)


def test_e7_grid_has_twenty_points_per_model_in_yaml_order() -> None:
    config = yaml.safe_load(Path("configs/e7_topn_neighbors.yaml").read_text(encoding="utf-8"))
    points = grid_points(config)
    names = {run_name(m, p) for m in config["models"] for p in points}
    assert len(points) == 20 and len(names) == 40
    assert points[0] == {"representation": "binary", "neighbors": 10, "shrinkage": 0}
    assert run_name("item_cf", points[-1]) == "item_cf_sum_log_count_L200_g10"
