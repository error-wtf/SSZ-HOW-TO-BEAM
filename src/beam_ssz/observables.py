"""Observable types for SSZ method assignment."""
from __future__ import annotations

from enum import Enum


class ObservableType(str, Enum):
    NULL_LIGHT = "null_light"
    TIMELIKE_CLOCK = "timelike_clock"
    TIMELIKE_ORBIT = "timelike_orbit"
    TIMELIKE_WORLDLINE_TRANSFER = "timelike_worldline_transfer"
    EXTENDED_BODY_TIDAL = "extended_body_tidal"
