"""Supplementary Chapter 4 analyses requested by the advisor (feedback of 06/11/2026).

Nothing here selects a model or a configuration. Every model is the one locked in
outputs/chinh_thuc_cloud_20261026/chuong_4/test/lock.json:

1. Rescore the test split at seed 42 with the locked models (UserCF, ItemCF and SVD from
   the local refit of rebuild_locked_runs.py) and compare every aggregate with the
   official test/metrics.csv. Per-user values are only used if the aggregates match.
2. Recompute the four predeclared paired tests (must equal the official file), then add
   supplementary tests (PureSVD against every other comparison model, Holm within that
   family) and per-model bootstrap CIs of mean NDCG@10.
3. Per-user analyses: NDCG@10 distribution, PureSVD - Popularity differences, and three
   equal-size user groups by mainstreaminess (mean train listeners of the user's artists).
4. M1 on test for the four ablation variants (supplementary: test was already opened),
   with an independent tag-based ILD and two example lists.
5. M2 decision paths per profile size on the reserved users (Table 4.10).
6. Figures 4.1-4.7 as PNG plus the CSV each one is drawn from.
"""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import importlib.metadata  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from itertools import combinations  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter, ScalarFormatter  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_statistics import holm  # noqa: E402

from musicrec.data.cold_start import partition_users, profile_order  # noqa: E402
from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.inference import resample_indices  # noqa: E402
from musicrec.evaluation.paired import (  # noqa: E402
    equivalence_test,
    mean_interval,
    paired_comparison,
)  # noqa: E402
from musicrec.evaluation.ranking import evaluate_ranking  # noqa: E402
from musicrec.recommenders.base import Recommender  # noqa: E402
from musicrec.recommenders.implicit_als import ImplicitALSRecommender  # noqa: E402
from musicrec.recommenders.item_cf import ItemCFRecommender  # noqa: E402
from musicrec.recommenders.m1 import M1Recommender  # noqa: E402
from musicrec.recommenders.m2 import M2Recommender  # noqa: E402
from musicrec.recommenders.popularity import PopularityRecommender  # noqa: E402
from musicrec.recommenders.pure_svd import PureSVDRecommender  # noqa: E402
from musicrec.recommenders.random import RandomRecommender  # noqa: E402
from musicrec.recommenders.svd import SVDRecommender  # noqa: E402
from musicrec.recommenders.user_cf import UserCFRecommender  # noqa: E402

RUN = Path("outputs/chinh_thuc_cloud_20261026")
DOCS = Path("docs/results/chinh_thuc_cloud_20261026")
MODELS = ["random", "popularity", "user_cf", "item_cf", "svd", "pure_svd", "implicit_als", "m1"]
LABELS = {
    "random": "Random",
    "popularity": "Popularity",
    "user_cf": "UserCF",
    "item_cf": "ItemCF",
    "svd": "SVD có độ lệch",
    "pure_svd": "PureSVD",
    "implicit_als": "Implicit ALS",
    "m1": "M1",
}
M1_VARIANTS = {
    "nen": (1.0, 0.0),
    "chi_da_dang": (0.75, 0.0),
    "chi_phat_pho_bien": (1.0, 0.5),
    "m1_day_du": (0.75, 0.5),
}
METRICS = ["precision", "recall", "ndcg", "catalog_coverage", "gini", "arp", "novelty", "ild"]
RESAMPLES, SEED = 1000, 42
EQUIVALENCE_MARGIN = 0.05
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dd"


def style(ax: Any) -> None:
    """Recessive grid and axes, ink-colored text."""
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=10)
    comma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    for axis, scale in [(ax.xaxis, ax.get_xscale()), (ax.yaxis, ax.get_yscale())]:
        if scale == "linear" and isinstance(axis.get_major_formatter(), ScalarFormatter):
            axis.set_major_formatter(comma)


def save(fig: Any, out: Path, name: str) -> None:
    fig.tight_layout()
    fig.savefig(out / f"{name}.png", dpi=300)
    plt.close(fig)


def compare(a: dict[str, float], b: dict[str, float], indices: Any) -> dict[str, Any]:
    """Paired comparison on one shared bootstrap index matrix (musicrec.evaluation.paired)."""
    return paired_comparison(a, b, indices)


