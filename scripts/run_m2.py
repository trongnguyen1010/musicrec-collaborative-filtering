"""Run Step 16 on disjoint tuning users and supplied profiles; reserve test for Step 17."""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.metadata  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from itertools import product  # noqa: E402
from pathlib import Path  # noqa: E402
from time import perf_counter  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import psutil  # noqa: E402
import yaml  # noqa: E402

from musicrec.data.cold_start import partition_users, profile_order  # noqa: E402
from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.cold_start import evaluate_cold_start, select_m2_config  # noqa: E402
from musicrec.recommenders.m2 import M2Recommender, mix_profile_scores  # noqa: E402
from musicrec.recommenders.popularity import PopularityRecommender  # noqa: E402


def main() -> None:
    """Fit shared components once, evaluate all nine mixtures and three matching controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/models/m2.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    def guard(event: str, values: tuple) -> None:
        if event == "open" and isinstance(values[0], (str, bytes)):
            if Path(os.fsdecode(values[0])).name == "test.parquet":
                raise RuntimeError("Step 16 must never open test.parquet, including hashing")

    sys.addaudithook(guard)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def read(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def write(path: Path, data: dict) -> None:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, allow_nan=False)
            handle.write("\n")

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    expected = {
        "step": 16,
        "seed": 42,
        "profile_sizes": [0, 1, 3, 5],
        "minimum_train_profile_size": 5,
        "alpha_grid": [0.25, 0.5, 0.75],
        "history_threshold_grid": [3, 5, 10],
        "tag_min_artist_df": 2,
        "item_cf": {"neighbors": 40, "shrinkage": 0},
        "ks": [5, 10, 20],
        "baselines": ["popularity", "content", "item_cf"],
        "test_file_read": False,
    }
    if any(config.get(k) != v for k, v in expected.items()):
        raise ValueError("Expected the predeclared Step 16 grid and cold-user protocol")
    split, clean, out = (
        Path(config["split_run"]).resolve(),
        Path(config["clean_run"]).resolve(),
        args.output_dir.resolve(),
    )
    if out.exists() or any(out == p or p in out.parents for p in [split, clean]):
        raise ValueError("Output must be a new directory outside source runs")
    inputs = {}

    def pin(path: Path, digest: str | None = None) -> None:
        actual = sha(path)
        if digest is not None and digest != actual:
            raise ValueError(f"Checksum mismatch: {path}")
        inputs[str(path)] = actual

    for directory, step, names in [
        (split, 4, ["train.parquet", "validation.parquet", "id_mappings.json"]),
        (clean, 3, ["tag_assignments.parquet", "tags.parquet"]),
    ]:
        metadata = read(directory / "metrics.json")
        if metadata["step"] != step or (step == 4 and metadata["seed"] != 42):
            raise ValueError("Expected verified source split and cleaning runs")
        pin(directory / "metrics.json")
        for name in names:
            pin(directory / name, metadata["output_sha256"][name])
    pin(args.config.resolve())
    train = pd.read_parquet(split / "train.parquet")
    validation = pd.read_parquet(split / "validation.parquet")
    roles = partition_users(sorted(train.user_id.unique(), key=int), config["seed"])
    learn = train[train.user_id.isin(roles["learning"])].copy()
    tuning = train[train.user_id.isin(roles["tuning"])].copy()
    eligible = tuning.groupby("user_id").size()
    users = sorted(eligible[eligible >= 5].index, key=int)
    if not users:
        raise ValueError("No tuning users have five train profile observations")
    if set(roles["learning"]) & set(users) or set(roles["reserved"]) & set(users):
        raise RuntimeError("M2 roles overlap")
    interactions = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count))
        for r in learn.itertuples(index=False)
    ]
    histories = {str(u): set(g.item_id.astype(str)) for u, g in learn.groupby("user_id")}
    targets = {
        u: set(validation.loc[validation.user_id == u, "item_id"].astype(str)) for u in users
    }
    assignments, dictionary = (
        pd.read_parquet(clean / "tag_assignments.parquet"),
        pd.read_parquet(clean / "tags.parquet"),
    )
    values = dictionary.set_index("tagID")["tagValue"].to_dict()
    tags = ((r.userID, r.artistID, values[r.tagID]) for r in assignments.itertuples(index=False))
    out.mkdir(parents=True, exist_ok=False)
    write(out / "experiment.json", config)
    write(out / "user_roles.json", roles)
    tick = perf_counter()
    model = M2Recommender(min_tag_df=2).fit(interactions, tags=tags)
    fit_seconds = perf_counter() - tick
    profiles, profile_rows = {}, []
    for user in users:
        records = tuning[tuning.user_id == user].set_index("item_id")["listening_count"].to_dict()
        order = profile_order(user, list(records), config["seed"])
        profiles[user] = [Interaction(user, item, float(records[item])) for item in order[:5]]
        for rank, row in enumerate(profiles[user], 1):
            profile_rows.append(
                {
                    "user_id": user,
                    "rank": rank,
                    "item_id": row.item_id,
                    "listening_count": row.listening_count,
                    "proxy_score": model._proxy(row).proxy_score,
                    "in_catalog": row.item_id in model._item_index,
                    "has_tags": row.item_id in model._item_index
                    and bool(model._tagged[model._item_index[row.item_id]]),
                }
            )
    pd.DataFrame(profile_rows).to_csv(out / "profiles.csv", index=False)
    write(
        out / "cohort.json",
        {
            "users": users,
            "tuning_users_total": len(roles["tuning"]),
            "excluded_below_five_train": len(roles["tuning"]) - len(users),
            "reserved_users_not_evaluated": len(roles["reserved"]),
            "targets": {u: sorted(v, key=int) for u, v in targets.items()},
            "learning_catalog": model._items,
        },
    )
    grid = list(product(config["alpha_grid"], config["history_threshold_grid"]))
    labels = {f"alpha_{a:g}_threshold_{t}": (a, t) for a, t in grid}
    methods = [*config["baselines"], *labels]
    evaluations, rows, diagnostics, costs = {}, [], [], {}
    popularity_control = PopularityRecommender().fit(interactions)
    for n in config["profile_sizes"]:
        directory = out / f"n_{n}"
        directory.mkdir()
        ranks, record_rows = {m: {} for m in methods}, {m: [] for m in methods}
        sort_seconds = {m: 0.0 for m in methods}
        profile_seconds = []
        provided = {u: {r.item_id for r in profiles[u][:n]} for u in users}
        for user in users:
            tick = perf_counter()
            model.set_profile(user, profiles[user][:n])
            features = model.profile_scores(user)
            profile_seconds.append(perf_counter() - tick)
            candidates = np.array([i not in provided[user] for i in model._items])
            known = [
                model._item_index[r.item_id]
                for r in profiles[user][:n]
                if r.item_id in model._item_index
            ]
            diagnostics.append(
                {
                    "n": n,
                    "user_id": user,
                    "provided": n,
                    "known_profile_artists": len(known),
                    "tagged_profile_artists": int(model._tagged[known].sum()),
                    "cf_supported_candidates": int(features.cf_available[candidates].sum()),
                    "content_available_candidates": int(
                        features.content_available[candidates].sum()
                    ),
                    "no_cf_candidates": not features.cf_available[candidates].any(),
                    "no_content_candidates": not features.content_available[candidates].any(),
                }
            )
            component_scores = {
                "popularity": features.popularity,
                "content": np.where(
                    features.content_available, features.content, features.popularity
                ),
                "item_cf": np.where(features.cf_available, features.cf, features.popularity),
            }
            for name in methods:
                tick = perf_counter()
                scores = (
                    component_scores[name]
                    if name in component_scores
                    else mix_profile_scores(features, *labels[name])
                )
                recs = model.rank_scores(user, scores, 20, provided[user], reason=f"m2_{name}")
                sort_seconds[name] += perf_counter() - tick
                ranks[name][user] = [r.item_id for r in recs]
                for rank, rec in enumerate(recs, 1):
                    i = model._item_index[rec.item_id]
                    record_rows[name].append(
                        {
                            "user_id": user,
                            "rank": rank,
                            "item_id": rec.item_id,
                            "score": rec.score,
                            "cf_available": bool(features.cf_available[i]),
                            "content_available": bool(features.content_available[i]),
                            "reason": "popularity_empty_profile" if n == 0 else rec.reason,
                        }
                    )
            if ranks["popularity"][user] != [
                r.item_id for r in popularity_control.recommend(user, 20, provided[user])
            ]:
                raise RuntimeError("Popularity component changed the control order")
            if n == 0 and any(ranks[m][user] != ranks["popularity"][user] for m in methods):
                raise RuntimeError("All N=0 branches must recover the Popularity item order")
        evaluations[n] = {}
        for name in methods:
            target = directory / name
            target.mkdir()
            tick = perf_counter()
            result = evaluate_cold_start(ranks[name], targets, histories, provided, ks=(5, 10, 20))
            eval_seconds = perf_counter() - tick
            if result["users_eligible"] == 0:
                raise ValueError("No tuning users have catalog targets")
            evaluations[n][name] = result
            write(target / "evaluation.json", result)
            pd.DataFrame(record_rows[name]).to_csv(target / "recommendations.csv", index=False)
            for k, metrics in result["at_k"].items():
                rows.append({"n": n, "method": name, "k": int(k), **metrics})
            costs[f"{n}/{name}"] = {
                "sort_and_mix_seconds": sort_seconds[name],
                "evaluation_seconds": eval_seconds,
            }
            print(f"N={n} {name} NDCG@10={result['at_k']['10']['ndcg']:.10f}", flush=True)
        costs[f"{n}/profile_features"] = {
            "total_seconds": sum(profile_seconds),
            "mean_ms_per_user": float(np.mean(profile_seconds) * 1000),
            "p95_ms_per_user": float(np.quantile(profile_seconds, 0.95) * 1000),
        }
    selection_rows = [
        {
            "alpha": a,
            "history_threshold": t,
            "method": label,
            "ndcg_by_n": {n: evaluations[n][label]["at_k"]["10"]["ndcg"] for n in [1, 3, 5]},
        }
        for label, (a, t) in labels.items()
    ]
    selection = select_m2_config(selection_rows)
    write(
        out / "selection.json",
        {
            "winner": selection,
            "grid": selection_rows,
            "reserved_users_used": False,
            "test_file_read": False,
        },
    )
    model.alpha, model.history_threshold = selection["alpha"], selection["history_threshold"]
    model.save(out / "model")
    restored = M2Recommender.load(out / "model")
    verified, tick = 0, perf_counter()
    for n in [0, 1, 3, 5]:
        expected_path = out / f"n_{n}" / selection["method"] / "recommendations.csv"
        frame = pd.read_csv(
            expected_path, dtype={"user_id": str, "item_id": str}, float_precision="round_trip"
        )
        for user, group in frame.groupby("user_id", sort=False):
            restored.set_profile(user, profiles[user][:n])
            recs = restored.recommend(user, 20, {r.item_id for r in profiles[user][:n]})
            if [r.item_id for r in recs] != group.item_id.tolist() or not np.array_equal(
                [r.score for r in recs], group.score.to_numpy()
            ):
                raise RuntimeError("Saved M2 reload changed selected recommendations or scores")
            verified += 1
    reload_seconds = perf_counter() - tick
    pd.DataFrame(rows).to_csv(out / "metrics.csv", index=False)
    pd.DataFrame(diagnostics).to_csv(out / "profile_diagnostics.csv", index=False)
    code = out / "code"
    root = Path(__file__).resolve().parents[1]
    paths = [
        Path(__file__),
        args.config,
        root / "src/musicrec/data/cold_start.py",
        root / "src/musicrec/data/contracts.py",
        root / "src/musicrec/evaluation/cold_start.py",
        root / "src/musicrec/evaluation/ranking.py",
        root / "src/musicrec/recommenders/m2.py",
        root / "src/musicrec/recommenders/item_cf.py",
        root / "src/musicrec/recommenders/popularity.py",
        root / "src/musicrec/recommenders/base.py",
        root / "tests/unit/test_m2.py",
    ]
    for path in paths:
        destination = code / path.resolve().relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    if any(sha(Path(p)) != digest for p, digest in inputs.items()):
        raise RuntimeError("A source or experiment configuration changed")
    write(
        out / "metrics.json",
        {
            "step": 16,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "config": config,
            "selection": selection,
            "learning_users": len(roles["learning"]),
            "tuning_users": len(users),
            "reserved_users_not_evaluated": len(roles["reserved"]),
            "learning_interactions": len(interactions),
            "catalog_size": len(model._items),
            "variant_profile_evaluations": len(methods) * 4,
            "shared_fit_calls": 1,
            "fit_seconds": fit_seconds,
            "feature_report": model.feature_report,
            "profile_sizes": config["profile_sizes"],
            "timing_seconds": costs,
            "reload_verified_lists": verified,
            "reload_seconds": reload_seconds,
            "model_bytes": sum(p.stat().st_size for p in (out / "model").rglob("*") if p.is_file()),
            "process_peak_working_set_bytes": psutil.Process().memory_info().peak_wset
            if sys.platform == "win32"
            else None,
            "memory_scope": "whole process including grid results, tag fitting and reload",
            "input_sha256": inputs,
            "inputs_unchanged": True,
            "test_file_read": False,
            "reserved_users_evaluated": False,
            "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "git_status": subprocess.check_output(["git", "status", "--short"], text=True),
            "git_diff_sha256": hashlib.sha256(subprocess.check_output(["git", "diff"])).hexdigest(),
            "runtime": {
                "python": sys.version,
                **{
                    n: importlib.metadata.version(n)
                    for n in ["numpy", "scipy", "pandas", "pyarrow"]
                },
            },
            "command": sys.argv,
            "code_sha256": {
                p.relative_to(code).as_posix(): sha(p) for p in code.rglob("*") if p.is_file()
            },
            "output_sha256": {
                p.relative_to(out).as_posix(): sha(p)
                for p in out.rglob("*")
                if p.is_file() and code not in p.parents
            },
        },
    )
    print(json.dumps(selection), flush=True)


if __name__ == "__main__":
    main()
