"""Tests for stability_analysis module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.stability_analysis import (
    BridgeStabilityAnalyzer,
    StabilityResult,
    prove_stability_theorem,
)
from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric


def test_stability_analyzer_instantiation():
    """Test that analyzer can be instantiated."""
    analyzer = BridgeStabilityAnalyzer()
    assert analyzer is not None


def test_compute_effective_potential():
    """Test effective potential computation."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    V = analyzer.compute_effective_potential(bridge, u=0.0)
    assert V >= 0


def test_analyze_stability_proxy():
    """Test stability analysis."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.analyze_stability_proxy(bridge)
    
    assert isinstance(result, StabilityResult)
    assert hasattr(result, 'linearly_stable')
    assert hasattr(result, 'unstable_modes')


def test_stability_result_structure():
    """Test stability result has correct structure."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.analyze_stability_proxy(bridge)
    
    assert isinstance(result.unstable_modes, int)
    assert isinstance(result.growth_rates, list)
    assert isinstance(result.perturbation_modes, list)
    assert len(result.perturbation_modes) > 0


def test_jebsen_birkhoff_check():
    """Test Jebsen-Birkhoff-like check."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.check_jebsen_birkhoff_proxy(bridge)
    
    assert 'is_static' in result
    assert 'is_spherically_symmetric' in result
    assert result['is_static'] is True  # By construction
    assert result['is_spherically_symmetric'] is True  # By construction


def test_full_stability_report():
    """Test full stability report generation."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    report = analyzer.full_stability_report(bridge, verbose=False)
    
    assert 'linear_stability' in report
    assert 'symmetry_checks' in report
    assert 'recommendations' in report
    assert 'overall_status' in report


def test_stability_weak_bridge():
    """Test stability for weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    
    analyzer = BridgeStabilityAnalyzer()
    result = analyzer.analyze_stability_proxy(bridge)
    
    # Weak bridge should be stable
    assert result is not None


def test_stability_strong_bridge():
    """Test stability for strong bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=5.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    
    analyzer = BridgeStabilityAnalyzer()
    result = analyzer.analyze_stability_proxy(bridge)
    
    assert result is not None


def test_prove_stability_theorem():
    """Test stability theorem prover."""
    bridge = create_canonical_bridge()
    
    theorem = prove_stability_theorem(bridge)
    
    assert 'theorem_name' in theorem
    assert 'statement' in theorem
    assert 'status' in theorem
    assert 'assumptions' in theorem
    assert 'open_issues' in theorem


def test_recommendations_present():
    """Test that recommendations are provided."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.analyze_stability_proxy(bridge)
    
    assert result.recommended_lambda_max > 0
    assert result.recommended_ell0_min > 0


def test_stability_conclusion():
    """Test that conclusion is provided."""
    analyzer = BridgeStabilityAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.analyze_stability_proxy(bridge)
    
    assert len(result.stability_conclusion) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
