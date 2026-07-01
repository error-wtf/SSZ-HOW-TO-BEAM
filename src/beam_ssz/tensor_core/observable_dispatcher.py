"""Observable classification and method dispatcher.

Implements the SSZ Prime Directive:
    Observable → Class → Method → Scope → Calculate

Critical rules from ssz-complete-documentation:
- NULL (light) → PPN (1+γ)
- TIMELIKE STATIC (clocks) → Ξ-proxy
- TIMELIKE ORBIT → PPN (γ,β)
- Factor-2 rule for null observables
"""

from enum import Enum, auto
from typing import Tuple, Dict, Any
import numpy as np


class ObservableType(Enum):
    """Classification of observables per SSZ Prime Directive."""
    NULL_GEODESIC = auto()  # Light paths, ds²=0
    TIMELIKE_STATIC = auto()  # Clocks at rest
    TIMELIKE_ORBIT = auto()  # Orbiting clocks/particles


class Regime(Enum):
    """SSZ regime classification by r/r_s."""
    VERY_CLOSE = auto()  # r_s/r < 1.8, inner exponential
    BLENDED = auto()  # 1.8–2.2, Hermite blend
    PHOTON_SPHERE = auto()  # 2.2–3.0
    STRONG = auto()  # 3.0–10.0
    WEAK = auto()  # > 10.0


def classify_regime(r: float, r_s: float) -> Regime:
    """Classify SSZ regime by r/r_s ratio.
    
    From ssz-complete-documentation:
        < 1.8: very_close (g2/inner exponential)
        1.8–2.2: blended (C² Hermite blend)
        2.2–3.0: photon_sphere
        3.0–10.0: strong
        > 10.0: weak
    
    Args:
        r: Radius from center
        r_s: Schwarzschild radius
    
    Returns:
        Regime classification
    """
    if r_s <= 0:
        return Regime.WEAK
    
    ratio = r / r_s
    
    if ratio < 1.8:
        return Regime.VERY_CLOSE
    elif ratio < 2.2:
        return Regime.BLENDED
    elif ratio < 3.0:
        return Regime.PHOTON_SPHERE
    elif ratio < 10.0:
        return Regime.STRONG
    else:
        return Regime.WEAK


def select_xi_formula(regime: Regime, r: float, r_s: float) -> float:
    """Select correct Ξ formula for regime.
    
    Args:
        regime: Classified regime
        r: Radius
        r_s: Schwarzschild radius
    
    Returns:
        Ξ value
    """
    if regime == Regime.VERY_CLOSE:
        # Inner exponential / g2 branch
        # Placeholder - actual implementation depends on specific model
        return _xi_inner_exponential(r, r_s)
    elif regime == Regime.BLENDED:
        # Hermite blend
        return _xi_hermite_blend(r, r_s)
    else:
        # g1 branch: Ξ = r_s/(2r)
        return r_s / (2.0 * r)


def _xi_inner_exponential(r: float, r_s: float) -> float:
    """Inner exponential branch for very close regime."""
    # Simplified model - actual would use specific SSZ form
    ratio = r / r_s
    return np.exp(-1.0 / ratio) if ratio > 0 else 1.0


def _xi_hermite_blend(r: float, r_s: float) -> float:
    """C² Hermite blend for transition regime."""
    # Blend between very_close and strong formulas
    t = (r / r_s - 1.8) / 0.4  # 0 at 1.8, 1 at 2.2
    t = max(0.0, min(1.0, t))
    
    xi_inner = _xi_inner_exponential(r, r_s)
    xi_outer = r_s / (2.0 * r)
    
    # Hermite interpolation for C² continuity
    h00 = 2*t**3 - 3*t**2 + 1
    h10 = t**3 - 2*t**2 + t
    h01 = -2*t**3 + 3*t**2
    h11 = t**3 - t**2
    
    # Simplified - proper implementation needs derivative matching
    return h00 * xi_inner + h01 * xi_outer


