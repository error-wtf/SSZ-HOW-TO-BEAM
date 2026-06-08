"""Tidal safety proxies for early BEAM-SSZ candidates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TidalSafety:
    max_delta_a: float
    limit: float

    @property
    def passes(self) -> bool:
        return self.max_delta_a <= self.limit


def tidal_acceleration_proxy(curvature_scale: float, body_length: float) -> float:
    """Geodesic-deviation magnitude proxy: |Delta a| ~ |R| * L.

    This is not a replacement for a full Riemann tensor; it is a conservative
    scalar gate for early candidates.
    """
    if body_length < 0:
        raise ValueError("body_length must be non-negative")
    return abs(curvature_scale) * body_length


def evaluate_tidal_safety(curvature_scale: float, body_length: float, limit: float) -> TidalSafety:
    return TidalSafety(tidal_acceleration_proxy(curvature_scale, body_length), limit)
