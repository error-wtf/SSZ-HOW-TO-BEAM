"""Tests for constants and canonical formulas."""
import sys
sys.path.insert(0, 'src')

import pytest
import math

from beam_ssz.constants import (
    PHI,
    XI_RS,
    D_RS,
    C,
    G,
    X_BLEND_MIN,
    X_BLEND_MAX,
)


def test_phi_golden_ratio():
    """Test that PHI is the golden ratio."""
    expected_phi = (1.0 + math.sqrt(5.0)) / 2.0
    assert abs(PHI - expected_phi) < 1e-15


def test_phi_value():
    """Test PHI has expected value."""
    assert abs(PHI - 1.618033988749895) < 1e-15


def test_xi_rs_calculation():
    """Test XI_RS is correctly calculated from PHI."""
    expected = 1.0 - math.exp(-PHI)
    assert abs(XI_RS - expected) < 1e-15
    assert abs(XI_RS - 0.801712) < 0.001


def test_d_rs_calculation():
    """Test D_RS is correctly calculated from XI_RS."""
    expected = 1.0 / (1.0 + XI_RS)
    assert abs(D_RS - expected) < 1e-15
    assert abs(D_RS - 0.555) < 0.001


def test_speed_of_light_value():
    """Test C is the speed of light in m/s."""
    assert C == 299792458.0
    assert C > 299792000.0
    assert C < 299793000.0


def test_gravitational_constant_value():
    """Test G is the gravitational constant."""
    assert G == 6.67430e-11
    assert G > 6.6e-11
    assert G < 6.7e-11


def test_blend_boundaries():
    """Test blend zone boundaries."""
    assert X_BLEND_MIN == 1.8
    assert X_BLEND_MAX == 2.2
    assert X_BLEND_MAX > X_BLEND_MIN


def test_xi_rs_is_positive():
    """Test XI_RS is positive."""
    assert XI_RS > 0


def test_d_rs_is_positive():
    """Test D_RS is positive."""
    assert D_RS > 0


def test_d_rs_less_than_one():
    """Test D_RS is less than 1."""
    assert D_RS < 1.0


def test_phi_greater_than_one():
    """Test PHI is greater than 1."""
    assert PHI > 1.0


def test_physical_constants_consistency():
    """Test that physical constants are self-consistent."""
    # G * C should be very small
    gc = G * C
    assert gc < 1.0
    assert gc > 0.0
    
    # C / G should be very large
    c_over_g = C / G
    assert c_over_g > 1e18


def test_blend_zone_width():
    """Test blend zone has expected width."""
    width = X_BLEND_MAX - X_BLEND_MIN
    assert abs(width - 0.4) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
