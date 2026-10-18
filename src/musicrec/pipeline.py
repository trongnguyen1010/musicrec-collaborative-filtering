"""Run an auditable validation-only Popularity experiment from one effective config."""

import argparse
import hashlib
import platform
import subprocess
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pandas as pd

from musicrec.configuration import ROOT, canonical_json, read_config, sha256, write_json
from musicrec.data.contracts import Interaction
from musicrec.data.preparation import (
    fit_transform,
    load_artists,
    split_interactions,
    split_summary,
    transform_counts,
    validate_interactions,
)
from musicrec.evaluation.evaluator import evaluate
from musicrec.recommenders.popularity import PopularityRecommender


def interactions_from_frame(frame: pd.DataFrame) -> list[Interaction]:
    """Keep raw counts in the public Interaction contract."""
    return [
        Interaction(str(row["user_id"]), str(row["item_id"]), float(row["listening_count"]))
        for row in frame.to_dict("records")
    ]


def git_state() -> dict[str, str]:
    """Capture commit and source hash, including uncommitted and new implementation files."""

    def command(*args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=ROOT)

    paths = sorted(
        p
        for folder in ("src", "scripts", "configs", "tests")
        for p in (ROOT / folder).rglob("*")
        if p.is_file() and p.suffix in (".py", ".yaml") and "__pycache__" not in p.parts
    )
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return {
        "git_sha": command("rev-parse", "HEAD").decode().strip(),
        "branch": command("branch", "--show-current").decode().strip(),
        "dirty": str(bool(command("status", "--porcelain"))),
        "code_hash": digest.hexdigest(),
    }


def snapshot_sources(folder: Path) -> str:
    """Keep exact uncommitted experiment sources with each independently reproducible run."""
    paths = [
        p
        for name in ("src", "scripts", "configs", "tests")
        for p in (ROOT / name).rglob("*")
        if p.is_file() and p.suffix in (".py", ".yaml") and "__pycache__" not in p.parts
    ]
    paths += [
        ROOT / name
        for name in ("pyproject.toml", "params.yaml", "dvc.yaml")
        if (ROOT / name).is_file()
    ]
    destination = folder / "source_snapshot.zip"
    with (
        destination.open("xb") as stream,
        ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive,
    ):
        for path in sorted(paths):
            archive.write(path, path.relative_to(ROOT).as_posix())
    return sha256(destination)


def runtime_environment() -> dict[str, Any]:
    """Record the actual numerical and serving versions rather than only version ranges."""
    packages = {}
    for name in (
        "numpy",
        "scipy",
        "pandas",
        "scikit-learn",
        "pyarrow",
        "PyYAML",
        "fastapi",
        "streamlit",
        "httpx",
        "threadpoolctl",
    ):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = "not_installed"
    return {
        "python": platform.python_version(),
        "os": platform.platform(),
        "processor": platform.processor(),
        "packages": packages,
        "blas_threads": 1,
    }


def run(config: dict[str, Any], run_id: str | None = None) -> Path:
    """Validate, split, fit, save/reload and evaluate validation without touching test."""
    if config["model"]["name"] != "popularity":
        raise ValueError("This pipeline currently supports model.name=popularity")
    identity = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%S_%fZ")
    if Path(identity).name != identity or identity in (".", ".."):
        raise ValueError("run_id must be a directory name")
    out = ROOT / str(config["output"]["runs_dir"]) / identity
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "config.json", config)
    manifest: dict[str, Any] = {
        "status": "running",
        "run_id": identity,
        **git_state(),
        "config_hash": hashlib.sha256(canonical_json(config)).hexdigest(),
        "seed": int(config["project"]["seed"]),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "test_evaluated": False,
    }
    manifest["source_snapshot_sha256"] = snapshot_sources(out)
    manifest["environment"] = runtime_environment()
    try:
        source = ROOT / config["source"]["interactions"]
        metadata = ROOT / config["source"]["artists"]
        for key, path in (("interactions", source), ("artists", metadata)):
            manifest[key] = {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        expected = config["source"].get("interaction_sha256")
        if expected and expected != manifest["interactions"]["sha256"]:
            raise ValueError("Source checksum differs from configured dataset")
        frame, report = validate_interactions(source)
        names, metadata_report = load_artists(metadata, frame)
        report.update(metadata_report)
        write_json(out / "data_report.json", report)
        frame.to_parquet(out / "interactions.parquet", index=False)
        split_cfg = config["split"]
        if split_cfg["strategy"] != "per_user_random":
            raise ValueError("Unsupported split strategy")
        splits = split_interactions(
            frame,
            manifest["seed"],
            int(split_cfg["min_user_artists"]),
            float(split_cfg["heldout_fraction"]),
        )
        if sum(len(f) for f in splits.values()) != len(frame):
            raise RuntimeError("Split lost interactions")
        summary = split_summary(splits)
        write_json(
            out / "split_manifest.json",
            {
                "seed": manifest["seed"],
                "summary": summary,
                "test_mask": "train_union_validation",
                "refit": False,
            },
        )
        transform = fit_transform(splits["train"])
        write_json(out / "transform.json", transform)
        for name, subset in splits.items():
            transform_counts(subset, transform).to_parquet(out / f"{name}.parquet", index=False)
        write_json(
            out / "id_maps.json",
            {
                "users": sorted(set(frame.user_id)),
                "train_artists": sorted(set(splits["train"].item_id)),
                "all_artists": sorted(set(frame.item_id)),
            },
        )
        write_json(out / "artist_names.json", names)
        model = PopularityRecommender().fit(interactions_from_frame(splits["train"]))
        model.save(out / "model.json")
        reloaded = PopularityRecommender.load(out / "model.json")
        if model.recommend("probe", 20, set()) != reloaded.recommend("probe", 20, set()):
            raise RuntimeError("Model roundtrip changed recommendations")
        evaluation = config["evaluation"]
        if (
            evaluation["candidate_catalog"],
            evaluation["ground_truth"],
            evaluation["test_mask"],
        ) != ("train", "full_including_cold_misses", "train_union_validation"):
            raise ValueError("Unsupported evaluator protocol")
        metrics, predictions, user_metrics = evaluate(
            reloaded, splits["train"], splits["validation"], evaluation["ks"]
        )
        write_json(out / "validation_metrics.json", metrics)
        predictions.to_parquet(out / "validation_predictions.parquet", index=False)
        user_metrics.to_csv(out / "validation_users.csv", index=False)
        manifest.update(
            status="completed",
            artifacts={p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()},
        )
    except Exception as exc:
        manifest.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        write_json(out / "manifest.json", manifest)
    pointer = ROOT / "outputs/latest_run.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_bytes(canonical_json({"run_dir": str(out.relative_to(ROOT))}))
    return out


def main() -> None:
    """CLI entrypoint; every invocation writes a fresh run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="params.yaml")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    print(run(read_config(args.config), args.run_id))


if __name__ == "__main__":
    main()
