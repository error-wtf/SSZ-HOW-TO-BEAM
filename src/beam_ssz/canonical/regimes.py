"""Canonical SSZ regime classification.

Regime boundaries aligned with ssz-complete-documentation.
"""

from enum import Enum, auto
from typing import Dict, Tuple
import numpy as np


class Regime(Enum):
    """SSZ regime classification."""
    VERY_CLOSE = auto()      # r_s/r < 1.8: strong field, exp form
    BLENDED = auto()         # 1.8 ≤ r/r_s ≤ 2.2: interpolation
    PHOTON_SPHERE = auto()   # 2.2 < r/r_s < 3.0: transition
    STRONG = auto()          # 3.0 ≤ r/r_s ≤ 10.0: weak field valid
    WEAK = auto()            # r/r_s > 10.0: asymptotic


# Canonical regime boundaries (r/r_s ratios)
REGIME_BOUNDARIES: Dict[Regime, Tuple[float, float]] = {
    Regime.VERY_CLOSE: (0.0, 1.8),
    Regime.BLENDED: (1.8, 2.2),
    Regime.PHOTON_SPHERE: (2.2, 3.0),
    Regime.STRONG: (3.0, 10.0),
    Regime.WEAK: (10.0, np.inf),
}


# Human-readable regime descriptions
REGIME_DESCRIPTIONS: Dict[Regime, str] = {
    Regime.VERY_CLOSE: "Very close to center: strong field, exponential Xi form",
    Regime.BLENDED: "Blend zone: Hermite interpolation between branches",
    Regime.PHOTON_SPHERE: "Photon sphere region: transition regime",
    Regime.STRONG: "Strong field: weak branch valid but significant effects",
    Regime.WEAK: "Weak field: asymptotic regime, small Xi",
}


def classify_regime(r: float, r_s: float = 1.0) -> Regime:
    """Classify SSZ regime based on r/r_s ratio.
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Regime enum value
        
    Examples:
        >>> classify_regime(1.0, 1.0)  # r/r_s = 1 (horizon)
        Regime.VERY_CLOSE
        >>> classify_regime(5.0, 1.0)  # r/r_s = 5
        Regime.STRONG
        >>> classify_regime(20.0, 1.0)  # r/r_s = 20
        Regime.WEAK
    """
    ratio = r / r_s
    
    if ratio < 1.8:
        return Regime.VERY_CLOSE
    elif ratio <= 2.2:
        return Regime.BLENDED
    elif ratio < 3.0:
        return Regime.PHOTON_SPHERE
    elif ratio <= 10.0:
        return Regime.STRONG
    else:
        return Regime.WEAK


def get_regime_info(r: float, r_s: float = 1.0) -> Dict:
    """Get comprehensive regime information.
    
    Args:
        r: Radial coordinate
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Dictionary with regime details
    """
    regime = classify_regime(r, r_s)
    ratio = r / r_s
    
    bounds = REGIME_BOUNDARIES[regime]
    
    return {
        'regime': regime.name,
        'r_ratio': float(ratio),
        'description': REGIME_DESCRIPTIONS[regime],
        'bounds': (float(bounds[0]), float(bounds[1]) if np.isfinite(bounds[1]) else 'inf'),
        'canonical_xi_branch': _get_canonical_branch(regime),
    }


def _get_canonical_branch(regime: Regime) -> str:
    """Get canonical Xi branch for regime."""
    branch_map = {
        Regime.VERY_CLOSE: "xi_strong (exp)",
        Regime.BLENDED: "xi_blend (Hermite)",
        Regime.PHOTON_SPHERE: "xi_weak (linear)",
        Regime.STRONG: "xi_weak (linear)",
        Regime.WEAK: "xi_weak (linear, asymptotic)",
    }
    return branch_map.get(regime, "unknown")


def validate_regime_transition(r_values: np.ndarray, 
                               r_s: float = 1.0) -> Dict:
    """Validate regime transitions across radial range.
    
    Args:
        r_values: Array of radial coordinates
        r_s: Schwarzschild radius (default 1.0)
        
    Returns:
        Validation report
    """
    ratios = r_values / r_s
    regimes = [classify_regime(r, r_s) for r in r_values]
    
    # Check for regime transitions
    transitions = []
    for i in range(len(regimes) - 1):
        if regimes[i] != regimes[i+1]:
            transitions.append({
                'from': regimes[i].name,
                'to': regimes[i+1].name,
                'at_r_ratio': float((ratios[i] + ratios[i+1]) / 2),
            })
    
    return {
        'n_points': len(r_values),
        'r_ratio_range': (float(ratios.min()), float(ratios.max())),
        'regimes_present': list(set(r.name for r in regimes)),
        'n_transitions': len(transitions),
        'transitions': transitions,
        'is_monotonic': all(ratios[i] <= ratios[i+1] for i in range(len(ratios)-1)),
    }
