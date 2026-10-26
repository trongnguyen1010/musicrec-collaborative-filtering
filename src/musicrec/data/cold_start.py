"""Fixed user roles and nested provided histories for the separate M2 protocol."""

import random


def partition_users(users: list[str], seed: int = 42) -> dict[str, list[str]]:
    """Shuffle numeric IDs once; floor 80%/10%, reserve the remaining users unopened."""
    if len(users) < 10 or len(users) != len(set(users)) or any(not u.isdecimal() for u in users):
        raise ValueError("Expected at least ten distinct numeric user IDs")
    shuffled = sorted(users, key=int)
    random.Random(seed).shuffle(shuffled)
    train_end = len(users) * 80 // 100
    # Floor the tuning size separately, as specified in the experiment configuration.
    tuning_end = train_end + len(users) // 10
    return {
        "learning": shuffled[:train_end],
        "tuning": shuffled[train_end:tuning_end],
        "reserved": shuffled[tuning_end:],
    }


def profile_order(user_id: str, items: list[str], seed: int = 42) -> list[str]:
    """Choose nested prefixes using only train artist IDs, independent of targets/counts."""
    if not user_id or len(items) != len(set(items)) or any(not i.isdecimal() for i in items):
        raise ValueError("Expected a user ID and distinct numeric profile artist IDs")
    ordered = sorted(items, key=int)
    random.Random(f"musicrec-m2-profile-v1:{seed}:{user_id}").shuffle(ordered)
    return ordered
