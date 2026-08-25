"""Train the current baseline and write a transparent JSON artifact."""

import json
from pathlib import Path

import pandas as pd

from musicrec.data.contracts import Interaction
from musicrec.recommenders.popularity import PopularityRecommender

TRAIN_FILE = Path("data/processed/splits/train.parquet")
OUTPUT_DIR = Path("outputs/train")


def main() -> None:
    frame = pd.read_parquet(TRAIN_FILE)
    interactions = [
        Interaction(str(row.user_id), str(row.item_id), float(row.listening_count))
        for row in frame.itertuples(index=False)
    ]
    model = PopularityRecommender().fit(interactions)
    scores = {item_id: model.predict("offline", item_id) for item_id in frame["item_id"].unique()}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "popularity_scores.json").write_text(
        json.dumps(scores, indent=2, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
