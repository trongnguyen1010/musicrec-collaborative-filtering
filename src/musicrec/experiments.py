"""Train and tune thesis baselines on validation without opening test metrics."""

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from musicrec.configuration import ROOT, read_config, sha256, write_json
from musicrec.evaluation.evaluator import evaluate, histories
from musicrec.evaluation.ranking import ndcg_at_k
from musicrec.pipeline import (
    git_state,
    interactions_from_frame,
    runtime_environment,
    snapshot_sources,
)
from musicrec.recommenders.models import MatrixModel, make_model, top_indices


def validation_ndcg(
    model: MatrixModel, train: pd.DataFrame, validation: pd.DataFrame, k: int = 10
) -> float:
    """Fast selection metric; identical target/mask/tie rules as the shared evaluator."""
    seen = histories(train)
    truth = histories(validation)
    values = []
    for user, relevant in truth.items():
        scores = model.scores(user).copy()
        for item in seen.get(user, set()):
            scores[model.item_index[item]] = -np.inf
        ids = [model.items[i] for i in top_indices(scores, k)]
        values.append(ndcg_at_k(ids, relevant, k))
    return float(np.mean(values))


def trial_configs(kind: str, settings: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    """Use a declared, reproducible small random-search budget within the 30-trial cap."""
    budget = int(settings["trials_per_family"])
    if not 1 <= budget <= 30:
        raise ValueError("Trial budget must be in 1..30")
    rng = np.random.default_rng(seed)
    configs = []
    for trial in range(budget):
        params: dict[str, Any] = {"seed": seed}
        if kind in ("user_cf", "item_cf"):
            params.update(
                neighbors=int(rng.choice(settings["neighbors"])),
                shrinkage=float(rng.choice(settings["shrinkage"])),
                min_common=int(rng.choice(settings["min_common"])),
            )
        else:
            dims = settings["factors"]
            params["factors"] = int(dims[trial % len(dims)])
            if kind in ("svd", "bpr"):
                params.update(
                    learning_rate=float(np.exp(rng.uniform(*np.log(settings["learning_rate"])))),
                    regularization=float(np.exp(rng.uniform(*np.log(settings["regularization"])))),
                    epochs=int(settings["epochs"]),
                    patience=int(settings["patience"]),
                    batch_size=int(settings["batch_size"]),
                )
        if params not in configs:
            configs.append(params)
    return configs


def run_study(data_run: Path, config: dict[str, Any], run_id: str | None = None) -> Path:
    """Tune, persist selected seeds and evaluate validation for six new baselines."""
    identity = run_id or datetime.now(UTC).strftime("study_%Y%m%dT%H%M%S_%fZ")
    if Path(identity).name != identity or identity in (".", ".."):
        raise ValueError("Invalid run ID")
    out = ROOT / str(config["output"]["runs_dir"]) / identity
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "config.json", config)
    train = pd.read_parquet(data_run / "train.parquet")
    val = pd.read_parquet(data_run / "validation.parquet")
    interactions = interactions_from_frame(train)
    settings = config["experiment"]
    seed = int(config["project"]["seed"])
    manifest = {
        "data_run": str(data_run.relative_to(ROOT)),
        "data_manifest_hash": sha256(data_run / "manifest.json"),
        **git_state(),
        "test_evaluated": False,
        "status": "running",
    }
    write_json(out / "provenance.json", manifest)
    write_json(out / "source_snapshot.json", {"sha256": snapshot_sources(out)})
    write_json(out / "environment.json", runtime_environment())
    summary = {}
    with threadpool_limits(limits=1):
        for kind in settings["models"]:
            print(f"Tuning {kind}", flush=True)
            folder = out / kind
            folder.mkdir()
            trials = [{"seed": seed}] if kind == "random" else trial_configs(kind, settings, seed)
            best = -np.inf
            best_model = None
            best_params = None
            for index, params in enumerate(trials):
                start = time.perf_counter()
                model = make_model(kind, params)
                if kind in ("svd", "bpr"):
                    model.monitor = lambda m=model: validation_ndcg(m, train, val)
                model.fit(interactions)
                value = validation_ndcg(model, train, val)
                elapsed = time.perf_counter() - start
                write_json(
                    folder / f"trial_{index:02}.json",
                    {
                        "params": params,
                        "validation_ndcg_at_10": value,
                        "seconds": elapsed,
                        "history": model.history,
                    },
                )
                print(f"  trial {index}: NDCG@10={value:.6f}, {elapsed:.1f}s", flush=True)
                if value > best + 1e-12:
                    best = value
                    best_model = model
                    best_params = params
            if best_model is None or best_params is None:
                raise RuntimeError("No successful trial")
            write_json(
                folder / "selected.json",
                {
                    "params": best_params,
                    "validation_ndcg_at_10": best,
                    "selection": "highest_validation_ndcg_then_first_trial",
                    "trials": len(trials),
                },
            )
            seeds = (
                settings["model_seeds"] if kind in ("svd", "bpr", "pure_svd", "random") else [seed]
            )
            for model_seed in seeds:
                selected = best_model
                if model_seed != seed:
                    selected = make_model(kind, {**best_params, "seed": int(model_seed)})
                    if kind in ("svd", "bpr"):
                        selected.monitor = lambda m=selected: validation_ndcg(m, train, val)
                    selected.fit(interactions)
                destination = folder / f"seed_{model_seed}"
                destination.mkdir()
                selected.save(destination / "model.npz")
                loaded = MatrixModel.load(destination / "model.npz")
                for user in list(histories(val))[:10]:
                    if loaded.recommend(user, 20, set()) != selected.recommend(user, 20, set()):
                        raise RuntimeError("Model roundtrip changed ranking")
                metrics, predictions, user_metrics = evaluate(
                    loaded, train, val, config["evaluation"]["ks"]
                )
                write_json(destination / "validation_metrics.json", metrics)
                predictions.to_parquet(destination / "validation_predictions.parquet", index=False)
                user_metrics.to_csv(destination / "validation_users.csv", index=False)
                write_json(destination / "training_history.json", selected.history)
            summary[kind] = {"validation_ndcg_at_10": best, "params": best_params}
            write_json(folder / "completed.json", {"kind": kind, "seeds": seeds})
    write_json(out / "validation_summary.json", summary)
    write_json(
        out / "manifest.json",
        {
            **manifest,
            "status": "completed",
            "artifacts": {
                str(p.relative_to(out)): sha256(p) for p in sorted(out.rglob("*")) if p.is_file()
            },
        },
    )
    return out


def main() -> None:
    """CLI for validation-only baseline tuning."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-run", required=True)
    parser.add_argument("--config", default="params.yaml")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    print(run_study(ROOT / args.data_run, read_config(args.config), args.run_id))


if __name__ == "__main__":
    main()
