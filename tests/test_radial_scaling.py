from beam_ssz.radial_scaling import coordinate_distance_x, rho_between_x, segmentation_excess_x


def test_rho_exceeds_coordinate_distance_for_outward_interval():
    coord = coordinate_distance_x(2.2, 10.0)
    rho = rho_between_x(2.2, 10.0, steps=512)
    assert rho > coord
    assert segmentation_excess_x(2.2, 10.0, steps=512) > 0.0


def test_rho_reverses_sign_when_limits_swap():
    a = rho_between_x(3.0, 6.0, steps=256)
    b = rho_between_x(6.0, 3.0, steps=256)
    assert abs(a + b) < 1e-12
