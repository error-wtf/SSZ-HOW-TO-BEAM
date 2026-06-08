"""Inverse metric tensor for SSZ.

This module provides the inverse SSZ metric tensor components.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .metric_tensor import MetricTensor


@dataclass(frozen=True)
class InverseMetricResult:
    """Result of inverse metric tensor calculation."""
    g_tt_inv: float
    g_rr_inv: float
    g_thth_inv: float
    g_phiphi_inv: float
    is_finite: bool


class InverseMetric:
    """SSZ inverse metric tensor calculation."""
    
    @staticmethod
    def compute(r: float, rs: float, theta: float) -> InverseMetricResult:
        """Compute inverse SSZ metric tensor components.
        
        For diagonal metric, inverse is just reciprocal of diagonal elements.
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            
        Returns:
            InverseMetricResult with all components
        """
        metric = MetricTensor.compute(r, rs, theta)
        
        # Inverse of diagonal metric
        g_tt_inv = 1.0 / metric.g_tt
        g_rr_inv = 1.0 / metric.g_rr
        g_thth_inv = 1.0 / metric.g_thth
        g_phiphi_inv = 1.0 / metric.g_phiphi
        
        # Check finiteness
        is_finite = all(np.isfinite([g_tt_inv, g_rr_inv, g_thth_inv, g_phiphi_inv]))
        
        return InverseMetricResult(
            g_tt_inv=g_tt_inv,
            g_rr_inv=g_rr_inv,
            g_thth_inv=g_thth_inv,
            g_phiphi_inv=g_phiphi_inv,
            is_finite=is_finite,
        )
    
    @staticmethod
    def compute_matrix(r: float, rs: float, theta: float) -> np.ndarray:
        """Compute inverse metric tensor as 4x4 matrix.
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            
        Returns:
            4x4 numpy array representing g^mu_nu
        """
        result = InverseMetric.compute(r, rs, theta)
        
        g_inv = np.zeros((4, 4))
        g_inv[0, 0] = result.g_tt_inv
        g_inv[1, 1] = result.g_rr_inv
        g_inv[2, 2] = result.g_thth_inv
        g_inv[3, 3] = result.g_phiphi_inv
        
        return g_inv
