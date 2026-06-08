"""Experimental ladder for real-beaming research.

This module defines a staged approach to experimental validation,
starting with harmless test systems and progressing cautiously.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from typing import List


class ExperimentLevel(str, Enum):
    """Levels of experimental readiness."""
    LEVEL_0_FOUNDATIONAL = "LEVEL_0_FOUNDATIONAL"
    LEVEL_1_PHOTON = "LEVEL_1_PHOTON"
    LEVEL_2_ATOMIC_CLOCK = "LEVEL_2_ATOMIC_CLOCK"
    LEVEL_3_COLD_ATOM = "LEVEL_3_COLD_ATOM"
    LEVEL_4_MESOSCOPIC = "LEVEL_4_MESOSCOPIC"
    LEVEL_5_MACROSCOPIC_INERT = "LEVEL_5_MACROSCOPIC_INERT"
    LEVEL_6_BIOLOGICAL_FORBIDDEN = "LEVEL_6_BIOLOGICAL_FORBIDDEN"


@dataclass(frozen=True)
class ExperimentStage:
    """Definition of an experimental stage."""
    level: ExperimentLevel
    name: str
    description: str
    required_observables: tuple[str, ...]
    allowed_test_systems: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    pass_criteria: tuple[str, ...]
    failure_criteria: tuple[str, ...]


class ExperimentLadder:
    """Experimental ladder for real-beaming research."""
    
    STAGES = {
        ExperimentLevel.LEVEL_0_FOUNDATIONAL: ExperimentStage(
            level=ExperimentLevel.LEVEL_0_FOUNDATIONAL,
            name="Mathematical Consistency",
            description="Mathematical consistency only - no physical experiments",
            required_observables=(
                "Metric regularity",
                "Energy condition analysis",
                "Causality checks",
                "Geodesic completeness",
            ),
            allowed_test_systems=("Mathematical models",),
            forbidden_claims=(
                "Physical implementation",
                "Experimental validation",
                "Technology readiness",
            ),
            pass_criteria=(
                "All mathematical checks pass",
                "No inconsistencies found",
                "Formulas are well-defined",
            ),
            failure_criteria=(
                "Mathematical inconsistencies",
                "Singularities in claimed finite regions",
                "Causality violations",
            ),
        ),
        ExperimentLevel.LEVEL_1_PHOTON: ExperimentStage(
            level=ExperimentLevel.LEVEL_1_PHOTON,
            name="Photon/Frequency Phase Tests",
            description="Photon and frequency/phase measurements",
            required_observables=(
                "Phase shift",
                "Frequency shift",
                "Interference patterns",
                "Coherence time",
            ),
            allowed_test_systems=(
                "Photons",
                "Laser systems",
                "Interferometers",
                "Optical cavities",
            ),
            forbidden_claims=(
                "Matter transport",
                "Information transfer beyond classical limits",
                "Human applications",
            ),
            pass_criteria=(
                "Phase shifts match predictions",
                "Coherence preserved",
                "No unexplained losses",
            ),
            failure_criteria=(
                "Phase shifts inconsistent with theory",
                "Coherence degradation unexplained",
                "Unexpected losses",
            ),
        ),
        ExperimentLevel.LEVEL_2_ATOMIC_CLOCK: ExperimentStage(
            level=ExperimentLevel.LEVEL_2_ATOMIC_CLOCK,
            name="Atomic Clock/Interferometer Tests",
            description="Atomic clock and interferometer precision tests",
            required_observables=(
                "Clock rate differences",
                "Interference fringe shifts",
                "Time dilation effects",
                "Precision timing",
            ),
            allowed_test_systems=(
                "Atomic clocks",
                "Interferometers",
                "Precision timing systems",
                "Optical atomic clocks",
            ),
            forbidden_claims=(
                "Matter transport",
                "Human applications",
                "Biological systems",
            ),
            pass_criteria=(
                "Clock rate differences match predictions",
                "Fringe shifts consistent",
                "Timing precision maintained",
            ),
            failure_criteria=(
                "Clock rate deviations unexplained",
                "Fringe shifts inconsistent",
                "Timing degradation",
            ),
        ),
        ExperimentLevel.LEVEL_3_COLD_ATOM: ExperimentStage(
            level=ExperimentLevel.LEVEL_3_COLD_ATOM,
            name="Cold Atom Coherence Tests",
            description="Cold atom and BEC coherence experiments",
            required_observables=(
                "Quantum coherence",
                "BEC properties",
                "Atom interferometry",
                "Collective behavior",
            ),
            allowed_test_systems=(
                "Cold atoms",
                "Bose-Einstein condensates",
                "Atom interferometers",
                "Ultracold gases",
            ),
            forbidden_claims=(
                "Macroscopic object transport",
                "Human applications",
                "Biological systems",
            ),
            pass_criteria=(
                "Coherence preserved",
                "BEC properties maintained",
                "Interference patterns stable",
            ),
            failure_criteria=(
                "Coherence loss unexplained",
                "BEC degradation",
                "Interference instability",
            ),
        ),
        ExperimentLevel.LEVEL_4_MESOSCOPIC: ExperimentStage(
            level=ExperimentLevel.LEVEL_4_MESOSCOPIC,
            name="Mesoscopic Coherence/Mechanical Oscillator Tests",
            description="Mesoscopic coherence and mechanical oscillator tests",
            required_observables=(
                "Mechanical oscillator coherence",
                "Mesoscopic quantum effects",
                "Coupling efficiency",
                "Decoherence rates",
            ),
            allowed_test_systems=(
                "Mechanical oscillators",
                "Mesoscopic systems",
                "Nanomechanical resonators",
                "Optomechanical systems",
            ),
            forbidden_claims=(
                "Macroscopic object transport",
                "Human applications",
                "Biological systems",
            ),
            pass_criteria=(
                "Oscillator coherence maintained",
                "Coupling efficient",
                "Decoherence within limits",
            ),
            failure_criteria=(
                "Coherence loss excessive",
                "Coupling inefficient",
                "Decoherence too rapid",
            ),
        ),
        ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT: ExperimentStage(
            level=ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT,
            name="Macroscopic Inert Matter Only",
            description="Macroscopic inert matter tests (non-biological)",
            required_observables=(
                "Structural integrity",
                "Material properties",
                "Thermal effects",
                "Stress analysis",
            ),
            allowed_test_systems=(
                "Inert materials",
                "Non-living macroscopic objects",
                "Test masses",
                "Reference materials",
            ),
            forbidden_claims=(
                "Human applications",
                "Biological systems",
                "Living organisms",
            ),
            pass_criteria=(
                "Structural integrity maintained",
                "Material properties unchanged",
                "Thermal effects manageable",
                "Stress within limits",
            ),
            failure_criteria=(
                "Structural failure",
                "Material degradation",
                "Thermal damage",
                "Stress exceed limits",
            ),
        ),
        ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN: ExperimentStage(
            level=ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN,
            name="Biological Systems - FORBIDDEN",
            description="Biological system experiments are FORBIDDEN until all prior levels pass and ethics/legal review exists",
            required_observables=(),
            allowed_test_systems=(),
            forbidden_claims=(
                "Human transfer",
                "Biological experiments",
                "Living organism transport",
                "Any biological application",
            ),
            pass_criteria=(),
            failure_criteria=(
                "Any attempt without full prior validation",
                "Any attempt without ethics/legal review",
                "Any attempt without medical oversight",
            ),
        ),
    }
    
    @staticmethod
    def get_stage(level: ExperimentLevel) -> ExperimentStage:
        """Get the definition for an experimental stage.
        
        Args:
            level: Experiment level
            
        Returns:
            ExperimentStage definition
        """
        return ExperimentLadder.STAGES[level]
    
    @staticmethod
    def get_all_levels() -> List[ExperimentLevel]:
        """Get all experimental levels in order.
        
        Returns:
            List of ExperimentLevel in ascending order
        """
        return [
            ExperimentLevel.LEVEL_0_FOUNDATIONAL,
            ExperimentLevel.LEVEL_1_PHOTON,
            ExperimentLevel.LEVEL_2_ATOMIC_CLOCK,
            ExperimentLevel.LEVEL_3_COLD_ATOM,
            ExperimentLevel.LEVEL_4_MESOSCOPIC,
            ExperimentLevel.LEVEL_5_MACROSCOPIC_INERT,
            ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN,
        ]
    
    @staticmethod
    def can_progress_to(current_level: ExperimentLevel, target_level: ExperimentLevel) -> bool:
        """Check if progression to target level is allowed.
        
        Args:
            current_level: Current experimental level
            target_level: Target experimental level
            
        Returns:
            True if progression is allowed, False otherwise
        """
        levels = ExperimentLadder.get_all_levels()
        
        try:
            current_idx = levels.index(current_level)
            target_idx = levels.index(target_level)
        except ValueError:
            return False
        
        # Can only progress to adjacent levels
        if target_idx != current_idx + 1:
            return False
        
        # Biological level is always forbidden
        if target_level == ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN:
            return False
        
        return True
    
    @staticmethod
    def is_level_allowed(level: ExperimentLevel) -> bool:
        """Check if a level is currently allowed.
        
        Args:
            level: Experiment level to check
            
        Returns:
            True if level is allowed, False otherwise
        """
        return level != ExperimentLevel.LEVEL_6_BIOLOGICAL_FORBIDDEN
