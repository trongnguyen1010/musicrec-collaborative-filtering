"""H1: post-hoc removal of the principal spectral component of a frozen ALS score matrix."""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.implicit_als import ImplicitALSRecommender

GAMMA_MODES = ("global", "deviation")
GATE_K = 10
GATE_QUANTILE = 0.9


@dataclass(frozen=True)
class Spectrum:
    """Singular values and the principal pair of S=PQ^T, never materializing S."""

    singular_values: NDArray[np.float64]
    left: NDArray[np.float64]
    right: NDArray[np.float64]


def score_spectrum(users: NDArray[Any], items: NDArray[Any]) -> Spectrum:
    """Thin QR of both factors, then an SVD of the small R_P R_Q^T matrix.

    The sign of the pair is fixed so that the item vector has a non-negative sum;
    the product sigma * l r^T, which is all H1 uses, does not depend on that sign.
    """
    p, q = np.asarray(users, dtype=np.float64), np.asarray(items, dtype=np.float64)
    if p.ndim != 2 or q.ndim != 2 or p.shape[1] != q.shape[1] or not min(p.shape + q.shape):
        raise ValueError("Expected non-empty factor matrices with the same latent width")
    if not (np.isfinite(p).all() and np.isfinite(q).all()):
        raise ValueError("Factors must be finite")
    q_p, r_p = np.linalg.qr(p, mode="reduced")
    q_q, r_q = np.linalg.qr(q, mode="reduced")
    u_c, sigma, v_c_t = np.linalg.svd(r_p @ r_q.T)
    left, right = q_p @ u_c[:, 0], q_q @ v_c_t[0]
    if right.sum() < 0:
        left, right = -left, -right
    return Spectrum(sigma, left, right)


def deviation_weights(
    history_popularity: NDArray[np.float64], top_popularity: NDArray[np.float64]
) -> tuple[NDArray[np.float64], float | None]:
    """Return min(1, d_u/d_ref) with d_u=max(0, g_u-h_u) and d_ref=q90 of positive d_u.

    Without any positive deviation every weight is zero and d_ref is None.
    """
    h, g = np.asarray(history_popularity, dtype=np.float64), np.asarray(top_popularity)
    if h.shape != g.shape or h.ndim != 1 or not (np.isfinite(h).all() and np.isfinite(g).all()):
        raise ValueError("Expected aligned finite per-user popularity means")
    deviation = np.maximum(0.0, g - h)
    positive = deviation[deviation > 0]
    if not len(positive):
        return np.zeros_like(deviation), None
    reference = float(np.quantile(positive, GATE_QUANTILE, method="linear"))
    return np.minimum(1.0, deviation / reference), reference


