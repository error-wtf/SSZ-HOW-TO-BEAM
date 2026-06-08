from math import exp, isclose

import pytest

from beam_ssz.constants import PHI
from beam_ssz.regimes import Regime, classify_regime
from beam_ssz.xi import (
    d2xi_strong_dx2,
    d2xi_weak_dx2,
    dxi_strong_dx,
    dxi_weak_dx,
    evaluate_d_s_x,
    evaluate_xi_x,
    forbidden_deprecated_xi,
    xi_strong_x,
    xi_weak_x,
)


def test_xi_at_rs_canonical():
    ev = evaluate_xi_x(1.0)
    assert isclose(ev.xi, 1.0 - exp(-PHI), rel_tol=1e-12)
    D, s, _ = evaluate_d_s_x(1.0)
    assert isclose(D, 1.0 / (1.0 + ev.xi), rel_tol=1e-12)
    assert isclose(s, 1.0 + ev.xi, rel_tol=1e-12)


def test_weak_branch_formula():
    assert isclose(xi_weak_x(10.0), 0.05)
    assert dxi_weak_dx(10.0) < 0
    assert d2xi_weak_dx2(10.0) > 0


def test_strong_branch_monotonic_derivative():
    assert xi_strong_x(1.0) > xi_strong_x(1.7)
    assert dxi_strong_dx(1.2) < 0
    assert d2xi_strong_dx2(1.2) > 0


def test_regime_boundaries():
    assert classify_regime(1.0).regime == Regime.VERY_CLOSE
    assert classify_regime(2.0).regime == Regime.BLENDED
    assert classify_regime(2.5).regime == Regime.PHOTON_SPHERE
    assert classify_regime(5.0).regime == Regime.STRONG
    assert classify_regime(11.0).regime == Regime.WEAK


def test_forbidden_formula_hard_fail():
    with pytest.raises(RuntimeError):
        forbidden_deprecated_xi(1, 2, 3)
