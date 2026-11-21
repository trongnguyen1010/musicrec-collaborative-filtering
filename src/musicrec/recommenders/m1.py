"""M1: tái xếp hạng tham lam (Thuật toán 3.1, mục 3.7) trên một tập ứng viên cố định.

Mỗi bước chọn nghệ sĩ cân bằng mức phù hợp, độ trùng lặp với các nghệ sĩ đã chọn và mức
phổ biến, công thức (3.9). Mọi thống kê (số người nghe, độ tương đồng) chỉ học từ tập
huấn luyện. Ý tưởng kế thừa MMR (2.14), thêm thành phần phạt phổ biến.
"""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csc_matrix, load_npz, save_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


@dataclass(frozen=True)
class CandidatePool:
    """Tập ứng viên của mô hình nền và các đặc trưng học từ tập huấn luyện.

    Dùng chung, không đổi, cho mọi cấu hình λ, β trong lưới, nên các biến thể so sánh
    công bằng trên cùng ứng viên.
    """

    recommendations: list[Recommendation]
    relevance: NDArray[np.float64]
    popularity: NDArray[np.float64]
    similarity: NDArray[np.float64]


def rerank_candidates(
    pool: CandidatePool, k: int, lambda_weight: float, beta: float
) -> list[Recommendation]:
    """Chọn tham lam K nghệ sĩ từ tập ứng viên theo công thức (3.9).

    Nhận tập ứng viên, K, λ (trọng số phù hợp so với đa dạng) và β (mức phạt phổ biến);
    trả K nghệ sĩ theo thứ tự được chọn, giữ điểm gốc của mô hình nền. Hòa thì theo
    thứ hạng gốc.
    """
    if type(k) is not int or k <= 0:
        raise ValueError("k must be a positive integer")
    if not isfinite(lambda_weight) or not 0 <= lambda_weight <= 1:
        raise ValueError("lambda_weight must be finite and in [0, 1]")
    if not isfinite(beta) or beta < 0:
        raise ValueError("beta must be finite and non-negative")
    # λ = 1, β = 0: không đa dạng, không phạt, giữ nguyên thứ tự của mô hình nền.
    if lambda_weight == 1 and beta == 0:
        return pool.recommendations[:k]
    n = len(pool.recommendations)
    selected: list[int] = []
    redundancy = np.zeros(n, dtype=np.float64)
    available = np.ones(n, dtype=bool)
    # Phần không đổi qua các bước: λ·s_ui − β·p_i.
    fixed = lambda_weight * pool.relevance - beta * pool.popularity
    for _ in range(min(k, n)):
        # Công thức (3.9): λ·s_ui − (1 − λ)·max_{j∈S} sim(i, j) − β·p_i.
        # redundancy[i] = độ tương đồng lớn nhất của i với các nghệ sĩ đã chọn (tập S).
        utility = np.round(fixed - (1 - lambda_weight) * redundancy, 12)
        utility[~available] = -np.inf
        index = int(np.argmax(utility))
        selected.append(index)
        available[index] = False
        # Sau khi chọn nghệ sĩ mới, cập nhật độ trùng lặp của các ứng viên còn lại.
        redundancy = np.maximum(redundancy, pool.similarity[:, index])
    return [
        Recommendation(
            pool.recommendations[i].item_id,
            pool.recommendations[i].score,
            f"m1_lambda={lambda_weight:g}_beta={beta:g};score=raw_base;"
            f"base={pool.recommendations[i].reason}",
        )
        for i in selected
    ]


