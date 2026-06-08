"""Canonical method assignment guardrails."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .observables import ObservableType


class Method(str, Enum):
    XI_DIRECT = "xi_direct"
    PPN = "ppn"
    SSZ_METRIC_WORLDLINE = "ssz_metric_worldline"
    SSZ_TIDAL_TENSOR = "ssz_tidal_tensor"


@dataclass(frozen=True)
class MethodAssignment:
    observable: ObservableType
    method: Method
    note: str


_ASSIGNMENTS: dict[ObservableType, MethodAssignment] = {
    ObservableType.NULL_LIGHT: MethodAssignment(
        ObservableType.NULL_LIGHT,
        Method.PPN,
        "Null/light-path observables require PPN completion with (1+gamma); Xi-only is half.",
    ),
    ObservableType.TIMELIKE_CLOCK: MethodAssignment(
        ObservableType.TIMELIKE_CLOCK,
        Method.XI_DIRECT,
        "Static clock/redshift observables use Xi directly: D=1/(1+Xi).",
    ),
    ObservableType.TIMELIKE_ORBIT: MethodAssignment(
        ObservableType.TIMELIKE_ORBIT,
        Method.PPN,
        "Orbit observables use PPN beta/gamma machinery, not Xi-only shortcuts.",
    ),
    ObservableType.TIMELIKE_WORLDLINE_TRANSFER: MethodAssignment(
        ObservableType.TIMELIKE_WORLDLINE_TRANSFER,
        Method.SSZ_METRIC_WORLDLINE,
        "Transfer candidates use SSZ metric, proper-time continuity, causality and tidal filters.",
    ),
    ObservableType.EXTENDED_BODY_TIDAL: MethodAssignment(
        ObservableType.EXTENDED_BODY_TIDAL,
        Method.SSZ_TIDAL_TENSOR,
        "Extended-body safety uses tidal tensor / curvature proxy constraints.",
    ),
}


def assign_method(observable: ObservableType | str) -> MethodAssignment:
    obs = ObservableType(observable)
    return _ASSIGNMENTS[obs]


def assert_method(observable: ObservableType | str, method: Method | str) -> None:
    expected = assign_method(observable).method
    method_enum = Method(method)
    if expected != method_enum:
        raise ValueError(f"Wrong method for {observable}: expected {expected.value}, got {method_enum.value}")
