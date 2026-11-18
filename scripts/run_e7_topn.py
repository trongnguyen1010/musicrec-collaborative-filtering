"""E7: UserCF/ItemCF with top-N 'sum' aggregation on the locked Chapter 3 representations.

Phases (one per call):
- validation: fit on train and score validation for the selected grid points (all by
  default). --max-users scores only the first users by id and is a timing sample: it
  reports NDCG@10 of that subset only and is never used for selection.
- select: read every full validation result, pick the NDCG@10 winner per model
  (ties: grid order), write selection.json. Fails if a grid point is missing.
- stats: paired tests of the two test winners against Popularity and PureSVD (per-user
  NDCG@10 from --baseline-csv), Holm within the E7 family of four pairs, one shared
  bootstrap index matrix, rank-biserial r. Labelled a post-lock supplementary analysis.
- test: write lock.json (winners and result hashes) before test.parquet is opened, refit
  each winner on train (no refit on validation), mask train + validation, score test once.
Every run directory records timings, machine and library versions.
"""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.metadata  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from math import fsum  # noqa: E402
from pathlib import Path  # noqa: E402
from time import perf_counter  # noqa: E402
from typing import Any  # noqa: E402

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.ranking import evaluate_ranking, ndcg_at_k  # noqa: E402
from musicrec.recommenders.item_cf import ItemCFRecommender  # noqa: E402
from musicrec.recommenders.user_cf import UserCFRecommender  # noqa: E402

