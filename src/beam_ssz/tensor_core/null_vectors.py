"""Null vector generation for energy condition tests.

Generates test null vectors k^mu such that g_{mu nu} k^mu k^nu = 0.
"""

import numpy as np
from typing import List


def radial_null_vector(x: np.ndarray, g: np.ndarray, outgoing: bool = True) -> np.ndarray:
    """Generate radial null vector at position x.
    
    For spherical metric, radial null satisfies:
        g_tt (k^t)^2 + g_rr (k^r)^2 = 0
        => k^r = ± sqrt(-g_tt/g_rr) k^t
    
    Args:
        x: Position [t, r, theta, phi]
        g: Metric at x
        outgoing: True for outgoing (k^r > 0), False for ingoing
    
    Returns:
        k^mu array normalized to k^t = 1
    """
    k = np.zeros(4, dtype=float)
    k[0] = 1.0  # k^t = 1
    
    # k^r = ± sqrt(-g_tt/g_rr)
    g_tt = g[0, 0]
    g_rr = g[1, 1]
    
    if g_rr == 0:
        raise ValueError("g_rr is zero, cannot construct radial null vector")
    
    ratio = -g_tt / g_rr
    if ratio < 0:
        # This shouldn't happen for valid Lorentzian metric
        ratio = abs(ratio)
    
    k[1] = np.sqrt(ratio)
    if not outgoing:
        k[1] = -k[1]
    
    k[2] = 0.0  # theta component
    k[3] = 0.0  # phi component
    
    return k


def angular_null_vectors(x: np.ndarray, g: np.ndarray, n_angles: int = 4) -> List[np.ndarray]:
    """Generate null vectors with angular components.
    
    Creates vectors in different angular directions.
    
    Args:
        x: Position [t, r, theta, phi]
        g: Metric at x
        n_angles: Number of angular samples
    
    Returns:
        List of null vector arrays
    """
    vectors = []
    
    for i in range(n_angles):
        angle = 2 * np.pi * i / n_angles
        
        k = np.zeros(4, dtype=float)
        k[0] = 1.0  # time component
        
        # Small angular perturbation
        epsilon = 0.1
        k[2] = epsilon * np.cos(angle)  # theta
        k[3] = epsilon * np.sin(angle)  # phi
        
        # Adjust radial component to maintain null condition
        # This is approximate - proper null condition requires solving
        g_tt = g[0, 0]
        g_rr = g[1, 1]
        
        # Null condition: g_tt (k^t)^2 + g_rr (k^r)^2 + angular = 0
        angular_term = (
            g[2, 2] * k[2]**2 +
            g[3, 3] * k[3]**2 +
            2 * g[1, 2] * k[1] * k[2] +
            2 * g[1, 3] * k[1] * k[3] +
            2 * g[2, 3] * k[2] * k[3]
        )
        
        remaining = -(g_tt * k[0]**2 + angular_term)
        
        if g_rr > 0 and remaining >= 0:
            k[1] = np.sqrt(remaining / g_rr)
            vectors.append(k)
            # Also add opposite direction
            k_neg = k.copy()
            k_neg[1] = -k[1]
            vectors.append(k_neg)
    
    return vectors


def generate_null_vectors(
    x: np.ndarray,
    g: np.ndarray,
    n_samples: int = 8,
) -> List[np.ndarray]:
    """Generate a set of test null vectors.
    
    Combines radial and angular null vectors.
    
    Args:
        x: Position [t, r, theta, phi]
        g: Metric at x
        n_samples: Total number of samples (default 8)
    
    Returns:
        List of null vector arrays k^mu
    """
    vectors = []
    
    # Add radial null vectors
    try:
        k_out = radial_null_vector(x, g, outgoing=True)
        vectors.append(k_out)
        
        k_in = radial_null_vector(x, g, outgoing=False)
        vectors.append(k_in)
    except ValueError:
        pass  # Skip if radial construction fails
    
    # Add angular perturbed vectors
    angular_vecs = angular_null_vectors(x, g, n_angles=min(n_samples // 2, 4))
    vectors.extend(angular_vecs)
    
    return vectors[:n_samples]


def verify_null(k: np.ndarray, g: np.ndarray, tolerance: float = 1e-6) -> bool:
    """Verify that k is null with respect to g.
    
    Args:
        k: Vector k^mu
        g: Metric g_{mu nu}
        tolerance: Maximum allowed deviation from zero
    
    Returns:
        True if |g_{mu nu} k^mu k^nu| < tolerance
    """
    norm = 0.0
    for mu in range(4):
        for nu in range(4):
            norm += g[mu, nu] * k[mu] * k[nu]
    
    return abs(norm) < tolerance
