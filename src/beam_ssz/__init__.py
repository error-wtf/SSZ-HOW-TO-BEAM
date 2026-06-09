"""SSZ-HOW-TO-BEAM v1.0.0 research framework.

SSZ continuous-worldline bridge model with strict no-copy constraint.
Release-quality mathematical/numerical candidate framework.

Primary model: CONTINUOUS_WORLDLINE_BRIDGE
Not: destructive scan / copy reconstruction / pattern buffer identity.

Core Principle:
d_eff(A,B) -> 0
N(A) ∩ N(B) != empty
x_C^μ(τ): A -> B with dτ > 0

Carmen bleibt Carmen because her worldline doesn't break.
Not because she's copied or stored in a buffer.

Tensor-core diagnostics with array-based computations.
Implements SSZ Prime Directive for observable classification.
Implements Claim-Gate system for scientific honesty.
"""

from .xi import evaluate_xi_x, evaluate_d_s_x
from .metric import SSZMetric
from .validators import validate_candidate
from .geodesics import radial_freefall_velocity, effective_potential
from .radial_scaling import rho_between_x
from .holonomy import closed_loop_invariant

# v0.6 bridge metric
from .bridge_metric import SSZBridgeMetric, create_canonical_bridge, evaluate_bridge_candidate

# v0.9 tensor core (array-based)
from .tensor_core import (
    CoordinateIndex,
    TensorStatus,
    EnergyConditionStatus,
    minkowski_cartesian,
    minkowski_spherical,
    ssz_metric,
    compute_christoffel,
    compute_riemann,
    compute_ricci,
    ricci_scalar,
    compute_einstein,
    validate_tensor_finite,
)

# v0.9 observable dispatcher (Prime Directive)
from .tensor_core.observable_dispatcher import (
    ObservableType,
    Regime,
    classify_regime,
    compute_observable_factor,
    ObservableDispatcher,
)

# v0.9 energy proxy (heuristic only - NOT tensor T_mu_nu)
from .energy_proxy import (
    EnergyProxyStatus,
    EnergyProxyDiagnostic,
)

# v1.0 observables (relative to SSZ background)
from .observables import (
    ReferenceFrame,
    compute_redshift,
    RedshiftResult,
    compute_phase_shift,
    PhaseShiftResult,
    compute_photon_delay,
    TimeDelayResult,
    compute_interferometer_response,
    InterferometerResult,
)

# v1.0 numerical GR diagnostics
from .numerical_gr_diagnostics import (
    ConvergenceReport,
    ConstraintReport,
    test_convergence_rate,
    generate_convergence_report,
    check_hamiltonian_constraint,
    validate_numerical_solution,
)

# v1.0 validation pipeline
from .validation_pipeline import (
    ValidationGate,
    GateResult,
    ValidationReport,
    ValidationPipeline,
    generate_v1_report,
)

# Claim Gates v1.0
from .claim_gates import (
    EvidenceLevel,
    ClaimCategory,
    ClaimStatus,
    ClaimGateResult,
    evaluate_claim_gate,
    evaluate_all_ssz_core_claims,
    generate_v1_claim_report,
)

# v0.9 SSZ Core (continuous-worldline bridge)
from .ssz_core import (
    # Status
    SSZValidationStatus,
    TransportMode,
    TransportReadiness,
    SegmentationStatus,
    WorldlineStatus,
    NoCopyStatus,
    # Segmentation
    xi_from_radius,
    d_ssz_from_xi,
    s_ssz_from_xi,
    validate_segmentation_state,
    # Effective distance
    effective_segment_distance,
    bridge_effective_distance,
    distance_reduction_ratio,
    # Neighborhood
    segment_neighborhood,
    neighborhood_overlap,
    has_segment_overlap,
    # Worldline
    WorldlineSample,
    validate_worldline_continuity,
    # Transport mode
    validate_transport_mode,
    no_copy_constraint,
    # Validation
    SSZBridgeValidationReport,
    validate_ssz_bridge_candidate,
    # Metric
    ssz_metric_tensor,
    validate_ssz_metric,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    # Core v0.4/v0.6
    "evaluate_xi_x",
    "evaluate_d_s_x",
    "SSZMetric",
    "validate_candidate",
    "radial_freefall_velocity",
    "effective_potential",
    "rho_between_x",
    "closed_loop_invariant",
    "SSZBridgeMetric",
    "create_canonical_bridge",
    "evaluate_bridge_candidate",
    # Tensor core v0.9
    "CoordinateIndex",
    "TensorStatus",
    "EnergyConditionStatus",
    "minkowski_cartesian",
    "minkowski_spherical",
    "ssz_metric",
    "compute_christoffel",
    "compute_riemann",
    "compute_ricci",
    "ricci_scalar",
    "compute_einstein",
    "validate_tensor_finite",
    # Observable dispatcher
    "ObservableType",
    "Regime",
    "classify_regime",
    "compute_observable_factor",
    "ObservableDispatcher",
    # Energy proxy
    "EnergyProxyStatus",
    "EnergyProxyDiagnostic",
    # v1.0 Observables
    "ReferenceFrame",
    "compute_redshift",
    "RedshiftResult",
    "compute_phase_shift",
    "PhaseShiftResult",
    "compute_photon_delay",
    "TimeDelayResult",
    "compute_interferometer_response",
    "InterferometerResult",
    # v1.0 Numerical GR
    "ConvergenceReport",
    "ConstraintReport",
    "test_convergence_rate",
    "generate_convergence_report",
    "check_hamiltonian_constraint",
    "validate_numerical_solution",
    # v1.0 Validation Pipeline
    "ValidationGate",
    "GateResult",
    "ValidationReport",
    "ValidationPipeline",
    "generate_v1_report",
    # v0.9 SSZ Core
    "SSZValidationStatus",
    "TransportMode",
    "TransportReadiness",
    "xi_from_radius",
    "d_ssz_from_xi",
    "effective_segment_distance",
    "neighborhood_overlap",
    "WorldlineSample",
    "no_copy_constraint",
    "SSZBridgeValidationReport",
    "validate_ssz_bridge_candidate",
    # Claim Gates v1.0
    "EvidenceLevel",
    "ClaimCategory",
    "ClaimStatus",
    "evaluate_claim_gate",
    "evaluate_all_ssz_core_claims",
    "generate_v1_claim_report",
]
