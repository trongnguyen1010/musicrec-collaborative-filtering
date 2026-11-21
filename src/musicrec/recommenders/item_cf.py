"""ItemCF: lọc cộng tác dựa trên nghệ sĩ (mục 2.2).

Độ tương đồng côsin giữa hai nghệ sĩ (2.3) học từ tập huấn luyện, co rút (2.5), mỗi nghệ sĩ
giữ L láng giềng. Hai cách tổng hợp: trung bình có trọng số (2.4, mô hình chính đã khóa)
hoặc tổng độ tương đồng kiểu top-N (3.5, phân tích bổ sung E7).
"""

import hashlib
import json
from collections.abc import Iterable
from math import isfinite, log2
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, load_npz, save_npz

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender

NUMERIC_TIE_DECIMALS = 12
AGGREGATIONS = ("mean", "sum")
REPRESENTATIONS = {"mean": ("proxy",), "sum": ("binary", "log_count")}


class ItemCFRecommender(Recommender):
    """Lấy giao giữa L láng giềng của nghệ sĩ đích và lịch sử nghe của người dùng: N_L(i) ∩ H_u.

    Côsin dùng cả cột điểm chưa trừ trung bình, vị trí thiếu coi là 0 (chỉ khi tính côsin).
    Dự đoán là trung bình điểm đã quan sát, trọng số theo độ tương đồng; nếu không có láng
    giềng nào trong lịch sử thì dùng trung bình người dùng (người dùng mới: trung bình toàn cục).
    """

    def __init__(
        self,
        neighbors: int = 40,
        shrinkage: float = 0.0,
        aggregation: str = "mean",
        representation: str | None = None,
    ) -> None:
        """aggregation='mean' (mặc định, mô hình đã khóa ở Chương 4) hoặc 'sum' (top-N, E7).

        neighbors là L, shrinkage là γ của công thức co rút (2.5).
        'sum' dùng biểu diễn 'binary' (x = 1) hoặc 'log_count' (x = log2(1 + lượt nghe)) cho
        cả côsin lẫn điểm, không chia, và điểm bằng 0 khi không có láng giềng hỗ trợ.
        """
        if type(neighbors) is not int or neighbors <= 0:
            raise ValueError("neighbors must be a positive integer")
        if not isfinite(shrinkage) or shrinkage < 0:
            raise ValueError("shrinkage must be finite and non-negative")
        if aggregation not in AGGREGATIONS:
            raise ValueError("aggregation must be 'mean' or 'sum'")
        representation = representation or REPRESENTATIONS[aggregation][0]
        if representation not in REPRESENTATIONS[aggregation]:
            raise ValueError(f"representation {representation!r} is not valid for {aggregation}")
        self.neighbors = neighbors
        self.shrinkage = float(shrinkage)
        self.aggregation = aggregation
        self.representation = representation
        self._users: list[str] = []
        self._items: list[str] = []
        self._ratings: csr_matrix[np.float64]
        self._weights: csr_matrix[np.float64]

    def _value(self, row: Interaction) -> float:
        """Giá trị trong ma trận của một tương tác, theo biểu diễn của mô hình."""
        if self.representation == "binary":
            return 1.0
        if self.representation == "log_count":
            return log2(1 + row.listening_count)
        if row.proxy_score is None:
            raise ValueError("proxy representation requires proxy_score")
        return float(row.proxy_score)

    def _extra_state(self) -> dict[str, str]:
        """Chỉ lưu chế độ khác mặc định, để tệp state.json cũ giữ nguyên từng byte."""
        if self.aggregation == "mean":
            return {}
        return {"aggregation": self.aggregation, "representation": self.representation}

    @staticmethod
    def _id_key(value: str) -> tuple[bool, int, str]:
        # Sắp mã theo giá trị số để thứ tự ánh xạ tất định.
        return not value.isdecimal(), int(value) if value.isdecimal() else 0, value

    def _prepare(self) -> None:
        """Dựng ma trận phụ cho suy luận từ dữ liệu đã lưu, không huấn luyện lại."""
        self._user_index = {user: index for index, user in enumerate(self._users)}
        self._item_index = {item: index for index, item in enumerate(self._items)}
        self._means = np.asarray(self._ratings.sum(axis=1)).ravel() / np.diff(self._ratings.indptr)
        self._global_mean = float(self._ratings.data.mean())
        self._binary = self._ratings.copy()
        self._binary.data = np.ones_like(self._binary.data)
        self._incoming = self._weights.T.tocsr()

    def fit(self, interactions: Iterable[Interaction]) -> "ItemCFRecommender":
        """Học láng giềng từng nghệ sĩ: côsin (2.3), co rút (2.5), giữ L láng giềng."""
        rows = list(interactions)
        if not rows or (
            self.representation == "proxy" and any(row.proxy_score is None for row in rows)
        ):
            raise ValueError("ItemCF requires non-empty train interactions with proxy_score")
        if len({(row.user_id, row.item_id) for row in rows}) != len(rows):
            raise ValueError("Duplicate user-artist pair")
        self._users = sorted({row.user_id for row in rows}, key=self._id_key)
        self._items = sorted({row.item_id for row in rows}, key=self._id_key)
        user_index = {user: index for index, user in enumerate(self._users)}
        item_index = {item: index for index, item in enumerate(self._items)}
        self._ratings = csr_matrix(
            (
                np.array([self._value(row) for row in rows], dtype=np.float64),
                (
                    [user_index[row.user_id] for row in rows],
                    [item_index[row.item_id] for row in rows],
                ),
            ),
            shape=(len(self._users), len(self._items)),
            dtype=np.float64,
        )
        self._ratings.sort_indices()
        item_rows = self._ratings.T.tocsr()
        norms = np.sqrt(np.asarray(item_rows.power(2).sum(axis=1)).ravel())
        normalized = csr_matrix(item_rows.multiply(1 / norms[:, None]))
        binary = item_rows.copy()
        binary.data = np.ones_like(binary.data)
        neighbor_rows, neighbor_columns, weights = [], [], []
        # Tính côsin theo khối 256 nghệ sĩ để giới hạn bộ nhớ; không dựng cả ma trận nghệ sĩ × nghệ
        # sĩ.
        for first in range(0, len(self._items), 256):
            last = min(first + 256, len(self._items))
            similarity = csr_matrix(normalized[first:last] @ normalized.T)
            similarity.data = np.clip(similarity.data, 0, 1)
            if self.shrinkage:
                common = csr_matrix(binary[first:last] @ binary.T)
                common.data /= common.data + self.shrinkage
                similarity = csr_matrix(similarity.multiply(common))
            for local, target in enumerate(range(first, last)):
                start, end = similarity.indptr[local : local + 2]
                columns, values = similarity.indices[start:end], similarity.data[start:end]
                valid = (columns != target) & (values > 0)
                columns, values = columns[valid], values[valid]
                order = np.lexsort((columns, -np.round(values, NUMERIC_TIE_DECIMALS)))
                for index in order[: self.neighbors]:
                    neighbor_rows.append(target)
                    neighbor_columns.append(int(columns[index]))
                    weights.append(float(values[index]))
        self._weights = csr_matrix(
            (weights, (neighbor_rows, neighbor_columns)),
            shape=(len(self._items), len(self._items)),
            dtype=np.float64,
        )
        self._prepare()
        return self

    def _score_catalog(self, user_id: str) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
        # Chấm điểm mọi nghệ sĩ cho một người dùng; trả (điểm, có láng giềng hỗ trợ hay không).
        if not self._users:
            raise RuntimeError("Fit ItemCF before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if user_id not in self._user_index:
            fill = 0.0 if self.aggregation == "sum" else self._global_mean
            return np.full(len(self._items), fill), np.zeros(len(self._items), dtype=bool)
        user = self._user_index[user_id]
        numerator = (self._ratings.getrow(user) @ self._incoming).toarray().ravel()
        if self.aggregation == "sum":
            # Công thức (3.5): s_ui = tổng trên j ∈ H_u ∩ N_L(i) của sim(i, j) · x_uj; không hỗ trợ
            # → 0.
            # Không chia, nên nghệ sĩ giống nhiều nghệ sĩ trong lịch sử được điểm cao hơn.
            support = (self._binary.getrow(user) @ self._incoming).toarray().ravel()
            return numerator, support > 0
        # Công thức (2.4): trung bình có trọng số Σ sim(i, j) r_uj / Σ |sim(i, j)|.
        denominator = (self._binary.getrow(user) @ self._incoming).toarray().ravel()
        supported = denominator > 0
        scores = np.full(len(self._items), self._means[user])
        scores[supported] = numerator[supported] / denominator[supported]
        return scores, supported

    def predict(self, user_id: str, item_id: str) -> float:
        """Dự đoán điểm đại diện 1–5 (cho RMSE) bằng trung bình có trọng số."""
        # Giới hạn: mỗi lần gọi chấm cả danh mục; cần gom theo lô nếu phải chấm nhiều cặp.
        scores, _ = self._score_catalog(user_id)
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the train catalog")
        return float(scores[self._item_index[item_id]])

    def score_profile(
        self, interactions: Iterable[Interaction]
    ) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
        """Chấm điểm cho hồ sơ người dùng mới bằng láng giềng đã học, không học thêm hàng mới.

        Dùng trong M2. Trả riêng cờ hỗ trợ: điểm dự phòng bằng trung bình không phải bằng
        chứng cộng tác. Nghệ sĩ lạ trong hồ sơ bị bỏ qua, không thêm vào danh mục.
        """
        if not self._users:
            raise RuntimeError("Fit ItemCF before profile inference")
        if self.aggregation != "mean":
            raise ValueError("Profile scoring is defined for the mean aggregation only")
        rows = list(interactions)
        if (
            any(r.proxy_score is None for r in rows)
            or len({r.item_id for r in rows}) != len(rows)
            or len({r.user_id for r in rows}) > 1
        ):
            raise ValueError("Expected one user's unique profile artists with proxy scores")
        known = [r for r in rows if r.item_id in self._item_index]
        indices = [self._item_index[r.item_id] for r in known]
        profile = csr_matrix(
            (
                np.array([r.proxy_score for r in known], dtype=np.float64),
                ([0] * len(known), indices),
            ),
            shape=(1, len(self._items)),
            dtype=np.float64,
        )
        binary = profile.copy()
        binary.data = np.ones_like(binary.data)
        numerator = (profile @ self._incoming).toarray().ravel()
        denominator = (binary @ self._incoming).toarray().ravel()
        supported = denominator > 0
        fallback = float(profile.data.mean()) if known else self._global_mean
        scores = np.full(len(self._items), fallback)
        scores[supported] = numerator[supported] / denominator[supported]
        return scores, supported

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Xếp hạng nghệ sĩ chưa nghe; điểm làm tròn để so, hòa thì theo thứ tự ánh xạ."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        scores, supported = self._score_catalog(user_id)
        excluded = {self._item_index[item] for item in seen_item_ids if item in self._item_index}
        if user_id in self._user_index:
            excluded.update(self._ratings.getrow(self._user_index[user_id]).indices)
        candidates = np.array([i for i in range(len(self._items)) if i not in excluded], dtype=int)
        ranked = candidates[
            np.argsort(-np.round(scores[candidates], NUMERIC_TIE_DECIMALS), kind="stable")[:k]
        ]
        if self.aggregation == "sum":
            fallback = "item_cf_no_support"
        elif user_id in self._user_index:
            fallback = "item_cf_user_mean_fallback"
        else:
            fallback = "item_cf_global_mean_cold_start"
        return [
            Recommendation(
                self._items[i], float(scores[i]), "item_cf" if supported[i] else fallback
            )
            for i in ranked
        ]

    def save(self, directory: Path) -> None:
        """Lưu dữ liệu huấn luyện và trọng số láng giềng ra thư mục mới (kèm SHA-256)."""
        if not self._users:
            raise RuntimeError("Fit ItemCF before saving")
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "ratings.npz", self._ratings)
        save_npz(directory / "neighbors.npz", self._weights)
        state = {
            "schema_version": 1,
            "model": "item_cf",
            "numeric_tie_decimals": NUMERIC_TIE_DECIMALS,
            "neighbors": self.neighbors,
            "shrinkage": self.shrinkage,
            **self._extra_state(),
            "users": self._users,
            "items": self._items,
            "user_means": self._means.tolist(),
            "global_mean": self._global_mean,
            "sha256": {
                name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in ["ratings.npz", "neighbors.npz"]
            },
        }
        with (directory / "state.json").open("x", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, allow_nan=False)
            handle.write("\n")

    def _valid_values(self, values: NDArray[np.float64]) -> bool:
        """Giá trị lưu phải khớp biểu diễn (đại diện 1–5, nhị phân 1, log ≥ 1)."""
        if self.representation == "proxy":
            return bool(np.isin(values, [1, 2, 3, 4, 5]).all())
        if self.representation == "binary":
            return bool((values == 1).all())
        return bool(np.isfinite(values).all() and (values >= 1).all())

    @classmethod
    def load(cls, directory: Path) -> "ItemCFRecommender":
        """Nạp lại mô hình đã lưu sau khi kiểm tra, không huấn luyện hay tính lại độ tương đồng."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if (
            state.get("schema_version") != 1
            or state.get("model") != "item_cf"
            or state.get("numeric_tie_decimals") != NUMERIC_TIE_DECIMALS
        ):
            raise ValueError("Unsupported ItemCF model schema")
        for name in ["ratings.npz", "neighbors.npz"]:
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != state["sha256"][name]:
                raise ValueError(f"Model checksum mismatch: {name}")
        model = cls(
            state["neighbors"],
            state["shrinkage"],
            state.get("aggregation", "mean"),
            state.get("representation"),
        )
        model._users, model._items = state["users"], state["items"]
        for ids in [model._users, model._items]:
            if (
                not ids
                or any(not isinstance(value, str) or not value for value in ids)
                or len(ids) != len(set(ids))
                or ids != sorted(ids, key=cls._id_key)
            ):
                raise ValueError("Invalid model ID mappings")
        model._ratings = csr_matrix(load_npz(directory / "ratings.npz"), dtype=np.float64)
        model._weights = csr_matrix(load_npz(directory / "neighbors.npz"), dtype=np.float64)
        if (
            model._ratings.shape != (len(model._users), len(model._items))
            or not model._ratings.has_canonical_format
            or not model._valid_values(model._ratings.data)
            or (np.diff(model._ratings.indptr) == 0).any()
            or (np.asarray(model._ratings.getnnz(axis=0)) == 0).any()
            or model._weights.shape != (len(model._items), len(model._items))
            or not model._weights.has_canonical_format
            or not np.isfinite(model._weights.data).all()
            or (model._weights.data <= 0).any()
            or (model._weights.data > 1).any()
            or (model._weights.diagonal() != 0).any()
            or (np.diff(model._weights.indptr) > model.neighbors).any()
        ):
            raise ValueError("Invalid model matrices")
        model._prepare()
        if (
            not np.allclose(model._means, state["user_means"], rtol=0, atol=1e-12)
            or model._global_mean != state["global_mean"]
        ):
            raise ValueError("Invalid stored train means")
        return model
