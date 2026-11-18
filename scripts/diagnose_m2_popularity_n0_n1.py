"""Read-only diagnosis: why Popularity has the same NDCG@10 at N = 0 and N = 1 (Table 4.13).

Rebuilds, with the locked M2 model of the official run, the Popularity lists of the reserved
users at N = 0 and N = 1 exactly as scripts/evaluate_m2_test.py does (target mode test_pairs:
user roles from user_roles.json, train/test of the split, profile_order seed 42,
rank_scores on features.popularity), then reports per user whether the supplied artist is in
the Popularity top-10, whether any target lies in the top-10, and whether NDCG@10 changes.
Nothing is refit and no existing file is written; results go to a new --output-dir.

    python -B scripts/diagnose_m2_popularity_n0_n1.py \
        --output-dir outputs/chuong_4_bo_sung_3/popularity_n0_n1
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from musicrec.data.cold_start import partition_users, profile_order
from musicrec.data.contracts import Interaction
from musicrec.evaluation.cold_start import evaluate_cold_start
from musicrec.recommenders.m2 import M2Recommender

RUN = Path("outputs/chinh_thuc_cloud_20261026")
M2_RUN = RUN / "chuong_4/m2_tuning"
SPLIT = RUN / "chuong_3/run/split"
LOCKED = Path("outputs/chuong_4_bo_sung_2/thong_ke/m2_test")
SEED = 42
K = 10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out: Path = args.output_dir
    out.mkdir(parents=True, exist_ok=False)

    split_meta = json.loads((SPLIT / "metrics.json").read_text(encoding="utf-8"))
    for name in ["train.parquet", "test.parquet"]:
        if sha256(SPLIT / name) != split_meta["output_sha256"][name]:
            raise ValueError(f"Checksum mismatch: {name}")
    train = pd.read_parquet(SPLIT / "train.parquet")
    test = pd.read_parquet(SPLIT / "test.parquet")
    roles = json.loads((M2_RUN / "user_roles.json").read_text(encoding="utf-8"))
    if roles != partition_users(sorted(train.user_id.unique(), key=int), SEED):
        raise RuntimeError("Saved user roles differ from the deterministic partition")
    learn = train[train.user_id.isin(roles["learning"])]
    reserved = train[train.user_id.isin(roles["reserved"])]
    counts = reserved.groupby("user_id").size()
    users = sorted(counts[counts >= 5].index, key=int)
    histories = {str(u): set(g.item_id.astype(str)) for u, g in learn.groupby("user_id")}
    test_items = {u: set(test.loc[test.user_id == u, "item_id"].astype(str)) for u in users}
    model = M2Recommender.load(M2_RUN / "model")

    lists: dict[int, dict[str, list[str]]] = {0: {}, 1: {}}
    supplied: dict[str, str] = {}
    for user in users:
        records = reserved[reserved.user_id == user].set_index("item_id")["listening_count"]
        order = profile_order(user, list(records.index), SEED)
        profile = [Interaction(user, i, float(records[i])) for i in order[:5]]
        supplied[user] = profile[0].item_id
        for n in (0, 1):
            provided = {r.item_id for r in profile[:n]}
            model.set_profile(user, profile[:n])
            features = model.profile_scores(user)
            recs = model.rank_scores(user, features.popularity, 20, provided, reason="diag")
            lists[n][user] = [r.item_id for r in recs]

    evals = {}
    for n in (0, 1):
        given = {u: ({supplied[u]} if n else set()) for u in users}
        evals[n] = evaluate_cold_start(lists[n], test_items, histories, given, ks=(5, 10, 20))
        locked = json.loads(
            (LOCKED / f"n_{n}/popularity/evaluation.json").read_text(encoding="utf-8")
        )
        if not np.isclose(evals[n]["at_k"]["10"]["ndcg"], locked["at_k"]["10"]["ndcg"], 0, 1e-12):
            raise RuntimeError(f"N={n}: rebuilt NDCG@10 differs from the locked evaluation")

    catalog = set(model._items)
    rows: list[dict[str, Any]] = []
    for user in users:
        top0, top1 = lists[0][user][:K], lists[1][user][:K]
        targets = test_items[user] & catalog
        in_top = supplied[user] in top0
        removed_pos = top0.index(supplied[user]) + 1 if in_top else None
        target_pos = [p + 1 for p, i in enumerate(top0) if i in targets]
        v0 = evals[0]["per_user"][user]
        v1 = evals[1]["per_user"][user]
        rows.append(
            {
                "user_id": user,
                "eligible": bool(v0["eligible"]),
                "supplied_artist": supplied[user],
                "supplied_in_pop_top10": in_top,
                "supplied_rank_in_pop_top10": removed_pos,
                "target_positions_in_n0_top10": " ".join(map(str, target_pos)),
                "promoted_artist_n1": (set(top1) - set(top0)).pop() if in_top else "",
                "promoted_is_target": bool(in_top and (set(top1) - set(top0)).pop() in targets),
                "ndcg10_n0": v0["at_k"]["10"]["ndcg"] if v0["eligible"] else None,
                "ndcg10_n1": v1["at_k"]["10"]["ndcg"] if v1["eligible"] else None,
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(out / "per_user.csv", index=False)
    hit = table[table.supplied_in_pop_top10]
    eligible = table[table.eligible]
    summary = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "question": "Popularity NDCG@10 equal at N = 0 and N = 1 in Table 4.13",
        "reserved_users_evaluated": len(users),
        "eligible_users": int(table.eligible.sum()),
        "ndcg10": {str(n): evals[n]["at_k"]["10"]["ndcg"] for n in (0, 1)},
        "catalog_coverage_at_10": {
            str(n): evals[n]["at_k"]["10"]["catalog_coverage"] for n in (0, 1)
        },
        "distinct_artists_at_10": {
            str(n): len({i for v in lists[n].values() for i in v[:K]}) for n in (0, 1)
        },
        "arp_at_10": {str(n): evals[n]["at_k"]["10"]["arp"] for n in (0, 1)},
        "matches_locked_evaluation": True,
        "users_with_supplied_artist_in_pop_top10": len(hit),
        "of_these_no_target_in_top10": int((hit.target_positions_in_n0_top10 == "").sum()),
        "of_these_with_target_in_top10": hit[hit.target_positions_in_n0_top10 != ""][
            ["user_id", "supplied_rank_in_pop_top10", "target_positions_in_n0_top10"]
        ].to_dict("records"),
        "of_these_promoted_artist_is_target": int(hit.promoted_is_target.sum()),
        "eligible_users_with_changed_ndcg10": int(
            (~np.isclose(eligible.ndcg10_n0, eligible.ndcg10_n1, rtol=0, atol=1e-15)).sum()
        ),
        "inputs_sha256": {
            "train.parquet": sha256(SPLIT / "train.parquet"),
            "test.parquet": sha256(SPLIT / "test.parquet"),
            "user_roles.json": sha256(M2_RUN / "user_roles.json"),
        },
        "git_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip(),
        "command": sys.argv,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            **{p: importlib.metadata.version(p) for p in ["numpy", "scipy", "pandas", "pyarrow"]},
        },
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
