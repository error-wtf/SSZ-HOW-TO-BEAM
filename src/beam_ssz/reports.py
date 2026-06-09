"""Markdown report generation."""
from __future__ import annotations

from .bridge_candidate import BridgeCandidate
from .validators import ValidationReport


def render_candidate_report(candidate: BridgeCandidate, report: ValidationReport) -> str:
    failures = "\n".join(f"- {item}" for item in report.failures) or "- none"
    warnings = "\n".join(f"- {item}" for item in report.warnings) or "- none"
    return f"""# BEAM-SSZ Candidate Report: {candidate.candidate_id}

## Summary

- Result: {'PASS' if report.passed else 'REJECT'}
- Candidate class: {report.candidate_class.value}
- Compression ratio: {candidate.compression_ratio:.6e}
- Effective distance: {candidate.effective_distance:.6e}
- Normal distance: {candidate.normal_distance:.6e}
- Max tidal acceleration proxy: {candidate.max_tidal_delta_a:.6e}
- Tidal limit: {candidate.tidal_limit:.6e}
- Proper time delta: {candidate.worldline.delta_tau:.6e}
- CTC flag: {candidate.worldline.closed_timelike_curve_flag}
- Singularity flag: {candidate.singularity_flag}

## Failures

{failures}

## Warnings / Notes

{warnings}
"""


# Convenience class for testing
class ReportGenerator:
    """Simple report generator wrapper."""
    
    def generate(self, candidate: BridgeCandidate, report: ValidationReport) -> str:
        """Generate report for candidate."""
        return render_candidate_report(candidate, report)
    
    def generate_summary(self, results: list) -> str:
        """Generate summary report."""
        return f"Summary: {len(results)} candidates processed"
