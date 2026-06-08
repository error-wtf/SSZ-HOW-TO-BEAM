from beam_ssz.effective_potential import potential_curvature, potential_gradient
from beam_ssz.geodesics import effective_potential


def test_effective_potential_positive():
    assert effective_potential(3.0, angular_momentum=0.0, c=1.0) > 0.0
    assert effective_potential(3.0, angular_momentum=2.0, c=1.0) > effective_potential(3.0, angular_momentum=0.0, c=1.0)


def test_potential_derivatives_are_finite():
    assert abs(potential_gradient(4.0, angular_momentum=1.0, c=1.0)) < 10.0
    assert abs(potential_curvature(4.0, angular_momentum=1.0, c=1.0)) < 10.0
