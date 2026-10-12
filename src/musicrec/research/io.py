"""Safe split files, provenance and local experiment tracking."""

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

from musicrec.recommenders.diffusion import IntArray

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/research"
SPLITS = ROOT / "data/processed/reproduction"
os.environ.setdefault("MLFLOW_DISABLE_TELEMETRY", "true")
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")


def sha256(path: Path) -> str:
    """Hash inputs without loading a large dataset into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Atomically replace a JSON result; a crash cannot create a completed run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    temporary.replace(path)


def provenance() -> dict[str, Any]:
    """Capture tracked-code diff as well as Git SHA (uncommitted edits matter)."""
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    sources = sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "scripts").glob("*.py"))
    sources += sorted((ROOT / "configs").rglob("*.yaml"))
    code = {str(path.relative_to(ROOT)): sha256(path) for path in sources}
    fingerprint = hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest()
    snapshot = OUT / f"source_{fingerprint}.zip"
    if not snapshot.exists():
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(snapshot, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sources:
                archive.write(path, path.relative_to(ROOT))
    return {
        "git_sha": revision,
        "code_files": code,
        "code_sha256": fingerprint,
        "source_snapshot": str(snapshot),
        "python": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ["numpy", "scipy", "pandas", "torch", "mlflow", "dvc"]
        },
    }


def track(
    name: str, params: dict[str, Any], metrics: dict[str, float], artifacts: list[Path]
) -> str:
    """Log locally to SQLite/MLflow; no account or external tracking service."""
    import mlflow

    mlflow.set_tracking_uri("sqlite:///" + (OUT / "mlflow.db").as_posix())
    mlflow.set_experiment("hetrec-lastfm-reproduction")
    with mlflow.start_run(run_name=name) as run:
        mlflow.log_params(params)
        # MLflow metric names reject '@'; published/CSV names retain their notation.
        mlflow.log_metrics({key.replace("@", "_at_"): value for key, value in metrics.items()})
        for path in artifacts:
            mlflow.log_artifact(str(path))
        return str(run.info.run_id)


@dataclass
class Split:
    """Immutable-on-disk author split; integer IDs are retained including padding."""

    path: Path
    users: list[str]
    items: list[str]
    train: IntArray
    validation: IntArray
    test: IntArray
    valid_history: IntArray
    test_history: IntArray
    valid_users: IntArray
    test_users: IntArray

    @classmethod
    def load(cls, path: Path) -> "Split":
        """Load only non-object NumPy arrays and verify the export manifest."""
        metadata = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        if sha256(path) != metadata["sha256"]:
            raise ValueError(f"Split checksum mismatch: {path}")
        with np.load(path, allow_pickle=False) as data:
            return cls(
                path,
                data["users"].tolist(),
                data["items"].tolist(),
                **{
                    key: np.asarray(data[key], dtype=np.int64)
                    for key in [
                        "train",
                        "validation",
                        "test",
                        "valid_history",
                        "test_history",
                        "valid_users",
                        "test_users",
                    ]
                },
            )

    def matrix(self) -> sparse.csr_matrix:
        """Binary train adjacency, with no validation or test edges."""
        return sparse.csr_matrix(
            (np.ones(len(self.train)), self.train.T), shape=(len(self.users), len(self.items))
        )

    def validate(self, canonical: set[tuple[str, str]]) -> dict[str, Any]:
        """Check conservation, ID mapping, disjointness and native history masks."""
        if self.users[0] != "[PAD]" or self.items[0] != "[PAD]":
            raise ValueError("Expected RecBole padding at index zero")
        if len(set(self.users)) != len(self.users) or len(set(self.items)) != len(self.items):
            raise ValueError("Duplicate catalog token")
        sets = []
        for part in [self.train, self.validation, self.test]:
            if part.ndim != 2 or part.shape[1] != 2 or (part <= 0).any():
                raise ValueError("Invalid interaction shape or padding in interactions")
            if (part[:, 0] >= len(self.users)).any() or (part[:, 1] >= len(self.items)).any():
                raise ValueError("ID out of catalog")
            pairs = set(map(tuple, part.tolist()))
            if len(pairs) != len(part):
                raise ValueError("Duplicate interaction")
            sets.append(pairs)
        train, valid, test = sets
        if train & valid or train & test or valid & test:
            raise ValueError("Split leakage")
        raw = {(self.users[u], self.items[i]) for u, i in train | valid | test}
        if raw != canonical:
            raise ValueError(f"Split differs from canonical pairs: {len(raw ^ canonical)}")
        for history, evaluated, positives, expected in [
            (self.valid_history, self.valid_users, valid, train),
            (self.test_history, self.test_users, test, train | valid),
        ]:
            evaluated_set = set(evaluated.tolist())
            if evaluated_set != {u for u, _ in positives}:
                raise ValueError("Native evaluation user set differs from ground truth")
            expected = {(u, i) for u, i in expected if u in evaluated_set}
            if set(map(tuple, history.tolist())) != expected:
                raise ValueError("Native history mask differs from protocol")
        trained_users = {u for u, _ in train}
        trained_items = {i for _, i in train}
        return {
            "split_sha256": sha256(self.path),
            "train": len(train),
            "validation": len(valid),
            "test": len(test),
            "test_users": len(self.test_users),
            "empty_test_users": len(self.users) - 1 - len(self.test_users),
            "cold_test_users": len(set(self.test_users) - trained_users),
            "cold_test_interactions": sum(i not in trained_items for _, i in test),
        }
