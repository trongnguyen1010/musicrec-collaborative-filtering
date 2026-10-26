"""Run the frozen Step 15 grid and matching seed ablations; never fit the base or open test."""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.metadata  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from itertools import product  # noqa: E402
from pathlib import Path  # noqa: E402
from time import perf_counter  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import psutil  # noqa: E402
import yaml  # noqa: E402

from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.m1 import select_full_variant, within_drop  # noqa: E402
from musicrec.evaluation.ranking import evaluate_ranking  # noqa: E402
from musicrec.evaluation.validation import (  # noqa: E402
    _check_cohort,
    summarize_history_groups,
    summarize_seeds,
)
from musicrec.recommenders.implicit_als import ImplicitALSRecommender  # noqa: E402
from musicrec.recommenders.m1 import M1Recommender, rerank_candidates  # noqa: E402
from musicrec.recommenders.pure_svd import PureSVDRecommender  # noqa: E402

BASE_CLASSES = {"implicit_als": ImplicitALSRecommender, "pure_svd": PureSVDRecommender}


def main() -> None:
    """Save all outcomes, including infeasible configurations, in a new local run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/models/m1.yaml"))
    parser.add_argument("--evaluation-config", type=Path, default=Path("configs/evaluation.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    def guard(event: str, values: tuple) -> None:
        if event == "open" and isinstance(values[0], (str, bytes)):
            name = os.fsdecode(values[0])
            if Path(name).name == "test.parquet":
                raise RuntimeError("Step 15 must never open test.parquet, including hashing")

    sys.addaudithook(guard)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def read(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def write(path: Path, value: dict) -> None:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, allow_nan=False)
            handle.write("\n")

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    evaluation_config = yaml.safe_load(args.evaluation_config.read_text(encoding="utf-8"))
    expected = {
        "step": 15,
        "candidate_size": 100,
        "lambda_grid": [0.5, 0.75, 1.0],
        "beta_grid": [0.0, 0.1, 0.25, 0.5],
        "selection_seed": 42,
        "confirmation_seeds": [43, 44],
        "max_relative_ndcg_drop": 0.05,
        "ks": [5, 10, 20],
    }
    if any(config.get(k) != v for k, v in expected.items()):
        raise ValueError("Expected the predeclared Step 15 grid/seed/bound protocol")
    if evaluation_config["ks"] != config["ks"] or set(config["base_runs"]) != {42, 43, 44}:
        raise ValueError("Expected unchanged evaluator and three pinned base checkpoints")
    base_class = config.get("base_class", "implicit_als")
    if base_class not in BASE_CLASSES:
        raise ValueError("Expected an implicit_als or pure_svd base")
    source, out = Path(config["representations_run"]).resolve(), args.output_dir.resolve()
    sources = [source, *(Path(p).resolve() for p in config["base_runs"].values())]
    if out.exists() or any(out == p or p in out.parents for p in sources):
        raise ValueError("Output must be a new directory outside source runs")
    input_hashes = {}

    def pin(path: Path, expected_hash: str | None = None) -> None:
        actual = sha(path)
        if expected_hash is not None and actual != expected_hash:
            raise ValueError(f"Source checksum mismatch: {path}")
        input_hashes[str(path)] = actual

    metadata = read(source / "metrics.json")
    if metadata["step"] != 5 or metadata["seed"] != 42:
        raise ValueError("Expected the verified seed 42 representations")
    pin(source / "metrics.json")
    for name in ["train.parquet", "validation.parquet", "id_mappings.json", "transform.json"]:
        pin(source / name, metadata["output_sha256"][name])
    base_evaluations, base_metadata, verification = {}, {}, {}
    root = Path(__file__).resolve().parents[1]
    for seed, name in config["base_runs"].items():
        run = Path(name).resolve()
        info = read(run / "metrics.json")
        if (
            info["seed"] != seed
            or Path(info["source_run"]).resolve() != source
            or info["config"]["model"] != base_class
            or info["evaluation_config"] != evaluation_config
        ):
            raise ValueError("Expected matching base runs for every seed")
        # The ALS runs of 26/10 carry an independent audit; runs from the tuning
        # driver do not, and that absence is recorded instead of being hidden.
        if (run / "verification.json").exists():
            if not read(run / "verification.json")["all_checks_passed"]:
                raise ValueError("Base run failed its independent verification")
            pin(run / "verification.json")
            verification[seed] = "independent_audit_passed"
        else:
            verification[seed] = "not_available_runner_checks_only"
        for relative, digest in info["output_sha256"].items():
            pin(run / relative, digest)
        for relative, digest in info["code_sha256"].items():
            pin(run / "code" / relative, digest)
        pin(run / "metrics.json")
        for name in ["train.parquet", "validation.parquet", "id_mappings.json", "transform.json"]:
            if info["input_sha256"][name] != metadata["output_sha256"][name]:
                raise ValueError("Base model used different data")
        for relative in [f"{base_class}.py", "ranking.py"]:
            folder = "evaluation" if relative == "ranking.py" else "recommenders"
            if sha(root / "src/musicrec" / folder / relative) != info["code_sha256"][relative]:
                raise ValueError("Frozen base inference/evaluator code changed")
        base_evaluations[seed], base_metadata[seed] = read(run / "evaluation.json"), info
    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")
    interactions = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count))
        for r in train.itertuples(index=False)
    ]
    histories = {str(u): set(g["item_id"].astype(str)) for u, g in train.groupby("user_id")}
    targets = {
        u: set(validation.loc[validation["user_id"].astype(str) == u, "item_id"].astype(str))
        for u in histories
    }
    users = sorted(histories, key=int)
    lengths = {u: len(h) for u, h in histories.items()}
    out.mkdir(parents=True, exist_ok=False)
    write(out / "experiment.json", config)
    code = out / "code"
    code.mkdir()
    code_paths = [
        Path(__file__),
        args.config,
        args.evaluation_config,
        root / "src/musicrec/recommenders/m1.py",
        root / f"src/musicrec/recommenders/{base_class}.py",
        root / "src/musicrec/recommenders/base.py",
        root / "src/musicrec/data/contracts.py",
        root / "src/musicrec/evaluation/m1.py",
        root / "src/musicrec/evaluation/ranking.py",
        root / "src/musicrec/evaluation/validation.py",
        root / "tests/unit/test_m1.py",
    ]
    # Keep package-relative names: recommender and selection modules are both named m1.py.
    for path in code_paths:
        relative = path.resolve().relative_to(root)
        destination = code / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    code_hashes = {str(p.relative_to(code)): sha(p) for p in code.rglob("*") if p.is_file()}
    pin(args.config.resolve())
    pin(args.evaluation_config.resolve())
    all_evaluations, metric_rows, resources, group_rows = {}, [], {}, []
    winner = None
    matched = {}
    started = perf_counter()
    for seed in [42, 43, 44]:
        if seed != 42 and winner is None:
            break
        base_run = Path(config["base_runs"][seed])
        base = BASE_CLASSES[base_class].load(base_run / "model")
        if base.seed != seed or set(base._users) != set(users):
            raise ValueError("Loaded checkpoint does not match the seed/cohort")
        wrapper = M1Recommender(base, candidate_size=100).fit(interactions)
        parameters = (
            list(product(config["lambda_grid"], config["beta_grid"]))
            if seed == 42
            else list(matched.values())
        )
        seed_dir = out / f"seed_{seed}"
        seed_dir.mkdir()
        ranks = {pair: {} for pair in parameters}
        records = {pair: [] for pair in parameters}
        greedy_seconds = {pair: 0.0 for pair in parameters}
        candidate_rows, candidate_seconds, hit_count, target_count = [], [], 0, 0
        for user in users:
            tick = perf_counter()
            pool = wrapper.prepare_candidates(user, histories[user])
            candidate_seconds.append(perf_counter() - tick)
            candidate_rows.extend(
                {"user_id": user, "rank": rank, "item_id": r.item_id, "score": r.score}
                for rank, r in enumerate(pool.recommendations, 1)
            )
            catalog_targets = targets[user] & set(base._items)
            target_count += len(catalog_targets)
            hit_count += len(catalog_targets & {r.item_id for r in pool.recommendations})
            for pair in parameters:
                tick = perf_counter()
                recs = rerank_candidates(pool, 20, *pair)
                greedy_seconds[pair] += perf_counter() - tick
                ranks[pair][user] = [r.item_id for r in recs]
                records[pair].extend(
                    {
                        "user_id": user,
                        "rank": rank,
                        "item_id": r.item_id,
                        "score": r.score,
                        "reason": r.reason,
                    }
                    for rank, r in enumerate(recs, 1)
                )
        pd.DataFrame(candidate_rows).to_parquet(seed_dir / "candidates.parquet", index=False)
        seed_results = {}
        for pair in parameters:
            label = f"lambda_{pair[0]:g}_beta_{pair[1]:g}"
            directory = seed_dir / label
            directory.mkdir()
            tick = perf_counter()
            result = evaluate_ranking(ranks[pair], targets, histories, ks=(5, 10, 20))
            eval_seconds = perf_counter() - tick
            _check_cohort(result, base_evaluations[seed])
            seed_results[pair] = result
            write(directory / "evaluation.json", result)
            groups = summarize_history_groups(result, lengths)
            write(directory / "history_groups.json", groups)
            pd.DataFrame(records[pair]).to_csv(directory / "recommendations.csv", index=False)
            for k, metrics in result["at_k"].items():
                metric_rows.append(
                    {"seed": seed, "lambda": pair[0], "beta": pair[1], "k": int(k), **metrics}
                )
            for label_group, group in groups["groups"].items():
                for k, metrics in group["at_k"].items():
                    group_rows.append(
                        {
                            "seed": seed,
                            "lambda": pair[0],
                            "beta": pair[1],
                            "group": label_group,
                            "k": int(k),
                            "users_eligible": group["users_eligible"],
                            **metrics,
                        }
                    )
            print(
                f"seed={seed} {label} NDCG@10={result['at_k']['10']['ndcg']:.10f} "
                f"ARP={result['at_k']['10']['arp']:.6f}",
                flush=True,
            )
            resources[f"{seed}/{label}"] = {
                "greedy_seconds": greedy_seconds[pair],
                "evaluation_seconds": eval_seconds,
            }
        if seed_results[(1.0, 0.0)] != base_evaluations[seed]:
            raise RuntimeError("Identity M1 must exactly reproduce the frozen base evaluation")
        original = pd.read_csv(
            base_run / "recommendations.csv", dtype={"user_id": str, "item_id": str}
        )
        expected_ids = original.groupby("user_id", sort=False)["item_id"].apply(list).to_dict()
        if ranks[(1.0, 0.0)] != expected_ids:
            raise RuntimeError("Identity M1 changed baseline artist order")
        if seed == 42:
            rows = [
                {"lambda": p[0], "beta": p[1], **r["at_k"]["10"]} for p, r in seed_results.items()
            ]
            winner = select_full_variant(rows, base_evaluations[42]["at_k"]["10"]["ndcg"])
            if winner is not None:
                matched = {
                    "base": (1.0, 0.0),
                    "diversity_only": (winner["lambda"], 0.0),
                    "popularity_only": (1.0, winner["beta"]),
                    "full": (winner["lambda"], winner["beta"]),
                }
            write(
                out / "selection.json",
                {
                    "seed": 42,
                    "winner": winner,
                    "matching_ablations": matched,
                    "frozen_before_confirmation": True,
                },
            )
        all_evaluations[seed] = seed_results
        resources[f"{seed}/candidates"] = {
            "retrieval_and_train_features_seconds": sum(candidate_seconds),
            "mean_per_user_seconds": float(np.mean(candidate_seconds)),
            "p95_per_user_seconds": float(np.quantile(candidate_seconds, 0.95)),
            "candidate_target_recall_micro": hit_count / target_count,
            "targets_in_catalog": target_count,
            "targets_in_pool": hit_count,
        }
        if winner is not None:
            wrapper.lambda_weight, wrapper.beta = winner["lambda"], winner["beta"]
            wrapper.save(seed_dir / "selected_model")
            restored = M1Recommender.load(seed_dir / "selected_model", base=base)
            tick = perf_counter()
            for user in users:
                actual = restored.recommend(user, 20, histories[user])
                if [r.item_id for r in actual] != ranks[matched["full"]][user]:
                    raise RuntimeError("Reload changed selected recommendations")
            resources[f"{seed}/reload"] = {"users": len(users), "seconds": perf_counter() - tick}
    summaries, confirmation = {}, {"passed": False, "reason": "no_feasible_full_variant"}
    if winner is not None:
        for name, pair in matched.items():
            summaries[name] = summarize_seeds({s: all_evaluations[s][pair] for s in [42, 43, 44]})
        per_seed = {
            s: within_drop(
                all_evaluations[s][matched["full"]]["at_k"]["10"]["ndcg"],
                base_evaluations[s]["at_k"]["10"]["ndcg"],
            )
            for s in [42, 43, 44]
        }
        mean_passed = within_drop(
            summaries["full"]["at_k"]["10"]["ndcg"]["mean"],
            summaries["base"]["at_k"]["10"]["ndcg"]["mean"],
        )
        confirmation = {
            "passed": all(per_seed.values()) and mean_passed,
            "per_seed_passed": per_seed,
            "mean_passed": mean_passed,
            "no_retuning": True,
            "selection_seed_is_not_independent_confirmation": True,
        }
    write(out / "seed_summary.json", summaries)
    pd.DataFrame(metric_rows).to_csv(out / "metrics.csv", index=False)
    pd.DataFrame(group_rows).to_csv(out / "history_groups.csv", index=False)
    if any(sha(Path(p)) != digest for p, digest in input_hashes.items()):
        raise RuntimeError("A pinned source/config changed during execution")
    peak = psutil.Process().memory_info()
    peak_bytes = peak.peak_wset if sys.platform == "win32" else None
    write(
        out / "metrics.json",
        {
            "step": 15,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "config": config,
            "evaluation_config": evaluation_config,
            "selection": winner,
            "confirmation": confirmation,
            "variant_seed_evaluations": len(all_evaluations[42])
            + sum(len(v) for s, v in all_evaluations.items() if s != 42),
            "resources": resources,
            "whole_run_seconds": perf_counter() - started,
            "process_peak_working_set_bytes": peak_bytes,
            "memory_scope": "whole process including candidate rows, all grid results and reload",
            "input_sha256": input_hashes,
            "inputs_unchanged": True,
            "test_file_read": False,
            "base_class": base_class,
            "base_fit_calls": 0,
            "base_verification": verification,
            "code_sha256": code_hashes,
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "git_status": subprocess.check_output(["git", "status", "--short"], text=True),
            "git_diff_sha256": hashlib.sha256(subprocess.check_output(["git", "diff"])).hexdigest(),
            "runtime": {
                "python": sys.version,
                **{
                    name: importlib.metadata.version(name)
                    for name in ["numpy", "scipy", "pandas", "implicit", "pyarrow"]
                },
            },
            "command": sys.argv,
            "output_sha256": {
                str(p.relative_to(out)): sha(p)
                for p in out.rglob("*")
                if p.is_file() and code not in p.parents
            },
        },
    )
    print(json.dumps({"selection": winner, "confirmation": confirmation}), flush=True)


if __name__ == "__main__":
    main()
