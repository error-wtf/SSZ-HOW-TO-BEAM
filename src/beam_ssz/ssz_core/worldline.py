"""SSZ continuous worldline validation.

x^μ(τ): A → B with dτ > 0.
No discontinuity, no duplicate branch.
"""

import numpy as np
from typing import List, Callable, Optional, Dict
from dataclasses import dataclass

from .status import WorldlineStatus, SSZValidationStatus


@dataclass
class WorldlineSample:
    """Single sample along worldline."""
    tau: float = 0.0  # Worldline parameter (must be monotonic)
    x: np.ndarray = None  # Coordinates [t, r, theta, phi]
    # Also accept individual coordinates for convenience
    t: float = 0.0
    r: float = 1.0
    theta: float = 0.0
    phi: float = 0.0
    
    def __post_init__(self):
        if self.x is None:
            self.x = np.array([self.t, self.r, self.theta, self.phi])


@dataclass
class WorldlineResult:
    """Result of worldline validation."""
    status: WorldlineStatus
    tau_monotonic: bool
    max_jump: float
    d_tau_positive: bool
    details: Dict
    
    @property
    def continuous(self) -> bool:
        """Check if worldline is continuous."""
        return self.tau_monotonic and self.d_tau_positive and self.max_jump < 100.0


def validate_worldline_continuity(
    samples: List[WorldlineSample],
    jump_threshold: float = 100.0,
    bridge_metric_explains: Optional[Callable] = None,
) -> WorldlineResult:
    """Validate worldline continuity.
    
    Args:
        samples: List of worldline samples
        jump_threshold: Maximum allowed coordinate jump
        bridge_metric_explains: Optional function to check if bridge explains jump
    
    Returns:
        WorldlineResult with status
    """
    if len(samples) < 2:
        return WorldlineResult(
            WorldlineStatus.WORLDLINE_PASS,  # Trivially continuous
            True, 0.0, True,
            {"n_samples": len(samples), "trivial": True}
        )
    
    details = {
        "n_samples": len(samples),
        "tau_values": [s.tau for s in samples],
    }
    
    # Check tau strictly increasing
    taus = [s.tau for s in samples]
    tau_diffs = np.diff(taus)
    
    tau_monotonic = np.all(tau_diffs > 0)
    min_d_tau = np.min(tau_diffs) if len(tau_diffs) > 0 else 0.0
    
    details["tau_monotonic"] = tau_monotonic
    details["min_d_tau"] = min_d_tau
    details["d_tau_positive"] = min_d_tau > 0
    
    if not tau_monotonic:
        return WorldlineResult(
            WorldlineStatus.TAU_NOT_MONOTONIC,
            False, 0.0, min_d_tau > 0,
            details
        )
    
    if min_d_tau <= 0:
        return WorldlineResult(
            WorldlineStatus.D_TAU_NON_POSITIVE,
            True, 0.0, False,
            details
        )
    
    # Check coordinate jumps
    max_jump = 0.0
    large_jumps = []
    
    for i in range(len(samples) - 1):
        x1 = samples[i].x
        x2 = samples[i+1].x
        
        # Check for NaN
        if not np.all(np.isfinite(x1)) or not np.all(np.isfinite(x2)):
            details["nan_at_index"] = i
            return WorldlineResult(
                WorldlineStatus.COORDINATE_NAN,
                True, max_jump, True,
                details
            )
        
        # Spatial jump
        spatial_jump = np.linalg.norm(x2[1:] - x1[1:])
        
        if spatial_jump > max_jump:
            max_jump = spatial_jump
        
        if spatial_jump > jump_threshold:
            large_jumps.append({
                "index": i,
                "jump": spatial_jump,
                "explained_by_bridge": False,
            })
    
    details["max_jump"] = max_jump
    details["large_jumps"] = large_jumps
    
    if large_jumps:
        # Check if bridge explains jumps
        unexplained = [j for j in large_jumps if not j.get("explained_by_bridge", False)]
        
        if unexplained:
            return WorldlineResult(
                WorldlineStatus.COORDINATE_JUMP,
                True, max_jump, True,
                details
            )
    
    # Check for duplicate branches (simplified: check if any tau appears twice)
    if len(set(taus)) != len(taus):
        return WorldlineResult(
            WorldlineStatus.DUPLICATE_BRANCH,
            True, max_jump, True,
            details
        )
    
    # All checks pass
    return WorldlineResult(
        WorldlineStatus.WORLDLINE_PASS,
        True, max_jump, True,
        details
    )


def proper_time_proxy(
    samples: List[WorldlineSample],
    metric_func: Optional[Callable] = None,
) -> float:
    """Compute finite proper time proxy.
    
    Args:
        samples: Worldline samples
        metric_func: Optional metric function g(x)
    
    Returns:
        Proper time proxy (finite)
    """
    if len(samples) < 2:
        return 0.0
    
    tau_proper = 0.0
    
    for i in range(len(samples) - 1):
        tau1 = samples[i].tau
        tau2 = samples[i+1].tau
        
        # Simple: sum of d_tau
        # With metric: would compute ∫ ds where ds² = g_μν dx^μ dx^ν
        d_tau = tau2 - tau1
        
        if metric_func:
            # Compute metric at midpoint
            x_mid = (samples[i].x + samples[i+1].x) / 2.0
            g = metric_func(x_mid)
            
            # For now, simple sum (full metric integration would be more complex)
            tau_proper += d_tau
        else:
            tau_proper += d_tau
    
    return tau_proper


def check_worldline_proxy_pass(
    result: WorldlineResult,
) -> bool:
    """Check if worldline proxy passes minimum requirements.
    
    Args:
        result: WorldlineResult
    
    Returns:
        True if passes
    """
    return (
        result.tau_monotonic and
        result.d_tau_positive and
        result.status == WorldlineStatus.WORLDLINE_PASS
    )
