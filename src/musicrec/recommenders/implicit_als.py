"""Implicit ALS (mục 2.3, thực nghiệm mở rộng): phân rã ma trận cho phản hồi ngầm.

Sở thích nhị phân và độ tin cậy theo (2.11), hàm mục tiêu (2.12), cập nhật luân phiên (2.13).
Vòng lặp tốt nhất được chọn trên tập xác thực.
"""

import hashlib
import json
from collections.abc import Callable, Iterable
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, load_npz, save_npz
from threadpoolctl import threadpool_limits

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender


class _StopTraining(Exception):
    """Ngoại lệ dừng huấn luyện khi NDCG@10 xác thực không cải thiện sau số vòng đã định."""


class ImplicitALSRecommender(Recommender):
    """Học sở thích p_ui với độ tin cậy c_ui = 1 + a·ln(1 + lượt nghe), công thức (2.11).

    Khác SVD có độ lệch, ALS dùng cả cặp chưa nghe (c = 1, p = 0), nên hợp với phản hồi ngầm.
    Mỗi bước luân phiên giải bằng gradient liên hợp ba bước, nhân tố dạng float32; khi xếp
    hạng, điểm là tích vô hướng float64 của hai nhân tố, không cắt, không độ lệch.
    """

    def __init__(
        self,
        latent_factors: int = 32,
        regularization: float = 0.1,
        confidence_scale: float = 1.0,
        max_epochs: int = 50,
        patience: int = 5,
        seed: int = 42,
    ) -> None:
        for name, value in [
            ("latent_factors", latent_factors),
            ("max_epochs", max_epochs),
            ("patience", patience),
        ]:
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if type(seed) is not int or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        for name, scale in [
            ("regularization", regularization),
            ("confidence_scale", confidence_scale),
        ]:
            if not isfinite(scale) or scale <= 0:
                raise ValueError(f"{name} must be finite and positive")
        self.latent_factors, self.max_epochs, self.patience = latent_factors, max_epochs, patience
        self.regularization, self.confidence_scale = float(regularization), float(confidence_scale)
        self.seed = seed
        self._users: list[str] = []
        self._items: list[str] = []
        self._confidence: csr_matrix[np.float32]
        self._user_factors: NDArray[np.float32]
        self._item_factors: NDArray[np.float32]
        self.learning_curve: list[dict[str, Any]] = []
        self.best_epoch = 0
        self.stop_reason = "not_fitted"

    @staticmethod
    def _id_key(value: str) -> tuple[bool, int, str]:
        return not value.isdecimal(), int(value) if value.isdecimal() else 0, value

    def _prepare(self) -> None:
        self._user_index = {u: i for i, u in enumerate(self._users)}
        self._item_index = {item: i for i, item in enumerate(self._items)}
        self._score_items = self._item_factors.astype(np.float64)

    def fit(
        self,
        interactions: Iterable[Interaction],
        *,
        validation_score: Callable[["ImplicitALSRecommender"], float] | None = None,
    ) -> "ImplicitALSRecommender":
        """Huấn luyện một lần; sau mỗi vòng chỉ đo tập xác thực để chọn vòng tốt nhất."""
        from implicit.cpu.als import AlternatingLeastSquares

        rows = list(interactions)
        if not rows or len({(r.user_id, r.item_id) for r in rows}) != len(rows):
            raise ValueError("Expected non-empty interactions with unique user-artist pairs")
        counts = np.array([r.listening_count for r in rows], dtype=np.float64)
        if not np.isfinite(counts).all() or (counts <= 0).any():
            raise ValueError("Expected finite positive raw listening counts")
        self._users = sorted({r.user_id for r in rows}, key=self._id_key)
        self._items = sorted({r.item_id for r in rows}, key=self._id_key)
        users, items = (
            {u: i for i, u in enumerate(self._users)},
            {v: i for i, v in enumerate(self._items)},
        )
        # Độ tin cậy (2.11): c_ui = 1 + a·ln(1 + lượt nghe); nghe càng nhiều càng tin là thích.
        values = (1.0 + self.confidence_scale * np.log1p(counts)).astype(np.float32)
        if not np.isfinite(values).all() or (values <= 1).any():
            raise ValueError("Confidence must be finite and greater than one in float32")
        self._confidence = csr_matrix(
            (values, ([users[r.user_id] for r in rows], [items[r.item_id] for r in rows])),
            shape=(len(users), len(items)),
        )
        self._confidence.sort_indices()
        with threadpool_limits(limits=1, user_api="blas"):
            backend = AlternatingLeastSquares(
                factors=self.latent_factors,
                regularization=self.regularization,
                alpha=1.0,
                dtype=np.float32,
                use_native=True,
                use_cg=True,
                iterations=self.max_epochs,
                calculate_training_loss=True,
                num_threads=1,
                random_state=self.seed,
            )
            backend.cg_steps = 3
            self.learning_curve, self.best_epoch = [], 0
            self.stop_reason = "max_epochs" if validation_score else "max_epochs_no_validation"
            best_score, stale, checkpoint = -float("inf"), 0, None

            def completed(epoch: int, elapsed: float, loss: float) -> None:
                nonlocal best_score, stale, checkpoint
                self._user_factors = np.asarray(backend.user_factors, dtype=np.float32)
                self._item_factors = np.asarray(backend.item_factors, dtype=np.float32)
                if not all(
                    np.isfinite(a).all() for a in [self._user_factors, self._item_factors]
                ) or not isfinite(loss):
                    raise FloatingPointError("Non-finite ALS factors or training loss")
                self._prepare()
                score = float(validation_score(self)) if validation_score else None
                if score is not None and (not isfinite(score) or not 0 <= score <= 1):
                    raise ValueError("Validation NDCG@10 must be finite and in [0, 1]")
                improved = score is None or score > best_score
                if improved:
                    self.best_epoch, stale = epoch + 1, 0
                    if score is not None:
                        best_score = score
                        checkpoint = (self._user_factors.copy(), self._item_factors.copy())
                else:
                    stale += 1
                self.learning_curve.append(
                    {
                        "epoch": epoch + 1,
                        "normalized_training_loss": float(loss),
                        "validation_ndcg_at_10": score,
                        "improved": improved,
                    }
                )
                if validation_score and stale >= self.patience:
                    self.stop_reason = "patience"
                    raise _StopTraining

            try:
                backend.fit(self._confidence, show_progress=False, callback=completed)
            except _StopTraining:
                pass
            if checkpoint is not None:
                self._user_factors, self._item_factors = checkpoint
            self._prepare()
        return self

    def _score_catalog(self, user_id: str) -> NDArray[np.float64]:
        if not self._users:
            raise RuntimeError("Fit implicit ALS before inference")
        if not user_id:
            raise ValueError("user_id must be non-empty")
        if user_id not in self._user_index:
            return np.zeros(len(self._items), dtype=np.float64)
        return np.asarray(
            self._score_items @ self._user_factors[self._user_index[user_id]].astype(np.float64)
        )

    def predict(self, user_id: str, item_id: str) -> float:
        """Trả mức liên kết x_uᵀ y_i, không phải điểm dự đoán hay xác suất."""
        if not self._users:
            raise RuntimeError("Fit implicit ALS before inference")
        if item_id not in self._item_index:
            raise ValueError("Artist is outside the train catalog")
        return float(self._score_catalog(user_id)[self._item_index[item_id]])

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Loại mọi nghệ sĩ đã biết trong lịch sử, xếp hạng toàn bộ nghệ sĩ chưa nghe."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        scores = self._score_catalog(user_id)
        excluded = {self._item_index[i] for i in seen_item_ids if i in self._item_index}
        if user_id in self._user_index:
            excluded.update(self._confidence.getrow(self._user_index[user_id]).indices)
        candidates = np.array([i for i in range(len(self._items)) if i not in excluded], dtype=int)
        ranked = candidates[np.argsort(-np.round(scores[candidates], 12), kind="stable")[:k]]
        reason = (
            "implicit_als"
            if user_id in self._user_index
            else "implicit_als_zero_profile_cold_start"
        )
        return [Recommendation(self._items[i], float(scores[i]), reason) for i in ranked]

    def save(self, directory: Path) -> None:
        """Lưu ma trận độ tin cậy, nhân tố và nguồn gốc ra thư mục mới, không ghi đè."""
        if not self._users:
            raise RuntimeError("Fit implicit ALS before saving")
        directory.mkdir(parents=True, exist_ok=False)
        save_npz(directory / "confidence.npz", self._confidence)
        np.savez_compressed(
            directory / "factors.npz", users=self._user_factors, items=self._item_factors
        )
        state = {
            "schema_version": 1,
            "model": "implicit_als",
            "numeric_tie_decimals": 12,
            "config": {
                name: getattr(self, name)
                for name in [
                    "latent_factors",
                    "regularization",
                    "confidence_scale",
                    "max_epochs",
                    "patience",
                    "seed",
                ]
            },
            "users": self._users,
            "items": self._items,
            "best_epoch": self.best_epoch,
            "stop_reason": self.stop_reason,
            "learning_curve": self.learning_curve,
            "sha256": {
                name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                for name in ["confidence.npz", "factors.npz"]
            },
        }
        with (directory / "state.json").open("x", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, allow_nan=False)
            handle.write("\n")

    @classmethod
    def load(cls, directory: Path) -> "ImplicitALSRecommender":
        """Nạp mô hình đã lưu; không huấn luyện lại, không gộp lịch sử xác thực vào."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if (
            state.get("schema_version") != 1
            or state.get("model") != "implicit_als"
            or state.get("numeric_tie_decimals") != 12
        ):
            raise ValueError("Unsupported ALS model schema")
        for name in ["confidence.npz", "factors.npz"]:
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != state["sha256"][name]:
                raise ValueError(f"Model checksum mismatch: {name}")
        model = cls(**state["config"])
        model._users, model._items = state["users"], state["items"]
        for ids in [model._users, model._items]:
            if (
                not ids
                or any(not isinstance(v, str) or not v for v in ids)
                or len(ids) != len(set(ids))
                or ids != sorted(ids, key=cls._id_key)
            ):
                raise ValueError("Invalid model ID mappings")
        model._confidence = csr_matrix(load_npz(directory / "confidence.npz"))
        with np.load(directory / "factors.npz", allow_pickle=False) as arrays:
            model._user_factors, model._item_factors = arrays["users"], arrays["items"]
        for array, shape in [
            (model._user_factors, (len(model._users), model.latent_factors)),
            (model._item_factors, (len(model._items), model.latent_factors)),
        ]:
            if array.shape != shape or array.dtype != np.float32 or not np.isfinite(array).all():
                raise ValueError("Invalid ALS factor arrays")
        if (
            model._confidence.shape != (len(model._users), len(model._items))
            or model._confidence.dtype != np.float32
            or not model._confidence.has_canonical_format
            or not np.isfinite(model._confidence.data).all()
            or (model._confidence.data <= 1).any()
            or (np.diff(model._confidence.indptr) == 0).any()
            or (model._confidence.getnnz(axis=0) == 0).any()
        ):
            raise ValueError("Invalid ALS confidence matrix")
        model.best_epoch, model.learning_curve, model.stop_reason = (
            state["best_epoch"],
            state["learning_curve"],
            state["stop_reason"],
        )
        if (
            not model.learning_curve
            or not 1 <= model.best_epoch <= len(model.learning_curve)
            or len(model.learning_curve) > model.max_epochs
        ):
            raise ValueError("Invalid ALS checkpoint history")
        model._prepare()
        return model
