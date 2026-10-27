"""Route demo requests to the pinned models; shared by FastAPI, Streamlit and offline checks.

Branches follow the approved demo plan (docs/KE_HOACH_PROTOTYPE_DEMO.md, P1-P5):
an existing train user gets PureSVD, M1 over that PureSVD, or ALS, with train and
validation masked as in the official test; a new user with 1-5 chosen artists gets M2;
an empty profile falls back to Popularity.
"""

import threading
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from musicrec.data.contracts import Interaction
from musicrec.recommenders.base import Recommendation, Recommender
from musicrec.recommenders.m1 import rerank_candidates
from musicrec.serving.release import Release

ExistingModel = Literal["pure_svd", "m1", "implicit_als"]
Branch = Literal["existing_user", "new_user", "popularity"]
MAX_PROFILE_ARTISTS = 5
# The validation grid of configs/models/m1_pure_svd.yaml; only these points have metrics.
M1_LAMBDAS = (0.5, 0.75, 1.0)
M1_BETAS = (0.0, 0.1, 0.25, 0.5)
_PROFILE_ID = "demo_new_user"


class UnknownUserError(LookupError):
    """The requested user is not one of the train users the checkpoints were fitted on."""


@dataclass(frozen=True, slots=True)
class ArtistInfo:
    """Display data for one artist; listeners counts distinct train users (as ARP does)."""

    item_id: str
    name: str
    url: str
    picture_url: str
    listeners: int


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Serialization-independent output of one routed request."""

    release: str
    branch: Branch
    model: str
    fallback_used: bool
    fallback_reason: str | None
    recommendations: list[Recommendation]
    ignored_item_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ProfileEntry:
    """One artist chosen by a new user; listening_count is optional in the demo."""

    item_id: str
    listening_count: float | None = None


class DemoService:
    """Keeps model routing and masking out of HTTP handlers."""

    def __init__(self, release: Release) -> None:
        self.release = release
        self._existing: dict[str, Recommender] = {
            "pure_svd": release.pure_svd,
            "m1": release.m1,
            "implicit_als": release.implicit_als,
        }
        known = (
            release.train[["user_id", "item_id"]],
            release.validation[["user_id", "item_id"]],
        )
        self._masks: dict[str, set[str]] = {}
        for frame in known:
            for user, group in frame.groupby("user_id"):
                self._masks.setdefault(str(user), set()).update(group.item_id)
        self._train_users = set(release.train.user_id)
        self._listeners = release.train.groupby("item_id").user_id.nunique().to_dict()
        self._m2_catalog = set(release.m2.catalog)
        # Unknown counts get the middle proxy level: log2(1+c) halfway between the
        # 40% and 60% train quantiles that M2 uses as proxy thresholds.
        low, high = release.m2.thresholds[1], release.m2.thresholds[2]
        self.default_listening_count = float(2 ** ((low + high) / 2) - 1)
        self._m2_lock = threading.Lock()

    @property
    def users(self) -> list[str]:
        """Train users in numeric order."""
        return sorted(self._train_users, key=lambda u: (not u.isdecimal(), len(u), u))

    def masked_items(self, user_id: str) -> set[str]:
        """Train plus validation artists of a user, the official test mask."""
        return set(self._masks.get(user_id, set()))

    def artist(self, item_id: str) -> ArtistInfo:
        """Name and train popularity of one artist; unnamed ids keep the id as name."""
        row = self.release.artists.get(item_id, {})
        return ArtistInfo(
            item_id,
            row.get("name", item_id),
            row.get("url", ""),
            row.get("picture_url", ""),
            int(self._listeners.get(item_id, 0)),
        )

    def search_artists(self, query: str, limit: int) -> list[ArtistInfo]:
        """Case-insensitive substring search over the M2 catalog, most listened first."""
        needle = query.casefold().strip()
        matches = [
            self.artist(item)
            for item in self._m2_catalog
            if needle in self.release.artists.get(item, {}).get("name", item).casefold()
        ]
        matches.sort(key=lambda a: (-a.listeners, a.name.casefold(), a.item_id))
        return matches[:limit]

    def recommend_existing(
        self,
        user_id: str,
        k: int,
        model: ExistingModel,
        m1_params: tuple[float, float] | None = None,
    ) -> RecommendationResult:
        """Rank the unseen train catalog for a known user with one pinned model.

        m1_params=(lambda, beta) re-ranks the same PureSVD top-100 pool with another point
        of the M1 validation grid; None keeps the selected (pinned) configuration.
        """
        if user_id not in self._train_users:
            raise UnknownUserError(user_id)
        if m1_params is not None:
            lambda_weight, beta = m1_params
            if model != "m1" or lambda_weight not in M1_LAMBDAS or beta not in M1_BETAS:
                raise ValueError("m1 lambda/beta must be a point of the M1 validation grid")
            m1 = self.release.m1
            if k > m1.candidate_size:
                raise ValueError("k must not exceed the M1 candidate size")
            pool = m1.prepare_candidates(user_id, self.masked_items(user_id))
            recommendations = rerank_candidates(pool, k, lambda_weight, beta)
        else:
            recommendations = self._existing[model].recommend(
                user_id, k, self.masked_items(user_id)
            )
        return RecommendationResult(
            self.release.version, "existing_user", model, False, None, recommendations
        )

    def recommend_popular(self, k: int, reason: str, seen: set[str]) -> RecommendationResult:
        """Popularity over train, flagged as a fallback with the cause."""
        recommendations = self.release.popularity.recommend(_PROFILE_ID, k, seen)
        return RecommendationResult(
            self.release.version, "popularity", "popularity", True, reason, recommendations
        )

    def recommend_new(self, profile: Sequence[ProfileEntry], k: int) -> RecommendationResult:
        """M2 on every chosen artist, exactly as evaluated; Popularity for an empty profile.

        Artists outside the M2 catalog still count toward the profile size (as in the
        official M2 test) but carry no signal; if none is known, M2 reduces to its
        popularity component and the result is flagged as a fallback.
        """
        if len(profile) > MAX_PROFILE_ARTISTS:
            raise ValueError(f"A new-user profile holds at most {MAX_PROFILE_ARTISTS} artists")
        if len({entry.item_id for entry in profile}) != len(profile):
            raise ValueError("Duplicate profile artist")
        if not profile:
            return self.recommend_popular(k, "empty_profile", set())
        ignored = [entry.item_id for entry in profile if entry.item_id not in self._m2_catalog]
        rows = [
            Interaction(
                _PROFILE_ID,
                entry.item_id,
                entry.listening_count or self.default_listening_count,
            )
            for entry in profile
        ]
        with self._m2_lock:
            self.release.m2.set_profile(_PROFILE_ID, rows)
            try:
                recommendations = self.release.m2.recommend(_PROFILE_ID, k, set())
            finally:
                self.release.m2.set_profile(_PROFILE_ID, [])
        degenerate = len(ignored) == len(profile)
        return RecommendationResult(
            self.release.version,
            "new_user",
            "m2",
            degenerate,
            "no_profile_artist_in_m2_catalog" if degenerate else None,
            recommendations,
            ignored,
        )

    def mean_listeners(self, recommendations: Sequence[Recommendation]) -> float | None:
        """Mean train listeners of one list, i.e. ARP restricted to a single user."""
        if not recommendations:
            return None
        return float(np.mean([self._listeners.get(r.item_id, 0) for r in recommendations]))
