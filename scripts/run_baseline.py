"""Shared CLI I/O for one authorized validation baseline at a time."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from math import fsum, isclose
from pathlib import Path
from time import perf_counter
from typing import Literal

import pandas as pd
import yaml

from musicrec.data.contracts import Interaction
from musicrec.evaluation.ranking import evaluate_ranking, ndcg_at_k, proxy_rmse
from musicrec.recommenders.base import Recommender
from musicrec.recommenders.item_cf import ItemCFRecommender
from musicrec.recommenders.popularity import PopularityRecommender
from musicrec.recommenders.pure_svd import PureSVDRecommender
from musicrec.recommenders.random import RandomRecommender
from musicrec.recommenders.svd import SVDRecommender
from musicrec.recommenders.user_cf import UserCFRecommender


def main(
    model_name: Literal["random", "popularity", "user_cf", "item_cf", "svd", "pure_svd"],
) -> None:
    """Verify source hashes, fit the train catalog and persist validation evidence."""
    proxy_model = model_name in ("user_cf", "item_cf", "svd", "pure_svd")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--representations-run" if proxy_model else "--split-run",
        dest="source_run",
        type=Path,
        required=True,
    )
    parser.add_argument("--config", type=Path, default=Path(f"configs/models/{model_name}.yaml"))
    parser.add_argument("--evaluation-config", type=Path, default=Path("configs/evaluation.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.source_run.resolve(), args.output_dir.resolve()
    if out.exists() or source == out or source in out.parents:
        raise ValueError("Output must be a new directory outside the split run")

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    metadata_path = source / "metrics.json"
    metadata_hash = sha256(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    names = ["train.parquet", "validation.parquet", "id_mappings.json"]
    if proxy_model:
        names.append("transform.json")
    recorded = metadata.get("output_sha256", {})
    source_step = 5 if proxy_model else 4
    if (
        metadata.get("step") != source_step
        or metadata.get("seed") != 42
        or not set(names) <= recorded.keys()
    ):
        raise ValueError(
            f"Expected a verified Step {source_step} run with seed 42 and input hashes"
        )
    input_hashes = {name: recorded[name] for name in names}
    for name, value in input_hashes.items():
        if sha256(source / name) != value:
            raise ValueError(f"Input checksum mismatch: {name}")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    expected_config = (
        {
            "model": "random",
            "seed": 42,
            "generator": "python_random_shuffle_per_user",
            "user_seed": "musicrec-random-v1:{seed}:{user_id}",
            "catalog_order": "numeric_train_item_id",
            "score": "descending_full_permutation_rank",
        }
        if model_name == "random"
        else {
            "model": "popularity",
            "seed": 42,
            "seed_role": "split_provenance_only",
            "score": "sum_log2_1p_listening_count",
            "fit_scope": "train_only",
            "tie_break": "numeric_train_item_id",
        }
    )
    if model_name == "user_cf":
        expected_config = {
            "model": "user_cf",
            "seed": 42,
            "seed_role": "split_provenance_only",
            "neighbors": 40,
            "shrinkage": 0,
            "similarity": "full_proxy_vector_cosine",
            "minimum_common_artists": 1,
            "neighbor_selection": "global_top_l_then_item_filter",
            "prediction": "user_mean_plus_weighted_neighbor_deviation",
            "known_user_fallback": "observed_user_mean",
            "unknown_user_fallback": "observed_global_mean",
            "score_clipping": "none",
            "tie_break": "numeric_train_mapping_order",
            "numeric_tie_decimals": 12,
            "fit_scope": "train_only",
        }
    if model_name == "item_cf":
        expected_config = {
            "model": "item_cf",
            "seed": 42,
            "seed_role": "split_provenance_only",
            "neighbors": 40,
            "shrinkage": 0,
            "similarity": "full_proxy_vector_cosine",
            "minimum_common_users": 1,
            "neighbor_selection": "global_target_top_l_then_history_filter",
            "prediction": "similarity_weighted_observed_proxy_mean",
            "known_user_fallback": "observed_user_mean",
            "unknown_user_fallback": "observed_global_mean",
            "score_clipping": "none",
            "tie_break": "numeric_train_mapping_order",
            "numeric_tie_decimals": 12,
            "fit_scope": "train_only",
        }
    if model_name == "svd":
        expected_config = {
            "model": "svd",
            "seed": 42,
            "seed_role": "initialization_and_epoch_shuffle",
            "latent_factors": 32,
            "learning_rate": 0.005,
            "regularization": 0.02,
            "max_epochs": 100,
            "patience": 5,
            "init_std": 0.1,
            "initializer": "numpy_pcg64_normal_zero_mean",
            "optimizer": "sequential_observed_pair_sgd_simultaneous_factor_updates",
            "training_order": "numeric_user_item_then_rng_permutation_each_epoch",
            "objective": "half_sum_observed_squared_error_plus_per_observation_l2",
            "global_mean": "fixed_observed_train_proxy_mean",
            "initial_biases": "zero",
            "selection_metric": "ndcg_at_10_validation_every_epoch",
            "selection_ties": "earliest_epoch",
            "min_delta": 0,
            "restore_best_checkpoint": True,
            "unknown_user_fallback": "global_mean_plus_learned_item_bias",
            "score_clipping": "none",
            "tie_break": "numeric_train_mapping_order",
            "numeric_tie_decimals": 12,
            "blas_threads": 1,
            "fit_scope": "train_only_validation_selects_epoch",
        }
    if model_name == "pure_svd":
        expected_config = {
            "model": "pure_svd",
            "seed": 42,
            "seed_role": "arpack_start_vector",
            "latent_factors": 32,
            "representation": "prepared_train_proxy_score",
            "missing_entries": "algebraic_zero_not_observed_dislike",
            "centering": "none",
            "normalization": "none",
            "biases": "none",
            "solver": "scipy_sparse_svds_arpack",
            "which": "LM",
            "tolerance": 1e-10,
            "max_iter": 10000,
            "ncv": "scipy_default",
            "start_vector": "pcg64_standard_normal_min_dimension",
            "singular_value_order": "descending",
            "sign_rule": "largest_absolute_component_entry_positive",
            "score": "train_row_times_right_subspace_projector",
            "unknown_user_fallback": "zero_profile_numeric_mapping_order",
            "score_clipping": "none",
            "tie_break": "numeric_train_mapping_order",
            "numeric_tie_decimals": 12,
            "blas_threads": 1,
            "fit_scope": "train_only_no_validation_epoch_selection",
        }
    if config != expected_config:
        raise ValueError(f"Expected the agreed {model_name} validation configuration")
    evaluation_config = yaml.safe_load(args.evaluation_config.read_text(encoding="utf-8"))
    if evaluation_config["ks"] != [5, 10, 20]:
        raise ValueError("Expected the shared cutoffs 5, 10, 20")
    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")
    mappings = json.loads((source / "id_mappings.json").read_text(encoding="utf-8"))
    for column in ["user_id", "item_id"]:
        expected = {value: index for index, value in enumerate(sorted(set(train[column]), key=int))}
        if mappings[f"{column}_to_index"] != expected:
            raise ValueError("Mappings must match the numeric train-only catalog and users")
        for frame in [train, validation]:
            actual = frame[column.replace("_id", "_index")].astype("Int64")
            if not frame[column].map(expected).astype("Int64").equals(actual):
                raise ValueError("Split indices do not match train mappings")
    for frame in [train, validation]:
        if frame.empty or frame.duplicated(["user_id", "item_id"]).any():
            raise ValueError("Expected non-empty splits with unique user-artist pairs")
    if set(validation.user_id) != set(train.user_id):
        raise ValueError("Validation must retain exactly the train users")
    histories = {user: set(group.item_id) for user, group in train.groupby("user_id")}
    targets = {user: set(group.item_id) for user, group in validation.groupby("user_id")}
    interactions = [
        Interaction(
            row.user_id,
            row.item_id,
            float(row.listening_count),
            float(row.proxy_score) if proxy_model else None,
        )
        for row in train.itertuples(index=False)
    ]
    model: Recommender = (
        RandomRecommender(seed=config["seed"])
        if model_name == "random"
        else PopularityRecommender()
    )
    if model_name == "user_cf":
        model = UserCFRecommender(neighbors=config["neighbors"], shrinkage=config["shrinkage"])
    if model_name == "item_cf":
        model = ItemCFRecommender(neighbors=config["neighbors"], shrinkage=config["shrinkage"])
    if model_name == "svd":
        model = SVDRecommender(
            **{
                name: config[name]
                for name in [
                    "latent_factors",
                    "learning_rate",
                    "regularization",
                    "max_epochs",
                    "patience",
                    "seed",
                    "init_std",
                ]
            }
        )
    if model_name == "pure_svd":
        model = PureSVDRecommender(
            **{name: config[name] for name in ["latent_factors", "seed", "tolerance", "max_iter"]}
        )
    monitor_seconds = []

    def validation_ndcg(current: SVDRecommender) -> float:
        start_monitor = perf_counter()
        catalog = set(mappings["item_id_to_index"])
        values = []
        for user in sorted(histories, key=int):
            relevant = targets[user] & catalog
            if relevant:
                recs = current.recommend(user, 10, histories[user])
                values.append(ndcg_at_k([item.item_id for item in recs], relevant, 10))
        if not values:
            raise ValueError("Epoch selection requires eligible validation users")
        score = fsum(values) / len(values)
        monitor_seconds.append(perf_counter() - start_monitor)
        print(
            json.dumps({"epoch": len(current.learning_curve) + 1, "validation_ndcg_at_10": score}),
            flush=True,
        )
        return score

    start = perf_counter()
    if isinstance(model, SVDRecommender):
        model.fit(interactions, validation_score=validation_ndcg)
    else:
        model.fit(interactions)
    fit_total_seconds = perf_counter() - start
    fit_seconds = fit_total_seconds - sum(monitor_seconds)
    lists, rows, latencies, recorded_recommendations = {}, [], [], {}
    for user in sorted(histories, key=int):
        start = perf_counter()
        recommended = model.recommend(user, max(evaluation_config["ks"]), histories[user])
        latencies.append(perf_counter() - start)
        lists[user] = [item.item_id for item in recommended]
        recorded_recommendations[user] = recommended
        rows.extend(
            {
                "user_id": user,
                "rank": rank,
                "item_id": item.item_id,
                "score": item.score,
                "reason": item.reason,
            }
            for rank, item in enumerate(recommended, start=1)
        )
    start = perf_counter()
    result = evaluate_ranking(lists, targets, histories, ks=tuple(evaluation_config["ks"]))
    evaluator_seconds = perf_counter() - start
    supplementary = {}
    if isinstance(model, SVDRecommender):
        best_score = model.learning_curve[model.best_epoch - 1]["validation_ndcg_at_10"]
        if not isclose(result["at_k"]["10"]["ndcg"], best_score, rel_tol=0, abs_tol=1e-15):
            raise RuntimeError("Restored checkpoint disagrees with selected validation epoch")
        supplementary.update(
            {
                "best_epoch": model.best_epoch,
                "epochs_completed": len(model.learning_curve),
                "best_validation_ndcg_at_10": best_score,
                "stop_reason": model.stop_reason,
                "fit_including_validation_seconds": fit_total_seconds,
                "validation_monitor_seconds": sum(monitor_seconds),
            }
        )
    if isinstance(model, PureSVDRecommender):
        supplementary.update(
            {
                "fit_diagnostics": model.fit_diagnostics,
                "rmse_not_applicable": "association_scores_are_not_calibrated_proxy_ratings",
            }
        )
    if proxy_model and model_name != "pure_svd":
        known_targets = validation[validation.item_index.notna()]
        start = perf_counter()
        predicted = [
            model.predict(row.user_id, row.item_id) for row in known_targets.itertuples(index=False)
        ]
        supplementary.update(
            {
                "proxy_rmse": proxy_rmse(known_targets.proxy_score.tolist(), predicted),
                "proxy_rmse_pairs": len(known_targets),
                "proxy_rmse_outside_catalog_excluded": int(validation.item_index.isna().sum()),
                "proxy_rmse_seconds": perf_counter() - start,
                "prediction_clipping": "none",
            }
        )
    out.mkdir(parents=True, exist_ok=False)

    def write_json(name: str, value: object) -> None:
        with (out / name).open("x", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")

    pd.DataFrame(rows).to_csv(out / "recommendations.csv", index=False, lineterminator="\n")
    pd.DataFrame([{"k": k, **values} for k, values in result["at_k"].items()]).to_csv(
        out / "metrics.csv",
        index=False,
        lineterminator="\n",
    )
    write_json("evaluation.json", result)
    state = {
        "model": model_name,
        "config": config,
        "catalog": sorted(mappings["item_id_to_index"], key=int),
        "known_users": sorted(histories, key=int),
        "learned_values": "catalog/user IDs only; no learned preferences or count statistics",
    }
    if model_name == "popularity":
        state["learned_values"] = "per-artist sum of log2(1 + raw train count); no user factors"
        state["scores"] = {item: model.predict("offline", item) for item in state["catalog"]}
    if isinstance(
        model, (UserCFRecommender, ItemCFRecommender, SVDRecommender, PureSVDRecommender)
    ):
        model.save(out / "model")
        start = perf_counter()
        restored = type(model).load(out / "model")
        for user in sorted(histories, key=int):
            if (
                restored.recommend(user, max(evaluation_config["ks"]), histories[user])
                != recorded_recommendations[user]
            ):
                raise RuntimeError(f"{model_name} reload changed validation recommendations")
        supplementary["reload_verified_users"] = len(histories)
        supplementary["reload_verification_seconds"] = perf_counter() - start
        state["learned_values"] = "train proxy CSR, observed means and top-L cosine neighbors"
        if isinstance(model, SVDRecommender):
            state["learned_values"] = (
                "train proxy CSR, global mean, user/item biases and factors; best validation epoch"
            )
            pd.DataFrame(model.learning_curve).to_csv(
                out / "learning_curve.csv", index=False, lineterminator="\n"
            )
        if isinstance(model, PureSVDRecommender):
            state["learned_values"] = (
                "train proxy CSR, leading right singular vectors and projected histories; no biases"
            )
        state["artifact_directory"] = "model"
        shutil.copyfile(source / "transform.json", out / "transform.json")
    write_json("model.json", state)
    shutil.copyfile(source / "id_mappings.json", out / "id_mappings.json")
    root = Path(__file__).resolve().parents[1]
    code = out / "code"
    code.mkdir()
    for path in [
        Path(__file__),
        root / f"scripts/run_{model_name}.py",
        root / f"src/musicrec/recommenders/{model_name}.py",
        root / "src/musicrec/recommenders/base.py",
        root / "src/musicrec/data/contracts.py",
        root / "src/musicrec/evaluation/ranking.py",
        root / f"tests/unit/test_{model_name}.py",
        args.config,
        args.evaluation_config,
    ]:
        shutil.copyfile(path, code / path.name)
    unchanged = sha256(metadata_path) == metadata_hash and all(
        sha256(source / name) == value for name, value in input_hashes.items()
    )
    if not unchanged:
        raise RuntimeError("Split inputs changed during the run")
    write_json(
        "metrics.json",
        {
            "step": {
                "random": 7,
                "popularity": 8,
                "user_cf": 9,
                "item_cf": 10,
                "svd": 11,
                "pure_svd": 12,
            }[model_name],
            "scope": f"{model_name} on validation only; no tuning or test evaluation",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "seed": config["seed"],
            "source_run": str(source),
            "source_metrics_sha256": metadata_hash,
            "input_sha256": input_hashes,
            "inputs_unchanged": unchanged,
            "test_file_read": False,
            "config": config,
            "evaluation_config": evaluation_config,
            "users_total": result["users_total"],
            "users_eligible": result["users_eligible"],
            "users_without_catalog_targets": result["users_without_catalog_targets"],
            "targets_total": result["targets_total"],
            "targets_outside_catalog": result["targets_outside_catalog"],
            "catalog_size": result["catalog_size"],
            "at_k": result["at_k"],
            "supplementary": supplementary,
            "timing_seconds": {
                "fit": fit_seconds,
                "recommend_total": sum(latencies),
                "recommend_mean_per_user": sum(latencies) / len(latencies),
                "recommend_p95_per_user": float(pd.Series(latencies).quantile(0.95)),
                "evaluation": evaluator_seconds,
            },
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
            "git_status": subprocess.check_output(["git", "status", "--porcelain"]).decode(),
            "git_diff_sha256": hashlib.sha256(
                subprocess.check_output(
                    ["git", "diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD"]
                )
            ).hexdigest(),
            "runtime": {
                "python": platform.python_version(),
                "blas_thread_environment": {
                    name: os.environ.get(name)
                    for name in [
                        "OPENBLAS_NUM_THREADS",
                        "MKL_NUM_THREADS",
                        "OMP_NUM_THREADS",
                        "BLIS_NUM_THREADS",
                    ]
                }
                if model_name in ("svd", "pure_svd")
                else None,
                **{
                    name: importlib.metadata.version(name)
                    for name in ["pandas", "numpy", "pyarrow", "scipy"]
                },
            },
            "command": sys.argv,
            "output_sha256": {
                path.relative_to(out).as_posix(): sha256(path)
                for path in sorted(out.rglob("*"))
                if path.is_file() and code not in path.parents
            },
            "code_sha256": {path.name: sha256(path) for path in sorted(code.iterdir())},
        },
    )
    print(json.dumps({"run": str(out), "validation_metrics": result["at_k"]}))
