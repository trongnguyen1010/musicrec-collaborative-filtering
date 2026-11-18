"""Run Step 5 only, preserving split rows and fitting proxy thresholds on train."""

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
from scipy.sparse import save_npz

from musicrec.data.representations import REPRESENTATION_CONFIG, prepare_representations


def main() -> None:
    """Save four input representations and their train-fitted transformation metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/base.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.split_run.resolve(), args.output_dir.resolve()
    if out.exists() or source == out or source in out.parents:
        raise ValueError("Output must be a new directory outside the split run")

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    metadata_path = source / "metrics.json"
    metadata_hash = sha256(metadata_path)
    split = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = split.get("output_sha256", {})
    required = {"train.parquet", "validation.parquet", "test.parquet", "id_mappings.json"}
    if split.get("step") != 4 or not required.issubset(expected):
        raise ValueError("Input must be a Step 4 run with recorded output hashes")
    for name, expected_hash in expected.items():
        if Path(name).name != name or sha256(source / name) != expected_hash:
            raise ValueError(f"Split output checksum mismatch: {name}")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))["representations"]
    if config != REPRESENTATION_CONFIG:
        raise ValueError("Step 5 requires the agreed log2 and strict linear-quantile protocol")
    splits = {
        name: pd.read_parquet(source / f"{name}.parquet")
        for name in ["train", "validation", "test"]
    }
    mappings = json.loads((source / "id_mappings.json").read_text(encoding="utf-8"))
    tables, matrices, summary = prepare_representations(splits, mappings)
    out.mkdir(parents=True, exist_ok=False)
    for name, frame in tables.items():
        frame.to_parquet(out / f"{name}.parquet", index=False)
    for name, matrix in matrices.items():
        save_npz(out / f"train_{name}.npz", matrix)
    shutil.copyfile(source / "id_mappings.json", out / "id_mappings.json")
    with (out / "transform.json").open("x", encoding="utf-8") as handle:
        json.dump(summary["transform"], handle, indent=2, allow_nan=False)
        handle.write("\n")
    root = Path(__file__).resolve().parents[1]
    snapshots = [Path(__file__), root / "src/musicrec/data/representations.py", args.config]
    code = out / "code"
    code.mkdir()
    for path in snapshots:
        shutil.copyfile(path, code / path.name)
    unchanged = metadata_hash == sha256(metadata_path) and all(
        sha256(source / name) == value for name, value in expected.items()
    )
    if not unchanged:
        raise RuntimeError("Split inputs changed during representation preparation")
    summary.update(
        {
            "step": 5,
            "scope": "input representations only; no features, evaluator or model training",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_run": str(source),
            "source_metrics_sha256": metadata_hash,
            "input_sha256": expected,
            "inputs_unchanged": unchanged,
            "seed": split["seed"],
            "config": config,
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
                **{
                    name: importlib.metadata.version(name)
                    for name in ["numpy", "pandas", "scipy", "pyarrow"]
                },
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
    print(
        json.dumps(
            {"run": str(out), "transform": summary["transform"], "splits": summary["splits"]}
        )
    )


if __name__ == "__main__":
    main()
