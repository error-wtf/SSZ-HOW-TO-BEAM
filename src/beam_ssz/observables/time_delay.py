"""Photon time delay (Shapiro delay) calculation.

Implements one-way and round-trip radar echo delays in SSZ metric.
Critical distinction: one-way vs round-trip (factor 2 separate from PPN).
"""

from dataclasses import dataclass
from typing import Literal
import numpy as np
from ..tensor_core import classify_regime, Regime
from .reference_frame import ReferenceFrame


@dataclass
class TimeDelayResult:
    """Result of photon time delay calculation."""
    delay_one_way: float  # One-way signal delay
    delay_round_trip: float  # Round-trip radar echo (factor 2)
    excess_delay: float  # Beyond geometric propagation
    reference_frame: str
    regime: str
    method_used: str
    
    # Source info
    r_emitter: float
    r_receiver: float
    r_closest_approach: float


def compute_photon_delay(
    r_emitter: float,
    r_receiver: float,
    r_s: float,
    xi_func: callable,
    path_type: Literal["radial", "deflected"] = "radial",
    reference: ReferenceFrame = ReferenceFrame.SSZ_CANONICAL,
) -> TimeDelayResult:
    """Compute photon time delay in SSZ metric.
    
    From ssz-complete-documentation:
    - One-way signal delay ≠ Round-trip radar echo (factor 2)
    - Factor 2 is SEPARATE from PPN (1+γ)
    - NEVER conflate them
    
    Args:
        r_emitter: Emitter radial coordinate
        r_receiver: Receiver radial coordinate  
        r_s: Schwarzschild radius
        xi_func: Xi(r) for SSZ segmentation
        path_type: "radial" or "deflected"
        reference: Reference frame
    
    Returns:
        TimeDelayResult with delays
    """
    # Regime classification
    regime_emitter = classify_regime(r_emitter, r_s)
    
    # Geometric delay (flat spacetime)
    d_geom = abs(r_receiver - r_emitter)  # c=1, so distance = time
    
    # SSZ delay calculation
    # For radial path: integrate dt = dr / (D * sqrt(1 - b² D² / r²))
    # where b is impact parameter (0 for radial)
    
    # Simplified: for radial (b=0), dt = dr / D
    # D = 1/(1+Xi)
    
    n_points = 100
    rs = np.linspace(min(r_emitter, r_receiver), max(r_emitter, r_receiver), n_points)
    
    dt_ssz = 0.0
    for i in range(len(rs) - 1):
        dr = rs[i+1] - rs[i]
        r_mid = (rs[i] + rs[i+1]) / 2.0
        
        xi = xi_func(r_mid)
        D = 1.0 / (1.0 + xi)
        
        # dt = dr / D for radial null geodesic (approximate)
        dt_ssz += abs(dr) / D
    
    # Excess delay beyond geometric
    excess = dt_ssz - d_geom
    
    # CRITICAL: One-way vs Round-trip
    # One-way: dt_one_way
    # Round-trip: 2 * dt_one_way (extra factor 2, SEPARATE from PPN)
    
    delay_one_way = dt_ssz
    delay_round_trip = 2.0 * dt_ssz  # Factor 2 for echo
    
    # Reference frame
    if reference == ReferenceFrame.SSZ_CANONICAL:
        ref_name = "SSZ_CANONICAL"
        method = "SSZ_metric_integration"
    else:
        ref_name = "FLAT_MINKOWSKI"
        method = "difference_from_flat"
    
    return TimeDelayResult(
        delay_one_way=delay_one_way,
        delay_round_trip=delay_round_trip,
        excess_delay=excess,
        reference_frame=ref_name,
        regime=regime_emitter.name,
        method_used=method,
        r_emitter=r_emitter,
        r_receiver=r_receiver,
        r_closest_approach=min(r_emitter, r_receiver) if path_type == "radial" else 0.0,
    )


def compute_shapiro_delay_cassini_style(
    r_earth: float,
    r_cassini: float,
    r_s: float,
    xi_func: callable,
) -> dict:
    """Shapiro delay in Cassini-style experiment configuration.
    
    Cassini measured time delay of signals passing near Sun.
    Key feature: asymmetric link (Earth to Cassini, not echo).
    
    Args:
        r_earth: Earth orbital radius
        r_cassini: Cassini orbital radius
        r_s: Solar Schwarzschild radius
        xi_func: SSZ Xi(r)
    
    Returns:
        Dict with Cassini-relevant metrics
    """
    # Closest approach to Sun (minimum r in path)
    r_min = min(r_earth, r_cassini, 1.0)  # Sun at r=0, but SSZ has different center
    
    result = compute_photon_delay(
        r_emitter=r_earth,
        r_receiver=r_cassini,
        r_s=r_s,
        xi_func=xi_func,
        path_type="deflected",
    )
    
    return {
        "delay_one_way_us": result.delay_one_way * 1e6,  # microseconds
        "delay_round_trip_us": result.delay_round_trip * 1e6,
        "excess_delay_us": result.excess_delay * 1e6,
        "regime": result.regime,
        "r_min_solar_radii": r_min,
        "cassini_style_measurement": True,
    }
