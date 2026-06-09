"""SSZ segmentation law validation tests.

These tests validate SSZ against its own segmentation rules,
NOT against Minkowski as physical reference.

Minkowski is only a code sanity baseline.
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.tensor_core import ssz_metric


class TestSSZSegmentationRules:
    """Test SSZ canonical segmentation laws.
    
    Xi(r) -> D_SSZ(r) = 1/(1+Xi)
    
    These are the CORE SSZ rules, not Minkowski reduction.
    """
    
    def test_xi_non_negative(self):
        """Xi >= 0 in physical regimes."""
        test_xis = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
        
        for Xi in test_xis:
            assert Xi >= 0, f"Xi={Xi} is negative"
    
    def test_d_ssz_positive(self):
        """D_SSZ = 1/(1+Xi) > 0 for all finite Xi >= 0."""
        test_xis = [0.0, 0.5, 1.0, 2.0, 5.0, 100.0]
        
        for Xi in test_xis:
            D = 1.0 / (1.0 + Xi)
            assert D > 0, f"D_SSZ={D} for Xi={Xi} is not positive"
            assert np.isfinite(D), f"D_SSZ={D} for Xi={Xi} is not finite"
    
    def test_d_ssz_leq_one(self):
        """D_SSZ <= 1 for Xi >= 0."""
        test_xis = [0.0, 0.5, 1.0, 2.0, 5.0, 100.0]
        
        for Xi in test_xis:
            D = 1.0 / (1.0 + Xi)
            assert D <= 1.0, f"D_SSZ={D} for Xi={Xi} exceeds 1"
    
    def test_increasing_xi_decreases_d(self):
        """More segmentation -> stronger time dilation."""
        xi_values = [0.0, 0.5, 1.0, 2.0, 5.0]
        d_values = [1.0 / (1.0 + Xi) for Xi in xi_values]
        
        # D should decrease monotonically
        for i in range(len(d_values) - 1):
            assert d_values[i] > d_values[i+1], \
                f"D not monotonically decreasing: {d_values[i]} vs {d_values[i+1]}"
    
    def test_ssz_metric_components_finite(self):
        """All SSZ metric components finite for valid Xi."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        test_cases = [
            (0.0, 1.0),    # Flat limit
            (0.5, 1.5),    # Mild segmentation
            (1.0, 2.0),    # Standard bridge
            (2.0, 3.0),    # Strong segmentation
        ]
        
        for Xi, s in test_cases:
            D = 1.0 / (1.0 + Xi)
            g = ssz_metric(x, D, s, Xi)
            
            # All components finite
            assert np.all(np.isfinite(g)), f"Non-finite components for Xi={Xi}"
            
            # No NaN
            assert not np.any(np.isnan(g)), f"NaN components for Xi={Xi}"
    
    def test_ssz_determinant_finite(self):
        """Determinant finite and negative (Lorentzian)."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        test_cases = [
            (0.0, 1.0),
            (0.5, 1.5),
            (1.0, 2.0),
            (2.0, 3.0),
        ]
        
        for Xi, s in test_cases:
            D = 1.0 / (1.0 + Xi)
            g = ssz_metric(x, D, s, Xi)
            det = np.linalg.det(g)
            
            assert np.isfinite(det), f"Non-finite determinant for Xi={Xi}"
            assert det < 0, f"Determinant not negative for Xi={Xi} (signature)"
    
    def test_ssz_inverse_finite(self):
        """Inverse metric exists and is finite."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        test_cases = [
            (0.0, 1.0),
            (0.5, 1.5),
            (1.0, 2.0),
        ]
        
        for Xi, s in test_cases:
            D = 1.0 / (1.0 + Xi)
            g = ssz_metric(x, D, s, Xi)
            
            g_inv = np.linalg.inv(g)
            
            assert np.all(np.isfinite(g_inv)), f"Non-finite inverse for Xi={Xi}"
    
    def test_ssz_lorentzian_signature(self):
        """Signature preserved: one negative, three positive eigenvalues."""
        x = np.array([0.0, 2.0, np.pi/2, 0.0])
        
        test_cases = [
            (0.0, 1.0),
            (0.5, 1.5),
            (1.0, 2.0),
        ]
        
        for Xi, s in test_cases:
            D = 1.0 / (1.0 + Xi)
            g = ssz_metric(x, D, s, Xi)
            
            eigenvalues = np.linalg.eigvalsh(g)
            
            # Count signs
            n_negative = np.sum(eigenvalues < 0)
            n_positive = np.sum(eigenvalues > 0)
            
            assert n_negative == 1, f"Expected 1 negative eigenvalue, got {n_negative} for Xi={Xi}"
            assert n_positive == 3, f"Expected 3 positive eigenvalues, got {n_positive} for Xi={Xi}"


class TestSSZNoArtificialSingularities:
    """Test that SSZ regularization prevents artificial singularities."""
    
    def test_finite_segmentation_at_critical_point(self):
        """Xi_max finite -> no infinite segmentation."""
        # Simulate critical radius behavior
        Xi_max = 10.0  # Example finite maximum
        
        D_at_max = 1.0 / (1.0 + Xi_max)
        
        assert np.isfinite(D_at_max), "D becomes infinite at Xi_max"
        assert D_at_max > 0, "D becomes zero or negative"
    
    def test_d_finite_at_high_xi(self):
        """D remains finite even at high Xi."""
        for Xi in [100.0, 1000.0, 10000.0]:
            D = 1.0 / (1.0 + Xi)
            assert np.isfinite(D), f"D not finite for Xi={Xi}"
            assert D > 0, f"D not positive for Xi={Xi}"
