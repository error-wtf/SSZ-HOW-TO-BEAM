"""SSZ transport mode validation.

No-copy constraint enforcement.
CONTINUOUS_WORLDLINE = pass, others = block.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from .status import TransportMode, NoCopyStatus, TransportReadiness


@dataclass
class TransportModeResult:
    """Result of transport mode validation."""
    mode: TransportMode
    no_copy_status: NoCopyStatus
    readiness: TransportReadiness
    allowed_claims: List[str]
    forbidden_claims: List[str]
    details: Dict


def validate_transport_mode(mode: TransportMode) -> TransportModeResult:
    """Validate transport mode.
    
    Args:
        mode: Transport mode
    
    Returns:
        TransportModeResult
    """
    details = {"mode": mode.value}
    
    if mode == TransportMode.CONTINUOUS_WORLDLINE:
        return TransportModeResult(
            mode,
            NoCopyStatus.NO_COPY_PASS,
            TransportReadiness.NO_COPY_CONSTRAINT_PASS,
            ["Transport mode: CONTINUOUS_WORLDLINE", "No-copy constraint satisfied"],
            [],
            details
        )
    
    elif mode == TransportMode.COPY_RECONSTRUCTION:
        details["blocker"] = "Copy reconstruction violates identity continuity"
        return TransportModeResult(
            mode,
            NoCopyStatus.COPY_MODE_DETECTED,
            TransportReadiness.MATH_CANDIDATE_ONLY,  # Blocks person-readiness
            ["Transport mode: COPY_RECONSTRUCTION (math-only, no person transport)"],
            ["No-copy constraint failed", "Person transport blocked", "Identity continuity not guaranteed"],
            details
        )
    
    elif mode == TransportMode.DESTRUCTIVE_SCAN:
        details["blocker"] = "Destructive scan violates matter continuity"
        return TransportModeResult(
            mode,
            NoCopyStatus.DESTRUCTIVE_STEP_DETECTED,
            TransportReadiness.MATH_CANDIDATE_ONLY,
            ["Transport mode: DESTRUCTIVE_SCAN (math-only, no person transport)"],
            ["No-copy constraint failed", "Matter continuity violated", "Person transport blocked"],
            details
        )
    
    else:  # UNDEFINED
        return TransportModeResult(
            mode,
            NoCopyStatus.NO_COPY_PASS,  # No violation, but undefined
            TransportReadiness.MATH_CANDIDATE_ONLY,
            [],
            ["Transport mode undefined", "Cannot validate no-copy constraint"],
            details
        )


def no_copy_constraint(
    mode: TransportMode,
    duplicates_detected: bool = False,
    destructive_step: bool = False,
    pattern_buffer_as_primary: bool = False,
) -> Dict:
    """Check no-copy constraint.
    
    Pass only if:
    - mode == CONTINUOUS_WORLDLINE
    - duplicates_detected is False
    - destructive_step is False
    - pattern_buffer_as_primary is False
    
    Args:
        mode: Transport mode
        duplicates_detected: Whether duplicate instances detected
        destructive_step: Whether destructive step detected
        pattern_buffer_as_primary: Whether pattern buffer is primary identity carrier
    
    Returns:
        Dict with validation result
    """
    violations = []
    
    if mode != TransportMode.CONTINUOUS_WORLDLINE:
        violations.append(f"Mode is {mode.value}, not CONTINUOUS_WORLDLINE")
    
    if duplicates_detected:
        violations.append("Duplicate instances detected")
    
    if destructive_step:
        violations.append("Destructive step detected")
    
    if pattern_buffer_as_primary:
        violations.append("Pattern buffer used as primary identity carrier")
    
    if not violations:
        return {
            "pass": True,
            "status": NoCopyStatus.NO_COPY_PASS,
            "violations": [],
            "message": "No-copy constraint satisfied",
            "person_transport_blocked": False,
            "readiness": TransportReadiness.NO_COPY_CONSTRAINT_PASS,
        }
    else:
        return {
            "pass": False,
            "status": NoCopyStatus.COPY_MODE_DETECTED if mode == TransportMode.COPY_RECONSTRUCTION else NoCopyStatus.DESTRUCTIVE_STEP_DETECTED,
            "violations": violations,
            "message": "No-copy constraint VIOLATED: " + "; ".join(violations),
            "person_transport_blocked": True,  # CRITICAL
            "readiness": TransportReadiness.MATH_CANDIDATE_ONLY,
        }


def check_person_transport_readiness(
    no_copy_result: Dict,
    biological_validated: bool = False,
) -> Dict:
    """Check if person transport is ready (it never is in v0.9).
    
    Args:
        no_copy_result: Result from no_copy_constraint
        biological_validated: Whether biological validation exists (always False in v0.9)
    
    Returns:
        Dict with readiness assessment
    """
    # Always blocked in v0.9
    blocked = True
    reasons = []
    
    if not no_copy_result.get("pass", False):
        reasons.append("No-copy constraint not satisfied")
    
    if not biological_validated:
        reasons.append("Biological transport NOT_VALIDATED")
    
    # Additional v0.9 blockers
    reasons.append("v0.9: No biological validation framework")
    reasons.append("v0.9: No experimental validation")
    reasons.append("v0.9: Tensor diagnostics pending")
    reasons.append("v0.9: Energy conditions pending")
    
    return {
        "person_transport_ready": False,  # ALWAYS FALSE in v0.9
        "blocked": True,
        "reasons": reasons,
        "readiness_level": TransportReadiness.BIOLOGICAL_NOT_VALIDATED.value,
        "allowed_claims": [
            "Math/proxy candidate only",
            "Mathematically likely possible",
        ],
        "forbidden_claims": [
            "Human transport possible",
            "Biological safety proven",
            "Person transport validated",
        ],
    }
