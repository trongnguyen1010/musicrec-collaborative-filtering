"""Steps 4.4-4.5: freeze the validation-selected models, then score the test split exactly once.

The lock (selected configs, checkpoints and their hashes, predeclared comparison pairs)
is written before test.parquet is opened. Models are loaded from the validation runs and
never refit, except Random and Popularity, which are deterministic train-only statistics.
Test lists mask train + validation; training statistics stay train-only.
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean, stdev
from time import perf_counter
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tune_validation import STOCHASTIC, name_of  # noqa: E402

from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.ranking import evaluate_ranking, proxy_rmse  # noqa: E402
from musicrec.recommenders.base import Recommender  # noqa: E402
from musicrec.recommenders.implicit_als import ImplicitALSRecommender  # noqa: E402
from musicrec.recommenders.item_cf import ItemCFRecommender  # noqa: E402
from musicrec.recommenders.m1 import M1Recommender  # noqa: E402
from musicrec.recommenders.popularity import PopularityRecommender  # noqa: E402
from musicrec.recommenders.pure_svd import PureSVDRecommender  # noqa: E402
from musicrec.recommenders.random import RandomRecommender  # noqa: E402
from musicrec.recommenders.svd import SVDRecommender  # noqa: E402
from musicrec.recommenders.user_cf import UserCFRecommender  # noqa: E402

LOADERS: dict[str, Any] = {
    "user_cf": UserCFRecommender,
    "item_cf": ItemCFRecommender,
    "svd": SVDRecommender,
    "pure_svd": PureSVDRecommender,
    "implicit_als": ImplicitALSRecommender,
}
RMSE_MODELS = {"user_cf", "item_cf", "svd"}
# Predeclared before opening test (ROADMAP Q12 proposal, adapted to Q3/Q4 decisions).
PAIRS = [
    ["pure_svd", "popularity"],
    ["svd", "pure_svd"],
    ["m1", "pure_svd"],
    ["implicit_als", "pure_svd"],
]
SEEDS = [42, 43, 44]


def sha256(path: Path) -> str:
    """Fingerprint one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(directory: Path) -> dict[str, str]:
    """Hashes of every file under a checkpoint directory."""
    return {
        p.relative_to(directory).as_posix(): sha256(p)
        for p in sorted(directory.rglob("*"))
        if p.is_file()
    }


def build_lock(tuning: Path, m1_run: Path, representations: Path) -> dict[str, Any]:
    """Freeze the selection made on validation; refuse anything not selected there."""
    summary = json.loads((tuning / "tuning_summary.json").read_text(encoding="utf-8"))
    models: dict[str, Any] = {"random": {"refit": True}, "popularity": {"refit": True}}
    for model in ["user_cf", "item_cf", "svd", "pure_svd", "implicit_als"]:
        selected = summary[model]["selected"]
        base = name_of(model, selected)
        runs = {42: tuning / model / base}
        if model in STOCHASTIC:
            runs.update({seed: tuning / model / f"{base}_seed{seed}" for seed in SEEDS[1:]})
        models[model] = {
            "selected": selected,
            "validation_ndcg_at_10_seed42": summary[model]["selected_ndcg_at_10_seed42"],
            "runs": {
                seed: {
                    "path": str(run),
                    "metrics_sha256": sha256(run / "metrics.json"),
                    "model_sha256": tree_hashes(run / "model"),
                }
                for seed, run in runs.items()
            },
        }
    m1_metrics = json.loads((m1_run / "metrics.json").read_text(encoding="utf-8"))
    if not m1_metrics["confirmation"]["passed"] or m1_metrics.get("base_class") != "pure_svd":
        raise ValueError("Expected a confirmed M1 run on the PureSVD base")
    models["m1"] = {
        "base": "pure_svd",
        "lambda": m1_metrics["selection"]["lambda"],
        "beta": m1_metrics["selection"]["beta"],
        "candidate_size": m1_metrics["config"]["candidate_size"],
        "runs": {
            seed: {
                "path": str(m1_run / f"seed_{seed}" / "selected_model"),
                "model_sha256": tree_hashes(m1_run / f"seed_{seed}" / "selected_model"),
            }
            for seed in SEEDS
        },
        "m1_metrics_sha256": sha256(m1_run / "metrics.json"),
    }
    return {
        "locked_at_utc": datetime.now(UTC).isoformat(),
        "representations_run": str(representations),
        "selection_rule": "ndcg_at_10_validation_seed42; stochastic winners confirmed on 43/44",
        "models": models,
        "comparison_pairs": PAIRS,
        "ks": [5, 10, 20],
        "test_masks": "train_plus_validation",
        "refit_on_validation": False,
    }


