"""Tests for complete_proof module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric
from beam_ssz.complete_proof import (
    CompleteBeamingProof,
    CompleteProofResult,
    ProofCompleteness,
    is_beaming_proven,
)


def test_proof_class_instantiation():
    """Test that proof class can be instantiated."""
    proof = CompleteBeamingProof()
    assert proof is not None


def test_prove_all_theorems():
    """Test proving all theorems."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert isinstance(result, CompleteProofResult)
    assert hasattr(result, 'theorems_proven')
    assert hasattr(result, 'proof_completeness')


def test_complete_result_structure():
    """Test complete result structure."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert isinstance(result.theorems_proven, int)
    assert isinstance(result.theorems_partial, int)
    assert isinstance(result.theorems_open, int)
    assert isinstance(result.all_necessary_conditions_met, bool)
    assert isinstance(result.sufficient_conditions_met, bool)
    assert isinstance(result.overall_conclusion, str)


def test_component_results_present():
    """Test that component results are present."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert len(result.component_results) > 0
    assert isinstance(result.component_results, dict)


def test_open_problems_list():
    """Test that open problems are listed."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert isinstance(result.open_problems_remaining, list)


def test_recommendations_present():
    """Test that recommendations are provided."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert isinstance(result.recommendations, list)


def test_generate_proof_document():
    """Test proof document generation."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    
    document = proof.generate_proof_document(bridge, l_normal=1.0)
    
    assert isinstance(document, str)
    assert len(document) > 0
    assert "COMPLETE MATHEMATICAL PROOF" in document


def test_is_beaming_proven():
    """Test convenience function."""
    bridge = create_canonical_bridge()
    
    result = is_beaming_proven(bridge, l_normal=1.0)
    
    assert 'proven' in result
    assert 'likely' in result
    assert 'possible' in result
    assert 'insufficient' in result
    assert 'theorems_proven' in result
    assert 'conclusion' in result
    assert 'full_report' in result


def test_weak_bridge_proof():
    """Test proof for weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    proof = CompleteBeamingProof()
    
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert result is not None
    assert result.theorems_proven >= 2  # At least basic theorems


def test_strong_bridge_proof():
    """Test proof for strong bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=5.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    proof = CompleteBeamingProof()
    
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    assert result is not None


def test_proof_completeness_enum():
    """Test proof completeness enum."""
    assert ProofCompleteness.RIGOROUS.value == "RIGOROUS"
    assert ProofCompleteness.STRONG.value == "STRONG"
    assert ProofCompleteness.MODERATE.value == "MODERATE"
    assert ProofCompleteness.WEAK.value == "WEAK"
    assert ProofCompleteness.INSUFFICIENT.value == "INSUFFICIENT"


def test_necessary_conditions():
    """Test that necessary conditions are checked."""
    bridge = create_canonical_bridge()
    proof = CompleteBeamingProof()
    result = proof.prove_all_theorems(bridge, l_normal=1.0)
    
    # Metric regularity and timelike worldlines should be proven
    assert result.all_necessary_conditions_met


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
