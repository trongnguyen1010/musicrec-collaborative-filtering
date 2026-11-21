"""Bộ đánh giá xếp hạng dùng chung, xếp hạng trên toàn bộ danh mục nghệ sĩ của tập huấn luyện.

Các thước đo ứng với mục 2.5 của báo cáo: Precision@K (2.15), Recall@K (2.16),
NDCG@K (2.17)–(2.19), RMSE (2.20), độ bao phủ (2.21), Gini (2.22), ARP (2.23),
độ mới (2.24) và ILD (2.25).
"""

from collections import Counter
from itertools import combinations
from math import fsum, isfinite, log2, sqrt
from typing import Any


def _top_k(recommended_ids: list[str], k: int) -> list[str]:
    # Chặn k không hợp lệ và danh sách gợi ý trùng nghệ sĩ trước khi cắt K phần tử đầu.
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    if len(recommended_ids) != len(set(recommended_ids)):
        raise ValueError("Duplicate recommendations")
    return recommended_ids[:k]


def precision_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Precision@K, công thức (2.15): tỷ lệ nghệ sĩ đúng trong K gợi ý đầu.

    Nhận danh sách gợi ý, tập nghệ sĩ đích và K; trả về số trong [0, 1].
    """
    return len(set(_top_k(recommended_ids, k)) & relevant_ids) / k


def recall_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Recall@K, công thức (2.16): tỷ lệ nghệ sĩ đích được tìm thấy trong K gợi ý đầu."""
    top_k = _top_k(recommended_ids, k)
    if not relevant_ids:
        return 0.0
    return len(set(top_k) & relevant_ids) / len(relevant_ids)


