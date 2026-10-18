"""Load the effective experiment configuration and write auditable JSON artifacts."""

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def read_config(path: str | Path = "params.yaml") -> dict[str, Any]:
    """Resolve the four YAML sections from the repository configuration entrypoint."""
    source = Path(path)
    if not source.is_absolute():
        source = ROOT / source
    entry = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(entry, dict):
        raise ValueError("Configuration must be a mapping")
    result: dict[str, Any] = {}
    for section in (
        "base",
        "dataset",
        "model",
        "evaluation",
        *(["experiment"] if "experiment" in entry else []),
    ):
        if section not in entry:
            raise ValueError(f"Missing configuration section: {section}")
        section_path = ROOT / entry[section]
        loaded = yaml.safe_load(section_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"Invalid section: {section}")
        for key, value in loaded.items():
            if key in result:
                raise ValueError(f"Duplicate configuration key: {key}")
            result[key] = value
    if (
        result["evaluation"]["selection_metric"] != "ndcg_at_10"
        or 10 not in result["evaluation"]["ks"]
    ):
        raise ValueError("The locked protocol selects NDCG@10 and requires K=10")
    return result


def canonical_json(value: Any) -> bytes:
    """Return a stable JSON representation; NaN and infinity are never valid artifacts."""
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    """Hash the exact source bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Create a new artifact without replacing a previous run's file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_json(value))
