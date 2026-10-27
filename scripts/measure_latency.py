"""Measure end-to-end HTTP latency of a running demo API and record the machine it ran on.

    uvicorn musicrec.api.main:app --port 8000   (in another shell)
    python scripts/measure_latency.py --output-dir outputs/demo/latency_<date>
"""

import argparse
import importlib.metadata
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import median, quantiles
from time import perf_counter
from typing import Any

import requests

REPEATS = 50
CALLS: list[tuple[str, str, dict[str, Any]]] = [
    ("GET /health", "/health", {}),
    ("GET /users", "/users?limit=2000", {}),
    ("GET /users/{id}/history", "/users/2/history", {}),
    ("GET /artists?q=", "/artists?q=the&limit=20", {}),
    ("POST /recommend pure_svd", "/recommend", {"user_id": "2", "k": 10, "model": "pure_svd"}),
    ("POST /recommend m1", "/recommend", {"user_id": "2", "k": 10, "model": "m1"}),
    ("POST /recommend implicit_als", "/recommend", {"user_id": "2", "k": 10, "model": "implicit_als"}),
    ("POST /recommend m2 (3 artists)", "/recommend", {"history": [{"item_id": i} for i in ["89", "289", "292"]], "k": 10}),
    ("POST /recommend popularity", "/recommend", {"history": [], "k": 10}),
]  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    session = requests.Session()
    results = {}
    for label, path, body in CALLS:
        timings = []
        for _ in range(REPEATS + 1):
            start = perf_counter()
            response = (
                session.post(args.api_url + path, json=body, timeout=30)
                if body
                else session.get(args.api_url + path, timeout=30)
            )
            elapsed = (perf_counter() - start) * 1000
            response.raise_for_status()
            timings.append(elapsed)
        timings = timings[1:]  # first call warms connection and caches
        results[label] = {
            "repeats": REPEATS,
            "median_ms": median(timings),
            "p95_ms": quantiles(timings, n=20)[-1],
            "max_ms": max(timings),
        }
        print(f"{label}: median {results[label]['median_ms']:.1f} ms")
    health = session.get(args.api_url + "/health", timeout=30).json()
    report = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "api_url": args.api_url,
        "release": health["model_version"],
        "latency": results,
        "machine": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
            **{
                name: importlib.metadata.version(name)
                for name in ["fastapi", "uvicorn", "numpy", "scipy", "pandas"]
            },
        },
        "command": sys.argv,
    }
    (args.output_dir / "latency.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")


if __name__ == "__main__":
    main()
