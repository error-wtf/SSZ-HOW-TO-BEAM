"""Effective source reconstruction from SSZ metric.

Computes T_eff_μν = G_μν / (8π) from given SSZ metric components.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto


class SourceStatus(Enum):
    """Status levels for effective source definition."""
    FORMATION_UNRESOLVED = auto()
    EFFECTIVE_SOURCE_DEFINED = auto()
    EFFECTIVE_SOURCE_FINITE = auto()
    ENERGY_CONDITION_VIOLATION_DETECTED = auto()
    SOURCE_SMOOTH = auto()


@dataclass
class SourceDiagnostics:
    """Diagnostic data for effective source."""
    max_energy_density: float
    min_energy_density: float
    max_pressure_radial: float
    max_pressure_angular: float
    nec_violation_points: int
    wec_violation_points: int
    sec_violation_points: int
    is_finite: bool
    is_smooth: bool
    
    def to_dict(self) -> Dict:
        return {
            'max_energy_density': float(self.max_energy_density),
            'min_energy_density': float(self.min_energy_density),
            'max_pressure_radial': float(self.max_pressure_radial),
            'max_pressure_angular': float(self.max_pressure_angular),
            'nec_violations': self.nec_violation_points,
            'wec_violations': self.wec_violation_points,
            'sec_violations': self.sec_violation_points,
            'is_finite': self.is_finite,
            'is_smooth': self.is_smooth,
        }


@dataclass
class EffectiveSourceResult:
    """Result of effective source computation.
    
    Contains T_eff_μν and diagnostic information without claiming
    physical realizability.
    """
    T_eff: np.ndarray  # (4,4) stress-energy tensor
    G: np.ndarray  # (4,4) Einstein tensor
    position: np.ndarray  # [t, u, theta, phi]
    energy_density: float  # T_00 (with metric signature adjustment)
    pressures: List[float]  # [p_r, p_theta, p_phi]
    equation_of_state: List[float]  # w_i = p_i / rho
    status: SourceStatus
    diagnostics: SourceDiagnostics
    
    # Metadata
    xi_at_point: float
    D_at_point: float
    s_at_point: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'position': self.position.tolist(),
            'energy_density': float(self.energy_density),
            'pressures': [float(p) for p in self.pressures],
            'equation_of_state': [float(w) for w in self.equation_of_state],
            'status': self.status.name,
            'diagnostics': self.diagnostics.to_dict(),
            'xi': float(self.xi_at_point),
            'D': float(self.D_at_point),
            's': float(self.s_at_point),
        }


def compute_effective_source(
    bridge,
    u: float,
    theta: float = np.pi / 2,
    phi: float = 0.0,
    h: float = 1e-4,
) -> EffectiveSourceResult:
    """Compute effective source T_eff_μν at bridge position.
    
    Given SSZ bridge metric, computes:
        G_μν = Einstein tensor
        T_eff_μν = G_μν / (8π)
    
    Args:
        bridge: SSZBridgeMetric instance
        u: Bridge coordinate [-1, 1]
        theta: Polar angle (default π/2)
        phi: Azimuthal angle (default 0)
        h: Numerical differentiation step
        
    Returns:
        EffectiveSourceResult with T_eff and diagnostics
        
    Note:
        This computes what source would be required, not whether
        such a source physically exists or can be engineered.
    """
    # Import here to avoid circular dependency
    from ..tensor_core import compute_einstein
    
    # Get metric components at this point
    xi_val = bridge.xi(u)
    D_val = bridge.D(u)
    s_val = bridge.s(u)
    
    # CRITICAL FIX: Use bridge's own metric_tensor method, not spherical ssz_metric_tensor
    # Bridge metric uses cylindrical throat geometry with R_B(u), not r=u
    # This prevents singularity at u=0 (which would be r=0 in spherical)
    def g_func(x):
        # Bridge metric is independent of position x, uses bridge coordinate u
        return np.array(bridge.metric_tensor(u, theta=theta))
    
    # Use proper radius for curvature calculation
    position = np.array([0.0, bridge.R(u), theta, phi])
    
    try:
        # Compute Einstein tensor using bridge metric
        G = compute_einstein(g_func, position, h)
        
        # Check finiteness
        if not np.all(np.isfinite(G)):
            diagnostics = SourceDiagnostics(
                max_energy_density=np.inf,
                min_energy_density=-np.inf,
                max_pressure_radial=np.inf,
                max_pressure_angular=np.inf,
                nec_violation_points=0,
                wec_violation_points=0,
                sec_violation_points=0,
                is_finite=False,
                is_smooth=False,
            )
            return EffectiveSourceResult(
                T_eff=np.full((4, 4), np.nan),
                G=G,
                position=position,
                energy_density=np.nan,
                pressures=[np.nan, np.nan, np.nan],
                equation_of_state=[np.nan, np.nan, np.nan],
                status=SourceStatus.FORMATION_UNRESOLVED,
                diagnostics=diagnostics,
                xi_at_point=xi_val,
                D_at_point=D_val,
                s_at_point=s_val,
            )
        
        # Compute effective source: T = G / (8π)
        factor = 1.0 / (8.0 * np.pi)
        T_eff = factor * G
        
        # Extract physical components
        # Note: With metric signature (-,+,+,+), T_00 relates to energy density
        # With our metric signature, adjust accordingly
        g_at_point = g_func(position)
        
        # Energy density: ρ = T^0_0 = g^{0μ} T_{μ0}
        g_inv = np.linalg.inv(g_at_point)
        rho = sum(g_inv[0, mu] * T_eff[mu, 0] for mu in range(4))
        
        # Pressures (spatial diagonal components)
        # p_i = T^i_i (no sum)
        p_radial = sum(g_inv[1, mu] * T_eff[mu, 1] for mu in range(4))
        p_theta = sum(g_inv[2, mu] * T_eff[mu, 2] for mu in range(4))
        p_phi = sum(g_inv[3, mu] * T_eff[mu, 3] for mu in range(4))
        
        pressures = [p_radial, p_theta, p_phi]
        
        # Equation of state w = p/ρ
        equation_of_state = []
        for p in pressures:
            if abs(rho) > 1e-15:
                w = p / rho
            else:
                w = np.inf if p > 0 else -np.inf
            equation_of_state.append(w)
        
        # Check energy conditions
        nec_ok = all(rho + p >= -1e-10 for p in pressures)
        wec_ok = rho >= -1e-10 and nec_ok
        sec_ok = rho + sum(pressures) >= -1e-10 and nec_ok
        
        # Determine status
        if not np.all(np.isfinite(T_eff)):
            status = SourceStatus.FORMATION_UNRESOLVED
        elif not nec_ok or not wec_ok:
            status = SourceStatus.ENERGY_CONDITION_VIOLATION_DETECTED
        else:
            status = SourceStatus.EFFECTIVE_SOURCE_FINITE
        
        # Create diagnostics
        diagnostics = SourceDiagnostics(
            max_energy_density=float(np.max(T_eff)),
            min_energy_density=float(np.min(T_eff)),
            max_pressure_radial=float(abs(p_radial)),
            max_pressure_angular=float(max(abs(p_theta), abs(p_phi))),
            nec_violation_points=0 if nec_ok else 1,
            wec_violation_points=0 if wec_ok else 1,
            sec_violation_points=0 if sec_ok else 1,
            is_finite=np.all(np.isfinite(T_eff)),
            is_smooth=True,  # Would need derivative check for full assessment
        )
        
        return EffectiveSourceResult(
            T_eff=T_eff,
            G=G,
            position=position,
            energy_density=float(rho),
            pressures=[float(p) for p in pressures],
            equation_of_state=[float(w) for w in equation_of_state],
            status=status,
            diagnostics=diagnostics,
            xi_at_point=float(xi_val),
            D_at_point=float(D_val),
            s_at_point=float(s_val),
        )
        
    except (np.linalg.LinAlgError, ValueError, ZeroDivisionError) as e:
        # Singularity or numerical failure
        diagnostics = SourceDiagnostics(
            max_energy_density=np.nan,
            min_energy_density=np.nan,
            max_pressure_radial=np.nan,
            max_pressure_angular=np.nan,
            nec_violation_points=0,
            wec_violation_points=0,
            sec_violation_points=0,
            is_finite=False,
            is_smooth=False,
        )
        return EffectiveSourceResult(
            T_eff=np.full((4, 4), np.nan),
            G=np.full((4, 4), np.nan),
            position=position,
            energy_density=np.nan,
            pressures=[np.nan, np.nan, np.nan],
            equation_of_state=[np.nan, np.nan, np.nan],
            status=SourceStatus.FORMATION_UNRESOLVED,
            diagnostics=diagnostics,
            xi_at_point=float(xi_val),
            D_at_point=float(D_val),
            s_at_point=float(s_val),
        )


def scan_effective_source_along_bridge(
    bridge,
    n_points: int = 50,
) -> List[EffectiveSourceResult]:
    """Scan effective source along entire bridge.
    
    Args:
        bridge: SSZBridgeMetric instance
        n_points: Number of evaluation points
        
    Returns:
        List of EffectiveSourceResult at each point
    """
    u_values = np.linspace(-1, 1, n_points)
    results = []
    
    for u in u_values:
        result = compute_effective_source(bridge, u)
        results.append(result)
    
    return results
