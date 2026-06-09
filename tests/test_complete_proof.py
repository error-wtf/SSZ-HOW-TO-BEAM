"""Tests for proof_status module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric
from beam_ssz.proof_status import (
    ProofStatus,
    ProofStatusResult,
    ProofLevel,
    check_proof_status,
)


def test_proof_status_instantiation():
    """Test that proof status class can be instantiated."""
    proof = ProofStatus()
    assert proof is not None


def test_check_proof_status():
    """Test checking proof status for bridge."""
    bridge = create_canonical_bridge()
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert isinstance(result, ProofStatusResult)
    assert hasattr(result, 'theorems_proven')
    assert hasattr(result, 'proof_level')


def test_proof_status_structure():
    """Test proof status result structure."""
    bridge = create_canonical_bridge()
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert isinstance(result.theorems_proven, int)
    assert isinstance(result.theorems_partial, int)
    assert isinstance(result.theorems_open, int)
    assert isinstance(result.all_necessary_conditions_met, bool)
    assert isinstance(result.sufficient_conditions_met, bool)
    assert isinstance(result.overall_conclusion, str)


def test_component_results_present():
    """Test that component results are present."""
    bridge = create_canonical_bridge()
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert len(result.component_results) > 0
    assert isinstance(result.component_results, dict)


def test_open_problems_list():
    """Test that open problems are listed."""
    bridge = create_canonical_bridge()
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert isinstance(result.open_problems_remaining, list)


def test_recommendations_present():
    """Test that recommendations are provided."""
    bridge = create_canonical_bridge()
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert isinstance(result.recommendations, list)


def test_proof_status_document():
    """Test proof status document generation."""
    bridge = create_canonical_bridge()
    
    document = check_proof_status(bridge, l_normal=1.0)
    
    assert isinstance(document.overall_conclusion, str)
    assert len(document.overall_conclusion) > 0


def test_check_proof_status_function():
    """Test convenience function."""
    bridge = create_canonical_bridge()
    
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert hasattr(result, 'theorems_proven')
    assert hasattr(result, 'proof_level')
    assert hasattr(result, 'overall_conclusion')


def test_weak_bridge_proof_status():
    """Test proof status for weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert result is not None
    assert result.theorems_proven >= 2  # At least basic theorems


def test_strong_bridge_proof_status():
    """Test proof status for strong bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=5.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    result = check_proof_status(bridge, l_normal=1.0)
    
    assert result is not None


def test_proof_level_enum():
    """Test proof level enum."""
    assert ProofLevel.ALGEBRAIC_PASS.value == "ALGEBRAIC_PASS"
    assert ProofLevel.TENSOR_PENDING.value == "TENSOR_PENDING"
    assert ProofLevel.ENERGY_PENDING.value == "ENERGY_PENDING"
    assert ProofLevel.EXPERIMENTALLY_UNVALIDATED.value == "EXPERIMENTALLY_UNVALIDATED"


def test_necessary_conditions():
    """Test that necessary conditions are checked."""
    bridge = create_canonical_bridge()
    result = check_proof_status(bridge, l_normal=1.0)
    
    # Metric regularity and timelike worldlines should pass algebraically
    assert result.all_necessary_conditions_met


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
