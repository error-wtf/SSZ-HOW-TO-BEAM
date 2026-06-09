"""Mathematical proofs for BEAM-SSZ theorems.

This package contains rigorous mathematical proofs for:
- Theorem 3: Distance Reduction
- Theorem 4: Energy Conditions
- Theorem 5: Tidal Safety
- Theorem 6: Stability
- Theorem 7: Quantum Consistency
- Theorem 8: Thermodynamic Feasibility
"""

from .theorem_3_distance import Theorem3DistanceProof, DistanceProofResult
from .theorem_4_energy import Theorem4EnergyProof, EnergyProofResult
from .theorem_5_tidal import Theorem5TidalProof, TidalProofResult
from .theorem_6_stability import Theorem6StabilityProof, StabilityProofResult
from .theorem_7_quantum import Theorem7QuantumProof, QuantumProofResult
from .theorem_8_thermodynamics import Theorem8ThermodynamicsProof, ThermodynamicsProofResult

# Convenience functions for testing
def distance_theorem() -> dict:
    """Theorem 3: Distance Reduction"""
    proof = Theorem3DistanceProof()
    return {"theorem": 3, "name": "Distance Reduction", "result": proof.prove()}

def energy_theorem() -> dict:
    """Theorem 4: Energy Conditions"""
    proof = Theorem4EnergyProof()
    return {"theorem": 4, "name": "Energy Conditions", "result": proof.prove()}

def tidal_theorem() -> dict:
    """Theorem 5: Tidal Safety"""
    proof = Theorem5TidalProof()
    return {"theorem": 5, "name": "Tidal Safety", "result": proof.prove()}

def stability_theorem() -> dict:
    """Theorem 6: Stability"""
    proof = Theorem6StabilityProof()
    return {"theorem": 6, "name": "Stability", "result": proof.prove()}

def quantum_theorem() -> dict:
    """Theorem 7: Quantum Consistency"""
    proof = Theorem7QuantumProof()
    return {"theorem": 7, "name": "Quantum Consistency", "result": proof.prove()}

def thermodynamics_theorem() -> dict:
    """Theorem 8: Thermodynamic Feasibility"""
    proof = Theorem8ThermodynamicsProof()
    return {"theorem": 8, "name": "Thermodynamic Feasibility", "result": proof.prove()}

__all__ = [
    'Theorem3DistanceProof',
    'DistanceProofResult',
    'Theorem4EnergyProof',
    'EnergyProofResult',
    'Theorem5TidalProof',
    'TidalProofResult',
    'Theorem6StabilityProof',
    'StabilityProofResult',
    'Theorem7QuantumProof',
    'QuantumProofResult',
    'Theorem8ThermodynamicsProof',
    'ThermodynamicsProofResult',
]