CLASSES: dict[str, Any] = {"user_cf": UserCFRecommender, "item_cf": ItemCFRecommender}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grid_points(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Grid in YAML order: representation, then neighbors, then shrinkage."""
    keys = list(config["grid"])
    return [
        dict(zip(keys, values, strict=True))
        for values in itertools.product(*(config["grid"][key] for key in keys))
    ]


def run_name(model: str, point: dict[str, Any]) -> str:
    return f"{model}_sum_{point['representation']}_L{point['neighbors']}_g{point['shrinkage']:g}"


def runtime() -> dict[str, Any]:
    """Machine and library versions recorded with every run."""
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "threads": {v: os.environ[v] for v in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"]},
        **{p: importlib.metadata.version(p) for p in ["numpy", "scipy", "pandas", "pyarrow"]},
        "git_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
        "git_status": subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True
        ).stdout,
    }


def grouped(frame: pd.DataFrame) -> dict[str, set[str]]:
    return {str(u): {str(i) for i in g.item_id} for u, g in frame.groupby("user_id")}


def load_train(source: Path) -> tuple[list[Interaction], dict[str, set[str]]]:
    train = pd.read_parquet(source / "train.parquet")
    interactions = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count), float(r.proxy_score))
        for r in train.itertuples(index=False)
    ]
    return interactions, grouped(train)


def fit_and_rank(
    model: str,
    point: dict[str, Any],
    interactions: list[Interaction],
    users: list[str],
    masks: dict[str, set[str]],
    k: int,
) -> tuple[dict[str, list[str]], dict[str, float]]:
    """Fit one configuration and rank the given users; returns lists and timings."""
    recommender = CLASSES[model](
        point["neighbors"], float(point["shrinkage"]), "sum", point["representation"]
    )
    start = perf_counter()
    recommender.fit(interactions)
    fit_seconds = perf_counter() - start
    start = perf_counter()
    lists = {u: [r.item_id for r in recommender.recommend(u, k, masks[u])] for u in users}
    return lists, {"fit_seconds": fit_seconds, "recommend_seconds": perf_counter() - start}


def validation_phase(args: argparse.Namespace, config: dict[str, Any]) -> None:
    source = Path(config["representations_run"])
    interactions, histories = load_train(source)
    validation = grouped(pd.read_parquet(source / "validation.parquet"))
    targets = {u: validation.get(u, set()) for u in histories}
    users = sorted(histories, key=int)
    sample = users[: args.max_users] if args.max_users else users
    k = max(config["ks"])
    points = [
        (m, p)
        for m in args.models or config["models"]
        for p in grid_points(config)
        if not args.only or run_name(m, p) in args.only
    ]
    if not points:
        raise ValueError("No grid point selected")
    phase = "validation_sample" if args.max_users else "validation"
    for model, point in points:
        out = args.output_dir / phase / run_name(model, point)
        out.mkdir(parents=True, exist_ok=False)
        lists, timing = fit_and_rank(model, point, interactions, sample, histories, k)
        start = perf_counter()
        if args.max_users:
            catalog = {i for h in histories.values() for i in h}
            values = [
                ndcg_at_k(lists[u], targets[u] & catalog, 10)
                for u in sample
                if targets[u] & catalog
            ]
            result: dict[str, Any] = {
                "sample_users": len(sample),
                "sample_eligible_users": len(values),
                "sample_ndcg_at_10": fsum(values) / len(values) if values else None,
            }
        else:
            result = evaluate_ranking(lists, targets, histories, ks=tuple(config["ks"]))
            (out / "evaluation.json").write_text(json.dumps(result, indent=2) + "\n", "utf-8")
            result = {
                "users_eligible": result["users_eligible"],
                "at_k": result["at_k"],
            }
        timing["evaluate_seconds"] = perf_counter() - start
        summary = {
            "phase": phase,
            "model": model,
            "aggregation": "sum",
            **point,
            "users_scored": len(sample),
            **result,
            "timing_seconds": timing,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "command": sys.argv,
            "config_sha256": sha256(args.config),
            "input_sha256": {
                n: sha256(source / n) for n in ["train.parquet", "validation.parquet"]
            },
            "runtime": runtime(),
        }
        (out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", "utf-8")
        ndcg = result.get("sample_ndcg_at_10", result.get("at_k", {}).get("10", {}).get("ndcg"))
        print(f"{run_name(model, point)} ndcg@10={ndcg} timing={timing}", flush=True)


def select_phase(args: argparse.Namespace, config: dict[str, Any]) -> None:
    winners = {}
    rows = []
    for model in config["models"]:
        best = None
        for point in grid_points(config):
            path = args.output_dir / "validation" / run_name(model, point) / "metrics.json"
            metrics = json.loads(path.read_text(encoding="utf-8"))
            ndcg = metrics["at_k"]["10"]["ndcg"]
            rows.append({"model": model, **point, "validation_ndcg_at_10": ndcg})
            if best is None or ndcg > best[1]:
                best = ({**point, "metrics_sha256": sha256(path)}, ndcg)
        assert best is not None
        winners[model] = {"selected": best[0], "validation_ndcg_at_10_seed42": best[1]}
    pd.DataFrame(rows).to_csv(args.output_dir / "validation_summary.csv", index=False)
    selection = {
        "rule": "max_ndcg_at_10_validation_seed42_ties_first_in_grid_order",
        "winners": winners,
        "test_file_read": False,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "config_sha256": sha256(args.config),
    }
    (args.output_dir / "selection.json").write_text(json.dumps(selection, indent=2) + "\n", "utf-8")
    print(json.dumps(winners, indent=1))


def test_phase(args: argparse.Namespace, config: dict[str, Any]) -> None:
    selection_path = args.output_dir / "selection.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    out = args.output_dir / "test"
    out.mkdir(parents=False, exist_ok=False)
    lock = {
        "locked_at_utc": datetime.now(UTC).isoformat(),
        "selection_sha256": sha256(selection_path),
        "winners": selection["winners"],
        "test_masks": config["test_masks"],
        "refit_on_validation": config["refit_on_validation"],
        "runtime": runtime(),
    }
    (out / "lock.json").write_text(json.dumps(lock, indent=2) + "\n", "utf-8")
    source = Path(config["representations_run"])
    interactions, histories = load_train(source)
    validation = grouped(pd.read_parquet(source / "validation.parquet"))
    validated = {u: validation.get(u, set()) for u in histories}
    test = grouped(pd.read_parquet(source / "test.parquet"))
    targets = {u: test.get(u, set()) for u in histories}
    users = sorted(histories, key=int)
    masks = {u: histories[u] | validated[u] for u in users}
    rows = []
    for model, winner in selection["winners"].items():
        point = {k: winner["selected"][k] for k in config["grid"]}
        lists, timing = fit_and_rank(model, point, interactions, users, masks, max(config["ks"]))
        result = evaluate_ranking(
            lists, targets, histories, ks=tuple(config["ks"]), split="test", validation=validated
        )
        target = out / model
        target.mkdir()
        (target / "evaluation.json").write_text(json.dumps(result, indent=2) + "\n", "utf-8")
        for k, metrics in result["at_k"].items():
            rows.append({"model": model, **point, "k": int(k), **metrics, **timing})
        print(f"{model} test ndcg@10={result['at_k']['10']['ndcg']} timing={timing}", flush=True)
    pd.DataFrame(rows).to_csv(out / "metrics.csv", index=False)


STATS_PAIRS = [
    ("user_cf", "Popularity"),
    ("user_cf", "PureSVD"),
    ("item_cf", "Popularity"),
    ("item_cf", "PureSVD"),
]


def stats_phase(args: argparse.Namespace, config: dict[str, Any]) -> None:
    from musicrec.evaluation.inference import holm, resample_indices
    from musicrec.evaluation.paired import mean_interval, paired_comparison

    baseline = pd.read_csv(args.baseline_csv, dtype={"user_id": str}).set_index("user_id")
    per_user: dict[str, dict[str, float]] = {
        name: {u: float(v) for u, v in baseline[name].items()} for name in baseline.columns
    }
    for model in config["models"]:
        path = args.output_dir / "test" / model / "evaluation.json"
        result = json.loads(path.read_text(encoding="utf-8"))
        per_user[model] = {
            u: float(v["at_k"]["10"]["ndcg"])
            for u, v in result["per_user"].items()
            if v["eligible"]
        }
    users = sorted(per_user["user_cf"], key=int)
    indices = resample_indices(len(users), 1000, 42)
    rows = [
        {"a": f"{a}_e7", "b": b, **paired_comparison(per_user[a], per_user[b], indices)}
        for a, b in STATS_PAIRS
    ]
    for row, adjusted in zip(rows, holm([r["wilcoxon_p"] for r in rows]), strict=True):
        row["holm_p"] = adjusted
    names = [*config["models"], *baseline.columns]
    out = {
        "label": "phan_tich_bo_sung_sau_khi_khoa_cau_hinh",
        "metric": "ndcg@10_test",
        "bootstrap": {"resamples": 1000, "seed": 42, "indices": "shared_across_pairs"},
        "test": "two_sided_wilcoxon_signed_rank_zero_differences_dropped",
        "adjustment": "holm_within_e7_family_of_4_pairs",
        "baseline_csv": str(args.baseline_csv),
        "baseline_csv_sha256": sha256(args.baseline_csv),
        "pairs": rows,
        "mean_ndcg10_ci": {
            n: mean_interval([per_user[n][u] for u in users], indices) for n in names
        },
    }
    target = args.output_dir / "test" / "statistics_ndcg_at_10.json"
    target.write_text(json.dumps(out, indent=2) + "\n", "utf-8")
    print(json.dumps(rows, indent=1))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["validation", "select", "test", "stats"])
    parser.add_argument(
        "--baseline-csv",
        type=Path,
        default=Path("outputs/chuong_4_bo_sung_2/thong_ke/phan_tich/ndcg10_tung_nguoi_dung.csv"),
    )
    parser.add_argument("--config", type=Path, default=Path("configs/e7_topn_neighbors.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--models", nargs="*", choices=sorted(CLASSES))
    parser.add_argument("--only", nargs="*", help="run names, e.g. user_cf_sum_binary_L20_g0")
    parser.add_argument("--max-users", type=int, default=None)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if config["aggregation"] != "sum":
        raise ValueError("E7 runs the sum aggregation only")
    phases = {
        "validation": validation_phase,
        "select": select_phase,
        "test": test_phase,
        "stats": stats_phase,
    }
    phases[args.phase](args, config)


if __name__ == "__main__":
    main()
