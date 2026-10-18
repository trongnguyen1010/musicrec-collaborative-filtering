"""Validation selection and controlled ablations for M1 and strictly held-out-user M2."""

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from musicrec.configuration import ROOT, read_config, sha256, write_json
from musicrec.evaluation.evaluator import evaluate, histories
from musicrec.evaluation.ranking import ndcg_at_k
from musicrec.experiments import trial_configs
from musicrec.pipeline import git_state, interactions_from_frame, snapshot_sources
from musicrec.recommenders.extensions import ColdStartModel, Reranker, tag_features
from musicrec.recommenders.models import ItemCFRecommender, MatrixModel


def save_evaluation(
    folder: Path,
    model: Any,
    train: pd.DataFrame,
    targets: pd.DataFrame,
    ks: list[int],
    mask: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Store metric, per-user values and recommendations for one locked condition."""
    folder.mkdir(parents=True, exist_ok=False)
    metric, predictions, users = evaluate(model, train, targets, ks, mask)
    if isinstance(model, ColdStartModel):
        query_users = sorted(set(targets.user_id))
        if set(query_users) & set(model.item_cf.users):
            raise ValueError("M2 evaluation users leaked into reference model")
        tagged = model.features.getnnz(axis=1)
        routes: Counter[str] = Counter()
        empty = with_tags = unknown = no_known = 0
        for user in query_users:
            profile = model.profiles.get(user, {})
            known = [model.item_cf.item_index[i] for i in profile if i in model.item_cf.item_index]
            empty += not bool(profile)
            no_known += not bool(known)
            unknown += len(profile) - len(known)
            with_tags += bool(known and np.any(tagged[known] > 0))
            routes[model.profile_scores(profile)[1]] += 1
        metric["profile_audit"] = {
            "query_users": len(query_users),
            "component_mode": model.mode,
            "empty_profiles": empty,
            "profiles_without_known_artist": no_known,
            "unknown_profile_artists": unknown,
            "users_with_tag_profile": with_tags,
            "tag_profile_rate": with_tags / len(query_users),
            "routes": dict(routes),
            "query_users_in_reference": 0,
        }
    write_json(folder / "metrics.json", metric)
    predictions.to_parquet(folder / "predictions.parquet", index=False)
    users.to_csv(folder / "users.csv", index=False)
    return metric


def select_m1(study: Path, data: Path, config: dict[str, Any]) -> None:
    """Select full M1 within the NDCG constraint; ablations share the selected C."""
    out = study / "m1"
    out.mkdir(exist_ok=False)
    train = pd.read_parquet(data / "train.parquet")
    val = pd.read_parquet(data / "validation.parquet")
    summary = json.loads((study / "validation_summary.json").read_text())
    kind = max(summary, key=lambda name: summary[name]["validation_ndcg_at_10"])
    seed = int(config["project"]["seed"])
    base = MatrixModel.load(study / kind / f"seed_{seed}" / "model.npz")
    settings = config["experiment"]
    variants = [
        (int(c), float(w), float(p))
        for c, w, p in product(
            settings["rerank_candidates"], settings["rerank_lambda"], settings["rerank_beta"]
        )
    ]
    sums = np.zeros((len(variants), 3), dtype=float)
    mask = histories(train)
    truth = histories(val)
    ranker = Reranker(base, max(settings["rerank_candidates"]))
    for counter, (user, relevant) in enumerate(truth.items()):
        pool = ranker.pool(user, mask[user], max(settings["rerank_candidates"]))
        for j, (c, w, p) in enumerate(variants):
            ranker.candidates = c
            ranker.weight = w
            ranker.penalty = p
            recs = ranker.select(pool, 10)
            ids = [r.item_id for r in recs]
            chosen = np.array([base.item_index[i] for i in ids])
            local = {int(idx): n for n, idx in enumerate(pool[0])}
            positions = [local[int(i)] for i in chosen]
            similarities = pool[2][np.ix_(positions, positions)]
            ild = (
                float(np.mean(1 - similarities[np.triu_indices(len(ids), 1)]))
                if len(ids) > 1
                else 0.0
            )
            sums[j] += [ndcg_at_k(ids, relevant, 10), float(base.popularity[chosen].mean()), ild]
        if (counter + 1) % 400 == 0:
            print(f"M1 validation users {counter + 1}/{len(truth)}", flush=True)
    sums /= len(truth)
    minimum = summary[kind]["validation_ndcg_at_10"] * (1 - float(settings["rerank_ndcg_drop"]))
    feasible = [i for i in range(len(variants)) if sums[i, 0] >= minimum - 1e-12]
    if not feasible:
        raise RuntimeError("No feasible M1 configuration, including identity")
    best = min(feasible, key=lambda j: (sums[j, 1], -sums[j, 2], -sums[j, 0], variants[j]))
    c, w, p = variants[best]
    selected = {
        "base_kind": kind,
        "seed": seed,
        "candidates": c,
        "weight": w,
        "penalty": p,
        "validation_ndcg_at_10": float(sums[best, 0]),
        "minimum_ndcg": minimum,
        "selection": "ndcg_drop<=5%; min ARP, max ILD, max NDCG",
    }
    write_json(out / "locked.json", selected)
    write_json(
        out / "trials.json",
        [
            {
                "candidates": v[0],
                "weight": v[1],
                "penalty": v[2],
                "ndcg": float(a[0]),
                "arp": float(a[1]),
                "ild": float(a[2]),
            }
            for v, a in zip(variants, sums, strict=True)
        ],
    )
    for name, weight, penalty in (
        ("base", 1.0, 0.0),
        ("diversity", w, 0.0),
        ("popularity", 1.0, p),
        ("full", w, p),
    ):
        ranker = Reranker(base, c, weight, penalty)
        save_evaluation(out / "validation" / name, ranker, train, val, config["evaluation"]["ks"])


def cold_partitions(frame: pd.DataFrame, train: pd.DataFrame, seed: int) -> dict[str, list[str]]:
    """Reserve entire users; every evaluation user can supply the largest Given-N profile."""
    eligible = sorted(str(u) for u, n in train.groupby("user_id").size().items() if n >= 5)
    if len(eligible) < 10:
        raise ValueError("Too few eligible users for strict M2 user holdout")
    shuffled = np.random.default_rng(seed).permutation(eligible).tolist()
    n = max(1, len(shuffled) // 10)
    val = sorted(shuffled[:n])
    test = sorted(shuffled[n : 2 * n])
    reference = sorted(set(frame.user_id) - set(val) - set(test))
    return {"reference": reference, "validation": val, "test": test}


def provided_profiles(train: pd.DataFrame, users: list[str], seed: int, n: int) -> pd.DataFrame:
    """Each N is a prefix of the same deterministic per-user permutation."""
    generator = np.random.default_rng(seed)
    pieces = []
    for user in sorted(users):
        group = train[train.user_id == user].sort_values("item_id")
        ordered = generator.permutation(len(group))
        if len(group) < n:
            raise ValueError("Given-N cohort contains an insufficient profile")
        pieces.append(group.iloc[ordered[:n]])
    return pd.concat(pieces, ignore_index=True) if pieces else train.iloc[:0].copy()


def attach_profiles(model: ColdStartModel, frame: pd.DataFrame) -> None:
    """Only supplied observations are available to inference."""
    model.profiles = {
        str(u): {str(r["item_id"]): float(r["listening_count"]) for r in group.to_dict("records")}
        for u, group in frame.groupby("user_id")
    }


def select_m2(study: Path, data: Path, config: dict[str, Any]) -> None:
    """Tune on separately held-out validation users; keep cold test users untouched."""
    out = study / "m2"
    out.mkdir(exist_ok=False)
    frame = pd.read_parquet(data / "interactions.parquet")
    train = pd.read_parquet(data / "train.parquet")
    val = pd.read_parquet(data / "validation.parquet")
    settings = config["experiment"]
    seed = int(config["project"]["seed"])
    groups = cold_partitions(frame, train, seed)
    reference = frame[frame.user_id.isin(groups["reference"])].copy()
    targets = val[val.user_id.isin(groups["validation"])].copy()
    write_json(out / "user_partitions.json", groups)
    reference.to_parquet(out / "reference.parquet", index=False)
    trials = trial_configs("item_cf", settings, seed)
    best = -np.inf
    best_model = None
    best_record = None
    features = None
    for trial, params in enumerate(trials):
        print(f"M2 reference ItemCF trial {trial}", flush=True)
        item_cf = ItemCFRecommender(**params)
        item_cf.fit(interactions_from_frame(reference))
        if features is None:
            features, audit = tag_features(
                reference,
                item_cf.items,
                ROOT / settings["tags"],
                ROOT / settings["tag_names"],
                settings["tag_encoding"],
            )
            if set(audit["tag_users"]) & (set(groups["validation"]) | set(groups["test"])):
                raise RuntimeError("M2 tag leakage")
            write_json(out / "tag_audit.json", audit)
        for alpha, threshold in product(settings["m2_alpha"], settings["m2_history_threshold"]):
            model = ColdStartModel(item_cf, features, float(alpha), int(threshold))
            scores = []
            for n in settings["given_n"]:
                profiles = provided_profiles(train, groups["validation"], seed, int(n))
                attach_profiles(model, profiles)
                masks = histories(profiles)
                truth = histories(targets)
                values = [
                    ndcg_at_k(
                        [r.item_id for r in model.recommend(u, 10, masks.get(u, set()))],
                        relevant,
                        10,
                    )
                    for u, relevant in truth.items()
                ]
                scores.append(float(np.mean(values)))
            value = float(np.mean(scores))
            record = {
                "item_cf": params,
                "alpha": float(alpha),
                "threshold": int(threshold),
                "mean_validation_ndcg": value,
                "by_n": scores,
            }
            write_json(out / f"trial_{trial}_{alpha}_{threshold}.json", record)
            if value > best + 1e-12:
                best = value
                best_model = model
                best_record = record
    if best_model is None:
        raise RuntimeError("No M2 configuration selected")
    best_model.save(out / "model")
    write_json(out / "locked.json", best_record)
    for n in settings["given_n"]:
        profiles = provided_profiles(train, groups["validation"], seed, int(n))
        profiles.to_parquet(out / f"validation_profile_{n}.parquet", index=False)
        for mode in ("popularity", "content", "cf", "combined"):
            model = ColdStartModel(
                best_model.item_cf, features, best_model.alpha, best_model.threshold, mode
            )
            attach_profiles(model, profiles)
            save_evaluation(
                out / "validation" / f"n_{n}" / mode,
                model,
                reference,
                targets,
                config["evaluation"]["ks"],
                profiles,
            )


def main() -> None:
    """Run M1 then M2 validation; test evaluation is a separately locked command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True)
    parser.add_argument("--data-run", required=True)
    parser.add_argument("--config", default="params.yaml")
    parser.add_argument("--component", choices=["all", "m1", "m2"], default="all")
    args = parser.parse_args()
    study = ROOT / args.study
    data = ROOT / args.data_run
    config = read_config(args.config)
    source_folder = study / f"extensions_source_{args.component}"
    source_folder.mkdir(exist_ok=False)
    source_hash = snapshot_sources(source_folder)
    with threadpool_limits(limits=1):
        if args.component in ("all", "m1"):
            select_m1(study, data, config)
        if args.component in ("all", "m2"):
            select_m2(study, data, config)
    write_json(
        study / "extensions_manifest.json",
        {
            **git_state(),
            "test_evaluated": False,
            "effective_config": config,
            "source_snapshot_sha256": source_hash,
            "tag_sha256": sha256(ROOT / config["experiment"]["tags"]),
            "tag_names_sha256": sha256(ROOT / config["experiment"]["tag_names"]),
            "status": "validation_completed",
        },
    )


if __name__ == "__main__":
    main()
