"""Candidate classification matrix for bridge candidates.

This module implements a classification system for metric bridge candidates
based on their mathematical and physical properties.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .metric_bridge import BridgeCandidate
from .no_go_filters import NoGoFilters, NoGoFilterResult


class CandidateClass(str, Enum):
    """Classification categories for bridge candidates."""
    SSZ_CANONICAL_PASS = "SSZ_CANONICAL_PASS"
    SSZ_CANONICAL_FAIL = "SSZ_CANONICAL_FAIL"
    SSZ_EXTENSION_PASS = "SSZ_EXTENSION_PASS"
    SSZ_EXTENSION_FAIL = "SSZ_EXTENSION_FAIL"
    GR_EXOTIC_PASS = "GR_EXOTIC_PASS"
    GR_EXOTIC_FAIL = "GR_EXOTIC_FAIL"
    TOY_MODEL_PASS = "TOY_MODEL_PASS"
    TOY_MODEL_FAIL = "TOY_MODEL_FAIL"
    INCONSISTENT = "INCONSISTENT"


@dataclass(frozen=True)
class ClassificationReport:
    """Report from candidate classification."""
    candidate_id: str
    candidate_class: CandidateClass
    canonical: bool
    nec_satisfied: bool
    ctc_free: bool
    singularity_free: bool
    worldline_continuous: bool
    tidal_safe: bool
    reduction_significant: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


class CandidateClassifier:
    """Classifier for metric bridge candidates."""
    
    # Tidal safety threshold (m/s^2)
    TIDAL_THRESHOLD = 1e6  # 1 million m/s^2 (very conservative)
    
    # Significant reduction threshold
    REDUCTION_THRESHOLD = 0.5  # 50% reduction
    
    @staticmethod
    def classify(
        candidate: BridgeCandidate,
        requires_nec_violation: bool = False,
        is_toy_model: bool = False,
        candidate_id: str = "unknown",
    ) -> ClassificationReport:
        """Classify a bridge candidate.
        
        Args:
            candidate: Bridge candidate to classify
            requires_nec_violation: Whether candidate requires NEC violation
            is_toy_model: Whether this is a toy model
            candidate_id: Identifier for the candidate
            
        Returns:
            ClassificationReport with full classification
        """
        reasons: list[str] = []
        warnings: list[str] = []
        
        # Basic checks
        canonical = not requires_nec_violation
        nec_satisfied = not requires_nec_violation
        ctc_free = not candidate.ctc_flag
        singularity_free = not candidate.singularity_flag
        worldline_continuous = candidate.worldline_continuous
        tidal_safe = candidate.tidal_max < CandidateClassifier.TIDAL_THRESHOLD
        reduction_significant = candidate.reduction_factor < CandidateClassifier.REDUCTION_THRESHOLD
        
        # Determine classification
        if is_toy_model:
            base_class = CandidateClass.TOY_MODEL_PASS
            reasons.append("Toy model for testing purposes")
        elif requires_nec_violation:
            base_class = CandidateClass.GR_EXOTIC_PASS
            reasons.append("Requires NEC violation - classified as GR_EXOTIC")
        else:
            base_class = CandidateClass.SSZ_CANONICAL_PASS
            reasons.append("Canonical SSZ formulation")
        
        # Check for failures
        if not worldline_continuous:
            if candidate.ctc_flag:
                reasons.append("FAIL: Closed timelike curve detected")
                base_class = CandidateClass.INCONSISTENT
            if candidate.singularity_flag:
                reasons.append("FAIL: Singularity detected")
                base_class = CandidateClass.INCONSISTENT
        
        if not tidal_safe:
            warnings.append(f"Tidal acceleration {candidate.tidal_max:.2e} m/s^2 exceeds threshold")
        
        if not reduction_significant:
            warnings.append(f"Reduction factor {candidate.reduction_factor:.3f} not significant")
        
        # Update classification based on checks
        if base_class == CandidateClass.SSZ_CANONICAL_PASS:
            if not worldline_continuous:
                base_class = CandidateClass.SSZ_CANONICAL_FAIL
        elif base_class == CandidateClass.GR_EXOTIC_PASS:
            if not worldline_continuous:
                base_class = CandidateClass.GR_EXOTIC_FAIL
        elif base_class == CandidateClass.TOY_MODEL_PASS:
            if not worldline_continuous:
                base_class = CandidateClass.TOY_MODEL_FAIL
        
        # Add success reasons
        if worldline_continuous:
            reasons.append("Worldline continuity satisfied")
        if tidal_safe:
            reasons.append("Tidal forces within safety threshold")
        if reduction_significant:
            reasons.append(f"Significant distance reduction: {candidate.reduction_factor:.3f}")
        
        return ClassificationReport(
            candidate_id=candidate_id,
            candidate_class=base_class,
            canonical=canonical,
            nec_satisfied=nec_satisfied,
            ctc_free=ctc_free,
            singularity_free=singularity_free,
            worldline_continuous=worldline_continuous,
            tidal_safe=tidal_safe,
            reduction_significant=reduction_significant,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )
    
    @staticmethod
    def classify_with_no_go_filters(
        candidate: BridgeCandidate,
        requires_nec_violation: bool = False,
        is_toy_model: bool = False,
        scan_copy_model: bool = False,
        unknown_quantum_copy: bool = False,
        claim_human_identity: bool = False,
        destructive: bool = False,
        superluminal: bool = False,
        biological_experiment: bool = False,
        candidate_id: str = "unknown",
    ) -> ClassificationReport:
        """Classify a candidate with full no-go filter analysis.
        
        Args:
            candidate: Bridge candidate to classify
            requires_nec_violation: Whether candidate requires NEC violation
            is_toy_model: Whether this is a toy model
            scan_copy_model: Whether model uses scan/copy
            unknown_quantum_copy: Whether it copies unknown quantum states
            claim_human_identity: Whether it claims human identity preservation
            destructive: Whether process is destructive
            superluminal: Whether signals are superluminal
            biological_experiment: Whether biological systems involved
            candidate_id: Identifier for the candidate
            
        Returns:
            ClassificationReport with full classification including no-go filters
        """
        # First, run basic classification
        report = CandidateClassifier.classify(
            candidate,
            requires_nec_violation,
            is_toy_model,
            candidate_id,
        )
        
        # Run no-go filters
        claimed_class = "SSZ_CANONICAL" if not requires_nec_violation else "GR_EXOTIC"
        no_go_reports = NoGoFilters.run_all_filters(
            scan_copy_model=scan_copy_model,
            unknown_quantum_state_copy=unknown_quantum_copy,
            claim_human_identity=claim_human_identity,
            destructive=destructive,
            superluminal_signal=superluminal,
            nec_violation=requires_nec_violation,
            claimed_classification=claimed_class,
            biological_experiment=biological_experiment,
        )
        
        overall_no_go = NoGoFilters.get_overall_result(no_go_reports)
        
        # Update classification based on no-go filters
        if overall_no_go == NoGoFilterResult.FAIL:
            report = ClassificationReport(
                candidate_id=report.candidate_id,
                candidate_class=CandidateClass.INCONSISTENT,
                canonical=report.canonical,
                nec_satisfied=report.nec_satisfied,
                ctc_free=report.ctc_free,
                singularity_free=report.singularity_free,
                worldline_continuous=False,
                tidal_safe=report.tidal_safe,
                reduction_significant=report.reduction_significant,
                reasons=tuple(list(report.reasons) + ["FAIL: No-go theorem violation"]),
                warnings=tuple(list(report.warnings) + [r.details for r in no_go_reports if r.result == NoGoFilterResult.FAIL]),
            )
        elif overall_no_go == NoGoFilterResult.EXOTIC:
            report = ClassificationReport(
                candidate_id=report.candidate_id,
                candidate_class=CandidateClass.GR_EXOTIC_PASS if report.candidate_class != CandidateClass.INCONSISTENT else report.candidate_class,
                canonical=False,
                nec_satisfied=False,
                ctc_free=report.ctc_free,
                singularity_free=report.singularity_free,
                worldline_continuous=report.worldline_continuous,
                tidal_safe=report.tidal_safe,
                reduction_significant=report.reduction_significant,
                reasons=tuple(list(report.reasons) + ["Classified as GR_EXOTIC due to no-go filter"]),
                warnings=tuple(list(report.warnings) + [r.details for r in no_go_reports if r.result == NoGoFilterResult.EXOTIC]),
            )
        elif overall_no_go == NoGoFilterResult.WARNING:
            report = ClassificationReport(
                candidate_id=report.candidate_id,
                candidate_class=report.candidate_class,
                canonical=report.canonical,
                nec_satisfied=report.nec_satisfied,
                ctc_free=report.ctc_free,
                singularity_free=report.singularity_free,
                worldline_continuous=report.worldline_continuous,
                tidal_safe=report.tidal_safe,
                reduction_significant=report.reduction_significant,
                reasons=report.reasons,
                warnings=tuple(list(report.warnings) + [r.details for r in no_go_reports if r.result == NoGoFilterResult.WARNING]),
            )
        
        return report


# Fix typo in constant
CandidateClassifier.REDUCTION_THRESHOLD = 0.5


def classify_candidate(candidate_id: str = "test_candidate", **kwargs) -> ClassificationReport:
    """Convenience function to classify a bridge candidate.
    
    Args:
        candidate_id: Candidate identifier
        **kwargs: Additional classification parameters
        
    Returns:
        ClassificationReport with results
    """
    classifier = CandidateClassifier()
    report = classifier.classify(
        candidate_id=candidate_id,
        canonical=True,
        nec_satisfied=kwargs.get("nec_satisfied", True),
        ctc_free=kwargs.get("ctc_free", True),
        singularity_free=kwargs.get("singularity_free", True),
        worldline_continuous=kwargs.get("worldline_continuous", True),
        tidal_safe=kwargs.get("tidal_safe", True),
        reduction_significant=kwargs.get("reduction_significant", True),
    )
    return report
