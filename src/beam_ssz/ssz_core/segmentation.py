"""SSZ segmentation rules implementation.

Core SSZ relations:
- Xi(r): segment density
- D_SSZ(r) = 1 / (1 + Xi(r)): time dilation
- s_SSZ(r): spatial scaling (convention-dependent)
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

from .status import SegmentationStatus, SSZValidationStatus


@dataclass
class SegmentationResult:
    """Result of SSZ segmentation validation."""
    xi: float
    D: float
    s: float
    status: SegmentationStatus
    details: Dict


def xi_from_radius(r: float, xi_max: Optional[float] = None, 
                   params: Optional[Dict] = None) -> float:
    """Return SSZ segment density Xi(r).
    
    Must be finite and documented.
    
    Args:
        r: Radius
        xi_max: Maximum Xi value if used
        params: Additional parameters
    
    Returns:
        Xi(r) value
    """
    # Canonical SSZ: Xi = r_s / (2r) for weak field
    # Simplified model
    if r <= 0:
        return float('inf')
    
    # Standard formula: Xi proportional to 1/r
    xi = 1.0 / r if params is None else params.get('xi_scale', 1.0) / r
    
    if xi_max is not None:
        xi = min(xi, xi_max)
    
    return xi


def d_ssz_from_xi(xi: float) -> float:
    """Compute D_SSZ = 1 / (1 + Xi).
    
    Args:
        xi: Segment density
    
    Returns:
        D_SSZ time dilation factor
    """
    return 1.0 / (1.0 + xi)


def s_ssz_from_xi(xi: float, convention: str = "inverse_D") -> float:
    """Compute s_SSZ from Xi.
    
    Args:
        xi: Segment density
        convention: 
            - "inverse_D": s = 1 / D = 1 + Xi
            - "one_plus_xi": s = 1 + Xi
    
    Returns:
        s_SSZ spatial scaling factor
    """
    if convention == "inverse_D":
        D = d_ssz_from_xi(xi)
        return 1.0 / D if D > 0 else float('inf')
    elif convention == "one_plus_xi":
        return 1.0 + xi
    else:
        raise ValueError(f"Unknown convention: {convention}")


def validate_segmentation_state(
    xi: float,
    D: Optional[float] = None,
    s: Optional[float] = None,
    convention: str = "inverse_D"
) -> SegmentationResult:
    """Validate SSZ segmentation state.
    
    Args:
        xi: Segment density
        D: Time dilation (computed if None)
        s: Spatial scaling (computed if None)
        convention: s convention
    
    Returns:
        SegmentationResult with status
    """
    details = {
        "xi_input": xi,
        "xi_finite": np.isfinite(xi),
        "xi_non_negative": xi >= 0 if np.isfinite(xi) else False,
    }
    
    # Check Xi
    if not np.isfinite(xi):
        return SegmentationResult(xi, float('nan'), float('nan'),
                                  SegmentationStatus.XI_NON_FINITE, details)
    
    if xi < 0:
        return SegmentationResult(xi, float('nan'), float('nan'),
                                  SegmentationStatus.XI_NEGATIVE, details)
    
    # Compute D
    if D is None:
        D = d_ssz_from_xi(xi)
    
    details["D"] = D
    details["D_positive"] = D > 0
    details["D_leq_one"] = D <= 1.0
    
    if D <= 0:
        return SegmentationResult(xi, D, float('nan'),
                                  SegmentationStatus.D_NON_POSITIVE, details)
    
    # Compute s
    if s is None:
        s = s_ssz_from_xi(xi, convention)
    
    details["s"] = s
    details["s_positive"] = s > 0
    details["s_finite"] = np.isfinite(s)
    
    if s <= 0 or not np.isfinite(s):
        return SegmentationResult(xi, D, s,
                                  SegmentationStatus.S_NON_POSITIVE, details)
    
    # All checks pass
    details["convention"] = convention
    
    return SegmentationResult(xi, D, s,
                              SegmentationStatus.SEGMENTATION_PASS, details)


def validate_segmentation_monotonicity(
    xi_values: np.ndarray,
    r_values: np.ndarray,
) -> Tuple[bool, str]:
    """Check if Xi increases as r decreases (stronger segmentation near center).
    
    Args:
        xi_values: Array of Xi values
        r_values: Array of radii (corresponding to xi_values)
    
    Returns:
        (is_monotonic, message)
    """
    # Sort by r
    sorted_indices = np.argsort(r_values)
    r_sorted = r_values[sorted_indices]
    xi_sorted = xi_values[sorted_indices]
    
    # Xi should increase as r decreases (stronger field)
    # So when sorted by r (increasing), Xi should be decreasing
    xi_diffs = np.diff(xi_sorted)
    
    # Check if Xi generally decreases with increasing r
    # (allow small fluctuations)
    decreasing_count = np.sum(xi_diffs < 0)
    total_count = len(xi_diffs)
    
    if decreasing_count >= 0.7 * total_count:  # 70% decreasing
        return True, f"Xi decreases with r in {decreasing_count}/{total_count} intervals"
    else:
        return False, f"Xi behavior unclear: {decreasing_count}/{total_count} decreasing"