def compute_observable_factor(
    observable_type: ObservableType,
    r: float,
    r_s: float,
    gamma: float = 1.0,  # PPN parameter
    beta: float = 1.0,  # PPN parameter
) -> Dict[str, Any]:
    """Compute transformation factor according to SSZ rules.
    
    Implements Prime Directive:
        Observable → Class → Method → Calculate
    
    Critical: Factor-2 rule for null observables
        Ξ-only gives 50% of GR effect
        Full GR needs PPN: (1+γ), γ=1
    
    Args:
        observable_type: Type of observable
        r: Radius
        r_s: Schwarzschild radius
        gamma: PPN gamma parameter (default 1 for GR)
        beta: PPN beta parameter (default 1 for GR)
    
    Returns:
        Dict with factor and metadata
    """
    regime = classify_regime(r, r_s)
    xi = select_xi_formula(regime, r, r_s)
    
    # Canonical SSZ D factor
    D = 1.0 / (1.0 + xi)
    
    if observable_type == ObservableType.NULL_GEODESIC:
        # NULL: Use PPN (1+γ)
        # CRITICAL: Factor-2 rule
        # Ξ-only would give ~0.5*(effect), need (1+γ) for full
        factor = (1.0 + gamma)
        method = "PPN"
        scope = "full_GR"
        
        # Note: D = 1/(1+Ξ) is the Ξ-proxy piece
        # For null, we need to interpret correctly
        time_dilation = D  # This is the Ξ-only piece
        
    elif observable_type == ObservableType.TIMELIKE_STATIC:
        # TIMELIKE STATIC: Ξ-proxy is correct method
        factor = D  # Direct D factor for clocks
        method = "XI_PROXY"
        scope = "g_tt_only"
        time_dilation = D
        
    elif observable_type == ObservableType.TIMELIKE_ORBIT:
        # TIMELIKE ORBIT: PPN (γ,β)
        factor = (gamma + beta)  # Simplified
        method = "PPN"
        scope = "gamma_beta"
        time_dilation = D
    else:
        raise ValueError(f"Unknown observable type: {observable_type}")
    
    return {
        "observable_type": observable_type.name,
        "regime": regime.name,
        "r_over_rs": r / r_s if r_s > 0 else float('inf'),
        "xi": xi,
        "D": D,
        "factor": factor,
        "method": method,
        "scope": scope,
        "time_dilation": time_dilation,
        "gamma": gamma,
        "beta": beta,
    }


def check_factor_2_warning(null_result: float, expected_gr: float) -> bool:
    """Check if null result shows Factor-2 signature.
    
    If null observable gives ~50% of expected GR:
    - This is NOT a bug
    - Indicates Ξ-only = g_tt piece was used
    - Full GR requires PPN: (1+γ)
    
    Args:
        null_result: Computed null observable effect
        expected_gr: Expected full GR value
    
    Returns:
        True if Factor-2 signature detected
    """
    if expected_gr == 0:
        return False
    
    ratio = null_result / expected_gr
    return 0.4 < ratio < 0.6  # Within ~50% range


class ObservableDispatcher:
    """Main dispatcher implementing SSZ Prime Directive."""
    
    @staticmethod
    def classify_and_compute(
        geodesic_type: str,  # "null" or "timelike"
        motion_state: str,  # "static" or "orbit"
        r: float,
        r_s: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Full classification and computation pipeline.
        
        Args:
            geodesic_type: "null" (light) or "timelike" (massive)
            motion_state: "static" or "orbit"
            r: Position
            r_s: Schwarzschild radius
            **kwargs: Additional parameters (gamma, beta, etc.)
        
        Returns:
            Computation result with full metadata
        """
        # Step 1: Observable → Class
        if geodesic_type == "null":
            obs_type = ObservableType.NULL_GEODESIC
        elif geodesic_type == "timelike":
            if motion_state == "static":
                obs_type = ObservableType.TIMELIKE_STATIC
            else:
                obs_type = ObservableType.TIMELIKE_ORBIT
        else:
            raise ValueError(f"Unknown geodesic type: {geodesic_type}")
        
        # Step 2: Class → Method (built into compute_observable_factor)
        # Step 3: Method → Scope (built into compute_observable_factor)
        # Step 4: Calculate
        
        return compute_observable_factor(
            obs_type, r, r_s,
            gamma=kwargs.get('gamma', 1.0),
            beta=kwargs.get('beta', 1.0)
        )
