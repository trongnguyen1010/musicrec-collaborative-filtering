"""Run Step 3 only: clean HetRec observations into a new, auditable directory."""

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

from musicrec.data.cleaning import clean_tables, read_source_table


def main() -> None:
    """Save cleaned tables, exclusions, configuration and immutable source hashes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/hetrec2011"))
    parser.add_argument("--config", type=Path, default=Path("configs/dataset.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw, out = args.raw_dir.resolve(), args.output_dir.resolve()
    if out.exists() or out == raw or raw in out.parents:
        raise ValueError("Output must be a new directory outside the raw source directory")
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if config["filters"]["min_item_interactions"] is not None:
        raise ValueError("Step 3 does not filter artists by listener count")
    min_history = config["filters"]["min_user_interactions"]
    if type(min_history) is not int or min_history < 1:
        raise ValueError("min_user_interactions must be a positive integer")

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    zip_path = raw.parent / "hetrec2011-lastfm-2k.zip"
    inputs = sorted(p for p in raw.iterdir() if p.is_file()) + [zip_path]
    hashes = {str(path): sha256(path) for path in inputs}
    if hashes[str(zip_path)] != config["source"]["checksum"]:
        raise ValueError("Source ZIP checksum does not match dataset configuration")
    tables, metrics = clean_tables(
        *(
            read_source_table(raw / name)
            for name in ["user_artists.dat", "artists.dat", "tags.dat", "user_taggedartists.dat"]
        ),
        min_user_interactions=min_history,
    )
    metrics.update(
        {
            "step": 3,
            "scope": "cleaning only; no split, mapping, transformations, TF-IDF or training",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "seed": None,
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
            "git_status": subprocess.check_output(["git", "status", "--porcelain"]).decode(),
            "git_diff_sha256": hashlib.sha256(
                subprocess.check_output(
                    ["git", "diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD"]
                )
            ).hexdigest(),
            "input_sha256": hashes,
            "config": config,
            "runtime": {
                "python": platform.python_version(),
                **{
                    name: importlib.metadata.version(name)
                    for name in ["pandas", "pyarrow", "pyyaml"]
                },
            },
            "definitions": {
                "ids": "Canonical positive decimal integer labels; no arithmetic on IDs",
                "count": "Positive int64 integer; preserve raw count, no log or clipping",
                "duplicates": "Equal user/artist/count keep first; conflicting counts abort",
                "exclusion_order": list(metrics["interaction_rules"])[4:],
                "tags_encoding": "ISO-8859-1 (Latin-1); all other input tables UTF-8",
                "tag_assignments": "Date view only; preserve userID; do not append timestamp view",
                "artist_catalog": "Keep source artists, including those without interactions",
            },
        }
    )
    out.mkdir(parents=True, exist_ok=False)
    for name, frame in tables.items():
        frame.to_parquet(out / f"{name}.parquet", index=False)
    pd.DataFrame(metrics["interaction_rules"].items(), columns=["rule", "count"]).to_csv(
        out / "interaction_rule_counts.csv", index=False
    )
    pd.DataFrame([metrics["before"], metrics["after"]], index=["before", "after"]).to_csv(
        out / "before_after.csv", index_label="stage"
    )
    code = out / "code"
    code.mkdir()
    snapshots = [Path(__file__), Path("src/musicrec/data/cleaning.py"), args.config]
    metrics["code_sha256"] = {}
    for path in snapshots:
        shutil.copyfile(path, code / path.name)
        metrics["code_sha256"][str(path)] = sha256(path)
    metrics["command"] = sys.argv
    metrics["raw_inputs_unchanged"] = all(
        sha256(Path(path)) == value for path, value in hashes.items()
    )
    if not metrics["raw_inputs_unchanged"]:
        raise RuntimeError("Raw inputs changed during cleaning")
    metrics["output_sha256"] = {path.name: sha256(path) for path in sorted(out.glob("*.parquet"))}
    with (out / "metrics.json").open("x", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"run": str(out), "after": metrics["after"], "tags": metrics["tags"]}))


if __name__ == "__main__":
    main()
