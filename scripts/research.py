"""Offline research CLI; protocols must always be explicitly selected."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

from musicrec.research.dataset import analyze, canonical_pairs
from musicrec.research.io import OUT, ROOT, SPLITS, Split, write_json
from musicrec.research.runner import run, summarize


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "analyze",
            "validate-splits",
            "run",
            "summarize",
            "download",
            "convert",
            "benchmark-splits",
            "train-bpr",
            "verify-reference",
            "verify-metrics",
            "report",
            "all",
        ],
    )
    parser.add_argument(
        "--protocol", choices=["aiprobs-original", "recbole-bpr-benchmark", "thesis"]
    )
    parser.add_argument("--model", choices=["pure_dhc", "probs", "aiprobs", "bpr"])
    parser.add_argument("--split-id", type=int)
    parser.add_argument(
        "--seed", type=int, help="Must match the fixed protocol, never reshuffles author splits"
    )
    parser.add_argument("--config", default="configs/reproduction.yaml")
    args = parser.parse_args()
    if args.action in {"download", "convert", "benchmark-splits", "train-bpr", "verify-metrics"}:
        if args.action == "download":
            subprocess.run([sys.executable, str(ROOT / "scripts/research_download.py")], check=True)
        else:
            extra = []
            if args.action == "train-bpr":
                if args.protocol not in {"aiprobs-original", "recbole-bpr-benchmark"}:
                    parser.error("--protocol is required for BPR training")
                extra = ["--protocol", args.protocol]
                if args.split_id is not None:
                    extra += ["--split-id", str(args.split_id)]
            legacy(args.action, extra)
        return
    if args.action == "verify-reference":
        from musicrec.research.reference import verify_full_reference, verify_tiny_reference

        print(verify_tiny_reference())
        print(verify_full_reference())
        return
    if args.action == "report":
        from musicrec.research.reporting import build_report

        build_report()
        return
    if args.action == "all":
        subprocess.run([sys.executable, str(ROOT / "scripts/research_download.py")], check=True)
        analyze()
        legacy("convert")
        legacy("benchmark-splits")
        subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "validate-splits"], check=True
        )
        from musicrec.research.reference import verify_full_reference, verify_tiny_reference

        verify_tiny_reference()
        verify_full_reference()
        for index in range(30):
            for model in ["pure_dhc", "probs", "aiprobs"]:
                run("aiprobs-original", model, index)
        for protocol, indices in [
            ("aiprobs-original", range(30)),
            ("recbole-bpr-benchmark", [2020, 2021, 2022]),
        ]:
            for index in indices:
                legacy("train-bpr", ["--protocol", protocol, "--split-id", str(index)])
                run(protocol, "bpr", index)
        legacy("verify-metrics")
        subprocess.run(
            [
                str(ROOT / ".venv-legacy/Scripts/python.exe"),
                str(ROOT / "scripts/research_checkpoint_check.py"),
            ],
            check=True,
            cwd=ROOT,
        )
        for helper in ["research_repeatability.py", "research_checks.py"]:
            subprocess.run([sys.executable, str(ROOT / "scripts" / helper)], check=True, cwd=ROOT)
        from musicrec.research.reporting import build_report

        build_report()
        return
    if args.action == "analyze":
        analyze()
    elif args.action == "validate-splits":
        canonical = canonical_pairs()
        records = [
            {"path": str(path), **Split.load(path).validate(canonical)}
            for path in sorted(SPLITS.rglob("*.npz"))
        ]
        if len(records) != 33:
            raise ValueError(f"Expected 30 author and 3 benchmark splits, found {len(records)}")
        write_json(OUT / "split_validation.json", records)
        print(f"Validated {len(records)} splits")
    elif args.action == "summarize":
        print(summarize().to_string(index=False))
    else:
        import yaml

        with open(args.config, encoding="utf-8") as stream:
            config = yaml.safe_load(stream)
        if config["k"] != 10 or config["binary"] is not True or config["filter"] is not None:
            parser.error("Published reproduction requires K=10, binary=True and no filtering")
        if config["evaluation_batch_size"] <= 0:
            parser.error("evaluation_batch_size must be positive")
        if args.protocol is None:
            parser.error("--protocol is required for a run")
        if args.protocol == "thesis":
            parser.error("Thesis training remains outside the reproduction scope")
        if args.protocol == "aiprobs-original" and args.model != "bpr":
            reference = OUT / "full_reference_verification.json"
            if not reference.exists() or json.loads(reference.read_text())["status"] != "passed":
                parser.error("Run verify-reference before launching the author experiments")
        models = [args.model] if args.model else config[args.protocol]["models"]
        indices = [args.split_id] if args.split_id is not None else config[args.protocol]["splits"]
        for index in indices:
            expected_seed = index if args.protocol == "recbole-bpr-benchmark" else 2020
            if args.seed is not None and args.seed != expected_seed:
                parser.error(f"Fixed protocol requires seed {expected_seed}")
            for model in models:
                run(args.protocol, model, index, config["evaluation_batch_size"])
        summarize()


def legacy(action: str, extra: list[str] | None = None) -> None:
    """Keep unsafe legacy serialization and RecBole imports outside the main environment."""
    executable = ROOT / ".venv-legacy" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not executable.exists():
        raise FileNotFoundError("Create the isolated legacy environment using research_setup.ps1")
    subprocess.run(
        [str(executable), str(ROOT / "scripts/research_legacy.py"), action, *(extra or [])],
        check=True,
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
