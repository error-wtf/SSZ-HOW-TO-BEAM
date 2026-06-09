"""Einstein tensor computation.

G_{mu nu} = R_{mu nu} - 1/2 g_{mu nu} R
"""

import numpy as np
from typing import Callable
from .ricci import compute_ricci, ricci_scalar


def compute_einstein(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
) -> np.ndarray:
    """Compute Einstein tensor G[mu, nu].
    
    G_{mu nu} = R_{mu nu} - 1/2 g_{mu nu} R
    
    Args:
        g_func: Function returning g[mu,nu]
        x: Position array
        h: Step size
    
    Returns:
        G[mu, nu] array (4,4), symmetric
    """
    # Get metric
    g = g_func(x)
    
    # Compute Ricci tensor and scalar
    Ricci = compute_ricci(g_func, x, h)
    R = ricci_scalar(g_func, x, h)
    
    # Compute Einstein tensor
    G = np.zeros((4, 4), dtype=float)
    for mu in range(4):
        for nu in range(4):
            G[mu, nu] = Ricci[mu, nu] - 0.5 * g[mu, nu] * R
    
    return G
