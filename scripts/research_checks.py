"""Record actual repository quality gate output; fail immediately on an unsuccessful check."""

import subprocess
import sys
import time

import psutil

from musicrec.research.io import OUT, ROOT, provenance, write_json


def main() -> None:
    write_json(
        OUT / "hardware.json",
        {
            "cpu_physical": psutil.cpu_count(logical=False),
            "cpu_logical": psutil.cpu_count(),
            "ram_bytes": psutil.virtual_memory().total,
        },
    )
    checks = []
    for args in [
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
        ["mypy", "src"],
        ["pytest", "--basetemp", "outputs/research/pytest-quality"],
    ]:
        started = time.perf_counter()
        result = subprocess.run(
            [sys.executable, "-m", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        checks.append(
            {
                "command": args,
                "exit_code": result.returncode,
                "seconds": time.perf_counter() - started,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        write_json(
            OUT / "quality_checks.json",
            {
                "status": "failed" if result.returncode else "running",
                "checks": checks,
            },
        )
        print(result.stdout, end="", flush=True)
        print(result.stderr, end="", file=sys.stderr, flush=True)
        result.check_returncode()
    write_json(
        OUT / "quality_checks.json",
        {
            "status": "passed",
            "checks": checks,
            "source_provenance": provenance(),
        },
    )


if __name__ == "__main__":
    main()
