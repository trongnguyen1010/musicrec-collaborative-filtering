"""Export and verify a local serving release backed by real experiment artifacts."""

import json
import shutil
from pathlib import Path
from typing import Any

from musicrec.configuration import ROOT, sha256, write_json


def export_release(study: Path, data: Path, destination: Path) -> Path:
    """Publish only after the immutable test run completed; never replace a release."""
    if not (study / "final_manifest.json").is_file():
        raise ValueError("Test evaluation must complete before export")
    selected = json.loads((study / "m1/locked.json").read_text())
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(
        study / selected["base_kind"] / f"seed_{selected['seed']}" / "model.npz",
        destination / "base.npz",
    )
    shutil.copytree(study / "m2/model", destination / "m2")
    shutil.copyfile(data / "train.parquet", destination / "train.parquet")
    shutil.copyfile(data / "artist_names.json", destination / "artist_names.json")
    write_json(destination / "rerank.json", selected)
    from musicrec.pipeline import snapshot_sources

    snapshot_sources(destination)
    run = json.loads((data / "manifest.json").read_text())
    manifest = {
        "schema": "musicrec_release_v1",
        "model_version": destination.name,
        "git_sha": run["git_sha"],
        "data_version": run["interactions"]["sha256"],
        "run_id": str(study.relative_to(ROOT)),
        "config_hash": sha256(study / "config.json"),
        "test_lock_sha256": sha256(study / "test_lock.json"),
        "base_kind": selected["base_kind"],
        "seed": selected["seed"],
        "known_profile": "training_history_only",
        "explicit_history_merge": "max_count_per_artist",
        "files": {
            str(p.relative_to(destination)).replace("\\", "/"): sha256(p)
            for p in destination.rglob("*")
            if p.is_file()
        },
    }
    write_json(destination / "manifest.json", manifest)
    verify_release(destination)
    return destination


def verify_release(folder: Path) -> dict[str, Any]:
    """Check required provenance and all payload hashes before loading numeric artifacts."""
    manifest: dict[str, Any] = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), dict):
        raise ValueError("Invalid release manifest")
    if manifest.get("schema") != "musicrec_release_v1":
        raise ValueError("Unsupported release schema")
    for field in (
        "model_version",
        "git_sha",
        "data_version",
        "run_id",
        "config_hash",
        "test_lock_sha256",
    ):
        if not manifest.get(field):
            raise ValueError(f"Missing release provenance: {field}")
    required = {
        "base.npz",
        "train.parquet",
        "artist_names.json",
        "rerank.json",
        "m2/item_cf.npz",
        "m2/tag_features.npz",
        "m2/params.json",
    }
    if not required.issubset(manifest["files"]):
        raise ValueError("Incomplete release payload")
    for name, expected in manifest["files"].items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError("Release payload escapes its root")
        if sha256(path) != expected:
            raise ValueError(f"Release checksum mismatch: {name}")
    return manifest
