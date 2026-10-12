"""Recompute the LastFM dataset card and figures from the official archive."""

import csv
import json
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

from musicrec.research.io import OUT, ROOT, provenance, sha256, track, write_json

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = ROOT / "data/raw/hetrec2011"
DOCS = ROOT / "docs/research"


def read_table(name: str) -> pd.DataFrame:
    """Strict TSV parsing; never silently drop malformed records."""
    # The verified tags.dat has CP1252 bytes (e.g. tropic\xe1lia), not valid UTF-8.
    encoding = "cp1252" if name == "tags.dat" else "utf-8"
    return pd.read_csv(RAW / name, sep="\t", quoting=csv.QUOTE_NONE, encoding=encoding)


def canonical_pairs() -> set[tuple[str, str]]:
    """The unchanged raw interaction population, for split conservation checks."""
    frame = read_table("user_artists.dat")
    return set(zip(frame.userID.astype(str), frame.artistID.astype(str), strict=True))


def describe(values: pd.Series) -> dict[str, float]:
    """Quantiles relevant to long-tail and implicit listening counts."""
    return {str(q): float(values.quantile(q)) for q in [0, 0.25, 0.5, 0.75, 0.9, 0.99, 1]}


def analyze() -> dict[str, Any]:
    """Validate all six tables, generate figures and record a local MLflow run."""
    frames = {
        name: read_table(name)
        for name in [
            "artists.dat",
            "tags.dat",
            "user_artists.dat",
            "user_friends.dat",
            "user_taggedartists.dat",
            "user_taggedartists-timestamps.dat",
        ]
    }
    artists, tags = frames["artists.dat"], frames["tags.dat"]
    inter, friends = frames["user_artists.dat"], frames["user_friends.dat"]
    tagged = frames["user_taggedartists.dat"]
    stamped = frames["user_taggedartists-timestamps.dat"]
    if inter.isna().any().any() or inter.duplicated(["userID", "artistID"]).any():
        raise ValueError("Missing or duplicate interaction")
    if not np.isfinite(inter.weight).all() or not (inter.weight > 0).all():
        raise ValueError("Nonfinite/nonpositive listening count")
    user_ids, artist_ids, tag_ids = set(inter.userID), set(artists.id), set(tags.tagID)
    if not set(inter.artistID) <= artist_ids:
        raise ValueError("Interaction artist absent from metadata")
    if len(artist_ids) != len(artists) or len(tag_ids) != len(tags):
        raise ValueError("Duplicate metadata ID")
    users = inter.groupby("userID").size()
    listeners = inter.groupby("artistID").size()
    edge_set = set(zip(friends.userID, friends.friendID, strict=True))
    relations = {
        "tag_unknown_users": len(set(tagged.userID) - user_ids),
        "tag_unknown_artists": len(set(tagged.artistID) - artist_ids),
        "tag_unknown_tags": len(set(tagged.tagID) - tag_ids),
        "friend_unknown_users": len((set(friends.userID) | set(friends.friendID)) - user_ids),
        "friend_missing_reverse": sum((b, a) not in edge_set for a, b in edge_set),
        "friend_self_loops": sum(a == b for a, b in edge_set),
    }
    if any(
        relations[key]
        for key in [
            "tag_unknown_users",
            "tag_unknown_tags",
            "friend_unknown_users",
        ]
    ):
        raise ValueError(f"Broken metadata references: {relations}")
    filters = {}
    for name, frame in [
        ("user_min_5", inter[inter.userID.isin(users[users >= 5].index)]),
        ("item_min_5", inter[inter.artistID.isin(listeners[listeners >= 5].index)]),
        (
            "both_single_pass",
            inter[
                inter.userID.isin(users[users >= 5].index)
                & inter.artistID.isin(listeners[listeners >= 5].index)
            ],
        ),
    ]:
        filters[name] = {
            "pairs": len(frame),
            "users": frame.userID.nunique(),
            "artists": frame.artistID.nunique(),
        }
    filtered = inter.copy()
    while True:
        n = len(filtered)
        filtered = filtered[filtered.groupby("userID").userID.transform("size") >= 5]
        filtered = filtered[filtered.groupby("artistID").artistID.transform("size") >= 5]
        if len(filtered) == n:
            break
    filters["iterative_5_core"] = {
        "pairs": len(filtered),
        "users": filtered.userID.nunique(),
        "artists": filtered.artistID.nunique(),
    }
    dates = pd.to_datetime(tagged[["year", "month", "day"]], errors="coerce")
    data: dict[str, Any] = {
        "source": "https://grouplens.org/datasets/hetrec-2011/",
        "zip_sha256": sha256(ROOT / "data/raw/hetrec2011-lastfm-2k.zip"),
        "files": {
            name: {
                "rows": len(frame),
                "columns": list(frame.columns),
                "encoding": "cp1252" if name == "tags.dat" else "utf-8",
                "nulls": {str(k): int(v) for k, v in frame.isna().sum().items()},
                "duplicate_rows": int(frame.duplicated().sum()),
                "sha256": sha256(RAW / name),
            }
            for name, frame in frames.items()
        },
        "users": len(users),
        "artists": len(artists),
        "pairs": len(inter),
        "density": len(inter) / (len(users) * len(artists)),
        "duplicate_pairs": 0,
        "total_listening_weight": int(inter.weight.sum()),
        "weight_quantiles": describe(inter.weight),
        "artists_per_user": describe(users),
        "listeners_per_artist": describe(listeners),
        "popular_artist_pair_share": {
            str(n): float(listeners.nlargest(n).sum() / len(inter)) for n in [10, 100, 1000]
        },
        "users_exactly_50_artists": int((users == 50).sum()),
        "users_under_3": int((users < 3).sum()),
        "users_under_5": int((users < 5).sum()),
        "artists_under_5_listeners": int((listeners < 5).sum()),
        "artists_with_tags": len(set(tagged.artistID) & artist_ids),
        "artists_in_tag_file": tagged.artistID.nunique(),
        "tag_rows_unknown_artist": int((~tagged.artistID.isin(artist_ids)).sum()),
        "users_with_tags": tagged.userID.nunique(),
        "tag_artist_coverage": len(set(tagged.artistID) & artist_ids) / len(artists),
        "directed_friendships": len(friends),
        "users_with_friends": len(set(friends.userID) | set(friends.friendID)),
        "friends_per_user": describe(
            friends.groupby("userID").size().reindex(sorted(user_ids), fill_value=0)
        ),
        "undirected_friendships": len({tuple(sorted((a, b))) for a, b in edge_set}),
        "tag_invalid_calendar_dates": int(dates.isna().sum()),
        "tag_timestamp_range": [int(stamped.timestamp.min()), int(stamped.timestamp.max())],
        "relations": relations,
        "filter_impact": filters,
        "provenance": provenance(),
    }
    prior = json.loads((ROOT / "docs/seminar/dataset_verified.json").read_text(encoding="utf-8"))
    for old, new in [
        ("sha256", "zip_sha256"),
        ("rows", "pairs"),
        ("users", "users"),
        ("artists_in_metadata", "artists"),
    ]:
        if prior[old] != data[new]:
            raise ValueError(f"Dataset differs from prior evidence: {old}")
    DOCS.mkdir(parents=True, exist_ok=True)
    figures = DOCS / "figures"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "figure.figsize": (8, 4.5)})
    for name, values, label in [
        ("listening_weight", inter.weight, "Listening count (log scale)"),
        ("artist_listeners", listeners, "Listeners per artist (log scale)"),
    ]:
        fig, ax = plt.subplots()
        ax.hist(values, bins=np.geomspace(max(1, values.min()), values.max() + 1, 45).tolist())
        ax.set(xscale="log", yscale="log", xlabel=label, ylabel="Frequency")
        fig.tight_layout()
        fig.savefig(figures / f"{name}.png", dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots()
    ranked = listeners.sort_values(ascending=False).to_numpy()
    ax.plot(np.arange(1, len(ranked) + 1) / len(ranked), np.cumsum(ranked) / ranked.sum())
    ax.set(xlabel="Fraction of artists, most popular first", ylabel="Cumulative fraction of pairs")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures / "popularity_concentration.png", dpi=160)
    plt.close(fig)
    report = DOCS / "dataset-study.md"
    lines = [
        "# Nghiên cứu HetRec 2011 Last.fm 2K",
        "",
        "Nguồn: [GroupLens](https://grouplens.org/datasets/hetrec-2011/). "
        "Dùng phi thương mại; ghi nhận Last.fm và Cantador, Brusilovsky, Kuflik (2011).",
        "",
        f"SHA-256 ZIP: `{data['zip_sha256']}`. Khớp bằng chứng kiểm tra trước trong dự án.",
        "",
        "## Cấu trúc và chất lượng",
        "",
        "`tags.dat` không phải UTF-8 hợp lệ; đọc CP1252 có thể mã hóa ngược bảo toàn byte. "
        "Các tệp còn lại đọc UTF-8 nghiêm ngặt. Cần kiểm tra ngữ nghĩa tag trước M2.",
        "",
        f"Có **{len(users):,} người dùng**, **{len(artists):,} nghệ sĩ**, **{len(inter):,} cặp**. "
        f"Mật độ {data['density']:.6%}; độ thưa {1 - data['density']:.6%}. "
        "Số cặp không phải tổng lượt nghe; mỗi cặp mang trọng số phản hồi ngầm.",
        "",
        "| Tệp | Số dòng | Trường |",
        "|---|---:|---|",
    ]
    lines += [
        f"| {name} | {len(frame):,} | {', '.join(frame.columns)} |"
        for name, frame in frames.items()
    ]
    lines += [
        "",
        "Không có interaction thiếu, trùng hoặc trọng số không hữu hạn/không dương. "
        f"Kiểm tra liên kết: `{relations}`.",
        "",
        "## Phân bố và hệ quả",
        "",
        f"Tổng trọng số lượt nghe quan sát: {data['total_listening_weight']:,}. "
        "Đây là tổng trên các cặp được thu thập, không phải lịch sử nghe toàn bộ của user.",
        "",
        "| Phân bố | Min | P25 | P50 | P75 | P90 | P99 | Max |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {label} | " + " | ".join(f"{value:,.2f}" for value in data[key].values()) + " |"
            for key, label in [
                ("weight_quantiles", "Lượt nghe/cặp"),
                ("artists_per_user", "Nghệ sĩ/user"),
                ("listeners_per_artist", "Người nghe/nghệ sĩ"),
            ]
        ],
        "",
        "Tỷ lệ cặp thuộc nhóm nghệ sĩ phổ biến nhất: "
        + "; ".join(
            f"top {n}: {fraction:.2%}" for n, fraction in data["popular_artist_pair_share"].items()
        )
        + ".",
        "",
        f"Trung vị lượt nghe: {inter.weight.median():g}; lớn nhất: {inter.weight.max():,}. "
        "Lượt nghe lệch mạnh, không thể diễn giải trực tiếp như rating 1–5.",
        "",
        f"{data['users_exactly_50_artists']}/{len(users)} user có đúng 50 nghệ sĩ; "
        f"{data['users_under_3']} user dưới 3 và {data['users_under_5']} user dưới 5. "
        "Given-N về sau phải được thiết kế bằng cách ẩn lịch sử, không suy ra rằng "
        "dữ liệu hiện tại đại diện đầy đủ cho người dùng mới.",
        "",
        f"{data['artists_under_5_listeners']:,} nghệ sĩ có dưới 5 người nghe. "
        "Lọc item làm thay đổi long-tail, vì vậy không áp vào tái hiện không lọc.",
        "",
        "| Bộ lọc khảo sát | Cặp | User | Nghệ sĩ |",
        "|---|---:|---:|---:|",
    ]
    lines += [
        f"| {name} | {row['pairs']:,} | {row['users']:,} | {row['artists']:,} |"
        for name, row in filters.items()
    ]
    lines += [
        "",
        "## Tag, mạng xã hội và giới hạn",
        "",
        f"Tag phủ {data['artists_with_tags']:,}/{len(artists):,} nghệ sĩ "
        f"({data['tag_artist_coverage']:.2%}) và {data['users_with_tags']:,} user. "
        f"Có {data['undirected_friendships']:,} cạnh bạn bè vô hướng.",
        f"{data['users_with_friends']:,}/{len(users):,} user có ít nhất một bạn; "
        f"trung vị bậc bạn bè {data['friends_per_user']['0.5']:g}, "
        f"lớn nhất {data['friends_per_user']['1']:g}. "
        "Bậc này tính cả user không có bạn bằng 0.",
        f"Có {data['artists_in_tag_file']:,} ID nghệ sĩ trong tệp tag; "
        f"{relations['tag_unknown_artists']} ID ngoài metadata, tương ứng "
        f"{data['tag_rows_unknown_artist']:,} lượt gắn tag. Độ phủ ở trên dùng giao "
        "với catalog, không lấy toàn bộ ID tag chia cho số nghệ sĩ.",
        "",
        f"Ngày tag không hợp lệ theo lịch: {data['tag_invalid_calendar_dates']}. "
        "Timestamp là thời điểm gắn tag, không phải thời điểm nghe. Các tag cũng là "
        "dữ liệu tương tác: M2 phải kiểm soát nguồn tag của các cặp bị giữ lại.",
        "",
        "## Hình sinh tự động",
        "",
        "![Lượt nghe](figures/listening_weight.png)",
        "",
        "![Người nghe mỗi nghệ sĩ](figures/artist_listeners.png)",
        "",
        "![Tập trung phổ biến](figures/popularity_concentration.png)",
        "",
        "Tái tạo: `python scripts/research.py analyze`. Chi tiết định lượng, schema, "
        "quantile và checksum từng tệp nằm trong artifact `dataset_analysis.json`.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    downloaded = json.loads((OUT / "download_manifest.json").read_text(encoding="utf-8"))
    card = ROOT / "docs/data-card.md"
    card.write_text(
        "\n".join(
            [
                "# Data card: HetRec 2011 Last.fm 2K",
                "",
                "| Thuộc tính | Giá trị |",
                "|---|---|",
                "| Nguồn | https://files.grouplens.org/datasets/hetrec2011/"
                "hetrec2011-lastfm-2k.zip |",
                f"| Ngày tải UTC | {downloaded['dataset']['downloaded_at']} |",
                "| Phiên bản | 1.0, May 2011 |",
                f"| SHA-256 | `{data['zip_sha256']}` |",
                f"| Kích thước ZIP | {downloaded['dataset']['bytes']} byte |",
                "| Đơn vị | user–artist; weight là số lượt nghe, phản hồi ngầm |",
                "| Quy mô | 1.892 user; 17.632 artist; 92.834 cặp |",
                "| Giấy phép | Phi thương mại; liên hệ Last.fm nếu dùng thương mại |",
                "| Trích dẫn | Last.fm; Cantador, Brusilovsky, Kuflik, HetRec 2011 |",
                "| Encoding | tags.dat CP1252; các bảng còn lại UTF-8 |",
                "",
                "Schema raw: `userID`, `artistID`, `weight`. Giữ nguyên ZIP và số lượt nghe. "
                "Tái hiện dùng binary/no-filter và 30 split tác giả; "
                "giao thức khóa luận tách riêng.",
                "",
                "Metadata có 444 pictureURL thiếu và 390 ID artist chỉ xuất hiện trong tag. "
                "Timestamp của tag không phải lịch sử nghe. Xem [nghiên cứu dữ liệu]"
                "(research/dataset-study.md) và manifest/MLflow cục bộ để truy vết.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = OUT / "dataset_analysis.json"
    write_json(result, data)
    run_id = track(
        "dataset-study",
        {"dataset_sha256": data["zip_sha256"], "git_sha": data["provenance"]["git_sha"]},
        {
            "users": float(len(users)),
            "artists": float(len(artists)),
            "pairs": float(len(inter)),
            "density": data["density"],
        },
        [result, report, card, *figures.glob("*.png")],
    )
    data["mlflow_run_id"] = run_id
    write_json(result, data)
    with report.open("a", encoding="utf-8") as stream:
        stream.write(f"\nMLflow run: `{run_id}`.\n")
    return data
