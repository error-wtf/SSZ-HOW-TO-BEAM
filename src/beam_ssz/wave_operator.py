"""Correct radial-scaling wave-operator chain rule.

For dρ=s(r)dr, the radial second derivative is
    ∂²/∂ρ² E = (1/s) d/dr [(1/s) dE/dr]
not merely (1/s²)E''.
"""
from __future__ import annotations

from .xi import evaluate_d_s_x


def wave_operator_1d_radial(x: float, dE_dx: float, d2E_dx2: float, *, r_s: float = 1.0) -> float:
    """Return ∂²E/∂ρ² from x-derivatives of E(x).

    Since r=r_s*x:
      dE/dr = E_x/r_s, d²E/dr² = E_xx/r_s², ds/dr = s_x/r_s.
      (1/s)d/dr[(1/s)dE/dr] = E_rr/s² - (s_r/s³)E_r.
    """
    if r_s <= 0:
        raise ValueError("r_s must be positive")
    _D, s, ev = evaluate_d_s_x(x)
    E_r = dE_dx / r_s
    E_rr = d2E_dx2 / (r_s * r_s)
    s_r = ev.dxi_dx / r_s
    return E_rr / (s * s) - (s_r * E_r) / (s * s * s)


def naive_missing_chain_term(x: float, d2E_dx2: float, *, r_s: float = 1.0) -> float:
    """Incorrect helper kept only for tests/documentation of the forbidden shortcut."""
    if r_s <= 0:
        raise ValueError("r_s must be positive")
    _D, s, _ev = evaluate_d_s_x(x)
    return (d2E_dx2 / (r_s * r_s)) / (s * s)
