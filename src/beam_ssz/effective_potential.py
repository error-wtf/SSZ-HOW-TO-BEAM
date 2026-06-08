"""Effective-potential helpers for timelike SSZ geodesics."""
from __future__ import annotations

from .geodesics import effective_potential


def numerical_derivative(func, x: float, h: float = 1e-5) -> float:
    if x - h <= 0:
        raise ValueError("x-h must be positive")
    return (func(x + h) - func(x - h)) / (2.0 * h)


def numerical_second_derivative(func, x: float, h: float = 1e-4) -> float:
    if x - h <= 0:
        raise ValueError("x-h must be positive")
    return (func(x + h) - 2.0 * func(x) + func(x - h)) / (h * h)


def potential_gradient(x: float, angular_momentum: float = 0.0, r_s: float = 1.0, c: float = 1.0) -> float:
    return numerical_derivative(lambda y: effective_potential(y, angular_momentum, r_s, c), x)


def potential_curvature(x: float, angular_momentum: float = 0.0, r_s: float = 1.0, c: float = 1.0) -> float:
    return numerical_second_derivative(lambda y: effective_potential(y, angular_momentum, r_s, c), x)
