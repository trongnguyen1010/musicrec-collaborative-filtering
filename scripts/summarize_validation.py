"""Verify frozen model runs and summarize Step 14 validation evidence, never test."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import yaml

from musicrec.evaluation.validation import (
    compare_seed_models,
    summarize_history_groups,
    summarize_seeds,
)


def main() -> None:
    """Persist a new summary of verified run metrics, cohorts, seeds and resources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/validation_summary.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        raise ValueError("Output must be a new directory")

    def guard(event: str, values: tuple) -> None:
        if event == "open" and isinstance(values[0], (str, bytes)):
            name = values[0].decode() if isinstance(values[0], bytes) else values[0]
            if Path(name).name == "test.parquet":
                raise RuntimeError("Step 14 must never open test.parquet, including hashing")

    sys.addaudithook(guard)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def read(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if config["step"] != 14 or config["model_seeds"] != [42, 43, 44] or config["split_seed"] != 42:
        raise ValueError("Expected the fixed Step 14 seed protocol")
    source = Path(config["representations_run"]).resolve()
    split = Path(config["split_run"]).resolve()
    if any(p == out or p in out.parents for p in [source, split]):
        raise ValueError("Output must be outside source runs")
    input_hashes = {}
    for directory, step in [(source, 5), (split, 4)]:
        metadata = read(directory / "metrics.json")
        if metadata["step"] != step or metadata["seed"] != 42:
            raise ValueError("Expected the original verified split/representations")
        for name in ["train.parquet", "validation.parquet", "id_mappings.json"]:
            expected = metadata["output_sha256"][name]
            if sha(directory / name) != expected:
                raise ValueError(f"Source checksum mismatch: {name}")
            input_hashes[str(directory / name)] = expected
    for name in ["train", "validation"]:
        columns = ["user_id", "item_id", "listening_count", "user_index", "item_index"]
        if not pd.read_parquet(source / f"{name}.parquet")[columns].equals(
            pd.read_parquet(split / f"{name}.parquet")[columns]
        ):
            raise ValueError("Baseline and representation runs must use identical split rows")
    train = pd.read_parquet(source / "train.parquet")
    lengths = {u: int(n) for u, n in train.groupby("user_id").size().items()}
    records, group_rows, resources, seed_rows = [], [], [], []
    seed_results, source_runs = {}, {}
    gate_config = config.get("retention_gate")
    gate_evaluations = {}
    reference_cohort = None
    reference_protocol = None
    for model, runs in config["runs"].items():
        evaluations = {}
        base_config = None
        for seed, name in runs.items():
            run = Path(name).resolve()
            if run == out or run in out.parents:
                raise ValueError("Output must be outside model runs")
            metadata = read(run / "metrics.json")
            if Path(metadata["source_run"]).resolve() not in (source, split):
                raise ValueError("All models must use the declared source split/representations")
            if (
                reference_protocol is not None
                and metadata["evaluation_config"] != reference_protocol
            ):
                raise ValueError("All models must use the same evaluation protocol")
            reference_protocol = metadata["evaluation_config"]
            if metadata["seed"] != seed or metadata["test_file_read"]:
                raise ValueError("Expected the declared model seed and validation-only run")
            values = {k: v for k, v in metadata["config"].items() if k != "seed"}
            if base_config is not None and values != base_config:
                raise ValueError("Seed confirmation must not change other model settings")
            base_config = values
            for filename, expected in metadata["input_sha256"].items():
                if filename not in {
                    "train.parquet",
                    "validation.parquet",
                    "id_mappings.json",
                    "transform.json",
                }:
                    raise ValueError("Unexpected input outside the validation protocol")
                if sha(Path(metadata["source_run"]) / filename) != expected:
                    raise ValueError(f"Model input checksum mismatch: {filename}")
            for filename, expected in metadata["output_sha256"].items():
                if sha(run / filename) != expected:
                    raise ValueError(f"Model output checksum mismatch: {filename}")
            for filename, expected in metadata["code_sha256"].items():
                if sha(run / "code" / filename) != expected:
                    raise ValueError(f"Model code snapshot mismatch: {filename}")
            verification = read(run / "verification.json")
            if not verification["all_checks_passed"]:
                raise ValueError("All source runs require passing independent verification")
            evaluation = read(run / "evaluation.json")
            if metadata["at_k"] != evaluation["at_k"]:
                raise ValueError("Recorded metrics disagree with saved evaluation")
            cohort = {
                u: [
                    v[k]
                    for k in ["eligible", "targets_total", "targets_in_catalog", "candidate_count"]
                ]
                for u, v in evaluation["per_user"].items()
            }
            if reference_cohort is not None and cohort != reference_cohort:
                raise ValueError("All model rows must share the exact validation cohort")
            reference_cohort = cohort
            evaluations[seed] = evaluation
            groups = summarize_history_groups(evaluation, lengths)
            for k, metrics in evaluation["at_k"].items():
                records.append({"model": model, "seed": seed, "k": int(k), **metrics})
            for label, group in groups["groups"].items():
                for k, metrics in group["at_k"].items():
                    group_rows.append(
                        {
                            "model": model,
                            "seed": seed,
                            "group": label,
                            "k": int(k),
                            **{key: value for key, value in group.items() if key != "at_k"},
                            **metrics,
                        }
                    )
            model_files = (
                list((run / "model").glob("*"))
                if (run / "model").is_dir()
                else [run / "model.json"]
            )
            resources.append(
                {
                    "model": model,
                    "seed": seed,
                    **metadata["timing_seconds"],
                    "fit_including_validation_seconds": metadata.get("supplementary", {}).get(
                        "fit_including_validation_seconds"
                    ),
                    "best_epoch": metadata.get("supplementary", {}).get("best_epoch"),
                    "process_peak_working_set_bytes": metadata.get("supplementary", {}).get(
                        "process_peak_working_set_bytes"
                    ),
                    "model_artifact_bytes": sum(
                        p.stat().st_size for p in model_files if p.is_file()
                    ),
                }
            )
            source_runs[f"{model}:{seed}"] = {
                "path": str(run),
                "metrics_sha256": sha(run / "metrics.json"),
                "verification_sha256": sha(run / "verification.json"),
                "config": metadata["config"],
            }
        if len(evaluations) > 1:
            summary = summarize_seeds(evaluations)
            seed_results[model] = summary
            for k, metrics in summary["at_k"].items():
                for metric, stats in metrics.items():
                    if stats is not None:
                        seed_rows.append({"model": model, "k": int(k), "metric": metric, **stats})
        if gate_config and model in (gate_config["candidate"], gate_config["control"]):
            gate_evaluations[model] = evaluations
    gate = None
    selected_candidate = config["candidate_for_m1"]
    if gate_config:
        if (
            gate_config["metric"] != "ndcg_at_10_validation"
            or gate_config["rule"] != "higher_mean_and_at_least_two_positive_seed_differences"
            or gate_config["tie"] != "retain_control"
        ):
            raise ValueError("Expected the predeclared three-seed retention rule")
        gate = compare_seed_models(
            gate_evaluations[gate_config["candidate"]], gate_evaluations[gate_config["control"]]
        )
        selected_candidate = gate_config["candidate"] if gate["passes"] else gate_config["control"]
    if not all(sha(Path(p)) == value for p, value in input_hashes.items()):
        raise RuntimeError("Inputs changed during summary")
    out.mkdir(parents=True, exist_ok=False)
    for filename, rows in [
        ("metrics.csv", records),
        ("history_groups.csv", group_rows),
        ("resources.csv", resources),
        ("seed_summary.csv", seed_rows),
    ]:
        pd.DataFrame(rows).to_csv(out / filename, index=False, lineterminator="\n")
    code = out / "code"
    code.mkdir()
    root = Path(__file__).resolve().parents[1]
    for path in [
        Path(__file__),
        args.config,
        root / "src/musicrec/evaluation/validation.py",
        root / "tests/unit/test_validation_summary.py",
    ]:
        shutil.copyfile(path, code / path.name)
    result = {
        "step": config.get("revision", 14),
        "scope": "validation synthesis of declared configurations; no tuning or test evaluation",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "input_sha256": input_hashes,
        "source_runs": source_runs,
        "model_seed_summaries": seed_results,
        "retention_gate": gate,
        "candidate_for_m1": selected_candidate,
        "candidate_status": "validation_candidate_pending_m1_design_no_test_lock",
        "train_history_mode": groups["train_history_mode"],
        "train_history_quantiles": train.groupby("user_id")
        .size()
        .quantile([0.25, 0.5, 0.75])
        .to_dict(),
        "history_group_counts": {
            k: {n: v for n, v in g.items() if n != "at_k"} for k, g in groups["groups"].items()
        },
        "resource_limitations": (
            "Historical per-run timings/on-disk size; OS process peak only where logged; "
            "not controlled latency benchmark or model-only RAM"
        ),
        "test_file_read": False,
        "test_open_guard_enabled": True,
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
        "git_diff_sha256": hashlib.sha256(
            subprocess.check_output(["git", "diff", "--binary", "HEAD"])
        ).hexdigest(),
        "output_sha256": {p.name: sha(p) for p in sorted(out.glob("*.csv"))},
        "code_sha256": {p.name: sha(p) for p in code.iterdir()},
    }
    with (out / "metrics.json").open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(
        json.dumps(
            {
                "run": str(out),
                "model_seed_rows": len(source_runs),
                "history_groups": result["history_group_counts"],
            }
        )
    )


if __name__ == "__main__":
    main()
