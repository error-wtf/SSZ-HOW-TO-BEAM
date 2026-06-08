"""Geodesic utilities for the canonical static, spherical SSZ metric.

The module implements the formulas documented in SSZ complete documentation:

    ds² = -D(r)² c² dt² + D(r)^(-2) dr² + r² dΩ²
    E = D(r)² c² dt/dτ
    L = r² dφ/dτ
    (dr/dτ)² = E²/c² - D(r)² (c² + L²/r²)

By default the helpers use SI c. For dimensionless demonstrations pass c=1.0.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .constants import C
from .xi import evaluate_d_s_x


@dataclass(frozen=True)
class TimelikeConstants:
    """Conserved quantities for a timelike geodesic in the SSZ toy metric."""

    energy: float
    angular_momentum: float = 0.0
    c: float = C


def d_factor(x: float) -> float:
    """Return D(x)=1/(1+Xi(x))."""
    return evaluate_d_s_x(x)[0]


def effective_potential(x: float, angular_momentum: float = 0.0, r_s: float = 1.0, c: float = C) -> float:
    """Return V_eff = D²(c² + L²/r²)."""
    if x <= 0 or r_s <= 0:
        raise ValueError("x and r_s must be positive")
    r = x * r_s
    D = d_factor(x)
    return D * D * (c * c + (angular_momentum * angular_momentum) / (r * r))


def radial_dr_dtau_squared(
    x: float,
    constants: TimelikeConstants | None = None,
    *,
    r_s: float = 1.0,
) -> float:
    """Return (dr/dtau)^2 for a timelike test particle."""
    if constants is None:
        constants = TimelikeConstants(energy=constants_for_rest_at_infinity(c=C).energy)
    if x <= 0:
        raise ValueError("x must be positive")
    return (constants.energy * constants.energy) / (constants.c * constants.c) - effective_potential(
        x, constants.angular_momentum, r_s, constants.c
    )


def constants_for_rest_at_infinity(c: float = C) -> TimelikeConstants:
    """For radial fall from rest at infinity: E = c² and L = 0 in this convention."""
    return TimelikeConstants(energy=c * c, angular_momentum=0.0, c=c)


def radial_freefall_velocity(x: float, c: float = C) -> float:
    """Return v_fall = c*sqrt(1-D²) for radial fall from rest at infinity."""
    D = d_factor(x)
    return c * sqrt(max(0.0, 1.0 - D * D))


def dt_dtau(x: float, energy: float | None = None, c: float = C) -> float:
    """Return dt/dtau = E/(D² c²). Defaults to rest-at-infinity energy E=c²."""
    if energy is None:
        energy = c * c
    D = d_factor(x)
    return energy / (D * D * c * c)


def four_velocity_norm_radial(
    x: float,
    dr_dtau: float,
    dt_dtau_value: float,
    *,
    c: float = C,
    r_s: float = 1.0,
) -> float:
    """Return g(u,u) for radial motion using coordinates (t,r).

    With SI-time coordinate t, g_tt=-D² c² and g_rr=s²=1/D².
    A correctly normalized timelike four velocity has norm -c².
    """
    D, s, _ = evaluate_d_s_x(x)
    return -(D * D) * c * c * dt_dtau_value * dt_dtau_value + (s * s) * dr_dtau * dr_dtau
