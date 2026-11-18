"""A tiny but complete demo release built from fitted models, shared by service and API tests."""

from pathlib import Path

import pandas as pd
import pytest

from musicrec.data.contracts import Interaction
from musicrec.recommenders.implicit_als import ImplicitALSRecommender
from musicrec.recommenders.m1 import M1Recommender
from musicrec.recommenders.m2 import M2Recommender
from musicrec.recommenders.pure_svd import PureSVDRecommender
from musicrec.serving.release import ReleaseSources, build_release

TRAIN = [
    ("1", "1", 50), ("1", "2", 30), ("1", "3", 5),
    ("2", "1", 40), ("2", "2", 10), ("2", "4", 7),
    ("3", "2", 20), ("3", "3", 15), ("3", "5", 3),
    ("4", "1", 12), ("4", "4", 9), ("4", "6", 2),
    ("5", "5", 8), ("5", "6", 6), ("5", "7", 4),
    ("6", "1", 25), ("6", "7", 11), ("6", "8", 1),
]  # fmt: skip
VALIDATION = [("1", "4", 9), ("2", "3", 2), ("6", "2", 3)]
M2_LEARNING_USERS = {"1", "2", "3", "4"}  # catalog 1-6; artists 7 and 8 stay unknown to M2
TAGS = [("1", "1", "rock"), ("2", "1", "rock"), ("3", "3", "jazz"), ("4", "4", "jazz")]


def interactions(rows: list[tuple[str, str, int]]) -> list[Interaction]:
    return [Interaction(u, i, float(c), 3) for u, i, c in rows]


@pytest.fixture(scope="session")
def demo_release_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("release_sources")
    train = interactions(TRAIN)
    pure_svd = PureSVDRecommender(latent_factors=2, representation="binary").fit(train)
    pure_svd.save(root / "pure_svd")
    m1 = M1Recommender(pure_svd, candidate_size=100, lambda_weight=0.75, beta=0.5).fit(train)
    m1.save(root / "m1")
    ImplicitALSRecommender(latent_factors=2, max_epochs=2).fit(train).save(root / "als")
    learning = [r for r in train if r.user_id in M2_LEARNING_USERS]
    M2Recommender(alpha=0.75, history_threshold=10, min_tag_df=1).fit(learning, tags=TAGS).save(
        root / "m2"
    )
    columns = ["user_id", "item_id", "listening_count"]
    pd.DataFrame(TRAIN, columns=columns).to_parquet(root / "train.parquet")
    pd.DataFrame(VALIDATION, columns=columns).to_parquet(root / "validation.parquet")
    lines = ["id\tname\turl\tpictureURL"] + [
        f"{i}\tArtist {i}\thttp://example.test/{i}\t" for i in range(1, 9)
    ]
    (root / "artists.dat").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sources = ReleaseSources(
        models={
            "pure_svd": root / "pure_svd",
            "m1": root / "m1",
            "implicit_als": root / "als",
            "m2": root / "m2",
        },
        train=root / "train.parquet",
        validation=root / "validation.parquet",
        artists=root / "artists.dat",
        provenance={"models": {"pure_svd": {"latent_factors": 2}}},
    )
    directory = tmp_path_factory.mktemp("releases") / "test-release"
    build_release(sources, directory, "test-release")
    return directory
