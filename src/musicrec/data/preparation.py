"""Validate HetRec counts, split by user, and fit train-only preference transforms."""

from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def validate_interactions(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Reject malformed source data; collapse duplicate pairs by summing raw counts."""
    try:
        frame = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("Interaction file is empty") from exc
    required = {"userID", "artistID", "weight"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing source columns: {sorted(required - set(frame.columns))}")
    if frame.empty:
        raise ValueError("Interaction file has no rows")
    frame = frame[["userID", "artistID", "weight"]].rename(
        columns={"userID": "user_id", "artistID": "item_id", "weight": "listening_count"}
    )
    for col in ("user_id", "item_id"):
        frame[col] = frame[col].str.strip()
        if frame[col].eq("").any():
            raise ValueError(f"Empty identifier in {col}: {int(frame[col].eq('').sum())} rows")
    try:
        frame["listening_count"] = pd.to_numeric(frame["listening_count"], errors="raise").astype(
            float
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("listening_count must be numeric") from exc
    counts = frame["listening_count"].to_numpy(dtype=float)
    if not np.isfinite(counts).all() or (counts <= 0).any():
        raise ValueError(
            f"listening_count must be finite and positive: "
            f"nonfinite={int((~np.isfinite(counts)).sum())}, nonpositive={int((counts <= 0).sum())}"
        )
    before = len(frame)
    frame = frame.groupby(["user_id", "item_id"], as_index=False, sort=True).agg(
        listening_count=("listening_count", "sum")
    )
    if not np.isfinite(frame["listening_count"].to_numpy(dtype=float)).all():
        raise ValueError("Duplicate aggregation overflowed")
    users = frame["user_id"].nunique()
    items = frame["item_id"].nunique()
    histories = frame.groupby("user_id").size()
    listeners = frame.groupby("item_id").size()
    report = {
        "rows_source": before,
        "duplicate_rows_merged": before - len(frame),
        "invalid_rows": 0,
        "invalid_policy": "fail_without_silent_drops",
        "duplicate_policy": "sum_counts_before_split",
        "rows": len(frame),
        "users": users,
        "artists": items,
        "density": len(frame) / (users * items),
        "sparsity": 1 - len(frame) / (users * items),
        "users_under_5": int((histories < 5).sum()),
        "history_quantiles": {
            str(q): float(histories.quantile(q)) for q in (0, 0.25, 0.5, 0.75, 1)
        },
        "listener_quantiles": {
            str(q): float(listeners.quantile(q)) for q in (0, 0.25, 0.5, 0.75, 1)
        },
        "count_quantiles": {
            str(q): float(frame.listening_count.quantile(q)) for q in (0, 0.25, 0.5, 0.75, 0.99, 1)
        },
        "history_distribution": dict(sorted(Counter(map(int, histories)).items())),
    }
    return frame, report


def load_artists(path: Path, interactions: pd.DataFrame) -> tuple[dict[str, str], dict[str, Any]]:
    """Keep valid interactions even when their display name is unavailable."""
    frame = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    if not {"id", "name"}.issubset(frame.columns) or frame.empty:
        raise ValueError("artists.dat requires nonempty id and name columns")
    frame["id"] = frame["id"].str.strip()
    if frame.id.eq("").any() or frame.id.duplicated().any():
        raise ValueError("Artist metadata contains empty or duplicate IDs")
    names = {str(row.id): str(row.name).strip() or f"Artist {row.id}" for row in frame.itertuples()}
    unknown = sorted(set(interactions.item_id) - set(names))
    return names, {
        "artists_metadata": len(frame),
        "interaction_ids_missing_metadata": unknown,
        "missing_name_count": int(frame.name.str.strip().eq("").sum()),
    }


def split_interactions(
    frame: pd.DataFrame, seed: int, minimum: int = 5, fraction: float = 0.1
) -> dict[str, pd.DataFrame]:
    """Split sorted unique pairs; users below minimum stay entirely in train."""
    if minimum < 5 or not 0 < fraction < 0.5:
        raise ValueError("Expected minimum >= 5 and held-out fraction in (0, .5)")
    if frame.duplicated(["user_id", "item_id"]).any() or frame.empty:
        raise ValueError("Split requires nonempty, deduplicated interactions")
    ordered = frame.sort_values(["user_id", "item_id"]).reset_index(drop=True)
    rng = np.random.default_rng(seed)
    indices: dict[str, list[int]] = {"train": [], "validation": [], "test": []}
    for _, group in ordered.groupby("user_id", sort=True):
        positions = group.index.to_numpy()
        if len(positions) < minimum:
            indices["train"].extend(positions.tolist())
            continue
        positions = rng.permutation(positions)
        n = max(1, int(np.floor(fraction * len(positions))))
        indices["validation"].extend(positions[:n].tolist())
        indices["test"].extend(positions[n : 2 * n].tolist())
        indices["train"].extend(positions[2 * n :].tolist())
    return {
        name: ordered.loc[rows].sort_values(["user_id", "item_id"]).reset_index(drop=True)
        for name, rows in indices.items()
    }


def split_summary(splits: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Check pair conservation/disjointness and report cold targets without dropping them."""
    pairs = {name: set(zip(f.user_id, f.item_id, strict=True)) for name, f in splits.items()}
    if any(
        pairs[a] & pairs[b]
        for a, b in (("train", "validation"), ("train", "test"), ("validation", "test"))
    ):
        raise ValueError("Overlapping split pairs")
    catalog = set(splits["train"].item_id)
    return {
        name: {
            "rows": len(f),
            "users": int(f.user_id.nunique()),
            "artists": int(f.item_id.nunique()),
            "cold_targets": int((~f.item_id.isin(catalog)).sum()) if name != "train" else 0,
        }
        for name, f in splits.items()
    }


def fit_transform(train: pd.DataFrame) -> dict[str, Any]:
    """Fit linear quantiles of log2 counts only on training observations."""
    values = np.log2(1 + train.listening_count.to_numpy(dtype=float))
    thresholds = np.quantile(values, [0.2, 0.4, 0.6, 0.8], method="linear").tolist()
    return {
        "log_base": 2,
        "quantile_levels": [0.2, 0.4, 0.6, 0.8],
        "method": "linear",
        "thresholds": thresholds,
        "rating_rule": "1 + number_of_thresholds_strictly_below_log_count",
    }


def transform_counts(frame: pd.DataFrame, transform: dict[str, Any]) -> pd.DataFrame:
    """Keep raw count columns intact while adding logs and proxy ratings."""
    result = frame.copy()
    values = np.log2(1 + result.listening_count.to_numpy(dtype=float))
    result["log_listening_count"] = values
    result["preference_proxy"] = 1 + np.searchsorted(transform["thresholds"], values, side="left")
    return result
