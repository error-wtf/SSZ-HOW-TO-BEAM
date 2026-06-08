"""Experimental Xi formulas playground.

This module provides a sandbox for testing alternative Xi formulas.
All non-canonical formulas must be explicitly labeled with their status.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import exp
from typing import Callable

from .xi import XiEvaluation, evaluate_xi_x


class FormulaStatus(str, Enum):
    """Status labels for Xi formulas."""
    CANONICAL = "CANONICAL"
    EXPERIMENTAL = "EXPERIMENTAL"
    DEPRECATED_TEST_ONLY = "DEPRECATED_TEST_ONLY"
    TOY_MODEL = "TOY_MODEL"


@dataclass(frozen=True)
class ExperimentalXiResult:
    """Result from experimental Xi evaluation."""
    formula_name: str
    status: FormulaStatus
    x: float
    xi: float
    canonical_xi: float
    difference: float
    relative_difference: float
    warnings: tuple[str, ...]


def xi_deprecated_test_only(x: float, r_phi: float = 1.0) -> float:
    """DEPRECATED formula: Xi = (r_s/r)^2 * exp(-r/r_phi).
    
    This formula is FORBIDDEN in canonical SSZ calculations.
    It is provided here only for comparison and testing purposes.
    
    Args:
        x: Dimensionless radius r / r_s
        r_phi: Characteristic radius scale (default 1.0 in units of r_s)
        
    Returns:
        Xi value (DEPRECATED)
    """
    return (1.0 / x) ** 2 * exp(-x / r_phi)


def xi_power_exp_test_only(x: float, alpha: float = 2.0, beta: float = 1.0) -> float:
    """Experimental power-exponential form: Xi = x^(-alpha) * exp(-beta*x).
    
    This is a toy model for testing alternative functional forms.
    
    Args:
        x: Dimensionless radius r / r_s
        alpha: Power law exponent
        beta: Exponential decay rate
        
    Returns:
        Xi value (TOY MODEL)
    """
    return x ** (-alpha) * exp(-beta * x)


def xi_custom_callable(x: float, func: Callable[[float], float]) -> float:
    """Evaluate a custom Xi function.
    
    Args:
        x: Dimensionless radius r / r_s
        func: Custom function of x returning Xi
        
    Returns:
        Xi value from custom function
    """
    return func(x)


def compare_against_canonical(
    x: float,
    experimental_func: Callable[[float], float],
    formula_name: str,
    status: FormulaStatus,
) -> ExperimentalXiResult:
    """Compare an experimental Xi formula against canonical SSZ.
    
    Args:
        x: Dimensionless radius r / r_s
        experimental_func: Experimental Xi function
        formula_name: Name of the experimental formula
        status: Status label for the formula
        
    Returns:
        ExperimentalXiResult with comparison data
    """
    canonical_ev = evaluate_xi_x(x)
    experimental_xi = experimental_func(x)
    
    difference = experimental_xi - canonical_ev.xi
    if canonical_ev.xi != 0:
        relative_difference = difference / canonical_ev.xi
    else:
        relative_difference = float('inf') if difference != 0 else 0.0
    
    warnings: list[str] = []
    if status == FormulaStatus.DEPRECATED_TEST_ONLY:
        warnings.append("This formula is deprecated and forbidden in canonical SSZ")
    if status == FormulaStatus.TOY_MODEL:
        warnings.append("This is a toy model for testing only")
    if experimental_xi < 0:
        warnings.append("Xi is negative: violates non-negativity requirement")
    if experimental_xi > 1.0 and x > 1.0:
        warnings.append("Xi > 1 for x > 1: unusual behavior")
    
    return ExperimentalXiResult(
        formula_name=formula_name,
        status=status,
        x=x,
        xi=experimental_xi,
        canonical_xi=canonical_ev.xi,
        difference=difference,
        relative_difference=relative_difference,
        warnings=tuple(warnings),
    )


# Pre-configured experimental formulas for easy access
EXPERIMENTAL_FORMULAS = {
    "deprecated_power_exp": (
        lambda x: xi_deprecated_test_only(x),
        FormulaStatus.DEPRECATED_TEST_ONLY,
    ),
    "power_exp_alpha2_beta1": (
        lambda x: xi_power_exp_test_only(x, alpha=2.0, beta=1.0),
        FormulaStatus.TOY_MODEL,
    ),
    "power_exp_alpha1_beta05": (
        lambda x: xi_power_exp_test_only(x, alpha=1.0, beta=0.5),
        FormulaStatus.TOY_MODEL,
    ),
}


def evaluate_experimental_by_name(
    x: float,
    formula_name: str,
) -> ExperimentalXiResult:
    """Evaluate a pre-configured experimental formula by name.
    
    Args:
        x: Dimensionless radius r / r_s
        formula_name: Name of the experimental formula
        
    Returns:
        ExperimentalXiResult with comparison data
        
    Raises:
        KeyError: If formula_name is not found
    """
    if formula_name not in EXPERIMENTAL_FORMULAS:
        raise KeyError(f"Unknown experimental formula: {formula_name}")
    
    func, status = EXPERIMENTAL_FORMULAS[formula_name]
    return compare_against_canonical(x, func, formula_name, status)
