"""Derivative calculations for SSZ functions.

This module provides derivative utilities for Xi, D, s, and related functions.
All derivatives are with respect to the dimensionless radius x = r / r_s unless otherwise noted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .xi import XiEvaluation, evaluate_xi_x


@dataclass(frozen=True)
class DerivativeResult:
    """Container for derivative evaluation results."""
    x: float
    xi: float
    dxi_dx: float
    d2xi_dx2: float
    d_ddx: float
    d_sdx: float
    d2_ddx2: float
    d2_sdx2: float


def compute_derivatives(x: float) -> DerivativeResult:
    """Compute all first and second derivatives for SSZ functions at x.
    
    Args:
        x: Dimensionless radius r / r_s
        
    Returns:
        DerivativeResult containing all derivative values
    """
    ev = evaluate_xi_x(x)
    xi = ev.xi
    dxi = ev.dxi_dx
    d2xi = ev.d2xi_dx2
    
    # D = 1 / (1 + xi)
    # dD/dx = -dxi/dx / (1 + xi)^2
    # d2D/dx2 = -d2xi/dx2 / (1 + xi)^2 + 2*(dxi/dx)^2 / (1 + xi)^3
    
    denom = 1.0 + xi
    denom_sq = denom * denom
    denom_cu = denom_sq * denom
    
    d_ddx = -dxi / denom_sq
    d2_ddx2 = -d2xi / denom_sq + 2.0 * dxi * dxi / denom_cu
    
    # s = 1 + xi
    # ds/dx = dxi/dx
    # d2s/dx2 = d2xi/dx2
    
    d_sdx = dxi
    d2_sdx2 = d2xi
    
    return DerivativeResult(
        x=x,
        xi=xi,
        dxi_dx=dxi,
        d2xi_dx2=d2xi,
        d_ddx=d_ddx,
        d_sdx=d_sdx,
        d2_ddx2=d2_ddx2,
        d2_sdx2=d2_sdx2,
    )


def derivative_chain_rule(
    f: Callable[[float], float],
    df_dx: Callable[[float], float],
    x: float,
    dx_dr: float = 1.0,
) -> tuple[float, float]:
    """Apply chain rule for derivative transformation.
    
    Args:
        f: Function of x
        df_dx: Derivative of f with respect to x
        x: Dimensionless radius
        dx_dr: dx/dr = 1/r_s (default 1.0 for dimensionless)
        
    Returns:
        Tuple of (f, df/dr) where df/dr = df/dx * dx/dr
    """
    fx = f(x)
    dfdr = df_dx(x) * dx_dr
    return fx, dfdr


def second_derivative_chain_rule(
    d2f_dx2: Callable[[float], float],
    df_dx: Callable[[float], float],
    x: float,
    dx_dr: float = 1.0,
    d2x_dr2: float = 0.0,
) -> float:
    """Apply chain rule for second derivative transformation.
    
    Args:
        d2f_dx2: Second derivative of f with respect to x
        df_dx: First derivative of f with respect to x
        x: Dimensionless radius
        dx_dr: dx/dr = 1/r_s
        d2x_dr2: d2x/dr2 (typically 0 for x = r/r_s)
        
    Returns:
        d2f/dr2 = d2f/dx2 * (dx/dr)^2 + df/dx * d2x/dr2
    """
    return d2f_dx2(x) * dx_dr * dx_dr + df_dx(x) * d2x_dr2


def covariant_derivative(f: Callable[[float], float], x: float, Gamma: np.ndarray = None) -> float:
    """Compute covariant derivative df/dx at point x.
    
    Args:
        f: Scalar field function
        x: Point at which to evaluate
        Gamma: Christoffel symbols (optional, defaults to zero)
        
    Returns:
        Covariant derivative value
    """
    import numpy as np
    # For scalar field, covariant derivative = regular derivative
    # Use numerical differentiation
    dx = 1e-8
    df = f(x + dx) - f(x - dx)
    return df / (2 * dx)
