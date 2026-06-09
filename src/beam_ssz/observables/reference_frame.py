"""Reference frame selection for observable calculations.

Critical: SSZ canonical background is the PRIMARY reference.
Minkowski is only for comparison, not the physical truth standard.
"""

from enum import Enum, auto
import numpy as np
from typing import Callable
from ..tensor_core import minkowski_spherical, ssz_metric


class ReferenceFrame(Enum):
    """Reference frame for observable calculations."""
    SSZ_CANONICAL = auto()  # Primary: SSZ segmentation background
    FLAT_MINKOWSKI = auto()  # Comparison only: flat limit


def get_reference_metric(
    frame: ReferenceFrame,
    r: float,
    xi_default: float = 0.0,
) -> Callable[[np.ndarray], np.ndarray]:
    """Get metric function for reference frame.
    
    Args:
        frame: ReferenceFrame.SSZ_CANONICAL or FLAT_MINKOWSKI
        r: Radial coordinate (for theta=pi/2 slice)
        xi_default: Default Xi for SSZ canonical (0 = flat limit)
    
    Returns:
        Function g(x) returning metric array
    """
    if frame == ReferenceFrame.FLAT_MINKOWSKI:
        # Flat Minkowski in spherical coordinates
        def g_minkowski(x):
            return minkowski_spherical(x)
        return g_minkowski
    
    elif frame == ReferenceFrame.SSZ_CANONICAL:
        # SSZ canonical background with Xi
        D = 1.0 / (1.0 + xi_default)
        s = 1.0 + xi_default
        
        def g_ssz(x):
            return ssz_metric(x, D, s, xi_default)
        return g_ssz
    
    else:
        raise ValueError(f"Unknown reference frame: {frame}")


def compute_observable_relative_to_reference(
    observable_value_ssz: float,
    observable_value_minkowski: float,
    reference: ReferenceFrame = ReferenceFrame.SSZ_CANONICAL,
) -> dict:
    """Compute observable relative to chosen reference.
    
    For SSZ_CANONICAL: returns absolute value in SSZ background
    For FLAT_MINKOWSKI: returns difference from flat (legacy comparison)
    
    Args:
        observable_value_ssz: Value in SSZ metric
        observable_value_minkowski: Value in Minkowski
        reference: Which reference frame
    
    Returns:
        Dict with value and metadata
    """
    if reference == ReferenceFrame.SSZ_CANONICAL:
        # Primary: absolute value in SSZ background
        return {
            "value": observable_value_ssz,
            "reference": "SSZ_CANONICAL",
            "frame_note": "Absolute value in SSZ segmentation background",
            "minkowski_comparison": observable_value_minkowski,
            "delta_from_flat": observable_value_ssz - observable_value_minkowski,
        }
    
    elif reference == ReferenceFrame.FLAT_MINKOWSKI:
        # Legacy: difference from flat (for comparison only)
        return {
            "value": observable_value_ssz - observable_value_minkowski,
            "reference": "FLAT_MINKOWSKI",
            "frame_note": "DIFFERENCE from flat (comparison only, not physical truth)",
            "ssz_absolute": observable_value_ssz,
            "minkowski_reference": observable_value_minkowski,
        }
    
    else:
        raise ValueError(f"Unknown reference: {reference}")
