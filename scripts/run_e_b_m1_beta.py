"""E-B: M1 with a wider popularity penalty, validation only, and the redrawn trade-off figure.

New grid: beta in {0.75, 1, 1.5, 2} x the old lambda grid {0.5, 0.75, 1}, on the locked
PureSVD binary k = 16 base (seed 42), candidate pool 100, train masked, validation targets.
The locked point (lambda 0.75, beta 0.5) is rescored first and must equal the saved Step 15
validation metrics. Figure: all 24 points (old 12 from docs m1_metrics.csv + new 12),
ARP@10 against NDCG@10, with the 5% drop bound (0.95 x NDCG@10 of lambda 1, beta 0) and
every point below it marked. Nothing is selected; the locked M1 stays (0.75, 0.5).
"""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from time import perf_counter  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_ch4_extras import BLUE, INK, MUTED, ORANGE, style  # noqa: E402
from run_e7_topn import runtime  # noqa: E402

from musicrec.data.contracts import Interaction  # noqa: E402
from musicrec.evaluation.ranking import evaluate_ranking  # noqa: E402
from musicrec.recommenders.m1 import M1Recommender  # noqa: E402
from musicrec.recommenders.pure_svd import PureSVDRecommender  # noqa: E402

RUN = Path("outputs/chinh_thuc_cloud_20261026")
LOCKED_METRICS = Path("docs/results/chinh_thuc_cloud_20261026/m1_metrics.csv")
LAMBDAS = [0.5, 0.75, 1.0]
NEW_BETAS = [0.75, 1.0, 1.5, 2.0]
METRICS = ["precision", "recall", "ndcg", "catalog_coverage", "gini", "arp", "novelty", "ild"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None, help="timing: first N new points")
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    source = RUN / "chuong_3/run/representations"
    train = pd.read_parquet(source / "train.parquet")
    validation = pd.read_parquet(source / "validation.parquet")

    def grouped(frame: pd.DataFrame) -> dict[str, set[str]]:
        return {str(u): {str(i) for i in g.item_id} for u, g in frame.groupby("user_id")}

    histories = grouped(train)
    targets = {u: set() for u in histories} | grouped(validation)
    users = sorted(histories, key=int)
    interactions = [
        Interaction(str(r.user_id), str(r.item_id), float(r.listening_count), float(r.proxy_score))
        for r in train.itertuples(index=False)
    ]
    base = PureSVDRecommender.load(RUN / "chuong_4/tuning/pure_svd/pure_svd_lat16/model")
    locked = pd.read_csv(LOCKED_METRICS)
    locked = locked[(locked.seed == 42) & (locked.k == 10)]
    points = [(0.75, 0.5)] + [(lam, b) for b in NEW_BETAS for lam in LAMBDAS][: args.limit]
    rows = []
    for lam, beta in points:
        start = perf_counter()
        model = M1Recommender(base, candidate_size=100, lambda_weight=lam, beta=beta)
        model.fit(interactions)
        lists = {u: [r.item_id for r in model.recommend(u, 20, histories[u])] for u in users}
        result = evaluate_ranking(lists, targets, histories, ks=(5, 10, 20))
        at10 = result["at_k"]["10"]
        rows.append(
            {"lambda": lam, "beta": beta, **{m: at10[m] for m in METRICS}}
            | {"seconds": perf_counter() - start}
        )
        print(json.dumps(rows[-1]), flush=True)
    check = locked[(locked["lambda"] == 0.75) & (locked.beta == 0.5)].iloc[0]
    reproduced = {m: abs(float(check[m]) - rows[0][m]) for m in METRICS}
    if max(reproduced.values()) > 1e-12:
        raise RuntimeError(f"Locked M1 point not reproduced: {reproduced}")
    new = pd.DataFrame(rows[1:])
    new.to_csv(out / "m1_beta_mo_rong_validation.csv", index=False)
    old = locked[["lambda", "beta", *METRICS]].assign(nguon="luoi_cu")
    grid = pd.concat([old, new.drop(columns="seconds").assign(nguon="mo_rong")], ignore_index=True)
    base_ndcg = float(old[(old["lambda"] == 1) & (old.beta == 0)].ndcg.iloc[0])
    bound = 0.95 * base_ndcg
    grid["duoi_nguong_5pct"] = grid.ndcg < bound
    grid.to_csv(out / "hinh_4_6.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.3, 3.9))
    markers = {0.5: "o", 0.75: "s", 1.0: "^"}
    for _, row in grid.iterrows():
        color = BLUE if row.nguon == "luoi_cu" else ORANGE
        ax.scatter(
            row.arp,
            row.ndcg,
            s=60,
            marker=markers[float(row["lambda"])],
            color=color if not row.duoi_nguong_5pct else "white",
            edgecolor=color,
            linewidth=1.5,
            zorder=3,
        )
    chosen = grid[(grid["lambda"] == 0.75) & (grid.beta == 0.5)].iloc[0]
    ax.scatter([chosen.arp], [chosen.ndcg], s=170, facecolor="none", edgecolor=INK, zorder=4)
    ax.annotate(
        "Cấu hình đã khóa",
        (chosen.arp, chosen.ndcg),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
        color=INK,
    )
    ax.axhline(bound, color=MUTED, linestyle="--", linewidth=1)
    ax.annotate(
        "Ngưỡng giảm 5% so với nền",
        (grid.arp.min(), bound),
        xytext=(0, 4),
        textcoords="offset points",
        fontsize=8,
        color=MUTED,
    )
    handles = [
        Line2D([], [], color=BLUE, marker="o", linestyle="", label="β ∈ {0; 0,1; 0,25; 0,5}"),
        Line2D([], [], color=ORANGE, marker="o", linestyle="", label="β ∈ {0,75; 1; 1,5; 2}"),
        Line2D(
            [],
            [],
            color=MUTED,
            marker="o",
            markerfacecolor="white",
            linestyle="",
            label="Dưới ngưỡng 5%",
        ),
    ] + [
        Line2D([], [], color=MUTED, marker=m, linestyle="", label=f"λ = {lam:g}".replace(".", ","))
        for lam, m in markers.items()
    ]
    ax.set_xlabel("ARP@10 trên tập xác thực (thấp hơn là ít phổ biến hơn)")
    ax.set_ylabel("NDCG@10 xác thực")
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="lower right", ncol=2)
    style(ax)
    fig.tight_layout()
    fig.savefig(out / "hinh_4_6.png", dpi=300)
    plt.close(fig)
    summary = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "command": sys.argv,
        "locked_point_reproduced_max_abs_difference": max(reproduced.values()),
        "base_ndcg10_lambda1_beta0": base_ndcg,
        "bound_0.95": bound,
        "points_above_bound": grid[~grid.duoi_nguong_5pct][["lambda", "beta"]].values.tolist(),
        "runtime": runtime(),
    }
    (out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", "utf-8")


if __name__ == "__main__":
    main()
