"""Observable proxy modules for SSZ.

Implements phase shift, photon time delay, interferometry, and redshift
relative to SSZ canonical background (not just Minkowski).

Reference frame options:
- "SSZ_CANONICAL" — primary SSZ background
- "FLAT_MINKOWSKI" — flat limit for comparison only
"""

from .phase_shift import compute_phase_shift, PhaseShiftResult
from .time_delay import compute_photon_delay, TimeDelayResult
from .redshift import compute_redshift, RedshiftResult
from .interferometry import compute_interferometer_response, InterferometerResult
from .reference_frame import ReferenceFrame, get_reference_metric

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
]