def holm_families(first: list[dict[str, Any]], second: list[dict[str, Any]]) -> dict[str, Any]:
    """Size of each Holm family and the unordered pairs that appear in both."""
    key = lambda r: tuple(sorted((r["a"], r["b"])))  # noqa: E731
    shared = sorted(set(map(key, first)) & set(map(key, second)))
    return {
        "predeclared": {"pairs": len(first), "members": [[r["a"], r["b"]] for r in first]},
        "supplementary": {"pairs": len(second), "members": [[r["a"], r["b"]] for r in second]},
        "pairs_in_both_families": [list(p) for p in shared],
        "note": "Holm is applied within each family separately; a pair listed in both "
        "families has the same raw Wilcoxon p but a Holm p from each family.",
    }


def m1_equivalence(predeclared: list[dict[str, Any]], base_mean: float) -> dict[str, Any]:
    """TOST for M1 - PureSVD on NDCG@10 with delta = 5% of PureSVD's mean NDCG@10."""
    row = next(r for r in predeclared if (r["a"], r["b"]) == ("m1", "pure_svd"))
    return {
        "pair": ["m1", "pure_svd"],
        "base_model": "pure_svd",
        "base_mean_ndcg10": base_mean,
        "relative_margin": EQUIVALENCE_MARGIN,
        **equivalence_test(row["ci90_low"], row["ci90_high"], EQUIVALENCE_MARGIN * base_mean),
    }


