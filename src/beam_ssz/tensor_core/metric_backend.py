"""Metric tensor implementations for SSZ.

Provides array-based metric tensors for:
- Minkowski (Cartesian and spherical)
- Flat bridge limit
- Full SSZ metric
"""

import numpy as np
from typing import Tuple, Dict, Any
from .coordinates import CoordinateIndex


def minkowski_cartesian() -> np.ndarray:
    """Return Minkowski metric in Cartesian coordinates.
    
    g = diag(-1, 1, 1, 1)
    
    Returns:
        g[mu, nu] metric tensor array
    """
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -1.0
    g[1, 1] = 1.0
    g[2, 2] = 1.0
    g[3, 3] = 1.0
    return g


def minkowski_spherical(x: np.ndarray) -> np.ndarray:
    """Return Minkowski metric in spherical coordinates.
    
    g = diag(-1, 1, r^2, r^2 sin^2(theta))
    
    Args:
        x: Array [t, r, theta, phi]
    
    Returns:
        g[mu, nu] metric tensor array
    """
    t, r, theta, phi = x
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -1.0
    g[1, 1] = 1.0
    g[2, 2] = r**2
    g[3, 3] = (r * np.sin(theta))**2
    return g


def ssz_metric(
    x: np.ndarray,
    D: float,
    s: float,
    Xi: float = None,
) -> np.ndarray:
    """SSZ bridge metric in spherical coordinates.
    
    Canonical form (from bridge_metric.py):
        g_tt = -D(r)^2
        g_rr = s(r)^2  
        g_thth = r^2
        g_phiphi = r^2 sin^2(theta)
    
    Where:
        D = 1 / (1 + Xi)
        s = 1 + Xi  (or s = 1/D depending on convention)
    
    Args:
        x: Array [t, r, theta, phi]
        D: Time dilation factor D(r)
        s: Spatial scaling factor s(r)
        Xi: Optional, the Xi parameter (for metadata only)
    
    Returns:
        g[mu, nu] metric tensor array
    """
    t, r, theta, phi = x
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -D**2
    g[1, 1] = s**2
    g[2, 2] = r**2
    g[3, 3] = (r * np.sin(theta))**2
    return g


def flat_bridge_limit() -> Tuple[float, float]:
    """Return flat bridge parameters (Xi=0, lambda=0).
    
    Returns:
        (D, s) = (1.0, 1.0)
    """
    return 1.0, 1.0


def metric_from_bridge_candidate(
    bridge: Any,
    x: np.ndarray,
) -> Dict[str, Any]:
    """Convert SSZBridgeMetric to array-based metric tensor.
    
    Args:
        bridge: SSZBridgeMetric instance
        x: Position array [t, r, theta, phi]
    
    Returns:
        Dict with:
            - 'g': metric array g[mu,nu]
            - 'g_inv': inverse metric
            - 'det': determinant
            - 'D': time dilation factor
            - 's': spatial scaling
            - 'Xi': Xi parameter
            - 'status': validation status
    """
    from ..bridge_metric import SSZBridgeMetric
    
    if not isinstance(bridge, SSZBridgeMetric):
        raise TypeError("Expected SSZBridgeMetric instance")
    
    # Extract parameters from bridge
    Xi = bridge.xi_left
    
    # Compute D and s (using canonical convention from bridge_metric.py)
    D = 1.0 / (1.0 + Xi)
    s = 1.0 + Xi  # or 1.0/D depending on convention
    
    # Build metric
    g = ssz_metric(x, D, s, Xi)
    
    # Compute determinant (should be -r^4 sin^2(theta) for s=1/D)
    det = np.linalg.det(g)
    
    # Compute inverse
    g_inv = np.linalg.inv(g)
    
    return {
        'g': g,
        'g_inv': g_inv,
        'det': det,
        'D': D,
        's': s,
        'Xi': Xi,
        'status': 'OK',
    }


def flat_bridge_limit() -> Tuple[float, float]:
    """Return flat bridge limit parameters (Xi=0, lambda=0).
    
    In the flat bridge limit:
    - Xi = 0 (no segmentation)
    - D = 1 (no time dilation)
    - s = 1 (no spatial stretching)
    - lambda = 0 (no bridge coupling)
    
    Returns:
        (D, s) = (1.0, 1.0)
    """
    return 1.0, 1.0
