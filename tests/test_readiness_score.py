"""Tests for real_beam_readiness_score module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.real_beam_readiness_score import (
    RealBeamReadinessScorer,
    ReadinessLevel,
    ReadinessAxis,
)


def test_assess_readiness_foundational():
    """Test readiness assessment for foundational level."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.90,
        ssz_guardrails=0.90,
        no_go_compliance=0.90,
        energy_condition_status=0.90,
        causality_status=0.90,
        tidal_status=0.90,
        experimental_ladder_level=0,
        reproducibility_level=0.90,
    )
    
    assert report.overall_level == ReadinessLevel.FOUNDATIONAL_ONLY
    assert "FOUNDATIONAL" in report.summary


def test_assess_readiness_photon():
    """Test readiness assessment for photon test level."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.95,
        ssz_guardrails=0.95,
        no_go_compliance=0.95,
        energy_condition_status=0.90,
        causality_status=0.95,
        tidal_status=0.90,
        experimental_ladder_level=1,
    )
    
    assert report.overall_level == ReadinessLevel.PHOTON_TEST_READY


def test_assess_readiness_not_ready():
    """Test readiness assessment when not ready due to blockers."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.50,  # FAIL
        ssz_guardrails=0.95,
        no_go_compliance=0.95,
        experimental_ladder_level=1,
    )
    
    assert report.overall_level == ReadinessLevel.NOT_READY
    assert len(report.blockers) > 0


def test_axis_scores_present():
    """Test that all axis scores are present in report."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.90,
        ssz_guardrails=0.90,
        no_go_compliance=0.90,
        energy_condition_status=0.85,
        causality_status=0.90,
        tidal_status=0.80,
        experimental_ladder_level=0,
        reproducibility_level=0.90,
    )
    
    assert "math_consistency" in report.axes
    assert "ssz_guardrails" in report.axes
    assert "no_go_compliance" in report.axes
    assert "energy_conditions" in report.axes
    assert "causality" in report.axes
    assert "tidal_safety" in report.axes
    assert "experimental_ladder" in report.axes
    assert "reproducibility" in report.axes


def test_axis_structure():
    """Test that axis has correct structure."""
    report = RealBeamReadinessScorer.assess_readiness()
    
    for name, axis in report.axes.items():
        assert isinstance(axis, ReadinessAxis)
        assert hasattr(axis, 'name')
        assert hasattr(axis, 'score')
        assert hasattr(axis, 'status')
        assert hasattr(axis, 'notes')
        assert 0.0 <= axis.score <= 1.0


def test_required_scores_foundational():
    """Test required scores for foundational level."""
    required = RealBeamReadinessScorer.get_required_scores_for_level(
        ReadinessLevel.FOUNDATIONAL_ONLY
    )
    
    assert "math_consistency" in required
    assert required["math_consistency"] == 0.80


def test_required_scores_photon():
    """Test required scores for photon test level."""
    required = RealBeamReadinessScorer.get_required_scores_for_level(
        ReadinessLevel.PHOTON_TEST_READY
    )
    
    assert "math_consistency" in required
    assert required["math_consistency"] == 0.90
    assert "energy_condition_status" in required


def test_required_scores_atomic():
    """Test required scores for atomic test level."""
    required = RealBeamReadinessScorer.get_required_scores_for_level(
        ReadinessLevel.ATOMIC_TEST_READY
    )
    
    assert required["math_consistency"] == 0.95


def test_required_scores_mesoscopic():
    """Test required scores for mesoscopic test level."""
    required = RealBeamReadinessScorer.get_required_scores_for_level(
        ReadinessLevel.MESOSCOPIC_TEST_READY
    )
    
    assert required["math_consistency"] == 0.98


def test_required_scores_macroscopic():
    """Test required scores for macroscopic test level."""
    required = RealBeamReadinessScorer.get_required_scores_for_level(
        ReadinessLevel.MACROSCOPIC_INERT_TEST_READY
    )
    
    assert required["math_consistency"] == 0.99


def test_required_scores_human():
    """Test required scores for human transfer level."""
    required = RealBeamReadinessScorer.get_required_scores_for_level(
        ReadinessLevel.HUMAN_TRANSFER_NOT_ALLOWED
    )
    
    assert required["math_consistency"] == 1.0


def test_custom_notes():
    """Test that custom notes are included."""
    custom_notes = {
        "math_consistency": ["Test note 1", "Test note 2"],
    }
    
    report = RealBeamReadinessScorer.assess_readiness(
        custom_notes=custom_notes,
    )
    
    assert len(report.axes["math_consistency"].notes) == 2
    assert "Test note 1" in report.axes["math_consistency"].notes


def test_recommendations_for_low_scores():
    """Test that recommendations are given for low scores."""
    report = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.60,  # Low but not failing
        ssz_guardrails=0.95,
        no_go_compliance=0.95,
    )
    
    assert len(report.recommendations) > 0


def test_experimental_ladder_axis_status():
    """Test experimental ladder axis status values."""
    # Level 0
    r0 = RealBeamReadinessScorer.assess_readiness(experimental_ladder_level=0)
    assert r0.axes["experimental_ladder"].status == "FOUNDATIONAL"
    
    # Level 1
    r1 = RealBeamReadinessScorer.assess_readiness(experimental_ladder_level=1)
    assert r1.axes["experimental_ladder"].status == "PHOTON_READY"
    
    # Level 2
    r2 = RealBeamReadinessScorer.assess_readiness(experimental_ladder_level=2)
    assert r2.axes["experimental_ladder"].status == "ATOMIC_READY"


def test_all_levels_have_required_scores():
    """Test that all levels have required scores defined."""
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
        # Should not raise exception
        assert isinstance(required, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
