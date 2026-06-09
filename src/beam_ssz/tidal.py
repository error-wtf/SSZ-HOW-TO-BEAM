"""Tidal safety proxies for early BEAM-SSZ candidates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TidalSafety:
    max_delta_a: float
    limit: float

    @property
    def passes(self) -> bool:
        return self.max_delta_a <= self.limit


def tidal_acceleration_proxy(curvature_scale: float, body_length: float) -> float:
    """Geodesic-deviation magnitude proxy: |Delta a| ~ |R| * L.

    This is not a replacement for a full Riemann tensor; it is a conservative
    scalar gate for early candidates.
    """
    if body_length < 0:
        raise ValueError("body_length must be non-negative")
    return abs(curvature_scale) * body_length


def evaluate_tidal_safety(curvature_scale: float, body_length: float, limit: float) -> TidalSafety:
    return TidalSafety(tidal_acceleration_proxy(curvature_scale, body_length), limit)


def compute_tidal_acceleration(r: float, mass: float, body_length: float) -> float:
    """Compute tidal acceleration at distance r from mass M.
    
    Uses Newtonian approximation: |Delta a| ~ 2GM*L/r^3
    where L is the body length (e.g., human height).
    
    Args:
        r: Distance from mass center (meters)
        mass: Mass of the source (kg)
        body_length: Length of the body experiencing tidal force (meters)
    
    Returns:
        Tidal acceleration in m/s^2
    """
    G = 6.674e-11  # Gravitational constant m^3 kg^-1 s^-2
    if r <= 0:
        raise ValueError("Distance r must be positive")
    if body_length < 0:
        raise ValueError("body_length must be non-negative")
    
    # Newtonian tidal acceleration: 2GM*L/r^3
    tidal_accel = 2 * G * mass * body_length / (r ** 3)
    return tidal_accel


@dataclass(frozen=True)
class TidalLimit:
    """Tidal safety limits for human transport."""
    max_safe_acceleration: float = 10.0  # m/s^2, roughly 1g
    
    def is_safe(self, tidal_accel: float) -> bool:
        return tidal_accel <= self.max_safe_acceleration


@dataclass(frozen=True)
class HumanBodyDimensions:
    """Standard human body dimensions for tidal calculations."""
    height: float = 1.75  # meters
    shoulder_width: float = 0.45  # meters
    head_height: float = 0.25  # meters
    torso_length: float = 0.60  # meters
    
    @property
    def characteristic_lengths(self) -> list[float]:
        """Return list of characteristic body dimensions."""
        return [self.height, self.shoulder_width, self.head_height, self.torso_length]


def compute_extended_body_tidal(
    bridge,
    u: float,
    body: HumanBodyDimensions = None,
    tolerance: float = 10.0
) -> dict:
    """Compute tidal safety for extended human body at bridge position.
    
    Evaluates tidal acceleration across different body parts and
    determines if passage is safe.
    
    Args:
        bridge: SSZBridgeMetric instance
        u: Bridge coordinate position
        body: HumanBodyDimensions (uses defaults if None)
        tolerance: Maximum tolerable acceleration in m/s^2 (default 1g)
        
    Returns:
        Dictionary with tidal analysis:
        - delta_a_head: Tidal acceleration across head (m/s^2)
        - delta_a_torso: Tidal acceleration across torso (m/s^2)
        - delta_a_full: Tidal acceleration head-to-toe (m/s^2)
        - max_delta_a: Maximum tidal acceleration (m/s^2)
        - is_safe: Whether all parts are within tolerance
        - limiting_factor: Which body part experiences most tidal stress
    """
    if body is None:
        body = HumanBodyDimensions()
    
    # Get metric and compute curvature scale at position u
    # Approximation: curvature_scale ~ d²D/du² / D
    h = 0.01
    xi_u = bridge.xi(u)
    xi_u_plus = bridge.xi(u + h)
    xi_u_minus = bridge.xi(u - h)
    
    # Second derivative of Xi (proxy for curvature)
    d2_xi = (xi_u_plus - 2 * xi_u + xi_u_minus) / (h ** 2)
    
    # Curvature scale: R ~ d²Xi / ell0² (approximate)
    curvature_scale = abs(d2_xi) / (bridge.ell0 ** 2)
    
    # Tidal accelerations for different body parts
    delta_a_head = curvature_scale * body.head_height
    delta_a_torso = curvature_scale * body.torso_length
    delta_a_full = curvature_scale * body.height
    delta_a_shoulder = curvature_scale * body.shoulder_width
    
    max_delta_a = max(delta_a_head, delta_a_torso, delta_a_full, delta_a_shoulder)
    
    # Determine limiting factor
    deltas = {
        'head': delta_a_head,
        'torso': delta_a_torso,
        'full_height': delta_a_full,
        'shoulder_width': delta_a_shoulder
    }
    limiting_factor = max(deltas, key=deltas.get)
    
    return {
        'delta_a_head': float(delta_a_head),
        'delta_a_torso': float(delta_a_torso),
        'delta_a_full': float(delta_a_full),
        'delta_a_shoulder': float(delta_a_shoulder),
        'max_delta_a': float(max_delta_a),
        'is_safe': max_delta_a <= tolerance,
        'limiting_factor': limiting_factor,
        'curvature_scale': float(curvature_scale),
        'tolerance': tolerance,
    }


def analyze_bridge_safety_for_humans(
    bridge,
    n_points: int = 50,
    tolerance: float = 10.0
) -> dict:
    """Analyze human safety across entire bridge.
    
    Scans along bridge coordinate and identifies safe/unsafe regions.
    
    Args:
        bridge: SSZBridgeMetric instance
        n_points: Number of evaluation points
        tolerance: Maximum tolerable tidal acceleration (m/s^2)
        
    Returns:
        Safety analysis dictionary:
        - safe_regions: List of (u_start, u_end) safe intervals
        - unsafe_regions: List of (u_start, u_end) unsafe intervals  
        - max_tidal_across_bridge: Maximum tidal acceleration found
        - most_dangerous_point: Bridge coordinate of max tidal
        - human_passable: Whether bridge has safe passage corridor
        - recommendation: String guidance
    """
    u_values = np.linspace(-1, 1, n_points)
    
    safe_regions = []
    unsafe_regions = []
    
    max_tidal = 0.0
    max_tidal_u = 0.0
    
    in_safe_region = None
    region_start = None
    
    for i, u in enumerate(u_values):
        result = compute_extended_body_tidal(bridge, u, tolerance=tolerance)
        
        if result['max_delta_a'] > max_tidal:
            max_tidal = result['max_delta_a']
            max_tidal_u = u
        
        is_safe = result['is_safe']
        
        # Track regions
        if in_safe_region is None:
            in_safe_region = is_safe
            region_start = u
        elif in_safe_region != is_safe:
            # Region ended
            region = (region_start, u)
            if in_safe_region:
                safe_regions.append(region)
            else:
                unsafe_regions.append(region)
            
            # Start new region
            in_safe_region = is_safe
            region_start = u
    
    # Close final region
    if in_safe_region is not None:
        region = (region_start, u_values[-1])
        if in_safe_region:
            safe_regions.append(region)
        else:
            unsafe_regions.append(region)
    
    # Assessment
    human_passable = len(safe_regions) > 0
    
    if max_tidal <= tolerance:
        recommendation = "PASS: Entire bridge safe for human passage"
    elif any(length > 0.5 for start, end in safe_regions for length in [end - start]):
        recommendation = "CONDITIONAL: Safe corridor exists but tidal forces present"
    else:
        recommendation = "REJECT: No safe passage corridor for humans"
    
    return {
        'safe_regions': safe_regions,
        'unsafe_regions': unsafe_regions,
        'max_tidal_across_bridge': float(max_tidal),
        'most_dangerous_point': float(max_tidal_u),
        'human_passable': human_passable,
        'recommendation': recommendation,
        'tolerance_used': tolerance,
        'n_evaluation_points': n_points,
    }


def find_safe_bridge_parameters(
    xi_left_range: tuple = (0.0, 1.0),
    xi_right_range: tuple = (0.0, 1.0),
    lambda_range: tuple = (0.0, 0.5),
    ell0_range: tuple = (1.0, 100.0),
    n_samples: int = 20,
    tolerance: float = 10.0
) -> dict:
    """Parameter scan for human-safe bridge configurations.
    
    Searches parameter space for bridge configurations that
    would be safe for human passage.
    
    Args:
        xi_left_range: (min, max) for left segment density
        xi_right_range: (min, max) for right segment density
        lambda_range: (min, max) for bridge coupling
        ell0_range: (min, max) for bridge scale in meters
        n_samples: Grid samples per parameter
        tolerance: Maximum tidal acceleration (m/s^2)
        
    Returns:
        Parameter scan results with safe configurations identified.
    """
    import numpy as np
    
    xi_left_vals = np.linspace(xi_left_range[0], xi_left_range[1], n_samples)
    xi_right_vals = np.linspace(xi_right_range[0], xi_right_range[1], n_samples)
    lambda_vals = np.linspace(lambda_range[0], lambda_range[1], n_samples)
    ell0_vals = np.linspace(ell0_range[0], ell0_range[1], n_samples)
    
    safe_configs = []
    
    for xi_left in xi_left_vals:
        for xi_right in xi_right_vals:
            for lambda_bridge in lambda_vals:
                for ell0 in ell0_vals:
                    try:
                        bridge = bridge.__class__(
                            xi_left=float(xi_left),
                            xi_right=float(xi_right),
                            lambda_bridge=float(lambda_bridge),
                            ell0=float(ell0)
                        )
                        
                        result = analyze_bridge_safety_for_humans(
                            bridge, n_points=20, tolerance=tolerance
                        )
                        
                        if result['human_passable']:
                            safe_configs.append({
                                'xi_left': float(xi_left),
                                'xi_right': float(xi_right),
                                'lambda_bridge': float(lambda_bridge),
                                'ell0': float(ell0),
                                'max_tidal': result['max_tidal_across_bridge'],
                            })
                    except Exception:
                        continue
    
    return {
        'safe_configurations': safe_configs,
        'n_safe_found': len(safe_configs),
        'total_samples': n_samples ** 4,
        'parameter_ranges': {
            'xi_left': xi_left_range,
            'xi_right': xi_right_range,
            'lambda': lambda_range,
            'ell0': ell0_range,
        },
        'recommendation': f"Found {len(safe_configs)} safe configurations out of {n_samples**4} sampled"
    }
