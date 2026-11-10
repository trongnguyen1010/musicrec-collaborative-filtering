"""E-D: descriptive statistics of the raw HetRec Last.fm 2k tables and of the cleaned data.

Reads data/raw/hetrec2011 (user_artists.dat, artists.dat, user_taggedartists.dat; UTF-8,
tags.dat Latin-1) and the locked cleaning outputs (rebuilt locally, chuong_4_bo_sung/
cleaning, whose counts equal the official Step 3 run). Checks the numbers quoted in the
advisor's draft, redraws Figures 4.1 and 4.2 on the RAW data and records how much of the
train catalog has usable tag vectors (the basis of tag ILD). Nothing is filtered here.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_ch4_extras import BLUE, style  # noqa: E402
from run_e7_topn import runtime  # noqa: E402

RAW = Path("data/raw/hetrec2011")
CLEAN = Path("outputs/chinh_thuc_cloud_20261026/chuong_4_bo_sung/cleaning")
ILD_REPORT = Path("outputs/chuong_4_bo_sung_2/thong_ke/phan_tich/ild_the_mo_hinh.json")
# Numbers quoted in the advisor's draft (feedback of 06/11/2026), checked one by one.
DRAFT = {
    "users_raw": 1892,
    "artists_catalog_raw": 17632,
    "artists_with_interactions_after": 17617,
    "interactions_raw": 92834,
    "interactions_after": 92801,
    "density_raw_pct": 0.2783,
    "mean_artists_per_user_raw": 49.07,
    "users_exactly_50_artists_raw": 1829,
    "users_exactly_50_artists_raw_pct": 96.67,
    "mean_listeners_per_artist_raw": 5.27,
    "median_listeners_per_artist_raw": 1,
    "total_listens": 69138727,
    "max_pair_listening_count": 352698,
    "tag_assignment_rows_raw": 186479,
    "tag_assignment_rows_joined_catalog": 184941,
    "catalog_artists_without_tags": 5499,
    "active_artists_without_tags": 5493,
}


def describe(frame: pd.DataFrame, catalog: int) -> dict[str, Any]:
    users = frame.user_id.nunique()
    per_user = frame.groupby("user_id").size()
    listeners = frame.groupby("item_id").user_id.nunique()
    plays = frame.groupby("user_id").listening_count.sum()
    return {
        "users": int(users),
        "artists_catalog": int(catalog),
        "artists_with_interactions": int(listeners.size),
        "interactions": int(len(frame)),
        "density_pct": 100 * len(frame) / (users * catalog),
        "density_active_artists_pct": 100 * len(frame) / (users * listeners.size),
        "mean_artists_per_user": float(per_user.mean()),
        "median_artists_per_user": float(per_user.median()),
        "min_artists_per_user": int(per_user.min()),
        "max_artists_per_user": int(per_user.max()),
        "users_exactly_50_artists": int((per_user == 50).sum()),
        "users_exactly_50_artists_pct": float(100 * (per_user == 50).mean()),
        "mean_listeners_per_artist_catalog": float(len(frame) / catalog),
        "mean_listeners_per_active_artist": float(listeners.mean()),
        "median_listeners_per_active_artist": float(listeners.median()),
        "single_listener_artists": int((listeners == 1).sum()),
        "total_listens": int(frame.listening_count.sum()),
        "max_pair_listening_count": int(frame.listening_count.max()),
        "median_pair_listening_count": float(frame.listening_count.median()),
        "mean_total_listens_per_user": float(plays.mean()),
        "median_total_listens_per_user": float(plays.median()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW / "user_artists.dat", sep="\t", dtype=str, encoding="utf-8")
    raw = raw.rename(columns={"userID": "user_id", "artistID": "item_id", "weight": "w"})
    raw["listening_count"] = raw.w.astype(np.int64)
    artists = pd.read_csv(RAW / "artists.dat", sep="\t", dtype=str, encoding="utf-8")
    tags_raw = pd.read_csv(RAW / "user_taggedartists.dat", sep="\t", dtype=str, encoding="utf-8")
    clean = pd.read_parquet(CLEAN / "interactions.parquet").astype({"user_id": str, "item_id": str})
    tags_clean = pd.read_parquet(CLEAN / "tag_assignments.parquet")
    catalog = set(artists.id)
    tagged = set(tags_clean.artistID.astype(str)) & catalog
    active = set(clean.item_id)
    stats = {
        "raw": describe(raw, len(catalog)),
        "after_cleaning": describe(clean, len(catalog)),
        "tags": {
            "tag_assignment_rows_raw": int(len(tags_raw)),
            "tag_assignment_rows_joined_catalog": int(len(tags_clean)),
            "tag_rows_outside_catalog": int(len(tags_raw) - len(tags_clean)),
            "catalog_artists_with_tags": len(tagged),
            "catalog_artists_without_tags": len(catalog - tagged),
            "active_artists_without_tags": len(active - tagged),
        },
    }
    ild = json.loads(ILD_REPORT.read_text(encoding="utf-8"))["tag_features"]
    train_catalog = ild["tagged_catalog_artists"] + ild["untagged_catalog_artists"]
    stats["tag_ild_coverage"] = {
        "source": str(ILD_REPORT),
        "train_catalog_artists": train_catalog,
        "train_catalog_with_tag_vector_df2": ild["tagged_catalog_artists"],
        "share_pct": 100 * ild["tagged_catalog_artists"] / train_catalog,
        "note": "tag vectors use train user-artist pairs only and tags with df >= 2",
    }
    flat = {**stats["raw"], **stats["after_cleaning"], **stats["tags"]}
    actual = {
        "users_raw": stats["raw"]["users"],
        "artists_catalog_raw": stats["raw"]["artists_catalog"],
        "artists_with_interactions_after": stats["after_cleaning"]["artists_with_interactions"],
        "interactions_raw": stats["raw"]["interactions"],
        "interactions_after": stats["after_cleaning"]["interactions"],
        "density_raw_pct": stats["raw"]["density_pct"],
        "mean_artists_per_user_raw": stats["raw"]["mean_artists_per_user"],
        "users_exactly_50_artists_raw": stats["raw"]["users_exactly_50_artists"],
        "users_exactly_50_artists_raw_pct": stats["raw"]["users_exactly_50_artists_pct"],
        "mean_listeners_per_artist_raw": stats["raw"]["mean_listeners_per_artist_catalog"],
        "median_listeners_per_artist_raw": stats["raw"]["median_listeners_per_active_artist"],
        "total_listens": stats["after_cleaning"]["total_listens"],
        "max_pair_listening_count": stats["after_cleaning"]["max_pair_listening_count"],
        "tag_assignment_rows_raw": flat["tag_assignment_rows_raw"],
        "tag_assignment_rows_joined_catalog": flat["tag_assignment_rows_joined_catalog"],
        "catalog_artists_without_tags": flat["catalog_artists_without_tags"],
        "active_artists_without_tags": flat["active_artists_without_tags"],
    }
    checks = []
    for key, quoted in DRAFT.items():
        value = actual[key]
        decimals = len(str(quoted).split(".")[1]) if isinstance(quoted, float) else 0
        rounded = round(value, decimals) if decimals else round(value)
        checks.append(
            {"so_lieu": key, "ban_nhap": quoted, "tinh_lai": value, "khop": rounded == quoted}
        )
    stats["draft_checks"] = checks
    pd.DataFrame(checks).to_csv(out / "kiem_tra_so_lieu_ban_nhap.csv", index=False)
    rows = [
        {"chi_so": k, "goc": stats["raw"][k], "sau_loc": stats["after_cleaning"][k]}
        for k in stats["raw"]
    ]
    pd.DataFrame(rows).to_csv(out / "thong_ke_mo_ta.csv", index=False)

    listeners = raw.groupby("item_id").user_id.nunique().sort_values(ascending=False).to_numpy()
    pd.DataFrame({"hang": np.arange(1, len(listeners) + 1), "so_nguoi_nghe": listeners}).to_csv(
        out / "hinh_4_1_goc.csv", index=False
    )
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    ax.plot(np.arange(1, len(listeners) + 1), listeners, color=BLUE, linewidth=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Thứ hạng nghệ sĩ theo số người nghe (thang log)")
    ax.set_ylabel("Số người nghe (thang log)")
    style(ax)
    fig.tight_layout()
    fig.savefig(out / "hinh_4_1_goc.png", dpi=300)
    plt.close(fig)
    plays = raw.groupby("user_id").listening_count.sum()
    plays.to_csv(out / "hinh_4_2_goc.csv", header=["tong_luot_nghe"])
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    bins = np.logspace(np.log10(max(1, plays.min())), np.log10(plays.max()), 40)
    ax.hist(plays, bins=bins, color=BLUE, edgecolor="white", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Tổng lượt nghe của người dùng trong dữ liệu gốc (thang log)")
    ax.set_ylabel("Số người dùng")
    style(ax)
    fig.tight_layout()
    fig.savefig(out / "hinh_4_2_goc.png", dpi=300)
    plt.close(fig)
    stats["created_at_utc"] = datetime.now(UTC).isoformat()
    stats["command"] = sys.argv
    stats["runtime"] = runtime()
    (out / "metrics.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", "utf-8"
    )
    print(pd.DataFrame(checks).to_string())


if __name__ == "__main__":
    main()
