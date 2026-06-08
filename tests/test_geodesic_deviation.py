from math import isfinite

from beam_ssz.geodesic_deviation import radial_curvature_proxy, radial_tidal_acceleration_proxy


def test_radial_curvature_proxy_finite_at_rs():
    value = radial_curvature_proxy(1.0)
    assert isfinite(value)


def test_radial_tidal_proxy_scales_with_separation():
    small = radial_tidal_acceleration_proxy(2.0, 0.5)
    large = radial_tidal_acceleration_proxy(2.0, 1.0)
    assert isfinite(small)
    assert abs(large - 2.0 * small) < 1e-12
