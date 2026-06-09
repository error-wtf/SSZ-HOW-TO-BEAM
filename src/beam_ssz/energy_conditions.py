"""Energy-condition classification for BEAM-SSZ candidates."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CandidateClass(str, Enum):
    SSZ_CANONICAL = "SSZ_CANONICAL"
    SSZ_EFFECTIVE_ONLY = "SSZ_EFFECTIVE_ONLY"
    GR_EXOTIC = "GR_EXOTIC"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class EnergyConditionReport:
    candidate_class: CandidateClass
    nec_satisfied: bool
    sec_satisfied: bool | None
    requires_exotic_matter: bool
    notes: tuple[str, ...]


def classify_energy_conditions(
    *,
    nec_satisfied: bool,
    sec_satisfied: bool | None = None,
    claims_traversable_wormhole: bool = False,
    claims_warp_drive: bool = False,
    effective_only: bool = False,
) -> EnergyConditionReport:
    notes: list[str] = []
    if claims_warp_drive or claims_traversable_wormhole:
        notes.append("Warp/traversable-wormhole claim is not canonical SSZ under NEC-satisfied guardrail.")
    if not nec_satisfied:
        notes.append("NEC violation required: classify as GR_EXOTIC, not canonical SSZ.")
        return EnergyConditionReport(CandidateClass.GR_EXOTIC, False, sec_satisfied, True, tuple(notes))
    if claims_warp_drive or claims_traversable_wormhole:
        return EnergyConditionReport(CandidateClass.REJECTED, True, sec_satisfied, False, tuple(notes))
    if effective_only:
        notes.append("Effective-distance diagnostic only; no physical metric actuator claim.")
        return EnergyConditionReport(CandidateClass.SSZ_EFFECTIVE_ONLY, True, sec_satisfied, False, tuple(notes))
    if sec_satisfied is False:
        notes.append("SEC violation can be SSZ-compatible in strong field; NEC remains the hard line.")
    return EnergyConditionReport(CandidateClass.SSZ_CANONICAL, True, sec_satisfied, False, tuple(notes))


def check_energy_conditions(xi: float, energy_density: float = 1.0, pressure: float = 0.0) -> dict:
    """Check energy conditions for SSZ metric.
    
    Args:
        xi: SSZ parameter
        energy_density: Energy density rho
        pressure: Pressure p
        
    Returns:
        Dict with energy condition checks
    """
    # NEC: rho + p >= 0
    nec = energy_density + pressure >= 0
    # WEC: rho >= 0 and NEC
    wec = energy_density >= 0 and nec
    # SEC: rho + 3p >= 0 and WEC
    sec = energy_density + 3*pressure >= 0 and wec
    # DEC: |p| <= rho and WEC
    dec = abs(pressure) <= energy_density and wec
    
    return {
        "nec_satisfied": nec,
        "wec_satisfied": wec,
        "sec_satisfied": sec,
        "dec_satisfied": dec,
        "xi": xi,
        "rho": energy_density,
        "p": pressure,
    }
