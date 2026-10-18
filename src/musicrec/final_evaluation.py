"""Freeze configuration hashes before test, evaluate once and compare paired users."""

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from threadpoolctl import threadpool_limits

from musicrec.configuration import ROOT, read_config, sha256, write_json
from musicrec.extension_experiments import attach_profiles, provided_profiles, save_evaluation
from musicrec.pipeline import git_state
from musicrec.recommenders.extensions import ColdStartModel, Reranker
from musicrec.recommenders.models import MatrixModel
from musicrec.recommenders.popularity import PopularityRecommender


def paired_statistics(left: pd.Series, right: pd.Series, samples: int, seed: int) -> dict[str, Any]:
    """Bootstrap paired user differences and use a two-sided Wilcoxon signed-rank test."""
    if set(left.index) != set(right.index):
        raise ValueError("Paired statistics require identical cohorts")
    difference = (left.sort_index() - right.sort_index()).to_numpy(dtype=float)
    if not len(difference) or not np.isfinite(difference).all():
        raise ValueError("Invalid user metric pairs")
    difference[np.abs(difference) < 1e-12] = 0
    rng = np.random.default_rng(seed)
    means = [
        float(rng.choice(difference, len(difference), replace=True).mean()) for _ in range(samples)
    ]
    p = (
        float(wilcoxon(difference, zero_method="wilcox", alternative="two-sided").pvalue)
        if np.any(difference)
        else 1.0
    )
    return {
        "users": len(difference),
        "mean_difference": float(difference.mean()),
        "ci95": np.quantile(means, [0.025, 0.975]).tolist(),
        "p_raw": p,
        "zero_differences": int((difference == 0).sum()),
        "bootstrap_samples": samples,
    }


def user_ndcg(path: Path) -> pd.Series:
    frame = pd.read_csv(path, dtype={"user_id": str})
    return frame[frame.k == 10].set_index("user_id").ndcg


