"""Radial scaling coordinate rho for SSZ: d rho = s(r) dr."""
from __future__ import annotations

from .xi import evaluate_d_s_x


def s_of_x(x: float) -> float:
    return evaluate_d_s_x(x)[1]


def rho_between_x(x1: float, x2: float, *, r_s: float = 1.0, steps: int = 2048) -> float:
    """Numerically integrate rho = ∫ s(r) dr = r_s ∫ s(x) dx.

    Uses the trapezoidal rule to keep the project stdlib-only.
    """
    if x1 <= 0 or x2 <= 0 or r_s <= 0:
        raise ValueError("x1, x2, and r_s must be positive")
    if steps < 2:
        raise ValueError("steps must be >= 2")
    if x1 == x2:
        return 0.0
    sign = 1.0
    a, b = x1, x2
    if b < a:
        a, b = b, a
        sign = -1.0
    h = (b - a) / steps
    total = 0.5 * (s_of_x(a) + s_of_x(b))
    for i in range(1, steps):
        total += s_of_x(a + i * h)
    return sign * r_s * h * total


def coordinate_distance_x(x1: float, x2: float, *, r_s: float = 1.0) -> float:
    if r_s <= 0:
        raise ValueError("r_s must be positive")
    return (x2 - x1) * r_s


def segmentation_excess_x(x1: float, x2: float, *, r_s: float = 1.0, steps: int = 2048) -> float:
    """Return ∫(s-1)dr = ∫Xi dr, the excess segmented radial distance."""
    return rho_between_x(x1, x2, r_s=r_s, steps=steps) - coordinate_distance_x(x1, x2, r_s=r_s)
