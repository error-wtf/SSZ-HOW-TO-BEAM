"""SSZ segment-neighborhood overlap.

N(A) ∩ N(B) ≠ ∅ temporary overlap under bridge.
This is a proxy, not a physical wormhole.
"""

import numpy as np
from typing import Callable, Dict
from dataclasses import dataclass

from .status import SSZValidationStatus


@dataclass
class NeighborhoodResult:
    """Result of neighborhood overlap calculation."""
    overlap_score: float
    has_overlap: bool
    threshold_used: float
    status: SSZValidationStatus
    details: Dict


def segment_neighborhood(
    point: np.ndarray,
    xi: float,
    scale: float = 1.0,
) -> Dict:
    """Return abstract SSZ neighborhood proxy.
    
    Args:
        point: Coordinates [t, r, theta, phi]
        xi: Segment density at point
        scale: Neighborhood scale factor
    
    Returns:
        Neighborhood proxy dict
    """
    r = point[1]
    
    # Neighborhood "size" inversely related to Xi
    # High Xi = strong segmentation = small neighborhood extent
    # Low Xi = weak segmentation = larger neighborhood extent
    D = 1.0 / (1.0 + xi)
    
    # Effective neighborhood radius
    neighborhood_radius = scale * D * r
    
    return {
        "center": point,
        "xi": xi,
        "D": D,
        "effective_radius": neighborhood_radius,
        "segmentation_strength": xi,
    }


def neighborhood_overlap(
    point_a,
    point_b,
    xi_a: float = None,
    xi_b: float = None,
    bridge_coupling: float = 0.0,
    scale: float = 1.0,
) -> float:
    """Return overlap score/proxy for N(A) ∩ N(B).
    
    Args:
        point_a: Point A coordinates or just r value
        point_b: Point B coordinates or just r value
        xi_a: Xi at A (if point_a is float)
        xi_b: Xi at B (if point_b is float)
        bridge_coupling: Bridge coupling (0 = no bridge, 1 = full)
        scale: Neighborhood scale
    
    Returns:
        Overlap score (0 = no overlap, 1 = complete overlap)
    """
    # Handle both array and float inputs
    if np.isscalar(point_a):
        # Simple case: just radii given
        r_a = float(point_a)
        r_b = float(point_b)
        # Use default Xi if not provided
        xi_a = xi_a if xi_a is not None else 0.1
        xi_b = xi_b if xi_b is not None else 0.1
    else:
        # Array case: extract radius from coordinate
        point_a = np.asarray(point_a)
        point_b = np.asarray(point_b)
        r_a = point_a[1] if len(point_a) > 1 else point_a[0]
        r_b = point_b[1] if len(point_b) > 1 else point_b[0]
        # Extract Xi if not provided, or use default
        xi_a = xi_a if xi_a is not None else 0.1
        xi_b = xi_b if xi_b is not None else 0.1
    
    # Distance between points (radial only for simplicity)
    spatial_distance = abs(r_b - r_a)
    
    # Neighborhood radii
    D_a = 1.0 / (1.0 + xi_a)
    D_b = 1.0 / (1.0 + xi_b)
    
    radius_a = scale * D_a * r_a
    radius_b = scale * D_b * r_b
    
    # Without bridge: check if neighborhoods overlap
    if bridge_coupling <= 0:
        if spatial_distance < (radius_a + radius_b):
            # Some overlap
            overlap = (radius_a + radius_b - spatial_distance) / (radius_a + radius_b)
            return max(0.0, min(1.0, overlap))
        else:
            return 0.0
    
    # With bridge: effective overlap increased
    # Bridge creates "connection corridor"
    
    # Bridge effectively increases neighborhood radii along connection
    effective_radius_a = radius_a * (1.0 + bridge_coupling)
    effective_radius_b = radius_b * (1.0 + bridge_coupling)
    
    if spatial_distance < (effective_radius_a + effective_radius_b):
        overlap = (effective_radius_a + effective_radius_b - spatial_distance)
        overlap /= (effective_radius_a + effective_radius_b)
        
        # Boost from bridge coupling
        overlap = min(1.0, overlap * (1.0 + bridge_coupling))
        
        return max(0.0, min(1.0, overlap))
    else:
        # Even with bridge, too far
        return bridge_coupling * 0.1  # Small residual from bridge


def has_segment_overlap(
    overlap_score: float,
    threshold: float = 0.1,
) -> bool:
    """Boolean proxy for overlap.
    
    Args:
        overlap_score: Score from neighborhood_overlap
        threshold: Threshold for "significant" overlap
    
    Returns:
        True if overlap > threshold
    """
    return overlap_score > threshold


def validate_neighborhood_proxy(
    overlap_score: float,
    threshold: float = 0.1,
    require_finite: bool = True,
) -> NeighborhoodResult:
    """Validate neighborhood overlap proxy.
    
    Args:
        overlap_score: Overlap score
        threshold: Threshold for "has overlap"
        require_finite: Require finite score
    
    Returns:
        NeighborhoodResult
    """
    details = {
        "overlap_score": overlap_score,
        "threshold": threshold,
        "is_finite": np.isfinite(overlap_score),
        "in_range_0_1": 0.0 <= overlap_score <= 1.0,
    }
    
    if require_finite and not np.isfinite(overlap_score):
        return NeighborhoodResult(
            overlap_score, False, threshold,
            SSZValidationStatus.FAIL, details
        )
    
    has_ovl = has_segment_overlap(overlap_score, threshold)
    
    if has_ovl:
        status = SSZValidationStatus.PASS
    else:
        status = SSZValidationStatus.PENDING
    
    details["has_overlap"] = has_ovl
    
    return NeighborhoodResult(
        overlap_score, has_ovl, threshold,
        status, details
    )
