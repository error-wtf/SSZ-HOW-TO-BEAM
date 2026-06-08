"""Canonical SSZ regime classification."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .constants import X_BLEND_MAX, X_BLEND_MIN, X_PHOTON_SPHERE_MAX, X_STRONG_PHYSICAL_MAX


class Regime(str, Enum):
    VERY_CLOSE = "very_close"
    BLENDED = "blended"
    PHOTON_SPHERE = "photon_sphere"
    STRONG = "strong"
    WEAK = "weak"


@dataclass(frozen=True)
class RegimeInfo:
    x: float
    regime: Regime
    formula_domain: str
    physical_note: str


def classify_regime(x: float) -> RegimeInfo:
    """Classify x=r/r_s according to canonical SSZ formula domains.

    Formula-domain and physical-regime are intentionally distinguished.
    Above x=2.2 the g1 branch is used even though x up to 10 may still be a
    physical strong-field context.
    """
    if x <= 0:
        raise ValueError("x=r/r_s must be positive")
    if x < X_BLEND_MIN:
        return RegimeInfo(x, Regime.VERY_CLOSE, "g2_inner_exponential", "near-horizon / very close")
    if x <= X_BLEND_MAX:
        return RegimeInfo(x, Regime.BLENDED, "hermite_c2_blend", "C2 transition between g2 and g1")
    if x <= X_PHOTON_SPHERE_MAX:
        return RegimeInfo(x, Regime.PHOTON_SPHERE, "g1_weak_branch", "physical photon-sphere regime, g1 formula domain")
    if x <= X_STRONG_PHYSICAL_MAX:
        return RegimeInfo(x, Regime.STRONG, "g1_weak_branch", "physical strong field, g1 formula domain")
    return RegimeInfo(x, Regime.WEAK, "g1_weak_branch", "weak field / GR-equivalent to tested precision")
