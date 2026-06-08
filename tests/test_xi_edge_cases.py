"""Edge case tests for xi module."""
import sys
sys.path.insert(0, 'src')

import pytest
import math

from beam_ssz.xi import (
    evaluate_xi_x,
    xi_weak_x,
    xi_strong_x,
    XiEvaluation,
    d_ssz_from_xi,
    s_from_xi,
)
from beam_ssz.constants import PHI


def test_xi_very_small_x():
    """Test Xi for very small x (close to singularity)."""
    x = 0.01  # Very close to r = 0
    result = evaluate_xi_x(x)
    
    assert result.xi > 0
    assert math.isfinite(result.xi)
    assert result.regime.value == "very_close"


def test_xi_very_large_x():
    """Test Xi for very large x (far field)."""
    x = 1000.0
    result = evaluate_xi_x(x)
    
    # Xi should be very small
    assert result.xi < 0.01
    assert math.isfinite(result.xi)
    assert result.regime.value == "weak"


def test_xi_at_blend_boundaries():
    """Test Xi at blend zone boundaries."""
    # At x = 1.8 (blend start)
    result_18 = evaluate_xi_x(1.8)
    assert result_18.regime.value == "blended"
    
    # At x = 2.2 (blend end)
    result_22 = evaluate_xi_x(2.2)
    assert result_22.regime.value == "blended"


def test_xi_continuity_at_regime_boundaries():
    """Test that Xi is continuous at regime boundaries."""
    # Check continuity at x = 1.8
    x = 1.8
    eps = 1e-6
    
    xi_left = evaluate_xi_x(x - eps).xi
    xi_blend = evaluate_xi_x(x).xi
    xi_right = evaluate_xi_x(x + eps).xi
    
    # Should be close (within numerical precision)
    assert abs(xi_blend - xi_left) < 0.1
    assert abs(xi_blend - xi_right) < 0.1


def test_xi_weak_formula_correctness():
    """Verify weak field formula."""
    for x in [3.0, 5.0, 10.0, 100.0]:
        expected = 1.0 / (2.0 * x)
        actual = xi_weak_x(x)
        assert abs(actual - expected) < 1e-10


def test_xi_strong_formula_correctness():
    """Verify strong field formula."""
    for x in [0.5, 1.0, 1.5]:
        expected = 1.0 - math.exp(-PHI / x)
        actual = xi_strong_x(x)
        assert abs(actual - expected) < 1e-10


def test_xi_derivatives_finite():
    """Test that derivatives are finite for all valid x."""
    for x in [0.1, 0.5, 1.0, 1.5, 1.9, 2.1, 3.0, 10.0, 100.0]:
        result = evaluate_xi_x(x)
        assert math.isfinite(result.dxi_dx)
        assert math.isfinite(result.d2xi_dx2)


def test_d_ssz_from_xi():
    """Test time dilation factor from Xi."""
    for xi in [0.0, 0.1, 0.5, 1.0, 2.0, 10.0]:
        D = d_ssz_from_xi(xi)
        expected = 1.0 / (1.0 + xi)
        assert abs(D - expected) < 1e-10


def test_s_from_xi():
    """Test radial scaling factor from Xi."""
    for xi in [0.0, 0.1, 0.5, 1.0, 2.0, 10.0]:
        s = s_from_xi(xi)
        expected = 1.0 + xi
        assert abs(s - expected) < 1e-10


def test_xi_d_ssz_s_consistency():
    """Test that D * s = 1 for all Xi."""
    for xi in [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
        D = d_ssz_from_xi(xi)
        s = s_from_xi(xi)
        assert abs(D * s - 1.0) < 1e-10


def test_xi_evaluation_structure():
    """Test that XiEvaluation has correct structure."""
    result = evaluate_xi_x(2.0)
    
    assert isinstance(result, XiEvaluation)
    assert hasattr(result, 'x')
    assert hasattr(result, 'xi')
    assert hasattr(result, 'dxi_dx')
    assert hasattr(result, 'd2xi_dx2')
    assert hasattr(result, 'regime')
    assert hasattr(result, 'formula_domain')
    assert hasattr(result, 'warnings')
    
    assert isinstance(result.x, float)
    assert isinstance(result.xi, float)
    assert isinstance(result.warnings, tuple)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
