"""Tests for experimental_xi module."""
import sys
sys.path.insert(0, 'src')

import pytest
import math

from beam_ssz.experimental_xi import (
    xi_deprecated_test_only,
    xi_power_exp_test_only,
    xi_custom_callable,
    compare_against_canonical,
    evaluate_experimental_by_name,
    EXPERIMENTAL_FORMULAS,
    FormulaStatus,
)


def test_deprecated_formula():
    """Test deprecated Xi formula."""
    x = 2.0
    r_phi = 1.0
    
    xi = xi_deprecated_test_only(x, r_phi)
    
    # Should return a value
    assert math.isfinite(xi)
    assert xi > 0


def test_power_exp_formula():
    """Test power-exponential toy formula."""
    x = 2.0
    alpha = 2.0
    beta = 1.0
    
    xi = xi_power_exp_test_only(x, alpha, beta)
    
    assert math.isfinite(xi)
    assert xi > 0


def test_custom_callable():
    """Test custom callable function."""
    x = 2.0
    
    def custom_func(x):
        return 0.5 / x
    
    xi = xi_custom_callable(x, custom_func)
    
    assert xi == 0.25


def test_compare_against_canonical_deprecated():
    """Test comparison against canonical for deprecated formula."""
    x = 2.0
    
    result = compare_against_canonical(
        x,
        lambda x: xi_deprecated_test_only(x),
        "deprecated_test",
        FormulaStatus.DEPRECATED_TEST_ONLY,
    )
    
    assert result.formula_name == "deprecated_test"
    assert result.status == FormulaStatus.DEPRECATED_TEST_ONLY
    assert result.x == x
    assert math.isfinite(result.xi)
    assert math.isfinite(result.canonical_xi)
    assert len(result.warnings) > 0  # Should have deprecation warning


def test_compare_against_canonical_toy():
    """Test comparison against canonical for toy model."""
    x = 2.0
    
    result = compare_against_canonical(
        x,
        lambda x: xi_power_exp_test_only(x, 2.0, 1.0),
        "toy_model",
        FormulaStatus.TOY_MODEL,
    )
    
    assert result.status == FormulaStatus.TOY_MODEL
    assert len(result.warnings) > 0  # Should have toy model warning


def test_evaluate_by_name_deprecated():
    """Test evaluation by name for deprecated formula."""
    x = 2.0
    
    result = evaluate_experimental_by_name(x, "deprecated_power_exp")
    
    assert result.status == FormulaStatus.DEPRECATED_TEST_ONLY
    assert "deprecated" in result.warnings[0].lower()


def test_evaluate_by_name_toy():
    """Test evaluation by name for toy model."""
    x = 2.0
    
    result = evaluate_experimental_by_name(x, "power_exp_alpha2_beta1")
    
    assert result.status == FormulaStatus.TOY_MODEL


def test_evaluate_by_name_invalid():
    """Test evaluation by name with invalid name."""
    with pytest.raises(KeyError):
        evaluate_experimental_by_name(2.0, "nonexistent_formula")


def test_experimental_formulas_dict():
    """Test that experimental formulas dictionary exists and has entries."""
    assert "deprecated_power_exp" in EXPERIMENTAL_FORMULAS
    assert "power_exp_alpha2_beta1" in EXPERIMENTAL_FORMULAS
    assert "power_exp_alpha1_beta05" in EXPERIMENTAL_FORMULAS


def test_comparison_difference_calculation():
    """Test that difference is calculated correctly."""
    x = 2.0
    
    result = compare_against_canonical(
        x,
        lambda x: xi_deprecated_test_only(x),
        "test",
        FormulaStatus.DEPRECATED_TEST_ONLY,
    )
    
    expected_diff = result.xi - result.canonical_xi
    assert abs(result.difference - expected_diff) < 1e-10


def test_comparison_relative_difference():
    """Test that relative difference is calculated correctly."""
    x = 2.0
    
    result = compare_against_canonical(
        x,
        lambda x: xi_power_exp_test_only(x, 1.0, 0.5),
        "test",
        FormulaStatus.TOY_MODEL,
    )
    
    if result.canonical_xi != 0:
        expected_rel_diff = result.difference / result.canonical_xi
        assert abs(result.relative_difference - expected_rel_diff) < 1e-10


def test_negative_xi_warning():
    """Test warning for negative Xi values."""
    x = 2.0
    
    def negative_func(x):
        return -0.1
    
    result = compare_against_canonical(
        x,
        negative_func,
        "negative_test",
        FormulaStatus.TOY_MODEL,
    )
    
    has_negative_warning = any("negative" in w.lower() for w in result.warnings)
    assert has_negative_warning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
