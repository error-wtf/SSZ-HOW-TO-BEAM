"""No-go theorem filters for mathematical diagnosis.

This module implements mathematical filters based on no-go theorems.
These are NOT moral prohibitions - they are mathematical consistency checks.
A FAIL means the hypothesis is mathematically/physically inconsistent under the given assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Energy conditions module provides CandidateClass and EnergyConditionReport
# Used for consistency in classification


class NoGoFilterResult(str, Enum):
    """Result of a no-go filter check."""
    PASS = "PASS"
    WARNING = "WARNING"
    NON_CANONICAL = "NON_CANONICAL"
    EXOTIC = "EXOTIC"
    FAIL = "FAIL"


@dataclass(frozen=True)
class NoGoFilterReport:
    """Report from no-go filter analysis."""
    filter_name: str
    result: NoGoFilterResult
    details: str
    classification: str


class NoGoFilters:
    """Mathematical filters based on no-go theorems."""
    
    @staticmethod
    def check_no_cloning_violation(
        scan_copy_model: bool,
        unknown_quantum_state_copy: bool,
    ) -> NoGoFilterReport:
        """Check for no-cloning theorem violation.
        
        Args:
            scan_copy_model: Whether the model uses scan/copy
            unknown_quantum_state_copy: Whether it copies unknown quantum states
            
        Returns:
            NoGoFilterReport with analysis
        """
        if unknown_quantum_state_copy:
            return NoGoFilterReport(
                filter_name="no_cloning",
                result=NoGoFilterResult.FAIL,
                details="Unknown quantum states cannot be perfectly copied (no-cloning theorem)",
                classification="QUANTUM_INFORMATION_FAIL",
            )
        
        if scan_copy_model:
            return NoGoFilterReport(
                filter_name="no_cloning",
                result=NoGoFilterResult.WARNING,
                details="Scan/copy model requires verification of quantum state handling",
                classification="REQUIRES_VERIFICATION",
            )
        
        return NoGoFilterReport(
            filter_name="no_cloning",
            result=NoGoFilterResult.PASS,
            details="No quantum cloning violation detected",
            classification="PASS",
        )
    
    @staticmethod
    def check_scan_copy_identity_break(
        scan_copy_model: bool,
        claim_human_identity: bool,
    ) -> NoGoFilterReport:
        """Check if scan/copy breaks identity continuity.
        
        Args:
            scan_copy_model: Whether the model uses scan/copy
            claim_human_identity: Whether it claims to preserve human identity
            
        Returns:
            NoGoFilterReport with analysis
        """
        if scan_copy_model and claim_human_identity:
            return NoGoFilterReport(
                filter_name="identity_continuity",
                result=NoGoFilterResult.FAIL,
                details="Scan/copy reconstruction cannot guarantee identity continuity",
                classification="IDENTITY_FAIL",
            )
        
        return NoGoFilterReport(
            filter_name="identity_continuity",
            result=NoGoFilterResult.PASS,
            details="Identity continuity not violated",
            classification="PASS",
        )
    
    @staticmethod
    def check_destructive_reconstruction(
        destructive: bool,
    ) -> NoGoFilterReport:
        """Check for destructive reconstruction.
        
        Args:
            destructive: Whether the process is destructive
            
        Returns:
            NoGoFilterReport with analysis
        """
        if destructive:
            return NoGoFilterReport(
                filter_name="destructive",
                result=NoGoFilterResult.FAIL,
                details="Destructive reconstruction violates continuity requirement",
                classification="DESTRUCTIVE_FAIL",
            )
        
        return NoGoFilterReport(
            filter_name="destructive",
            result=NoGoFilterResult.PASS,
            details="Non-destructive process",
            classification="PASS",
        )
    
    @staticmethod
    def check_faster_than_light_signal(
        superluminal_signal: bool,
    ) -> NoGoFilterReport:
        """Check for faster-than-light signal propagation.
        
        Args:
            superluminal_signal: Whether signals travel faster than light
            
        Returns:
            NoGoFilterReport with analysis
        """
        if superluminal_signal:
            return NoGoFilterReport(
                filter_name="ftl_signal",
                result=NoGoFilterResult.FAIL,
                details="Faster-than-light signal violates causality",
                classification="CAUSALITY_FAIL",
            )
        
        return NoGoFilterReport(
            filter_name="ftl_signal",
            result=NoGoFilterResult.PASS,
            details="No superluminal signal propagation",
            classification="PASS",
        )
    
    @staticmethod
    def check_nec_violation_classification(
        nec_violation: bool,
        claimed_classification: str,
    ) -> NoGoFilterReport:
        """Check if NEC violation matches claimed classification.
        
        Args:
            nec_violation: Whether NEC is violated
            claimed_classification: The claimed classification (e.g., SSZ_CANONICAL)
            
        Returns:
            NoGoFilterReport with analysis
        """
        if nec_violation and claimed_classification == "SSZ_CANONICAL":
            return NoGoFilterReport(
                filter_name="nec_classification",
                result=NoGoFilterResult.FAIL,
                details="NEC violation incompatible with SSZ_CANONICAL classification",
                classification="CLASSIFICATION_MISMATCH",
            )
        
        if nec_violation:
            return NoGoFilterReport(
                filter_name="nec_classification",
                result=NoGoFilterResult.EXOTIC,
                details="NEC violation requires GR_EXOTIC or SSZ_EXTENSION classification",
                classification="GR_EXOTIC",
            )
        
        return NoGoFilterReport(
            filter_name="nec_classification",
            result=NoGoFilterResult.PASS,
            details="NEC satisfied, compatible with canonical classification",
            classification="PASS",
        )
    
    @staticmethod
    def check_biological_experiment_claim(
        biological_experiment: bool,
        current_readiness_level: str,
    ) -> NoGoFilterReport:
        """Check if biological experiment claims are appropriate.
        
        Args:
            biological_experiment: Whether biological systems are involved
            current_readiness_level: Current experimental readiness level
            
        Returns:
            NoGoFilterReport with analysis
        """
        if biological_experiment:
            if current_readiness_level in ["FOUNDATIONAL_ONLY", "PHOTON_TEST_READY", "ATOMIC_TEST_READY"]:
                return NoGoFilterReport(
                    filter_name="biological_experiment",
                    result=NoGoFilterResult.FAIL,
                    details="Biological experiments require prior validation at lower levels",
                    classification="READINESS_FAIL",
                )
            
            return NoGoFilterReport(
                filter_name="biological_experiment",
                result=NoGoFilterResult.WARNING,
                details="Biological experiments require ethics/legal review",
                classification="REQUIRES_REVIEW",
            )
        
        return NoGoFilterReport(
            filter_name="biological_experiment",
            result=NoGoFilterResult.PASS,
            details="No biological systems involved",
            classification="PASS",
        )
    
    @staticmethod
    def run_all_filters(
        scan_copy_model: bool = False,
        unknown_quantum_state_copy: bool = False,
        claim_human_identity: bool = False,
        destructive: bool = False,
        superluminal_signal: bool = False,
        nec_violation: bool = False,
        claimed_classification: str = "SSZ_CANONICAL",
        biological_experiment: bool = False,
        current_readiness_level: str = "FOUNDATIONAL_ONLY",
    ) -> list[NoGoFilterReport]:
        """Run all no-go filters and return reports.
        
        Args:
            scan_copy_model: Whether the model uses scan/copy
            unknown_quantum_state_copy: Whether it copies unknown quantum states
            claim_human_identity: Whether it claims to preserve human identity
            destructive: Whether the process is destructive
            superluminal_signal: Whether signals travel faster than light
            nec_violation: Whether NEC is violated
            claimed_classification: The claimed classification
            biological_experiment: Whether biological systems are involved
            current_readiness_level: Current experimental readiness level
            
        Returns:
            List of NoGoFilterReport objects
        """
        reports = [
            NoGoFilters.check_no_cloning_violation(scan_copy_model, unknown_quantum_state_copy),
            NoGoFilters.check_scan_copy_identity_break(scan_copy_model, claim_human_identity),
            NoGoFilters.check_destructive_reconstruction(destructive),
            NoGoFilters.check_faster_than_light_signal(superluminal_signal),
            NoGoFilters.check_nec_violation_classification(nec_violation, claimed_classification),
            NoGoFilters.check_biological_experiment_claim(biological_experiment, current_readiness_level),
        ]
        return reports
    
    @staticmethod
    def get_overall_result(reports: list[NoGoFilterReport]) -> NoGoFilterResult:
        """Determine overall result from all filter reports.
        
        Args:
            reports: List of NoGoFilterReport objects
            
        Returns:
            Overall NoGoFilterResult
        """
        if any(r.result == NoGoFilterResult.FAIL for r in reports):
            return NoGoFilterResult.FAIL
        if any(r.result == NoGoFilterResult.EXOTIC for r in reports):
            return NoGoFilterResult.EXOTIC
        if any(r.result == NoGoFilterResult.NON_CANONICAL for r in reports):
            return NoGoFilterResult.NON_CANONICAL
        if any(r.result == NoGoFilterResult.WARNING for r in reports):
            return NoGoFilterResult.WARNING
        return NoGoFilterResult.PASS
