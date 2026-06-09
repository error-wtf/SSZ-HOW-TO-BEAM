"""Real-beam readiness score assessment.

This module provides a strict readiness assessment, not a marketing number.
It evaluates mathematical consistency, SSZ guardrails, no-go compliance,
and experimental readiness.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from typing import Dict, List


class ReadinessLevel(str, Enum):
    """Readiness levels for real-beaming research."""
    NOT_READY = "NOT_READY"
    FOUNDATIONAL_ONLY = "FOUNDATIONAL_ONLY"
    PHOTON_TEST_READY = "PHOTON_TEST_READY"
    ATOMIC_TEST_READY = "ATOMIC_TEST_READY"
    MESOSCOPIC_TEST_READY = "MESOSCOPIC_TEST_READY"
    MACROSCOPIC_INERT_TEST_READY = "MACROSCOPIC_INERT_TEST_READY"
    HUMAN_TRANSFER_NOT_ALLOWED = "HUMAN_TRANSFER_NOT_ALLOWED"


@dataclass(frozen=True)
class ReadinessAxis:
    """A single axis of readiness assessment."""
    name: str
    score: float  # 0.0 to 1.0
    status: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ReadinessReport:
    """Complete readiness assessment report."""
    overall_level: ReadinessLevel
    axes: Dict[str, ReadinessAxis]
    blockers: tuple[str, ...]
    recommendations: tuple[str, ...]
    summary: str


class RealBeamReadinessScorer:
    """Scorer for real-beaming readiness assessment."""
    
    @staticmethod
    def assess_readiness(
        math_consistency: float = 0.0,
        ssz_guardrails: float = 0.0,
        no_go_compliance: float = 0.0,
        energy_condition_status: float = 0.0,
        causality_status: float = 0.0,
        tidal_status: float = 0.0,
        experimental_ladder_level: int = 0,
        reproducibility_level: float = 0.0,
        custom_notes: Dict[str, List[str]] | None = None,
    ) -> ReadinessReport:
        """Assess overall readiness for real-beaming research.
        
        Args:
            math_consistency: Mathematical consistency score (0.0-1.0)
            ssz_guardrails: SSZ guardrails compliance score (0.0-1.0)
            no_go_compliance: No-go theorem compliance score (0.0-1.0)
            energy_condition_status: Energy condition analysis score (0.0-1.0)
            causality_status: Causality check score (0.0-1.0)
            tidal_status: Tidal safety score (0.0-1.0)
            experimental_ladder_level: Current experimental ladder level (0-5)
            reproducibility_level: Reproducibility score (0.0-1.0)
            custom_notes: Custom notes for each axis
            
        Returns:
            ReadinessReport with full assessment
        """
        notes = custom_notes or {}
        
        # Assess each axis
        axes = {}
        blockers = []
        recommendations = []
        
        # Mathematical consistency
        math_notes = tuple(notes.get("math_consistency", []))
        if math_consistency < 0.5:
            blockers.append("Mathematical inconsistencies detected")
            math_status = "FAIL"
        elif math_consistency < 0.8:
            recommendations.append("Improve mathematical consistency")
            math_status = "NEEDS_WORK"
        else:
            math_status = "PASS"
        axes["math_consistency"] = ReadinessAxis(
            name="Mathematical Consistency",
            score=math_consistency,
            status=math_status,
            notes=math_notes,
        )
        
        # SSZ guardrails
        ssz_notes = tuple(notes.get("ssz_guardrails", []))
        if ssz_guardrails < 0.5:
            blockers.append("SSZ guardrails violated")
            ssz_status = "FAIL"
        elif ssz_guardrails < 0.8:
            recommendations.append("Improve SSZ guardrails compliance")
            ssz_status = "NEEDS_WORK"
        else:
            ssz_status = "PASS"
        axes["ssz_guardrails"] = ReadinessAxis(
            name="SSZ Guardrails",
            score=ssz_guardrails,
            status=ssz_status,
            notes=ssz_notes,
        )
        
        # No-go compliance
        no_go_notes = tuple(notes.get("no_go_compliance", []))
        if no_go_compliance < 0.5:
            blockers.append("No-go theorems violated")
            no_go_status = "FAIL"
        elif no_go_compliance < 0.8:
            recommendations.append("Address no-go theorem concerns")
            no_go_status = "NEEDS_WORK"
        else:
            no_go_status = "PASS"
        axes["no_go_compliance"] = ReadinessAxis(
            name="No-Go Compliance",
            score=no_go_compliance,
            status=no_go_status,
            notes=no_go_notes,
        )
        
        # Energy conditions
        energy_notes = tuple(notes.get("energy_condition_status", []))
        if energy_condition_status < 0.5:
            blockers.append("Energy conditions problematic")
            energy_status = "FAIL"
        elif energy_condition_status < 0.8:
            recommendations.append("Clarify energy condition classification")
            energy_status = "NEEDS_WORK"
        else:
            energy_status = "PASS"
        axes["energy_conditions"] = ReadinessAxis(
            name="Energy Conditions",
            score=energy_condition_status,
            status=energy_status,
            notes=energy_notes,
        )
        
        # Causality
        causality_notes = tuple(notes.get("causality_status", []))
        if causality_status < 0.5:
            blockers.append("Causality violations detected")
            causality_status_str = "FAIL"
        elif causality_status < 0.8:
            recommendations.append("Verify causality structure")
            causality_status_str = "NEEDS_WORK"
        else:
            causality_status_str = "PASS"
        axes["causality"] = ReadinessAxis(
            name="Causality",
            score=causality_status,
            status=causality_status_str,
            notes=causality_notes,
        )
        
        # Tidal safety
        tidal_notes = tuple(notes.get("tidal_status", []))
        if tidal_status < 0.5:
            blockers.append("Tidal forces exceed safety limits")
            tidal_status_str = "FAIL"
        elif tidal_status < 0.8:
            recommendations.append("Improve tidal safety analysis")
            tidal_status_str = "NEEDS_WORK"
        else:
            tidal_status_str = "PASS"
        axes["tidal_safety"] = ReadinessAxis(
            name="Tidal Safety",
            score=tidal_status,
            status=tidal_status_str,
            notes=tidal_notes,
        )
        
        # Experimental ladder
        exp_notes = tuple(notes.get("experimental_ladder", []))
        if experimental_ladder_level < 0:
            exp_status = "INVALID"
        elif experimental_ladder_level == 0:
            exp_status = "FOUNDATIONAL"
        elif experimental_ladder_level == 1:
            exp_status = "PHOTON_READY"
        elif experimental_ladder_level == 2:
            exp_status = "ATOMIC_READY"
        elif experimental_ladder_level == 3:
            exp_status = "COLD_ATOM_READY"
        elif experimental_ladder_level == 4:
            exp_status = "MESOSCOPIC_READY"
        elif experimental_ladder_level == 5:
            exp_status = "MACROSCOPIC_READY"
        else:
            exp_status = "FORBIDDEN"
            blockers.append("Experimental level beyond allowed range")
        axes["experimental_ladder"] = ReadinessAxis(
            name="Experimental Ladder",
            score=min(experimental_ladder_level / 5.0, 1.0),
            status=exp_status,
            notes=exp_notes,
        )
        
        # Reproducibility
        repro_notes = tuple(notes.get("reproducibility", []))
        if reproducibility_level < 0.5:
            repro_status = "FAIL"
        elif reproducibility_level < 0.8:
            recommendations.append("Improve reproducibility")
            repro_status = "NEEDS_WORK"
        else:
            repro_status = "PASS"
        axes["reproducibility"] = ReadinessAxis(
            name="Reproducibility",
            score=reproducibility_level,
            status=repro_status,
            notes=repro_notes,
        )
        
        # Determine overall level
        if blockers:
            overall_level = ReadinessLevel.NOT_READY
            summary = f"NOT READY: {len(blockers)} critical blockers detected"
        elif experimental_ladder_level == 0:
            overall_level = ReadinessLevel.FOUNDATIONAL_ONLY
            summary = "FOUNDATIONAL ONLY: Mathematical consistency phase"
        elif experimental_ladder_level == 1:
            overall_level = ReadinessLevel.PHOTON_TEST_READY
            summary = "PHOTON TEST READY: Photon/frequency phase tests possible"
        elif experimental_ladder_level == 2:
            overall_level = ReadinessLevel.ATOMIC_TEST_READY
            summary = "ATOMIC TEST READY: Atomic clock/interferometer tests possible"
        elif experimental_ladder_level == 3:
            overall_level = ReadinessLevel.MESOSCOPIC_TEST_READY
            summary = "MESOSCOPIC TEST READY: Cold atom coherence tests possible"
        elif experimental_ladder_level == 4:
            overall_level = ReadinessLevel.MACROSCOPIC_INERT_TEST_READY
            summary = "MACROSCOPIC INERT TEST READY: Inert matter tests possible"
        else:
            overall_level = ReadinessLevel.HUMAN_TRANSFER_NOT_ALLOWED
            summary = "HUMAN TRANSFER NOT ALLOWED: Biological experiments require full validation and ethics/legal review"
        
        return ReadinessReport(
            overall_level=overall_level,
            axes=axes,
            blockers=tuple(blockers),
            recommendations=tuple(recommendations),
            summary=summary,
        )
    
    @staticmethod
    def get_required_scores_for_level(level: ReadinessLevel) -> Dict[str, float]:
        """Get minimum required scores for a given readiness level.
        
        Args:
            level: Target readiness level
            
        Returns:
            Dictionary of minimum required scores for each axis
        """
        if level == ReadinessLevel.NOT_READY:
            return {}
        elif level == ReadinessLevel.FOUNDATIONAL_ONLY:
            return {
                "math_consistency": 0.8,
                "ssz_guardrails": 0.8,
                "no_go_compliance": 0.8,
            }
        elif level == ReadinessLevel.PHOTON_TEST_READY:
            return {
                "math_consistency": 0.9,
                "ssz_guardrails": 0.9,
                "no_go_compliance": 0.9,
                "energy_condition_status": 0.8,
                "causality_status": 0.8,
                "tidal_status": 0.8,
                "reproducibility_level": 0.8,
            }
        elif level == ReadinessLevel.ATOMIC_TEST_READY:
            return {
                "math_consistency": 0.95,
                "ssz_guardrails": 0.95,
                "no_go_compliance": 0.95,
                "energy_condition_status": 0.9,
                "causality_status": 0.9,
                "tidal_status": 0.9,
                "reproducibility_level": 0.9,
            }
        elif level == ReadinessLevel.MESOSCOPIC_TEST_READY:
            return {
                "math_consistency": 0.98,
                "ssz_guardrails": 0.98,
                "no_go_compliance": 0.98,
                "energy_condition_status": 0.95,
                "causality_status": 0.95,
                "tidal_status": 0.95,
                "reproducibility_level": 0.95,
            }
        elif level == ReadinessLevel.MACROSCOPIC_INERT_TEST_READY:
            return {
                "math_consistency": 0.99,
                "ssz_guardrails": 0.99,
                "no_go_compliance": 0.99,
                "energy_condition_status": 0.98,
                "causality_status": 0.98,
                "tidal_status": 0.98,
                "reproducibility_level": 0.98,
            }
        else:  # HUMAN_TRANSFER_NOT_ALLOWED
            return {
                "math_consistency": 1.0,
                "ssz_guardrails": 1.0,
                "no_go_compliance": 1.0,
                "energy_condition_status": 1.0,
                "causality_status": 1.0,
                "tidal_status": 1.0,
                "reproducibility_level": 1.0,
            }


# Convenience function for testing
def calculate_readiness(**kwargs) -> dict:
    """Calculate readiness score for SSZ framework.
    
    Args:
        **kwargs: Readiness parameters
        
    Returns:
        Readiness assessment dict
    """
    scorer = RealBeamReadinessScorer()
    report = scorer.assess_readiness(**kwargs)
    return {
        "level": report.overall_level.value,
        "axes": {name: axis.score for name, axis in report.axes.items()},
        "blockers": list(report.blockers),
        "summary": report.summary,
    }
