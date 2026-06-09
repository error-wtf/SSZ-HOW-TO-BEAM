"""Riemann tensor computation.

R^rho_{sigma mu nu} = partial_mu Gamma^rho_{nu sigma}
                    - partial_nu Gamma^rho_{mu sigma}
                    + Gamma^rho_{mu lambda} Gamma^lambda_{nu sigma}
                    - Gamma^rho_{nu lambda} Gamma^lambda_{mu sigma}
"""

import numpy as np
from typing import Callable
from .christoffel import compute_christoffel


def christoffel_derivative(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    i: int,
    h: float = 1e-5,
) -> np.ndarray:
    """Compute derivative of Christoffel symbols.
    
    dGamma[lam, mu, nu]/dx_i using finite differences.
    """
    x_plus = x.copy()
    x_minus = x.copy()
    x_plus[i] += h
    x_minus[i] -= h
    
    Gamma_plus = compute_christoffel(g_func, x_plus, h)
    Gamma_minus = compute_christoffel(g_func, x_minus, h)
    
    return (Gamma_plus - Gamma_minus) / (2.0 * h)


def compute_riemann(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
) -> np.ndarray:
    """Compute Riemann tensor R[rho, sigma, mu, nu].
    
    Args:
        g_func: Function returning g[mu,nu] at position x
        x: Position array
        h: Step size for finite differences
    
    Returns:
        R[rho, sigma, mu, nu] array (4,4,4,4)
        Antisymmetric in last two indices: R[*,*,mu,nu] == -R[*,*,nu,mu]
    """
    # Compute Christoffel symbols
    Gamma = compute_christoffel(g_func, x, h)
    
    # Compute derivatives of Christoffel
    dGamma = np.zeros((4, 4, 4, 4), dtype=float)
    for i in range(4):
        dGamma[i] = christoffel_derivative(g_func, x, i, h)
    
    # Compute Riemann tensor
    R = np.zeros((4, 4, 4, 4), dtype=float)
    
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    # R^rho_{sigma mu nu} = partial_mu Gamma^rho_{nu sigma}
                    #                       - partial_nu Gamma^rho_{mu sigma}
                    #                       + Gamma^rho_{mu lam} Gamma^lam_{nu sigma}
                    #                       - Gamma^rho_{nu lam} Gamma^lam_{mu sigma}
                    
                    term1 = dGamma[mu, rho, nu, sigma]
                    term2 = dGamma[nu, rho, mu, sigma]
                    
                    term3 = 0.0
                    term4 = 0.0
                    for lam in range(4):
                        term3 += Gamma[rho, mu, lam] * Gamma[lam, nu, sigma]
                        term4 += Gamma[rho, nu, lam] * Gamma[lam, mu, sigma]
                    
                    R[rho, sigma, mu, nu] = term1 - term2 + term3 - term4
    
    return R
