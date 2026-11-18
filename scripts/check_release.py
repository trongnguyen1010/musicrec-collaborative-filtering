"""Check that the demo service reproduces the official test metrics from the release alone.

Every train user is ranked through DemoService (train + validation masked, K=20) for
PureSVD, M1 and ALS, plus the refit Popularity; reserved M2 users are ranked through
DemoService.recommend_new with the same N = 1/3/5 profiles as the official M2 test.
Metrics are recomputed with the shared evaluators and compared, column by column, with
the committed official metrics.csv files. Any difference above 1e-12 fails the check.

    python scripts/check_release.py --release artifacts/releases/demo-chinh-thuc-20261026 \
        --output-dir outputs/demo/check_release_<date>
"""

import argparse
import importlib.metadata
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd

from musicrec.data.cold_start import partition_users, profile_order
from musicrec.evaluation.cold_start import evaluate_cold_start
from musicrec.evaluation.ranking import evaluate_ranking
from musicrec.serving.release import load_release
from musicrec.serving.service import DemoService, ProfileEntry

RUN = Path("outputs/chinh_thuc_cloud_20261026")
OFFICIAL = Path("docs/results/chinh_thuc_cloud_20261026")
KS = (5, 10, 20)
TOLERANCE = 1e-12
METRICS = ["precision", "recall", "ndcg", "catalog_coverage", "gini", "arp", "novelty", "ild"]


def grouped(frame: pd.DataFrame) -> dict[str, set[str]]:
    return {str(u): set(g.item_id.astype(str)) for u, g in frame.groupby("user_id")}


def compare(rows: list[dict[str, Any]], official: pd.DataFrame, keys: list[str]) -> list[str]:
    """Return mismatch descriptions between recomputed rows and the official table."""
    errors = []
    mine = pd.DataFrame(rows).set_index(keys)
    reference = official.set_index(keys)
    for index, row in mine.iterrows():
        for metric in METRICS:
            diff = abs(float(row[metric]) - float(reference.loc[index, metric]))
            if diff > TOLERANCE:
                errors.append(f"{index} {metric}: diff {diff:.3e}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    started = perf_counter()
    service = DemoService(load_release(args.release))
    release = service.release
    load_seconds = perf_counter() - started

    representations = RUN / "chuong_3/run/representations"
    test = pd.read_parquet(representations / "test.parquet")
    train_sets = grouped(release.train)
    validation_sets = {u: set() for u in train_sets} | grouped(release.validation)
    targets = {u: set() for u in train_sets} | grouped(test)
    users = service.users

    rows: list[dict[str, Any]] = []
    timings: dict[str, float] = {}
    for model in ["popularity", "pure_svd", "m1", "implicit_als"]:
        start = perf_counter()
        lists = {}
        for user in users:
            if model == "popularity":
                recs = release.popularity.recommend(user, 20, service.masked_items(user))
            else:
                recs = service.recommend_existing(user, 20, model).recommendations  # type: ignore[arg-type]
            lists[user] = [r.item_id for r in recs]
        timings[model] = perf_counter() - start
        result = evaluate_ranking(
            lists, targets, train_sets, ks=KS, split="test", validation=validation_sets
        )
        rows.extend(
            {"model": model, "seed": 42, "k": int(k), **v} for k, v in result["at_k"].items()
        )
    warm_errors = compare(rows, pd.read_csv(OFFICIAL / "test/metrics.csv"), ["model", "seed", "k"])

    split = RUN / "chuong_3/run/split"
    split_train = pd.read_parquet(split / "train.parquet")
    split_test = pd.read_parquet(split / "test.parquet")
    for frame in [split_train, split_test]:
        frame["user_id"] = frame.user_id.astype(str)
        frame["item_id"] = frame.item_id.astype(str)
    roles = json.loads((RUN / "chuong_4/m2_tuning/user_roles.json").read_text(encoding="utf-8"))
    config = json.loads((RUN / "chuong_4/m2_tuning/metrics.json").read_text(encoding="utf-8"))
    seed = config["config"]["seed"]
    if roles != partition_users(sorted(split_train.user_id.unique(), key=int), seed):
        raise RuntimeError("Saved user roles differ from the deterministic partition")
    learn = split_train[split_train.user_id.isin(roles["learning"])]
    reserved = split_train[split_train.user_id.isin(roles["reserved"])]
    counts = reserved.groupby("user_id").size()
    cold_users = sorted(counts[counts >= 5].index, key=int)
    histories = grouped(learn)
    cold_targets = {u: set(split_test.loc[split_test.user_id == u, "item_id"]) for u in cold_users}
    profiles = {}
    for user in cold_users:
        records = reserved[reserved.user_id == user].set_index("item_id")["listening_count"]
        order = profile_order(user, list(records.index), seed)
        profiles[user] = [ProfileEntry(i, float(records[i])) for i in order[:5]]
    m2_rows: list[dict[str, Any]] = []
    for n in [1, 3, 5]:
        start = perf_counter()
        lists = {
            u: [r.item_id for r in service.recommend_new(profiles[u][:n], 20).recommendations]
            for u in cold_users
        }
        timings[f"m2_n{n}"] = perf_counter() - start
        provided = {u: {e.item_id for e in profiles[u][:n]} for u in cold_users}
        result = evaluate_cold_start(lists, cold_targets, histories, provided, ks=KS)
        m2_rows.extend(
            {"n": n, "method": "m2", "k": int(k), **v} for k, v in result["at_k"].items()
        )
    m2_errors = compare(
        m2_rows, pd.read_csv(OFFICIAL / "m2/test/metrics.csv"), ["n", "method", "k"]
    )

    pd.DataFrame(rows).to_csv(args.output_dir / "warm_metrics.csv", index=False)
    pd.DataFrame(m2_rows).to_csv(args.output_dir / "m2_metrics.csv", index=False)
    report = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "release": release.version,
        "release_manifest_files": len(release.manifest["files"]),
        "tolerance": TOLERANCE,
        "warm": {"users": len(users), "rows_compared": len(rows), "mismatches": warm_errors},
        "m2": {"users": len(cold_users), "rows_compared": len(m2_rows), "mismatches": m2_errors},
        "passed": not warm_errors and not m2_errors,
        "load_seconds": load_seconds,
        "recommend_seconds": timings,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            **{
                name: importlib.metadata.version(name)
                for name in ["numpy", "scipy", "pandas", "pyarrow", "fastapi"]
            },
        },
        "command": sys.argv,
    }
    (args.output_dir / "check.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    print(
        json.dumps({k: report[k] for k in ["passed", "warm", "m2", "recommend_seconds"]}, indent=1)
    )
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