class SpectralDebiasRecommender(Recommender):
    """Wrap a loaded ALS checkpoint; fit learns train context and a frozen gate, never ALS.

    Score: s'_ui = s_ui - gamma_u * sigma_1 * l_1(u) * r_1(i). The global mode uses
    gamma_u = gamma_0; the deviation mode scales gamma_0 by the frozen gate weight.
    """

    def __init__(
        self, base: ImplicitALSRecommender, *, gamma0: float = 0.0, mode: str = "global"
    ) -> None:
        if not isfinite(gamma0) or not 0 <= gamma0 <= 1:
            raise ValueError("gamma0 must be finite and in [0, 1]")
        if mode not in GAMMA_MODES:
            raise ValueError(f"mode must be one of {GAMMA_MODES}")
        self.base, self.gamma0, self.mode = base, float(gamma0), mode
        self._fitted = False

    def fit(self, interactions: Iterable[Interaction]) -> "SpectralDebiasRecommender":
        """Use binary train pairs for p(i), h_u and the base Top-10 behind the gate."""
        base = self.base
        rows = list(interactions)
        if not rows or len({(r.user_id, r.item_id) for r in rows}) != len(rows):
            raise ValueError("Expected non-empty unique train user-artist pairs")
        if {r.user_id for r in rows} != set(base._users) or {r.item_id for r in rows} != set(
            base._items
        ):
            raise ValueError("Train pairs must match the checkpoint users and catalog")
        listeners = np.zeros(len(base._items), dtype=np.int64)
        histories: dict[str, set[str]] = {}
        for r in rows:
            listeners[base._item_index[r.item_id]] += 1
            histories.setdefault(r.user_id, set()).add(r.item_id)
        self.listeners = listeners
        self.popularity = np.log1p(listeners) / np.log1p(listeners.max())
        self.spectrum = score_spectrum(base._user_factors, base._item_factors)
        history_mean = np.array(
            [self._mean_popularity(histories[u]) for u in base._users], dtype=np.float64
        )
        top_mean = np.array(
            [
                self._mean_popularity({r.item_id for r in base.recommend(u, GATE_K, histories[u])})
                for u in base._users
            ],
            dtype=np.float64,
        )
        self.weights, self.d_ref = deviation_weights(history_mean, top_mean)
        self.history_popularity, self.top_popularity = history_mean, top_mean
        self._fitted = True
        return self

    def _mean_popularity(self, items: set[str]) -> float:
        if not items:
            raise ValueError("The gate needs a non-empty train history and base Top-10")
        return float(np.mean([self.popularity[self.base._item_index[i]] for i in items]))

    def _require_fit(self) -> None:
        if not self._fitted:
            raise RuntimeError("Fit the spectral context before inference")

    def gamma(self, user_id: str) -> float:
        """Per-user strength; users outside the checkpoint keep the base ranking."""
        self._require_fit()
        if user_id not in self.base._user_index:
            return 0.0
        if self.mode == "global":
            return self.gamma0
        return self.gamma0 * float(self.weights[self.base._user_index[user_id]])

    def _scores(self, user_id: str, gamma: float) -> NDArray[np.float64]:
        u = self.base._user_index[user_id]
        spectrum = self.spectrum
        component = spectrum.singular_values[0] * spectrum.left[u] * spectrum.right
        scores: NDArray[np.float64] = self.base._score_catalog(user_id) - gamma * component
        return scores

    def predict(self, user_id: str, item_id: str) -> float:
        """Return the adjusted latent score, not a probability or rating."""
        gamma = self.gamma(user_id)
        if gamma == 0:
            return self.base.predict(user_id, item_id)
        if item_id not in self.base._item_index:
            raise ValueError("Artist is outside the train catalog")
        return float(self._scores(user_id, gamma)[self.base._item_index[item_id]])

    def recommend(self, user_id: str, k: int, seen_item_ids: set[str]) -> list[Recommendation]:
        """Mask exactly like the base; gamma_u=0 returns the base call unchanged."""
        if type(k) is not int or k <= 0:
            raise ValueError("k must be a positive integer")
        gamma = self.gamma(user_id)
        if gamma == 0:
            return self.base.recommend(user_id, k, seen_item_ids)
        base = self.base
        scores = self._scores(user_id, gamma)
        excluded = {base._item_index[i] for i in seen_item_ids if i in base._item_index}
        excluded.update(base._confidence.getrow(base._user_index[user_id]).indices)
        mask = np.ones(len(base._items), dtype=bool)
        mask[list(excluded)] = False
        candidates = np.flatnonzero(mask)
        ranked = candidates[np.argsort(-np.round(scores[candidates], 12), kind="stable")[:k]]
        reason = f"h1_{self.mode}_gamma0={self.gamma0:g};base=implicit_als"
        return [Recommendation(base._items[i], float(scores[i]), reason) for i in ranked]

    def save(self, directory: Path) -> None:
        """Save the frozen gate and spectrum; the ALS checkpoint stays separately pinned."""
        self._require_fit()
        directory.mkdir(parents=True, exist_ok=False)
        np.savez_compressed(
            directory / "context.npz",
            listeners=self.listeners,
            singular_values=self.spectrum.singular_values,
            left=self.spectrum.left,
            right=self.spectrum.right,
            weights=self.weights,
            history_popularity=self.history_popularity,
            top_popularity=self.top_popularity,
        )
        state = {
            "schema_version": 1,
            "model": "h1_spectral",
            "config": {"gamma0": self.gamma0, "mode": self.mode},
            "gate": {"k": GATE_K, "quantile": GATE_QUANTILE, "d_ref": self.d_ref},
            "users": self.base._users,
            "items": self.base._items,
            "context_sha256": hashlib.sha256((directory / "context.npz").read_bytes()).hexdigest(),
        }
        (directory / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, directory: Path, *, base: ImplicitALSRecommender) -> "SpectralDebiasRecommender":
        """Load the frozen context without recomputing it from the supplied pinned base."""
        state: dict[str, Any] = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        if state.get("schema_version") != 1 or state.get("model") != "h1_spectral":
            raise ValueError("Unsupported H1 schema")
        if (
            hashlib.sha256((directory / "context.npz").read_bytes()).hexdigest()
            != state["context_sha256"]
        ):
            raise ValueError("H1 context checksum mismatch")
        if state["users"] != base._users or state["items"] != base._items:
            raise ValueError("H1 context belongs to a different checkpoint mapping")
        model = cls(base, **state["config"])
        with np.load(directory / "context.npz") as data:
            model.listeners = data["listeners"]
            model.popularity = np.log1p(model.listeners) / np.log1p(model.listeners.max())
            model.spectrum = Spectrum(data["singular_values"], data["left"], data["right"])
            model.weights = data["weights"]
            model.history_popularity = data["history_popularity"]
            model.top_popularity = data["top_popularity"]
        model.d_ref = state["gate"]["d_ref"]
        model._fitted = True
        return model
