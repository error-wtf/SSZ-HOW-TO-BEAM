"""Einstein tensor for SSZ metric.

This module provides Einstein tensor calculations for the SSZ metric.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .ricci import RicciTensor
from .ricci_scalar import RicciScalar
from .metric_tensor import MetricTensor


@dataclass(frozen=True)
class EinsteinResult:
    """Result of Einstein tensor calculation."""
    G_tt: float
    G_rr: float
    G_thth: float
    G_phiphi: float
    is_finite: bool


class EinsteinTensor:
    """Einstein tensor calculation for SSZ metric."""
    
    @staticmethod
    def compute(r: float, rs: float, theta: float, dr: float = 1e-6) -> EinsteinResult:
        """Compute Einstein tensor components.
        
        Einstein tensor: G_μν = R_μν - (1/2) R g_μν
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            dr: Finite difference step
            
        Returns:
            EinsteinResult with all components
        """
        ricci = RicciTensor.compute(r, rs, theta, dr)
        ricci_scalar = RicciScalar.compute(r, rs, theta, dr)
        metric = MetricTensor.compute(r, rs, theta)
        
        R = ricci_scalar.R
        
        # Einstein tensor: G_μν = R_μν - (1/2) R g_μν
        G_tt = ricci.R_tt - 0.5 * R * metric.g_tt
        G_rr = ricci.R_rr - 0.5 * R * metric.g_rr
        G_thth = ricci.R_thth - 0.5 * R * metric.g_thth
        G_phiphi = ricci.R_phiphi - 0.5 * R * metric.g_phiphi
        
        # Check finiteness
        is_finite = all(np.isfinite([G_tt, G_rr, G_thth, G_phiphi]))
        
        return EinsteinResult(
            G_tt=G_tt,
            G_rr=G_rr,
            G_thth=G_thth,
            G_phiphi=G_phiphi,
            is_finite=is_finite,
        )
