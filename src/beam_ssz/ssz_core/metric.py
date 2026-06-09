"""SSZ metric implementation.

Canonical SSZ metric with proper regularization.
"""

import numpy as np
from typing import Optional


def ssz_metric_tensor(
    x: np.ndarray,
    xi: float,
    convention: str = "inverse_D",
    R_factor: Optional[float] = None,
) -> np.ndarray:
    """Compute SSZ metric tensor g_μν.
    
    Args:
        x: Coordinates [t, r, theta, phi]
        xi: Segment density Xi
        convention: s convention ("inverse_D" or "one_plus_xi")
        R_factor: Optional R(r) factor (default: r)
    
    Returns:
        Metric tensor g[μ,ν]
    """
    t, r, theta, phi = x
    
    # D and s from Xi
    D = 1.0 / (1.0 + xi)
    
    if convention == "inverse_D":
        s = 1.0 / D  # = 1 + Xi
    elif convention == "one_plus_xi":
        s = 1.0 + xi
    else:
        raise ValueError(f"Unknown convention: {convention}")
    
    # R factor (radial function)
    if R_factor is None:
        R = r
    else:
        R = R_factor
    
    # Metric components
    g = np.zeros((4, 4), dtype=float)
    
    g[0, 0] = -D**2  # g_tt
    g[1, 1] = s**2   # g_rr
    g[2, 2] = R**2   # g_theta_theta
    g[3, 3] = (R * np.sin(theta))**2  # g_phi_phi
    
    return g


def ssz_metric_determinant(g: np.ndarray) -> float:
    """Compute metric determinant.
    
    For valid SSZ metric:
    det(g) = -D² · s² · R⁴ · sin²(θ)
    
    Should be negative (Lorentzian signature).
    """
    return np.linalg.det(g)


def ssz_metric_inverse(g: np.ndarray) -> np.ndarray:
    """Compute inverse metric g^μν.
    
    Args:
        g: Metric tensor g_μν
    
    Returns:
        Inverse metric g^μν
    """
    return np.linalg.inv(g)


def validate_ssz_metric(
    g: np.ndarray,
    xi: float,
    tolerance: float = 1e-10,
) -> dict:
    """Validate SSZ metric properties.
    
    Args:
        g: Metric tensor
        xi: Xi value used
        tolerance: Numerical tolerance
    
    Returns:
        Validation dict
    """
    result = {
        "xi": xi,
        "shape": g.shape,
        "is_finite": np.all(np.isfinite(g)),
        "is_symmetric": np.allclose(g, g.T, atol=tolerance),
    }
    
    # Check determinant
    det = ssz_metric_determinant(g)
    result["determinant"] = det
    result["det_negative"] = det < 0
    result["det_finite"] = np.isfinite(det)
    
    # Check Lorentzian signature (one negative, three positive eigenvalues)
    eigenvalues = np.linalg.eigvalsh(g)
    n_negative = np.sum(eigenvalues < -tolerance)
    n_positive = np.sum(eigenvalues > tolerance)
    
    result["eigenvalues"] = eigenvalues
    result["n_negative"] = int(n_negative)
    result["n_positive"] = int(n_positive)
    result["lorentzian_signature"] = (n_negative == 1 and n_positive == 3)
    
    # Check inverse exists
    try:
        g_inv = ssz_metric_inverse(g)
        result["inverse_finite"] = np.all(np.isfinite(g_inv))
        result["inverse_exists"] = True
    except np.linalg.LinAlgError:
        result["inverse_finite"] = False
        result["inverse_exists"] = False
    
    # Overall status
    checks = [
        result["is_finite"],
        result["det_finite"],
        result["det_negative"],
        result["lorentzian_signature"],
        result["inverse_exists"],
        result["inverse_finite"],
    ]
    
    result["valid"] = all(checks)
    
    return result


def check_critical_radius_regularization(
    r: float,
    r_critical: float,
    xi_func: callable,
    tolerance: float = 0.01,
) -> dict:
    """Check if metric is regularized at critical radius.
    
    Args:
        r: Radius to check
        r_critical: Critical radius
        xi_func: Xi(r) function
        tolerance: Distance tolerance
    
    Returns:
        Regularization check dict
    """
    is_near_critical = abs(r - r_critical) < tolerance * r_critical
    
    xi = xi_func(r)
    
    # Near critical point, Xi should remain finite
    xi_finite = np.isfinite(xi)
    xi_not_diverging = xi < 1000  # Reasonable upper bound
    
    return {
        "r": r,
        "r_critical": r_critical,
        "is_near_critical": is_near_critical,
        "xi": xi,
        "xi_finite": xi_finite,
        "xi_not_diverging": xi_not_diverging,
        "regularized": xi_finite and xi_not_diverging,
    }
