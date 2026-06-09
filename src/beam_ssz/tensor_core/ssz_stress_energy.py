"""SSZ-specific stress-energy analysis.

Reconstructs required stress-energy from SSZ bridge parameters
and checks energy condition violations.
"""

import numpy as np
from typing import Dict, Tuple, Callable
from .stress_energy import compute_stress_energy
from .einstein import compute_einstein
from .metric_backend import ssz_metric


def reconstruct_stress_energy_from_ssz(
    xi_left: float,
    xi_right: float,
    lambda_bridge: float,
    ell0: float,
    throat_radius: float = 1.0,
    u: float = 0.0,
    theta: float = np.pi / 2,
    phi: float = 0.0,
) -> Dict:
    """Reconstruct stress-energy tensor from SSZ bridge parameters.
    
    Given D(u), s(u), computes what T_{mu nu} would be required
    to create such a metric via Einstein equations.
    
    Args:
        xi_left: Segment density at left endpoint
        xi_right: Segment density at right endpoint
        lambda_bridge: Bridge coupling parameter
        ell0: Bridge scale
        throat_radius: Throat radius R_0
        u: Bridge coordinate to evaluate at
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        Dictionary with:
        - T: Stress-energy tensor (4,4)
        - G: Einstein tensor (4,4)
        - energy_density: T_00 (geometrized units)
        - pressures: [T_11, T_22, T_33] (spatial diagonal)
        - equation_of_state: w_i = P_i / rho for each direction
        - energy_conditions: Dict with NEC, WEC, SEC, DEC results
    """
    # Create metric function
    def g_func(x):
        return ssz_metric(
            x, xi_left, xi_right, lambda_bridge,
            ell0, throat_radius
        )['g']
    
    # Position array [t, r, theta, phi]
    # For bridge metric, r is replaced by u coordinate
    x = np.array([0.0, u, theta, phi])
    
    # Compute Einstein tensor
    G = compute_einstein(g_func, x, h=1e-4)
    
    # Convert to stress-energy: T = G / (8π)
    factor = 1.0 / (8.0 * np.pi)
    T = factor * G
    
    # Extract physical components
    energy_density = T[0, 0]  # T_tt (note: with metric signature, this may need adjustment)
    
    # Spatial pressures (diagonal components)
    pressures = [T[1, 1], T[2, 2], T[3, 3]]
    
    # Equation of state w = P/rho for each direction
    equation_of_state = []
    for P in pressures:
        if abs(energy_density) > 1e-15:
            w = P / energy_density
        else:
            w = np.inf if P > 0 else -np.inf
        equation_of_state.append(w)
    
    # Check energy conditions
    energy_conditions = check_energy_conditions(T)
    
    return {
        'T': T,
        'G': G,
        'energy_density': float(energy_density),
        'pressures': [float(p) for p in pressures],
        'equation_of_state': equation_of_state,
        'energy_conditions': energy_conditions,
        'xi_eff': (xi_left + xi_right) / 2 + lambda_bridge * (1 - u**2)**2,
    }


