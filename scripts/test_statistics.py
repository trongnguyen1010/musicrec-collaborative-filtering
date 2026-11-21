"""Mục 4.6: kiểm định theo cặp trên kết quả kiểm thử đã lưu, cho các cặp khai báo trước trong
lock.json.

Chỉ đọc chỉ số theo người dùng mà evaluate_test.py đã lưu; không gợi ý, không đọc dữ liệu.
Mỗi cặp: chênh lệch trung bình chỉ số theo người dùng (A − B) trên nhóm hợp lệ chung, KTC
bootstrap phân vị 95% và 90% theo người dùng (1.000 lần lấy mẫu, hạt giống 42; một ma trận
chỉ số chung cho mọi cặp), p Wilcoxon có dấu hai phía, cỡ hiệu ứng r_rb, và p hiệu chỉnh
Holm trên mọi cặp khai báo trước.
"""

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from musicrec.evaluation.inference import resample_indices
from musicrec.evaluation.paired import paired_comparison

RESAMPLES = 1000
SEED = 42


def per_user(run: Path, model: str, seed: int, k: str, metric: str) -> dict[str, float]:
    """Chỉ số tại K của người dùng hợp lệ, lấy từ một lần đánh giá kiểm thử đã lưu."""
    path = run / model / f"seed_{seed}" / "evaluation.json"
    evaluation: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return {
        user: float(values["at_k"][k][metric])
        for user, values in evaluation["per_user"].items()
        if values["eligible"]
    }


def holm(p_values: list[float]) -> list[float]:
    """Hiệu chỉnh Holm từng bước xuống, công thức (2.29); đơn điệu và chặn trên ở 1.

    Khi so nhiều cặp cùng lúc, xác suất có ít nhất một kết luận sai tăng lên; Holm kiểm soát
    xác suất đó ở mức 0,05 mà ít bảo thủ hơn Bonferroni.
    """
    # Sắp p tăng dần. p nhỏ thứ j (j từ 1) nhân với (m − j + 1): p nhỏ nhất nhân m,
    # p kế tiếp nhân m − 1, ... Lấy max cộng dồn để p đã hiệu chỉnh không giảm, chặn ở 1.
    order = np.argsort(p_values)
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(p_values) - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def main() -> None:
    """Ghi statistics.json cạnh lần chạy kiểm thử."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-run", type=Path, required=True)
    parser.add_argument("--metric", default="ndcg")
    parser.add_argument("--k", default="10")
    args = parser.parse_args()
    lock = json.loads((args.test_run / "lock.json").read_text(encoding="utf-8"))
    indices: np.ndarray | None = None
    rows = []
    for model_a, model_b in lock["comparison_pairs"]:
        a = per_user(args.test_run, model_a, 42, args.k, args.metric)
        b = per_user(args.test_run, model_b, 42, args.k, args.metric)
        if indices is None:
            indices = resample_indices(len(a), RESAMPLES, SEED)
        rows.append({"a": model_a, "b": model_b, **paired_comparison(a, b, indices)})
    for row, adjusted in zip(rows, holm([r["wilcoxon_p"] for r in rows]), strict=True):
        row["holm_p"] = adjusted
    result = {
        "metric": f"{args.metric}@{args.k}",
        "seed": 42,
        "bootstrap": {
            "resamples": RESAMPLES,
            "seed": SEED,
            "unit": "user",
            "indices": "shared_across_pairs",
        },
        "test": "two_sided_wilcoxon_signed_rank_zero_differences_dropped",
        "adjustment": "holm_over_predeclared_pairs",
        "pairs": rows,
    }
    out = args.test_run / f"statistics_{args.metric}_at_{args.k}.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
