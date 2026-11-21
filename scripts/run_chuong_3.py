"""Chạy lại Bước 1–6 (Chương 3) từ tệp HetRec gốc hai lần và ghi lại môi trường chạy."""

import argparse
import ctypes
import filecmp
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STEPS: list[tuple[str, list[str]]] = [
    ("raw_eda", ["scripts/eda.py", "--raw-dir", "{raw}"]),
    ("cleaning", ["scripts/preprocess.py", "--raw-dir", "{raw}"]),
    ("split", ["scripts/split_data.py", "--clean-run", "{cleaning}"]),
    ("representations", ["scripts/prepare_inputs.py", "--split-run", "{split}"]),
    ("evaluator", ["scripts/evaluate.py", "--toy-check"]),
]
KEY_PACKAGES = ["numpy", "pandas", "pyarrow", "scipy", "scikit-learn", "matplotlib", "pyyaml"]


def total_ram_bytes() -> int | None:
    """Dung lượng RAM vật lý không cần gói ngoài; None nếu hệ điều hành không cho biết."""
    if hasattr(os, "sysconf") and "SC_PHYS_PAGES" in os.sysconf_names:
        return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    if sys.platform == "win32":

        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("load", ctypes.c_ulong),
                ("total_phys", ctypes.c_ulonglong),
                ("rest", ctypes.c_ulonglong * 6),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))  # type: ignore[attr-defined]
        return int(status.total_phys)
    return None


def cpu_name() -> str:
    """Tên CPU dễ đọc; platform.processor() thường rỗng trên Linux."""
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or platform.machine()


def environment(label: str) -> dict[str, Any]:
    """Máy, hệ điều hành, phiên bản Python và thư viện cho bảng 'Môi trường chạy' của khóa luận."""
    versions: dict[str, str | None] = {}
    for name in KEY_PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    installed = sorted(
        f"{dist.metadata['Name']}=={dist.version}" for dist in importlib.metadata.distributions()
    )
    git = ["git", "rev-parse", "HEAD"]
    return {
        "label": label,
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "os": platform.platform(),
        "cpu": cpu_name(),
        "logical_cpus": os.cpu_count(),
        "ram_bytes": total_ram_bytes(),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "key_packages": versions,
        "installed_packages": installed,
        "git_sha": subprocess.run(git, capture_output=True, text=True).stdout.strip(),
        "git_status_porcelain": subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        ).stdout.splitlines(),
    }


def run_pipeline(base: Path, raw: Path) -> dict[str, float]:
    """Chạy từng bước vào base/<bước>; trả số giây thực của mỗi bước."""
    paths = {"raw": str(raw)}
    seconds = {}
    for name, template in STEPS:
        out = base / name
        command = [sys.executable, "-B", *[part.format(**paths) for part in template]]
        start = datetime.now(UTC)
        subprocess.run([*command, "--output-dir", str(out)], check=True, stdout=subprocess.DEVNULL)
        seconds[name] = (datetime.now(UTC) - start).total_seconds()
        paths[name] = str(out)
    return seconds


def compare(first: Path, second: Path) -> dict[str, Any]:
    """So từng byte kết quả dữ liệu của hai lần chạy; siêu dữ liệu và bản chụp mã khác nhau là
    bình thường.
    """
    report: dict[str, Any] = {}
    for name, _ in STEPS:
        left = first / name
        files = sorted(
            path.relative_to(left).as_posix()
            for path in left.rglob("*")
            if path.is_file()
            and not any(
                part == "code" or part.startswith(".") for part in path.relative_to(left).parts
            )
            and path.suffix not in {".py", ".png"}
            and path.name != "metrics.json"
        )
        differ = [f for f in files if not filecmp.cmp(left / f, second / name / f, shallow=False)]
        hashes = []
        for run in (left, second / name):
            metadata = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
            hashes.append(metadata.get("output_sha256"))
        report[name] = {
            "files_compared": len(files),
            "files_differ": differ,
            "output_sha256_equal": hashes[0] == hashes[1],
        }
    return report


def main() -> None:
    """Ghi run/, recheck/, environment.json và summary.json vào thư mục mới."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/hetrec2011"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--label", required=True, help="Machine label, e.g. cloud or windows")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = environment(args.label)
    (out / "environment.json").write_text(
        json.dumps(env, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    seconds = {"run": run_pipeline(out / "run", args.raw_dir.resolve())}
    seconds["recheck"] = run_pipeline(out / "recheck", args.raw_dir.resolve())
    comparison = compare(out / "run", out / "recheck")
    identical = all(
        not step["files_differ"] and step["output_sha256_equal"] for step in comparison.values()
    )
    summary = {"seconds": seconds, "comparison": comparison, "recheck_identical": identical}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": str(out), "recheck_identical": identical, "seconds": seconds}))


if __name__ == "__main__":
    main()
