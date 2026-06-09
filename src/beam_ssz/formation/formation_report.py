"""Formation mechanism report generator.

Generates comprehensive reports on effective source status
without claiming physical realizability.
"""

from typing import Dict, List
from enum import Enum, auto
from dataclasses import dataclass


class FormationStatus(Enum):
    """Overall formation mechanism status."""
    FORMATION_UNRESOLVED = "Metric formation mechanism: UNRESOLVED"
    EFFECTIVE_SOURCE_DEFINED = "Metric formation mechanism: EFFECTIVE_SOURCE_MODEL_DEFINED"
    EFFECTIVE_SOURCE_FINITE = "Metric formation mechanism: EFFECTIVE_SOURCE_FINITE"
    ENERGY_BUDGET_ESTIMATED = "Metric formation mechanism: ENERGY_BUDGET_ESTIMATED"
    FORMATION_PATH_PENDING = "Metric formation mechanism: FORMATION_PATH_PENDING"
    PHYSICAL_GENERATION_NOT_SOLVED = "Metric formation mechanism: PHYSICAL_GENERATION_NOT_SOLVED"


@dataclass
class FormationReport:
    """Complete formation mechanism report."""
    status: FormationStatus
    effective_source_summary: Dict
    energy_budget_summary: Dict
    boundary_summary: Dict
    recommendations: List[str]
    caveats: List[str]
    
    def to_text(self) -> str:
        """Generate human-readable text report."""
        lines = [
            "=" * 80,
            "SSZ METRIC FORMATION MECHANISM REPORT",
            "=" * 80,
            "",
            f"Status: {self.status.value}",
            "",
            "EFFECTIVE SOURCE ANALYSIS:",
            "-" * 40,
        ]
        
        for key, value in self.effective_source_summary.items():
            lines.append(f"  {key}: {value}")
        
        lines.extend([
            "",
            "ENERGY BUDGET ESTIMATE:",
            "-" * 40,
        ])
        
        for key, value in self.energy_budget_summary.items():
            lines.append(f"  {key}: {value}")
        
        lines.extend([
            "",
            "BOUNDARY CONDITIONS:",
            "-" * 40,
        ])
        
        for key, value in self.boundary_summary.items():
            lines.append(f"  {key}: {value}")
        
        if self.recommendations:
            lines.extend([
                "",
                "RECOMMENDATIONS:",
                "-" * 40,
            ])
            for rec in self.recommendations:
                lines.append(f"  • {rec}")
        
        if self.caveats:
            lines.extend([
                "",
                "CAVEATS (IMPORTANT):",
                "-" * 40,
            ])
            for caveat in self.caveats:
                lines.append(f"  ⚠ {caveat}")
        
        lines.extend([
            "",
            "=" * 80,
        ])
        
        return '\n'.join(lines)


def generate_formation_report(bridge) -> FormationReport:
    """Generate complete formation report for SSZ bridge.
    
    Args:
        bridge: SSZBridgeMetric instance
        
    Returns:
        FormationReport with comprehensive analysis
    """
    from .effective_source import scan_effective_source_along_bridge, SourceStatus
    from .energy_budget import compute_energy_budget
    from .boundary_conditions import check_boundary_regularity
    
    # Scan effective source
    source_results = scan_effective_source_along_bridge(bridge, n_points=50)
    
    # Analyze source status
    finite_count = sum(1 for r in source_results if r.diagnostics.is_finite)
    nec_violations = sum(r.diagnostics.nec_violation_points for r in source_results)
    wec_violations = sum(r.diagnostics.wec_violation_points for r in source_results)
    
    # Determine source status
    if finite_count == 0:
        source_status = SourceStatus.FORMATION_UNRESOLVED
    elif nec_violations > 0 or wec_violations > 0:
        source_status = SourceStatus.ENERGY_CONDITION_VIOLATION_DETECTED
    else:
        source_status = SourceStatus.EFFECTIVE_SOURCE_FINITE
    
    # Energy budget
    try:
        budget = compute_energy_budget(bridge)
        budget_summary = {
            'total_energy_joules': f"{budget.total_effective_energy:.2e}",
            'solar_masses_equivalent': f"{budget.solar_masses:.2e}",
            'localization_radius_m': f"{budget.localization.localization_radius:.2f}",
            'localization_status': budget.localization_status.name,
        }
    except Exception as e:
        budget_summary = {
            'error': f"Could not compute: {str(e)}",
        }
    
    # Boundary conditions
    boundary = check_boundary_regularity(bridge)
    boundary_summary = {
        'left_endpoint_regular': boundary.left_endpoint_regular,
        'right_endpoint_regular': boundary.right_endpoint_regular,
        'throat_regular': boundary.throat_regular,
        'overall': 'REGULAR' if all([
            boundary.left_endpoint_regular,
            boundary.right_endpoint_regular,
            boundary.throat_regular,
        ]) else 'IRREGULAR',
    }
    
    # Effective source summary
    if source_results:
        max_energy = max(r.diagnostics.max_energy_density for r in source_results)
        min_energy = min(r.diagnostics.min_energy_density for r in source_results)
        
        effective_source_summary = {
            'status': source_status.name,
            'finite_points': f"{finite_count}/50",
            'nec_violations': nec_violations,
            'wec_violations': wec_violations,
            'energy_density_range': f"[{min_energy:.2e}, {max_energy:.2e}]",
        }
    else:
        effective_source_summary = {
            'status': 'COMPUTATION_FAILED',
        }
    
    # Determine overall formation status
    if source_status == SourceStatus.FORMATION_UNRESOLVED:
        overall_status = FormationStatus.FORMATION_UNRESOLVED
    elif budget_summary.get('total_energy_joules'):
        overall_status = FormationStatus.ENERGY_BUDGET_ESTIMATED
    else:
        overall_status = FormationStatus.EFFECTIVE_SOURCE_DEFINED
    
    # Recommendations
    recommendations = []
    if nec_violations > 0:
        recommendations.append(
            "Energy conditions violated: Exotic matter required (if physically possible)"
        )
    if not boundary.left_endpoint_regular or not boundary.right_endpoint_regular:
        recommendations.append(
            "Boundary irregularities detected: Check metric asymptotics"
        )
    
    # Caveats
    caveats = [
        "Effective source is mathematical construct, not physical source",
        "Energy budget is geometric requirement, not engineering specification",
        "Physical generation mechanism remains unsolved",
        "Engineering feasibility not established",
        "Exotic matter requirements may be physically impossible",
    ]
    
    return FormationReport(
        status=overall_status,
        effective_source_summary=effective_source_summary,
        energy_budget_summary=budget_summary,
        boundary_summary=boundary_summary,
        recommendations=recommendations,
        caveats=caveats,
    )


def quick_formation_assessment(bridge) -> str:
    """Quick one-line formation assessment.
    
    Args:
        bridge: SSZBridgeMetric instance
        
    Returns:
        One-line status string
    """
    report = generate_formation_report(bridge)
    return report.status.value
