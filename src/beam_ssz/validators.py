"""Candidate validation reports."""
from __future__ import annotations

from dataclasses import dataclass

from .bridge_candidate import BridgeCandidate
from .energy_conditions import CandidateClass


@dataclass(frozen=True)
class ValidationReport:
    candidate_id: str
    passed: bool
    candidate_class: CandidateClass
    failures: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_candidate(candidate: BridgeCandidate, *, max_compression_ratio: float = 1e-3) -> ValidationReport:
    failures: list[str] = []
    warnings: list[str] = list(candidate.energy.notes)

    if candidate.compression_ratio > max_compression_ratio:
        failures.append("effective distance not sufficiently compressed")
    if candidate.max_tidal_delta_a > candidate.tidal_limit:
        failures.append("tidal acceleration exceeds safety limit")
    if not candidate.worldline.has_positive_proper_time():
        failures.append("proper time is not positive")
    if not candidate.worldline.is_continuous():
        failures.append("worldline discontinuity exceeds tolerance")
    if not candidate.worldline.has_no_ctc_flag():
        failures.append("closed timelike curve flag present")
    if candidate.singularity_flag:
        failures.append("singularity flag present")
    if candidate.energy.candidate_class in {CandidateClass.GR_EXOTIC, CandidateClass.REJECTED}:
        failures.append(f"energy/classification gate failed: {candidate.energy.candidate_class.value}")

    return ValidationReport(
        candidate_id=candidate.candidate_id,
        passed=not failures,
        candidate_class=candidate.energy.candidate_class,
        failures=tuple(failures),
        warnings=tuple(warnings),
    )
