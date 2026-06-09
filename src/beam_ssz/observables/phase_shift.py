"""Phase shift calculation for interferometric observables.

Phase shift from path difference in SSZ metric relative to reference.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from ..tensor_core import ssz_metric, minkowski_spherical
from .reference_frame import ReferenceFrame, get_reference_metric


@dataclass
class PhaseShiftResult:
    """Result of phase shift calculation."""
    phase_shift: float  # Total phase shift
    optical_path_length: float  # ∫ n ds along path
    reference_frame: str
    ssz_absolute: float  # Absolute in SSZ background
    delta_from_flat: Optional[float]  # Difference from Minkowski (if computed)
    wavelength: float  # Wavelength used
    
    # Diagnostic info
    xi_left: float
    xi_right: float
    path_points: int


def compute_phase_shift(
    path_coords: list,  # List of [t, r, theta, phi] points
    wavelength: float,
    xi_func: callable,  # Xi(r) function
    reference: ReferenceFrame = ReferenceFrame.SSZ_CANONICAL,
    r_s: float = 1.0,  # Schwarzschild radius for scaling
) -> PhaseShiftResult:
    """Compute phase shift along path in SSZ metric.
    
    Phase ∝ optical path length = ∫ n ds
    where n is effective index from metric.
    
    Args:
        path_coords: List of coordinate points along path
        wavelength: Wavelength of light
        xi_func: Function Xi(r) defining SSZ segmentation
        reference: Reference frame (SSZ_CANONICAL primary)
        r_s: Schwarzschild radius
    
    Returns:
        PhaseShiftResult with phase and metadata
    """
    # Compute optical path in SSZ
    optical_path_ssz = 0.0
    
    for i in range(len(path_coords) - 1):
        x1 = np.array(path_coords[i])
        x2 = np.array(path_coords[i + 1])
        
        # Midpoint for Xi evaluation
        r_mid = (x1[1] + x2[1]) / 2.0
        xi = xi_func(r_mid)
        
        # SSZ metric at midpoint
        D = 1.0 / (1.0 + xi)
        s = 1.0 + xi
        
        # Compute segment along path
        dx = x2 - x1
        dt, dr, dtheta, dphi = dx
        
        # Metric interval ds² = -D² dt² + s² dr² + r² dθ² + r² sin²θ dφ²
        # For null geodesic (light): ds = 0, but we compute path length differently
        # For phase: count proper spatial distance / wavelength
        
        r_avg = r_mid
        theta_avg = (x1[2] + x2[2]) / 2.0
        
        # Spatial proper distance element
        ds_proper = np.sqrt(
            s**2 * dr**2 +
            r_avg**2 * dtheta**2 +
            (r_avg * np.sin(theta_avg))**2 * dphi**2
        )
        
        optical_path_ssz += ds_proper
    
    # Phase in SSZ background
    phase_ssz = optical_path_ssz / wavelength
    
    # For comparison: phase in Minkowski
    optical_path_minkowski = 0.0
    for i in range(len(path_coords) - 1):
        x1 = np.array(path_coords[i])
        x2 = np.array(path_coords[i + 1])
        
        dx = x2 - x1
        dr = dx[1]
        dtheta = dx[2]
        dphi = dx[3]
        
        r_avg = (x1[1] + x2[1]) / 2.0
        theta_avg = (x1[2] + x2[2]) / 2.0
        
        # Minkowski: s=1
        ds_mink = np.sqrt(
            dr**2 +
            r_avg**2 * dtheta**2 +
            (r_avg * np.sin(theta_avg))**2 * dphi**2
        )
        
        optical_path_minkowski += ds_mink
    
    phase_minkowski = optical_path_minkowski / wavelength
    
    # Reference frame handling
    if reference == ReferenceFrame.SSZ_CANONICAL:
        # Primary: absolute phase in SSZ background
        return PhaseShiftResult(
            phase_shift=phase_ssz,
            optical_path_length=optical_path_ssz,
            reference_frame="SSZ_CANONICAL",
            ssz_absolute=phase_ssz,
            delta_from_flat=phase_ssz - phase_minkowski,
            wavelength=wavelength,
            xi_left=xi_func(path_coords[0][1]),
            xi_right=xi_func(path_coords[-1][1]),
            path_points=len(path_coords),
        )
    
    else:
        # Legacy: difference from flat
        return PhaseShiftResult(
            phase_shift=phase_ssz - phase_minkowski,
            optical_path_length=optical_path_ssz - optical_path_minkowski,
            reference_frame="FLAT_MINKOWSKI",
            ssz_absolute=phase_ssz,
            delta_from_flat=None,
            wavelength=wavelength,
            xi_left=xi_func(path_coords[0][1]),
            xi_right=xi_func(path_coords[-1][1]),
            path_points=len(path_coords),
        )


# Convenience alias for testing
phase_shift = compute_phase_shift
