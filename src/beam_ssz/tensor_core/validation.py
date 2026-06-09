"""Tensor validation utilities.

Checks for finiteness, symmetry, and other tensor properties.
"""

import numpy as np
from typing import Callable, Tuple
from .status import TensorStatus


def validate_tensor_finite(
    tensor: np.ndarray,
    name: str = "tensor",
    tolerance: float = 1e10,
) -> Tuple[bool, dict]:
    """Check if tensor components are finite.
    
    Args:
        tensor: Numpy array to check
        name: Name for error messages
        tolerance: Maximum allowed magnitude
    
    Returns:
        Tuple of (is_valid, details_dict)
    """
    details = {
        "name": name,
        "shape": tensor.shape,
    }
    
    # Check for NaN
    if np.any(np.isnan(tensor)):
        nan_count = np.sum(np.isnan(tensor))
        details["error"] = f"{nan_count} NaN values found"
        return False, details
    
    # Check for inf
    if np.any(np.isinf(tensor)):
        inf_count = np.sum(np.isinf(tensor))
        details["error"] = f"{inf_count} inf values found"
        return False, details
    
    # Check magnitude
    max_val = np.max(np.abs(tensor))
    details["max_magnitude"] = float(max_val)
    
    if max_val > tolerance:
        details["error"] = f"Max magnitude {max_val} exceeds tolerance {tolerance}"
        return False, details
    
    return True, details


def validate_metric_symmetry(g: np.ndarray) -> Tuple[bool, dict]:
    """Check if metric is symmetric.
    
    g_{mu nu} should equal g_{nu mu}
    
    Args:
        g: Metric tensor g[mu,nu]
    
    Returns:
        Tuple of (is_valid, details)
    """
    diff = np.max(np.abs(g - g.T))
    
    details = {
        "max_asymmetry": float(diff),
    }
    
    if diff > 1e-10:
        details["error"] = f"Metric asymmetric by {diff}"
        return False, details
    
    return True, details


def validate_metric_complete(g: np.ndarray) -> Tuple[bool, dict]:
    """Complete metric validation including finiteness and symmetry.
    
    Args:
        g: Metric tensor g[mu,nu]
    
    Returns:
        Tuple of (is_valid, details)
    """
    # Check finiteness
    finite_valid, finite_details = validate_tensor_finite(g, "metric")
    
    # Check symmetry
    sym_valid, sym_details = validate_metric_symmetry(g)
    
    details = {
        "finite_check": finite_details,
        "symmetry_check": sym_details,
    }
    
    if not finite_valid:
        details["error"] = finite_details.get("error", "Metric not finite")
        return False, details
    
    if not sym_valid:
        details["error"] = sym_details.get("error", "Metric not symmetric")
        return False, details
    
    return True, details


def validate_christoffel_symmetry(Gamma: np.ndarray) -> Tuple[bool, dict]:
    """Check Christoffel symmetry in lower indices.
    
    Gamma^lambda_{mu nu} = Gamma^lambda_{nu mu}
    
    Args:
        Gamma: Christoffel symbols Gamma[lam,mu,nu]
    
    Returns:
        Tuple of (is_valid, details)
    """
    # Check Gamma[:, mu, nu] == Gamma[:, nu, mu]
    max_diff = 0.0
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                diff = abs(Gamma[lam, mu, nu] - Gamma[lam, nu, mu])
                max_diff = max(max_diff, diff)
    
    details = {
        "max_lower_index_asymmetry": float(max_diff),
    }
    
    if max_diff > 1e-10:
        details["error"] = f"Christoffel not symmetric in lower indices: {max_diff}"
        return False, details
    
    return True, details


def validate_riemann_antisymmetry(R: np.ndarray) -> Tuple[bool, dict]:
    """Check Riemann antisymmetry in last two indices.
    
    R^rho_{sigma mu nu} = -R^rho_{sigma nu mu}
    
    Args:
        R: Riemann tensor R[rho,sigma,mu,nu]
    
    Returns:
        Tuple of (is_valid, details)
    """
    max_diff = 0.0
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    val = R[rho, sigma, mu, nu]
                    swapped = R[rho, sigma, nu, mu]
                    diff = abs(val + swapped)  # Should be ~0 (antisymmetric)
                    max_diff = max(max_diff, diff)
    
    details = {
        "max_antisymmetry_violation": float(max_diff),
    }
    
    if max_diff > 1e-8:
        details["error"] = f"Riemann not antisymmetric: {max_diff}"
        return False, details
    
    return True, details


def validate_metric_complete(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
) -> Tuple[TensorStatus, dict]:
    """Complete validation of metric and derived tensors.
    
    Args:
        g_func: Function returning metric at position
        x: Position array
        h: Step size for derivatives
    
    Returns:
        Tuple of (TensorStatus, details_dict)
    """
    from .christoffel import compute_christoffel
    from .riemann import compute_riemann
    from .ricci import compute_ricci
    from .einstein import compute_einstein
    
    details = {}
    
    # Get metric
    g = g_func(x)
    
    # Validate metric
    is_finite, g_details = validate_tensor_finite(g, "metric")
    details["metric"] = g_details
    
    if not is_finite:
        return TensorStatus.FAILED, details
    
    is_sym, sym_details = validate_metric_symmetry(g)
    details["metric_symmetry"] = sym_details
    
    if not is_sym:
        return TensorStatus.FAILED, details
    
    # Compute and validate Christoffel
    try:
        Gamma = compute_christoffel(g_func, x, h)
        is_finite, gamma_details = validate_tensor_finite(Gamma, "Christoffel")
        details["christoffel"] = gamma_details
        
        if not is_finite:
            return TensorStatus.FAILED, details
        
        is_sym, sym_details = validate_christoffel_symmetry(Gamma)
        details["christoffel_symmetry"] = sym_details
        
        if not is_sym:
            return TensorStatus.FAILED, details
    except Exception as e:
        details["christoffel_error"] = str(e)
        return TensorStatus.FAILED, details
    
    # Compute and validate Riemann
    try:
        R = compute_riemann(g_func, x, h)
        is_finite, riemann_details = validate_tensor_finite(R, "Riemann")
        details["riemann"] = riemann_details
        
        if not is_finite:
            return TensorStatus.FAILED, details
        
        is_antisym, antisym_details = validate_riemann_antisymmetry(R)
        details["riemann_antisymmetry"] = antisym_details
        
        if not is_antisym:
            return TensorStatus.NUMERIC_WARNING, details
    except Exception as e:
        details["riemann_error"] = str(e)
        return TensorStatus.FAILED, details
    
    # Compute and validate Ricci
    try:
        Ricci = compute_ricci(g_func, x, h)
        is_finite, ricci_details = validate_tensor_finite(Ricci, "Ricci")
        details["ricci"] = ricci_details
        
        if not is_finite:
            return TensorStatus.FAILED, details
    except Exception as e:
        details["ricci_error"] = str(e)
        return TensorStatus.FAILED, details
    
    # Compute and validate Einstein
    try:
        G = compute_einstein(g_func, x, h)
        is_finite, einstein_details = validate_tensor_finite(G, "Einstein")
        details["einstein"] = einstein_details
        
        if not is_finite:
            return TensorStatus.FAILED, details
    except Exception as e:
        details["einstein_error"] = str(e)
        return TensorStatus.FAILED, details
    
    return TensorStatus.FINITE_PASS, details
