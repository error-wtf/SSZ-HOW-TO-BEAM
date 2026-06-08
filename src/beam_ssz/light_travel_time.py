"""Light travel time calculations for SSZ.

This module implements null geodesic light travel time calculations
following the canonical SSZ formulas.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.integrate import quad

from .constants import C
from .xi import evaluate_xi_x, evaluate_d_s_x


@dataclass(frozen=True)
class LightTravelTimeResult:
    """Result of light travel time calculation."""
    r1: float
    r2: float
    rs: float
    delta_t: float
    delta_t_flat: float
    shapiro_correction: float
    integration_success: bool


def radial_null_dt_dr(x: float, rs: float) -> float:
    """Radial null geodesic dt/dr = 1 / (D^2 * c).
    
    Args:
        x: Dimensionless radius r / r_s
        rs: Schwarzschild radius
        
    Returns:
        dt/dr in seconds per meter
    """
    d, _, _ = evaluate_d_s_x(x)
    return 1.0 / (d * d * C)


def light_travel_time(r1: float, r2: float, rs: float) -> LightTravelTimeResult:
    """Calculate light travel time between two radii.
    
    Args:
        r1: Starting radius (meters)
        r2: Ending radius (meters)
        rs: Schwarzschild radius (meters)
        
    Returns:
        LightTravelTimeResult with detailed information
    """
    if r1 <= 0 or r2 <= 0 or rs <= 0:
        raise ValueError("All radii must be positive")
    
    # Flat spacetime travel time
    delta_t_flat = abs(r2 - r1) / C
    
    # Integrate dt/dr = 1/(D^2 * c) from r1 to r2
    def integrand(r: float) -> float:
        x = r / rs
        return radial_null_dt_dr(x, rs)
    
    try:
        integral, error = quad(integrand, min(r1, r2), max(r1, r2), epsabs=1e-12, epsrel=1e-12)
        delta_t = integral
        integration_success = True
    except Exception as e:
        delta_t = delta_t_flat  # Fallback to flat spacetime
        integration_success = False
    
    shapiro_correction = delta_t - delta_t_flat
    
    return LightTravelTimeResult(
        r1=r1,
        r2=r2,
        rs=rs,
        delta_t=delta_t,
        delta_t_flat=delta_t_flat,
        shapiro_correction=shapiro_correction,
        integration_success=integration_success,
    )


def first_order_shapiro_proxy(r1: float, r2: float, rs: float) -> float:
    """First-order Shapiro delay approximation: 2/c * integral(Xi dr).
    
    This is a proxy for the full light travel time calculation.
    Valid for weak fields where Xi << 1.
    
    Args:
        r1: Starting radius (meters)
        r2: Ending radius (meters)
        rs: Schwarzschild radius (meters)
        
    Returns:
        First-order Shapiro delay in seconds
    """
    def integrand(r: float) -> float:
        x = r / rs
        ev = evaluate_xi_x(x)
        return ev.xi
    
    try:
        integral, _ = quad(integrand, min(r1, r2), max(r1, r2), epsabs=1e-12, epsrel=1e-12)
        return 2.0 * integral / C
    except Exception:
        return 0.0
