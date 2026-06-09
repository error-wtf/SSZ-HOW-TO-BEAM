"""Metric bridge search for candidate transfer mechanisms.

This module implements a mathematical framework for searching for
metric bridge candidates that could enable effective distance reduction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.integrate import quad

from .constants import C
from .xi import evaluate_xi_x, evaluate_d_s_x
from .radial_scaling import rho_between_x as rho_integral


@dataclass(frozen=True)
class BridgeParameters:
    """Parameters for a metric bridge candidate."""
    alpha: float  # Coupling strength
    lambda_segment: float  # Segment coupling parameter
    k_min: float  # Minimum coupling
    k_max: float  # Maximum coupling


@dataclass(frozen=True)
class BridgeCandidate:
    """A candidate metric bridge configuration."""
    parameters: BridgeParameters
    A: float  # Start radius
    B: float  # End radius
    rs: float  # Schwarzschild radius
    L_eff: float  # Effective distance
    L_coordinate: float  # Coordinate distance
    reduction_factor: float  # L_eff / L_coordinate
    tidal_max: float  # Maximum tidal acceleration
    ctc_flag: bool  # Closed timelike curve detected
    singularity_flag: bool  # Singularity detected
    worldline_continuous: bool  # Worldline continuity check


def coupling_function(
    r: float,
    rs: float,
    params: BridgeParameters,
) -> float:
    """Calculate coupling function K(r) for a bridge candidate.
    
    This is a mathematical model, not a physical actuator.
    K(r) = exp(-alpha * L_eff(r) / (1 + lambda_segment * Xi(r)))
    
    Args:
        r: Radius (meters)
        rs: Schwarzschild radius (meters)
        params: Bridge parameters
        
    Returns:
        Coupling value (dimensionless)
    """
    x = r / rs
    ev = evaluate_xi_x(x)
    
    # Effective distance from r to infinity (simplified model)
    L_eff_r = rho_integral(r, 10.0 * rs, rs)
    
    coupling = np.exp(-params.alpha * L_eff_r / (1.0 + params.lambda_segment * ev.xi))
    
    # Clamp to physical bounds
    return max(params.k_min, min(params.k_max, coupling))


def effective_distance(
    A: float,
    B: float,
    rs: float,
    params: BridgeParameters,
) -> float:
    """Calculate effective distance L_eff between A and B.
    
    L_eff = integral from A to B of sqrt(h_eff_ij dx^i dx^j)
    Simplified model: L_eff = integral(K(r) * s(r) dr)
    
    Args:
        A: Start radius (meters)
        B: End radius (meters)
        rs: Schwarzschild radius (meters)
        params: Bridge parameters
        
    Returns:
        Effective distance (meters)
    """
    def integrand(r: float) -> float:
        x = r / rs
        _, s, _ = evaluate_d_s_x(x)
        k = coupling_function(r, rs, params)
        return k * s
    
    try:
        integral, _ = quad(integrand, min(A, B), max(A, B), epsabs=1e-12, epsrel=1e-12)
        return integral
    except Exception:
        # Fallback to coordinate distance
        return abs(B - A)


def coordinate_distance(A: float, B: float) -> float:
    """Calculate coordinate distance between A and B.
    
    Args:
        A: Start radius (meters)
        B: End radius (meters)
        
    Returns:
        Coordinate distance (meters)
    """
    return abs(B - A)


def tidal_acceleration_estimate(
    r: float,
    rs: float,
    params: BridgeParameters,
    delta_r: float = 1.0,
) -> float:
    """Estimate tidal acceleration at radius r.
    
    This is a proxy calculation using the second derivative of the effective metric.
    
    Args:
        r: Radius (meters)
        rs: Schwarzschild radius (meters)
        params: Bridge parameters
        delta_r: Separation scale (meters)
        
    Returns:
        Tidal acceleration (m/s^2)
    """
    x = r / rs
    ev = evaluate_xi_x(x)
    
    # Simplified tidal proxy: ~ c^2 * |d2g/dr^2| * delta_r
    # Using SSZ metric g_tt = -D^2
    d, _, _ = evaluate_d_s_x(x)
    
    # Second derivative proxy (finite difference)
    dx = 0.01
    x_plus = x + dx
    x_minus = x - dx
    if x_minus <= 0:
        x_minus = dx
    
    d_plus, _, _ = evaluate_d_s_x(x_plus)
    d_minus, _, _ = evaluate_d_s_x(x_minus)
    
    d2g_dr2 = (d_plus**2 - 2 * d**2 + d_minus**2) / (dx * rs)**2
    
    tidal = C**2 * abs(d2g_dr2) * delta_r
    
    # Apply coupling reduction
    k = coupling_function(r, rs, params)
    return tidal * k


def check_ctc(
    A: float,
    B: float,
    rs: float,
    params: BridgeParameters,
) -> bool:
    """Check for closed timelike curves.
    
    This is a simplified check - CTC detection requires full causal structure analysis.
    
    Args:
        A: Start radius (meters)
        B: End radius (meters)
        rs: Schwarzschild radius (meters)
        params: Bridge parameters
        
    Returns:
        True if CTC detected, False otherwise
    """
    # Simplified check: if effective distance < coordinate distance * c / light_travel_time
    # This is not a rigorous CTC check, just a proxy
    L_eff = effective_distance(A, B, rs, params)
    L_coord = coordinate_distance(A, B)
    
    # If effective distance is unphysically small, flag as potential CTC
    if L_eff < L_coord * 0.1:
        return True
    
    return False


def check_singularity(
    r: float,
    rs: float,
) -> bool:
    """Check for metric singularity at radius r.
    
    Args:
        r: Radius (meters)
        rs: Schwarzschild radius (meters)
        
    Returns:
        True if singularity detected, False otherwise
    """
    x = r / rs
    ev = evaluate_xi_x(x)
    
    # In SSZ, D(r_s) = 0.555 is finite, so no singularity at horizon
    # Check for other potential singularities
    if ev.xi < -1.0:  # Unphysical negative Xi
        return True
    
    if not (ev.dxi_dx >= -1e6 and ev.dxi_dx <= 1e6):  # Divergent derivative
        return True
    
    return False


def evaluate_bridge_candidate(
    A: float,
    B: float,
    rs: float,
    params: BridgeParameters,
) -> BridgeCandidate:
    """Evaluate a complete bridge candidate.
    
    Args:
        A: Start radius (meters)
        B: End radius (meters)
        rs: Schwarzschild radius (meters)
        params: Bridge parameters
        
    Returns:
        BridgeCandidate with full evaluation
    """
    L_coord = coordinate_distance(A, B)
    L_eff = effective_distance(A, B, rs, params)
    reduction_factor = L_eff / L_coord if L_coord > 0 else 1.0
    
    # Estimate maximum tidal acceleration along the path
    r_values = np.linspace(min(A, B), max(A, B), 100)
    tidal_values = [tidal_acceleration_estimate(r, rs, params) for r in r_values]
    tidal_max = max(tidal_values) if tidal_values else 0.0
    
    ctc_flag = check_ctc(A, B, rs, params)
    singularity_flag = any(check_singularity(r, rs) for r in r_values)
    
    # Worldline continuity: check if path is smooth and finite
    worldline_continuous = (not ctc_flag) and (not singularity_flag) and (L_eff > 0)
    
    return BridgeCandidate(
        parameters=params,
        A=A,
        B=B,
        rs=rs,
        L_eff=L_eff,
        L_coordinate=L_coord,
        reduction_factor=reduction_factor,
        tidal_max=tidal_max,
        ctc_flag=ctc_flag,
        singularity_flag=singularity_flag,
        worldline_continuous=worldline_continuous,
    )


# Convenience alias for testing
MetricBridge = BridgeCandidate
