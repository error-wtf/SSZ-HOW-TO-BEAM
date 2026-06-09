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
    point_a: np.ndarray,
    point_b: np.ndarray,
    xi_a: float,
    xi_b: float,
    bridge_coupling: float = 0.0,
    scale: float = 1.0,
) -> float:
    """Return overlap score/proxy for N(A) ∩ N(B).
    
    Args:
        point_a: Point A coordinates
        point_b: Point B coordinates
        xi_a: Xi at A
        xi_b: Xi at B
        bridge_coupling: Bridge coupling (0 = no bridge, 1 = full)
        scale: Neighborhood scale
    
    Returns:
        Overlap score (0 = no overlap, 1 = complete overlap)
    """
    # Distance between points
    spatial_distance = np.linalg.norm(point_a[1:] - point_b[1:])
    
    # Neighborhood radii
    D_a = 1.0 / (1.0 + xi_a)
    D_b = 1.0 / (1.0 + xi_b)
    
    radius_a = scale * D_a * point_a[1]
    radius_b = scale * D_b * point_b[1]
    
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
