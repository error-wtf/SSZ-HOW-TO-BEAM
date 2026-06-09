"""Canonical SSZ implementation aligned with ssz-complete-documentation.

This module provides the canonical SSZ formulas as defined in the
reference repository: https://github.com/error-wtf/ssz-complete-documentation

Core Principle: Canonical formulas only - no toy normalizations as default.
"""

from .xi import (
    PHI,
    xi_weak,
    xi_strong,
    xi_blend,
    xi_canonical,
    XI_HORIZON,
    D_HORIZON,
)
from .regimes import (
    classify_regime,
    Regime,
    REGIME_BOUNDARIES,
)
from .scaling import (
    d_ssz,
    s_ssz,
)
from .method_assignment import (
    ObservableClass,
    Method,
    assign_method,
    validate_observable_method,
)
from .deprecated_guards import (
    detect_deprecated_formula,
    DeprecatedFormulaError,
)

__all__ = [
    # Constants
    'PHI',
    'XI_HORIZON',
    'D_HORIZON',
    # Xi functions
    'xi_weak',
    'xi_strong',
    'xi_blend',
    'xi_canonical',
    # Regimes
    'classify_regime',
    'Regime',
    'REGIME_BOUNDARIES',
    # Scaling
    'd_ssz',
    's_ssz',
    # Method assignment
    'ObservableClass',
    'Method',
    'assign_method',
    'validate_observable_method',
    # Guards
    'detect_deprecated_formula',
    'DeprecatedFormulaError',
]
