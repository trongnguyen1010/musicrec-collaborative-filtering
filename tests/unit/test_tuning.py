"""The Chapter 4 tuning grids match the agreed budgets and start from the first config."""

from pathlib import Path

import pytest
import yaml

from scripts.tune_validation import BASE_CONFIGS, ROOT, candidates, name_of

TUNING = yaml.safe_load((ROOT / "configs/tuning.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("model", list(BASE_CONFIGS))
def test_budget_is_exact_unique_and_starts_with_first_agreed_config(model: str) -> None:
    space = TUNING["models"][model]
    base = yaml.safe_load(Path(ROOT / BASE_CONFIGS[model]).read_text(encoding="utf-8"))
    points = candidates(model, space, base)
    assert len(points) == space["budget"]
    assert len({name_of(model, point) for point in points}) == len(points)
    assert all(base[key] == value for key, value in points[0].items())
    for point in points:
        for key, value in point.items():
            if key in space.get("grid", {}):
                assert value in space["grid"][key]
            else:
                low, high = space["log_uniform"][key]
                assert low <= value <= high


def test_random_svd_search_is_reproducible() -> None:
    space = TUNING["models"]["svd"]
    base = yaml.safe_load((ROOT / BASE_CONFIGS["svd"]).read_text(encoding="utf-8"))
    assert candidates("svd", space, base) == candidates("svd", space, base)
