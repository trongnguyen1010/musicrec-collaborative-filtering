"""Run Step 4 only from a verified cleaning run into a new directory."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import yaml

from musicrec.data.splitting import split_interactions


def main() -> None:
    """Save complete holdouts, train mappings and auditable split diagnostics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/base.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.clean_run.resolve(), args.output_dir.resolve()
    if out.exists() or source == out or source in out.parents:
        raise ValueError("Output must be a new directory outside the cleaning run")

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    metadata_path = source / "metrics.json"
    metadata_hash = sha256(metadata_path)
    cleaning = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = cleaning.get("output_sha256", {})
    if cleaning.get("step") != 3 or "interactions.parquet" not in expected:
        raise ValueError("Input must be a Step 3 run with recorded output hashes")
    for name, expected_hash in expected.items():
        if Path(name).name != name or sha256(source / name) != expected_hash:
            raise ValueError(f"Cleaning output checksum mismatch: {name}")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))["split"]
    if config["strategy"] != "per_user_random_holdout":
        raise ValueError("Step 4 requires per_user_random_holdout")
    interactions = pd.read_parquet(source / "interactions.parquet")
    tables, mappings, summary = split_interactions(
        interactions, config["seed"], config["validation_fraction"], config["test_fraction"]
    )
    out.mkdir(parents=True, exist_ok=False)
    for name in ["train", "validation", "test"]:
        tables[name].to_parquet(out / f"{name}.parquet", index=False)
    tables["user_split_counts"].to_csv(out / "user_split_counts.csv", index=False)
    with (out / "id_mappings.json").open("x", encoding="utf-8") as handle:
        json.dump(mappings, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    root = Path(__file__).resolve().parents[1]
    snapshots = [Path(__file__), root / "src/musicrec/data/splitting.py", args.config]
    code = out / "code"
    code.mkdir()
    for path in snapshots:
        shutil.copyfile(path, code / path.name)
    unchanged = metadata_hash == sha256(metadata_path) and all(
        sha256(source / name) == value for name, value in expected.items()
    )
    if not unchanged:
        raise RuntimeError("Cleaning inputs changed during splitting")
    summary.update(
        {
            "step": 4,
            "scope": "random holdout and mappings only; no transforms, features or training",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_run": str(source),
            "source_metrics_sha256": metadata_hash,
            "input_sha256": expected,
            "inputs_unchanged": unchanged,
            "seed": config["seed"],
            "config": config,
            "definitions": {
                "ordering": "numeric ascending user IDs, then numeric ascending artist IDs",
                "random_generator": "one random.Random(seed), users visited in numeric order",
                "holdout_order": "validation first, then test, then train from shuffled indices",
                "sizes": "n_val/n_test=max(1,floor(fraction*n)); train receives the remainder",
                "mappings": "zero-based contiguous user/item indices from train only",
                "unknown_items": "retain complete holdouts; item_index=null outside train catalog",
                "evaluation": "intersect targets with train catalog; report excluded targets/users",
                "scope": "not temporal, not leave-one-out; no model evaluation or M2 user split",
            },
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
            "git_status": subprocess.check_output(["git", "status", "--porcelain"]).decode(),
            "git_diff_sha256": hashlib.sha256(
                subprocess.check_output(
                    ["git", "diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD"]
                )
            ).hexdigest(),
            "code_sha256": {path.name: sha256(path) for path in snapshots},
            "runtime": {
                "python": platform.python_version(),
                **{name: importlib.metadata.version(name) for name in ["pandas", "pyarrow"]},
            },
            "command": sys.argv,
            "output_sha256": {
                path.name: sha256(path) for path in sorted(out.iterdir()) if path.is_file()
            },
        }
    )
    with (out / "metrics.json").open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"run": str(out), "splits": summary["splits"], "targets": summary["targets"]}))


if __name__ == "__main__":
    main()
