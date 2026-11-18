"""Package the official locked checkpoints into a demo release without refitting anything.

Sources come from the test locks of the official run: PureSVD k=16, M1 over it and ALS at
seed 42 (chuong_4/test/lock.json), M2 (chuong_4/m2_test/lock.json). Every checkpoint file
must match the lock hash and the train/validation interactions must match the
representations run, otherwise nothing is written. Lock paths recorded on the cloud
machine are re-rooted onto this checkout.

    python scripts/export_release.py --version demo-chinh-thuc-20261026
"""

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from musicrec.serving.release import ReleaseSources, build_release, sha256, tree_hashes

ROOT = Path(__file__).resolve().parents[1]
CLOUD_ROOT = "/home/claude/musicrec-collaborative-filtering/"
RUN = Path("outputs/chinh_thuc_cloud_20261026")
SEED = "42"


def local(path: str) -> Path:
    """Map a path recorded on the cloud machine onto this checkout."""
    if not path.startswith(CLOUD_ROOT):
        raise ValueError(f"Unexpected lock path root: {path}")
    return ROOT / path.removeprefix(CLOUD_ROOT)


def checked(directory: Path, expected: dict[str, str], name: str) -> Path:
    """Require the exact locked file set and hashes for one checkpoint directory."""
    actual = tree_hashes(directory)
    if actual != expected:
        bad = sorted(k for k in expected.keys() | actual.keys() if actual.get(k) != expected.get(k))
        raise ValueError(f"{name}: checkpoint differs from lock: {bad}")
    return directory


def collect(run: Path, artists: Path) -> ReleaseSources:
    """Resolve and verify every input against the official locks."""
    test_lock_path = run / "chuong_4/test/lock.json"
    m2_lock_path = run / "chuong_4/m2_test/lock.json"
    test_lock: dict[str, Any] = json.loads(test_lock_path.read_text(encoding="utf-8"))
    m2_lock: dict[str, Any] = json.loads(m2_lock_path.read_text(encoding="utf-8"))
    models = test_lock["models"]
    sources: dict[str, Path] = {}
    for name in ["pure_svd", "implicit_als"]:
        entry = models[name]["runs"][SEED]
        sources[name] = checked(local(entry["path"]) / "model", entry["model_sha256"], name)
    m1 = models["m1"]["runs"][SEED]
    sources["m1"] = checked(local(m1["path"]), m1["model_sha256"], "m1")
    sources["m2"] = checked(local(m2_lock["m2_run"]) / "model", m2_lock["model_sha256"], "m2")

    representations = local(test_lock["representations_run"])
    produced = json.loads((representations / "metrics.json").read_text(encoding="utf-8"))
    for name in ["train.parquet", "validation.parquet"]:
        if sha256(representations / name) != produced["output_sha256"][name]:
            raise ValueError(f"Representations checksum mismatch: {name}")

    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=ROOT
    ).stdout.strip()
    git_dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=ROOT
        ).stdout.strip()
    )
    rel = {name: path.relative_to(ROOT).as_posix() for name, path in sources.items()}
    provenance = {
        "git_sha": git_sha,
        "git_dirty": git_dirty,
        "test_lock": {
            "path": test_lock_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(test_lock_path),
        },
        "m2_lock": {
            "path": m2_lock_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(m2_lock_path),
        },
        "experiment_git_sha": test_lock["git_sha"],
        "representations": representations.relative_to(ROOT).as_posix(),
        "artists": artists.as_posix(),
        "artists_sha256": sha256(ROOT / artists),
        "models": {
            "pure_svd": {"source": rel["pure_svd"], "seed": 42, **models["pure_svd"]["selected"]},
            "m1": {
                "source": rel["m1"],
                "base": models["m1"]["base"],
                "lambda": models["m1"]["lambda"],
                "beta": models["m1"]["beta"],
                "candidate_size": models["m1"]["candidate_size"],
            },
            "implicit_als": {
                "source": rel["implicit_als"],
                "seed": 42,
                **models["implicit_als"]["selected"],
            },
            "m2": {"source": rel["m2"], **m2_lock["selected"]},
            "popularity": {"source": "refit on release train.parquet (as in the official test)"},
        },
        "mask": test_lock["test_masks"],
    }
    return ReleaseSources(
        models=sources,
        train=representations / "train.parquet",
        validation=representations / "validation.parquet",
        artists=ROOT / artists,
        provenance=provenance,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--artists", type=Path, default=Path("data/raw/hetrec2011/artists.dat"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/releases"))
    args = parser.parse_args()
    sources = collect(ROOT / args.run, args.artists)
    manifest = build_release(sources, ROOT / args.output_root / args.version, args.version)
    print(f"Release {args.version}: {len(manifest['files'])} files verified and written")


if __name__ == "__main__":
    main()