def summarize_test_seeds(evaluations: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """Equal-weight mean and sample std across the predeclared seeds, never the best seed.

    musicrec.evaluation.validation.summarize_seeds only accepts validation runs, and that
    audited code stays unchanged; this applies the same rule to the test cohort.
    """
    if set(evaluations) != set(SEEDS):
        raise ValueError("Expected exactly the predeclared model seeds 42, 43 and 44")
    reference = evaluations[SEEDS[0]]
    for evaluation in evaluations.values():
        if (
            evaluation["split"] != "test"
            or evaluation["catalog_size"] != reference["catalog_size"]
            or evaluation["users_eligible"] != reference["users_eligible"]
        ):
            raise ValueError("Seed comparison requires the same test cohort")
    summary: dict[str, Any] = {"at_k": {}}
    for k, metrics in reference["at_k"].items():
        summary["at_k"][k] = {}
        for name, value in metrics.items():
            if not isinstance(value, float):
                continue
            values = [evaluations[seed]["at_k"][k][name] for seed in SEEDS]
            summary["at_k"][k][name] = {
                "mean": fmean(values),
                "sample_std": stdev(values),
                "min": min(values),
                "max": max(values),
            }
    return summary


def main() -> None:
    """Write lock.json, then evaluate every locked model and seed on test once."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--representations-run", type=Path, required=True)
    parser.add_argument("--tuning-dir", type=Path, required=True)
    parser.add_argument("--m1-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.representations_run.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    lock = build_lock(args.tuning_dir.resolve(), args.m1_run.resolve(), source)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    lock["git_sha"] = git.stdout.strip()
    (out / "lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    lock_hash = sha256(out / "lock.json")

    metadata = json.loads((source / "metrics.json").read_text(encoding="utf-8"))
    names = ["train.parquet", "validation.parquet", "test.parquet", "id_mappings.json"]
    for name in names:
        if sha256(source / name) != metadata["output_sha256"][name]:
            raise ValueError(f"Input checksum mismatch: {name}")
    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")
    test = pd.read_parquet(source / "test.parquet")

    def grouped(frame: pd.DataFrame) -> dict[str, set[str]]:
        return {
            str(user): {str(item) for item in group.item_id}
            for user, group in frame.groupby("user_id")
        }

    histories = grouped(train)
    empty: dict[str, set[str]] = {user: set() for user in histories}
    validated = empty | grouped(validation)
    targets = empty | grouped(test)
    users = sorted(histories, key=lambda user: int(str(user)))
    interactions = [
        Interaction(
            str(r.user_id),
            str(r.item_id),
            float(str(r.listening_count)),
            float(str(r.proxy_score)),
        )
        for r in train.itertuples(index=False)
    ]
    known_test = test[test.item_index.notna()]

    def load(model: str, seed: int) -> Recommender:
        if model == "random":
            return RandomRecommender(seed=seed).fit(interactions)
        if model == "popularity":
            return PopularityRecommender().fit(interactions)
        if model == "m1":
            base = load("pure_svd", seed)
            path = Path(lock["models"]["m1"]["runs"][seed]["path"])
            return M1Recommender.load(path, base=base)
        path = Path(lock["models"][model]["runs"][seed]["path"]) / "model"
        loaded: Recommender = LOADERS[model].load(path)
        return loaded

    rows: list[dict[str, Any]] = []
    results: dict[str, dict[int, dict[str, Any]]] = {}
    timings: dict[str, float] = {}
    for model in [
        "random",
        "popularity",
        "user_cf",
        "item_cf",
        "svd",
        "pure_svd",
        "implicit_als",
        "m1",
    ]:
        seeds = SEEDS if model in STOCHASTIC | {"random", "m1"} else [42]
        results[model] = {}
        for seed in seeds:
            recommender = load(model, seed)
            start = perf_counter()
            lists: dict[str, list[str]] = {}
            records: list[dict[str, Any]] = []
            for user in users:
                recs = recommender.recommend(user, 20, histories[user] | validated[user])
                lists[user] = [r.item_id for r in recs]
                records.extend(
                    {"user_id": user, "rank": i, "item_id": r.item_id, "score": r.score}
                    for i, r in enumerate(recs, 1)
                )
            seconds = perf_counter() - start
            result = evaluate_ranking(
                lists, targets, histories, ks=(5, 10, 20), split="test", validation=validated
            )
            if model in RMSE_MODELS:
                predicted = [
                    recommender.predict(str(row.user_id), str(row.item_id))
                    for row in known_test.itertuples()
                ]
                result["proxy_rmse"] = proxy_rmse(known_test.proxy_score.tolist(), predicted)
                result["proxy_rmse_pairs"] = len(known_test)
            directory = out / model / f"seed_{seed}"
            directory.mkdir(parents=True)
            (directory / "evaluation.json").write_text(json.dumps(result) + "\n", encoding="utf-8")
            pd.DataFrame(records).to_csv(directory / "recommendations.csv", index=False)
            results[model][seed] = result
            timings[f"{model}/{seed}"] = seconds
            for k, values in result["at_k"].items():
                rows.append({"model": model, "seed": seed, "k": int(k), **values})
            print(f"{model} seed={seed} NDCG@10={result['at_k']['10']['ndcg']:.10f}", flush=True)
    pd.DataFrame(rows).to_csv(out / "metrics.csv", index=False)
    seed_summary = {m: summarize_test_seeds(r) for m, r in results.items() if len(r) > 1}
    (out / "seed_summary.json").write_text(json.dumps(seed_summary, indent=2) + "\n", "utf-8")
    meta = {
        "step": "4.5_test_once",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "lock_sha256": lock_hash,
        "lock_unchanged": sha256(out / "lock.json") == lock_hash,
        "input_sha256": {name: sha256(source / name) for name in names},
        "recommend_seconds": timings,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{
                name: importlib.metadata.version(name)
                for name in ["numpy", "scipy", "pandas", "pyarrow", "implicit"]
            },
        },
        "git_sha": lock["git_sha"],
        "git_status": subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        ).stdout,
        "command": sys.argv,
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
