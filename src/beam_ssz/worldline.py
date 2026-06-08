"""Worldline continuity and timelike checks."""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from .constants import C


@dataclass(frozen=True)
class WorldlineSegment:
    tau_start: float
    tau_end: float
    start_event: tuple[float, float, float, float]
    end_event: tuple[float, float, float, float]
    max_event_jump: float = 0.0
    closed_timelike_curve_flag: bool = False

    @property
    def delta_tau(self) -> float:
        return self.tau_end - self.tau_start

    def has_positive_proper_time(self) -> bool:
        return self.delta_tau > 0.0

    def is_continuous(self, tolerance: float = 1e-9) -> bool:
        return self.max_event_jump <= tolerance

    def has_no_ctc_flag(self) -> bool:
        return not self.closed_timelike_curve_flag


def timelike_norm_ok(norm: float, tolerance: float = 1e-6, c_scaled: bool = True) -> bool:
    """Check g(u,u)=-1 for c-scaled coordinates, or -c² otherwise."""
    target = -1.0 if c_scaled else -(C * C)
    return isclose(norm, target, rel_tol=tolerance, abs_tol=tolerance)
