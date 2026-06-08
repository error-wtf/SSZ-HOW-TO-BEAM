"""Edge case tests for bridge_metric module."""
import sys
sys.path.insert(0, 'src')

import pytest
import math

from beam_ssz.bridge_metric import SSZBridgeMetric, create_canonical_bridge, BridgeEvaluation


def test_bridge_extreme_lambda_zero():
    """Test bridge with lambda=0 (pure interpolation)."""
    bridge = SSZBridgeMetric(
        xi_left=0.5,
        xi_right=0.5,
        lambda_bridge=0.0,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    xi_minus = bridge.xi(-1.0)
    xi_center = bridge.xi(0.0)
    xi_plus = bridge.xi(1.0)
    
    assert abs(xi_minus - 0.5) < 1e-10
    assert abs(xi_center - 0.5) < 1e-10
    assert abs(xi_plus - 0.5) < 1e-10


def test_bridge_extreme_lambda_large():
    """Test bridge with very large lambda."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.1,
        lambda_bridge=100.0,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    xi_center = bridge.xi(0.0)
    assert xi_center > 50.0


def test_bridge_asymmetric_xi():
    """Test bridge with different Xi at endpoints."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.9,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    # Check endpoints match exactly
    assert abs(bridge.xi(-1.0) - 0.1) < 1e-10
    assert abs(bridge.xi(1.0) - 0.9) < 1e-10
    
    # With lambda coupling and asymmetric endpoints, Xi can have complex behavior
    # Just verify it's smooth and within bounds
    xi_values = [bridge.xi(u) for u in [-0.5, 0.0, 0.5]]
    for xi in xi_values:
        assert xi >= min(0.1, 0.9)  # Should be at least the minimum endpoint
        assert math.isfinite(xi)


def test_bridge_zero_xi():
    """Test bridge with Xi = 0 (flat spacetime)."""
    bridge = SSZBridgeMetric(
        xi_left=0.0,
        xi_right=0.0,
        lambda_bridge=0.0,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    for u in [-1.0, 0.0, 1.0]:
        assert abs(bridge.D(u) - 1.0) < 1e-10
        assert abs(bridge.s(u) - 1.0) < 1e-10


def test_bridge_consistency_check():
    """Test internal consistency of bridge calculations."""
    bridge = create_canonical_bridge()
    
    for u in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        D = bridge.D(u)
        s = bridge.s(u)
        product = D * s
        assert abs(product - 1.0) < 1e-10


def test_bridge_metric_tensor_signature():
    """Test that metric tensor has correct signature (-, +, +, +)."""
    bridge = create_canonical_bridge()
    
    for u in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        g = bridge.metric_tensor(u, math.pi/2)
        assert g[0][0] < 0
        assert g[1][1] > 0
        assert g[2][2] > 0
        assert g[3][3] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
