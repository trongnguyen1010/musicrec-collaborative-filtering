"""Run the agreed Chapter 4 tuning grids on validation only, then confirm winners on seeds 43/44."""

import argparse
import csv
import itertools
import json
import math
import random
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNNERS = {
    "user_cf": "run_user_cf.py",
    "item_cf": "run_item_cf.py",
    "svd": "run_svd.py",
    "pure_svd": "run_pure_svd.py",
    "implicit_als": "run_implicit_als.py",
}
BASE_CONFIGS = {
    "user_cf": "configs/models/user_cf.yaml",
    "item_cf": "configs/models/item_cf.yaml",
    "svd": "configs/models/svd.yaml",
    "pure_svd": "configs/models/pure_svd_binary.yaml",
    "implicit_als": "configs/models/implicit_als.yaml",
}
STOCHASTIC = {"svd", "pure_svd", "implicit_als"}


def candidates(model: str, space: dict[str, Any], base: dict[str, Any]) -> list[dict[str, Any]]:
    """The full budget for one model, first agreed configuration first."""
    if "log_uniform" not in space:
        keys = list(space["grid"])
        grid = [
            dict(zip(keys, values, strict=True))
            for values in itertools.product(*(space["grid"][key] for key in keys))
        ]
        first = {key: base[key] for key in keys}
        return [first, *[point for point in grid if point != first]]
    rng = random.Random(42)
    points = [{key: base[key] for key in [*space["grid"], *space["log_uniform"]]}]
    while len(points) < space["budget"]:
        point: dict[str, Any] = {key: rng.choice(values) for key, values in space["grid"].items()}
        for key, (low, high) in space["log_uniform"].items():
            value = math.exp(rng.uniform(math.log(low), math.log(high)))
            point[key] = float(f"{value:.4g}")
        if point not in points:
            points.append(point)
    return points


def name_of(model: str, point: dict[str, Any]) -> str:
    """Readable, unique run directory name for one configuration."""
    return model + "".join(f"_{key[:3]}{value:g}" for key, value in point.items())


def run(model: str, config: dict[str, Any], out: Path, source: Path, seed: int) -> dict[str, Any]:
    """Run one validation fit through the existing runner and return its summary row."""
    config_path = out.parent / "configs" / f"{out.name}.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    command = [
        sys.executable,
        "-B",
        str(ROOT / "scripts" / RUNNERS[model]),
        "--representations-run",
        str(source),
        "--config",
        str(config_path),
        "--output-dir",
        str(out),
    ]
    if model in STOCHASTIC:
        command += ["--model-seed", str(seed)]
    start = datetime.now(UTC)
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
    seconds = (datetime.now(UTC) - start).total_seconds()
    metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    supplementary = metrics["supplementary"]
    return {
        "model": model,
        "run": out.name,
        "seed": seed,
        "ndcg_at_10": metrics["at_k"]["10"]["ndcg"],
        "recall_at_10": metrics["at_k"]["10"]["recall"],
        "best_epoch": supplementary.get("best_epoch"),
        "wall_seconds": seconds,
    }


def main() -> None:
    """Tune each requested model into <output-dir>/<model>/ and write tuning_summary.json."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--representations-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--models", nargs="+", choices=list(RUNNERS), default=list(RUNNERS))
    parser.add_argument("--limit", type=int, help="Timing trial: run only the first N configs")
    parser.add_argument("--no-confirm", action="store_true", help="Skip seeds 43/44")
    args = parser.parse_args()
    tuning = yaml.safe_load((ROOT / "configs/tuning.yaml").read_text(encoding="utf-8"))
    source, root = args.representations_run.resolve(), args.output_dir.resolve()
    summary_path = root / "tuning_summary.json"
    summary: dict[str, Any] = (
        json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    )
    for model in args.models:
        base = yaml.safe_load((ROOT / BASE_CONFIGS[model]).read_text(encoding="utf-8"))
        points = candidates(model, tuning["models"][model], base)[: args.limit]
        rows = []
        for point in points:
            out = root / model / name_of(model, point)
            rows.append({**point, **run(model, {**base, **point}, out, source, 42)})
            print(json.dumps(rows[-1]), flush=True)
        best_row = max(rows, key=lambda row: row["ndcg_at_10"])
        best = points[rows.index(best_row)]
        confirmations = []
        if model in STOCHASTIC and not args.no_confirm:
            for seed in tuning["confirmation_seeds"]:
                out = root / model / f"{name_of(model, best)}_seed{seed}"
                confirmations.append({**best, **run(model, {**base, **best}, out, source, seed)})
                print(json.dumps(confirmations[-1]), flush=True)
        with (root / model / "tuning.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows([*rows, *confirmations])
        summary[model] = {
            "configs_run": len(rows),
            "budget": tuning["models"][model]["budget"],
            "selected": best,
            "selected_ndcg_at_10_seed42": best_row["ndcg_at_10"],
            "confirmation": confirmations,
        }
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
