"""Create cleaned implicit-feedback interactions and deterministic ID mappings."""

import json
import math
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/interim/validated.parquet")
OUTPUT_DIR = Path("data/processed")


def main() -> None:
    frame = pd.read_parquet(INPUT_FILE)
    interactions = (
        frame.groupby(["user_id", "item_id"], as_index=False)["listening_count"].sum().sort_values(
            ["user_id", "item_id"]
        )
    )
    interactions["log_listening_count"] = interactions["listening_count"].map(
        lambda value: math.log(float(value) + 1.0)
    )
    users = sorted(interactions["user_id"].unique())
    items = sorted(interactions["item_id"].unique())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    interactions.to_parquet(OUTPUT_DIR / "interactions.parquet", index=False)
    (OUTPUT_DIR / "id_mappings.json").write_text(
        json.dumps(
            {
                "user_to_index": {user_id: index for index, user_id in enumerate(users)},
                "item_to_index": {item_id: index for index, item_id in enumerate(items)},
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
