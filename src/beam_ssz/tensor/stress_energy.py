"""Stress-energy tensor for SSZ metric.

This module provides stress-energy tensor calculations from the Einstein tensor.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..constants import C, G
from .einstein import EinsteinTensor
from .metric_tensor import MetricTensor


@dataclass(frozen=True)
class StressEnergyResult:
    """Result of stress-energy tensor calculation."""
    T_tt: float
    T_rr: float
    T_thth: float
    T_phiphi: float
    is_finite: bool


class StressEnergyTensor:
    """Stress-energy tensor calculation for SSZ metric."""
    
    @staticmethod
    def compute(r: float, rs: float, theta: float, dr: float = 1e-6) -> StressEnergyResult:
        """Compute effective stress-energy tensor from Einstein tensor.
        
        From Einstein equations: G_μν = (8πG/c^4) T_μν
        Therefore: T_μν = (c^4 / 8πG) G_μν
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            dr: Finite difference step
            
        Returns:
            StressEnergyResult with all components
        """
        einstein = EinsteinTensor.compute(r, rs, theta, dr)
        
        # Conversion factor: c^4 / (8πG)
        factor = (C ** 4) / (8 * np.pi * G)
        
        # T_μν = (c^4 / 8πG) G_μν
        T_tt = factor * einstein.G_tt
        T_rr = factor * einstein.G_rr
        T_thth = factor * einstein.G_thth
        T_phiphi = factor * einstein.G_phiphi
        
        # Check finiteness
        is_finite = all(np.isfinite([T_tt, T_rr, T_thth, T_phiphi]))
        
        return StressEnergyResult(
            T_tt=T_tt,
            T_rr=T_rr,
            T_thth=T_thth,
            T_phiphi=T_phiphi,
            is_finite=is_finite,
        )
