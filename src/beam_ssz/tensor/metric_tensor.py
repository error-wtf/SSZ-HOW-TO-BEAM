"""Metric tensor for SSZ.

This module provides the SSZ metric tensor components.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from ..xi import evaluate_d_s_x


@dataclass(frozen=True)
class MetricTensorResult:
    """Result of metric tensor calculation."""
    g_tt: float
    g_rr: float
    g_thth: float
    g_phiphi: float
    determinant: float
    is_finite: bool


class MetricTensor:
    """SSZ metric tensor calculation."""
    
    @staticmethod
    def compute(r: float, rs: float, theta: float) -> MetricTensorResult:
        """Compute SSZ metric tensor components.
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            
        Returns:
            MetricTensorResult with all components
        """
        if r <= 0 or rs <= 0:
            raise ValueError("r and rs must be positive")
        
        x = r / rs
        d, s, _ = evaluate_d_s_x(x)
        
        # SSZ metric: ds² = -D²c²dt² + s²dr² + r²dΩ²
        g_tt = -(d ** 2)
        g_rr = s ** 2
        g_thth = r ** 2
        g_phiphi = r ** 2 * (np.sin(theta) ** 2)
        
        # Determinant: For metric diag(-D², s², r², r²sin²θ) with s = 1/D
        # det(g) = (-D²)(s²)(r²)(r²sin²θ) = (-D²)(1/D²)(r⁴sin²θ) = -r⁴sin²θ
        # NOTE: D cancels out! det(g) = -r^4 * sin^2(theta)
        determinant = - (r ** 4) * (np.sin(theta) ** 2)
        
        # Check finiteness
        is_finite = all(np.isfinite([g_tt, g_rr, g_thth, g_phiphi, determinant]))
        
        return MetricTensorResult(
            g_tt=g_tt,
            g_rr=g_rr,
            g_thth=g_thth,
            g_phiphi=g_phiphi,
            determinant=determinant,
            is_finite=is_finite,
        )
    
    @staticmethod
    def compute_matrix(r: float, rs: float, theta: float) -> np.ndarray:
        """Compute metric tensor as 4x4 matrix.
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            
        Returns:
            4x4 numpy array representing g_mu_nu
        """
        result = MetricTensor.compute(r, rs, theta)
        
        g = np.zeros((4, 4))
        g[0, 0] = result.g_tt
        g[1, 1] = result.g_rr
        g[2, 2] = result.g_thth
        g[3, 3] = result.g_phiphi
        
        return g
