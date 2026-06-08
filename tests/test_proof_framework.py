"""Tests for proof_framework module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.proof_framework import (
    BeamingProofFramework,
    ProofStatus,
    analyze_bridge_for_proof,
)
from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric


def test_theorem_1_metric_regularity():
    """Test Theorem 1 for canonical bridge."""
    bridge = create_canonical_bridge()
    result = BeamingProofFramework.theorem_1_metric_regularity(bridge)
    
    assert result.theorem_name == "Theorem 1: Metric Regularity"
    assert result.conditions_satisfied is True
    assert result.status in [ProofStatus.PROVEN, ProofStatus.DEPENDS_ON_PARAMETERS]


def test_theorem_2_timelike_worldline():
    """Test Theorem 2 for canonical bridge."""
    bridge = create_canonical_bridge()
    result = BeamingProofFramework.theorem_2_timelike_worldline(bridge)
    
    assert result.theorem_name == "Theorem 2: Timelike Worldline Existence"
    assert result.conditions_satisfied is True
    assert result.status in [ProofStatus.PROVEN, ProofStatus.DEPENDS_ON_PARAMETERS]


def test_theorem_3_distance_reduction():
    """Test Theorem 3 for canonical bridge."""
    bridge = create_canonical_bridge()
    l_normal = 1.0
    result = BeamingProofFramework.theorem_3_distance_reduction(bridge, l_normal)
    
    assert result.theorem_name == "Theorem 3: Distance Reduction"
    assert result.status == ProofStatus.DEPENDS_ON_PARAMETERS


def test_theorem_4_energy_conditions():
    """Test Theorem 4 (open problem)."""
    bridge = create_canonical_bridge()
    result = BeamingProofFramework.theorem_4_energy_conditions(bridge)
    
    assert result.theorem_name == "Theorem 4: Energy Conditions"
    assert result.status == ProofStatus.OPEN_PROBLEM


def test_theorem_5_tidal_safety():
    """Test Theorem 5 for tidal safety."""
    bridge = create_canonical_bridge()
    result = BeamingProofFramework.theorem_5_tidal_safety(bridge)
    
    assert result.theorem_name == "Theorem 5: Tidal Safety"
    assert result.status == ProofStatus.DEPENDS_ON_PARAMETERS


def test_prove_all_theorems():
    """Test that all theorems can be applied."""
    bridge = create_canonical_bridge()
    theorems = BeamingProofFramework.prove_all_theorems(bridge, l_normal=1.0)
    
    assert len(theorems) == 5
    
    theorem_names = [t.theorem_name for t in theorems]
    assert "Theorem 1: Metric Regularity" in theorem_names
    assert "Theorem 2: Timelike Worldline Existence" in theorem_names
    assert "Theorem 3: Distance Reduction" in theorem_names
    assert "Theorem 4: Energy Conditions" in theorem_names
    assert "Theorem 5: Tidal Safety" in theorem_names


def test_proof_summary_generation():
    """Test that proof summary is generated."""
    bridge = create_canonical_bridge()
    summary = BeamingProofFramework.get_proof_summary(bridge, l_normal=1.0)
    
    assert "BEAM-SSZ MATHEMATICAL PROOF FRAMEWORK" in summary
    assert "Theorem 1" in summary
    assert "Theorem 2" in summary
    assert "CONCLUSION:" in summary


def test_analyze_bridge_function():
    """Test analyze_bridge_for_proof convenience function."""
    bridge = create_canonical_bridge()
    results = analyze_bridge_for_proof(bridge, l_normal=1.0, verbose=False)
    
    assert "theorems" in results
    assert "summary" in results
    assert "overall_assessment" in results
    assert "open_problems" in results


def test_proof_status_values():
    """Test ProofStatus enum values."""
    assert ProofStatus.PROVEN.value == "PROVEN"
    assert ProofStatus.CONJECTURE.value == "CONJECTURE"
    assert ProofStatus.DEPENDS_ON_PARAMETERS.value == "DEPENDS_ON_PARAMETERS"
    assert ProofStatus.OPEN_PROBLEM.value == "OPEN_PROBLEM"
    assert ProofStatus.COUNTEREXAMPLE_EXISTS.value == "COUNTEREXAMPLE_EXISTS"


def test_theorem_result_structure():
    """Test TheoremResult dataclass structure."""
    bridge = create_canonical_bridge()
    result = BeamingProofFramework.theorem_1_metric_regularity(bridge)
    
    assert hasattr(result, 'theorem_name')
    assert hasattr(result, 'status')
    assert hasattr(result, 'statement')
    assert hasattr(result, 'assumptions')
    assert hasattr(result, 'implications')
    assert hasattr(result, 'conditions_satisfied')
    assert hasattr(result, 'proof_sketch')


def test_weak_bridge_all_theorems():
    """Test all theorems on weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    
    theorems = BeamingProofFramework.prove_all_theorems(bridge, l_normal=1.0)
    
    # All theorems should be applicable
    assert len(theorems) == 5
    
    # At least theorems 1 and 2 should be proven or parameter-dependent
    proven_count = sum(1 for t in theorems if t.status == ProofStatus.PROVEN)
    assert proven_count >= 2


def test_strong_bridge_theorems():
    """Test all theorems on strong bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=5.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    
    theorems = BeamingProofFramework.prove_all_theorems(bridge, l_normal=1.0)
    assert len(theorems) == 5


def test_open_problems_identified():
    """Test that open problems are correctly identified."""
    bridge = create_canonical_bridge()
    results = analyze_bridge_for_proof(bridge, l_normal=1.0, verbose=False)
    
    # Should identify Theorem 4 (Energy Conditions) as open
    open_problems = results["open_problems"]
    assert any("Energy" in p or "Theorem 4" in p for p in open_problems)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