def finalize(study: Path, data: Path, config: dict[str, Any]) -> None:
    """No training or selection is performed after creating the immutable test lock."""
    for filename in (
        "manifest.json",
        "extensions_manifest.json",
        "m1/locked.json",
        "m2/locked.json",
    ):
        if not (study / filename).is_file():
            raise ValueError(f"Incomplete validation: {filename}")
    locked_files = {
        str(p.relative_to(study)): sha256(p)
        for p in study.rglob("*")
        if p.is_file()
        and p.name
        in (
            "selected.json",
            "locked.json",
            "model.npz",
            "item_cf.npz",
            "tag_features.npz",
            "params.json",
        )
    }
    write_json(
        study / "test_lock.json",
        {
            "files": locked_files,
            "config": config,
            **git_state(),
            "refit": False,
            "mask": "train_union_validation",
            "selection": "validation_only",
        },
    )
    train = pd.read_parquet(data / "train.parquet")
    val = pd.read_parquet(data / "validation.parquet")
    test = pd.read_parquet(data / "test.parquet")
    output = study / "test"
    output.mkdir(exist_ok=False)
    ks = config["evaluation"]["ks"]
    settings = config["experiment"]
    seed = int(config["project"]["seed"])
    pop = PopularityRecommender.load(data / "model.json")
    save_evaluation(output / "popularity", pop, train, test, ks, val)
    summary = json.loads((study / "validation_summary.json").read_text())
    family_users = {}
    totals = {}
    for kind in summary:
        seeds = []
        rows = []
        for source in sorted((study / kind).glob("seed_*")):
            print(f"Test {kind} {source.name}", flush=True)
            model = MatrixModel.load(source / "model.npz")
            result = save_evaluation(output / kind / source.name, model, train, test, ks, val)
            seeds.append(user_ndcg(output / kind / source.name / "users.csv"))
            rows.append(result["by_k"]["10"])
            if kind == "svd":
                eligible = test[test.item_id.isin(model.item_index)]
                predicted = [
                    model.predict(str(r["user_id"]), str(r["item_id"]))
                    for r in eligible.to_dict("records")
                ]
                write_json(
                    output / kind / source.name / "rmse_proxy.json",
                    {
                        "rmse": float(
                            np.sqrt(
                                np.mean(np.square(eligible.preference_proxy.to_numpy() - predicted))
                            )
                        ),
                        "observations": len(eligible),
                        "cold_excluded": len(test) - len(eligible),
                        "clipped": False,
                    },
                )
        family_users[kind] = pd.concat(seeds, axis=1).mean(axis=1)
        totals[kind] = {
            name: {
                "mean": float(np.mean([r[name] for r in rows])),
                "std": float(np.std([r[name] for r in rows], ddof=1)) if len(rows) > 1 else 0.0,
            }
            for name in ("precision", "recall", "ndcg", "coverage", "arp", "ild")
        }
    m1 = json.loads((study / "m1/locked.json").read_text())
    base = MatrixModel.load(study / m1["base_kind"] / f"seed_{seed}" / "model.npz")
    for name, w, p in (
        ("base", 1.0, 0.0),
        ("diversity", m1["weight"], 0.0),
        ("popularity", 1.0, m1["penalty"]),
        ("full", m1["weight"], m1["penalty"]),
    ):
        save_evaluation(
            output / "m1" / name, Reranker(base, m1["candidates"], w, p), train, test, ks, val
        )
    groups = json.loads((study / "m2/user_partitions.json").read_text())
    reference = pd.read_parquet(study / "m2/reference.parquet")
    targets = test[test.user_id.isin(groups["test"])].copy()
    m2 = ColdStartModel.load(study / "m2/model")
    for n in settings["given_n"]:
        profile = provided_profiles(train, groups["test"], seed, int(n))
        for mode in ("popularity", "content", "cf", "combined"):
            cold_model = ColdStartModel(m2.item_cf, m2.features, m2.alpha, m2.threshold, mode)
            attach_profiles(cold_model, profile)
            save_evaluation(
                output / "m2" / f"n_{n}" / mode, cold_model, reference, targets, ks, profile
            )
    chosen = max(summary, key=lambda name: summary[name]["validation_ndcg_at_10"])
    pairs = {
        "selected_vs_popularity": (
            family_users[chosen],
            user_ndcg(output / "popularity/users.csv"),
        ),
        "svd_vs_pure_svd": (family_users["svd"], family_users["pure_svd"]),
        "m1_vs_base": (
            user_ndcg(output / "m1/full/users.csv"),
            user_ndcg(output / "m1/base/users.csv"),
        ),
        "m2_vs_popularity_n3": (
            user_ndcg(output / "m2/n_3/combined/users.csv"),
            user_ndcg(output / "m2/n_3/popularity/users.csv"),
        ),
    }
    stats = {
        name: paired_statistics(a, b, int(settings["bootstrap_samples"]), seed)
        for name, (a, b) in pairs.items()
    }
    adjusted = 0.0
    for rank, name in enumerate(sorted(stats, key=lambda n: stats[n]["p_raw"])):
        adjusted = max(adjusted, min(1.0, stats[name]["p_raw"] * (len(stats) - rank)))
        stats[name]["p_holm"] = adjusted
    write_json(
        output / "summary.json",
        {
            "families": totals,
            "selected_on_validation": chosen,
            "paired_tests": stats,
            "seed_aggregation": (
                "paired comparisons use per-user mean over model seeds; M1 uses seed 42 only"
            ),
        },
    )
    if any(sha256(study / name) != expected for name, expected in locked_files.items()):
        raise RuntimeError("Locked configuration/model changed during test")
    write_json(
        study / "final_manifest.json",
        {
            "status": "test_completed",
            **git_state(),
            "test_lock_sha256": sha256(study / "test_lock.json"),
            "artifacts": {
                str(p.relative_to(output)): sha256(p) for p in output.rglob("*") if p.is_file()
            },
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True)
    parser.add_argument("--data-run", required=True)
    parser.add_argument("--config", default="params.yaml")
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        finalize(ROOT / args.study, ROOT / args.data_run, read_config(args.config))


if __name__ == "__main__":
    main()
