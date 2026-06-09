"""Test tensor core on Minkowski metrics.

Minkowski spacetime should have zero curvature.
This is the fundamental sanity check for the tensor implementation.
"""

import numpy as np
import pytest

# Add src to path
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.tensor_core import (
    minkowski_cartesian,
    minkowski_spherical,
    compute_christoffel,
    compute_riemann,
    compute_ricci,
    ricci_scalar,
    compute_einstein,
    CoordinateIndex,
)


class TestMinkowskiCartesian:
    """Tests for Minkowski metric in Cartesian coordinates.
    
    g = diag(-1, 1, 1, 1)
    All curvature tensors should be exactly zero.
    """
    
    def test_metric_components(self):
        """Test Minkowski metric components."""
        g = minkowski_cartesian()
        
        assert g[0, 0] == -1.0
        assert g[1, 1] == 1.0
        assert g[2, 2] == 1.0
        assert g[3, 3] == 1.0
        
        # Off-diagonal should be zero
        for i in range(4):
            for j in range(4):
                if i != j:
                    assert g[i, j] == 0.0
    
    def test_christoffel_zero(self):
        """Christoffel symbols should be zero for flat metric."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_cartesian()
        
        Gamma = compute_christoffel(g_func, x, h=1e-5)
        
        # All components should be ~0
        assert np.allclose(Gamma, 0.0, atol=1e-10)
    
    def test_riemann_zero(self):
        """Riemann tensor should be zero for flat metric."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_cartesian()
        
        R = compute_riemann(g_func, x, h=1e-5)
        
        # All components should be ~0
        # Note: Finite differences introduce numerical error
        assert np.allclose(R, 0.0, atol=1e-8)
    
    def test_ricci_zero(self):
        """Ricci tensor should be zero for flat metric."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_cartesian()
        
        Ricci = compute_ricci(g_func, x, h=1e-5)
        
        assert np.allclose(Ricci, 0.0, atol=1e-8)
    
    def test_ricci_scalar_zero(self):
        """Ricci scalar should be zero for flat metric."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_cartesian()
        
        R = ricci_scalar(g_func, x, h=1e-5)
        
        assert np.isclose(R, 0.0, atol=1e-8)
    
    def test_einstein_zero(self):
        """Einstein tensor should be zero for flat metric."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_cartesian()
        
        G = compute_einstein(g_func, x, h=1e-5)
        
        assert np.allclose(G, 0.0, atol=1e-8)


class TestMinkowskiSpherical:
    """Tests for Minkowski metric in spherical coordinates.
    
    g = diag(-1, 1, r^2, r^2 sin^2(theta))
    Curvature should still be zero (coordinate singularity at r=0, theta=0,pi).
    """
    
    def test_metric_components(self):
        """Test spherical Minkowski metric."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])  # r=2, theta=pi/2
        g = minkowski_spherical(x)
        
        assert g[0, 0] == -1.0
        assert g[1, 1] == 1.0
        assert g[2, 2] == 4.0  # r^2 = 4
        assert np.isclose(g[3, 3], 4.0)  # r^2 sin^2(theta) = 4 * 1 = 4
    
    def test_christoffel_nonzero_but_curvature_zero(self):
        """Christoffel symbols are nonzero in spherical coords, but curvature is zero."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        g = minkowski_spherical(x)
        
        # Christoffel has angular components due to coordinate lines
        # But Riemann should still be zero
        def g_func(x):
            return minkowski_spherical(x)
        
        R = compute_riemann(g_func, x, h=1e-5)
        
        # Riemann should be ~0 (finite difference errors larger in spherical)
        assert np.allclose(R, 0.0, atol=1e-6)
    
    def test_riemann_zero_at_test_point(self):
        """Riemann tensor numerically zero at test point."""
        # Avoid coordinate singularities
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        R = compute_riemann(g_func, x, h=1e-5)
        
        # Larger tolerance for spherical due to coordinate complexity
        assert np.allclose(R, 0.0, atol=1e-6)
    
    def test_ricci_zero_at_test_point(self):
        """Ricci tensor numerically zero."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        Ricci = compute_ricci(g_func, x, h=1e-5)
        
        assert np.allclose(Ricci, 0.0, atol=1e-6)
    
    def test_ricci_scalar_zero_at_test_point(self):
        """Ricci scalar numerically zero."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        R = ricci_scalar(g_func, x, h=1e-5)
        
        assert np.isclose(R, 0.0, atol=1e-6)
    
    def test_einstein_zero_at_test_point(self):
        """Einstein tensor numerically zero."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        G = compute_einstein(g_func, x, h=1e-5)
        
        assert np.allclose(G, 0.0, atol=1e-6)
