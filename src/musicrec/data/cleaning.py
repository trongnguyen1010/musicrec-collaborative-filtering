"""Clean source observations without splitting or learning model inputs."""

import csv
from pathlib import Path
from typing import Any

import pandas as pd


def read_source_table(path: Path) -> pd.DataFrame:
    """Read literal TAB fields, preserving NA text and per-file encoding."""
    frame = pd.read_csv(
        path,
        sep="\t",
        encoding="latin-1" if path.name == "tags.dat" else "utf-8",
        dtype=str,
        keep_default_na=False,
        quoting=csv.QUOTE_NONE,
    )
    return frame


def clean_interactions(
    source: pd.DataFrame, artist_ids: set[str], min_user_interactions: int = 5
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """Keep valid distinct counts; reject conflicting pairs instead of summing."""
    if type(min_user_interactions) is not int or min_user_interactions < 1:
        raise ValueError("min_user_interactions must be a positive integer")
    frame = source.loc[:, ["userID", "artistID", "weight"]].copy()
    frame["source_line"] = range(2, len(frame) + 2)
    frame["removal_reason"] = ""
    valid_ids = (
        frame[["userID", "artistID"]]
        .apply(lambda column: column.str.fullmatch(r"[1-9][0-9]*", na=False))
        .all(axis=1)
    )
    # HetRec counts are positive int64 integers, not explicit ratings or floats.
    integers = frame.weight.str.fullmatch(r"[0-9]+", na=False)
    counts = frame.weight.where(integers, "0").map(int)
    valid_counts = integers & counts.gt(0) & counts.le(2**63 - 1)
    for invalid, reason in [
        (~valid_ids, "invalid_id"),
        (~valid_counts, "invalid_count"),
        (~frame.artistID.isin(artist_ids), "artist_outside_catalog"),
    ]:
        frame.loc[invalid & frame.removal_reason.eq(""), "removal_reason"] = reason
    eligible = frame.removal_reason.eq("")
    observed = frame.loc[eligible, ["userID", "artistID"]].assign(weight=counts[eligible])
    conflicts = observed.groupby(["userID", "artistID"]).weight.nunique().gt(1)
    if conflicts.any():
        raise ValueError(
            f"Conflicting counts for user-artist pairs: {list(conflicts[conflicts].index)}"
        )
    duplicate = observed.duplicated(["userID", "artistID", "weight"])
    frame.loc[observed.index[duplicate], "removal_reason"] = "duplicate_observation"
    eligible = frame.removal_reason.eq("")
    histories = frame.loc[eligible].groupby("userID").artistID.nunique()
    short_users = set(histories[histories < min_user_interactions].index)
    frame.loc[eligible & frame.userID.isin(short_users), "removal_reason"] = "user_below_minimum"
    kept = frame.loc[frame.removal_reason.eq(""), ["userID", "artistID"]].copy()
    kept["listening_count"] = counts.loc[kept.index].astype("int64")
    kept = kept.rename(columns={"userID": "user_id", "artistID": "item_id"})
    kept = kept.sort_values(["user_id", "item_id"]).reset_index(drop=True)
    excluded = frame.loc[frame.removal_reason.ne("")].reset_index(drop=True)
    reasons = [
        "invalid_id",
        "invalid_count",
        "artist_outside_catalog",
        "duplicate_observation",
        "user_below_minimum",
    ]
    summary = {
        "input_rows": len(frame),
        "output_rows": len(kept),
        "excluded_rows": len(excluded),
        "users_below_minimum": len(short_users),
        **{reason: int(frame.removal_reason.eq(reason).sum()) for reason in reasons},
    }
    return kept, excluded, summary


def clean_tables(
    interactions: pd.DataFrame,
    artists: pd.DataFrame,
    tags: pd.DataFrame,
    assignments: pd.DataFrame,
    min_user_interactions: int = 5,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """Separate foreign artist tags while keeping authorship and missing content."""
    for frame, key in [(artists, "id"), (tags, "tagID")]:
        if (
            frame[key].duplicated().any()
            or not frame[key].str.fullmatch(r"[1-9][0-9]*", na=False).all()
        ):
            raise ValueError(f"Invalid or duplicate catalog key: {key}")
    artist_ids = set(artists.id)
    cleaned, excluded, quality = clean_interactions(interactions, artist_ids, min_user_interactions)
    if cleaned.empty:
        raise ValueError("Cleaning leaves no interactions")
    for key, allowed in [("userID", set(interactions.userID)), ("tagID", set(tags.tagID))]:
        if not assignments[key].isin(allowed).all():
            raise ValueError(f"Tag assignments contain unknown {key}")
    outside = ~assignments.artistID.isin(artist_ids)
    orphan = assignments.loc[outside].copy()
    orphan["source_line"] = assignments.index[outside] + 2
    orphan["removal_reason"] = "artist_outside_catalog"
    valid_tags = assignments.loc[~outside].copy()
    artists = artists.copy()
    artists["display_name"] = artists.name.where(
        artists.name.str.strip().ne(""), "Artist " + artists.id
    )
    tagged_ids, active_ids = set(valid_tags.artistID), set(cleaned.item_id)
    tables = {
        "interactions": cleaned,
        "excluded_interactions": excluded,
        "artists": artists,
        "tags": tags.copy(),
        "tag_assignments": valid_tags,
        "excluded_tag_assignments": orphan,
    }
    metrics = {
        "interaction_rules": quality,
        "before": {
            "users": int(interactions.userID.nunique()),
            "interaction_artists": int(interactions.artistID.nunique()),
            "interactions": len(interactions),
            "catalog_artists": len(artists),
        },
        "after": {
            "users": int(cleaned.user_id.nunique()),
            "interaction_artists": len(active_ids),
            "interactions": len(cleaned),
            "catalog_artists": len(artists),
            "total_listens": int(cleaned.listening_count.sum()),
            "min_user_history": int(cleaned.groupby("user_id").item_id.nunique().min()),
            "single_listener_artists": int(
                cleaned.groupby("item_id").user_id.nunique().eq(1).sum()
            ),
            "max_listening_count": int(cleaned.listening_count.max()),
        },
        "tags": {
            "dictionary_rows": len(tags),
            "input_assignments": len(assignments),
            "retained_assignments": len(valid_tags),
            "excluded_assignments": len(orphan),
            "excluded_artist_ids": int(orphan.artistID.nunique()),
            "catalog_artists_with_tags": len(artist_ids & tagged_ids),
            "catalog_artists_without_tags": len(artist_ids - tagged_ids),
            "active_artists_without_tags": len(active_ids - tagged_ids),
            "assignments_by_excluded_users_retained_for_later_protocol_filtering": int(
                (~valid_tags.userID.isin(set(cleaned.user_id))).sum()
            ),
            "scope": "Source metadata only; retain userID for later M2 protocol filtering",
        },
    }
    return tables, metrics
