from math import isclose, sqrt

from beam_ssz.constants import C, D_RS
from beam_ssz.geodesics import (
    constants_for_rest_at_infinity,
    dt_dtau,
    four_velocity_norm_radial,
    radial_dr_dtau_squared,
    radial_freefall_velocity,
)


def test_radial_freefall_velocity_at_rs_matches_documented_value():
    v = radial_freefall_velocity(1.0, c=1.0)
    assert isclose(v, sqrt(1.0 - D_RS * D_RS), rel_tol=2e-4)
    assert 0.82 < v < 0.84


def test_radial_timelike_norm_for_rest_at_infinity():
    c = 1.0
    x = 3.0
    constants = constants_for_rest_at_infinity(c=c)
    dr2 = radial_dr_dtau_squared(x, constants, r_s=1.0)
    assert dr2 >= 0.0
    norm = four_velocity_norm_radial(x, sqrt(dr2), dt_dtau(x, c=c), c=c)
    assert isclose(norm, -c * c, rel_tol=1e-10, abs_tol=1e-10)
