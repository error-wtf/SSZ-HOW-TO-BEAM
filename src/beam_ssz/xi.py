"""Canonical Xi engine with analytic derivatives.

All public evaluation functions use the dimensionless radius x = r / r_s.
Derivatives returned by :func:`evaluate_xi_x` are with respect to x. Convert to
r-derivatives via dXi/dr = (dXi/dx)/r_s and d²Xi/dr² = (d²Xi/dx²)/r_s².
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Tuple

from .constants import PHI, X_BLEND_MAX, X_BLEND_MIN
from .regimes import Regime, classify_regime


@dataclass(frozen=True)
class XiEvaluation:
    x: float
    xi: float
    dxi_dx: float
    d2xi_dx2: float
    regime: Regime
    formula_domain: str
    warnings: tuple[str, ...] = ()


def xi_weak_x(x: float) -> float:
    _validate_x(x)
    return 1.0 / (2.0 * x)


def dxi_weak_dx(x: float) -> float:
    _validate_x(x)
    return -1.0 / (2.0 * x * x)


def d2xi_weak_dx2(x: float) -> float:
    _validate_x(x)
    return 1.0 / (x**3)


def xi_strong_x(x: float) -> float:
    _validate_x(x)
    return 1.0 - exp(-PHI / x)


def dxi_strong_dx(x: float) -> float:
    _validate_x(x)
    return -exp(-PHI / x) * PHI / (x**2)


def d2xi_strong_dx2(x: float) -> float:
    _validate_x(x)
    e = exp(-PHI / x)
    return e * (2.0 * PHI / (x**3) - (PHI**2) / (x**4))


def _validate_x(x: float) -> None:
    if not isfinite(x) or x <= 0:
        raise ValueError("x=r/r_s must be finite and positive")


def _solve_3x3(a: list[list[float]], b: list[float]) -> tuple[float, float, float]:
    """Tiny Gaussian solver for deterministic stdlib-only Hermite coefficients."""
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    n = 3
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-15:
            raise ArithmeticError("singular Hermite coefficient system")
        m[col], m[pivot] = m[pivot], m[col]
        scale = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= scale
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            for j in range(col, n + 1):
                m[r][j] -= factor * m[col][j]
    return (m[0][3], m[1][3], m[2][3])


def _hermite_coefficients() -> Tuple[float, float, float, float, float, float]:
    x0, x1 = X_BLEND_MIN, X_BLEND_MAX
    dx = x1 - x0
    f0 = xi_strong_x(x0)
    fp0 = dxi_strong_dx(x0) * dx
    fpp0 = d2xi_strong_dx2(x0) * dx * dx
    f1 = xi_weak_x(x1)
    fp1 = dxi_weak_dx(x1) * dx
    fpp1 = d2xi_weak_dx2(x1) * dx * dx

    a0 = f0
    a1 = fp0
    a2 = 0.5 * fpp0
    r0 = f1 - (a0 + a1 + a2)
    r1 = fp1 - (a1 + 2.0 * a2)
    r2 = fpp1 - (2.0 * a2)
    a3, a4, a5 = _solve_3x3(
        [[1.0, 1.0, 1.0], [3.0, 4.0, 5.0], [6.0, 12.0, 20.0]],
        [r0, r1, r2],
    )
    return a0, a1, a2, a3, a4, a5


_HERMITE = _hermite_coefficients()


def xi_blend_x(x: float) -> float:
    return _eval_blend(x)[0]


def dxi_blend_dx(x: float) -> float:
    return _eval_blend(x)[1]


def d2xi_blend_dx2(x: float) -> float:
    return _eval_blend(x)[2]


def _eval_blend(x: float) -> tuple[float, float, float]:
    _validate_x(x)
    if not (X_BLEND_MIN <= x <= X_BLEND_MAX):
        raise ValueError("blend formula only valid for 1.8 <= x <= 2.2")
    a0, a1, a2, a3, a4, a5 = _HERMITE
    dx = X_BLEND_MAX - X_BLEND_MIN
    t = (x - X_BLEND_MIN) / dx
    value = a0 + a1*t + a2*t**2 + a3*t**3 + a4*t**4 + a5*t**5
    dp_dt = a1 + 2*a2*t + 3*a3*t**2 + 4*a4*t**3 + 5*a5*t**4
    d2p_dt2 = 2*a2 + 6*a3*t + 12*a4*t**2 + 20*a5*t**3
    return value, dp_dt / dx, d2p_dt2 / (dx * dx)


def evaluate_xi_x(x: float) -> XiEvaluation:
    """Evaluate canonical Xi and derivatives for dimensionless x=r/r_s."""
    info = classify_regime(x)
    warnings: list[str] = []
    if info.regime == Regime.VERY_CLOSE:
        xi, dx1, dx2 = xi_strong_x(x), dxi_strong_dx(x), d2xi_strong_dx2(x)
    elif info.regime == Regime.BLENDED:
        xi, dx1, dx2 = _eval_blend(x)
    else:
        xi, dx1, dx2 = xi_weak_x(x), dxi_weak_dx(x), d2xi_weak_dx2(x)
        if info.regime in {Regime.PHOTON_SPHERE, Regime.STRONG}:
            warnings.append("physical strong/photon regime uses g1 formula domain in canonical calculators")
    if xi < -1e-15:
        warnings.append("Xi below zero: violates canonical non-negative field")
    return XiEvaluation(x, xi, dx1, dx2, info.regime, info.formula_domain, tuple(warnings))


def d_ssz_from_xi(xi: float) -> float:
    if xi < 0:
        raise ValueError("Xi must be non-negative")
    return 1.0 / (1.0 + xi)


def s_from_xi(xi: float) -> float:
    if xi < 0:
        raise ValueError("Xi must be non-negative")
    return 1.0 + xi


def evaluate_d_s_x(x: float) -> tuple[float, float, XiEvaluation]:
    ev = evaluate_xi_x(x)
    return d_ssz_from_xi(ev.xi), s_from_xi(ev.xi), ev


def forbidden_deprecated_xi(*_: object, **__: object) -> None:
    """Hard fail for the deprecated formula Xi=(rs/r)^2 exp(-r/r_phi)."""
    raise RuntimeError("Deprecated Xi formula is forbidden in BEAM-SSZ and canonical SSZ calculations")
