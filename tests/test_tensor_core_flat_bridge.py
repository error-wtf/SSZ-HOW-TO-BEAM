"""Test tensor core on flat bridge limit.

Xi=0, lambda=0 should reduce to flat spacetime (no curvature).
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.tensor_core import (
    ssz_metric,
    flat_bridge_limit,
    compute_christoffel,
    compute_riemann,
    compute_ricci,
    ricci_scalar,
    compute_einstein,
)


class TestFlatBridgeLimit:
    """Tests for Xi=0, lambda=0 flat bridge.
    
    Should have D=1, s=1 and produce zero curvature.
    """
    
    def test_flat_parameters(self):
        """Test flat bridge parameters."""
        D, s = flat_bridge_limit()
        
        assert D == 1.0
        assert s == 1.0
    
    def test_metric_equals_minkowski_spherical(self):
        """Flat SSZ metric should equal spherical Minkowski."""
        from beam_ssz.tensor_core import minkowski_spherical
        
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        D, s = flat_bridge_limit()
        g_ssz = ssz_metric(x, D, s)
        g_mink = minkowski_spherical(x)
        
        assert np.allclose(g_ssz, g_mink)
    
    def test_determinant_flat(self):
        """Determinant of flat bridge metric."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        D, s = flat_bridge_limit()
        g = ssz_metric(x, D, s)
        
        det = np.linalg.det(g)
        
        # det = -r^4 sin^2(theta) = -16 * 1 = -16 for r=2, theta=pi/2
        expected = -16.0
        assert np.isclose(det, expected, rtol=1e-10)
    
    def test_riemann_zero_for_flat(self):
        """Flat bridge should have zero Riemann tensor."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            D, s = flat_bridge_limit()
            return ssz_metric(x, D, s)
        
        R = compute_riemann(g_func, x, h=1e-5)
        
        # Should be ~0 (numerical errors)
        assert np.allclose(R, 0.0, atol=1e-6)
    
    def test_ricci_zero_for_flat(self):
        """Flat bridge should have zero Ricci tensor."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            D, s = flat_bridge_limit()
            return ssz_metric(x, D, s)
        
        Ricci = compute_ricci(g_func, x, h=1e-5)
        
        assert np.allclose(Ricci, 0.0, atol=1e-6)
    
    def test_einstein_zero_for_flat(self):
        """Flat bridge should have zero Einstein tensor."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            D, s = flat_bridge_limit()
            return ssz_metric(x, D, s)
        
        G = compute_einstein(g_func, x, h=1e-5)
        
        assert np.allclose(G, 0.0, atol=1e-6)
    
    def test_no_false_curvature(self):
        """Ensure no false curvature is generated for flat case."""
        # Test at multiple points
        test_points = [
            np.array([0.0, 1.0, np.pi/2, 0.0]),
            np.array([0.0, 2.0, np.pi/3, 0.0]),
            np.array([0.0, 5.0, np.pi/4, np.pi/2]),
        ]
        
        for x in test_points:
            def g_func(x):
                D, s = flat_bridge_limit()
                return ssz_metric(x, D, s)
            
            # All curvature tensors should be ~0
            R = compute_riemann(g_func, x, h=1e-5)
            Ricci = compute_ricci(g_func, x, h=1e-5)
            R_scalar = ricci_scalar(g_func, x, h=1e-5)
            G = compute_einstein(g_func, x, h=1e-5)
            
            assert np.allclose(R, 0.0, atol=1e-5), f"Riemann nonzero at {x}"
            assert np.allclose(Ricci, 0.0, atol=1e-5), f"Ricci nonzero at {x}"
            assert np.isclose(R_scalar, 0.0, atol=1e-5), f"R scalar nonzero at {x}"
            assert np.allclose(G, 0.0, atol=1e-5), f"Einstein nonzero at {x}"
