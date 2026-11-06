"""Run H1 round 1 on validation seed 42; never fit ALS, never open test.

Spectral H1 (global and deviation-gated gamma) and the direct popularity-penalty control
are scored on the pinned Chapter 4 ALS checkpoint, then the agreed development gate locks
at most one configuration per family. Seed 43/44 confirmation and the test pass are not
implemented here yet (TODO, see DAC_TA_H1_THONG_NHAT_SAU_DEBATE.md sections 6.7 and 7).
"""

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
from pathlib import Path  # noqa: E402
from time import perf_counter  # noqa: E402
from typing import Any  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import psutil  # type: ignore[import-untyped]  # noqa: E402
import yaml  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.exposure import (  # noqa: E402
    head_split,
    mean_defined,
    non_head_exposure,
    popularity_alignment,
)
from musicrec.evaluation.h1_gate import apply_gate  # noqa: E402
from musicrec.evaluation.inference import joint_test, resample_indices  # noqa: E402
from musicrec.evaluation.ranking import evaluate_ranking  # noqa: E402
from musicrec.recommenders.base import Recommender  # noqa: E402
from musicrec.recommenders.direct_penalty import DirectPenaltyRecommender  # noqa: E402
from musicrec.recommenders.implicit_als import ImplicitALSRecommender  # noqa: E402
from musicrec.recommenders.spectral import SpectralDebiasRecommender  # noqa: E402

