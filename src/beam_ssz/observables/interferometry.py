"""Interferometer response calculation for SSZ detection.

LIGO-style interferometer response to SSZ metric perturbations.
"""

from dataclasses import dataclass
from typing import Tuple
import numpy as np
from .phase_shift import compute_phase_shift
from .reference_frame import ReferenceFrame


@dataclass
class InterferometerResult:
    """Result of interferometer response calculation."""
    arm_length_difference: float  # ΔL = L_x - L_y
    phase_difference: float  # Δφ = φ_x - φ_y
    strain_amplitude: float  # h = ΔL / L
    response_plus: float  # Response to h+ polarization
    response_cross: float  # Response to h× polarization
    
    # Detector geometry
    detector_name: str
    arm_length: float
    orientation: Tuple[float, float]  # (latitude, longitude)
    
    # SSZ source
    xi_at_detector: float
    direction_to_source: Tuple[float, float]  # (theta, phi)


def compute_interferometer_response(
    detector_name: str,
    arm_length: float,
    orientation: Tuple[float, float],
    xi_func: callable,
    direction_to_source: Tuple[float, float],
    wavelength: float = 1064e-9,  # LIGO: 1064 nm
) -> InterferometerResult:
    """Compute LIGO-style interferometer response to SSZ background.
    
    Simplified model: assumes static SSZ background creates
    differential arm length due to anisotropic Xi distribution.
    
    Real LIGO: time-varying signals from moving sources
    This proxy: static SSZ background effect
    
    Args:
        detector_name: e.g., "LIGO_Hanford", "LIGO_Livingston"
        arm_length: Arm cavity length (LIGO: ~4 km)
        orientation: (latitude, longitude) in degrees
        xi_func: Xi(r, theta, phi) — may have angular dependence
        direction_to_source: (theta, phi) to SSZ "source"
        wavelength: Laser wavelength
    
    Returns:
        InterferometerResult with response metrics
    """
    # Simplified: assume Xi varies with direction to source
    # creating effective arm length difference
    
    theta_src, phi_src = direction_to_source
    lat, lon = orientation
    
    # Angle between detector arms and source direction
    # Simplified: assume one arm more aligned with source than other
    
    # Xi at detector location (approximate)
    r_detector = 1.0  # Normalized
    xi_detector = xi_func(r_detector)
    
    # Anisotropy proxy: difference in Xi "seen" by each arm
    # Due to source direction
    angle_factor = np.sin(theta_src) * np.cos(phi_src - np.radians(lon))
    
    # Effective Xi difference between arms (proxy)
    delta_xi = xi_detector * 0.01 * angle_factor  # 1% anisotropy proxy
    
    # Arm length difference from metric
    # L_eff = L × s (spatial scaling factor)
    # s = 1 + Xi
    
    s_x = 1.0 + xi_detector + delta_xi/2  # One arm
    s_y = 1.0 + xi_detector - delta_xi/2  # Other arm
    
    L_x = arm_length * s_x
    L_y = arm_length * s_y
    
    delta_L = L_x - L_y
    
    # Phase difference
    phase_x = L_x / wavelength
    phase_y = L_y / wavelength
    delta_phi = phase_x - phase_y
    
    # Strain amplitude (GW-style metric)
    h = delta_L / arm_length
    
    # Polarization responses (simplified)
    # For SSZ background: mostly "plus" like
    h_plus = h * np.cos(2 * theta_src)
    h_cross = h * np.sin(2 * theta_src) * 0.1  # Suppressed
    
    return InterferometerResult(
        arm_length_difference=delta_L,
        phase_difference=delta_phi,
        strain_amplitude=h,
        response_plus=h_plus,
        response_cross=h_cross,
        detector_name=detector_name,
        arm_length=arm_length,
        orientation=orientation,
        xi_at_detector=xi_detector,
        direction_to_source=direction_to_source,
    )


def compute_ligo_style_proxies(
    xi_func: callable,
    h_threshold: float = 1e-21,  # LIGO detection threshold
) -> dict:
    """Compute LIGO-style observable proxies for SSZ.
    
    Args:
        xi_func: Xi(r, theta, phi) with possible angular dependence
        h_threshold: Detection threshold for strain
    
    Returns:
        Dict with LIGO-relevant metrics
    """
    # Hanford-style detector
    hanford = compute_interferometer_response(
        detector_name="LIGO_Hanford_Proxy",
        arm_length=4000.0,  # 4 km
        orientation=(46.4, -119.4),  # (lat, lon)
        xi_func=xi_func,
        direction_to_source=(np.pi/2, 0),  # Overhead
    )
    
    # Livingston-style
    livingston = compute_interferometer_response(
        detector_name="LIGO_Livingston_Proxy",
        arm_length=4000.0,
        orientation=(30.6, -90.8),
        xi_func=xi_func,
        direction_to_source=(np.pi/2, 0),
    )
    
    # Coincidence (both detectors)
    h_hanford = hanford.strain_amplitude
    h_livingston = livingston.strain_amplitude
    
    # Detection proxy
    detected = (abs(h_hanford) > h_threshold) or (abs(h_livingston) > h_threshold)
    
    return {
        "hanford_strain": h_hanford,
        "livingston_strain": h_livingston,
        "coincidence_detected": detected,
        "threshold": h_threshold,
        "xi_at_detectors": hanford.xi_at_detector,
        "ligo_style_proxy": True,
        "WARNING": "Static SSZ background proxy only, not time-varying GW signal",
    }
