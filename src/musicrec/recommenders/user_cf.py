"""UserCF: lọc cộng tác dựa trên người dùng (mục 2.2).

Độ tương đồng côsin (2.1) trên toàn véc-tơ điểm của tập huấn luyện, co rút (2.5), và hai
cách tổng hợp điểm: trung bình có trọng số quanh trung bình người dùng (2.2, mô hình chính
đã khóa) hoặc tổng độ tương đồng kiểu top-N (3.6, phân tích bổ sung E7).
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


class UserCFRecommender(Recommender):
    """Giữ L láng giềng có độ tương đồng dương cao nhất, rồi chỉ dùng láng giềng đã nghe nghệ sĩ.

    Côsin dùng cả hàng điểm chưa trừ trung bình, vị trí thiếu coi là 0. Trung bình người
    dùng chỉ tính trên điểm đã quan sát; nghệ sĩ không có láng giềng nào nghe thì lấy trung
    bình của người dùng, người dùng lạ thì lấy trung bình toàn cục. Điểm không bị cắt.
    """

    def __init__(
        self,
        neighbors: int = 40,
        shrinkage: float = 0.0,
        aggregation: str = "mean",
        representation: str | None = None,
    ) -> None:
        """aggregation='mean' (mặc định, mô hình đã khóa ở Chương 4) hoặc 'sum' (top-N, E7).

        neighbors là L (số láng giềng), shrinkage là γ của công thức co rút (2.5).
        'sum' dùng biểu diễn 'binary' (x = 1) hoặc 'log_count' (x = log2(1 + lượt nghe)) cho
        cả côsin lẫn điểm, không chia, và điểm bằng 0 khi không có láng giềng nào nghe.
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
        """Dựng các ma trận phụ cho suy luận từ điểm đã lưu, không học lại láng giềng."""
        self._user_index = {user: index for index, user in enumerate(self._users)}
        self._item_index = {item: index for index, item in enumerate(self._items)}
        counts = np.diff(self._ratings.indptr)
        self._means = np.asarray(self._ratings.sum(axis=1)).ravel() / counts
        self._global_mean = float(self._ratings.data.mean())
        self._binary = self._ratings.copy()
        self._binary.data = np.ones_like(self._binary.data)
        self._centered = self._ratings.copy()
        self._centered.data -= np.repeat(self._means, counts)
        self._centered.eliminate_zeros()

    def fit(self, interactions: Iterable[Interaction]) -> "UserCFRecommender":
        """Học từ tập huấn luyện: ma trận người dùng × nghệ sĩ, côsin, giữ L láng giềng."""
        rows = list(interactions)
        if not rows or (
            self.representation == "proxy" and any(row.proxy_score is None for row in rows)
        ):
            raise ValueError("UserCF requires non-empty train interactions with proxy_score")
        pairs = {(row.user_id, row.item_id) for row in rows}
        if len(pairs) != len(rows):
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
        self._prepare()
        # Côsin (2.1): chuẩn hóa từng hàng về độ dài 1 rồi nhân ma trận.
        norms = np.sqrt(np.asarray(self._ratings.power(2).sum(axis=1)).ravel())
        normalized = csr_matrix(self._ratings.multiply(1 / norms[:, None]))
        similarity = csr_matrix(normalized @ normalized.T)
        similarity.data = np.clip(similarity.data, 0, 1)
        # Co rút (2.5): nhân với n_uv / (n_uv + γ), giảm tin cậy khi hai người nghe chung ít nghệ
        # sĩ.
        if self.shrinkage:
            common = csr_matrix(self._binary @ self._binary.T)
            common.data /= common.data + self.shrinkage
            similarity = csr_matrix(similarity.multiply(common))
        similarity.setdiag(0)
        similarity.eliminate_zeros()
        # Giữ L láng giềng có độ tương đồng dương lớn nhất; hòa thì theo mã người dùng.
        neighbor_rows, neighbor_columns, weights = [], [], []
        for user in range(len(self._users)):
            start, end = similarity.indptr[user : user + 2]
            columns, values = similarity.indices[start:end], similarity.data[start:end]
            order = np.lexsort((columns, -np.round(values, NUMERIC_TIE_DECIMALS)))[: self.neighbors]
            for index in order:
                if values[index] > 0:
                    neighbor_rows.append(user)
                    neighbor_columns.append(int(columns[index]))
                    weights.append(float(values[index]))
        self._weights = csr_matrix(
            (weights, (neighbor_rows, neighbor_columns)),
            shape=(len(self._users), len(self._users)),
            dtype=np.float64,
        )
        return self

    def _score_catalog(self, user_id: str) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
        # Chấm điểm mọi nghệ sĩ cho một người dùng; trả (điểm, có láng giềng hỗ trợ hay không).
        if not self._users:
            raise RuntimeError("Fit UserCF before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if user_id not in self._user_index:
            fill = 0.0 if self.aggregation == "sum" else self._global_mean
            return np.full(len(self._items), fill), np.zeros(len(self._items), dtype=bool)
        user = self._user_index[user_id]
        weights = self._weights.getrow(user)
        if self.aggregation == "sum":
            # Công thức (3.6): s_ui = tổng trên v ∈ N_L(u) của sim(u, v) · x_vi; không ai nghe → 0.
            # Không chia, nên nghệ sĩ được nhiều láng giềng cùng nghe có điểm cao hơn.
            support = csr_matrix(weights @ self._binary).toarray().ravel()
            return csr_matrix(weights @ self._ratings).toarray().ravel(), support > 0
        # Công thức (2.2): r̂_ui = r̄_u + Σ sim(u, v)(r_vi − r̄_v) / Σ |sim(u, v)|.
        # Phép chia làm mất thông tin "bao nhiêu láng giềng cùng nghe" — lý do NDCG thấp.
        numerator = csr_matrix(weights @ self._centered).toarray().ravel()
        denominator = csr_matrix(weights @ self._binary).toarray().ravel()
        supported = denominator > 0
        scores = np.full(len(self._items), self._means[user])
        scores[supported] += numerator[supported] / denominator[supported]
        return scores, supported

    def predict(self, user_id: str, item_id: str) -> float:
        """Dự đoán điểm đại diện 1–5 cho một cặp (dùng cho RMSE), có dự phòng bằng trung bình."""
        # Giới hạn: mỗi lần gọi chấm cả danh mục; cần gom theo lô nếu phải chấm nhiều cặp.
        scores, _ = self._score_catalog(user_id)
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the train catalog")
        return float(scores[self._item_index[item_id]])

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Xếp hạng mọi nghệ sĩ chưa nghe trong danh mục, hòa điểm thì theo thứ tự ánh xạ."""
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
            fallback = "user_cf_no_support"
        elif user_id in self._user_index:
            fallback = "user_cf_user_mean_fallback"
        else:
            fallback = "user_cf_global_mean_cold_start"
        return [
            Recommendation(
                self._items[i], float(scores[i]), "user_cf" if supported[i] else fallback
            )
            for i in ranked
        ]

    def save(self, directory: Path) -> None:
        """Lưu mô hình ra thư mục mới (JSON + NPZ, kèm SHA-256), không ghi đè tệp cũ."""
        if not self._users:
            raise RuntimeError("Fit UserCF before saving")
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "ratings.npz", self._ratings)
        save_npz(directory / "neighbors.npz", self._weights)
        state = {
            "schema_version": 1,
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
    def load(cls, directory: Path) -> "UserCFRecommender":
        """Nạp lại mô hình đã lưu, kiểm tra mã băm, không huấn luyện hay tính lại độ tương đồng."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if (
            state.get("schema_version") != 1
            or state.get("numeric_tie_decimals") != NUMERIC_TIE_DECIMALS
        ):
            raise ValueError("Unsupported UserCF model schema")
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
            or model._weights.shape != (len(model._users), len(model._users))
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
