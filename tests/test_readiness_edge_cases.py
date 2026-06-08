"""Edge case tests for readiness score module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.real_beam_readiness_score import (
    RealBeamReadinessScorer,
    ReadinessLevel,
)


def test_readiness_all_zeros():
    """Test readiness with all zero scores."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.0,
        ssz_guardrails=0.0,
        no_go_compliance=0.0,
    )
    
    assert report.overall_level == ReadinessLevel.NOT_READY
    assert len(report.blockers) > 0


def test_readiness_all_perfect():
    """Test readiness with all perfect scores."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=1.0,
        ssz_guardrails=1.0,
        no_go_compliance=1.0,
        energy_condition_status=1.0,
        causality_status=1.0,
        tidal_status=1.0,
        experimental_ladder_level=5,
        reproducibility_level=1.0,
    )
    
    # Should be at least macroscopic ready
    assert report.overall_level in [
        ReadinessLevel.MACROSCOPIC_INERT_TEST_READY,
        ReadinessLevel.HUMAN_TRANSFER_NOT_ALLOWED,
    ]


def test_readiness_boundary_scores():
    """Test readiness at boundary scores (0.5, 0.8, 0.95, 0.99, 1.0)."""
    boundaries = [0.5, 0.8, 0.95, 0.99, 1.0]
    
    for score in boundaries:
        report = RealBeamReadinessScorer.assess_readiness(
            math_consistency=score,
            ssz_guardrails=score,
            no_go_compliance=score,
        )
        
        # Should not crash and should return valid report
        assert report is not None
        assert report.overall_level is not None


def test_readiness_negative_level():
    """Test readiness with negative experimental ladder level."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.9,
        ssz_guardrails=0.9,
        no_go_compliance=0.9,
        experimental_ladder_level=-1,
    )
    
    # Should handle gracefully
    assert "INVALID" in report.axes["experimental_ladder"].status or \
           report.overall_level == ReadinessLevel.NOT_READY


def test_readiness_very_high_level():
    """Test readiness with very high experimental ladder level."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.9,
        ssz_guardrails=0.9,
        no_go_compliance=0.9,
        experimental_ladder_level=100,  # Unreasonably high
    )
    
    # Should be forbidden or not ready
    assert report.overall_level in [
        ReadinessLevel.HUMAN_TRANSFER_NOT_ALLOWED,
        ReadinessLevel.NOT_READY,
    ]


def test_readiness_single_blocker():
    """Test that one blocker causes NOT_READY."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.4,  # Only this fails
        ssz_guardrails=0.95,
        no_go_compliance=0.95,
        energy_condition_status=0.9,
        causality_status=0.9,
        tidal_status=0.9,
        experimental_ladder_level=2,
    )
    
    assert report.overall_level == ReadinessLevel.NOT_READY
    assert "Mathematical inconsistencies" in str(report.blockers)


def test_readiness_exact_thresholds():
    """Test readiness at exact threshold values."""
    # At exactly 0.5, should be blocker
    report_49 = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.49,
    )
    assert report_49.overall_level == ReadinessLevel.NOT_READY
    
    # At exactly 0.5, should also be blocker
    report_50 = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.50,
    )
    assert report_50.overall_level == ReadinessLevel.NOT_READY
    
    # Just above 0.5, should not have that blocker
    report_51 = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.51,
        ssz_guardrails=0.9,
        no_go_compliance=0.9,
    )
    # Should not have math_consistency blocker
    blockers_str = str(report_51.blockers)
    assert "Mathematical inconsistencies" not in blockers_str or report_51.blockers == ()


def test_required_scores_all_levels():
    """Test that all readiness levels have required scores."""
    levels = [
        ReadinessLevel.NOT_READY,
        ReadinessLevel.FOUNDATIONAL_ONLY,
        ReadinessLevel.PHOTON_TEST_READY,
        ReadinessLevel.ATOMIC_TEST_READY,
        ReadinessLevel.MESOSCOPIC_TEST_READY,
        ReadinessLevel.MACROSCOPIC_INERT_TEST_READY,
        ReadinessLevel.HUMAN_TRANSFER_NOT_ALLOWED,
    ]
    
    for level in levels:
        required = RealBeamReadinessScorer.get_required_scores_for_level(level)
        assert isinstance(required, dict)
        # All required scores should be between 0 and 1
        for key, value in required.items():
            assert 0.0 <= value <= 1.0


def test_experimental_ladder_score_calculation():
    """Test experimental ladder score is calculated correctly."""
    for level in range(0, 6):
        report = RealBeamReadinessScorer.assess_readiness(
            experimental_ladder_level=level,
        )
        
        expected_score = min(level / 5.0, 1.0)
        actual_score = report.axes["experimental_ladder"].score
        assert abs(actual_score - expected_score) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
