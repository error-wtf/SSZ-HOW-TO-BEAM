"""First radial geodesic-deviation proxy for BEAM-SSZ.

This is not yet the full tensor package. It turns Xi'' into a finite radial-curvature
proxy so candidate filters can be tested before the v0.5 tensor engine.
"""
from __future__ import annotations

from math import isfinite

from .xi import evaluate_xi_x


def radial_curvature_proxy(x: float, *, r_s: float = 1.0) -> float:
    """Return a finite proxy proportional to D*Xi''(r).

    The holonomy documentation gives kappa_SSZ ≈ d²Xi/dr² * D(r) at leading order.
    """
    if r_s <= 0:
        raise ValueError("r_s must be positive")
    ev = evaluate_xi_x(x)
    D = 1.0 / (1.0 + ev.xi)
    return D * ev.d2xi_dx2 / (r_s * r_s)


def radial_tidal_acceleration_proxy(x: float, separation: float, *, r_s: float = 1.0) -> float:
    """Return |kappa|*separation as a first tidal acceleration proxy in c=1 units."""
    if separation < 0:
        raise ValueError("separation must be non-negative")
    kappa = radial_curvature_proxy(x, r_s=r_s)
    value = abs(kappa) * separation
    if not isfinite(value):
        raise ArithmeticError("non-finite tidal proxy")
    return value


def geodesic_deviation(x1: float, x2: float, separation: float, *, r_s: float = 1.0) -> dict:
    """Calculate geodesic deviation between two nearby geodesics.
    
    Args:
        x1: Dimensionless radius at point 1
        x2: Dimensionless radius at point 2
        separation: Separation between geodesics
        r_s: Schwarzschild radius
        
    Returns:
        Dict with deviation metrics
    """
    kappa1 = radial_curvature_proxy(x1, r_s=r_s)
    kappa2 = radial_curvature_proxy(x2, r_s=r_s)
    
    return {
        "kappa_1": kappa1,
        "kappa_2": kappa2,
        "delta_kappa": kappa2 - kappa1,
        "tidal_acceleration_1": radial_tidal_acceleration_proxy(x1, separation, r_s=r_s),
        "tidal_acceleration_2": radial_tidal_acceleration_proxy(x2, separation, r_s=r_s),
        "separation": separation,
    }
