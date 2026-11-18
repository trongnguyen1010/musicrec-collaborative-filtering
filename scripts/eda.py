"""Inspect raw HetRec tables without cleaning, splitting or training."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    """Fingerprint a file without modifying it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interaction_quality(frame: pd.DataFrame) -> tuple[dict[str, int], pd.Series]:
    """Count invalid/duplicate observations; do not remove or combine source rows."""
    keys = ["userID", "artistID"]
    missing_ids = frame[keys].apply(lambda col: col.str.strip().eq("")).any(axis=1)
    weights = pd.to_numeric(frame["weight"], errors="coerce")
    finite = pd.Series(np.isfinite(weights), index=frame.index)
    valid = ~missing_ids & finite & weights.gt(0)
    observed = frame.loc[valid, keys].assign(numeric_weight=weights[valid])
    conflicts = observed.groupby(keys)["numeric_weight"].nunique().gt(1)
    return {
        "rows": len(frame),
        "rows_with_blank_id": int(missing_ids.sum()),
        "nonnumeric_or_missing_weight": int(weights.isna().sum()),
        "infinite_weight": int((weights.notna() & ~finite).sum()),
        "nonpositive_finite_weight": int((finite & weights.le(0)).sum()),
        "exact_duplicate_extra_rows": int(frame.duplicated().sum()),
        "duplicate_pair_extra_rows": int(frame.duplicated(keys).sum()),
        "pairs_with_conflicting_valid_counts": int(conflicts.sum()),
        "valid_rows_for_descriptive_analysis": int(valid.sum()),
    }, valid


def describe(series: pd.Series) -> dict[str, float | None]:
    """Use pandas linear quantiles and sample standard deviation (ddof=1)."""
    values = series.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    return {str(k): float(v) if np.isfinite(v) else None for k, v in values.items()}


def read_table(path: Path) -> pd.DataFrame:
    """Retain blank fields and literal text such as NA; tags are inspected by ID."""
    encoding = "latin-1" if path.name == "tags.dat" else "utf-8"
    return pd.read_csv(
        path,
        sep="\t",
        encoding=encoding,
        dtype=str,
        keep_default_na=False,
        quoting=csv.QUOTE_NONE,
    )


