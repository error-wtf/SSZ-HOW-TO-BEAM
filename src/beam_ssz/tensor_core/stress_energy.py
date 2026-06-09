"""Stress-energy tensor from Einstein tensor.

In geometrized units (G = c = 1):
    G_{mu nu} = 8π T_{mu nu}
    => T_{mu nu} = G_{mu nu} / (8π)

WARNING: This is a numerical diagnostic only. The resulting T_{mu nu}
may not correspond to any known physical matter source.
"""

import numpy as np
from typing import Callable
from .einstein import compute_einstein


def compute_stress_energy(
    g_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 1e-5,
    units: str = "geometrized",
) -> np.ndarray:
    """Compute stress-energy tensor T[mu, nu] from Einstein tensor.
    
    T_{mu nu} = G_{mu nu} / (8π)  [geometrized units]
    
    Args:
        g_func: Function returning g[mu,nu]
        x: Position array
        h: Step size
        units: "geometrized" (G=c=1) or "si" (requires conversion)
    
    Returns:
        T[mu, nu] array (4,4), symmetric
    
    Raises:
        ValueError: If units not supported
    """
    if units != "geometrized":
        raise ValueError(f"Only 'geometrized' units supported, got {units}")
    
    # Compute Einstein tensor
    G = compute_einstein(g_func, x, h)
    
    # Convert to stress-energy: T = G / (8π)
    factor = 1.0 / (8.0 * np.pi)
    T = factor * G
    
    return T
