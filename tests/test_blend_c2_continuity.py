from math import isclose

from beam_ssz.xi import (
    d2xi_strong_dx2,
    d2xi_weak_dx2,
    dxi_strong_dx,
    dxi_weak_dx,
    evaluate_xi_x,
    xi_strong_x,
    xi_weak_x,
)


def test_blend_matches_strong_boundary_c2():
    x = 1.8
    ev = evaluate_xi_x(x)
    assert isclose(ev.xi, xi_strong_x(x), rel_tol=1e-12, abs_tol=1e-12)
    assert isclose(ev.dxi_dx, dxi_strong_dx(x), rel_tol=1e-12, abs_tol=1e-12)
    assert isclose(ev.d2xi_dx2, d2xi_strong_dx2(x), rel_tol=1e-11, abs_tol=1e-11)


def test_blend_matches_weak_boundary_c2():
    x = 2.2
    ev = evaluate_xi_x(x)
    assert isclose(ev.xi, xi_weak_x(x), rel_tol=1e-12, abs_tol=1e-12)
    assert isclose(ev.dxi_dx, dxi_weak_dx(x), rel_tol=1e-12, abs_tol=1e-12)
    assert isclose(ev.d2xi_dx2, d2xi_weak_dx2(x), rel_tol=1e-11, abs_tol=1e-11)


def test_blend_monotonic_decreasing_sampled():
    previous = None
    for i in range(401):
        x = 1.8 + 0.4 * i / 400
        ev = evaluate_xi_x(x)
        if previous is not None:
            assert ev.xi <= previous + 1e-12
        previous = ev.xi
