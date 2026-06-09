"""Energy condition diagnostics.

CRITICAL: These checks require tensor-derived T_mu_nu.
Heuristic/proxy energy classes must NOT claim PASS status automatically.

NEC: T_{mu nu} k^mu k^nu >= 0 for all null k
WEC: T_{mu nu} v^mu v^nu >= 0 for all timelike v (implies NEC)
SEC: (T_{mu nu} - 1/2 g_{mu nu} T) v^mu v^nu >= 0
DEC: T_{mu nu} v^mu v^nu >= 0 and |T_{0i}| <= T_{00} for each i
"""

import numpy as np
from typing import List, Tuple
from .status import EnergyConditionStatus
from .null_vectors import generate_null_vectors, verify_null


def contract_T_with_vectors(T: np.ndarray, g: np.ndarray, vectors: List[np.ndarray]) -> List[float]:
    """Compute T_{mu nu} v^mu v^nu for each vector.
    
    Args:
        T: Stress-energy tensor T[mu,nu]
        g: Metric (for index lowering)
        vectors: List of vectors v^mu
    
    Returns:
        List of contractions T_mu_nu v^mu v^nu
    """
    results = []
    for v in vectors:
        val = 0.0
        for mu in range(4):
            for nu in range(4):
                val += T[mu, nu] * v[mu] * v[nu]
        results.append(val)
    return results


def check_nec(
    T: np.ndarray,
    g: np.ndarray,
    x: np.ndarray,
    n_samples: int = 8,
    tolerance: float = 1e-10,
) -> Tuple[EnergyConditionStatus, dict]:
    """Check Null Energy Condition (NEC).
    
    NEC: T_{mu nu} k^mu k^nu >= 0 for all null k
    
    Args:
        T: Stress-energy tensor
        g: Metric
        x: Position (for null vector generation)
        n_samples: Number of null vectors to test
        tolerance: Threshold for violation (allowing numerical noise)
    
    Returns:
        Tuple of (status, details_dict)
        - NEC_PASS_NUMERIC if all samples >= -tolerance
        - NEC_FAIL_NUMERIC if any sample < -tolerance
    """
    # Generate test null vectors
    null_vectors = generate_null_vectors(x, g, n_samples)
    
    if not null_vectors:
        return EnergyConditionStatus.UNDEFINED, {"error": "No null vectors generated"}
    
    # Verify null condition
    valid_vectors = []
    for k in null_vectors:
        if verify_null(k, g, tolerance=1e-4):
            valid_vectors.append(k)
    
    if not valid_vectors:
        return EnergyConditionStatus.UNDEFINED, {"error": "No valid null vectors"}
    
    # Compute contractions
    contractions = contract_T_with_vectors(T, g, valid_vectors)
    
    # Check NEC
    min_value = min(contractions)
    
    details = {
        "n_tested": len(valid_vectors),
        "min_value": min_value,
        "max_value": max(contractions),
        "values": contractions,
    }
    
    if min_value < -tolerance:
        return EnergyConditionStatus.NEC_FAIL_NUMERIC, details
    else:
        return EnergyConditionStatus.NEC_PASS_NUMERIC, details


def check_wec(
    T: np.ndarray,
    g: np.ndarray,
    x: np.ndarray,
    n_samples: int = 8,
    tolerance: float = 1e-10,
) -> Tuple[EnergyConditionStatus, dict]:
    """Check Weak Energy Condition (WEC).
    
    WEC: T_{mu nu} v^mu v^nu >= 0 for all timelike v
    
    This is computationally harder than NEC. We sample timelike vectors.
    
    Args:
        T: Stress-energy tensor
        g: Metric
        x: Position
        n_samples: Number of timelike vectors to test
        tolerance: Threshold for violation
    
    Returns:
        Tuple of (status, details_dict)
    """
    # Generate timelike vectors (unit time component, small spatial)
    timelike_vectors = []
    
    # Unit vector in time direction
    v0 = np.array([1.0, 0.0, 0.0, 0.0])
    timelike_vectors.append(v0)
    
    # Add vectors with small spatial components
    for i in range(min(n_samples - 1, 6)):
        epsilon = 0.1
        v = np.array([1.0, 0.0, 0.0, 0.0])
        if i < 2:
            v[1] = epsilon * (1 if i == 0 else -1)
        elif i < 4:
            v[2] = epsilon * (1 if i == 2 else -1)
        else:
            v[3] = epsilon * (1 if i == 4 else -1)
        timelike_vectors.append(v)
    
    # Compute contractions
    contractions = contract_T_with_vectors(T, g, timelike_vectors)
    
    min_value = min(contractions)
    
    details = {
        "n_tested": len(timelike_vectors),
        "min_value": min_value,
        "max_value": max(contractions),
        "values": contractions,
    }
    
    if min_value < -tolerance:
        return EnergyConditionStatus.WEC_FAIL_NUMERIC, details
    else:
        return EnergyConditionStatus.WEC_PASS_NUMERIC, details


def check_energy_conditions(
    T: np.ndarray,
    g: np.ndarray,
    x: np.ndarray,
    check_nec: bool = True,
    check_wec: bool = True,
    n_samples: int = 8,
) -> dict:
    """Check all available energy conditions.
    
    Args:
        T: Stress-energy tensor
        g: Metric
        x: Position
        check_nec: Whether to check NEC
        check_wec: Whether to check WEC
        n_samples: Number of vectors to test
    
    Returns:
        Dict with status and details for each condition
    """
    results = {}
    
    if check_nec:
        nec_status, nec_details = check_nec(T, g, x, n_samples)
        results["NEC"] = {
            "status": nec_status,
            "details": nec_details,
        }
    
    if check_wec:
        wec_status, wec_details = check_wec(T, g, x, n_samples)
        results["WEC"] = {
            "status": wec_status,
            "details": wec_details,
        }
    
    return results
