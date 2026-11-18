"""Small load test of POST /recommend on a running demo API (PureSVD, K = 10).

uvicorn musicrec.api.main:app --port 8010   (in another shell, one worker)
python scripts/load_test.py --api-url http://127.0.0.1:8010 --output-dir outputs/demo/load_<date>

For each concurrency level, `concurrency` client threads (one HTTP session each) send requests
back to back until `requests` responses are collected; user ids cycle through the first users
of /users so requests differ. Reports throughput, median and P95 latency and error rate,
plus the machine and library versions. Requests before `warmup` are not counted.
"""

import argparse
import importlib.metadata
import json
import os
import platform
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from statistics import median, quantiles
from time import perf_counter
from typing import Any

import requests


def run_level(url: str, users: list[str], concurrency: int, total: int) -> dict[str, Any]:
    latencies: list[float] = []
    errors = 0
    lock = threading.Lock()
    counter = [0]

    def worker() -> None:
        nonlocal errors
        session = requests.Session()
        while True:
            with lock:
                if counter[0] >= total:
                    return
                n = counter[0]
                counter[0] += 1
            body = {"user_id": users[n % len(users)], "k": 10, "model": "pure_svd"}
            start = perf_counter()
            try:
                ok = session.post(url + "/recommend", json=body, timeout=30).status_code == 200
            except requests.RequestException:
                ok = False
            elapsed = (perf_counter() - start) * 1000
            with lock:
                latencies.append(elapsed)
                errors += not ok

    start = perf_counter()
    with ThreadPoolExecutor(concurrency) as pool:
        for _ in range(concurrency):
            pool.submit(worker)
    wall = perf_counter() - start
    return {
        "concurrency": concurrency,
        "requests": len(latencies),
        "wall_seconds": wall,
        "throughput_rps": len(latencies) / wall,
        "median_ms": median(latencies),
        "p95_ms": quantiles(latencies, n=20)[18],
        "error_rate_pct": 100 * errors / len(latencies),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8010")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--levels", type=int, nargs="+", default=[1, 8, 32])
    parser.add_argument("--requests", type=int, default=400)
    parser.add_argument("--warmup", type=int, default=40)
    args = parser.parse_args()
    users = [u["user_id"] for u in requests.get(args.api_url + "/users?limit=200").json()]
    run_level(args.api_url, users, 1, args.warmup)
    rows = [run_level(args.api_url, users, c, args.requests) for c in args.levels]
    health = requests.get(args.api_url + "/health").json()
    result = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "command": sys.argv,
        "endpoint": "POST /recommend, existing user, pure_svd, k=10",
        "server": "uvicorn, one worker process, same machine as the client",
        "release": health.get("model_version"),
        "levels": rows,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            **{
                p: importlib.metadata.version(p)
                for p in ["fastapi", "uvicorn", "requests", "numpy", "scipy"]
            },
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "load_test.json").write_text(json.dumps(result, indent=2) + "\n", "utf-8")
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
