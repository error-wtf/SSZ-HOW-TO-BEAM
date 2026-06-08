"""Causality gates."""
from __future__ import annotations


def no_closed_timelike_curve(ctc_flag: bool) -> bool:
    return not ctc_flag


def proper_time_monotonic(delta_tau: float) -> bool:
    return delta_tau > 0.0
