"""E-S: sensitivity table around grid boundaries, validation only (configs/e_s_sensitivity.yaml).

Baselines run through the existing validation runners (run_baseline.py) with
--tuning-config pointing at the E-S file, seed 42, so the evaluation is identical to the
Chapter 4 tuning. M2 reuses the locked Step 16 model (learning users only) and rescores the
tuning users' validation targets for every (alpha, n_min) point; the locked point must
reproduce the saved Step 16 NDCG@10 exactly. Nothing is selected or locked here.
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_e7_topn import runtime  # noqa: E402
from tune_validation import BASE_CONFIGS, ROOT, RUNNERS, name_of  # noqa: E402

from musicrec.data.cold_start import profile_order  # noqa: E402
from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.cold_start import evaluate_cold_start  # noqa: E402
from musicrec.recommenders.m2 import M2Recommender, mix_profile_scores  # noqa: E402

REPRESENTATIONS = Path("outputs/chinh_thuc_cloud_20261026/chuong_3/run/representations")
M2_RUN = Path("outputs/chinh_thuc_cloud_20261026/chuong_4/m2_tuning")
STOCHASTIC = {"pure_svd", "implicit_als"}


def run_baseline(model: str, point: dict[str, Any], root: Path, settings: Path) -> dict[str, Any]:
    base = yaml.safe_load((ROOT / BASE_CONFIGS[model]).read_text(encoding="utf-8"))
    out = root / model / name_of(model, point)
    config_path = root / "configs" / f"{out.name}.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.safe_dump({**base, **point}, sort_keys=False), "utf-8")
    command = [
        sys.executable,
        "-B",
        str(ROOT / "scripts" / RUNNERS[model]),
        "--representations-run",
        str(REPRESENTATIONS.resolve()),
        "--config",
        str(config_path),
        "--output-dir",
        str(out.resolve()),
        "--tuning-config",
        str(settings.resolve()),
    ]
    if model in STOCHASTIC:
        command += ["--model-seed", "42"]
    start = perf_counter()
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
    seconds = perf_counter() - start
    metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
    return {
        "model": model,
        **point,
        "run": out.name,
        "seed": 42,
        "ndcg_at_10": metrics["at_k"]["10"]["ndcg"],
        "recall_at_10": metrics["at_k"]["10"]["recall"],
        "best_epoch": metrics.get("supplementary", {}).get("best_epoch"),
        "wall_seconds": seconds,
    }


def run_m2(settings: dict[str, Any], out: Path) -> list[dict[str, Any]]:
    """Rescore tuning users for every (alpha, n_min); returns one row per point and N."""
    experiment = json.loads((M2_RUN / "experiment.json").read_text(encoding="utf-8"))
    split = Path(experiment["split_run"])
    train = pd.read_parquet(split / "train.parquet")
    validation = pd.read_parquet(split / "validation.parquet")
    roles = json.loads((M2_RUN / "user_roles.json").read_text(encoding="utf-8"))
    cohort = json.loads((M2_RUN / "cohort.json").read_text(encoding="utf-8"))
    users = cohort["users"]
    learn = train[train.user_id.isin(roles["learning"])]
    tuning = train[train.user_id.isin(roles["tuning"])]
    histories = {str(u): set(g.item_id.astype(str)) for u, g in learn.groupby("user_id")}
    targets = {
        u: set(validation.loc[validation.user_id == u, "item_id"].astype(str)) for u in users
    }
    model = M2Recommender.load(M2_RUN / "model")
    profiles = {}
    for user in users:
        records = tuning[tuning.user_id == user].set_index("item_id")["listening_count"].to_dict()
        order = profile_order(user, list(records), experiment["seed"])
        profiles[user] = [Interaction(user, i, float(records[i])) for i in order[:5]]
    saved = pd.read_csv(M2_RUN / "metrics.csv")
    points = [(a, t) for a in settings["alpha"] for t in settings["history_threshold"]]
    rows = []
    for n in experiment["profile_sizes"]:
        provided = {u: {r.item_id for r in profiles[u][:n]} for u in users}
        ranks: dict[tuple[float, int], dict[str, list[str]]] = {p: {} for p in points}
        for user in users:
            model.set_profile(user, profiles[user][:n])
            features = model.profile_scores(user)
            for alpha, threshold in points:
                scores = mix_profile_scores(features, alpha, threshold)
                recs = model.rank_scores(user, scores, 20, provided[user], reason="m2")
                ranks[(alpha, threshold)][user] = [r.item_id for r in recs]
        for (alpha, threshold), lists in ranks.items():
            result = evaluate_cold_start(lists, targets, histories, provided, ks=(5, 10, 20))
            ndcg = result["at_k"]["10"]["ndcg"]
            label = f"alpha_{alpha:g}_threshold_{threshold}"
            match = saved[(saved.n == n) & (saved.method == label) & (saved.k == 10)]
            if len(match) and abs(float(match.ndcg.iloc[0]) - ndcg) > 1e-12:
                raise RuntimeError(f"{label} N={n} does not reproduce the Step 16 result")
            rows.append(
                {
                    "model": "m2",
                    "alpha": alpha,
                    "history_threshold": threshold,
                    "n": n,
                    "users_eligible": result["users_eligible"],
                    "ndcg_at_10": ndcg,
                    "reproduces_step16": bool(len(match)),
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(out / "m2_validation.csv", index=False)
    mean = (
        frame[frame.n.isin([1, 3, 5])]
        .groupby(["alpha", "history_threshold"])
        .ndcg_at_10.mean()
        .rename("mean_ndcg_at_10_n135")
        .reset_index()
    )
    mean.to_csv(out / "m2_mean_n135.csv", index=False)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/e_s_sensitivity.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=None, help="timing: first N points/model")
    args = parser.parse_args()
    settings = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    models = args.models or [*settings["models"], "m2"]
    rows = []
    for model in models:
        start = perf_counter()
        if model == "m2":
            run_m2(settings["m2"], args.output_dir)
            print(f"m2 done in {perf_counter() - start:.1f}s", flush=True)
            continue
        for point in settings["models"][model]["points"][: args.limit]:
            rows.append(run_baseline(model, point, args.output_dir, args.config))
            print(json.dumps(rows[-1]), flush=True)
    if rows:
        path = args.output_dir / "baselines_validation.csv"
        frame = pd.DataFrame(rows)
        if path.exists():
            frame = pd.concat([pd.read_csv(path), frame], ignore_index=True)
        frame.to_csv(path, index=False)
    meta = {"created_at_utc": datetime.now(UTC).isoformat(), "command": sys.argv, **runtime()}
    (args.output_dir / f"metrics_{datetime.now(UTC):%Y%m%dT%H%M%S}.json").write_text(
        json.dumps(meta, indent=2) + "\n", "utf-8"
    )


if __name__ == "__main__":
    main()
