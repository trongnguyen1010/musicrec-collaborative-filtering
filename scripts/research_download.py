"""Download only the pinned LastFM inputs; never execute downloaded code."""

import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2"
ZIP_URL = "https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip"
ZIP_SHA = "6738f48195667ff03caaab4d32ca9a3133d8cc026b7c3cdaf6ce1010e913c59c"
SOURCE_FILES = [
    "main.py",
    "MD_DHC_Recbole.py",
    "DhcExtension.py",
    "packages_management.py",
    "parameters_management.py",
    "README.md",
    "LICENSE",
]


def download(url: str, path: Path, git_sha: str | None = None) -> dict:
    """Atomically download and verify a public HTTPS input, with bounded retries."""
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            if not path.exists():
                request = urllib.request.Request(url, headers={"User-Agent": "musicrec-research"})
                temporary = path.with_suffix(path.suffix + ".part")
                try:
                    with urllib.request.urlopen(request, timeout=120) as response:
                        with temporary.open("wb") as output:
                            while block := response.read(1024 * 1024):
                                output.write(block)
                except OSError:
                    if os.name != "nt" or url != ZIP_URL:
                        raise
                    # Use Windows' native TLS implementation; never disable verification.
                    subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-NonInteractive",
                            "-File",
                            str(ROOT / "scripts/download_hetrec.ps1"),
                            "-Destination",
                            str(temporary),
                        ],
                        check=True,
                    )
                temporary.replace(path)
            content = path.read_bytes()
            blob_sha = hashlib.sha1(
                f"blob {len(content)}\0".encode() + content, usedforsecurity=False
            ).hexdigest()
            if git_sha is not None and blob_sha != git_sha:
                raise ValueError(f"Git blob checksum mismatch: {path}")
            return {
                "url": url,
                "path": str(path.relative_to(ROOT)),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "git_blob_sha1": blob_sha,
                "downloaded_at": datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(),
            }
        except (OSError, ValueError):
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("Unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    archive = ROOT / "data/raw/hetrec2011-lastfm-2k.zip"
    dataset = download(ZIP_URL, archive)
    if dataset["sha256"] != ZIP_SHA or dataset["bytes"] != 2589075:
        raise ValueError("Official archive differs from the previously verified version")
    destination = ROOT / "data/raw/hetrec2011"
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            target = (destination / entry.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Unsafe archive member")
        bundle.extractall(destination)
    api = f"https://api.github.com/repos/pitteryue/AIProbS/git/trees/{COMMIT}?recursive=1"
    request = urllib.request.Request(api, headers={"User-Agent": "musicrec-research"})
    with urllib.request.urlopen(request, timeout=60) as response:
        tree = json.load(response)
    if tree.get("truncated"):
        raise ValueError("Incomplete upstream tree")
    blobs = {row["path"]: row["sha"] for row in tree["tree"] if row["type"] == "blob"}
    names = SOURCE_FILES + [f"Data/30 LastFM Realizations/lastfm {i}.pth" for i in range(30)]

    def fetch(name: str) -> dict:
        url = f"https://raw.githubusercontent.com/pitteryue/AIProbS/{COMMIT}/"
        url += urllib.parse.quote(name)
        path = ROOT / "data/interim/aiprobs-source" / name
        result = download(url, path, blobs[name])
        print(f"verified {name}", flush=True)
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(fetch, names))
    manifest = {
        "dataset": dataset,
        "aiprobs_commit": COMMIT,
        "upstream_files": records,
        "checked_at": datetime.now(UTC).isoformat(),
    }
    output = ROOT / "outputs/research/download_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Verified dataset and {len(records)} upstream files: {output}")


if __name__ == "__main__":
    main()
