"""Tensor regime classification for SSZ metrics.

Provides functionality to classify metric regimes based on Xi values.
"""

from enum import Enum, auto


class Regime(Enum):
    """Classification of metric regimes based on Xi values."""
    MINKOWSKI = auto()      # Xi = 0
    WEAK_FIELD = auto()     # 0 < Xi < 0.1
    MODERATE = auto()       # 0.1 <= Xi < 1.0
    STRONG = auto()         # 1.0 <= Xi < 10.0
    EXTREME = auto()        # Xi >= 10.0


def classify_regime(Xi: float) -> Regime:
    """Classify the metric regime based on Xi value.
    
    Args:
        Xi: The SSZ segmentation parameter (must be >= 0)
        
    Returns:
        Regime: The classified regime
        
    Raises:
        ValueError: If Xi < 0
    """
    if Xi < 0:
        raise ValueError(f"Xi must be non-negative, got {Xi}")
    
    if Xi == 0:
        return Regime.MINKOWSKI
    elif Xi < 0.1:
        return Regime.WEAK_FIELD
    elif Xi < 1.0:
        return Regime.MODERATE
    elif Xi < 10.0:
        return Regime.STRONG
    else:
        return Regime.EXTREME
