"""Frequency/clock holonomy diagnostics for SSZ bridge candidates."""
from __future__ import annotations

from math import prod

from .xi import evaluate_d_s_x


def D_of_x(x: float) -> float:
    return evaluate_d_s_x(x)[0]


def frequency_ratio_x(x_a: float, x_b: float) -> float:
    """Return f_A/f_B = D(B)/D(A)."""
    return D_of_x(x_b) / D_of_x(x_a)


def closed_loop_invariant(xs: list[float] | tuple[float, ...]) -> float:
    """Return Π D(x_i)/D(x_{i+1}) for a closed static loop.

    For canonical static spherical SSZ this telescopes to exactly 1 up to roundoff.
    """
    if len(xs) < 2:
        raise ValueError("closed loop needs at least two clock radii")
    ratios = []
    for i, x in enumerate(xs):
        y = xs[(i + 1) % len(xs)]
        ratios.append(D_of_x(x) / D_of_x(y))
    return prod(ratios)


def dynamic_D(base_D: float, h: float, f: float) -> float:
    """Toy dynamic modulation D(t)=D0*(1+h*f)."""
    value = base_D * (1.0 + h * f)
    if value <= 0:
        raise ValueError("dynamic D became non-positive")
    return value


def dynamic_closed_loop_invariant(xs: list[float], h_values: list[float], f_values: list[float]) -> float:
    """Closed-loop invariant with local dynamic D modulation per node."""
    if not (len(xs) == len(h_values) == len(f_values)):
        raise ValueError("xs, h_values, and f_values must have same length")
    Ds = [dynamic_D(D_of_x(x), h, f) for x, h, f in zip(xs, h_values, f_values)]
    total = 1.0
    for i, D in enumerate(Ds):
        total *= D / Ds[(i + 1) % len(Ds)]
    return total


def edge_modulated_loop_invariant(xs: list[float], edge_gains: list[float]) -> float:
    """Toy non-static holonomy diagnostic with edge-local gains.

    Static node ratios telescope to 1. Edge gains represent path-dependent dynamic
    modulation during transport and therefore need not telescope.
    """
    if len(xs) < 2 or len(xs) != len(edge_gains):
        raise ValueError("edge_gains must match number of loop edges/nodes")
    total = closed_loop_invariant(xs)
    for gain in edge_gains:
        total *= gain
    return total
