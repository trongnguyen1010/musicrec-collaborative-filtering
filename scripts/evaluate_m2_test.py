"""Step 17: score the validation-selected M2 once on the reserved users' test pairs.

The saved Step 16 model is loaded, never refit. The lock (selected alpha/threshold, model
hashes, cohort rule and predeclared comparisons) is written before test.parquet is opened.
Reserved users supply nested train profiles (N = 0/1/3/5); their test pairs are the targets.
Learning-user statistics stay the only source of catalog, popularity, novelty and ILD.
Per comparison: mean per-user NDCG@10 difference, 95% user bootstrap CI (1,000 resamples,
seed 42), two-sided Wilcoxon signed-rank p and Holm adjustment over all predeclared pairs.
"""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.metadata  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_statistics import holm  # noqa: E402

from musicrec.data.cold_start import partition_users, profile_order  # noqa: E402
from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.cold_start import evaluate_cold_start  # noqa: E402
from musicrec.recommenders.m2 import M2Recommender  # noqa: E402

PROFILE_SIZES = [0, 1, 3, 5]
METHODS = ["popularity", "content", "item_cf", "m2"]
PAIRS: list[tuple[str, str, int]] = [
    ("m2", b, n) for n in [1, 3, 5] for b in ["popularity", "content", "item_cf"]
]
PRIMARY = ("m2", "popularity", 3)
RESAMPLES = 1000
SEED = 42


