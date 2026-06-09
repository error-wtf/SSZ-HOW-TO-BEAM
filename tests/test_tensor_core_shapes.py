"""Test tensor shapes and symmetries.

Verifies that all tensors have correct shapes and required symmetries.
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.tensor_core import (
    minkowski_cartesian,
    minkowski_spherical,
    compute_christoffel,
    compute_riemann,
    compute_ricci,
    compute_einstein,
)


class TestTensorShapes:
    """Verify tensor shapes are correct."""
    
    def test_metric_shape(self):
        """Metric should be 4x4."""
        g = minkowski_cartesian()
        assert g.shape == (4, 4)
    
    def test_christoffel_shape(self):
        """Christoffel should be 4x4x4."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        Gamma = compute_christoffel(g_func, x, h=1e-5)
        assert Gamma.shape == (4, 4, 4)
    
    def test_riemann_shape(self):
        """Riemann should be 4x4x4x4."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        R = compute_riemann(g_func, x, h=1e-5)
        assert R.shape == (4, 4, 4, 4)
    
    def test_ricci_shape(self):
        """Ricci should be 4x4."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        Ricci = compute_ricci(g_func, x, h=1e-5)
        assert Ricci.shape == (4, 4)
    
    def test_einstein_shape(self):
        """Einstein should be 4x4."""
        x = np.array([0.0, 1.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        G = compute_einstein(g_func, x, h=1e-5)
        assert G.shape == (4, 4)


class TestMetricSymmetries:
    """Test metric and tensor symmetries."""
    
    def test_metric_symmetric(self):
        """Metric should be symmetric."""
        g = minkowski_cartesian()
        assert np.allclose(g, g.T)
    
    def test_christoffel_lower_symmetric(self):
        """Christoffel should be symmetric in lower indices."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        Gamma = compute_christoffel(g_func, x, h=1e-5)
        
        # Gamma[lam, mu, nu] == Gamma[lam, nu, mu]
        for lam in range(4):
            for mu in range(4):
                for nu in range(4):
                    assert np.isclose(
                        Gamma[lam, mu, nu],
                        Gamma[lam, nu, mu],
                        atol=1e-10
                    ), f"Christoffel not symmetric at [{lam},{mu},{nu}]"
    
    def test_ricci_symmetric(self):
        """Ricci tensor should be symmetric."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        Ricci = compute_ricci(g_func, x, h=1e-5)
        
        assert np.allclose(Ricci, Ricci.T, atol=1e-10)
    
    def test_einstein_symmetric(self):
        """Einstein tensor should be symmetric."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        G = compute_einstein(g_func, x, h=1e-5)
        
        assert np.allclose(G, G.T, atol=1e-10)
    
    def test_riemann_antisymmetric_last_two(self):
        """Riemann should be antisymmetric in last two indices."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        def g_func(x):
            return minkowski_spherical(x)
        
        R = compute_riemann(g_func, x, h=1e-5)
        
        # R[rho, sigma, mu, nu] == -R[rho, sigma, nu, mu]
        for rho in range(4):
            for sigma in range(4):
                for mu in range(4):
                    for nu in range(4):
                        val = R[rho, sigma, mu, nu]
                        swapped = R[rho, sigma, nu, mu]
                        assert np.isclose(val, -swapped, atol=1e-8), \
                            f"Riemann not antisymmetric at [{rho},{sigma},{mu},{nu}]"
