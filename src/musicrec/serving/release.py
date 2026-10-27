"""Package pinned experiment checkpoints into a self-checking demo release, and load it back.

A release copies checkpoint directories byte for byte (no refit), the train/validation
interactions needed for history masks and Popularity, and an artist name table. Every
file is listed with its SHA-256 in manifest.json; loading refuses missing, extra or
changed files before any model is restored.
"""

import csv
import hashlib
import importlib.metadata
import json
import platform
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from musicrec.data.contracts import Interaction
from musicrec.recommenders.implicit_als import ImplicitALSRecommender
from musicrec.recommenders.m1 import M1Recommender
from musicrec.recommenders.m2 import M2Recommender
from musicrec.recommenders.popularity import PopularityRecommender
from musicrec.recommenders.pure_svd import PureSVDRecommender

SCHEMA_VERSION = 1
MODEL_DIRS = ("pure_svd", "m1", "implicit_als", "m2")
DATA_FILES = ("train.parquet", "validation.parquet", "artists.json")


def sha256(path: Path) -> str:
    """Hex SHA-256 of one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(directory: Path) -> dict[str, str]:
    """SHA-256 of every file below a directory, keyed by POSIX relative path."""
    return {
        p.relative_to(directory).as_posix(): sha256(p)
        for p in sorted(directory.rglob("*"))
        if p.is_file()
    }


@dataclass(frozen=True, slots=True)
class ReleaseSources:
    """Already verified inputs; model directories hold the files the loaders expect."""

    models: dict[str, Path]
    train: Path
    validation: Path
    artists: Path
    provenance: dict[str, Any]


def read_artists(path: Path, item_ids: set[str]) -> list[dict[str, str]]:
    """Read HetRec artists.dat (tab separated, UTF-8) restricted to catalog ids."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE))
    return [
        {"id": row["id"], "name": row["name"], "url": row["url"], "picture_url": row["pictureURL"]}
        for row in rows
        if row["id"] in item_ids
    ]


def build_release(sources: ReleaseSources, directory: Path, version: str) -> dict[str, Any]:
    """Copy inputs into a new directory and write the manifest; never overwrite."""
    if set(sources.models) != set(MODEL_DIRS):
        raise ValueError(f"Expected model sources {sorted(MODEL_DIRS)}")
    directory.mkdir(parents=True, exist_ok=False)
    for name, source in sources.models.items():
        shutil.copytree(source, directory / "models" / name)
    data = directory / "data"
    data.mkdir()
    shutil.copyfile(sources.train, data / "train.parquet")
    shutil.copyfile(sources.validation, data / "validation.parquet")
    items = {
        str(item)
        for frame in [sources.train, sources.validation]
        for item in pd.read_parquet(frame, columns=["item_id"]).item_id
    }
    artists = read_artists(sources.artists, items)
    (data / "artists.json").write_text(
        json.dumps(artists, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "release": version,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "provenance": sources.provenance,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{name: importlib.metadata.version(name) for name in ["numpy", "scipy", "pandas"]},
        },
        "files": tree_hashes(directory),
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


@dataclass(frozen=True)
class Release:
    """Restored models plus the train-only statistics the service needs."""

    version: str
    manifest: dict[str, Any]
    pure_svd: PureSVDRecommender
    m1: M1Recommender
    implicit_als: ImplicitALSRecommender
    m2: M2Recommender
    popularity: PopularityRecommender
    train: pd.DataFrame
    validation: pd.DataFrame
    artists: dict[str, dict[str, str]]


def verify_release(directory: Path) -> dict[str, Any]:
    """Return the manifest after checking the exact file set and every hash."""
    manifest: dict[str, Any] = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported release schema")
    actual = tree_hashes(directory)
    actual.pop("manifest.json")
    expected: dict[str, str] = manifest["files"]
    if actual.keys() != expected.keys():
        missing, extra = expected.keys() - actual.keys(), actual.keys() - expected.keys()
        raise ValueError(f"Release file set differs: missing={sorted(missing)} extra={extra}")
    changed = sorted(name for name, digest in expected.items() if actual[name] != digest)
    if changed:
        raise ValueError(f"Release checksum mismatch: {changed}")
    return manifest


def load_release(directory: Path) -> Release:
    """Verify, then restore checkpoints without fitting; Popularity is a train statistic."""
    manifest = verify_release(directory)
    models = directory / "models"
    pure_svd = PureSVDRecommender.load(models / "pure_svd")
    train = pd.read_parquet(directory / "data" / "train.parquet")
    validation = pd.read_parquet(directory / "data" / "validation.parquet")
    for frame in [train, validation]:
        frame["user_id"] = frame.user_id.astype(str)
        frame["item_id"] = frame.item_id.astype(str)
    popularity = PopularityRecommender().fit(
        Interaction(str(r.user_id), str(r.item_id), float(str(r.listening_count)))
        for r in train[["user_id", "item_id", "listening_count"]].itertuples(index=False)
    )
    artists = json.loads((directory / "data" / "artists.json").read_text(encoding="utf-8"))
    return Release(
        version=str(manifest["release"]),
        manifest=manifest,
        pure_svd=pure_svd,
        m1=M1Recommender.load(models / "m1", base=pure_svd),
        implicit_als=ImplicitALSRecommender.load(models / "implicit_als"),
        m2=M2Recommender.load(models / "m2"),
        popularity=popularity,
        train=train,
        validation=validation,
        artists={row["id"]: row for row in artists},
    )
