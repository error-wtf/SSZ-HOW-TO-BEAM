"""Status enums for tensor diagnostics.

These statuses separate proxy/heuristic results from genuine tensor computations.
"""

from enum import Enum, auto


class TensorStatus(Enum):
    """Status of tensor validation for a metric candidate."""
    NOT_RUN = "NOT_RUN"
    FLAT_PASS = "FLAT_PASS"  # Passes flat limit (Minkowski zero-curvature)
    FINITE_PASS = "FINITE_PASS"  # Tensor components finite
    NUMERIC_WARNING = "NUMERIC_WARNING"  # Finite but large numerical errors
    FAILED = "FAILED"  # NaN/inf or symmetry violation


class EnergyConditionStatus(Enum):
    """Status of energy condition validation.
    
    IMPORTANT: Heuristic/proxy energy classes must NEVER automatically
    claim PASS status. Only tensor-derived T_mu_nu can yield PASS/FAIL.
    """
    NOT_RUN = "NOT_RUN"
    PROXY_ONLY = "PROXY_ONLY"  # Heuristic only, no tensor validation
    TENSOR_PENDING = "TENSOR_PENDING"  # Tensor computation not yet run
    NEC_PASS_NUMERIC = "NEC_PASS_NUMERIC"  # Sampled NEC pass (tensor-derived)
    NEC_FAIL_NUMERIC = "NEC_FAIL_NUMERIC"  # NEC violation found (tensor-derived)
    WEC_PASS_NUMERIC = "WEC_PASS_NUMERIC"  # Sampled WEC pass
    WEC_FAIL_NUMERIC = "WEC_FAIL_NUMERIC"  # WEC violation found
    SEC_PASS_NUMERIC = "SEC_PASS_NUMERIC"  # Sampled SEC pass
    SEC_FAIL_NUMERIC = "SEC_FAIL_NUMERIC"  # SEC violation found
    DEC_PASS_NUMERIC = "DEC_PASS_NUMERIC"  # Sampled DEC pass
    DEC_FAIL_NUMERIC = "DEC_FAIL_NUMERIC"  # DEC violation found
    UNDEFINED = "UNDEFINED"  # Cannot compute (e.g., no T_mu_nu)


class ReadinessLevel(Enum):
    """Overall readiness level of a bridge candidate.
    
    This combines algebraic, tensor, energy, and numerical status.
    """
    MATH_CANDIDATE_ONLY = "MATH_CANDIDATE_ONLY"
    ALGEBRAIC_PASS = "ALGEBRAIC_PASS"
    TENSOR_FINITE = "TENSOR_FINITE"
    ENERGY_DIAGNOSTIC_RUN = "ENERGY_DIAGNOSTIC_RUN"
    NEC_NUMERIC_PASS = "NEC_NUMERIC_PASS"
    NEC_NUMERIC_FAIL = "NEC_NUMERIC_FAIL"
    NUMERICAL_GR_SCAFFOLD = "NUMERICAL_GR_SCAFFOLD"
    PHOTON_OBSERVABLE_DESIGN_READY = "PHOTON_OBSERVABLE_DESIGN_READY"
    EXPERIMENTALLY_UNVALIDATED = "EXPERIMENTALLY_UNVALIDATED"
    BIOLOGICAL_NOT_VALIDATED = "BIOLOGICAL_NOT_VALIDATED"
