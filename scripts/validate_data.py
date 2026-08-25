"""Validate the HetRec `user_artists.dat` source file into a stable schema."""

from pathlib import Path

import pandas as pd

RAW_FILE = Path("data/raw/user_artists.dat")
OUTPUT_FILE = Path("data/interim/validated.parquet")
REQUIRED_COLUMNS = {"userID", "artistID", "weight"}


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Expected HetRec source file at {RAW_FILE}")
    frame = pd.read_csv(RAW_FILE, sep="\t")
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing source columns: {sorted(missing)}")
    validated = frame.loc[:, ["userID", "artistID", "weight"]].rename(
        columns={"userID": "user_id", "artistID": "item_id", "weight": "listening_count"}
    )
    validated = validated.dropna().astype({"user_id": str, "item_id": str, "listening_count": float})
    if (validated["listening_count"] <= 0).any():
        raise ValueError("listening_count must be positive")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    validated.to_parquet(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
