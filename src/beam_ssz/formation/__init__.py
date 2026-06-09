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
    SourceStatus,
)
from .energy_budget import (
    compute_energy_budget,
    EnergyBudgetResult,
    SourceLocalization,
)
from .boundary_conditions import (
    check_boundary_regularity,
    check_asymptotic_behavior,
    BoundaryStatus,
)
from .formation_report import (
    generate_formation_report,
    FormationStatus,
)

# Import scan function from effective_source
from .effective_source import (
    scan_effective_source_along_bridge,
)

# Import sensitivity analysis from energy_budget
from .energy_budget import (
    energy_budget_sensitivity_analysis,
)

__all__ = [
    # Effective source
    "compute_effective_source",
    "scan_effective_source_along_bridge",
    "EffectiveSourceResult",
    "SourceDiagnostics",
    "SourceStatus",
    # Energy budget
    "compute_energy_budget",
    "energy_budget_sensitivity_analysis",
    "EnergyBudgetResult",
    "SourceLocalization",
    # Boundary conditions
    "check_boundary_regularity",
    "check_asymptotic_behavior",
    "BoundaryStatus",
    # Formation report
    "generate_formation_report",
    "FormationStatus",
]
