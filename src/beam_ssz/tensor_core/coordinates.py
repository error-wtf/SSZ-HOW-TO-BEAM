"""Coordinate system definitions for tensor operations.

Index convention:
    0 = t (time)
    1 = r (radial)  
    2 = theta (polar angle)
    3 = phi (azimuthal angle)
"""

from enum import IntEnum


class CoordinateIndex(IntEnum):
    """Standard 4D coordinate indices for SSZ metrics."""
    T = 0  # time
    R = 1  # radial
    THETA = 2  # polar angle
    PHI = 3  # azimuthal angle


COORD_NAMES = ("t", "r", "theta", "phi")


def coord_name(idx: int) -> str:
    """Return coordinate name for index."""
    return COORD_NAMES[idx]
