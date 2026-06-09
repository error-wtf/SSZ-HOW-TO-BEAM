"""Christoffel symbol computation.

Gamma^lambda_{mu nu} = 1/2 g^{lambda sigma} (
    partial_mu g_{nu sigma} + partial_nu g_{mu sigma} - partial_sigma g_{mu nu}
)
"""

import numpy as np
from typing import Callable
from .finite_differences import metric_derivative


def compute_christoffel(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
) -> np.ndarray:
    """Compute Christoffel symbols Gamma[lambda, mu, nu].
    
    Uses finite differences for metric derivatives.
    
    Args:
        g_func: Function returning g[mu,nu] at position x
        x: Position array [t, r, theta, phi]
        h: Step size for finite differences
    
    Returns:
        Gamma[lambda, mu, nu] array (4,4,4)
        Symmetric in lower indices: Gamma[lam, mu, nu] == Gamma[lam, nu, mu]
    """
    # Get metric and inverse at x
    g = g_func(x)
    g_inv = np.linalg.inv(g)
    
    # Compute all partial derivatives of metric
    # dg[i, mu, nu] = partial_i g_{mu nu}
    dg = np.zeros((4, 4, 4), dtype=float)
    for i in range(4):
        dg[i] = metric_derivative(g_func, x, i, h)
    
    # Compute Christoffel symbols
    Gamma = np.zeros((4, 4, 4), dtype=float)
    
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                # Gamma^lambda_{mu nu} = 1/2 g^{lambda sigma} (
                #   partial_mu g_{nu sigma} + partial_nu g_{mu sigma} - partial_sigma g_{mu nu}
                # )
                val = 0.0
                for sigma in range(4):
                    term = (
                        dg[mu, nu, sigma] + dg[nu, mu, sigma] - dg[sigma, mu, nu]
                    )
                    val += g_inv[lam, sigma] * term
                Gamma[lam, mu, nu] = 0.5 * val
    
    return Gamma
