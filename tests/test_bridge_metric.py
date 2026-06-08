"""Tests for bridge_metric module - Core Real-Beaming Solution."""
import sys
sys.path.insert(0, 'src')

import pytest
import math

from beam_ssz.bridge_metric import (
    SSZBridgeMetric,
    create_canonical_bridge,
    evaluate_bridge_candidate,
    BridgeEvaluation,
)


def test_bridge_creation():
    """Test that bridge metric can be created."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    assert bridge.xi_left == 0.1
    assert bridge.xi_right == 0.2
    assert bridge.lambda_bridge == 0.5


def test_weight_function():
    """Test w(u) interpolation function."""
    bridge = create_canonical_bridge()
    
    assert bridge.w(-1.0) == 0.0  # At A
    assert bridge.w(0.0) == 0.5   # Midpoint
    assert bridge.w(1.0) == 1.0   # At B


def test_bridge_profile():
    """Test q(u) bridge profile function."""
    bridge = create_canonical_bridge()
    
    assert bridge.q(-1.0) == 0.0  # Zero at boundaries
    assert bridge.q(1.0) == 0.0
    assert bridge.q(0.0) == 1.0   # Maximum at center
    assert bridge.q(0.5) > 0.0


def test_segment_density():
    """Test Ξ_B(u) segment density."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    # At boundaries
    assert abs(bridge.xi(-1.0) - 0.1) < 1e-10
    assert abs(bridge.xi(1.0) - 0.2) < 1e-10
    
    # With coupling, center should be higher
    xi_center = bridge.xi(0.0)
    assert xi_center > 0.1 and xi_center > 0.2


def test_time_dilation_factor():
    """Test D_B(u) time dilation factor."""
    bridge = create_canonical_bridge()
    
    # D should be positive everywhere
    for u in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        D = bridge.D(u)
        assert D > 0
        assert math.isfinite(D)


def test_radial_scaling():
    """Test s_B(u) radial scaling factor."""
    bridge = create_canonical_bridge()
    
    # s = 1/D should hold
    for u in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        s = bridge.s(u)
        D = bridge.D(u)
        assert abs(s - 1.0/D) < 1e-10


def test_throat_radius():
    """Test R_B(u) throat radius function."""
    bridge = create_canonical_bridge()
    
    # R should be positive
    for u in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        R = bridge.R(u)
        assert R > 0
        assert math.isfinite(R)
    
    # R(u) = R0 * (1 + 0.25 * u^2)
    # At u=0: R(0) = R0
    assert abs(bridge.R(0.0) - bridge.throat_radius) < 1e-10
    # At u=1: R(1) = R0 * 1.25
    assert abs(bridge.R(1.0) - 1.25 * bridge.throat_radius) < 1e-10


def test_metric_tensor():
    """Test metric tensor computation."""
    bridge = create_canonical_bridge()
    
    g = bridge.metric_tensor(0.0, math.pi/2)
    
    # Should be 4x4
    assert len(g) == 4
    assert len(g[0]) == 4
    
    # Should be diagonal
    for i in range(4):
        for j in range(4):
            if i != j:
                assert abs(g[i][j]) < 1e-10
    
    # g_tt should be negative (timelike)
    assert g[0][0] < 0
    
    # Spatial components should be positive
    assert g[1][1] > 0
    assert g[2][2] > 0
    assert g[3][3] > 0


def test_bridge_distance():
    """Test bridge distance calculation."""
    bridge = create_canonical_bridge()
    
    l_bridge = bridge.bridge_distance()
    
    # Should be positive and finite
    assert l_bridge > 0
    assert math.isfinite(l_bridge)
    
    # Should scale with ell0
    bridge2 = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.1,
        lambda_bridge=0.0,
        ell0=2e-3,  # Double
        throat_radius=1e-2,
    )
    l_bridge2 = bridge2.bridge_distance()
    
    # With λ=0, Ξ is constant, so distance should scale with ell0
    ratio = l_bridge2 / l_bridge
    assert abs(ratio - 2.0) < 0.5  # Approximate since Ξ varies slightly


def test_timelike_norm():
    """Test worldline norm calculation."""
    bridge = create_canonical_bridge()
    
    u = 0.0
    du_dtau = 1.0 / bridge.ell0
    dt_dtau = bridge.required_dt_dtau_for_timelike(u, du_dtau)
    
    norm = bridge.timelike_norm(u, dt_dtau, du_dtau)
    
    # Should be close to -c²
    from beam_ssz.constants import C
    assert abs(norm + C**2) < 0.01 * C**2


def test_is_regular():
    """Test regularity check."""
    bridge = create_canonical_bridge()
    
    is_regular, issues = bridge.is_regular()
    
    # Canonical bridge should be regular
    assert is_regular
    assert len(issues) == 0


def test_dxi_du():
    """Test derivative of Ξ_B."""
    bridge = create_canonical_bridge()
    
    # Derivative should exist and be finite
    for u in [-0.5, 0.0, 0.5]:
        dxi = bridge.dxi_du(u)
        assert math.isfinite(dxi)


def test_tidal_proxy():
    """Test tidal acceleration proxy."""
    bridge = create_canonical_bridge()
    
    tidal = bridge.tidal_proxy(0.0)
    
    # Should be finite
    assert math.isfinite(tidal)
    assert tidal >= 0


def test_max_tidal():
    """Test maximum tidal across bridge."""
    bridge = create_canonical_bridge()
    
    max_tidal = bridge.max_tidal_across_bridge()
    
    assert math.isfinite(max_tidal)
    assert max_tidal >= 0


def test_evaluate_candidate():
    """Test full candidate evaluation."""
    bridge = create_canonical_bridge()
    
    result = bridge.evaluate_candidate(l_normal=1.0)
    
    assert isinstance(result, BridgeEvaluation)
    assert result.is_regular == True
    assert math.isfinite(result.distance_ratio)
    assert math.isfinite(result.tidal_proxy)


def test_distance_reduction():
    """Test that bridge can achieve distance reduction."""
    # Strong coupling bridge
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.1,
        lambda_bridge=2.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    
    l_normal = 1.0
    result = bridge.evaluate_candidate(l_normal)
    
    # Should show significant reduction (η < 1)
    assert result.distance_ratio < 1.0
    
    # Should be classified appropriately
    assert result.energy_class in ["SSZ_CANONICAL", "SSZ_EXTENSION", "GR_EXOTIC", "TOY_MODEL"]


def test_evaluate_bridge_candidate():
    """Test the evaluate_bridge_candidate convenience function."""
    bridge = create_canonical_bridge()
    
    passed = evaluate_bridge_candidate(bridge, 1.0, verbose=False)
    
    # Should return boolean
    assert isinstance(passed, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
