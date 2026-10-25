"""Verify Step 6 on synthetic hand examples; never read held-out data or fit models."""

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from math import isclose, log2, sqrt
from pathlib import Path
from time import perf_counter

import yaml

from musicrec.evaluation.ranking import (
    evaluate_ranking,
    gini_index,
    ndcg_at_k,
    precision_at_k,
    proxy_rmse,
    rank_candidates,
    recall_at_k,
)


def main() -> None:
    """Persist reproducible toy evidence without overwriting an existing run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toy-check", action="store_true", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        raise ValueError("Output must be a new directory")
    root = Path(__file__).resolve().parents[1]
    config_path = root / "configs/evaluation.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    inputs = {
        "train": {"u1": ["a", "b"], "u2": ["b", "c"], "u3": ["d", "e"], "u4": ["c", "f"]},
        "targets": {"u1": ["c", "e", "z"], "u2": ["d"], "u3": ["z"], "u4": ["a"]},
        "recommendations": {"u1": ["c", "d", "e"], "u2": ["d"], "u3": ["a", "b"], "u4": []},
    }
    start = perf_counter()
    result = evaluate_ranking(
        inputs["recommendations"],
        {user: set(items) for user, items in inputs["targets"].items()},
        {user: set(items) for user, items in inputs["train"].items()},
        ks=(3, *config["ks"]),
    )
    measured_seconds = perf_counter() - start
    expected = {
        "precision": 1 / 3,
        "recall": 2 / 3,
        "ndcg": ((1 + 0.5) / (1 + 1 / log2(3)) + 1) / 3,
        "catalog_coverage": 0.5,
        "gini": 7 / 12,
        "arp": 1.25,
        "novelty": (log2(14 / 3) + 3 * log2(7)) / 4,
        "ild": 2 / 3,
    }
    for metric, value in expected.items():
        if not isclose(result["at_k"]["3"][metric], value, abs_tol=1e-12):
            raise RuntimeError(f"Hand calculation mismatch: {metric}")
    checks = {
        "appendix_precision": precision_at_k(["b", "a", "c"], {"a", "c"}, 3),
        "appendix_recall": recall_at_k(["b", "a", "c"], {"a", "c"}, 3),
        "appendix_ndcg": ndcg_at_k(["b", "a", "c"], {"a", "c"}, 3),
        "short_precision_at_5": precision_at_k(["a", "b", "c"], {"a", "c"}, 5),
        "appendix_gini": gini_index([2, 1, 1, 0]),
        "proxy_rmse": proxy_rmse([1, 3, 5], [2, 3, 4]),
    }
    for actual, value in zip(
        checks.values(), [2 / 3, 1, 0.6934264036172708, 0.4, 0.375, sqrt(2 / 3)], strict=True
    ):
        if actual is None or not isclose(actual, value, abs_tol=1e-12):
            raise RuntimeError("Appendix hand calculation mismatch")
    if rank_candidates({"30": 1, "10": 1, "2": 1}, ["2", "10", "30"], {"2"}, 5) != ["10", "30"]:
        raise RuntimeError("Mask or tie-break mismatch")

    out.mkdir(parents=True, exist_ok=False)

    def write_json(name: str, value: object) -> None:
        with (out / name).open("x", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    write_json("toy_inputs.json", inputs)
    write_json("toy_results.json", result)
    write_json("hand_checks.json", {"expected_at_3": expected, "appendix": checks, "passed": True})
    code = out / "code"
    code.mkdir()
    for path in [
        Path(__file__),
        root / "src/musicrec/evaluation/ranking.py",
        root / "tests/unit/test_ranking.py",
        config_path,
    ]:
        shutil.copyfile(path, code / path.name)
    write_json(
        "metrics.json",
        {
            "step": 6,
            "scope": "synthetic evaluator verification only; no model quality results",
            "created_at_utc": datetime.now(UTC).isoformat(),
            "seed": 42,
            "dataset": "synthetic hand examples; no HetRec files read",
            "config": config,
            "command": sys.argv,
            "python": platform.python_version(),
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
            "git_diff_sha256": hashlib.sha256(
                subprocess.check_output(
                    ["git", "diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD"]
                )
            ).hexdigest(),
            "evaluator_seconds_toy_only": measured_seconds,
            "output_sha256": {
                path.name: sha256(path) for path in sorted(out.iterdir()) if path.is_file()
            },
            "code_sha256": {path.name: sha256(path) for path in sorted(code.iterdir())},
            "all_hand_checks_passed": True,
        },
    )
    print(json.dumps({"run": str(out), "hand_checks_passed": True, "appendix": checks}))


if __name__ == "__main__":
    main()
