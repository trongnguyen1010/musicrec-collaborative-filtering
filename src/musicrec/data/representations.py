"""Prepare observed interaction values with thresholds fitted on train only."""

from typing import Any

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

REPRESENTATION_CONFIG: dict[str, Any] = {
    "log_base": 2,
    "quantiles": [0.2, 0.4, 0.6, 0.8],
    "quantile_method": "linear",
    "score_boundary": "strictly_greater",
}


def prepare_representations(
    splits: dict[str, pd.DataFrame], mappings: dict[str, dict[str, int]]
) -> tuple[dict[str, pd.DataFrame], dict[str, csr_matrix], dict[str, Any]]:
    """Keep complete split rows and build four sparse train inputs on the existing catalog."""
    if set(splits) != {"train", "validation", "test"}:
        raise ValueError("Expected train, validation and test splits")
    if set(mappings) != {"user_id_to_index", "item_id_to_index"}:
        raise ValueError("Expected train user and item mappings")
    for mapping in mappings.values():
        if not mapping or any(type(index) is not int for index in mapping.values()):
            raise ValueError("Mappings must contain integer indices")
        if sorted(mapping.values()) != list(range(len(mapping))):
            raise ValueError("Mappings must be contiguous and zero-based")
    for column in ["user_id", "item_id"]:
        if set(splits["train"][column]) != set(mappings[f"{column}_to_index"]):
            raise ValueError("Mappings must contain exactly the train IDs")

    tables = {}
    summary: dict[str, Any] = {"splits": {}}
    columns = ["user_id", "item_id", "listening_count", "user_index", "item_index"]
    for name in ["train", "validation", "test"]:
        frame = splits[name].copy()
        if list(frame.columns) != columns or frame.empty:
            raise ValueError("Expected non-empty Step 4 split columns")
        if frame[["user_id", "item_id", "listening_count", "user_index"]].isna().any().any():
            raise ValueError("Only unknown held-out item indices may be missing")
        if (
            not pd.api.types.is_integer_dtype(frame.listening_count)
            or not frame.listening_count.between(1, 2**63 - 1).all()
        ):
            raise ValueError("Counts must be positive int64 integers")
        if frame.duplicated(["user_id", "item_id"]).any():
            raise ValueError("Duplicate user-artist pairs")
        for column in ["user_id", "item_id"]:
            expected = frame[column].map(mappings[f"{column}_to_index"]).astype("Int64")
            actual = frame[column.replace("_id", "_index")]
            if not pd.api.types.is_integer_dtype(actual) or not actual.astype("Int64").equals(
                expected
            ):
                raise ValueError(f"{name}: indices do not match train mappings")
        if frame.user_index.isna().any() or (name == "train" and frame.item_index.isna().any()):
            raise ValueError("Train indices and all user indices must be known")
        frame["log_count"] = np.log2(1.0 + frame.listening_count.to_numpy(dtype=np.float64))
        if name == "train":
            thresholds = np.quantile(
                frame.log_count, REPRESENTATION_CONFIG["quantiles"], method="linear"
            )
        frame["proxy_score"] = (
            1 + (frame.log_count.to_numpy()[:, None] > thresholds).sum(axis=1)
        ).astype("uint8")
        frame["binary"] = np.ones(len(frame), dtype=np.uint8)
        tables[name] = frame
        summary["splits"][name] = {
            "interactions": len(frame),
            "outside_catalog": int(frame.item_index.isna().sum()),
            "score_counts": {
                str(score): int((frame.proxy_score == score).sum()) for score in range(1, 6)
            },
            "log_count_min": float(frame.log_count.min()),
            "log_count_max": float(frame.log_count.max()),
        }
    train = tables["train"]
    shape = (len(mappings["user_id_to_index"]), len(mappings["item_id_to_index"]))
    coordinates = (train.user_index.to_numpy(), train.item_index.to_numpy(dtype=np.int64))
    matrices = {
        name: csr_matrix((train[column].to_numpy(), coordinates), shape=shape)
        for name, column in {
            "raw_count": "listening_count",
            "log_count": "log_count",
            "proxy_score": "proxy_score",
            "binary": "binary",
        }.items()
    }
    summary["transform"] = {
        **REPRESENTATION_CONFIG,
        "fit_scope": "train only",
        "log_transform": "log2(1 + listening_count)",
        "thresholds": thresholds.tolist(),
        "score_rule": "1 + number of thresholds strictly exceeded; ties stay lower",
        "unobserved": "absent entries; not negative feedback or a one-star score",
        "unknown_items": "retain held-out rows with null item_index; no held-out matrices",
        "matrix_shape": list(shape),
        "matrix_nnz": len(train),
    }
    return tables, matrices, summary
