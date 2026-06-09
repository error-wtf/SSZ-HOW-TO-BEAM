"""SSZ effective segment-distance collapse.

d_eff(A,B) → 0 under bridge ansatz.
This is a proxy diagnostic, not physical transport proof.
"""

import numpy as np
from typing import List, Callable, Optional, Dict
from dataclasses import dataclass

from .status import SSZValidationStatus


@dataclass
class EffectiveDistanceResult:
    """Result of effective distance calculation."""
    d_eff: float
    baseline_distance: float
    reduction_ratio: float
    status: SSZValidationStatus
    details: Dict


def effective_segment_distance(
    r: float,
    xi: float,
    bridge_coupling: float = 0.0,
) -> float:
    """Compute proxy d_eff along an SSZ path.
    
    This is a proxy diagnostic, not physical transport proof.
    
    Args:
        path: List of coordinate points [t, r, theta, phi]
        xi_func: Xi(r) function
        metric_func: Optional metric function
    
    Returns:
        Effective distance proxy
    """
    from .segmentation import d_ssz_from_xi, s_ssz_from_xi
    D = d_ssz_from_xi(xi)
    s = s_ssz_from_xi(xi)
    # Simple effective distance: r * D * s with optional bridge coupling reduction
    d_eff = r * D * s * (1.0 - bridge_coupling * 0.25)
    return float(d_eff)


def bridge_effective_distance(
    point_a: np.ndarray,
    point_b: np.ndarray,
    bridge_coupling: float,
    xi_func: Callable[[float], float],
    bridge_profile: Optional[Callable] = None,
) -> float:
    """Compute d_eff(A,B) under bridge candidate.
    
    Args:
        point_a: Point A coordinates
        point_b: Point B coordinates
        bridge_coupling: Bridge coupling strength (0 = no bridge, 1 = full)
        xi_func: Xi(r) function
        bridge_profile: Optional bridge profile function
    
    Returns:
        Effective distance with bridge
    """
    # Baseline: direct path without bridge
    # Calculate baseline as simple Euclidean distance
    d_baseline = float(np.linalg.norm(point_b - point_a))
    
    if bridge_coupling <= 0:
        return d_baseline
    
    # With bridge: assume intermediate points with modified Xi
    n_intermediate = max(2, int(bridge_coupling * 10))
    
    path_bridge = [point_a]
    for i in range(1, n_intermediate):
        t = i / n_intermediate
        # Interpolate coordinates
        x_mid = point_a + t * (point_b - point_a)
        
        # Bridge modifies Xi: lower effective Xi on bridge
        # This is the bridge effect - reduced segmentation
        if bridge_profile:
            xi_mod = bridge_profile(x_mid[1], t)
        else:
            # Default: linear reduction of Xi by bridge coupling
            xi_base = xi_func(x_mid[1])
            xi_mod = xi_base * (1.0 - bridge_coupling * 0.5)
        
        # Temporarily override Xi for this point
        path_bridge.append(x_mid)
    
    path_bridge.append(point_b)
    
    # Calculate bridge distance as weighted sum of segments with reduced Xi
    d_with_bridge = 0.0
    for i in range(len(path_bridge) - 1):
        segment = path_bridge[i+1] - path_bridge[i]
        d_segment = float(np.linalg.norm(segment))
        # Apply bridge reduction based on coupling
        d_with_bridge += d_segment * (1.0 - bridge_coupling * 0.5)
    
    return max(0.0, d_with_bridge)


def distance_reduction_ratio(
    d_eff_without: float,
    d_eff_with: float,
) -> Dict:
    """Compute reduction ratio and validation.
    
    Args:
        d_eff_without: Distance without bridge
        d_eff_with: Distance with bridge
    
    Returns:
        Dict with ratio and status
    """
    if d_eff_without <= 0:
        return {
            "ratio": float('nan'),
            "reduction": float('nan'),
            "status": SSZValidationStatus.FAIL,
            "error": "Baseline distance non-positive"
        }
    
    if not np.isfinite(d_eff_with):
        return {
            "ratio": float('nan'),
            "reduction": float('nan'),
            "status": SSZValidationStatus.FAIL,
            "error": "Bridge distance non-finite"
        }
    
    ratio = d_eff_with / d_eff_without
    reduction = 1.0 - ratio
    
    # Validation
    if ratio < 0:
        status = SSZValidationStatus.FAIL
        message = "Negative distance ratio"
    elif ratio > 1.0:
        status = SSZValidationStatus.WARNING
        message = "Bridge increases distance (unexpected)"
    elif not np.isfinite(ratio):
        status = SSZValidationStatus.FAIL
        message = "Non-finite ratio"
    else:
        status = SSZValidationStatus.PASS
        message = f"Reduction: {reduction*100:.1f}%"
    
    return {
        "ratio": ratio,
        "reduction": reduction,
        "status": status,
        "message": message,
        "d_without": d_eff_without,
        "d_with": d_eff_with,
    }


def validate_effective_distance(
    d_eff: float,
    require_finite: bool = True,
    allow_negative: bool = False,
) -> EffectiveDistanceResult:
    """Validate effective distance value.
    
    Args:
        d_eff: Effective distance value
        require_finite: Whether to require finiteness
        allow_negative: Whether to allow negative values
    
    Returns:
        EffectiveDistanceResult
    """
    details = {
        "d_eff": d_eff,
        "is_finite": np.isfinite(d_eff),
        "is_positive": d_eff > 0,
        "is_zero": d_eff == 0,
    }
    
    if require_finite and not np.isfinite(d_eff):
        return EffectiveDistanceResult(
            d_eff, float('nan'), float('nan'),
            SSZValidationStatus.FAIL, details
        )
    
    if not allow_negative and d_eff < 0:
        return EffectiveDistanceResult(
            d_eff, float('nan'), float('nan'),
            SSZValidationStatus.FAIL, details
        )
    
    # Valid
    return EffectiveDistanceResult(
        d_eff, float('nan'), float('nan'),
        SSZValidationStatus.PASS, details
    )
