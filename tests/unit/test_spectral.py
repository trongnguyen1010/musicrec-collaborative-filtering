"""Dense-SVD, basis-change, identity and frozen-gate checks for the H1 spectral wrapper."""

from pathlib import Path

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from musicrec.data.contracts import Interaction
from musicrec.recommenders.implicit_als import ImplicitALSRecommender
from musicrec.recommenders.spectral import (
    SpectralDebiasRecommender,
    deviation_weights,
    score_spectrum,
)

PAIRS = [("1", "1"), ("1", "2"), ("2", "2"), ("2", "3"), ("3", "1"), ("4", "4")]


def toy_als(users: np.ndarray, items: np.ndarray) -> ImplicitALSRecommender:
    """A loaded-looking checkpoint with fixed factors; it is never fitted."""
    model = ImplicitALSRecommender(latent_factors=users.shape[1])
    model._users = [str(u) for u in range(1, users.shape[0] + 1)]
    model._items = [str(i) for i in range(1, items.shape[0] + 1)]
    model._user_factors = users.astype(np.float32)
    model._item_factors = items.astype(np.float32)
    rows = [int(u) - 1 for u, _ in PAIRS]
    cols = [int(i) - 1 for _, i in PAIRS]
    model._confidence = csr_matrix(
        (np.full(len(PAIRS), 2.0, dtype=np.float32), (rows, cols)),
        shape=(users.shape[0], items.shape[0]),
    )
    model._prepare()
    return model


def factors() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(7)
    return rng.normal(size=(4, 3)), rng.normal(size=(6, 3))


def interactions() -> list[Interaction]:
    # Item 5 and 6 need a train listener so that the train catalog equals the checkpoint.
    return [Interaction(u, i, 1) for u, i in [*PAIRS, ("3", "5"), ("4", "6")]]


def toy_with_full_catalog() -> ImplicitALSRecommender:
    users, items = factors()
    model = toy_als(users, items)
    rows, cols = zip(
        *[(int(r.user_id) - 1, int(r.item_id) - 1) for r in interactions()], strict=True
    )
    model._confidence = csr_matrix(
        (np.full(len(rows), 2.0, dtype=np.float32), (rows, cols)), shape=(4, 6)
    )
    return model


def test_qr_spectrum_matches_dense_svd_of_scores() -> None:
    users, items = factors()
    spectrum = score_spectrum(users, items)
    dense = users @ items.T
    u, s, vt = np.linalg.svd(dense)
    np.testing.assert_allclose(spectrum.singular_values, s[:3], rtol=1e-12)
    np.testing.assert_allclose(
        spectrum.singular_values[0] * np.outer(spectrum.left, spectrum.right),
        s[0] * np.outer(u[:, 0], vt[0]),
        atol=1e-12,
    )
    assert spectrum.right.sum() >= 0


def test_principal_component_is_invariant_to_invertible_basis_change() -> None:
    users, items = factors()
    spectrum = score_spectrum(users, items)
    assert spectrum.singular_values[0] > 1.1 * spectrum.singular_values[1]
    change = np.array([[2.0, 1.0, 0.0], [0.0, 1.0, 3.0], [1.0, 0.0, 1.0]])
    moved = score_spectrum(users @ change, items @ np.linalg.inv(change).T)
    np.testing.assert_allclose(
        moved.singular_values[0] * np.outer(moved.left, moved.right),
        spectrum.singular_values[0] * np.outer(spectrum.left, spectrum.right),
        atol=1e-10,
    )


def test_deviation_weights_hand_quantile_and_no_positive_case() -> None:
    weights, reference = deviation_weights(
        np.array([0.5, 0.5, 0.5, 0.5]), np.array([0.4, 0.6, 0.7, 0.9])
    )
    # Positive deviations 0.1, 0.2, 0.4: linear q90 at position 1.8 is 0.2 + 0.8*0.2.
    assert reference == pytest.approx(0.36)
    np.testing.assert_allclose(weights, [0, 0.1 / 0.36, 0.2 / 0.36, 1])
    weights, reference = deviation_weights(np.array([0.5, 0.7]), np.array([0.5, 0.2]))
    assert reference is None
    np.testing.assert_array_equal(weights, [0, 0])
    with pytest.raises(ValueError):
        deviation_weights(np.array([0.5]), np.array([np.nan]))


def test_zero_gamma_is_the_base_call_and_full_gamma_removes_the_dense_component() -> None:
    base = toy_with_full_catalog()
    model = SpectralDebiasRecommender(base).fit(interactions())
    for user in base._users:
        assert model.recommend(user, 6, {"4"}) == base.recommend(user, 6, {"4"})
    model.gamma0 = 1.0
    users, items = factors()
    dense = (
        users.astype(np.float32).astype(np.float64) @ items.astype(np.float32).astype(np.float64).T
    )
    u, s, vt = np.linalg.svd(dense)
    residual = dense - s[0] * np.outer(u[:, 0], vt[0])
    for row, user in enumerate(base._users):
        seen = {"4"} | {i for i in base._items if base._confidence[row, int(i) - 1]}
        allowed = [j for j in range(6) if str(j + 1) not in seen]
        expected = sorted(allowed, key=lambda j: (-round(residual[row, j], 12), j))
        actual = model.recommend(user, 6, {"4"})
        assert [r.item_id for r in actual] == [str(j + 1) for j in expected]
        np.testing.assert_allclose([r.score for r in actual], residual[row, expected], atol=1e-10)
    assert model.recommend("unknown", 3, set()) == base.recommend("unknown", 3, set())


def test_deviation_gate_is_frozen_and_survives_save_load(tmp_path: Path) -> None:
    base = toy_with_full_catalog()
    model = SpectralDebiasRecommender(base, gamma0=0.5, mode="deviation").fit(interactions())
    gammas = {u: model.gamma(u) for u in base._users}
    assert all(
        g == pytest.approx(0.5 * w) for g, w in zip(gammas.values(), model.weights, strict=True)
    )
    for user, gamma in gammas.items():
        if gamma == 0:
            assert model.recommend(user, 4, set()) == base.recommend(user, 4, set())
    model.save(tmp_path / "h1")
    restored = SpectralDebiasRecommender.load(tmp_path / "h1", base=base)
    for user in base._users:
        assert restored.recommend(user, 4, {"1"}) == model.recommend(user, 4, {"1"})
        assert restored.gamma(user) == model.gamma(user)
    (tmp_path / "h1" / "context.npz").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum"):
        SpectralDebiasRecommender.load(tmp_path / "h1", base=base)


def test_invalid_configuration_and_train_mismatch() -> None:
    base = toy_with_full_catalog()
    for kwargs in [{"gamma0": -0.1}, {"gamma0": 1.5}, {"mode": "mainstream"}]:
        with pytest.raises(ValueError):
            SpectralDebiasRecommender(base, **kwargs)
    with pytest.raises(ValueError, match="checkpoint"):
        SpectralDebiasRecommender(base).fit(interactions()[:-1])
    with pytest.raises(RuntimeError):
        SpectralDebiasRecommender(base).recommend("1", 3, set())
