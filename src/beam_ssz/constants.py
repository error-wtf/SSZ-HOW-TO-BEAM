"""Physical and SSZ constants used by BEAM-SSZ."""
from __future__ import annotations

from math import sqrt

PHI: float = (1.0 + sqrt(5.0)) / 2.0
XI_RS: float = 1.0 - __import__("math").exp(-PHI)
D_RS: float = 1.0 / (1.0 + XI_RS)
C: float = 299_792_458.0
G: float = 6.67430e-11
HBAR: float = 1.054571817e-34  # Reduced Planck constant (J·s)
K_B: float = 1.380649e-23  # Boltzmann constant (J/K)

# Canonical formula-domain boundaries in x = r / r_s.
X_STRONG_MAX: float = 1.8
X_BLEND_MIN: float = 1.8
X_BLEND_MAX: float = 2.2
X_WEAK_MIN: float = 2.2
X_PHOTON_SPHERE_MAX: float = 3.0
X_STRONG_PHYSICAL_MAX: float = 10.0

# SSZ constants dictionary for easy access
SSZ_CONSTANTS = {
    "PHI": PHI,
    "XI_RS": XI_RS,
    "D_RS": D_RS,
    "C": C,
    "G": G,
    "HBAR": HBAR,
    "K_B": K_B,
    "X_STRONG_MAX": X_STRONG_MAX,
    "X_BLEND_MIN": X_BLEND_MIN,
    "X_BLEND_MAX": X_BLEND_MAX,
    "X_WEAK_MIN": X_WEAK_MIN,
    "X_PHOTON_SPHERE_MAX": X_PHOTON_SPHERE_MAX,
    "X_STRONG_PHYSICAL_MAX": X_STRONG_PHYSICAL_MAX,
}
