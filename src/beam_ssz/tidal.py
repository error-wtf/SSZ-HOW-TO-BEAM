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


def compute_tidal_acceleration(r: float, mass: float, body_length: float) -> float:
    """Compute tidal acceleration at distance r from mass M.
    
    Uses Newtonian approximation: |Delta a| ~ 2GM*L/r^3
    where L is the body length (e.g., human height).
    
    Args:
        r: Distance from mass center (meters)
        mass: Mass of the source (kg)
        body_length: Length of the body experiencing tidal force (meters)
    
    Returns:
        Tidal acceleration in m/s^2
    """
    G = 6.674e-11  # Gravitational constant m^3 kg^-1 s^-2
    if r <= 0:
        raise ValueError("Distance r must be positive")
    if body_length < 0:
        raise ValueError("body_length must be non-negative")
    
    # Newtonian tidal acceleration: 2GM*L/r^3
    tidal_accel = 2 * G * mass * body_length / (r ** 3)
    return tidal_accel


@dataclass(frozen=True)
class TidalLimit:
    """Tidal safety limits for human transport."""
    max_safe_acceleration: float = 10.0  # m/s^2, roughly 1g
    
    def is_safe(self, tidal_accel: float) -> bool:
        return tidal_accel <= self.max_safe_acceleration
