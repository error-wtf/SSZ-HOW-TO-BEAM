"""SSZ v0.9 Core: Continuous-worldline bridge validation.

Core SSZ model:
- d_eff(A,B) → 0
- x^μ(τ): A → B with dτ > 0
- N(A) ∩ N(B) ≠ ∅
- CONTINUOUS_WORLDLINE mode (no copy/reconstruction)
"""

# Status enums
from .status import (
    SSZValidationStatus,
    TransportMode,
    TransportReadiness,
    SegmentationStatus,
    WorldlineStatus,
    NoCopyStatus,
)

# Segmentation
from .segmentation import (
    xi_from_radius,
    d_ssz_from_xi,
    s_ssz_from_xi,
    validate_segmentation_state,
    validate_segmentation_monotonicity,
    SegmentationResult,
)

# Effective distance
from .effective_distance import (
    effective_segment_distance,
    bridge_effective_distance,
    distance_reduction_ratio,
    validate_effective_distance,
    EffectiveDistanceResult,
)

# Neighborhood overlap
from .neighborhood import (
    segment_neighborhood,
    neighborhood_overlap,
    has_segment_overlap,
    validate_neighborhood_proxy,
    NeighborhoodResult,
)

# Worldline
from .worldline import (
    WorldlineSample,
    validate_worldline_continuity,
    proper_time_proxy,
    check_worldline_proxy_pass,
    WorldlineResult,
)

# Transport mode
from .transport_mode import (
    validate_transport_mode,
    no_copy_constraint,
    check_person_transport_readiness,
    TransportModeResult,
)

# Validation pipeline
from .validation import (
    SSZBridgeValidationReport,
    validate_ssz_bridge_candidate,
    generate_scientific_position,
)

# Metric
from .metric import (
    ssz_metric_tensor,
    ssz_metric_determinant,
    ssz_metric_inverse,
    validate_ssz_metric,
    check_critical_radius_regularization,
)

__all__ = [
    # Status
    "SSZValidationStatus",
    "TransportMode",
    "TransportReadiness",
    "SegmentationStatus",
    "WorldlineStatus",
    "NoCopyStatus",
    # Segmentation
    "xi_from_radius",
    "d_ssz_from_xi",
    "s_ssz_from_xi",
    "validate_segmentation_state",
    "validate_segmentation_monotonicity",
    "SegmentationResult",
    # Effective distance
    "effective_segment_distance",
    "bridge_effective_distance",
    "distance_reduction_ratio",
    "validate_effective_distance",
    "EffectiveDistanceResult",
    # Neighborhood
    "segment_neighborhood",
    "neighborhood_overlap",
    "has_segment_overlap",
    "validate_neighborhood_proxy",
    "NeighborhoodResult",
    # Worldline
    "WorldlineSample",
    "validate_worldline_continuity",
    "proper_time_proxy",
    "check_worldline_proxy_pass",
    "WorldlineResult",
    # Transport mode
    "validate_transport_mode",
    "no_copy_constraint",
    "check_person_transport_readiness",
    "TransportModeResult",
    # Validation
    "SSZBridgeValidationReport",
    "validate_ssz_bridge_candidate",
    "generate_scientific_position",
    # Metric
    "ssz_metric_tensor",
    "ssz_metric_determinant",
    "ssz_metric_inverse",
    "validate_ssz_metric",
    "check_critical_radius_regularization",
]
