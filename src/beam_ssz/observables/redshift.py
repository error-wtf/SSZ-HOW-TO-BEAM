"""Gravitational redshift calculation in SSZ metric.

Redshift from time dilation: z = 1/D - 1 = Xi
For SSZ: z = Xi(receiver) - Xi(emitter) approximately
"""

from dataclasses import dataclass
import numpy as np
from .reference_frame import ReferenceFrame


@dataclass
class RedshiftResult:
    """Result of redshift calculation."""
    redshift_z: float  # z = Δλ/λ
    time_dilation_ratio: float  # D_emitter / D_receiver
    xi_emitter: float
    xi_receiver: float
    reference_frame: str
    
    # Source info
    r_emitter: float
    r_receiver: float
    
    # Multiplicative bookkeeping (not linear addition!)
    energy_at_emitter: float  # E_rest
    energy_at_receiver: float  # E_obs = E_rest × factors


def compute_redshift(
    r_emitter: float,
    r_receiver: float,
    xi_func: callable,
    E_rest: float = 1.0,  # Rest frame energy for bookkeeping
    reference: ReferenceFrame = ReferenceFrame.SSZ_CANONICAL,
) -> RedshiftResult:
    """Compute gravitational redshift in SSZ metric.
    
    From ssz-complete-documentation:
        z = 1/D - 1 = Xi (approximately, for static case)
        Energy: E_obs = E_rest × D_factors (multiplicative, NOT additive)
    
    Args:
        r_emitter: Emitter position
        r_receiver: Receiver position
        xi_func: Xi(r) function
        E_rest: Rest energy for bookkeeping
        reference: Reference frame
    
    Returns:
        RedshiftResult with z and energy bookkeeping
    """
    # Xi values
    xi_e = xi_func(r_emitter)
    xi_r = xi_func(r_receiver)
    
    # D factors
    D_e = 1.0 / (1.0 + xi_e)
    D_r = 1.0 / (1.0 + xi_r)
    
    # Time dilation ratio (receiver / emitter, for blueshift/redshift)
    # Photon emitted at D_e, received at D_r
    # Frequency ratio: ν_r / ν_e = D_e / D_r
    # Redshift: z = ν_e / ν_r - 1 = D_r / D_e - 1
    
    D_ratio = D_r / D_e
    z = D_ratio - 1.0
    
    # Alternative: z ≈ xi_r - xi_e for small differences
    z_approx = xi_r - xi_e
    
    # Energy bookkeeping (multiplicative!)
    # From ssz-complete-documentation:
    #   E_obs = E_rest × (transform factors)
    #   NEVER add SR + GR + "extra" linearly!
    
    transform_factors = {
        "D_gravitational": D_r,  # Time dilation at receiver
        "D_emitter_factor": D_e / D_r,  # Relative
    }
    
    # Multiplicative: E_obs = E_rest × D_r (in SSZ background)
    E_obs = E_rest * D_r
    
    if reference == ReferenceFrame.SSZ_CANONICAL:
        ref_name = "SSZ_CANONICAL"
    else:
        ref_name = "FLAT_MINKOWSKI"
        # In Minkowski comparison: z_diff = z_ssz - z_mink
        # But Minkowski has z=0, so this is just z_ssz
    
    return RedshiftResult(
        redshift_z=z,
        time_dilation_ratio=D_ratio,
        xi_emitter=xi_e,
        xi_receiver=xi_r,
        reference_frame=ref_name,
        r_emitter=r_emitter,
        r_receiver=r_receiver,
        energy_at_emitter=E_rest,
        energy_at_receiver=E_obs,
    )


def compute_redshift_pound_rebka_style(
    delta_h: float,  # Height difference (small)
    g_surface: float,  # Surface gravity
    xi_func: callable,
    r_surface: float,
) -> dict:
    """Pound-Rebka style redshift (small height difference).
    
    Classical GR: z ≈ g Δh / c²
    SSZ: depends on Xi gradient
    
    Args:
        delta_h: Height difference
        g_surface: Surface gravity
        xi_func: Xi(r)
        r_surface: Surface radius
    
    Returns:
        Dict with Pound-Rebka relevant metrics
    """
    r_top = r_surface + delta_h
    r_bottom = r_surface
    
    result = compute_redshift(
        r_emitter=r_bottom,
        r_receiver=r_top,
        xi_func=xi_func,
    )
    
    # Classical expectation
    z_classical = g_surface * delta_h  # c=1 units
    
    return {
        "z_ssz": result.redshift_z,
        "z_classical_gr": z_classical,
        "ssz_to_classical_ratio": result.redshift_z / z_classical if z_classical != 0 else None,
        "pound_rebka_style": True,
        "xi_gradient": result.xi_receiver - result.xi_emitter,
    }
