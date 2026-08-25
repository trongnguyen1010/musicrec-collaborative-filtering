"""Produce a deterministic train/validation/test split for eligible users."""

from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/processed/interactions.parquet")
OUTPUT_DIR = Path("data/processed/splits")


def main() -> None:
    interactions = pd.read_parquet(INPUT_FILE)
    train, validation, test = [], [], []
    for _, group in interactions.groupby("user_id", sort=True):
        group = group.sample(frac=1, random_state=42)
        if len(group) < 3:
            continue
        test.append(group.iloc[0])
        validation.append(group.iloc[1])
        train.extend(group.iloc[2:].to_dict("records"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(train).to_parquet(OUTPUT_DIR / "train.parquet", index=False)
    pd.DataFrame(validation).to_parquet(OUTPUT_DIR / "validation.parquet", index=False)
    pd.DataFrame(test).to_parquet(OUTPUT_DIR / "test.parquet", index=False)


if __name__ == "__main__":
    main()
