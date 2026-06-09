"""SSZ Metric Formation Mechanism - Effective Source Model.

This module provides effective source reconstruction from SSZ metrics,
addressing the formation mechanism problem at the effective field theory level.

Given an SSZ metric g_μν, we compute:
    G_μν = Einstein tensor
    T_eff_μν = G_μν / (8π)  [geometrized units]

This defines what stress-energy would be required to create such a geometry,
without claiming such matter exists or can be physically realized.

Status Levels:
    FORMATION_UNRESOLVED: Initial state
    EFFECTIVE_SOURCE_DEFINED: T_eff computed
    EFFECTIVE_SOURCE_FINITE: All components finite
    ENERGY_BUDGET_ESTIMATED: Integrated energy calculated
    FORMATION_PATH_PENDING: Physical generation mechanism unknown
    PHYSICAL_GENERATION_NOT_SOLVED: Realistic source remains unsolved

Forbidden Claims:
    "Metric formation solved"
    "Physical bridge generation achieved"
    "Engineering feasible"
"""

from .effective_source import (
    compute_effective_source,
    EffectiveSourceResult,
    SourceDiagnostics,
)
from .energy_budget import (
    compute_energy_budget,
    EnergyBudgetResult,
    SourceLocalization,
)
from .boundary_conditions import (
    check_boundary_regularity,
    BoundaryStatus,
)
from .formation_report import (
    generate_formation_report,
    FormationStatus,
)

__all__ = [
    # Effective source
    "compute_effective_source",
    "EffectiveSourceResult",
    "SourceDiagnostics",
    # Energy budget
    "compute_energy_budget",
    "EnergyBudgetResult",
    "SourceLocalization",
    # Boundary conditions
    "check_boundary_regularity",
    "BoundaryStatus",
    # Formation report
    "generate_formation_report",
    "FormationStatus",
]
