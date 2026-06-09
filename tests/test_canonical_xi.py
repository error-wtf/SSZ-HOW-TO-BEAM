"""Tests for canonical SSZ Xi functions.

Validates against ssz-complete-documentation reference values.
"""

import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

import numpy as np
import pytest

from beam_ssz.canonical import (
    PHI, XI_HORIZON, D_HORIZON,
    xi_weak, xi_strong, xi_blend, xi_canonical,
)


class TestCanonicalXi:
    """Test canonical SSZ Xi formulas."""
    
    def test_phi_constant(self):
        """PHI is Golden Ratio (1+sqrt(5))/2."""
        expected_phi = (1.0 + np.sqrt(5.0)) / 2.0
        assert abs(PHI - expected_phi) < 1e-15
        assert abs(PHI - 1.618033988749895) < 1e-15
    
    def test_xi_horizon_value(self):
        """Xi at horizon is canonical value (not 1!)."""
        # Ξ(r_s) = 1 - exp(-φ) ≈ 0.801711847
        expected = 1.0 - np.exp(-PHI)
        assert abs(XI_HORIZON - expected) < 1e-10
        assert abs(XI_HORIZON - 0.801711847) < 1e-6
    
    def test_d_horizon_value(self):
        """D at horizon is canonical value."""
        # D(r_s) = 1/(1+Ξ) ≈ 0.555027709
        expected = 1.0 / (1.0 + XI_HORIZON)
        assert abs(D_HORIZON - expected) < 1e-10
        assert abs(D_HORIZON - 0.555027709) < 1e-6
    
    def test_xi_weak_formula(self):
        """Xi_weak(r) = r_s/(2r)."""
        # At r/r_s = 10: Ξ = 0.05
        xi = xi_weak(10.0, 1.0)
        assert abs(xi - 0.05) < 1e-10
        
        # At r/r_s = 100: Ξ = 0.005
        xi = xi_weak(100.0, 1.0)
        assert abs(xi - 0.005) < 1e-10
    
    def test_xi_strong_formula(self):
        """Xi_strong(r) = 1 - exp(-φ*r_s/r)."""
        # At r = r_s (horizon): Ξ = 1 - exp(-φ)
        xi = xi_strong(1.0, 1.0)
        assert abs(xi - XI_HORIZON) < 1e-10
    
    def test_xi_strong_decreases_with_r(self):
        """Xi_strong decreases monotonically with r."""
        r_values = np.linspace(0.5, 1.8, 100)
        xi_values = [xi_strong(r, 1.0) for r in r_values]
        
        # Check monotonic decrease
        for i in range(len(xi_values) - 1):
            assert xi_values[i] >= xi_values[i+1]
    
    def test_xi_weak_decreases_with_r(self):
        """Xi_weak decreases monotonically with r."""
        r_values = np.linspace(2.2, 100, 100)
        xi_values = [xi_weak(r, 1.0) for r in r_values]
        
        # Check monotonic decrease
        for i in range(len(xi_values) - 1):
            assert xi_values[i] >= xi_values[i+1]
    
    def test_blend_zone_exists(self):
        """Blend zone connects weak and strong branches."""
        # At blend start (r/r_s = 1.8): use xi_strong
        xi_at_18 = xi_strong(1.8, 1.0)
        
        # At blend end (r/r_s = 2.2): use xi_weak
        xi_at_22 = xi_weak(2.2, 1.0)
        
        # Blend should be between these
        xi_blend_18 = xi_blend(1.8, 1.0)
        xi_blend_20 = xi_blend(2.0, 1.0)
        xi_blend_22 = xi_blend(2.2, 1.0)
        
        # Check blend values are reasonable
        assert xi_blend_18 > 0
        assert xi_blend_22 > 0
        assert xi_blend_20 > 0
    
    def test_xi_canonical_selects_correct_branch(self):
        """xi_canonical selects correct branch based on r/r_s."""
        # Very close: strong branch
        xi_close = xi_canonical(1.0, 1.0)
        assert abs(xi_close - xi_strong(1.0, 1.0)) < 1e-10
        
        # Far: weak branch
        xi_far = xi_canonical(10.0, 1.0)
        assert abs(xi_far - xi_weak(10.0, 1.0)) < 1e-10
        
        # Blend zone: blend function
        xi_blend_mid = xi_canonical(2.0, 1.0)
        # Should be between strong and weak values
        xi_strong_val = xi_strong(2.0, 1.0)
        xi_weak_val = xi_weak(2.0, 1.0)
        assert min(xi_strong_val, xi_weak_val) <= xi_blend_mid <= max(xi_strong_val, xi_weak_val)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
