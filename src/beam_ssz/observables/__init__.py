"""Observable proxy modules for SSZ.

Implements phase shift, photon time delay, interferometry, and redshift
relative to SSZ canonical background (not just Minkowski).

Reference frame options:
- "SSZ_CANONICAL" — primary SSZ background
- "FLAT_MINKOWSKI" — flat limit for comparison only
"""

from enum import Enum, auto

from .phase_shift import compute_phase_shift, PhaseShiftResult
from .time_delay import compute_photon_delay, TimeDelayResult
from .redshift import compute_redshift, RedshiftResult
from .interferometry import compute_interferometer_response, InterferometerResult
from .reference_frame import ReferenceFrame, get_reference_metric


class ObservableType(Enum):
    """Observable measurement types."""
    # Original types
    PHASE_SHIFT = auto()
    TIME_DELAY = auto()
    REDSHIFT = auto()
    INTERFEROMETRY = auto()
    # Types needed by method_assignment
    NULL_LIGHT = auto()
    TIMELIKE_CLOCK = auto()
    TIMELIKE_ORBIT = auto()
    TIMELIKE_WORLDLINE_TRANSFER = auto()
    EXTENDED_BODY_TIDAL = auto()

# Convenience aliases for testing
interferometry_phase = compute_interferometer_response
phase_shift = compute_phase_shift
shapiro_delay = compute_photon_delay
redshift = compute_redshift

__all__ = [
    "compute_phase_shift",
    "PhaseShiftResult",
    "compute_photon_delay",
    "TimeDelayResult",
    "compute_redshift",
    "RedshiftResult",
    "compute_interferometer_response",
    "InterferometerResult",
    "ReferenceFrame",
    "get_reference_metric",
    "ObservableType",
    "interferometry_phase",
    "phase_shift",
    "shapiro_delay",
    "redshift",
]