def sha256(path: Path) -> str:
    """Hex SHA-256 of one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(directory: Path) -> dict[str, str]:
    """SHA-256 of every file below a directory, keyed by relative path."""
    return {
        p.relative_to(directory).as_posix(): sha256(p)
        for p in sorted(directory.rglob("*"))
        if p.is_file()
    }


def compare(a: dict[str, float], b: dict[str, float], rng: np.random.Generator) -> dict[str, Any]:
    """Paired difference, bootstrap CI and Wilcoxon p on one shared eligible cohort."""
    if a.keys() != b.keys():
        raise ValueError("Paired methods must share the eligible cohort")
    users = sorted(a, key=int)
    diff = np.array([a[u] - b[u] for u in users])
    boot = diff[rng.integers(0, len(diff), size=(RESAMPLES, len(diff)))].mean(axis=1)
    nonzero = int(np.count_nonzero(diff))
    return {
        "users": len(users),
        "nonzero_differences": nonzero,
        "mean_a": float(np.mean([a[u] for u in users])),
        "mean_b": float(np.mean([b[u] for u in users])),
        "mean_difference": float(diff.mean()),
        "ci95_low": float(np.percentile(boot, 2.5)),
        "ci95_high": float(np.percentile(boot, 97.5)),
        "wilcoxon_p": float(wilcoxon(diff, zero_method="wilcox").pvalue) if nonzero else 1.0,
    }


def main() -> None:
    """Write lock.json, then evaluate reserved users on test exactly once."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m2-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    m2_run, out = args.m2_run.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    metadata = json.loads((m2_run / "metrics.json").read_text(encoding="utf-8"))
    config = metadata["config"]
    selection = json.loads((m2_run / "selection.json").read_text(encoding="utf-8"))
    if selection["reserved_users_used"] or selection["test_file_read"]:
        raise RuntimeError("Step 16 must not have touched reserved users or test")
    split = Path(config["split_run"]).resolve()
    lock: dict[str, Any] = {
        "step": 17,
        "locked_at_utc": datetime.now(UTC).isoformat(),
        "m2_run": str(m2_run),
        "selected": {
            "alpha": selection["winner"]["alpha"],
            "history_threshold": selection["winner"]["history_threshold"],
            "validation_mean_ndcg_at_10_n135": selection["winner"]["mean_ndcg_at_10"],
        },
        "m2_metrics_sha256": sha256(m2_run / "metrics.json"),
        "selection_sha256": sha256(m2_run / "selection.json"),
        "user_roles_sha256": sha256(m2_run / "user_roles.json"),
        "model_sha256": tree_hashes(m2_run / "model"),
        "cohort": "reserved_users_with_at_least_five_train_interactions",
        "profiles": "profile_order_seed_42_nested_prefix_of_train_artists",
        "targets": "test_pairs_intersect_learning_catalog",
        "profile_sizes": PROFILE_SIZES,
        "methods": METHODS,
        "comparison_pairs": PAIRS,
        "primary_comparison": PRIMARY,
        "metric": "ndcg@10",
        "git_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip(),
    }
    (out / "lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    lock_hash = sha256(out / "lock.json")

    split_meta = json.loads((split / "metrics.json").read_text(encoding="utf-8"))
    for name in ["train.parquet", "test.parquet"]:
        if sha256(split / name) != split_meta["output_sha256"][name]:
            raise ValueError(f"Checksum mismatch: {name}")
    train = pd.read_parquet(split / "train.parquet")
    test = pd.read_parquet(split / "test.parquet")
    roles = json.loads((m2_run / "user_roles.json").read_text(encoding="utf-8"))
    if roles != partition_users(sorted(train.user_id.unique(), key=int), config["seed"]):
        raise RuntimeError("Saved user roles differ from the deterministic partition")
    learn = train[train.user_id.isin(roles["learning"])]
    reserved = train[train.user_id.isin(roles["reserved"])]
    counts = reserved.groupby("user_id").size()
    users = sorted(counts[counts >= 5].index, key=int)
    histories = {str(u): set(g.item_id.astype(str)) for u, g in learn.groupby("user_id")}
    targets = {u: set(test.loc[test.user_id == u, "item_id"].astype(str)) for u in users}
    model = M2Recommender.load(m2_run / "model")
    if (model.alpha, model.history_threshold) != (
        lock["selected"]["alpha"],
        lock["selected"]["history_threshold"],
    ):
        raise RuntimeError("Saved model does not carry the selected configuration")
    profiles = {}
    for user in users:
        records = reserved[reserved.user_id == user].set_index("item_id")["listening_count"]
        order = profile_order(user, list(records.index), config["seed"])
        profiles[user] = [Interaction(user, i, float(records[i])) for i in order[:5]]

    rows: list[dict[str, Any]] = []
    per_user: dict[tuple[str, int], dict[str, float]] = {}
    for n in PROFILE_SIZES:
        provided = {u: {r.item_id for r in profiles[u][:n]} for u in users}
        ranks: dict[str, dict[str, list[str]]] = {m: {} for m in METHODS}
        for user in users:
            model.set_profile(user, profiles[user][:n])
            features = model.profile_scores(user)
            component = {
                "popularity": features.popularity,
                "content": np.where(
                    features.content_available, features.content, features.popularity
                ),
                "item_cf": np.where(features.cf_available, features.cf, features.popularity),
            }
            for name, scores in component.items():
                recs = model.rank_scores(user, scores, 20, provided[user], reason=f"m2_{name}")
                ranks[name][user] = [r.item_id for r in recs]
            ranks["m2"][user] = [r.item_id for r in model.recommend(user, 20, provided[user])]
        if n == 0 and any(ranks[m] != ranks["popularity"] for m in METHODS):
            raise RuntimeError("All N=0 branches must recover the Popularity order")
        for name in METHODS:
            result = evaluate_cold_start(ranks[name], targets, histories, provided, ks=(5, 10, 20))
            result["split"] = "test"
            target = out / f"n_{n}" / name
            target.mkdir(parents=True)
            (target / "evaluation.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            per_user[(name, n)] = {
                u: float(v["at_k"]["10"]["ndcg"])
                for u, v in result["per_user"].items()
                if v["eligible"]
            }
            for k, metrics in result["at_k"].items():
                rows.append(
                    {
                        "n": n,
                        "method": name,
                        "k": int(k),
                        "users_eligible": result["users_eligible"],
                        **metrics,
                    }
                )
            print(f"N={n} {name} NDCG@10={result['at_k']['10']['ndcg']:.10f}", flush=True)
    pd.DataFrame(rows).to_csv(out / "metrics.csv", index=False)

    rng = np.random.default_rng(SEED)
    stats = [
        {"a": a, "b": b, "n": n, **compare(per_user[(a, n)], per_user[(b, n)], rng)}
        for a, b, n in PAIRS
    ]
    for row, adjusted in zip(stats, holm([r["wilcoxon_p"] for r in stats]), strict=True):
        row["holm_p"] = adjusted
    (out / "statistics_ndcg_at_10.json").write_text(
        json.dumps(
            {
                "metric": "ndcg@10",
                "bootstrap": {"resamples": RESAMPLES, "seed": SEED, "unit": "user"},
                "test": "two_sided_wilcoxon_signed_rank_zero_differences_dropped",
                "adjustment": "holm_over_predeclared_pairs",
                "primary": PRIMARY,
                "pairs": stats,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    git_status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    (out / "metrics.json").write_text(
        json.dumps(
            {
                "step": 17,
                "created_at_utc": datetime.now(UTC).isoformat(),
                "lock_sha256": lock_hash,
                "lock_unchanged": sha256(out / "lock.json") == lock_hash,
                "reserved_users_total": len(roles["reserved"]),
                "reserved_users_evaluated": len(users),
                "learning_users": len(roles["learning"]),
                "catalog_size": len(model._items),
                "test_pairs_of_cohort": sum(len(v) for v in targets.values()),
                "input_sha256": {
                    name: sha256(split / name) for name in ["train.parquet", "test.parquet"]
                },
                "git_sha": lock["git_sha"],
                "git_status": git_status.stdout,
                "command": sys.argv,
                "runtime": {
                    "python": sys.version,
                    "platform": platform.platform(),
                    **{
                        p: importlib.metadata.version(p)
                        for p in ["numpy", "scipy", "pandas", "pyarrow"]
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
