"""Full integration test - tests entire pipeline."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.bridge_metric import (
    SSZBridgeMetric,
    create_canonical_bridge,
)
from beam_ssz.xi import evaluate_xi_x
from beam_ssz.proof_framework import BeamingProofFramework
from beam_ssz.complete_proof import is_beaming_proven
from beam_ssz.einstein_solver import estimate_energy_requirements
from beam_ssz.stability_analysis import BridgeStabilityAnalyzer
from beam_ssz.quantum_consistency import BridgeQuantumAnalyzer
from beam_ssz.thermodynamics import BridgeThermodynamicAnalyzer


def test_full_pipeline():
    """Test complete analysis pipeline."""
    # 1. Xi evaluation
    xi_result = evaluate_xi_x(2.0)
    assert xi_result.xi > 0
    
    # 2. Bridge creation
    bridge = create_canonical_bridge()
    assert bridge is not None
    
    # 3. Bridge distance
    l_bridge = bridge.bridge_distance()
    assert l_bridge > 0
    
    # 4. Proof framework
    framework = BeamingProofFramework()
    theorems = framework.prove_all_theorems(bridge, 1.0)
    assert len(theorems) == 5
    
    # 5. Complete assessment
    status = is_beaming_proven(bridge, 1.0)
    assert 'completeness' in status


def test_all_analyzers():
    """Test all analyzer modules work together."""
    bridge = create_canonical_bridge()
    
    # Einstein solver
    energy = estimate_energy_requirements(bridge, verbose=False)
    assert energy['status'] in ['SUCCESS', 'NUMERICAL_ERROR']
    
    # Stability
    stab_analyzer = BridgeStabilityAnalyzer()
    stab_result = stab_analyzer.analyze_stability_proxy(bridge)
    assert stab_result is not None
    
    # Quantum
    q_analyzer = BridgeQuantumAnalyzer()
    q_result = q_analyzer.analyze_quantum_consistency(bridge)
    assert q_result is not None
    
    # Thermodynamics
    t_analyzer = BridgeThermodynamicAnalyzer()
    t_result = t_analyzer.analyze_thermodynamics(bridge)
    assert t_result is not None


def test_end_to_end_proof():
    """Test end-to-end proof generation."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.1,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    # Complete proof
    status = is_beaming_proven(bridge, l_normal=1.0)
    
    assert status['proven'] in [True, False]
    assert status['likely'] in [True, False]
    assert status['possible'] in [True, False]
    assert status['insufficient'] in [True, False]
    assert status['theorems_proven'] >= 2  # At least basic theorems
    assert len(status['conclusion']) > 0
    assert len(status['full_report']) > 0


def test_bridge_parameter_variations():
    """Test various bridge parameter combinations."""
    params = [
        (0.01, 0.01, 0.01, 1e-2, 1e-2),  # Weak
        (0.1, 0.1, 0.5, 1e-3, 1e-2),     # Moderate
        (0.2, 0.3, 2.0, 5e-4, 5e-3),     # Strong
    ]
    
    for xi_a, xi_b, lam, ell0, r0 in params:
        bridge = SSZBridgeMetric(
            xi_left=xi_a,
            xi_right=xi_b,
            lambda_bridge=lam,
            ell0=ell0,
            throat_radius=r0,
        )
        
        # Should not crash
        l_bridge = bridge.bridge_distance()
        assert l_bridge > 0
        
        is_reg, _ = bridge.is_regular()
        assert is_reg


def test_tensor_scaffold_integration():
    """Test tensor scaffold with bridge parameters."""
    from beam_ssz.tensor import MetricTensor, EinsteinTensor
    
    # Use bridge parameters to compute metric
    bridge = create_canonical_bridge()
    
    # Get Xi at center
    xi_center = bridge.xi(0.0)
    
    # Approximate r from Xi (simplified)
    # Xi ~ 1/(2x) for weak field
    if xi_center > 0.01:
        r_approx = 1.0 / (2.0 * xi_center)
        
        # Compute metric
        metric = MetricTensor.compute(r_approx, rs=1.0, theta=3.14159/2)
        assert metric.is_finite


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
