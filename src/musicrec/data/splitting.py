"""Split observed pairs without learning features or dropping held-out artists."""

import math
import random
import re
from typing import Any

import pandas as pd


def split_interactions(
    interactions: pd.DataFrame,
    seed: int = 42,
    validation_fraction: float = 0.1,
    test_fraction: float = 0.1,
) -> tuple[dict[str, pd.DataFrame], dict[str, dict[str, int]], dict[str, Any]]:
    """Return complete splits, train-only mappings and catalog diagnostics."""
    columns = ["user_id", "item_id", "listening_count"]
    if list(interactions.columns) != columns or interactions.empty:
        raise ValueError("Expected non-empty cleaned user_id/item_id/listening_count columns")
    frame = interactions.copy()
    if frame.isna().any().any():
        raise ValueError("Cleaned interactions must not contain missing values")
    for column in ["user_id", "item_id"]:
        if (
            not frame[column]
            .map(
                lambda value: (
                    isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*", value) is not None
                )
            )
            .all()
        ):
            raise ValueError("IDs must be canonical positive integer strings")
    if (
        not pd.api.types.is_integer_dtype(frame.listening_count)
        or not frame.listening_count.between(1, 2**63 - 1).all()
    ):
        raise ValueError("Counts must be positive int64 integers")
    if frame.duplicated(["user_id", "item_id"]).any():
        raise ValueError("Duplicate user-artist pairs must be resolved before splitting")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    fractions = [validation_fraction, test_fraction]
    if (
        any(type(value) not in (int, float) or not 0 < value < 1 for value in fractions)
        or sum(fractions) >= 1
    ):
        raise ValueError("Holdout fractions must be positive and sum to less than one")

    frame = frame.sort_values(["user_id", "item_id"], key=lambda col: col.map(int)).reset_index(
        drop=True
    )
    rng = random.Random(seed)
    indices: dict[str, list[int]] = {name: [] for name in ["train", "validation", "test"]}
    counts = []
    for user_id, group in frame.groupby("user_id", sort=False):
        n = len(group)
        n_val = max(1, math.floor(validation_fraction * n))
        n_test = max(1, math.floor(test_fraction * n))
        if n - n_val - n_test < 1:
            raise ValueError(f"User {user_id} has too few interactions for three non-empty splits")
        order = list(group.index)
        rng.shuffle(order)
        indices["validation"].extend(order[:n_val])
        indices["test"].extend(order[n_val : n_val + n_test])
        indices["train"].extend(order[n_val + n_test :])
        counts.append(
            {"user_id": user_id, "train": n - n_val - n_test, "validation": n_val, "test": n_test}
        )
    tables = {
        name: frame.loc[sorted(rows)].reset_index(drop=True) for name, rows in indices.items()
    }
    mappings = {
        "user_id_to_index": {
            value: i for i, value in enumerate(sorted(set(tables["train"].user_id), key=int))
        },
        "item_id_to_index": {
            value: i for i, value in enumerate(sorted(set(tables["train"].item_id), key=int))
        },
    }
    summary: dict[str, Any] = {
        "input": {
            "interactions": len(frame),
            "users": frame.user_id.nunique(),
            "artists": frame.item_id.nunique(),
            "total_listens": sum(map(int, frame.listening_count)),
        },
        "train_catalog_artists": len(mappings["item_id_to_index"]),
        "splits": {},
        "targets": {},
    }
    per_user = pd.DataFrame(counts).set_index("user_id")
    for name, part in tables.items():
        part["user_index"] = part.user_id.map(mappings["user_id_to_index"]).astype("int64")
        part["item_index"] = part.item_id.map(mappings["item_id_to_index"]).astype("Int64")
        summary["splits"][name] = {
            "interactions": len(part),
            "users": part.user_id.nunique(),
            "artists": part.item_id.nunique(),
            "total_listens": sum(map(int, part.listening_count)),
        }
        if name != "train":
            valid = part.item_index.notna()
            available = part.loc[valid].groupby("user_id").size()
            per_user[f"{name}_in_catalog"] = (
                per_user.index.map(available.to_dict()).fillna(0).astype(int)
            )
            per_user[f"{name}_outside_catalog"] = per_user[name] - per_user[f"{name}_in_catalog"]
            summary["targets"][name] = {
                "total": len(part),
                "in_catalog": int(valid.sum()),
                "outside_catalog": int((~valid).sum()),
                "outside_catalog_fraction": float((~valid).mean()),
                "users_with_valid_targets": int((per_user[f"{name}_in_catalog"] > 0).sum()),
                "users_without_valid_targets": int((per_user[f"{name}_in_catalog"] == 0).sum()),
            }
    tables["user_split_counts"] = per_user.reset_index()
    return tables, mappings, summary
