"""Ricci tensor and scalar computation.

R_{mu nu} = R^rho_{mu rho nu} (contraction of Riemann)
R = g^{mu nu} R_{mu nu}
"""

import numpy as np
from typing import Callable
from .riemann import compute_riemann


def compute_ricci(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
) -> np.ndarray:
    """Compute Ricci tensor Ricci[mu, nu].
    
    Contraction: R_{mu nu} = R^rho_{mu rho nu}
    
    Args:
        g_func: Function returning g[mu,nu]
        x: Position array
        h: Step size
    
    Returns:
        Ricci[mu, nu] array (4,4), symmetric
    """
    # Get metric for index raising
    g = g_func(x)
    g_inv = np.linalg.inv(g)
    
    # Compute Riemann tensor
    R = compute_riemann(g_func, x, h)
    
    # Contract: Ricci_{mu nu} = g^{rho sigma} R_{mu rho sigma nu}
    # Or equivalently from Riemann components: R^rho_{mu rho nu}
    # In our convention R[rho, sigma, mu, nu] = R^rho_{sigma mu nu}
    # So Ricci_{mu nu} = sum over rho of R^rho_{mu rho nu}
    
    Ricci = np.zeros((4, 4), dtype=float)
    for mu in range(4):
        for nu in range(4):
            for rho in range(4):
                # R^rho_{mu rho nu}
                Ricci[mu, nu] += R[rho, mu, rho, nu]
    
    return Ricci


def ricci_scalar(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
) -> float:
    """Compute Ricci scalar R = g^{mu nu} R_{mu nu}.
    
    Args:
        g_func: Function returning g[mu,nu]
        x: Position array
        h: Step size
    
    Returns:
        Ricci scalar (float)
    """
    # Get metric
    g = g_func(x)
    g_inv = np.linalg.inv(g)
    
    # Compute Ricci tensor
    Ricci = compute_ricci(g_func, x, h)
    
    # Contract: R = g^{mu nu} R_{mu nu}
    R = 0.0
    for mu in range(4):
        for nu in range(4):
            R += g_inv[mu, nu] * Ricci[mu, nu]
    
    return R
