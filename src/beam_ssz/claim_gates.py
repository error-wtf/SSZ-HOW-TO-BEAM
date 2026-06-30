"""Claim Gate System for v1.0

Claims strictly dependent on test results and evidence levels.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Dict


class EvidenceLevel(Enum):
    """Hierarchy of evidence strength."""
    NONE = auto()
    DOCUMENTED_ASSUMPTION = auto()
    PROXY_TESTED = auto()
    ALGEBRAIC_TESTED = auto()
    NUMERIC_TENSOR_TESTED = auto()
    CONVERGENCE_TESTED = auto()
    EXPERIMENTALLY_TESTED = auto()


class ClaimCategory(Enum):
    """Categories of scientific claims."""
    SSZ_SEGMENTATION = auto()
    EFFECTIVE_DISTANCE = auto()
    SEGMENT_OVERLAP = auto()
    WORLDLINE_CONTINUITY = auto()
    NO_COPY = auto()
    TENSOR_DIAGNOSTIC = auto()
    ENERGY_CONDITION = auto()
    NUMERICAL_GR = auto()
    OBSERVABLE_PROXY = auto()
    BIOLOGICAL_SAFETY = auto()
    EXPERIMENTAL_VALIDATION = auto()


class ClaimStatus(Enum):
    """Status of claim evaluation."""
    ALLOWED = auto()
    ALLOWED_WITH_SCOPE = auto()
    PARTIAL = auto()
    PENDING = auto()
    FORBIDDEN = auto()
    FAILED = auto()


@dataclass
class ClaimGateResult:
    """Result of claim gate evaluation."""
    claim: str
    category: ClaimCategory
    required_evidence: EvidenceLevel
    actual_evidence: EvidenceLevel
    status: ClaimStatus
    allowed_wording: str
    forbidden_wordings: List[str]
    test_reference: Optional[str]
    notes: str


# Claim gate rules
CLAIM_RULES = {
    ClaimCategory.SSZ_SEGMENTATION: {
        "required": EvidenceLevel.PROXY_TESTED,
        "allowed_if_pass": "SSZ segmentation laws are internally consistent in tested regimes.",
        "forbidden": ["SSZ universally proven", "SSZ axioms validated everywhere"],
    },
    ClaimCategory.EFFECTIVE_DISTANCE: {
        "required": EvidenceLevel.PROXY_TESTED,
        "allowed_if_pass": "effective SSZ segment-distance reduction proxy passes in tested candidates.",
        "forbidden": ["physical transport achieved", "distance actually collapses"],
    },
    ClaimCategory.SEGMENT_OVERLAP: {
        "required": EvidenceLevel.PROXY_TESTED,
        "allowed_if_pass": "segment-neighborhood overlap proxy passes in tested regimes.",
        "forbidden": ["wormhole physically opened", "spatial topology changed"],
    },
    ClaimCategory.WORLDLINE_CONTINUITY: {
        "required": EvidenceLevel.PROXY_TESTED,
        "allowed_if_pass": "continuous-worldline proxy passes.",
        "forbidden": ["identity proven", "consciousness continuity validated"],
    },
    ClaimCategory.NO_COPY: {
        "required": EvidenceLevel.PROXY_TESTED,
        "allowed_if_pass": "no-copy model gate is enforced.",
        "forbidden": ["person transport possible", "human-safe"],
    },
    ClaimCategory.TENSOR_DIAGNOSTIC: {
        "required": EvidenceLevel.NUMERIC_TENSOR_TESTED,
        "allowed_if_pass": "SSZ tensor diagnostics are finite and internally consistent in tested regimes.",
        "forbidden": ["Full tensor proof complete", "tensor validation universal"],
    },
    ClaimCategory.ENERGY_CONDITION: {
        "required": EvidenceLevel.NUMERIC_TENSOR_TESTED,
        "allowed_if_pass": "sampled tensor-derived energy diagnostic passes for tested candidate/tolerance.",
        "forbidden": ["NEC proven", "energy conditions satisfied", "no exotic matter required"],
    },
    ClaimCategory.NUMERICAL_GR: {
        "required": EvidenceLevel.CONVERGENCE_TESTED,
        "allowed_if_pass": "Numerical-GR scaffold runs and produces constraint diagnostics.",
        "forbidden": ["validated numerical relativity evolution", "GR evolution proven stable"],
    },
    ClaimCategory.OBSERVABLE_PROXY: {
        "required": EvidenceLevel.PROXY_TESTED,
        "allowed_if_pass": "observable proxy designs are implemented.",
        "forbidden": ["experimentally confirmed", "observationally proven"],
    },
    ClaimCategory.BIOLOGICAL_SAFETY: {
        "required": EvidenceLevel.EXPERIMENTALLY_TESTED,
        "allowed_if_pass": "biological safety validated for specific tested organisms and conditions (not universal)",
        "forbidden": ["biological safety proven universally", "all life forms safe", "unconditional biological safety"],
    },
    ClaimCategory.EXPERIMENTAL_VALIDATION: {
        "required": EvidenceLevel.EXPERIMENTALLY_TESTED,
        "allowed_if_pass": "experimental signature detected in specific measurement campaign",
        "forbidden": ["universal experimental validation", "all experiments confirm", "definitive experimental proof"],
    },
}


def evaluate_claim_gate(
    category: ClaimCategory,
    actual_evidence: Optional[EvidenceLevel] = None,
    tests_passed: bool = True,
    scope: Optional[str] = None,
    test_reference: Optional[str] = None,
    evidence_level: Optional[EvidenceLevel] = None,  # Alias for compatibility
) -> dict:
    """Evaluate a claim against the gate rules.
    
    Args:
        category: Category of claim
        actual_evidence: Level of evidence available
        tests_passed: Whether relevant tests pass
        scope: Optional scope limitation
        test_reference: Optional test file reference
    
    Returns:
        dict with evaluation result
    """
    # Use evidence_level alias if actual_evidence not provided
    if actual_evidence is None and evidence_level is not None:
        actual_evidence = evidence_level
    elif actual_evidence is None:
        actual_evidence = EvidenceLevel.NONE
    
    rules = CLAIM_RULES.get(category, {})
    required = rules.get("required", EvidenceLevel.NONE)
    allowed_wording = rules.get("allowed_if_pass", "")
    forbidden = rules.get("forbidden", [])
    
    # Determine status
    if category in [ClaimCategory.BIOLOGICAL_SAFETY, ClaimCategory.EXPERIMENTAL_VALIDATION]:
        status = ClaimStatus.FORBIDDEN
        notes = "This claim is strictly FORBIDDEN in version 1.1.0 (exploratory status only)."
    elif not tests_passed:
        status = ClaimStatus.FAILED
        notes = f"Tests failed or not run (required: {required.name})"
    elif actual_evidence.value < required.value:
        status = ClaimStatus.PENDING
        notes = f"Insufficient evidence (have: {actual_evidence.name}, need: {required.name})"
    else:
        if scope:
            status = ClaimStatus.ALLOWED_WITH_SCOPE
            notes = f"Allowed with scope: {scope}"
        else:
            status = ClaimStatus.ALLOWED
            notes = "All requirements met"
    
    # Build allowed wording
    if status in [ClaimStatus.ALLOWED, ClaimStatus.ALLOWED_WITH_SCOPE]:
        final_wording = allowed_wording
        if scope:
            final_wording += f" [{scope}]"
    else:
        final_wording = "[NOT ALLOWED]"
    
    # Return dict for compatibility
    return {
        "claim": category.name,
        "category": category,
        "required_evidence": required,
        "actual_evidence": actual_evidence,
        "status": status,
        "allowed": status in [ClaimStatus.ALLOWED, ClaimStatus.ALLOWED_WITH_SCOPE],
        "allowed_wording": final_wording,
        "forbidden_wordings": forbidden,
        "test_reference": test_reference,
        "notes": notes,
        "wording": final_wording,
    }


def evaluate_all_ssz_core_claims(
    segmentation_pass: bool,
    effective_distance_pass: bool,
    overlap_pass: bool,
    worldline_pass: bool,
    no_copy_pass: bool,
) -> Dict[ClaimCategory, ClaimGateResult]:
    """Evaluate all SSZ core claims.
    
    Args:
        Various test pass statuses
    
    Returns:
        Dict of claim results
    """
    results = {}
    
    # SSZ Segmentation
    results[ClaimCategory.SSZ_SEGMENTATION] = evaluate_claim_gate(
        ClaimCategory.SSZ_SEGMENTATION,
        EvidenceLevel.PROXY_TESTED if segmentation_pass else EvidenceLevel.DOCUMENTED_ASSUMPTION,
        segmentation_pass,
        test_reference="tests/test_ssz_segmentation_rules.py",
    )
    
    # Effective Distance
    results[ClaimCategory.EFFECTIVE_DISTANCE] = evaluate_claim_gate(
        ClaimCategory.EFFECTIVE_DISTANCE,
        EvidenceLevel.PROXY_TESTED if effective_distance_pass else EvidenceLevel.DOCUMENTED_ASSUMPTION,
        effective_distance_pass,
        test_reference="tests/test_ssz_effective_distance.py",
    )
    
    # Segment Overlap
    results[ClaimCategory.SEGMENT_OVERLAP] = evaluate_claim_gate(
        ClaimCategory.SEGMENT_OVERLAP,
        EvidenceLevel.PROXY_TESTED if overlap_pass else EvidenceLevel.DOCUMENTED_ASSUMPTION,
        overlap_pass,
        test_reference="tests/test_ssz_segment_neighborhood_overlap.py",
    )
    
    # Worldline Continuity
    results[ClaimCategory.WORLDLINE_CONTINUITY] = evaluate_claim_gate(
        ClaimCategory.WORLDLINE_CONTINUITY,
        EvidenceLevel.PROXY_TESTED if worldline_pass else EvidenceLevel.DOCUMENTED_ASSUMPTION,
        worldline_pass,
        test_reference="tests/test_ssz_continuous_worldline.py",
    )
    
    # No-Copy
    results[ClaimCategory.NO_COPY] = evaluate_claim_gate(
        ClaimCategory.NO_COPY,
        EvidenceLevel.PROXY_TESTED if no_copy_pass else EvidenceLevel.DOCUMENTED_ASSUMPTION,
        no_copy_pass,
        test_reference="tests/test_no_copy_constraint.py",
    )
    
    # Always forbidden in v1.0
    results[ClaimCategory.BIOLOGICAL_SAFETY] = evaluate_claim_gate(
        ClaimCategory.BIOLOGICAL_SAFETY,
        EvidenceLevel.NONE,
        False,
    )
    
    results[ClaimCategory.EXPERIMENTAL_VALIDATION] = evaluate_claim_gate(
        ClaimCategory.EXPERIMENTAL_VALIDATION,
        EvidenceLevel.NONE,
        False,
    )
    
    return results


def generate_v1_claim_report(results: Dict[ClaimCategory, ClaimGateResult]) -> str:
    """Generate v1.0 claim report."""
    
    lines = [
        "# v1.0 Claim Gate Report",
        "",
        "## Allowed Claims",
        "",
    ]
    
    for cat, result in results.items():
        if result.status in [ClaimStatus.ALLOWED, ClaimStatus.ALLOWED_WITH_SCOPE]:
            lines.append(f"- **{result.category.name}**: {result.allowed_wording}")
    
    lines.extend([
        "",
        "## Forbidden Claims",
        "",
    ])
    
    for cat, result in results.items():
        if result.status == ClaimStatus.FORBIDDEN:
            lines.append(f"- **{result.category.name}**: {result.notes}")
            for forbidden in result.forbidden_wordings:
                lines.append(f"  - ❌ \"{forbidden}\"")
    
    lines.extend([
        "",
        "## Pending Claims",
        "",
    ])
    
    for cat, result in results.items():
        if result.status == ClaimStatus.PENDING:
            lines.append(f"- **{result.category.name}**: {result.notes}")
    
    return "\n".join(lines)
