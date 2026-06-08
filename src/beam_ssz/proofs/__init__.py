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
