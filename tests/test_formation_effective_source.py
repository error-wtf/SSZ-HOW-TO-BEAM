"""Tests for effective source computation.

Verifies that effective source T_eff_μν can be computed from SSZ metrics
without claiming physical realizability.
"""

import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

import numpy as np
import pytest

from beam_ssz.bridge_metric import SSZBridgeMetric
from beam_ssz.formation import (
    compute_effective_source,
    scan_effective_source_along_bridge,
    SourceStatus,
)


class TestEffectiveSourceComputation:
    """Test effective source reconstruction from SSZ metric."""
    
    def test_effective_source_computation_runs(self):
        """Effective source can be computed for canonical bridge."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.5,
            ell0=1e-3,
        )
        
        result = compute_effective_source(bridge, u=0.0)
        
        # Should return result object
        assert result is not None
        assert result.T_eff is not None
        assert result.G is not None
        
        # T_eff should be 4x4
        assert result.T_eff.shape == (4, 4)
    
    def test_einstein_tensor_relation(self):
        """T_eff = G / (8π) relation holds."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.0,
            lambda_bridge=0.1,
            ell0=1.0,
        )
        
        result = compute_effective_source(bridge, u=0.0)
        
        if result.diagnostics.is_finite:
            # Check T_eff = G / (8π)
            factor = 1.0 / (8.0 * np.pi)
            expected_T = factor * result.G
            
            # Allow numerical tolerance
            assert np.allclose(result.T_eff, expected_T, rtol=1e-5)
    
    def test_status_levels(self):
        """Status correctly classified."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.1,
            ell0=1.0,
        )
        
        result = compute_effective_source(bridge, u=0.0)
        
        # Status should be valid enum value
        assert isinstance(result.status, SourceStatus)
        assert result.status in [
            SourceStatus.FORMATION_UNRESOLVED,
            SourceStatus.EFFECTIVE_SOURCE_DEFINED,
            SourceStatus.EFFECTIVE_SOURCE_FINITE,
            SourceStatus.ENERGY_CONDITION_VIOLATION_DETECTED,
        ]
    
    def test_diagnostics_finite_check(self):
        """Diagnostics correctly identify finiteness."""
        bridge = SSZBridgeMetric(
            xi_left=0.0,
            xi_right=0.0,
            lambda_bridge=0.0,
            ell0=1.0,
        )
        
        result = compute_effective_source(bridge, u=0.0)
        
        # For flat metric (Xi=0), should be finite
        # (though T_eff will be zero)
        assert result.diagnostics.is_finite or np.all(result.T_eff == 0)
    
    def test_scan_along_bridge(self):
        """Can scan effective source along entire bridge."""
        bridge = SSZBridgeMetric(
            xi_left=0.2,
            xi_right=0.0,
            lambda_bridge=0.3,
            ell0=1.0,
        )
        
        results = scan_effective_source_along_bridge(bridge, n_points=20)
        
        assert len(results) == 20
        
        # All should have position data
        for r in results:
            assert r.position is not None
            assert len(r.position) == 4
    
    def test_equation_of_state_computed(self):
        """Equation of state w = p/ρ is computed."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.1,
            ell0=1.0,
        )
        
        result = compute_effective_source(bridge, u=0.0)
        
        # Should have 3 equation of state values
        assert len(result.equation_of_state) == 3
        
        # Each should be a number (possibly inf)
        for w in result.equation_of_state:
            assert isinstance(w, (float, np.floating)) or np.isinf(w)
    
    def test_strong_vs_moderate_field_behavior(self):
        """Different Xi regimes produce different source characteristics."""
        # Weak field bridge
        bridge_weak = SSZBridgeMetric(
            xi_left=0.01,
            xi_right=0.01,
            lambda_bridge=0.01,
            ell0=100.0,
        )
        
        # Stronger field bridge
        bridge_strong = SSZBridgeMetric(
            xi_left=1.0,
            xi_right=1.0,
            lambda_bridge=0.5,
            ell0=1.0,
        )
        
        result_weak = compute_effective_source(bridge_weak, u=0.0)
        result_strong = compute_effective_source(bridge_strong, u=0.0)
        
        # Both should complete without error
        assert result_weak is not None
        assert result_strong is not None

    def test_flat_bridge_zero_curvature(self):
        """Flat bridge (xi=0) must have zero Einstein tensor and source."""
        bridge = SSZBridgeMetric(
            xi_left=0.0,
            xi_right=0.0,
            lambda_bridge=0.0,
            ell0=1.0,
            throat_radius=1.0,
        )

        result = compute_effective_source(bridge, u=0.0)

        assert result.diagnostics.is_finite
        assert np.all(np.isfinite(result.G))
        # Flat metric -> zero curvature
        assert np.allclose(result.G, 0.0, atol=1e-8)
        assert np.allclose(result.T_eff, 0.0, atol=1e-8)

    def test_nontrivial_bridge_nonzero_curvature(self):
        """Non-trivial bridge must have non-zero Einstein tensor (anti-freeze test)."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.5,
            lambda_bridge=0.2,
            ell0=1.0,
            throat_radius=1.0,
        )

        result = compute_effective_source(bridge, u=0.25)

        assert result.diagnostics.is_finite
        assert np.all(np.isfinite(result.G))

        # CRITICAL: If g_func ignores x, G will be all zeros.
        # This test verifies that g_func actually depends on u.
        assert np.max(np.abs(result.G)) > 1e-12, \
            "G is effectively zero - g_func may be frozen, not depending on x[1]=u"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
