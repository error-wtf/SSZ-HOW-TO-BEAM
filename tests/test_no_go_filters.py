"""Tests for no_go_filters module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.no_go_filters import NoGoFilters, NoGoFilterResult


def test_no_cloning_pass():
    """Test no-cloning filter with no copying."""
    report = NoGoFilters.check_no_cloning_violation(
        scan_copy_model=False,
        unknown_quantum_state_copy=False,
    )
    assert report.result == NoGoFilterResult.PASS
    assert "No quantum cloning violation" in report.details


def test_no_cloning_fail():
    """Test no-cloning filter with unknown quantum state copy."""
    report = NoGoFilters.check_no_cloning_violation(
        scan_copy_model=False,
        unknown_quantum_state_copy=True,
    )
    assert report.result == NoGoFilterResult.FAIL
    assert "cannot be perfectly copied" in report.details


def test_no_cloning_warning():
    """Test no-cloning filter with scan/copy model."""
    report = NoGoFilters.check_no_cloning_violation(
        scan_copy_model=True,
        unknown_quantum_state_copy=False,
    )
    assert report.result == NoGoFilterResult.WARNING


def test_identity_continuity_pass():
    """Test identity continuity filter - no claims."""
    report = NoGoFilters.check_scan_copy_identity_break(
        scan_copy_model=False,
        claim_human_identity=False,
    )
    assert report.result == NoGoFilterResult.PASS


def test_identity_continuity_fail():
    """Test identity continuity filter - scan/copy + identity claim."""
    report = NoGoFilters.check_scan_copy_identity_break(
        scan_copy_model=True,
        claim_human_identity=True,
    )
    assert report.result == NoGoFilterResult.FAIL
    assert "cannot guarantee identity continuity" in report.details


def test_destructive_pass():
    """Test destructive filter - non-destructive."""
    report = NoGoFilters.check_destructive_reconstruction(
        destructive=False,
    )
    assert report.result == NoGoFilterResult.PASS


def test_destructive_fail():
    """Test destructive filter - destructive."""
    report = NoGoFilters.check_destructive_reconstruction(
        destructive=True,
    )
    assert report.result == NoGoFilterResult.FAIL
    assert "violates continuity" in report.details


def test_ftl_pass():
    """Test FTL filter - no superluminal."""
    report = NoGoFilters.check_faster_than_light_signal(
        superluminal_signal=False,
    )
    assert report.result == NoGoFilterResult.PASS


def test_ftl_fail():
    """Test FTL filter - superluminal."""
    report = NoGoFilters.check_faster_than_light_signal(
        superluminal_signal=True,
    )
    assert report.result == NoGoFilterResult.FAIL
    assert "violates causality" in report.details


def test_nec_pass():
    """Test NEC filter - canonical classification."""
    report = NoGoFilters.check_nec_violation_classification(
        nec_violation=False,
        claimed_classification="SSZ_CANONICAL",
    )
    assert report.result == NoGoFilterResult.PASS


def test_nec_fail():
    """Test NEC filter - violation with canonical claim."""
    report = NoGoFilters.check_nec_violation_classification(
        nec_violation=True,
        claimed_classification="SSZ_CANONICAL",
    )
    assert report.result == NoGoFilterResult.FAIL


def test_nec_exotic():
    """Test NEC filter - violation acknowledged as exotic."""
    report = NoGoFilters.check_nec_violation_classification(
        nec_violation=True,
        claimed_classification="GR_EXOTIC",
    )
    assert report.result == NoGoFilterResult.EXOTIC


def test_biological_early_level():
    """Test biological filter - too early."""
    report = NoGoFilters.check_biological_experiment_claim(
        biological_experiment=True,
        current_readiness_level="PHOTON_TEST_READY",
    )
    assert report.result == NoGoFilterResult.FAIL
    assert "prior validation" in report.details


def test_biological_appropriate_level():
    """Test biological filter - appropriate level with warning."""
    report = NoGoFilters.check_biological_experiment_claim(
        biological_experiment=True,
        current_readiness_level="MACROSCOPIC_INERT_TEST_READY",
    )
    assert report.result == NoGoFilterResult.WARNING
    assert "ethics/legal review" in report.details


def test_biological_no_experiment():
    """Test biological filter - no biological systems."""
    report = NoGoFilters.check_biological_experiment_claim(
        biological_experiment=False,
        current_readiness_level="FOUNDATIONAL_ONLY",
    )
    assert report.result == NoGoFilterResult.PASS


def test_run_all_filters():
    """Test running all filters."""
    reports = NoGoFilters.run_all_filters(
        scan_copy_model=False,
        unknown_quantum_state_copy=False,
        claim_human_identity=False,
        destructive=False,
        superluminal_signal=False,
        nec_violation=False,
        claimed_classification="SSZ_CANONICAL",
        biological_experiment=False,
    )
    
    # Should return 6 reports
    assert len(reports) == 6
    
    # All should pass
    for r in reports:
        assert r.result == NoGoFilterResult.PASS


def test_overall_result_pass():
    """Test overall result calculation - all pass."""
    reports = [
        type('R', (), {'result': NoGoFilterResult.PASS})(),
        type('R', (), {'result': NoGoFilterResult.PASS})(),
    ]
    
    overall = NoGoFilters.get_overall_result(reports)
    assert overall == NoGoFilterResult.PASS


def test_overall_result_warning():
    """Test overall result calculation - one warning."""
    reports = [
        type('R', (), {'result': NoGoFilterResult.PASS})(),
        type('R', (), {'result': NoGoFilterResult.WARNING})(),
    ]
    
    overall = NoGoFilters.get_overall_result(reports)
    assert overall == NoGoFilterResult.WARNING


def test_overall_result_fail():
    """Test overall result calculation - one fail."""
    reports = [
        type('R', (), {'result': NoGoFilterResult.PASS})(),
        type('R', (), {'result': NoGoFilterResult.FAIL})(),
    ]
    
    overall = NoGoFilters.get_overall_result(reports)
    assert overall == NoGoFilterResult.FAIL


def test_overall_result_exotic():
    """Test overall result calculation - exotic overrides warning."""
    reports = [
        type('R', (), {'result': NoGoFilterResult.EXOTIC})(),
        type('R', (), {'result': NoGoFilterResult.WARNING})(),
    ]
    
    overall = NoGoFilters.get_overall_result(reports)
    assert overall == NoGoFilterResult.EXOTIC


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
