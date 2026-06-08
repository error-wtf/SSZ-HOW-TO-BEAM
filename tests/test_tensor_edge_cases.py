"""Edge case tests for tensor calculations."""
import sys
sys.path.insert(0, 'src')

import pytest
import math
import numpy as np

from beam_ssz.tensor import MetricTensor, InverseMetric, RicciScalar, CurvatureInvariants


def test_metric_at_various_radii():
    """Test metric computation at various radii."""
    rs = 1.0
    radii = [1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0]
    
    for r in radii:
        result = MetricTensor.compute(r, rs, math.pi/2)
        assert result.is_finite
        assert result.g_tt < 0
        assert result.g_rr > 0
        assert result.g_thth > 0
        assert result.g_phiphi > 0


def test_metric_near_schwarzschild_radius():
    """Test metric at r = r_s (horizon in GR, but regular in SSZ)."""
    r = 1.0
    rs = 1.0
    theta = math.pi/2
    
    result = MetricTensor.compute(r, rs, theta)
    
    # In SSZ, metric should be finite at r = r_s
    assert result.is_finite
    assert not math.isinf(result.g_tt)
    assert not math.isinf(result.g_rr)
    
    # g_tt should be approximately -0.308 at r_s
    assert abs(result.g_tt - (-0.308)) < 0.01


def test_inverse_metric_determinant():
    """Test that g * g_inv = identity approximately."""
    r = 10.0
    rs = 1.0
    theta = math.pi/2
    
    g = MetricTensor.compute_matrix(r, rs, theta)
    g_inv = InverseMetric.compute_matrix(r, rs, theta)
    
    product = np.dot(g, g_inv)
    
    # Check diagonal elements are close to 1
    for i in range(4):
        assert abs(product[i, i] - 1.0) < 0.1


def test_ricci_scalar_finite_everywhere():
    """Test Ricci scalar is finite for all valid radii."""
    rs = 1.0
    radii = [1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 100.0]
    
    for r in radii:
        result = RicciScalar.compute(r, rs, math.pi/2)
        assert result.is_finite
        assert math.isfinite(result.R)


def test_curvature_invariants_positive():
    """Test that curvature invariants are positive."""
    r = 10.0
    rs = 1.0
    theta = math.pi/2
    
    result = CurvatureInvariants.compute(r, rs, theta)
    
    assert result.is_finite
    # Kretschmann scalar should be positive
    assert result.K > 0


def test_metric_far_field_limit():
    """Test that metric approaches flat spacetime far from source."""
    rs = 1.0
    theta = math.pi/2
    
    # At very large radius
    r = 10000.0
    result = MetricTensor.compute(r, rs, theta)
    
    # g_tt should approach -1
    assert abs(result.g_tt - (-1.0)) < 0.01
    
    # g_rr should approach +1
    assert abs(result.g_rr - 1.0) < 0.01
    
    # Angular components should approach r^2
    assert abs(result.g_thth - r**2) < r**2 * 0.01


def test_metric_spatial_components_scale_correctly():
    """Test that spatial components scale with radius."""
    rs = 1.0
    theta = math.pi/2
    
    r1 = 10.0
    r2 = 20.0
    
    result1 = MetricTensor.compute(r1, rs, theta)
    result2 = MetricTensor.compute(r2, rs, theta)
    
    # Angular components should scale with r^2
    ratio_th = result2.g_thth / result1.g_thth
    expected_ratio = (r2 / r1) ** 2
    assert abs(ratio_th - expected_ratio) < 0.01


def test_determinant_sign():
    """Test that metric determinant has correct sign."""
    rs = 1.0
    theta = math.pi/2
    
    for r in [1.0, 2.0, 5.0, 10.0]:
        result = MetricTensor.compute(r, rs, theta)
        # Determinant should be negative (Lorentzian signature)
        assert result.determinant < 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