def check_energy_conditions(T: np.ndarray) -> Dict[str, bool]:
    """Check classical energy conditions for stress-energy tensor.
    
    Args:
        T: Stress-energy tensor (4,4)
        
    Returns:
        Dictionary with condition names and satisfaction status
    """
    results = {}
    
    # Null Energy Condition (NEC): T_{mu nu} k^mu k^nu >= 0 for all null k
    # For diagonal T: rho + p_i >= 0 for all i
    rho = T[0, 0]
    if len(T) >= 4:
        p_radial = T[1, 1]
        p_theta = T[2, 2]
        p_phi = T[3, 3]
        
        # NEC: rho + p_i >= 0
        nec_satisfied = all([
            rho + p_radial >= -1e-15,
            rho + p_theta >= -1e-15,
            rho + p_phi >= -1e-15
        ])
        results['NEC'] = bool(nec_satisfied)
        results['NEC_details'] = {
            'rho + p_radial': float(rho + p_radial),
            'rho + p_theta': float(rho + p_theta),
            'rho + p_phi': float(rho + p_phi),
        }
        
        # Weak Energy Condition (WEC): rho >= 0 and rho + p_i >= 0
        wec_satisfied = rho >= -1e-15 and nec_satisfied
        results['WEC'] = bool(wec_satisfied)
        results['WEC_details'] = {
            'rho': float(rho),
        }
        
        # Strong Energy Condition (SEC): rho + sum(p_i) >= 0 and rho + p_i >= 0
        sec_sum = rho + p_radial + p_theta + p_phi
        sec_satisfied = sec_sum >= -1e-15 and nec_satisfied
        results['SEC'] = bool(sec_satisfied)
        results['SEC_details'] = {
            'rho + sum(p)': float(sec_sum),
        }
        
        # Dominant Energy Condition (DEC): |p_i| <= rho for all i
        dec_satisfied = all([
            abs(p_radial) <= abs(rho) + 1e-15,
            abs(p_theta) <= abs(rho) + 1e-15,
            abs(p_phi) <= abs(rho) + 1e-15
        ])
        results['DEC'] = bool(dec_satisfied)
        results['DEC_details'] = {
            '|p_radial| / |rho|': float(abs(p_radial) / (abs(rho) + 1e-15)),
            '|p_theta| / |rho|': float(abs(p_theta) / (abs(rho) + 1e-15)),
            '|p_phi| / |rho|': float(abs(p_phi) / (abs(rho) + 1e-15)),
        }
    
    return results


def analyze_ssz_bridge_matter(
    xi_left: float,
    xi_right: float,
    lambda_bridge: float,
    ell0: float,
    throat_radius: float = 1.0,
    n_points: int = 50,
) -> Dict:
    """Full analysis of matter requirements for SSZ bridge.
    
    Scans along bridge coordinate and determines:
    - Where energy conditions are violated
    - How much exotic matter is required
    - Whether physical realization is plausible
    
    Args:
        xi_left: Left segment density
        xi_right: Right segment density
        lambda_bridge: Bridge coupling
        ell0: Bridge scale
        throat_radius: Throat radius
        n_points: Number of evaluation points along bridge
        
    Returns:
        Analysis dictionary with:
        - violation_points: List of (u, condition) where violated
        - exotic_matter_fraction: Fraction of bridge requiring w < -1/3
        - physical_realizable: Boolean assessment
        - recommendation: String guidance
    """
    u_values = np.linspace(-1, 1, n_points)
    
    violations = []
    exotic_fraction = 0.0
    w_values = []
    
    for u in u_values:
        result = reconstruct_stress_energy_from_ssz(
            xi_left, xi_right, lambda_bridge, ell0,
            throat_radius, u
        )
        
        # Check for NEC violations (requires exotic matter)
        if not result['energy_conditions'].get('NEC', True):
            violations.append((float(u), 'NEC'))
        
        # Track equation of state
        w_avg = np.mean(result['equation_of_state'])
        w_values.append(w_avg)
        
        # Count exotic regions (w < -1/3 is dark energy-like)
        if w_avg < -1/3:
            exotic_fraction += 1.0
    
    exotic_fraction /= n_points
    
    # Assessment
    physical_realizable = exotic_fraction < 0.1 and len(violations) == 0
    
    # Recommendation
    if exotic_fraction > 0.5:
        recommendation = "REJECT: Requires >50% exotic matter (w < -1/3)"
    elif exotic_fraction > 0.1:
        recommendation = "MARGINAL: Requires 10-50% exotic matter"
    elif len(violations) > 0:
        recommendation = "REJECT: Energy condition violations detected"
    else:
        recommendation = "ACCEPT: Matter content physically plausible"
    
    return {
        'xi_left': xi_left,
        'xi_right': xi_right,
        'lambda_bridge': lambda_bridge,
        'violation_points': violations,
        'exotic_matter_fraction': exotic_fraction,
        'w_along_bridge': w_values,
        'physical_realizable': physical_realizable,
        'recommendation': recommendation,
        'n_evaluation_points': n_points,
    }
