"""Ricci tensor for SSZ metric.

This module provides Ricci tensor calculations for the SSZ metric.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .riemann import RiemannTensor


@dataclass(frozen=True)
class RicciResult:
    """Result of Ricci tensor calculation."""
    R_tt: float
    R_rr: float
    R_thth: float
    R_phiphi: float
    is_finite: bool


class RicciTensor:
    """Ricci tensor calculation for SSZ metric."""
    
    @staticmethod
    def compute(r: float, rs: float, theta: float, dr: float = 1e-6) -> RicciResult:
        """Compute Ricci tensor components.
        
        Ricci tensor: R_μν = R^λ_μλν
        
        Args:
            r: Radial coordinate (meters)
            rs: Schwarzschild radius (meters)
            theta: Polar angle (radians)
            dr: Finite difference step
            
        Returns:
            RicciResult with all components
        """
        riemann = RiemannTensor.compute(r, rs, theta, dr)
        components = riemann.components
        
        # Contract Riemann to get Ricci: R_μν = R^λ_μλν
        # For spherical metric, only diagonal components are non-zero
        
        # R_tt = R^r_trt + R^th_tth + R^phi_tphi
        R_tt = components.get(('r', 't', 'r', 't'), 0.0)
        
        # R_rr = R^t_rtr + R^th_rth + R^phi_rphi
        R_rr = components.get(('th', 'r', 't', 'h'), 0.0) + components.get(('phi', 'r', 'p', 'h', 'i'), 0.0)
        
        # R_thth = R^t_tht + R^r_thth + R^phi_thphi
        R_thth = components.get(('r', 'th', 'r', 'th'), 0.0) + components.get(('th', 'phi', 't', 'h', 'phi'), 0.0)
        
        # R_phiphi = R^t_phiphi + R^r_phiphi + R^th_phiphi
        R_phiphi = components.get(('r', 'phi', 'r', 'phi'), 0.0)
        
        # Check finiteness
        is_finite = all(np.isfinite([R_tt, R_rr, R_thth, R_phiphi]))
        
        return RicciResult(
            R_tt=R_tt,
            R_rr=R_rr,
            R_thth=R_thth,
            R_phiphi=R_phiphi,
            is_finite=is_finite,
        )
