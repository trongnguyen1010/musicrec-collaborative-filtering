"""Rerun locked split-zero inference from scratch and compare saved per-user evidence."""

import json
import os

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

import numpy as np
import torch

from musicrec.recommenders.bpr import BPRRecommender
from musicrec.recommenders.diffusion import DiffusionRecommender, Variant
from musicrec.research.io import OUT, SPLITS, Split, sha256, write_json
from musicrec.research.runner import evaluate


def main() -> None:
    torch.set_num_threads(4)
    split = Split.load(SPLITS / "aiprobs-original/split_00.npz")
    records = []
    for name in ["pure_dhc", "probs", "aiprobs", "bpr"]:
        destination = OUT / "runs/aiprobs-original" / name / "split_00"
        saved = json.loads((destination / "result.json").read_text(encoding="utf-8"))
        if saved["status"] != "completed" or saved["split_sha256"] != sha256(split.path):
            raise ValueError("Completed compatible result required")
        model: DiffusionRecommender | BPRRecommender
        if name == "bpr":
            model = BPRRecommender(OUT / "bpr/aiprobs-original/split_00/factors.npz")
        else:
            variant: Variant = name  # type: ignore[assignment]
            model = DiffusionRecommender(variant, split.users, split.items).fit_matrix(
                split.matrix()
            )
        metrics, ranking = evaluate(model, split, "test", batch_size=64)
        with np.load(destination / "ranking.npz", allow_pickle=False) as prior:
            np.testing.assert_array_equal(ranking["ranking"], prior["ranking"])
            np.testing.assert_array_equal(ranking["per_user_metrics"], prior["per_user_metrics"])
        if metrics != saved["test"]:
            raise AssertionError(f"Repeated metrics differ: {name}")
        records.append(
            {
                "model": name,
                "split_id": 0,
                "mlflow_run_id": saved["mlflow_run_id"],
                "ranking": "bit-exact",
                "per_user_metrics": "bit-exact",
            }
        )
    write_json(
        OUT / "repeatability.json",
        {
            "status": "passed",
            "scope": "fresh fit for diffusion; fresh factor load for BPR; split 0; CPU inference",
            "records": records,
        },
    )
    print("Repeated split-zero rankings and metrics are bit-exact for all four models")


if __name__ == "__main__":
    main()
