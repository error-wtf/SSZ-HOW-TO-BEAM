"""Tensor-Core: Array-based tensor computations for SSZ metrics.

This module provides genuine tensor calculations using numpy arrays,
separated from proxy/heuristic diagnostics.

Index convention: 0=t, 1=r, 2=theta, 3=phi

Status: v0.9 implementation - tensor validation pending until tests pass.
"""

from .coordinates import CoordinateIndex, COORD_NAMES
from .status import TensorStatus, EnergyConditionStatus
from .metric_backend import (
    minkowski_cartesian,
    minkowski_spherical,
    ssz_metric,
    metric_from_bridge_candidate,
    flat_bridge_limit,
)
from .finite_differences import central_diff, second_diff
from .christoffel import compute_christoffel
from .riemann import compute_riemann
from .ricci import compute_ricci, ricci_scalar
from .einstein import compute_einstein
from .stress_energy import compute_stress_energy
from .ssz_stress_energy import (
    reconstruct_stress_energy_from_ssz,
    check_energy_conditions,
    analyze_ssz_bridge_matter,
)
from .null_vectors import generate_null_vectors
from .energy_conditions import check_nec, check_wec
from .validation import validate_tensor_finite, validate_metric_complete
from .regime import classify_regime, Regime

__all__ = [
    "CoordinateIndex",
    "COORD_NAMES",
    "TensorStatus",
    "EnergyConditionStatus",
    "minkowski_cartesian",
    "minkowski_spherical",
    "ssz_metric",
    "metric_from_bridge_candidate",
    "flat_bridge_limit",
    "central_diff",
    "second_diff",
    "compute_christoffel",
    "compute_riemann",
    "compute_ricci",
    "ricci_scalar",
    "compute_einstein",
    "compute_stress_energy",
    "reconstruct_stress_energy_from_ssz",
    "check_energy_conditions",
    "analyze_ssz_bridge_matter",
    "generate_null_vectors",
    "check_nec",
    "check_wec",
    "validate_tensor_finite",
    "validate_metric_complete",
    "classify_regime",
    "Regime",
]
