"""Comprehensive integration tests across modules."""
import sys
sys.path.insert(0, 'src')

import pytest
import math

from beam_ssz.xi import evaluate_xi_x
from beam_ssz.regimes import classify_regime, Regime
from beam_ssz.bridge_metric import create_canonical_bridge
from beam_ssz.energy_conditions import classify_energy_conditions, CandidateClass
from beam_ssz.no_go_filters import NoGoFilters, NoGoFilterResult


def test_xi_to_regime_consistency():
    """Test that Xi evaluation and regime classification agree."""
    test_points = [0.5, 1.0, 1.5, 1.9, 2.0, 2.1, 2.5, 5.0, 10.0]
    
    for x in test_points:
        xi_result = evaluate_xi_x(x)
        regime_result = classify_regime(x)
        
        assert xi_result.regime == regime_result.regime


def test_strong_field_xi_properties():
    """Test Xi properties in strong field regime."""
    x_values = [0.5, 1.0, 1.5]  # Strong field
    
    for x in x_values:
        result = evaluate_xi_x(x)
        
        # Xi should be positive
        assert result.xi > 0
        
        # Xi should be less than 1 (saturation property)
        assert result.xi < 1.0
        
        # Derivative should be negative (Xi decreases with r)
        assert result.dxi_dx < 0


def test_weak_field_xi_properties():
    """Test Xi properties in weak field regime."""
    x_values = [10.0, 50.0, 100.0]  # Weak field
    
    for x in x_values:
        result = evaluate_xi_x(x)
        
        # Xi should be small
        assert result.xi < 0.1
        
        # Xi should be positive
        assert result.xi > 0


def test_bridge_with_canonical_xi():
    """Test bridge using Xi values from canonical evaluation."""
    # Get Xi values at specific radii
    xi_inner = evaluate_xi_x(1.5).xi  # Near horizon
    xi_outer = evaluate_xi_x(10.0).xi  # Far field
    
    from beam_ssz.bridge_metric import SSZBridgeMetric
    
    bridge = SSZBridgeMetric(
        xi_left=xi_inner,
        xi_right=xi_outer,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    # Should be regular
    is_regular, issues = bridge.is_regular()
    assert is_regular
    
    # Should have finite bridge distance
    l_bridge = bridge.bridge_distance()
    assert math.isfinite(l_bridge)
    assert l_bridge > 0


def test_energy_condition_nec_satisfied():
    """Test energy condition classification when NEC is satisfied."""
    report = classify_energy_conditions(
        nec_satisfied=True,
        sec_satisfied=None,
    )
    
    assert report.nec_satisfied
    assert report.candidate_class == CandidateClass.SSZ_CANONICAL
    assert not report.requires_exotic_matter


def test_energy_condition_nec_violated():
    """Test energy condition classification when NEC is violated."""
    report = classify_energy_conditions(
        nec_satisfied=False,
        sec_satisfied=None,
    )
    
    assert not report.nec_satisfied
    assert report.candidate_class == CandidateClass.GR_EXOTIC
    assert report.requires_exotic_matter


def test_no_go_all_pass_scenario():
    """Test all no-go filters in ideal scenario."""
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
    
    all_pass = all(r.result == NoGoFilterResult.PASS for r in reports)
    assert all_pass
    
    overall = NoGoFilters.get_overall_result(reports)
    assert overall == NoGoFilterResult.PASS


def test_no_go_problematic_scenario():
    """Test no-go filters catch problematic scenarios."""
    # Scan/copy claiming human identity
    reports = NoGoFilters.run_all_filters(
        scan_copy_model=True,
        unknown_quantum_state_copy=False,
        claim_human_identity=True,
        destructive=False,
        superluminal_signal=False,
        nec_violation=False,
        claimed_classification="SSZ_CANONICAL",
        biological_experiment=False,
    )
    
    # Should have at least one FAIL
    has_fail = any(r.result == NoGoFilterResult.FAIL for r in reports)
    assert has_fail


def test_end_to_end_bridge_pipeline():
    """Test complete pipeline: Xi -> Bridge -> Evaluation -> Classification."""
    # Step 1: Get Xi values
    xi_a = evaluate_xi_x(2.0).xi  # r/r_s = 2.0
    xi_b = evaluate_xi_x(5.0).xi  # r/r_s = 5.0
    
    # Step 2: Create bridge
    from beam_ssz.bridge_metric import SSZBridgeMetric
    bridge = SSZBridgeMetric(
        xi_left=xi_a,
        xi_right=xi_b,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    # Step 3: Evaluate bridge
    result = bridge.evaluate_candidate(l_normal=1.0)
    
    # Step 4: Verify evaluation
    assert result.is_regular
    assert result.worldline_norm_ok
    assert result.causality_ok
    assert math.isfinite(result.distance_ratio)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
