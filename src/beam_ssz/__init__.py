"""SSZ-HOW-TO-BEAM v0.6 research scaffold."""

from .xi import evaluate_xi_x, evaluate_d_s_x
from .metric import SSZMetric
from .validators import validate_candidate
from .geodesics import radial_freefall_velocity, effective_potential
from .radial_scaling import rho_between_x
from .holonomy import closed_loop_invariant

# v0.6 bridge metric
from .bridge_metric import SSZBridgeMetric, create_canonical_bridge, evaluate_bridge_candidate

__all__ = [
    "evaluate_xi_x",
    "evaluate_d_s_x",
    "SSZMetric",
    "validate_candidate",
    "radial_freefall_velocity",
    "effective_potential",
    "rho_between_x",
    "closed_loop_invariant",
    # v0.6 exports
    "SSZBridgeMetric",
    "create_canonical_bridge",
    "evaluate_bridge_candidate",
]
