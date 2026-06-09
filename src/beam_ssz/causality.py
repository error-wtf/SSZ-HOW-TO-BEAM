"""Causality gates."""
from __future__ import annotations

import numpy as np
from typing import Dict, Tuple


def no_closed_timelike_curve(ctc_flag: bool) -> bool:
    return not ctc_flag


def proper_time_monotonic(delta_tau: float) -> bool:
    return delta_tau > 0.0


def check_causality(point_a: np.ndarray, point_b: np.ndarray, xi: float = 0.1) -> Dict:
    """Check causality between two points.
    
    Args:
        point_a: Point A coordinates
        point_b: Point B coordinates
        xi: SSZ parameter
        
    Returns:
        Dict with causality check results
    """
    # Calculate proper time interval
    dt = point_b[0] - point_a[0]
    dr = np.linalg.norm(point_b[1:] - point_a[1:])
    
    # Simple causality check: dt > 0 and no superluminal signaling
    is_timelike = abs(dt) > dr / (1.0 + xi)
    is_causal = dt > 0
    
    return {
        "is_causal": is_causal,
        "is_timelike": is_timelike,
        "delta_t": float(dt),
        "spatial_distance": float(dr),
        "status": "CAUSAL" if is_causal else "NOT_CAUSAL"
    }


class CausalityAnalyzer:
    """Analyze causality in SSZ framework."""
    
    def __init__(self, xi_func=None):
        self.xi_func = xi_func or (lambda r: 0.1)
        
    def analyze_path(self, path: list) -> Dict:
        """Analyze causality along a path."""
        results = []
        for i in range(len(path) - 1):
            result = check_causality(np.array(path[i]), np.array(path[i+1]))
            results.append(result)
        
        all_causal = all(r["is_causal"] for r in results)
        return {
            "all_causal": all_causal,
            "segment_results": results,
            "total_segments": len(results)
        }