def tag_ild(lists: dict[str, list[str]], features: Any, index: dict[str, int], tagged: Any) -> Any:
    """Mean over lists of mean (1 - tag cosine) over pairs whose two artists both have tags."""
    values = []
    for items in lists.values():
        rows = [index[i] for i in items if i in index and tagged[index[i]]]
        if len(rows) < 2:
            continue
        sims = (features[rows] @ features[rows].T).toarray()
        pairs = [1 - sims[a, b] for a, b in combinations(range(len(rows)), 2)]
        values.append(float(np.mean(pairs)))
    return {"ild_tag": float(np.mean(values)) if values else None, "ild_tag_lists": len(values)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuilt-tuning", type=Path, default=RUN / "chuong_4_bo_sung/tuning")
    parser.add_argument("--cleaning-run", type=Path, default=RUN / "chuong_4_bo_sung/cleaning")
    parser.add_argument("--output-dir", type=Path, default=RUN / "chuong_4_bo_sung/phan_tich")
    args = parser.parse_args()
    out = args.output_dir
    figs = out / "hinh"
    figs.mkdir(parents=True, exist_ok=True)
    lock = json.loads((RUN / "chuong_4/test/lock.json").read_text(encoding="utf-8"))
    rebuilt = json.loads((args.rebuilt_tuning / "rebuild_report.json").read_text("utf-8"))

    source = RUN / "chuong_3/run/representations"
    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")
    test = pd.read_parquet(source / "test.parquet")

    def grouped(frame: pd.DataFrame) -> dict[str, set[str]]:
        return {str(u): {str(i) for i in g.item_id} for u, g in frame.groupby("user_id")}

    histories = grouped(train)
    empty: dict[str, set[str]] = {user: set() for user in histories}
    validated = empty | grouped(validation)
    targets = empty | grouped(test)
    users = sorted(histories, key=int)
    interactions = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count), float(r.proxy_score))
        for r in train.itertuples(index=False)
    ]

    loaders: dict[str, Any] = {
        "user_cf": UserCFRecommender,
        "item_cf": ItemCFRecommender,
        "svd": SVDRecommender,
        "pure_svd": PureSVDRecommender,
        "implicit_als": ImplicitALSRecommender,
    }
    loaded: dict[str, Recommender] = {
        "random": RandomRecommender(seed=42).fit(interactions),
        "popularity": PopularityRecommender().fit(interactions),
    }
    for model, cls in loaders.items():
        directory = (
            args.rebuilt_tuning / model / rebuilt[model]["run"] / "model"
            if model in {"user_cf", "item_cf", "svd"}
            else RUN
            / "chuong_4/tuning"
            / model
            / Path(lock["models"][model]["runs"]["42"]["path"]).name
            / "model"
        )
        loaded[model] = cls.load(directory)
    loaded["m1"] = M1Recommender.load(
        RUN / "chuong_4/m1_pure_svd/seed_42/selected_model", base=loaded["pure_svd"]
    )

    # 1. Rescore and compare with the official aggregates.
    official = pd.read_csv(DOCS / "test/metrics.csv")
    official = official[official.seed == 42]
    lists: dict[str, dict[str, list[str]]] = {}
    evaluations: dict[str, dict[str, Any]] = {}
    check: dict[str, Any] = {}
    for model in MODELS:
        recommender = loaded[model]
        lists[model] = {
            u: [r.item_id for r in recommender.recommend(u, 20, histories[u] | validated[u])]
            for u in users
        }
        result = evaluate_ranking(
            lists[model], targets, histories, ks=(5, 10, 20), split="test", validation=validated
        )
        evaluations[model] = result
        diffs = {}
        for k in ["5", "10", "20"]:
            row = official[(official.model == model) & (official.k == int(k))].iloc[0]
            for name in METRICS:
                diffs[f"{name}@{k}"] = abs(float(result["at_k"][k][name]) - float(row[name]))
        check[model] = {"max_abs_difference": max(diffs.values()), "differences": diffs}
        print(model, "max |diff| vs official:", check[model]["max_abs_difference"], flush=True)
    (out / "doi_chieu_chinh_thuc.json").write_text(json.dumps(check, indent=2) + "\n", "utf-8")

    per_user = {
        model: {
            u: float(v["at_k"]["10"]["ndcg"])
            for u, v in evaluations[model]["per_user"].items()
            if v["eligible"]
        }
        for model in MODELS
    }
    eligible = sorted(per_user["pure_svd"], key=int)
    pd.DataFrame(
        {LABELS[m]: [per_user[m][u] for u in eligible] for m in MODELS}, index=eligible
    ).rename_axis("user_id").to_csv(out / "ndcg10_tung_nguoi_dung.csv")

    # 2. Statistics.
    indices = resample_indices(len(per_user["pure_svd"]), RESAMPLES, SEED)
    predeclared = [
        {"a": a, "b": b, **compare(per_user[a], per_user[b], indices)}
        for a, b in lock["comparison_pairs"]
    ]
    for row, adjusted in zip(
        predeclared, holm([r["wilcoxon_p"] for r in predeclared]), strict=True
    ):
        row["holm_p"] = adjusted
    others = ["random", "popularity", "user_cf", "item_cf", "svd"]
    family = [
        {"a": "pure_svd", "b": b, **compare(per_user["pure_svd"], per_user[b], indices)}
        for b in others
    ]
    for row, adjusted in zip(family, holm([r["wilcoxon_p"] for r in family]), strict=True):
        row["holm_p"] = adjusted
    intervals = {
        model: mean_interval([per_user[model][u] for u in eligible], indices) for model in MODELS
    }
    official_stats = json.loads((DOCS / "test/statistics_ndcg_at_10.json").read_text("utf-8"))
    # Bootstrap-free fields only: the official file drew a fresh bootstrap per pair.
    reproduced = all(
        abs(a["holm_p"] - b["holm_p"]) <= 1e-12 * max(1.0, b["holm_p"])
        and abs(a["mean_difference"] - b["mean_difference"]) <= 1e-12
        for a, b in zip(predeclared, official_stats["pairs"], strict=True)
    )
    stats = {
        "bootstrap": {
            "resamples": RESAMPLES,
            "seed": SEED,
            "unit": "user",
            "indices": "shared_across_pairs",
        },
        "test": "two_sided_wilcoxon_signed_rank_zero_differences_dropped",
        "predeclared_pairs_recomputed": predeclared,
        "predeclared_equal_official": reproduced,
        "supplementary_family_pure_svd_vs_others_holm": family,
        "holm_families": holm_families(predeclared, family),
        "m1_pure_svd_equivalence": m1_equivalence(predeclared, intervals["pure_svd"]["mean"]),
        "mean_ndcg10_bootstrap_ci": intervals,
    }
    (out / "kiem_dinh_bo_sung.json").write_text(json.dumps(stats, indent=2) + "\n", "utf-8")
    print("predeclared pairs equal official:", reproduced, flush=True)

    # 3. Per-user analyses.
    listeners = train.groupby("item_id").user_id.nunique()
    mainstream = (
        train.assign(listeners=train.item_id.map(listeners)).groupby("user_id").listeners.mean()
    )
    mainstream.index = mainstream.index.astype(str)
    scores = mainstream.loc[eligible]
    group = pd.qcut(scores.rank(method="first"), 3, labels=["Thấp", "Trung bình", "Cao"])
    rows = []
    for label in ["Thấp", "Trung bình", "Cao"]:
        members = [u for u in eligible if group[u] == label]
        row: dict[str, Any] = {
            "nhom": label,
            "so_nguoi": len(members),
            "trung_binh_nguoi_nghe_min": float(scores[members].min()),
            "trung_binh_nguoi_nghe_max": float(scores[members].max()),
        }
        for model in MODELS:
            row[LABELS[model]] = float(np.mean([per_user[model][u] for u in members]))
        rows.append(row)
    pd.DataFrame(rows).to_csv(out / "nhom_uu_pho_bien.csv", index=False)

    diff = np.array([per_user["pure_svd"][u] - per_user["popularity"][u] for u in eligible])
    split = {
        "users": len(diff),
        "improved": int((diff > 0).sum()),
        "equal": int((diff == 0).sum()),
        "worse": int((diff < 0).sum()),
        "equal_both_zero": int(
            sum(per_user["pure_svd"][u] == 0 and per_user["popularity"][u] == 0 for u in eligible)
        ),
    }
    (out / "chenh_lech_puresvd_popularity.json").write_text(
        json.dumps(split, indent=2) + "\n", "utf-8"
    )
    pd.DataFrame({"user_id": eligible, "chenh_lech": diff}).to_csv(
        out / "hinh/hinh_4_5.csv", index=False
    )

    # 4. M1 variants on test (supplementary) and tag ILD.
    cleaning = args.cleaning_run
    assignments = pd.read_parquet(cleaning / "tag_assignments.parquet")
    dictionary = pd.read_parquet(cleaning / "tags.parquet").set_index("tagID")["tagValue"].to_dict()
    tags = [
        (str(r.userID), str(r.artistID), dictionary[r.tagID])
        for r in assignments.itertuples(index=False)
    ]
    tag_model = M2Recommender(min_tag_df=2).fit(interactions, tags=tags)
    features, index, tagged = tag_model._features, tag_model._item_index, tag_model._tagged
    variant_rows, variant_lists = [], {}
    for name, (lam, beta) in M1_VARIANTS.items():
        variant = M1Recommender(
            loaded["pure_svd"], candidate_size=100, lambda_weight=lam, beta=beta
        )
        variant.fit(interactions)
        variant_lists[name] = {
            u: [r.item_id for r in variant.recommend(u, 20, histories[u] | validated[u])]
            for u in users
        }
        result = evaluate_ranking(
            variant_lists[name], targets, histories, ks=(10,), split="test", validation=validated
        )
        at10 = result["at_k"]["10"]
        top10 = {u: variant_lists[name][u][:10] for u in eligible}
        variant_rows.append(
            {
                "bien_the": name,
                "lambda": lam,
                "beta": beta,
                **{m: at10[m] for m in METRICS},
                **tag_ild(top10, features, index, tagged),
            }
        )
        per_user[f"m1_{name}"] = {
            u: float(v["at_k"]["10"]["ndcg"])
            for u, v in result["per_user"].items()
            if v["eligible"]
        }
    if variant_lists["m1_day_du"] != lists["m1"]:
        raise RuntimeError("Refitted full M1 differs from the locked M1 checkpoint")
    m1_tests = [
        {"a": f"m1_{n}", "b": "m1_nen", **compare(per_user[f"m1_{n}"], per_user["m1_nen"], indices)}
        for n in ["chi_da_dang", "chi_phat_pho_bien", "m1_day_du"]
    ]
    for row, adjusted in zip(m1_tests, holm([r["wilcoxon_p"] for r in m1_tests]), strict=True):
        row["holm_p"] = adjusted
    pd.DataFrame(variant_rows).to_csv(out / "m1_bien_the_test.csv", index=False)
    (out / "m1_kiem_dinh_bien_the.json").write_text(json.dumps(m1_tests, indent=2) + "\n", "utf-8")
    pop_lists = {u: lists["popularity"][u][:10] for u in eligible}
    pure_lists = {u: lists["pure_svd"][u][:10] for u in eligible}
    ild_tag_models = {
        "popularity": tag_ild(pop_lists, features, index, tagged),
        "pure_svd": tag_ild(pure_lists, features, index, tagged),
    }
    (out / "ild_the_mo_hinh.json").write_text(
        json.dumps(
            {
                **ild_tag_models,
                "tag_features": tag_model.feature_report,
                "definition": "1 - cosine of L2-normalised TF-IDF tag vectors, pairs of tagged "
                "artists only, mean per list then over lists with at least one such pair; "
                "tag vocabulary df>=2 fitted on all train pairs (M2 recipe)",
            },
            indent=2,
        )
        + "\n",
        "utf-8",
    )

    artists = pd.read_parquet(cleaning / "artists.parquet")
    names = dict(zip(artists.id.astype(str), artists.display_name, strict=True))
    changed = [
        u for u in eligible if len(set(lists["pure_svd"][u][:10]) - set(lists["m1"][u][:10])) >= 3
    ]
    examples = []
    for user in changed[:3]:
        for rank in range(10):
            before, after = lists["pure_svd"][user][rank], lists["m1"][user][rank]
            examples.append(
                {
                    "user_id": user,
                    "hang": rank + 1,
                    "puresvd": names.get(before, before),
                    "puresvd_nguoi_nghe": int(listeners.get(before, 0)),
                    "puresvd_dung": before in targets[user],
                    "m1": names.get(after, after),
                    "m1_nguoi_nghe": int(listeners.get(after, 0)),
                    "m1_dung": after in targets[user],
                }
            )
    pd.DataFrame(examples).to_csv(out / "m1_vi_du.csv", index=False)

    # 5. M2 decision paths on the reserved users (same cohort and profiles as Step 17).
    m2_run = RUN / "chuong_4/m2_tuning"
    split_train = pd.read_parquet(RUN / "chuong_3/run/split/train.parquet")
    roles = json.loads((m2_run / "user_roles.json").read_text(encoding="utf-8"))
    if roles != partition_users(sorted(split_train.user_id.unique(), key=int), 42):
        raise RuntimeError("Saved M2 user roles differ from the deterministic partition")
    reserved = split_train[split_train.user_id.isin(roles["reserved"])]
    counts = reserved.groupby("user_id").size()
    cohort = sorted(counts[counts >= 5].index, key=int)
    m2 = M2Recommender.load(m2_run / "model")
    path_rows = []
    for n in [0, 1, 3, 5]:
        content = fallback = outside = 0
        for user in cohort:
            records = reserved[reserved.user_id == user].set_index("item_id")["listening_count"]
            order = profile_order(user, list(records.index), 42)[:n]
            m2.set_profile(user, [Interaction(user, i, float(records[i])) for i in order])
            features_n = m2.profile_scores(user)
            has_content = bool(features_n.content_available.any())
            has_cf = bool(features_n.cf_available.any())
            content += has_content
            fallback += not (has_content or has_cf)
            outside += sum(i not in m2._item_index for i in order)
        path_rows.append(
            {
                "n": n,
                "nguoi_dung": len(cohort),
                "co_diem_noi_dung_pct": 100 * content / len(cohort),
                "chuyen_hoan_toan_pho_bien_pct": 100 * fallback / len(cohort),
                "nghe_si_dau_vao_ngoai_anh_xa": outside,
            }
        )
    pd.DataFrame(path_rows).to_csv(out / "m2_duong_xu_ly.csv", index=False)

    # 6. Figures.
    counts_artist = listeners.sort_values(ascending=False).to_numpy()
    pd.DataFrame(
        {"hang": np.arange(1, len(counts_artist) + 1), "so_nguoi_nghe": counts_artist}
    ).to_csv(figs / "hinh_4_1.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    ax.plot(np.arange(1, len(counts_artist) + 1), counts_artist, color=BLUE, linewidth=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Thứ hạng nghệ sĩ theo số người nghe (thang log)")
    ax.set_ylabel("Số người nghe (thang log)")
    style(ax)
    save(fig, figs, "hinh_4_1")

    plays = train.groupby("user_id").listening_count.sum()
    plays.to_csv(figs / "hinh_4_2.csv", header=["tong_luot_nghe"])
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    bins = np.logspace(np.log10(max(1, plays.min())), np.log10(plays.max()), 40)
    ax.hist(plays, bins=bins, color=BLUE, edgecolor="white", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Tổng lượt nghe của người dùng trên tập huấn luyện (thang log)")
    ax.set_ylabel("Số người dùng")
    style(ax)
    save(fig, figs, "hinh_4_2")

    curve_dir = args.rebuilt_tuning / "svd_curve"
    curve = pd.read_csv(curve_dir / "learning_curve.csv")
    curve.to_csv(figs / "hinh_4_3.csv", index=False)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(6.3, 4.8), sharex=True)
    best = int(curve.loc[curve.validation_ndcg_at_10.idxmax(), "epoch"])
    top.plot(curve.epoch, curve.validation_ndcg_at_10, color=BLUE, linewidth=2)
    top.axvline(best, color=MUTED, linestyle="--", linewidth=1)
    top.set_ylabel("NDCG@10 xác thực")
    bottom.plot(curve.epoch, curve.train_proxy_rmse, color=ORANGE, linewidth=2, label="Huấn luyện")
    bottom.plot(curve.epoch, curve.validation_proxy_rmse, color=AQUA, linewidth=2, label="Xác thực")
    bottom.axvline(best, color=MUTED, linestyle="--", linewidth=1)
    bottom.set_ylabel("RMSE điểm đại diện")
    bottom.legend(frameon=False, fontsize=8)
    bottom.set_xlabel("Vòng huấn luyện")
    top.annotate(
        f"Vòng tốt nhất: {best}",
        (best, curve.validation_ndcg_at_10.max()),
        xytext=(8, -12),
        textcoords="offset points",
        color=INK,
        fontsize=9,
    )
    style(top)
    style(bottom)
    save(fig, figs, "hinh_4_3")

    order = ["popularity", "user_cf", "item_cf", "svd", "pure_svd", "implicit_als", "m1"]
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    ax.boxplot(
        [[per_user[m][u] for u in eligible] for m in order],
        tick_labels=[LABELS[m] for m in order],
        patch_artist=True,
        boxprops={"facecolor": "#cde2fb", "edgecolor": BLUE},
        medianprops={"color": INK},
        whiskerprops={"color": BLUE},
        capprops={"color": BLUE},
        flierprops={
            "marker": "o",
            "markersize": 3,
            "markerfacecolor": BLUE,
            "markeredgecolor": "none",
            "alpha": 0.4,
        },
        showmeans=True,
        meanprops={
            "marker": "D",
            "markersize": 5,
            "markerfacecolor": ORANGE,
            "markeredgecolor": "white",
        },
    )
    ax.set_ylabel("NDCG@10 từng người dùng (tập kiểm thử)")
    ax.tick_params(axis="x", labelrotation=20)
    style(ax)
    save(fig, figs, "hinh_4_4")
    pd.read_csv(out / "ndcg10_tung_nguoi_dung.csv").to_csv(figs / "hinh_4_4.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    edges = np.linspace(-1, 1, 41)
    ax.hist(diff, bins=edges, color=BLUE, edgecolor="white", linewidth=1)
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_xlabel("NDCG@10 của PureSVD trừ Popularity, theo từng người dùng")
    ax.set_ylabel("Số người dùng")
    style(ax)
    save(fig, figs, "hinh_4_5")

    grid = pd.read_csv(DOCS / "m1_metrics.csv")
    grid = grid[(grid.seed == 42) & (grid.k == 10)].copy()
    base_ndcg = float(grid[(grid["lambda"] == 1) & (grid.beta == 0)].ndcg.iloc[0])
    grid.to_csv(figs / "hinh_4_6.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.3, 3.8))
    markers = {0.5: "o", 0.75: "s", 1.0: "^"}
    for beta, color in zip([0.0, 0.1, 0.25, 0.5], [BLUE, ORANGE, AQUA, YELLOW], strict=True):
        for lam, marker in markers.items():
            part = grid[(grid.beta == beta) & (grid["lambda"] == lam)]
            ax.scatter(
                part.arp,
                part.ndcg,
                s=60,
                color=color,
                marker=marker,
                edgecolor="white",
                linewidth=1.5,
                zorder=3,
            )
    from matplotlib.lines import Line2D

    handles = [
        Line2D(
            [],
            [],
            color=c,
            marker="o",
            linestyle="",
            markersize=7,
            label=f"β = {b:g}".replace(".", ","),
        )
        for b, c in zip([0.0, 0.1, 0.25, 0.5], [BLUE, ORANGE, AQUA, YELLOW], strict=True)
    ] + [
        Line2D(
            [],
            [],
            color=MUTED,
            marker=m,
            linestyle="",
            markersize=7,
            label=f"λ = {lam:g}".replace(".", ","),
        )
        for lam, m in markers.items()
    ]
    chosen = grid[(grid["lambda"] == 0.75) & (grid.beta == 0.5)].iloc[0]
    ax.scatter(
        [chosen.arp], [chosen.ndcg], s=160, facecolor="none", edgecolor=INK, linewidth=1.5, zorder=4
    )
    ax.annotate(
        "Cấu hình chọn",
        (chosen.arp, chosen.ndcg),
        xytext=(-70, -18),
        textcoords="offset points",
        fontsize=8,
        color=INK,
    )
    ax.axhline(0.95 * base_ndcg, color=MUTED, linestyle="--", linewidth=1)
    ax.annotate(
        "Ngưỡng giảm 5% so với nền",
        (grid.arp.max(), 0.95 * base_ndcg),
        xytext=(-150, -12),
        textcoords="offset points",
        fontsize=8,
        color=MUTED,
    )
    ax.set_xlabel("ARP@10 trên tập xác thực (thấp hơn là ít phổ biến hơn)")
    ax.set_ylabel("NDCG@10 xác thực")
    ax.legend(handles=handles, frameon=False, fontsize=8, loc="lower right", ncol=2)
    style(ax)
    save(fig, figs, "hinh_4_6")

    m2_metrics = pd.read_csv(DOCS / "m2/test/metrics.csv")
    m2_metrics = m2_metrics[m2_metrics.k == 10]
    m2_metrics.to_csv(figs / "hinh_4_7.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    m2_labels = {
        "popularity": "Popularity",
        "item_cf": "Chỉ ItemCF",
        "content": "Chỉ nội dung thẻ",
        "m2": "M2",
    }
    for (method, label), color in zip(m2_labels.items(), [BLUE, ORANGE, AQUA, YELLOW], strict=True):
        part = m2_metrics[m2_metrics.method == method].sort_values("n")
        ax.plot(
            part.n,
            part.ndcg,
            color=color,
            linewidth=2,
            marker="o",
            markersize=8,
            markeredgecolor="white",
            label=label,
        )
    ax.set_xticks([0, 1, 3, 5])
    ax.set_xlabel("Số nghệ sĩ được cung cấp (N)")
    ax.set_ylabel("NDCG@10 (nhóm để dành)")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4)
    style(ax)
    save(fig, figs, "hinh_4_7")

    meta = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "command": sys.argv,
        "git_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
        "git_status": subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True
        ).stdout,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            **{
                p: importlib.metadata.version(p)
                for p in ["numpy", "scipy", "pandas", "pyarrow", "implicit", "matplotlib"]
            },
        },
        "lock": str(RUN / "chuong_4/test/lock.json"),
    }
    (out / "metrics.json").write_text(json.dumps(meta, indent=2) + "\n", "utf-8")


if __name__ == "__main__":
    main()