def make_figures(
    out: Path, weights: pd.Series, histories: pd.Series, artists: pd.DataFrame
) -> list[str]:
    """Plot raw descriptive quantities, without producing model input transforms."""
    os.environ.setdefault("MPLCONFIGDIR", str(out / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    paths: list[str] = []

    def save(fig: Any, name: str) -> None:
        fig.tight_layout()
        fig.savefig(out / name, dpi=180, facecolor="white")
        plt.close(fig)
        paths.append(f"figures/{name}")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.geomspace(float(weights.min()), float(weights.max()) + 1, 45)
    ax.hist(weights, bins=bins, color="#2878A0", edgecolor="white")
    ax.set_xscale("log")
    ax.axvline(weights.median(), color="#B85016", label=f"Trung vị: {weights.median():,.0f}")
    ax.axvline(
        weights.mean(), color="#222222", linestyle="--", label=f"Trung bình: {weights.mean():,.2f}"
    )
    ax.set(
        title="Lượt nghe mỗi cặp người dùng–nghệ sĩ",
        xlabel="Số lượt nghe gốc (trục log)",
        ylabel="Số cặp tương tác",
    )
    ax.legend()
    save(fig, "01_listening_counts.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    frequencies = histories.value_counts().sort_index()
    axes[0].bar(frequencies.index, frequencies.values, color="#2878A0")
    axes[0].set(title=f"Toàn bộ {len(histories):,} người dùng", ylabel="Số người dùng")
    shorter = histories[histories < 50].value_counts().sort_index()
    axes[1].bar(shorter.index, shorter.values, color="#B85016")
    axes[1].set(title=f"Phóng to nhóm dưới 50 nghệ sĩ ({int(shorter.sum())} người)")
    for ax in axes:
        ax.set_xlabel("Số nghệ sĩ phân biệt trong lịch sử quan sát")
    save(fig, "02_user_history.png")

    listeners = artists["listeners"].sort_values(ascending=False).reset_index(drop=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].hist(
        listeners,
        bins=np.geomspace(1, float(listeners.max()) + 1, 30),
        color="#2878A0",
        edgecolor="white",
    )
    axes[0].set_xscale("log")
    axes[0].set(
        title="Phân bố số người nghe/nghệ sĩ",
        xlabel="Số người nghe (trục log)",
        ylabel="Số nghệ sĩ",
    )
    axes[1].loglog(np.arange(1, len(listeners) + 1), listeners, color="#B85016")
    axes[1].set(
        title="Phần đầu và đuôi dài",
        xlabel="Hạng nghệ sĩ theo số người nghe",
        ylabel="Số người nghe",
    )
    save(fig, "03_artist_audience.png")

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(1, len(listeners) + 1) / len(listeners) * 100
    y = listeners.cumsum() / listeners.sum() * 100
    ax.plot(x, y, color="#2878A0", label="Nghệ sĩ nhiều người nghe xếp trước")
    ax.plot([0, 100], [0, 100], "--", color="#999999", label="Mốc phân bố đều")
    top = math.ceil(len(listeners) * 0.2)
    share = float(listeners.iloc[:top].sum() / listeners.sum() * 100)
    ax.scatter(top / len(listeners) * 100, share, color="#B85016", zorder=3)
    ax.annotate(
        f"{top:,} nghệ sĩ (~20%) → {share:.2f}% cặp",
        (20, share),
        xytext=(27, 60),
        arrowprops={"arrowstyle": "->"},
    )
    ax.set(
        xlim=(0, 100),
        ylim=(0, 102),
        xlabel="Tỷ lệ nghệ sĩ tích lũy (%)",
        ylabel="Tỷ lệ cặp người dùng–nghệ sĩ tích lũy (%)",
        title="Mức tập trung tương tác theo số người nghe",
    )
    ax.legend(loc="lower right")
    save(fig, "04_interaction_concentration.png")

    fig, ax = plt.subplots(figsize=(9, 3.5))
    covered = artists["unique_tags"].gt(0)
    artist_pct = float(covered.mean() * 100)
    edge_pct = float(artists.loc[covered, "listeners"].sum() / artists.listeners.sum() * 100)
    labels = ["Nghệ sĩ trong danh mục", "Cặp tương tác có nghệ sĩ mang thẻ"]
    ax.barh(labels, [artist_pct, edge_pct], color="#2878A0", label="Có thẻ")
    ax.barh(
        labels,
        [100 - artist_pct, 100 - edge_pct],
        left=[artist_pct, edge_pct],
        color="#DDDDDD",
        label="Không có thẻ",
    )
    for i, value in enumerate([artist_pct, edge_pct]):
        ax.text(value / 2, i, f"{value:.2f}%", ha="center", va="center", color="white")
    ax.set(
        xlim=(0, 100),
        xlabel="Tỷ lệ (%)",
        title="Độ phủ thẻ trên toàn snapshot gốc — chưa phải đặc trưng train",
    )
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.5), ncol=2)
    save(fig, "05_tag_coverage.png")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/hetrec2011"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw, out = args.raw_dir.resolve(), args.output_dir.resolve()
    if out == raw or raw in out.parents:
        raise ValueError("EDA output must be outside raw data")
    inputs = [*sorted(raw.iterdir()), raw.parent / "hetrec2011-lastfm-2k.zip"]
    hashes = {p.as_posix(): sha256(p) for p in inputs if p.is_file()}
    tables = {p.name: read_table(p) for p in raw.glob("*.dat")}
    interactions, artists = tables["user_artists.dat"], tables["artists.dat"]
    assignments = tables["user_taggedartists.dat"]
    quality, valid = interaction_quality(interactions)
    unknown = ~interactions.artistID.isin(artists.id)
    quality["rows_with_artist_outside_catalog"] = int(unknown.sum())
    observed = interactions.loc[valid & ~unknown].copy()
    if observed.empty:
        raise ValueError("No valid observations for descriptive analysis")
    observed["weight"] = pd.to_numeric(observed.weight)
    histories = observed.groupby("userID").artistID.nunique()
    listeners = observed.groupby("artistID").userID.nunique().reindex(artists.id, fill_value=0)
    catalog_tags = assignments[assignments.artistID.isin(artists.id)]
    tag_counts = catalog_tags.groupby("artistID").tagID.nunique()
    profiles = artists.set_index("id")[["name"]].copy()
    profiles["listeners"] = listeners
    profiles["total_listens"] = (
        observed.groupby("artistID").weight.sum().reindex(profiles.index, fill_value=0)
    )
    profiles["unique_tags"] = tag_counts.reindex(profiles.index, fill_value=0)
    unique_pairs = len(observed[["userID", "artistID"]].drop_duplicates())
    possible_pairs = len(histories) * len(profiles)
    tag_frequency = catalog_tags.groupby("tagID").artistID.nunique().rename("artists")
    covered = profiles.unique_tags.gt(0)
    concentration = {}
    for fraction in [0.01, 0.1, 0.2]:
        n = math.ceil(len(listeners) * fraction)
        concentration[str(fraction)] = {
            "artists": n,
            "share_of_unique_pairs": float(listeners.nlargest(n).sum() / unique_pairs),
        }
    missing = [
        {
            "file": name,
            "column": col,
            "rows": len(frame),
            "blank_or_whitespace": int(frame[col].str.strip().eq("").sum()),
        }
        for name, frame in tables.items()
        for col in frame.columns
    ]
    table_quality = {
        name: {"rows": len(frame), "exact_duplicate_extra_rows": int(frame.duplicated().sum())}
        for name, frame in tables.items()
    }
    encoding = {}
    for name, column in [("tags.dat", 1), ("artists.dat", 1)]:
        values = [line.split(b"\t")[column] for line in (raw / name).read_bytes().splitlines()[1:]]
        bad = []
        for number, value in enumerate(values, 2):
            try:
                value.decode("utf-8")
            except UnicodeDecodeError:
                bad.append(number)
        encoding[name] = {"invalid_utf8_text_rows": len(bad), "source_line_numbers": bad}
    metrics: dict[str, Any] = {
        "step": 2,
        "scope": "raw EDA only; no cleaning/split/transformation/model training",
        "examined_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
        "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
        "git_diff_sha256": hashlib.sha256(
            subprocess.check_output(["git", "diff", "--binary", "HEAD"])
        ).hexdigest(),
        "script_sha256": sha256(Path(__file__)),
        "command": sys.argv,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{n: importlib.metadata.version(n) for n in ["pandas", "numpy", "matplotlib"]},
        },
        "input_sha256": hashes,
        "seed": None,
        "definitions": {
            "missing": "empty or whitespace; literal NA is retained",
            "quantile": "linear interpolation",
            "std": "sample, ddof=1",
            "density": "distinct valid user-artist pairs / observed users / catalog artists",
            "tags": "date view only; inspect catalog join without modifying source",
            "encoding": "tags text inspected in Latin-1; coverage joins use IDs only",
            "coverage_limit": "whole-snapshot availability; not leakage-safe train coverage",
        },
        "interaction_quality": quality,
        "quality_by_table": table_quality,
        "source_rows": len(interactions),
        "users": len(histories),
        "artists": len(profiles),
        "unique_pairs": unique_pairs,
        "possible_pairs": possible_pairs,
        "density": unique_pairs / possible_pairs,
        "sparsity": 1 - unique_pairs / possible_pairs,
        "total_listens": int(observed.weight.sum()),
        "distributions": {
            "listening_count": describe(observed.weight),
            "user_history": describe(histories),
            "artist_listeners": describe(listeners),
            "tags_per_catalog_artist_including_zero": describe(profiles.unique_tags),
        },
        "history": {
            "exactly_50_artists": int(histories.eq(50).sum()),
            "below_5_users": int(histories.lt(5).sum()),
            "pairs_at_below_5_users": int(histories[histories.lt(5)].sum()),
        },
        "long_tail": {
            "one_listener_artists": int(listeners.eq(1).sum()),
            "below_5_listener_artists": int(listeners.lt(5).sum()),
            "pairs_at_below_5_listener_artists": int(listeners[listeners.lt(5)].sum()),
        },
        "concentration": concentration,
        "tags": {
            "assignment_rows": len(assignments),
            "catalog_assignment_rows": len(catalog_tags),
            "outside_catalog_rows": len(assignments) - len(catalog_tags),
            "outside_catalog_artist_ids": int(
                assignments.loc[~assignments.artistID.isin(artists.id), "artistID"].nunique()
            ),
            "duplicate_user_artist_tag_extra_rows": int(
                assignments.duplicated(["userID", "artistID", "tagID"]).sum()
            ),
            "catalog_artists_with_tags": int(covered.sum()),
            "catalog_artists_without_tags": int((~covered).sum()),
            "artist_coverage": float(covered.mean()),
            "pairs_at_tagged_artists": int(profiles.loc[covered, "listeners"].sum()),
            "pair_coverage": float(profiles.loc[covered, "listeners"].sum() / unique_pairs),
            "tags_used_in_catalog": len(tag_frequency),
            "tags_on_one_catalog_artist": int(tag_frequency.eq(1).sum()),
        },
        "text_encoding": encoding,
        "not_performed": [
            "row deletion or aggregation into cleaned data",
            "ID mapping",
            "split",
            "model input transformation",
            "training or tuning",
        ],
    }
    out.mkdir(parents=True, exist_ok=False)
    (out / "figures").mkdir()
    (out / "tables").mkdir()
    pd.DataFrame(missing).to_csv(out / "tables/quality_by_column.csv", index=False)
    pd.DataFrame(table_quality).T.to_csv(out / "tables/quality_by_table.csv", index_label="file")
    histories.rename("artists").to_csv(out / "tables/user_history.csv")
    profiles.to_csv(out / "tables/artist_profile.csv", index_label="artistID")
    tag_frequency.to_csv(out / "tables/tag_frequency.csv")
    pd.DataFrame(metrics["distributions"]).to_csv(out / "tables/distribution_summary.csv")
    metrics["figures"] = make_figures(out / "figures", observed.weight, histories, profiles)
    shutil.copyfile(__file__, out / "eda_script.py")
    if any(sha256(Path(p)) != value for p, value in hashes.items()):
        raise RuntimeError("Source data changed during EDA")
    metrics["raw_inputs_unchanged"] = True
    metrics["finished_at_utc"] = datetime.now(UTC).isoformat()
    with (out / "metrics.json").open("x", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(
        json.dumps(
            {
                "run": str(out),
                "users": len(histories),
                "artists": len(profiles),
                "pairs": unique_pairs,
                "raw_unchanged": True,
            }
        )
    )


if __name__ == "__main__":
    main()
