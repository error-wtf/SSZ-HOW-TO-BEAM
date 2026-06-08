"""Ricci scalar for SSZ metric.

This module provides Ricci scalar calculations for the SSZ metric.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .ricci import RicciTensor
from .inverse_metric import InverseMetric


@dataclass(frozen=True)
class RicciScalarResult:
    """Result of Ricci scalar calculation."""
    R: float
    is_finite: bool


class RicciScalar:
    """Ricci scalar calculation for SSZ metric."""
    
    @staticmethod
    def compute(r: float, rs: float, theta: float, dr: float = 1e-6) -> RicciScalarResult:
        """Compute Ricci scalar.
        
        Ricci scalar: R = g^μν R_μν
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            dr: Finite difference step
            
        Returns:
            RicciScalarResult with scalar value
        """
        ricci = RicciTensor.compute(r, rs, theta, dr)
        g_inv = InverseMetric.compute_matrix(r, rs, theta)
        
        # Contract: R = g^tt R_tt + g^rr R_rr + g^thth R_thth + g^phiphi R_phiphi
        R = (
            g_inv[0, 0] * ricci.R_tt +
            g_inv[1, 1] * ricci.R_rr +
            g_inv[2, 2] * ricci.R_thth +
            g_inv[3, 3] * ricci.R_phiphi
        )
        
        # Check finiteness
        is_finite = np.isfinite(R)
        
        return RicciScalarResult(R=R, is_finite=is_finite)
