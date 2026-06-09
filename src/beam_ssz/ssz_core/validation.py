"""SSZ bridge validation pipeline.

Integrates all SSZ v0.9 validation gates.
Generates allowed claims from test results only.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field

from .status import (
    SSZValidationStatus, TransportReadiness,
    SegmentationStatus, WorldlineStatus, NoCopyStatus
)
from .segmentation import validate_segmentation_state, SegmentationResult
from .effective_distance import (
    effective_segment_distance, bridge_effective_distance,
    distance_reduction_ratio, EffectiveDistanceResult
)
from .neighborhood import neighborhood_overlap, validate_neighborhood_proxy, NeighborhoodResult
from .worldline import validate_worldline_continuity, WorldlineSample, WorldlineResult
from .transport_mode import validate_transport_mode, no_copy_constraint, TransportMode


@dataclass
class SSZBridgeValidationReport:
    """Complete SSZ bridge validation report."""
    # Gate statuses
    segmentation_status: SSZValidationStatus = SSZValidationStatus.NOT_RUN
    effective_distance_status: SSZValidationStatus = SSZValidationStatus.NOT_RUN
    overlap_status: SSZValidationStatus = SSZValidationStatus.NOT_RUN
    worldline_status: SSZValidationStatus = SSZValidationStatus.NOT_RUN
    no_copy_status: SSZValidationStatus = SSZValidationStatus.NOT_RUN
    
    # Pending gates (for future v0.9+ development)
    tensor_status: SSZValidationStatus = SSZValidationStatus.PENDING
    energy_status: SSZValidationStatus = SSZValidationStatus.PENDING
    
    # Permanent blockers
    biological_status: str = "NOT_VALIDATED"
    experimental_status: str = "NONE"
    
    # Claims
    allowed_claims: List[str] = field(default_factory=list)
    forbidden_claims: List[str] = field(default_factory=list)
    unresolved_items: List[str] = field(default_factory=list)
    
    # Overall
    overall_readiness: TransportReadiness = TransportReadiness.MATH_CANDIDATE_ONLY
    
    # Alias for compatibility
    @property
    def readiness(self) -> TransportReadiness:
        return self.overall_readiness
    
    # Scientific position
    scientific_position: str = ""


def validate_ssz_bridge_candidate(
    point_a,
    point_b,
    xi_func: Callable[[float], float],
    bridge_coupling: float = 0.0,
    transport_mode = None,
) -> SSZBridgeValidationReport:
    """Validate SSZ bridge candidate through all gates.
    
    Args:
        point_a: Point A coordinates
        point_b: Point B coordinates
        xi_func: Xi(r) function
        bridge_coupling: Bridge coupling strength
        transport_mode: Optional transport mode
    
    Returns:
        SSZBridgeValidationReport
    """
    report = SSZBridgeValidationReport()
    allowed = []
    forbidden = [
        "Physical beaming achieved",
        "Human transport possible",
        "Carmen can be transported",
        "Biological safety proven",
        "Metric formation solved",
        "Experimental validation confirmed",
    ]
    unresolved = []
    
    # Gate 1: Segmentation
    xi_a = xi_func(point_a[1])
    xi_b = xi_func(point_b[1])
    
    seg_result_a = validate_segmentation_state(xi_a)
    seg_result_b = validate_segmentation_state(xi_b)
    
    if (seg_result_a.status == SegmentationStatus.SEGMENTATION_PASS and
        seg_result_b.status == SegmentationStatus.SEGMENTATION_PASS):
        report.segmentation_status = SSZValidationStatus.PASS
        allowed.append("SSZ segmentation laws are internally consistent")
    else:
        report.segmentation_status = SSZValidationStatus.FAIL
        forbidden.append("SSZ segmentation claims")
        unresolved.append(f"Segmentation issues: A={seg_result_a.status.value}, B={seg_result_b.status.value}")
    
    # Gate 2: Effective Distance
    try:
        d_without = effective_segment_distance([point_a, point_b], xi_func)
        d_with = bridge_effective_distance(point_a, point_b, bridge_coupling, xi_func)
        
        ratio_result = distance_reduction_ratio(d_without, d_with)
        
        if ratio_result["status"] == SSZValidationStatus.PASS and ratio_result["reduction"] > 0:
            report.effective_distance_status = SSZValidationStatus.PASS
            allowed.append("Effective SSZ segment-distance reduction proxy passes")
        else:
            report.effective_distance_status = ratio_result["status"]
            if ratio_result["status"] == SSZValidationStatus.FAIL:
                unresolved.append(f"Distance reduction failed: {ratio_result.get('message', '')}")
    except Exception as e:
        report.effective_distance_status = SSZValidationStatus.FAIL
        unresolved.append(f"Distance calculation error: {e}")
    
    # Gate 3: Segment Overlap
    try:
        overlap_score = neighborhood_overlap(point_a, point_b, xi_a, xi_b, bridge_coupling)
        overlap_result = validate_neighborhood_proxy(overlap_score)
        
        report.overlap_status = overlap_result.status
        if overlap_result.has_overlap:
            allowed.append("Segment-neighborhood overlap proxy passes")
    except Exception as e:
        report.overlap_status = SSZValidationStatus.FAIL
        unresolved.append(f"Overlap calculation error: {e}")
    
    # Gate 4: Worldline Continuity (simplified for two points)
    samples = [
        WorldlineSample(tau=0.0, t=point_a[0], r=point_a[1], theta=point_a[2], phi=point_a[3]),
        WorldlineSample(tau=1.0, t=point_b[0], r=point_b[1], theta=point_b[2], phi=point_b[3]),
    ]
    
    wl_result = validate_worldline_continuity(samples)
    
    if wl_result.status == WorldlineStatus.WORLDLINE_PASS:
        report.worldline_status = SSZValidationStatus.PASS
        allowed.append("Continuous-worldline proxy passes")
    else:
        report.worldline_status = SSZValidationStatus.FAIL
        unresolved.append(f"Worldline issue: {wl_result.status.value}")
    
    # Gate 5: No-Copy
    if transport_mode:
        nc_result = no_copy_constraint(transport_mode)
        if nc_result["pass"]:
            report.no_copy_status = SSZValidationStatus.PASS
            allowed.append("No-copy constraint enforced")
        else:
            report.no_copy_status = SSZValidationStatus.FAIL
            forbidden.append("Person transport (no-copy violation)")
            unresolved.append(f"No-copy violation: {nc_result.get('message', '')}")
    else:
        # Default: continuous worldline assumed
        nc_result = no_copy_constraint(TransportMode.CONTINUOUS_WORLDLINE)  # Assume continuous for pending
        report.no_copy_status = SSZValidationStatus.PENDING
    
    # Determine overall readiness
    core_passes = sum([
        report.segmentation_status == SSZValidationStatus.PASS,
        report.effective_distance_status == SSZValidationStatus.PASS,
        report.overlap_status == SSZValidationStatus.PASS,
        report.worldline_status == SSZValidationStatus.PASS,
        report.no_copy_status == SSZValidationStatus.PASS,
    ])
    
    if core_passes == 5:
        report.overall_readiness = TransportReadiness.NO_COPY_CONSTRAINT_PASS
        allowed.append("BEAM-SSZ v0.9 supports a no-copy continuous-worldline bridge candidate at SSZ proxy/algebraic level")
    elif core_passes >= 3:
        report.overall_readiness = TransportReadiness.SEGMENT_OVERLAP_PROXY_PASS
    elif core_passes >= 1:
        report.overall_readiness = TransportReadiness.SEGMENTATION_PASS
    else:
        report.overall_readiness = TransportReadiness.MATH_CANDIDATE_ONLY
    
    # Update report
    report.allowed_claims = list(set(allowed))
    report.forbidden_claims = list(set(forbidden))
    report.unresolved_items = unresolved
    
    # Scientific position
    report.scientific_position = generate_scientific_position(report)
    
    return report


def generate_scientific_position(report: SSZBridgeValidationReport) -> str:
    """Generate scientific position statement."""
    
    position = f"""SSZ-HOW-TO-BEAM v0.9 Validation Report

Overall Readiness: {report.overall_readiness.value}

Gate Status:
- Segmentation: {report.segmentation_status.value}
- Effective Distance: {report.effective_distance_status.value}
- Segment Overlap: {report.overlap_status.value}
- Worldline Continuity: {report.worldline_status.value}
- No-Copy: {report.no_copy_status.value}
- Tensor: {report.tensor_status.value}
- Energy: {report.energy_status.value}

Allowed Claims:
{chr(10).join(f"  • {claim}" for claim in report.allowed_claims)}

Explicitly Forbidden:
{chr(10).join(f"  • {claim}" for claim in report.forbidden_claims)}

Critical Limitations:
- Biological Transport: {report.biological_status}
- Experimental Validation: {report.experimental_status}

Core Scientific Position:
BEAM-SSZ does not treat a person as information to be copied,
but as a continuous worldline whose effective segment-distance
between origin and target is reduced by a controlled SSZ bridge.

This is a mathematical candidate framework with proxy-level validation.
Physical implementation, biological safety, and experimental confirmation remain open problems.

Unresolved Items:
{chr(10).join(f"  - {item}" for item in report.unresolved_items) if report.unresolved_items else "  None"}
"""
    
    return position
