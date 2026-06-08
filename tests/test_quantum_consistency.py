"""Tests for quantum_consistency module."""
import sys
sys.path.insert(0, 'src')

import pytest
import numpy as np

from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric
from beam_ssz.quantum_consistency import (
    BridgeQuantumAnalyzer,
    QuantumConsistencyResult,
    prove_quantum_theorem,
)


def test_analyzer_instantiation():
    """Test that analyzer can be instantiated."""
    analyzer = BridgeQuantumAnalyzer()
    assert analyzer is not None


def test_compute_curvature_scale():
    """Test curvature scale computation."""
    analyzer = BridgeQuantumAnalyzer()
    bridge = create_canonical_bridge()
    
    R = analyzer.compute_curvature_scale(bridge, u=0.0)
    assert R > 0
    assert np.isfinite(R)


def test_estimate_hawking_temperature():
    """Test Hawking temperature estimation."""
    analyzer = BridgeQuantumAnalyzer()
    bridge = create_canonical_bridge()
    
    T = analyzer.estimate_hawking_temperature_proxy(bridge)
    # May be None or a positive number
    if T is not None:
        assert T >= 0


def test_check_quantum_inequalities():
    """Test quantum inequality check."""
    analyzer = BridgeQuantumAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.check_quantum_inequalities(bridge)
    
    assert 'satisfied' in result
    assert 'negative_energy_exists' in result


def test_check_semicalssical_validity():
    """Test semiclassical validity check."""
    analyzer = BridgeQuantumAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.check_semicalssical_validity(bridge)
    
    assert 'valid' in result
    assert 'curvature_scale' in result
    assert 'planck_curvature' in result
    assert 'ratio' in result


def test_analyze_quantum_consistency():
    """Test full quantum consistency analysis."""
    analyzer = BridgeQuantumAnalyzer()
    bridge = create_canonical_bridge()
    
    result = analyzer.analyze_quantum_consistency(bridge)
    
    assert isinstance(result, QuantumConsistencyResult)
    assert hasattr(result, 'vacuum_stable')
    assert hasattr(result, 'semiclassical_valid')
    assert hasattr(result, 'overall_assessment')


def test_weak_bridge_quantum():
    """Test quantum analysis for weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    
    analyzer = BridgeQuantumAnalyzer()
    result = analyzer.analyze_quantum_consistency(bridge)
    
    assert result is not None
    # Weak bridge should be semiclassically valid
    assert result.semiclassical_valid or result.planck_scale_ratio < 1.0


def test_prove_quantum_theorem():
    """Test quantum theorem prover."""
    bridge = create_canonical_bridge()
    
    theorem = prove_quantum_theorem(bridge)
    
    assert 'theorem_name' in theorem
    assert 'statement' in theorem
    assert 'status' in theorem
    assert 'assumptions' in theorem
    assert 'open_issues' in theorem


def test_quantum_result_structure():
    """Test quantum result has all fields."""
    import numpy as np
    analyzer = BridgeQuantumAnalyzer()
    bridge = create_canonical_bridge()
    result = analyzer.analyze_quantum_consistency(bridge)
    
    # Check types - accept numpy or python types
    assert isinstance(result.particle_production, (float, int, np.floating, np.integer))
    assert isinstance(result.quantum_inequalities_satisfied, (bool, np.bool_, type(None)))
    assert isinstance(result.semiclassical_valid, (bool, np.bool_, type(None)))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