def ndcg_at_k(recommended_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """NDCG@K nhị phân, công thức (2.17)–(2.19).

    Nhận danh sách gợi ý, tập nghệ sĩ đích và K; trả về DCG / IDCG trong [0, 1].
    Người dùng không có đích bị loại ở bộ đánh giá theo nhóm, không phải ở đây.
    """
    top_k = _top_k(recommended_ids, k)
    # IDCG (2.19): mọi đích xếp ở đầu danh sách, tối đa min(K, |T_u|) vị trí.
    # rank bắt đầu từ 0 nên vị trí j = rank + 1, mẫu số là log2(j + 1) = log2(rank + 2).
    ideal = fsum(1 / log2(rank + 2) for rank in range(min(k, len(relevant_ids))))
    # DCG (2.17): đích ở vị trí càng sâu thì đóng góp càng nhỏ (chia log2 của vị trí).
    dcg = fsum(1 / log2(rank + 2) for rank, item in enumerate(top_k) if item in relevant_ids)
    return dcg / ideal if ideal else 0.0


def rank_candidates(
    scores: dict[str, float], catalog: list[str], seen: set[str], k: int
) -> list[str]:
    """Xếp hạng mọi nghệ sĩ chưa nghe trong danh mục huấn luyện, hòa điểm thì theo thứ tự ánh xạ.

    Bên gọi phải đưa điểm cho mọi ứng viên, không lấy mẫu âm. Điểm của nghệ sĩ đã nghe
    được phép có nhưng bị loại trước khi sắp xếp.
    """
    _top_k(catalog, k)
    if not catalog or set(scores) - set(catalog):
        raise ValueError("Scores must belong to a non-empty train catalog")
    candidates = [item for item in catalog if item not in seen]
    if set(candidates) - scores.keys():
        raise ValueError("Full ranking requires a score for every unseen catalog item")
    if not all(isfinite(score) for score in scores.values()):
        raise ValueError("Scores must be finite")
    # sorted ổn định: hai nghệ sĩ cùng điểm giữ thứ tự trong danh mục, nên kết quả tất định.
    return sorted(candidates, key=lambda item: -scores[item])[:k]


def gini_index(frequencies: list[int]) -> float | None:
    """Hệ số Gini, công thức (2.22), tính trên cả nghệ sĩ không được gợi ý lần nào.

    Gini gần 1 nghĩa là số lần xuất hiện dồn vào ít nghệ sĩ; trả None nếu không có lượt nào.
    """
    if not frequencies or any(type(value) is not int or value < 0 for value in frequencies):
        raise ValueError("Expected a non-empty catalog of non-negative integer counts")
    total, n = sum(frequencies), len(frequencies)
    if not total:
        return None
    weighted = sum(rank * value for rank, value in enumerate(sorted(frequencies), start=1))
    return 2 * weighted / (n * total) - (n + 1) / n


def proxy_rmse(actual: list[float], predicted: list[float]) -> float:
    """RMSE, công thức (2.20), chỉ cho dự đoán trên cùng điểm đại diện 1–5 đã quan sát.

    Chỉ mô hình dự đoán điểm (UserCF, ItemCF, SVD có độ lệch) mới gọi hàm này;
    dự đoán không bị cắt về [1, 5]. RMSE chỉ để tham khảo vì điểm 1–5 do nhóm quy đổi.
    """
    if not actual or len(actual) != len(predicted):
        raise ValueError("Expected non-empty aligned targets and predictions")
    if not all(isfinite(value) and 1 <= value <= 5 for value in actual):
        raise ValueError("Targets must be finite proxy scores in [1, 5]")
    if not all(isfinite(value) for value in predicted):
        raise ValueError("Predictions must be finite")
    return sqrt(fsum((a - b) ** 2 for a, b in zip(actual, predicted, strict=True)) / len(actual))


def evaluate_ranking(
    recommendations: dict[str, list[str]],
    targets: dict[str, set[str]],
    train: dict[str, set[str]],
    *,
    ks: tuple[int, ...] = (5, 10, 20),
    split: str = "validation",
    validation: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    """Chấm các danh sách gợi ý đã có; không huấn luyện, không lấy mẫu, không đọc tệp.

    Mọi người dùng phải có danh sách (có thể rỗng) và tập đích. Trung bình xếp hạng
    tính cả người trả về danh sách rỗng nhưng có đích hợp lệ; các thước đo ngoài độ
    chính xác dùng cùng nhóm người dùng đó. ARP và độ mới gộp theo vị trí được trả về;
    ILD lấy trung bình trên người có ít nhất hai kết quả và báo cáo mẫu số này.
    Tập huấn luyện quyết định danh mục, số người nghe và côsin nhị phân. Khi chấm tập
    kiểm thử, lịch sử xác thực bị loại khỏi ứng viên nhưng không cộng vào thống kê
    huấn luyện (chống rò rỉ).
    """
    if not train or set(recommendations) != set(train) or set(targets) != set(train):
        raise ValueError("Train, targets and recommendation user sets must match and be non-empty")
    if not ks or len(ks) != len(set(ks)):
        raise ValueError("Expected distinct positive cutoffs")
    for k in ks:
        _top_k([], k)
    if split not in {"validation", "test"}:
        raise ValueError("Expected validation or test split")
    if split == "test":
        if validation is None or set(validation) != set(train):
            raise ValueError("Test requires validation histories for every user")
    elif validation is not None:
        raise ValueError("Validation evaluation must only mask train")

    # Danh mục và số người nghe của mỗi nghệ sĩ chỉ học từ tập huấn luyện.
    listeners: dict[str, set[str]] = {}
    for user, history in train.items():
        if not history:
            raise ValueError("Every evaluation user must have a non-empty train history")
        for item in history:
            listeners.setdefault(item, set()).add(user)
    catalog = set(listeners)
    eligible: dict[str, set[str]] = {}
    per_user: dict[str, Any] = {}
    for user in sorted(train):
        # Khi chấm tập kiểm thử, loại cả lịch sử huấn luyện lẫn xác thực khỏi ứng viên.
        seen = train[user] | (validation[user] if validation is not None else set())
        if validation is not None and train[user] & validation[user]:
            raise ValueError("Train and validation histories overlap")
        if targets[user] & seen:
            raise ValueError("Held-out targets overlap observed history")
        items = recommendations[user]
        _top_k(items, max(ks))
        if set(items) - catalog or set(items) & seen:
            raise ValueError("Recommendations contain out-of-catalog or seen items")
        # Đích ngoài danh mục không thể được gợi ý nên được đếm và báo cáo riêng.
        relevant = targets[user] & catalog
        if relevant:
            eligible[user] = relevant
        per_user[user] = {
            "targets_total": len(targets[user]),
            "targets_in_catalog": len(relevant),
            "targets_outside_catalog": len(targets[user] - catalog),
            "candidate_count": len(catalog - seen),
            "eligible": bool(relevant),
            "at_k": {},
        }

    # Mẫu số của P_i trong công thức độ mới (2.24), có làm trơn +1.
    denominator = sum(len(users) + 1 for users in listeners.values())
    by_k = {}
    for k in ks:
        exposure: Counter[str] = Counter()
        precisions, recalls, ndcgs, diversities = [], [], [], []
        short, empty = 0, 0
        for user, relevant in eligible.items():
            items = recommendations[user][:k]
            precision = precision_at_k(items, relevant, k)
            recall = recall_at_k(items, relevant, k)
            ndcg = ndcg_at_k(items, relevant, k)
            # ILD (2.25): khoảng cách 1 - côsin trên véc-tơ người nghe nhị phân của từng cặp.
            distances = [
                1 - len(listeners[a] & listeners[b]) / sqrt(len(listeners[a]) * len(listeners[b]))
                for a, b in combinations(items, 2)
            ]
            ild = fsum(distances) / len(distances) if distances else None
            per_user[user]["at_k"][str(k)] = {
                "precision": precision,
                "recall": recall,
                "ndcg": ndcg,
                "returned": len(items),
                "ild": ild,
            }
            precisions.append(precision)
            recalls.append(recall)
            ndcgs.append(ndcg)
            if ild is not None:
                diversities.append(ild)
            exposure.update(items)
            short += len(items) < k
            empty += not items
        positions, n = exposure.total(), len(eligible)
        by_k[str(k)] = {
            "precision": fsum(precisions) / n if n else None,
            "recall": fsum(recalls) / n if n else None,
            "ndcg": fsum(ndcgs) / n if n else None,
            "catalog_coverage": len(exposure) / len(catalog) if n else None,
            "gini": gini_index([exposure[item] for item in catalog]),
            # ARP (2.23): số người nghe trung bình của các nghệ sĩ được gợi ý.
            "arp": fsum(count * len(listeners[item]) for item, count in exposure.items())
            / positions
            if positions
            else None,
            "novelty": fsum(
                count * -log2((len(listeners[item]) + 1) / denominator)
                for item, count in exposure.items()
            )
            / positions
            if positions
            else None,
            "ild": fsum(diversities) / len(diversities) if diversities else None,
            "ild_users": len(diversities),
            "returned_positions": positions,
            "short_list_users": short,
            "empty_list_users": empty,
            "full_list_rate": (n - short) / n if n else None,
        }
    total_targets = sum(len(items) for items in targets.values())
    outside = sum(len(items - catalog) for items in targets.values())
    return {
        "split": split,
        "users_total": len(train),
        "users_eligible": len(eligible),
        "users_without_catalog_targets": len(train) - len(eligible),
        "targets_total": total_targets,
        "targets_outside_catalog": outside,
        "outside_catalog_target_rate": outside / total_targets if total_targets else None,
        "catalog_size": len(catalog),
        "at_k": by_k,
        "per_user": per_user,
    }
