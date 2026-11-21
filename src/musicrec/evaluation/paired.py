"""So sánh theo cặp trên từng người dùng, dùng chung một ma trận chỉ số bootstrap.

Mọi cặp mô hình của cùng một nhóm người dùng được lấy mẫu lại bằng cùng ma trận chỉ số
(số lần lấy mẫu × số người dùng) từ musicrec.evaluation.inference.resample_indices, nên
mọi khoảng tin cậy trong một bảng đến từ cùng các mẫu bootstrap. Với mỗi cặp, mô-đun trả:
chênh lệch trung bình (A − B), khoảng tin cậy phân vị 95% và 90% (2.30), giá trị p hai phía
của kiểm định Wilcoxon có dấu (bỏ chênh lệch bằng 0) (2.26)–(2.27) và cỡ hiệu ứng
r_rb = (W+ − W−) / (W+ + W−) (2.28) trên cùng các chênh lệch khác 0. Hai mô hình tương đương
theo TOST mức 0,05 khi khoảng tin cậy 90% nằm hẳn trong (−delta, delta), công thức (2.31).
"""

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.stats import rankdata, wilcoxon


def aligned(a: Mapping[str, float], b: Mapping[str, float]) -> tuple[list[str], NDArray[Any]]:
    """Sắp người dùng theo mã số và trả chênh lệch A − B của từng người theo thứ tự đó.

    Hai mô hình phải được chấm trên đúng cùng nhóm người dùng thì mới so theo cặp được.
    """
    if a.keys() != b.keys():
        raise ValueError("Paired methods must share the eligible cohort")
    users = sorted(a, key=int)
    return users, np.array([a[u] - b[u] for u in users], dtype=np.float64)


def signed_rank_sums(diff: Sequence[float] | NDArray[Any]) -> tuple[float, float]:
    """W+ và W− của kiểm định Wilcoxon có dấu, công thức (2.26), sau khi bỏ chênh lệch 0.

    Các |d| bằng nhau nhận hạng trung bình, giống scipy với zero_method='wilcox'.
    """
    values = np.asarray(diff, dtype=np.float64)
    nonzero = values[values != 0]
    if not len(nonzero):
        return 0.0, 0.0
    # Xếp hạng |d|, rồi cộng hạng của chênh lệch dương vào W+ và chênh lệch âm vào W−.
    ranks = rankdata(np.abs(nonzero), method="average")
    return float(ranks[nonzero > 0].sum()), float(ranks[nonzero < 0].sum())


def rank_biserial(diff: Sequence[float] | NDArray[Any]) -> float | None:
    """Cỡ hiệu ứng r_rb = (W+ − W−) / (W+ + W−), công thức (2.28); None nếu mọi d = 0.

    r_rb trong [−1, 1]: dương là A tốt hơn B ở đa số người dùng. p chỉ cho biết có khác
    hay không; r_rb cho biết khác nhiều hay ít.
    """
    plus, minus = signed_rank_sums(diff)
    total = plus + minus
    return None if total == 0 else (plus - minus) / total


def percentile_interval(means: NDArray[Any], level: float) -> tuple[float, float]:
    """Khoảng tin cậy phân vị hai phía của các trung bình bootstrap, công thức (2.30)."""
    if not 0 < level < 1:
        raise ValueError("level must lie in (0, 1)")
    tail = 100 * (1 - level) / 2
    return float(np.percentile(means, tail)), float(np.percentile(means, 100 - tail))


def bootstrap_means(values: NDArray[Any], indices: NDArray[np.int64]) -> NDArray[Any]:
    """Trung bình của từng mẫu bootstrap, lấy theo ma trận chỉ số dùng chung."""
    if indices.ndim != 2 or indices.shape[1] != len(values):
        raise ValueError("Resample indices must match the cohort size")
    means: NDArray[Any] = np.asarray(values[indices].mean(axis=1), dtype=np.float64)
    return means


def mean_interval(
    values: Sequence[float] | NDArray[Any], indices: NDArray[np.int64]
) -> dict[str, Any]:
    """Trung bình chỉ số theo người dùng của một mô hình, kèm khoảng tin cậy 95% và 90%."""
    array = np.asarray(values, dtype=np.float64)
    means = bootstrap_means(array, indices)
    low95, high95 = percentile_interval(means, 0.95)
    low90, high90 = percentile_interval(means, 0.90)
    return {
        "mean": float(array.mean()),
        "ci95_low": low95,
        "ci95_high": high95,
        "ci90_low": low90,
        "ci90_high": high90,
    }


def paired_comparison(
    a: Mapping[str, float], b: Mapping[str, float], indices: NDArray[np.int64]
) -> dict[str, Any]:
    """So sánh hai mô hình A và B theo cặp trên từng người dùng.

    Nhận NDCG@10 (hoặc chỉ số khác) của từng người cho A và B cùng ma trận bootstrap;
    trả chênh lệch trung bình, khoảng tin cậy 95%/90%, p Wilcoxon và r_rb. Giá trị p
    ở đây chưa hiệu chỉnh; hiệu chỉnh Holm làm ở scripts/test_statistics.py.
    """
    users, diff = aligned(a, b)
    means = bootstrap_means(diff, indices)
    low95, high95 = percentile_interval(means, 0.95)
    low90, high90 = percentile_interval(means, 0.90)
    nonzero = int(np.count_nonzero(diff))
    plus, minus = signed_rank_sums(diff)
    return {
        "users": len(users),
        "nonzero_differences": nonzero,
        "positive_differences": int((diff > 0).sum()),
        "negative_differences": int((diff < 0).sum()),
        "mean_a": float(np.mean([a[u] for u in users])),
        "mean_b": float(np.mean([b[u] for u in users])),
        "mean_difference": float(diff.mean()),
        "ci95_low": low95,
        "ci95_high": high95,
        "ci90_low": low90,
        "ci90_high": high90,
        "wilcoxon_p": float(wilcoxon(diff, zero_method="wilcox").pvalue) if nonzero else 1.0,
        "w_plus": plus,
        "w_minus": minus,
        "rank_biserial": rank_biserial(diff),
    }


def equivalence_test(ci90_low: float, ci90_high: float, delta: float) -> dict[str, Any]:
    """Kết luận TOST theo quy tắc khoảng, công thức (2.31).

    Tương đương khi −delta < cận dưới KTC 90% và cận trên < delta. Dùng KTC 90% vì TOST
    gồm hai kiểm định một phía, mỗi phía mức 0,05. Với M1, delta = 5% NDCG@10 của
    PureSVD (công thức (4.1)). "Không có ý nghĩa thống kê" chưa đủ để nói hai mô hình
    ngang nhau, nên cần kiểm định tương đương này.
    """
    if not delta > 0:
        raise ValueError("delta must be positive")
    if ci90_low > ci90_high:
        raise ValueError("Interval bounds are reversed")
    return {
        "delta": float(delta),
        "margin": [-float(delta), float(delta)],
        "ci90": [float(ci90_low), float(ci90_high)],
        "lower_test_rejects": bool(ci90_low > -delta),
        "upper_test_rejects": bool(ci90_high < delta),
        "equivalent": bool(-delta < ci90_low and ci90_high < delta),
        "rule": "tost_alpha_0.05_via_90pct_bootstrap_interval_inside_open_margin",
    }
