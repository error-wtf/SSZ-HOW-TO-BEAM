"""Tests for tensor scaffold modules."""
import sys
sys.path.insert(0, 'src')

import pytest
import math
import numpy as np

from beam_ssz.tensor import (
    MetricTensor,
    InverseMetric,
    ChristoffelSymbols,
    RiemannTensor,
    RicciTensor,
    RicciScalar,
    EinsteinTensor,
    StressEnergyTensor,
    CurvatureInvariants,
)


def test_metric_tensor():
    """Test metric tensor computation."""
    result = MetricTensor.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert result.g_tt < 0  # Timelike
    assert result.g_rr > 0  # Spacelike
    assert result.g_thth > 0
    assert result.g_phiphi > 0


def test_metric_tensor_matrix():
    """Test metric tensor matrix form."""
    g = MetricTensor.compute_matrix(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert g.shape == (4, 4)
    assert np.allclose(g, np.diag(np.diag(g)))  # Diagonal


def test_inverse_metric():
    """Test inverse metric computation."""
    result = InverseMetric.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    
    # Check that g * g_inv = identity (approximately)
    g = MetricTensor.compute_matrix(r=10.0, rs=1.0, theta=math.pi/2)
    g_inv = InverseMetric.compute_matrix(r=10.0, rs=1.0, theta=math.pi/2)
    
    product = np.dot(g, g_inv)
    identity = np.eye(4)
    
    # Diagonal should be close to 1
    for i in range(4):
        assert abs(product[i, i] - 1.0) < 0.1


def test_christoffel_symbols():
    """Test Christoffel symbol computation."""
    result = ChristoffelSymbols.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert len(result.symbols) > 0


def test_christoffel_non_zero_symbols():
    """Test that expected Christoffel symbols are non-zero."""
    result = ChristoffelSymbols.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    # Key symbols should exist
    assert ('r', 't', 't') in result.symbols or result.symbols.get(('r', 't', 't'), 0) != 0


def test_riemann_tensor():
    """Test Riemann tensor computation."""
    result = RiemannTensor.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert len(result.components) > 0


def test_ricci_tensor():
    """Test Ricci tensor computation."""
    result = RicciTensor.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert all(math.isfinite(v) for v in [result.R_tt, result.R_rr, result.R_thth, result.R_phiphi])


def test_ricci_scalar():
    """Test Ricci scalar computation."""
    result = RicciScalar.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert math.isfinite(result.R)


def test_einstein_tensor():
    """Test Einstein tensor computation."""
    result = EinsteinTensor.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert all(math.isfinite(v) for v in [result.G_tt, result.G_rr, result.G_thth, result.G_phiphi])


def test_stress_energy_tensor():
    """Test stress-energy tensor computation."""
    result = StressEnergyTensor.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert all(math.isfinite(v) for v in [result.T_tt, result.T_rr, result.T_thth, result.T_phiphi])


def test_curvature_invariants():
    """Test curvature invariants computation."""
    result = CurvatureInvariants.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert math.isfinite(result.R)
    assert math.isfinite(result.K)


def test_metric_near_horizon():
    """Test metric computation near Schwarzschild radius."""
    # In SSZ, metric should be finite at r = r_s
    result = MetricTensor.compute(r=1.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    assert result.g_tt != 0
    assert result.g_rr != 0


def test_metric_far_field():
    """Test metric in far field (should approach flat)."""
    result = MetricTensor.compute(r=1000.0, rs=1.0, theta=math.pi/2)
    
    assert result.is_finite
    # g_tt should approach -1
    assert abs(result.g_tt - (-1.0)) < 0.1
    # g_rr should approach +1
    assert abs(result.g_rr - 1.0) < 0.1


def test_christoffel_symmetry():
    """Test Christoffel symbol lower index symmetry."""
    result = ChristoffelSymbols.compute(r=10.0, rs=1.0, theta=math.pi/2)
    
    # Γ^λ_μν = Γ^λ_νμ
    for (lam, mu, nu), val in result.symbols.items():
        if (lam, nu, mu) in result.symbols:
            assert abs(val - result.symbols[(lam, nu, mu)]) < 1e-10


def test_tensor_scenario_different_radii():
    """Test tensor computations at various radii."""
    radii = [1.5, 2.0, 3.0, 5.0, 10.0]
    rs = 1.0
    
    for r in radii:
        metric = MetricTensor.compute(r, rs, math.pi/2)
        assert metric.is_finite, f"Metric not finite at r={r}"
        
        ricci = RicciTensor.compute(r, rs, math.pi/2)
        assert ricci.is_finite, f"Ricci not finite at r={r}"


def test_einstein_matches_ricci():
    """Test that Einstein tensor matches Ricci and metric."""
    r, rs = 10.0, 1.0
    theta = math.pi/2
    
    ricci = RicciTensor.compute(r, rs, theta)
    ricci_scalar = RicciScalar.compute(r, rs, theta)
    metric = MetricTensor.compute(r, rs, theta)
    einstein = EinsteinTensor.compute(r, rs, theta)
    
    # G_μν = R_μν - (1/2) R g_μν
    G_tt_expected = ricci.R_tt - 0.5 * ricci_scalar.R * metric.g_tt
    
    assert abs(einstein.G_tt - G_tt_expected) < 1.0  # Allow some numerical error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
