"""Radial null geodesic and light-travel time helpers in SSZ."""
from __future__ import annotations

from .constants import C
from .xi import evaluate_d_s_x


def dt_dr_null(x: float, *, c: float = C) -> float:
    """Return dt/dr for radial light: c dt = ± dr/D², positive branch."""
    D = evaluate_d_s_x(x)[0]
    return 1.0 / (D * D * c)


def light_travel_time_x(x1: float, x2: float, *, r_s: float = 1.0, c: float = C, steps: int = 4096) -> float:
    """Return Δt = r_s ∫ dx/(D(x)^2 c), trapezoidal rule."""
    if x1 <= 0 or x2 <= 0 or r_s <= 0 or c <= 0:
        raise ValueError("x1, x2, r_s, and c must be positive")
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
    total = 0.5 * (dt_dr_null(a, c=c) + dt_dr_null(b, c=c))
    for i in range(1, steps):
        total += dt_dr_null(a + i * h, c=c)
    return sign * r_s * h * total


def flat_light_travel_time_x(x1: float, x2: float, *, r_s: float = 1.0, c: float = C) -> float:
    return (x2 - x1) * r_s / c
