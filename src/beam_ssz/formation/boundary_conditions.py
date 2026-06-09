"""Boundary condition checks for SSZ metric formation.

Verifies regularity at endpoints and throat center.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum, auto


class BoundaryStatus(Enum):
    """Status of boundary regularity."""
    REGULAR = auto()
    SINGULAR = auto()
    DIVERGENT = auto()
    UNDEFINED = auto()
    REGULARITY_VIOLATION = auto()


@dataclass
class BoundaryCheckResult:
    """Result of boundary condition check."""
    left_endpoint_regular: bool
    right_endpoint_regular: bool
    throat_regular: bool
    metric_determinant_finite: bool
    curvature_finite_at_boundaries: bool
    
    # Details
    left_status: BoundaryStatus
    right_status: BoundaryStatus
    throat_status: BoundaryStatus
    
    def to_dict(self) -> Dict:
        return {
            'left_endpoint_regular': self.left_endpoint_regular,
            'right_endpoint_regular': self.right_endpoint_regular,
            'throat_regular': self.throat_regular,
            'metric_determinant_finite': self.metric_determinant_finite,
            'curvature_finite_at_boundaries': self.curvature_finite_at_boundaries,
            'left_status': self.left_status.name,
            'right_status': self.right_status.name,
            'throat_status': self.throat_status.name,
        }


def check_boundary_regularity(
    bridge,
    h: float = 1e-4,
) -> BoundaryCheckResult:
    """Check regularity of SSZ metric at boundaries.
    
    Verifies that metric components, determinant, and curvature
    remain finite at:
    - Left endpoint (u = -1)
    - Right endpoint (u = +1)  
    - Throat center (u = 0)
    
    Args:
        bridge: SSZBridgeMetric instance
        h: Numerical check step size
        
    Returns:
        BoundaryCheckResult with regularity status
    """
    from ..tensor_core import ricci_scalar
    from ..ssz_core.metric import ssz_metric_tensor
    
    check_points = {
        'left': -1.0,
        'throat': 0.0,
        'right': 1.0,
    }
    
    statuses = {}
    determinants_finite = {}
    curvatures_finite = {}
    
    for name, u in check_points.items():
        try:
            # Check metric components
            g_list = bridge.metric_tensor(u)
            g = np.array(g_list)
            
            # Check finiteness
            components_finite = np.all(np.isfinite(g))
            
            # Check determinant
            det = np.linalg.det(g)
            det_finite = np.isfinite(det) and abs(det) > 1e-15
            
            # Check curvature (via Ricci scalar as proxy)
            # REAL FIX: g_func must depend on x[1]=u for proper differentiation
            def g_func(x):
                u_x = float(x[1])
                theta_x = float(x[2])
                return np.array(bridge.metric_tensor(u_x, theta=theta_x), dtype=float)
            
            # Use bridge coordinate u, NOT bridge.R(u)
            position = np.array([0.0, float(u), np.pi/2, 0.0], dtype=float)
            try:
                R = ricci_scalar(g_func, position, h)
                R_finite = np.isfinite(R) and abs(R) < 1e15
            except Exception as e:
                # Curvature check failed - mark as not finite
                R_finite = False
            
            determinants_finite[name] = det_finite
            curvatures_finite[name] = R_finite
            
            # Determine status
            if components_finite and det_finite and R_finite:
                statuses[name] = BoundaryStatus.REGULAR
            elif not components_finite or not det_finite:
                statuses[name] = BoundaryStatus.SINGULAR
            else:
                statuses[name] = BoundaryStatus.REGULARITY_VIOLATION
                
        except (np.linalg.LinAlgError, ValueError, ZeroDivisionError):
            statuses[name] = BoundaryStatus.UNDEFINED
            determinants_finite[name] = False
            curvatures_finite[name] = False
    
    return BoundaryCheckResult(
        left_endpoint_regular=statuses.get('left') == BoundaryStatus.REGULAR,
        right_endpoint_regular=statuses.get('right') == BoundaryStatus.REGULAR,
        throat_regular=statuses.get('throat') == BoundaryStatus.REGULAR,
        metric_determinant_finite=all(determinants_finite.values()),
        curvature_finite_at_boundaries=all(curvatures_finite.values()),
        left_status=statuses.get('left', BoundaryStatus.UNDEFINED),
        right_status=statuses.get('right', BoundaryStatus.UNDEFINED),
        throat_status=statuses.get('throat', BoundaryStatus.UNDEFINED),
    )


def check_asymptotic_behavior(
    bridge,
    n_points: int = 20,
) -> Dict:
    """Check asymptotic behavior near boundaries.
    
    Examines how metric components behave as u approaches ±1.
    
    Args:
        bridge: SSZBridgeMetric instance
        n_points: Number of points near each boundary
        
    Returns:
        Dictionary with asymptotic analysis
    """
    # Points near left endpoint
    u_left = np.linspace(-1, -0.9, n_points)
    
    # Points near right endpoint  
    u_right = np.linspace(0.9, 1, n_points)
    
    results = {
        'left_behavior': [],
        'right_behavior': [],
    }
    
    for u in u_left:
        try:
            g = bridge.metric_tensor(u)
            D = bridge.D(u)
            s = bridge.s(u)
            results['left_behavior'].append({
                'u': float(u),
                'D': float(D),
                's': float(s),
                'g_tt': float(g[0][0]),
            })
        except:
            pass
    
    for u in u_right:
        try:
            g = bridge.metric_tensor(u)
            D = bridge.D(u)
            s = bridge.s(u)
            results['right_behavior'].append({
                'u': float(u),
                'D': float(D),
                's': float(s),
                'g_tt': float(g[0][0]),
            })
        except:
            pass
    
    # Analyze trends
    if len(results['left_behavior']) > 1:
        left_Ds = [p['D'] for p in results['left_behavior']]
        left_trend = 'decreasing' if left_Ds[-1] < left_Ds[0] else 'increasing'
        results['left_trend'] = left_trend
    
    if len(results['right_behavior']) > 1:
        right_Ds = [p['D'] for p in results['right_behavior']]
        right_trend = 'decreasing' if right_Ds[-1] < right_Ds[0] else 'increasing'
        results['right_trend'] = right_trend
    
    return results
