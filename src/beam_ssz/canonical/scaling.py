"""Canonical SSZ scaling functions D(Ξ) and s(Ξ).

Formulas:
    D_SSZ(Ξ) = 1 / (1 + Ξ)
    s(Ξ) = 1 + Ξ = 1 / D

At horizon (Ξ ≈ 0.8017):
    D(r_s) ≈ 0.5550
    s(r_s) ≈ 1.8017
"""

import numpy as np
from typing import Union


def d_ssz(xi: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Canonical D(Ξ) = 1/(1+Ξ).
    
    This is the time dilation/scaling factor in SSZ metric.
    
    Args:
        xi: Segment density Ξ
        
    Returns:
        D_SSZ value
        
    Examples:
        >>> d_ssz(0.0)  # Flat space
        1.0
        >>> from beam_ssz.canonical.xi import XI_HORIZON
        >>> d_ssz(XI_HORIZON)  # At horizon
        0.555027709...
    """
    return 1.0 / (1.0 + xi)


def s_ssz(xi: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Canonical s(Ξ) = 1 + Ξ = 1/D.
    
    This is the spatial stretching factor in SSZ metric.
    
    Args:
        xi: Segment density Ξ
        
    Returns:
        s value
        
    Examples:
        >>> s_ssz(0.0)  # Flat space
        1.0
        >>> from beam_ssz.canonical.xi import XI_HORIZON
        >>> s_ssz(XI_HORIZON)  # At horizon
        1.801711847...
    """
    return 1.0 + xi


def d_from_s(s: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Compute D from s.
    
    Since s = 1/D, we have D = 1/s.
    
    Args:
        s: Spatial stretching factor
        
    Returns:
        D value
    """
    return 1.0 / s


def s_from_d(d: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Compute s from D.
    
    Since D = 1/s, we have s = 1/D.
    
    Args:
        d: Time dilation factor
        
    Returns:
        s value
    """
    return 1.0 / d


def compute_canonical_scalars(r: Union[float, np.ndarray],
                               r_s: float = 1.0) -> dict:
    """Compute all canonical SSZ scalars at given radius.
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Dictionary with Ξ, D, s values
    """
    from .xi import xi_canonical
    from .regimes import classify_regime, Regime
    
    xi = xi_canonical(r, r_s)
    d = d_ssz(xi)
    s = s_ssz(xi)
    regime = classify_regime(r, r_s)
    
    return {
        'r': float(r) if np.isscalar(r) else r,
        'r_s': float(r_s),
        'r_ratio': float(r / r_s) if np.isscalar(r) else r / r_s,
        'xi': float(xi) if np.isscalar(xi) else xi,
        'D': float(d) if np.isscalar(d) else d,
        's': float(s) if np.isscalar(s) else s,
        'regime': regime.name,
    }


def validate_d_s_consistency(xi: Union[float, np.ndarray]) -> dict:
    """Validate D and s consistency.
    
    Checks that D * s = 1 (within numerical precision).
    
    Args:
        xi: Segment density Ξ
        
    Returns:
        Validation report
    """
    d = d_ssz(xi)
    s = s_ssz(xi)
    
    product = d * s
    
    # Should be exactly 1.0 by construction
    deviation = abs(product - 1.0)
    
    return {
        'xi': float(xi) if np.isscalar(xi) else xi,
        'D': float(d) if np.isscalar(d) else d,
        's': float(s) if np.isscalar(s) else s,
        'D_times_s': float(product) if np.isscalar(product) else product,
        'deviation_from_unity': float(deviation) if np.isscalar(deviation) else deviation,
        'is_consistent': deviation < 1e-14,
    }