EXPECTED = {
    "model": "h1_spectral",
    "base_class": "implicit_als",
    "selection_seed": 42,
    "confirmation_seeds": [43, 44],
    "gamma_modes": ["global", "deviation"],
    "gamma0_grid": [0.0, 0.1, 0.25, 0.5, 0.75, 1.0],
    "direct_beta_grid": [0.0, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    "head_share": 0.2,
    "primary_k": 10,
    "max_relative_ndcg_drop": 0.05,
    "epsilon": 1.0e-12,
    "ks": [5, 10, 20],
    "bootstrap": {"resamples": 10000, "seed": 42},
}


def main() -> None:
    """Save every configuration's outcome, including infeasible ones, in a new local run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/models/h1.yaml"))
    parser.add_argument("--evaluation-config", type=Path, default=Path("configs/evaluation.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--max-configs", type=int, help="Timing trial only: at most N non-base configurations"
    )
    args = parser.parse_args()
    # A user sample would shrink the train catalog the evaluator derives, so timing trials
    # keep every user and only limit the number of configurations.
    sample = args.max_configs is not None

    def guard(event: str, values: tuple[object, ...]) -> None:
        if event == "open" and isinstance(values[0], (str, bytes)):
            if Path(os.fsdecode(values[0])).name == "test.parquet":
                raise RuntimeError("H1 round 1 must never open test.parquet, including hashing")

    sys.addaudithook(guard)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def read(path: Path) -> dict[str, Any]:
        value: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return value

    def write(path: Path, value: dict[str, Any]) -> None:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, allow_nan=False)
            handle.write("\n")

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    evaluation_config = yaml.safe_load(args.evaluation_config.read_text(encoding="utf-8"))
    if any(config.get(k) != v for k, v in EXPECTED.items()):
        raise ValueError("Expected the predeclared H1 round 1 grid/seed/bound protocol")
    if evaluation_config["ks"] != config["ks"] or set(config["base_runs"]) != {42, 43, 44}:
        raise ValueError("Expected unchanged evaluator and three pinned base checkpoints")
    root = Path(__file__).resolve().parents[1]
    source, out = Path(config["representations_run"]).resolve(), args.output_dir.resolve()
    base_run = Path(config["base_runs"][42]).resolve()
    if out.exists() or any(out == p or p in out.parents for p in [source, base_run]):
        raise ValueError("Output must be a new directory outside source runs")
    input_hashes: dict[str, str] = {}

    def pin(path: Path, expected_hash: str | None = None) -> None:
        actual = sha(path)
        if expected_hash is not None and actual != expected_hash:
            raise ValueError(f"Source checksum mismatch: {path}")
        input_hashes[str(path)] = actual

    # The lock records cloud paths; local copies are accepted only through equal hashes.
    lock_path = Path(config["lock"]).resolve()
    pin(lock_path)
    locked = read(lock_path)["models"]["implicit_als"]
    if locked["selected"] != {"latent_factors": 32, "regularization": 0.1, "confidence_scale": 1}:
        raise ValueError("The lock does not describe the Chapter 4 ALS configuration")
    metadata = read(source / "metrics.json")
    if metadata["step"] != 5 or metadata["seed"] != 42:
        raise ValueError("Expected the verified seed 42 representations")
    pin(source / "metrics.json")
    for name in ["train.parquet", "validation.parquet", "id_mappings.json", "transform.json"]:
        pin(source / name, metadata["output_sha256"][name])
    run_lock = locked["runs"]["42"]
    pin(base_run / "metrics.json", run_lock["metrics_sha256"])
    for name, digest in run_lock["model_sha256"].items():
        pin(base_run / "model" / name, digest)
    info = read(base_run / "metrics.json")
    if info["seed"] != 42 or info["config"]["model"] != "implicit_als":
        raise ValueError("Expected the seed 42 implicit ALS run")
    if info["evaluation_config"] != evaluation_config:
        raise ValueError("The evaluator protocol changed since the base run")
    for name in ["train.parquet", "validation.parquet", "id_mappings.json", "transform.json"]:
        if info["input_sha256"][name] != metadata["output_sha256"][name]:
            raise ValueError("Base model used different data")
    # The base ran on Linux; a Windows checkout may hold the same code with CRLF endings.
    for relative, folder in [("implicit_als.py", "recommenders"), ("ranking.py", "evaluation")]:
        text = (root / "src/musicrec" / folder / relative).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(text).hexdigest() != info["code_sha256"][relative]:
            raise ValueError("Frozen base inference/evaluator code changed")
    pin(base_run / "evaluation.json")
    pin(base_run / "recommendations.csv")

    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")
    interactions = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count))  # type: ignore[arg-type]
        for r in train.itertuples(index=False)
    ]
    all_histories = {str(u): set(g["item_id"].astype(str)) for u, g in train.groupby("user_id")}
    grouped = validation.groupby(validation["user_id"].astype(str))["item_id"]
    held = {u: set(items.astype(str)) for u, items in grouped}
    all_users = sorted(all_histories, key=int)
    users = all_users
    histories = {u: all_histories[u] for u in users}
    targets = {u: held.get(u, set()) for u in users}

    started = perf_counter()
    tick = perf_counter()
    base = ImplicitALSRecommender.load(base_run / "model")
    if base.seed != 42 or set(base._users) != set(all_users):
        raise ValueError("Loaded checkpoint does not match the seed/cohort")
    resources: dict[str, dict[str, float]] = {"load": {"seconds": perf_counter() - tick}}
    tick = perf_counter()
    spectral = SpectralDebiasRecommender(base, mode="deviation").fit(interactions)
    resources["spectral_context_and_gate"] = {"seconds": perf_counter() - tick}
    tick = perf_counter()
    direct = DirectPenaltyRecommender(base).fit(interactions)
    resources["direct_context"] = {"seconds": perf_counter() - tick}

    listeners = {item: int(n) for item, n in zip(base._items, spectral.listeners, strict=True)}
    popularity = {item: float(p) for item, p in zip(base._items, spectral.popularity, strict=True)}
    split = head_split(listeners, config["head_share"])
    singular = spectral.spectrum.singular_values
    p64, q64 = (base._user_factors.astype(np.float64), base._item_factors.astype(np.float64))
    balance = np.linalg.norm(p64.T @ p64 - q64.T @ q64) / np.linalg.norm(q64.T @ q64)
    weights = spectral.weights
    audit = {
        "descriptive_only_no_threshold_gate": True,
        "singular_values_top5": [float(s) for s in singular[:5]],
        "sigma1_minus_sigma2": float(singular[0] - singular[1]),
        "sigma1_over_sigma2": float(singular[0] / singular[1]),
        "sigma1_energy_share": float(singular[0] ** 2 / np.sum(singular**2)),
        "factor_balance_relative_frobenius": float(balance),
        "spearman_r1_train_listeners": float(
            spearmanr(spectral.spectrum.right, spectral.listeners).statistic
        ),
        "gate": {
            "d_ref": spectral.d_ref,
            "users_with_positive_deviation": int(np.count_nonzero(weights > 0)),
            "users_at_full_strength": int(np.count_nonzero(weights == 1)),
            "users_total": len(weights),
            "weight_quantiles": {
                str(q): float(np.quantile(weights, q)) for q in [0.1, 0.25, 0.5, 0.75, 0.9]
            },
            "no_positive_deviation": spectral.d_ref is None,
        },
        "non_head_split": split.summary(),
    }

    out.mkdir(parents=True, exist_ok=False)
    write(out / "experiment.json", {**config, "sample": sample})
    code = out / "code"
    code_paths = [
        Path(__file__),
        args.config,
        args.evaluation_config,
        root / "src/musicrec/recommenders/spectral.py",
        root / "src/musicrec/recommenders/direct_penalty.py",
        root / "src/musicrec/recommenders/implicit_als.py",
        root / "src/musicrec/recommenders/base.py",
        root / "src/musicrec/data/contracts.py",
        root / "src/musicrec/evaluation/exposure.py",
        root / "src/musicrec/evaluation/h1_gate.py",
        root / "src/musicrec/evaluation/inference.py",
        root / "src/musicrec/evaluation/ranking.py",
    ]
    for path in code_paths:
        destination = code / path.resolve().relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    code_hashes = {str(p.relative_to(code)): sha(p) for p in code.rglob("*") if p.is_file()}
    pin(args.config.resolve())
    pin(args.evaluation_config.resolve())
    write(out / "spectral_audit.json", audit)

    configurations: list[tuple[str, float, Recommender]] = [("base", 0.0, base)]
    for mode in config["gamma_modes"]:
        configurations += [(mode, g, spectral) for g in config["gamma0_grid"] if g > 0]
    configurations += [("direct", b, direct) for b in config["direct_beta_grid"] if b > 0]
    if args.max_configs is not None:
        configurations = configurations[: 1 + args.max_configs]

    k = config["primary_k"]
    base_lists: dict[str, list[str]] = {}
    base_result: dict[str, Any] = {}
    rows, points, per_user_rows = [], [], []
    for family, coefficient, model in configurations:
        if family in ("global", "deviation"):
            spectral.mode, spectral.gamma0 = family, coefficient
        elif family == "direct":
            direct.beta = coefficient
        label = f"{family}_{coefficient:g}"
        tick = perf_counter()
        recs = {u: model.recommend(u, max(config["ks"]), histories[u]) for u in users}
        recommend_seconds = perf_counter() - tick
        lists = {u: [r.item_id for r in v] for u, v in recs.items()}
        tick = perf_counter()
        result = evaluate_ranking(lists, targets, histories, ks=(5, 10, 20))
        eligible = [u for u, v in result["per_user"].items() if v["eligible"]]
        exposure = non_head_exposure(lists, eligible, split.non_head, k)
        a_history = popularity_alignment(lists, histories, popularity, eligible, k)
        a_target = popularity_alignment(lists, targets, popularity, eligible, k)
        evaluation_seconds = perf_counter() - tick
        if family == "base":
            base_lists, base_result = lists, result
        directory = out / "validation_seed_42" / label
        directory.mkdir(parents=True)
        write(directory / "evaluation.json", result)
        pd.DataFrame(
            [
                {"user_id": u, "rank": rank, "item_id": r.item_id, "score": r.score}
                for u in users
                for rank, r in enumerate(recs[u], 1)
            ]
        ).to_csv(directory / "recommendations.csv", index=False, lineterminator="\n")
        per_user_rows += [
            {
                "family": family,
                "coefficient": coefficient,
                "user_id": u,
                "ndcg_at_10": result["per_user"][u]["at_k"]["10"]["ndcg"],
                "non_head_exposure_at_10": exposure[u],
                "a_history_at_10": a_history[u],
                "a_target_at_10": a_target[u],
            }
            for u in eligible
        ]
        summary = {
            "family": family,
            "coefficient": coefficient,
            "ndcg": result["at_k"]["10"]["ndcg"],
            "exposure": float(np.mean([exposure[u] for u in eligible])),
            "a_history": mean_defined(a_history),
            "a_target": mean_defined(a_target),
            **{f"{m}_at_10": result["at_k"]["10"][m] for m in ["arp", "catalog_coverage", "ild"]},
            "users_eligible": len(eligible),
        }
        rows.append(summary)
        if family != "base":
            points.append(
                {
                    "family": family,
                    "coefficient": coefficient,
                    "ndcg": summary["ndcg"],
                    "exposure": summary["exposure"],
                }
            )
        resources[label] = {
            "recommend_seconds": recommend_seconds,
            "evaluation_seconds": evaluation_seconds,
        }
        print(
            f"{label} NDCG@10={summary['ndcg']:.10f} NonHeadExposure@10="
            f"{summary['exposure']:.6f} ({recommend_seconds:.1f}s + {evaluation_seconds:.1f}s)",
            flush=True,
        )
    pd.DataFrame(per_user_rows).to_parquet(out / "per_user_validation_seed_42.parquet")
    pd.DataFrame(rows).drop(columns=["a_history", "a_target"]).assign(
        a_history=[r["a_history"]["mean"] for r in rows],
        a_target=[r["a_target"]["mean"] for r in rows],
    ).to_csv(out / "points_validation_seed_42.csv", index=False, lineterminator="\n")

    selection: dict[str, Any] = {"sample_only_no_gate": True} if sample else {}
    if not sample:
        original = pd.read_csv(
            base_run / "recommendations.csv", dtype={"user_id": str, "item_id": str}
        )
        expected = original.groupby("user_id", sort=False)["item_id"].apply(list).to_dict()
        if base_lists != expected:
            raise RuntimeError("Reloaded ALS changed the frozen validation artist order")
        if base_result != read(base_run / "evaluation.json"):
            raise RuntimeError("Reloaded ALS does not reproduce the frozen base evaluation")
        base_row = rows[0]
        gate = apply_gate(points, {"ndcg": base_row["ndcg"], "exposure": base_row["exposure"]})
        frame = pd.DataFrame(per_user_rows)
        base_frame = frame[frame["family"] == "base"].set_index("user_id")
        indices = resample_indices(len(base_frame), **config["bootstrap"])
        development = {}
        chosen = [*gate["locked"].values(), gate["direct_control"]]
        for point in [p for p in chosen if p is not None and p["coefficient"] > 0]:
            new = frame[
                (frame["family"] == point["family"])
                & (frame["coefficient"] == point["coefficient"])
            ].set_index("user_id")
            new = new.loc[base_frame.index]
            development[f"{point['family']}_{point['coefficient']:g}"] = joint_test(
                new["ndcg_at_10"].to_numpy(),
                base_frame["ndcg_at_10"].to_numpy(),
                new["non_head_exposure_at_10"].to_numpy(),
                base_frame["non_head_exposure_at_10"].to_numpy(),
                indices,
            )
        selection = {
            "seed": 42,
            "split": "validation",
            "gate": gate,
            "development_bootstrap_after_selection": development,
            "development_evidence_only": True,
            "frozen_before_confirmation": True,
            "todo": [
                "seed 43/44 confirmation with the locked family/coefficient, gate per seed",
                "single locked test pass with train+validation mask and the agreed label",
            ],
        }
        write(out / "lock_h1.json", selection)
    if any(sha(Path(p)) != digest for p, digest in input_hashes.items()):
        raise RuntimeError("A pinned source/config changed during execution")
    peak = psutil.Process().memory_info()
    write(
        out / "metrics.json",
        {
            "step": "h1_round1",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "sample": {"users": len(users), "configurations": len(configurations)}
            if sample
            else None,
            "config": config,
            "evaluation_config": evaluation_config,
            "status": selection.get("gate", {}).get("status"),
            "resources": resources,
            "whole_run_seconds": perf_counter() - started,
            "process_peak_working_set_bytes": getattr(peak, "peak_wset", None),
            "input_sha256": input_hashes,
            "inputs_unchanged": True,
            "test_file_read": False,
            "base_fit_calls": 0,
            "base_source_run_recorded": info.get("source_run"),
            "code_sha256": code_hashes,
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "git_status": subprocess.check_output(["git", "status", "--short"], text=True),
            "git_diff_sha256": hashlib.sha256(subprocess.check_output(["git", "diff"])).hexdigest(),
            "runtime": {
                "python": sys.version,
                "machine": {
                    "platform": sys.platform,
                    "logical_cpus": os.cpu_count(),
                    "ram_bytes": psutil.virtual_memory().total,
                },
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
    print(json.dumps({"status": selection.get("gate", {}).get("status")}), flush=True)


if __name__ == "__main__":
    main()
