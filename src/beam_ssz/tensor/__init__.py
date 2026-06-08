"""Tensor calculations for SSZ metric.

This module provides tensor calculation scaffolds for the SSZ metric.
These are smoke-test implementations, not full precision calculations.

For v0.8+ numerical backend, see:
- metric_array: 4D array-based metric implementation
- christoffel_array: Numerical Christoffel symbols
- riemann_array: Curvature tensor with proper symmetries
"""
from __future__ import annotations

from .metric_tensor import MetricTensor
from .inverse_metric import InverseMetric
from .christoffel import ChristoffelSymbols
from .riemann import RiemannTensor
from .ricci import RicciTensor
from .ricci_scalar import RicciScalar
from .einstein import EinsteinTensor
from .stress_energy import StressEnergyTensor
from .invariants import CurvatureInvariants

# New v0.8 array backend (numerical implementation)
from .metric_array import MetricArray, minkowski_metric, ssz_metric_array, flat_bridge_metric
from .christoffel_array import compute_christoffel, christoffel_from_finite_diff
from .riemann_array import compute_riemann_from_christoffel, check_riemann_symmetries, check_flatness

__all__ = [
    # Legacy scaffold classes
    "MetricTensor",
    "InverseMetric",
    "ChristoffelSymbols",
    "RiemannTensor",
    "RicciTensor",
    "RicciScalar",
    "EinsteinTensor",
    "StressEnergyTensor",
    "CurvatureInvariants",
    # New v0.8 array backend
    "MetricArray",
    "minkowski_metric",
    "ssz_metric_array",
    "flat_bridge_metric",
    "compute_christoffel",
    "christoffel_from_finite_diff",
    "compute_riemann_from_christoffel",
    "check_riemann_symmetries",
    "check_flatness",
]
