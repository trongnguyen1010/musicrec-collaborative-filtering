"""Chia vai trò người dùng và thứ tự hồ sơ lồng nhau cho giao thức Given-N của M2 (mục 3.10)."""

import random


def partition_users(users: list[str], seed: int = 42) -> dict[str, list[str]]:
    """Xáo trộn người dùng một lần rồi chia ba nhóm: học 80%, tinh chỉnh 10%, để dành phần còn lại.

    Nhóm học dùng để học M2, nhóm tinh chỉnh để chọn α, n_min, nhóm để dành chỉ mở khi
    đánh giá cuối. Ba nhóm rời nhau nên người được đánh giá chưa từng góp vào mô hình.
    """
    if len(users) < 10 or len(users) != len(set(users)) or any(not u.isdecimal() for u in users):
        raise ValueError("Expected at least ten distinct numeric user IDs")
    shuffled = sorted(users, key=int)
    random.Random(seed).shuffle(shuffled)
    train_end = len(users) * 80 // 100
    # Làm tròn xuống riêng cỡ nhóm tinh chỉnh, đúng như cấu hình thực nghiệm.
    tuning_end = train_end + len(users) // 10
    return {
        "learning": shuffled[:train_end],
        "tuning": shuffled[train_end:tuning_end],
        "reserved": shuffled[tuning_end:],
    }


def profile_order(user_id: str, items: list[str], seed: int = 42) -> list[str]:
    """Xếp thứ tự ngẫu nhiên cố định các nghệ sĩ huấn luyện của một người.

    Hồ sơ Given-N là N nghệ sĩ đầu của thứ tự này, nên hồ sơ N = 1 nằm trong N = 3, và
    N = 3 nằm trong N = 5 (lồng nhau). Thứ tự không phụ thuộc đích hay lượt nghe.
    """
    if not user_id or len(items) != len(set(items)) or any(not i.isdecimal() for i in items):
        raise ValueError("Expected a user ID and distinct numeric profile artist IDs")
    ordered = sorted(items, key=int)
    random.Random(f"musicrec-m2-profile-v1:{seed}:{user_id}").shuffle(ordered)
    return ordered
