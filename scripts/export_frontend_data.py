"""Write the static numbers the Next.js frontend shows, straight from saved result files.

No number is typed by hand: every value comes from the official run outputs or the
Chapter 5 backend check, and the JSON lists the files it was read from.

    python scripts/export_frontend_data.py
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPLIT = Path("outputs/chinh_thuc_cloud_20261026/chuong_3/run/split/metrics.json")
TEST = Path("docs/results/chinh_thuc_cloud_20261026/test/metrics.csv")
M2_TEST = Path("docs/results/chinh_thuc_cloud_20261026/m2/test/metrics.csv")
LATENCY = Path("docs/results/chuong_5/latency.json")
CHECK = Path("docs/results/chuong_5/check_release.json")
MANIFEST = Path("docs/results/chuong_5/release_manifest.json")
M1_GRID = Path("docs/results/chinh_thuc_cloud_20261026/m1_metrics.csv")
OUTPUT = Path("frontend/src/data/results.json")
WARM_MODELS = [
    "random",
    "popularity",
    "user_cf",
    "item_cf",
    "svd",
    "pure_svd",
    "m1",
    "implicit_als",
]
COLUMNS = ["precision", "recall", "ndcg", "catalog_coverage", "arp", "novelty", "ild"]


def read_json(path: Path) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    split = read_json(SPLIT)
    test = pd.read_csv(ROOT / TEST)
    warm = test[(test.seed == 42) & (test.k == 10)].set_index("model")
    m2 = pd.read_csv(ROOT / M2_TEST)
    m2 = m2[(m2.k == 10) & m2.method.isin(["popularity", "m2"])]
    latency = read_json(LATENCY)
    check = read_json(CHECK)
    manifest = read_json(MANIFEST)
    grid = pd.read_csv(ROOT / M1_GRID)
    grid = grid[(grid.seed == 42) & (grid.k == 10)]
    data = {
        "sources": [
            p.as_posix() for p in [SPLIT, TEST, M2_TEST, LATENCY, CHECK, MANIFEST, M1_GRID]
        ],
        "release": manifest["release"],
        "dataset": {
            **{key: split["input"][key] for key in ["interactions", "users", "artists"]},
            "train_catalog_artists": split["train_catalog_artists"],
            "train_users": split["splits"]["train"]["users"],
            "splits": {
                name: split["splits"][name]["interactions"]
                for name in ["train", "validation", "test"]
            },
            "test_users_with_targets": split["targets"]["test"]["users_with_valid_targets"],
        },
        "models": manifest["provenance"]["models"],
        "warm_test_k10": [
            {"model": model, **{c: float(warm.loc[model, c]) for c in COLUMNS}}
            for model in WARM_MODELS
        ],
        "m2_test_k10": [
            {
                "n": int(row.n),
                "method": str(row.method),
                "users": int(row.users_eligible),
                **{c: float(getattr(row, c)) for c in COLUMNS},
            }
            for row in m2.itertuples()
        ],
        "m1_validation_grid_k10": [
            {
                "lambda": float(row.lambda_),
                "beta": float(row.beta),
                **{c: float(getattr(row, c)) for c in COLUMNS},
            }
            for row in grid.rename(columns={"lambda": "lambda_"}).itertuples()
        ],
        "check": {
            "passed": check["passed"],
            "warm_users": check["warm"]["users"],
            "warm_rows": check["warm"]["rows_compared"],
            "m2_users": check["m2"]["users"],
            "m2_rows": check["m2"]["rows_compared"],
            "tolerance": check["tolerance"],
        },
        "latency_median_ms": {
            label: round(values["median_ms"], 1) for label, values in latency["latency"].items()
        },
    }
    (ROOT / OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / OUTPUT).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