class M1Recommender(Recommender):
    """Bọc một mô hình nền đã huấn luyện (PureSVD); fit chỉ học thống kê nhị phân từ tập huấn luyện.

    candidate_size = 100: M1 chỉ tái xếp hạng 100 ứng viên đầu của mô hình nền, vừa đủ rộng
    để có nghệ sĩ ít phổ biến, vừa giữ ứng viên đủ phù hợp và tính nhanh.
    """

    def __init__(
        self,
        base: Recommender,
        *,
        candidate_size: int = 100,
        lambda_weight: float = 1.0,
        beta: float = 0.0,
    ) -> None:
        if type(candidate_size) is not int or candidate_size <= 0:
            raise ValueError("candidate_size must be a positive integer")
        if not isfinite(lambda_weight) or not 0 <= lambda_weight <= 1:
            raise ValueError("lambda_weight must be finite and in [0, 1]")
        if not isfinite(beta) or beta < 0:
            raise ValueError("beta must be finite and non-negative")
        self.base = base
        self.candidate_size, self.lambda_weight, self.beta = candidate_size, lambda_weight, beta
        self._users: list[str] = []
        self._items: list[str] = []
        self._binary: csc_matrix[np.float64]

    def _prepare(self) -> None:
        # Công thức (3.8): p_i = ln(1 + c_i) / ln(1 + max c_j), mức phổ biến chuẩn hóa về [0, 1].
        self._item_index = {item: i for i, item in enumerate(self._items)}
        self._user_index = {user: i for i, user in enumerate(self._users)}
        self._histories = self._binary.tocsr()
        self._listeners = np.asarray(self._binary.sum(axis=0)).ravel()
        self._popularity = np.log1p(self._listeners) / np.log1p(self._listeners.max())

    def fit(self, interactions: Iterable[Interaction]) -> "M1Recommender":
        """Học ma trận nghe nhị phân từ tập huấn luyện (bỏ qua số lượt nghe); từ chối cặp trùng."""
        rows = list(interactions)
        if not rows or len({(r.user_id, r.item_id) for r in rows}) != len(rows):
            raise ValueError("Expected non-empty unique train user-artist pairs")
        self._users = sorted({r.user_id for r in rows})
        self._items = sorted({r.item_id for r in rows})
        users, items = (
            {u: i for i, u in enumerate(self._users)},
            {v: i for i, v in enumerate(self._items)},
        )
        self._binary = csc_matrix(
            (
                np.ones(len(rows)),
                ([users[r.user_id] for r in rows], [items[r.item_id] for r in rows]),
            ),
            shape=(len(users), len(items)),
        )
        self._prepare()
        return self

    def _require_fit(self) -> None:
        # Chặn gọi suy luận trước khi học thống kê.
        if not self._users:
            raise RuntimeError("Fit M1 train statistics before inference")

    def prepare_candidates(self, user_id: str, seen_item_ids: set[str]) -> CandidatePool:
        """Lấy 100 ứng viên từ mô hình nền và tính đặc trưng cho M1.

        Nhận người dùng và nghệ sĩ cần loại; trả CandidatePool gồm mức phù hợp chuẩn hóa
        (3.7), mức phổ biến (3.8) và ma trận côsin giữa các ứng viên.
        """
        self._require_fit()
        if not user_id:
            raise ValueError("user_id must be non-empty")
        seen = set(seen_item_ids)
        if user_id in self._user_index:
            seen.update(self._items[i] for i in self._histories[self._user_index[user_id]].indices)
        candidates = self.base.recommend(user_id, self.candidate_size, seen)
        ids = [r.item_id for r in candidates]
        if len(ids) > self.candidate_size or len(ids) != len(set(ids)):
            raise ValueError("Base returned duplicate or excessive candidates")
        if set(ids) & seen or set(ids) - self._item_index.keys():
            raise ValueError("Base returned seen or out-of-catalog candidates")
        scores = np.array([r.score for r in candidates], dtype=np.float64)
        if not np.isfinite(scores).all():
            raise ValueError("Base scores must be finite")
        if not len(ids):
            return CandidatePool(candidates, scores, scores.copy(), np.empty((0, 0)))
        # Công thức (3.7): chuẩn hóa min–max điểm mô hình nền về [0, 1] để so được với p_i.
        spread = float(np.ptp(scores))
        relevance = (scores - scores.min()) / spread if spread else np.ones(len(scores))
        indices = [self._item_index[item] for item in ids]
        columns = self._binary[:, indices]
        # Côsin giữa hai nghệ sĩ trên véc-tơ người nghe nhị phân: số người nghe chung chia
        # căn tích số người nghe. Chỉ tính cho 100 ứng viên nên ma trận nhỏ.
        similarity = (columns.T @ columns).toarray()
        similarity /= np.sqrt(np.outer(self._listeners[indices], self._listeners[indices]))
        return CandidatePool(candidates, relevance, self._popularity[indices], similarity)

    def predict(self, user_id: str, item_id: str) -> float:
        """Trả điểm của mô hình nền; điểm M1 phụ thuộc các nghệ sĩ đã chọn nên không tính riêng."""
        self._require_fit()
        return self.base.predict(user_id, item_id)

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Trả danh sách theo thứ tự tham lam, kèm điểm gốc (điểm không nhất thiết giảm dần)."""
        if type(k) is not int or not 0 < k <= self.candidate_size:
            raise ValueError("k must be a positive integer no larger than candidate_size")
        return rerank_candidates(
            self.prepare_candidates(user_id, seen_item_ids), k, self.lambda_weight, self.beta
        )

    def save(self, directory: Path) -> None:
        """Lưu thống kê huấn luyện và tham số λ, β; mô hình nền được lưu và kiểm tra riêng."""
        self._require_fit()
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "binary.npz", self._binary)
        state = {
            "schema_version": 1,
            "model": "m1",
            "users": self._users,
            "items": self._items,
            "config": {
                "candidate_size": self.candidate_size,
                "lambda_weight": self.lambda_weight,
                "beta": self.beta,
            },
            "binary_sha256": hashlib.sha256((directory / "binary.npz").read_bytes()).hexdigest(),
        }
        (directory / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, directory: Path, *, base: Recommender) -> "M1Recommender":
        """Nạp lại M1 không huấn luyện; bên gọi đưa vào đúng mô hình nền đã ghim."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if state.get("schema_version") != 1 or state.get("model") != "m1":
            raise ValueError("Unsupported M1 schema")
        if (
            hashlib.sha256((directory / "binary.npz").read_bytes()).hexdigest()
            != state["binary_sha256"]
        ):
            raise ValueError("M1 binary context checksum mismatch")
        model = cls(base, **state["config"])
        model._users, model._items = state["users"], state["items"]
        if any(
            not ids or any(not isinstance(i, str) or not i for i in ids) or ids != sorted(set(ids))
            for ids in [model._users, model._items]
        ):
            raise ValueError("Invalid M1 mappings")
        model._binary = csc_matrix(load_npz(directory / "binary.npz"))
        if (
            model._binary.shape != (len(model._users), len(model._items))
            or not model._binary.has_canonical_format
            or not np.all(model._binary.data == 1)
            or (model._binary.getnnz(axis=0) == 0).any()
            or (model._binary.getnnz(axis=1) == 0).any()
        ):
            raise ValueError("Invalid binary train context")
        model._prepare()
        return model
