"""Tests for boundary condition checks.

Verifies regularity at bridge endpoints without claiming physical existence.
"""

import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

import numpy as np
import pytest

from beam_ssz.bridge_metric import SSZBridgeMetric
from beam_ssz.formation import (
    check_boundary_regularity,
    check_asymptotic_behavior,
    BoundaryStatus,
)


class TestBoundaryConditions:
    """Test boundary regularity checks."""
    
    def test_boundary_check_runs(self):
        """Boundary check runs for canonical bridge."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.5,
            ell0=1e-3,
        )
        
        result = check_boundary_regularity(bridge)
        
        assert result is not None
        assert result.left_status is not None
        assert result.right_status is not None
        assert result.throat_status is not None
    
    def test_symmetric_bridge_regular_endpoints(self):
        """Symmetric bridge should have regular endpoints."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.1,
            ell0=1.0,
        )
        
        result = check_boundary_regularity(bridge)
        
        # For well-behaved bridge, should be regular or at least not singular
        assert result.left_status != BoundaryStatus.SINGULAR
        assert result.right_status != BoundaryStatus.SINGULAR
    
    def test_throat_center_regular(self):
        """Throat center should be regular."""
        bridge = SSZBridgeMetric(
            xi_left=0.2,
            xi_right=0.0,
            lambda_bridge=0.3,
            ell0=1.0,
        )
        
        result = check_boundary_regularity(bridge)
        
        # Throat should be regular for sensible parameters
        assert result.throat_status != BoundaryStatus.SINGULAR
    
    def test_asymptotic_behavior_check_runs(self):
        """Asymptotic behavior check runs."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.0,
            lambda_bridge=0.2,
            ell0=1.0,
        )
        
        result = check_asymptotic_behavior(bridge)
        
        assert result is not None
        assert 'left_behavior' in result or 'right_behavior' in result
    
    def test_determinant_finite_check(self):
        """Metric determinant finiteness is checked."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.1,
            ell0=1.0,
        )
        
        result = check_boundary_regularity(bridge)
        
        # Should have determinant check
        assert hasattr(result, 'metric_determinant_finite')
    
    def test_flat_metric_boundaries(self):
        """Flat metric (Xi=0) has regular boundaries."""
        bridge = SSZBridgeMetric(
            xi_left=0.0,
            xi_right=0.0,
            lambda_bridge=0.0,
            ell0=1.0,
        )
        
        result = check_boundary_regularity(bridge)
        
        # Flat metric should be regular everywhere
        assert result.left_status == BoundaryStatus.REGULAR
        assert result.right_status == BoundaryStatus.REGULAR
        assert result.throat_status == BoundaryStatus.REGULAR


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
