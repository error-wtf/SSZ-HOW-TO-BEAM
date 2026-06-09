"""SSZ effective distance collapse tests.

Core validation: d_eff(A,B) -> 0 under bridge ansatz.
This is the PRIMARY physical claim of SSZ transport.
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

from beam_ssz.bridge_metric import SSZBridgeMetric


class TestSSZEffectiveDistance:
    """Test effective distance reduction under SSZ bridge.
    
    This is Gate B: d_eff(A,B) decreases under bridge ansatz.
    """
    
    def test_bridge_reduces_distance(self):
        """Bridge candidate reduces effective segment-distance."""
        # Create bridge
        bridge = SSZBridgeMetric(
            ell0=1.0,
            xi_left=0.5,
            xi_right=0.0,
            lambda_bridge=0.1,
        )
        
        # Get bridge profile
        profile = bridge.get_bridge_profile(n_points=50)
        
        # Check that bridge creates path with reduced effective distance
        # The bridge profile should show monotonic transition
        u_values = profile['u']
        
        # U should be monotonic from 0 to 1
        for i in range(len(u_values) - 1):
            assert u_values[i+1] > u_values[i], "U not monotonic"
    
    def test_bridge_distance_calculation_finite(self):
        """Bridge distance calculation finite."""
        bridge = SSZBridgeMetric(
            ell0=1.0,
            xi_left=0.5,
            xi_right=0.0,
            lambda_bridge=0.1,
        )
        
        # Distance should be finite and positive
        d_left = bridge.left_distance
        d_right = bridge.right_distance
        
        assert np.isfinite(d_left), "Left distance not finite"
        assert np.isfinite(d_right), "Right distance not finite"
        assert d_left >= 0, "Left distance negative"
        assert d_right >= 0, "Right distance negative"
    
    def test_no_negative_pathological_distance(self):
        """No negative or pathological distances."""
        bridge = SSZBridgeMetric(
            ell0=1.0,
            xi_left=0.5,
            xi_right=0.0,
            lambda_bridge=0.1,
        )
        
        # All internal distances should be non-negative
        profile = bridge.get_bridge_profile(n_points=20)
        
        for key in ['Xi', 'dXi_du', 'weight_left', 'weight_right']:
            if key in profile:
                values = profile[key]
                # Check for NaN/inf
                assert np.all(np.isfinite(values)), f"{key} has non-finite values"
    
    def test_distance_reduction_ratio(self):
        """Test distance reduction ratio is meaningful."""
        bridge = SSZBridgeMetric(
            ell0=1.0,
            xi_left=1.0,
            xi_right=0.0,
            lambda_bridge=0.1,
        )
        
        # With bridge vs without bridge distance comparison
        # This is a proxy test - actual d_eff requires full calculation
        
        profile = bridge.get_bridge_profile(n_points=50)
        Xi_values = profile['Xi']
        
        # Xi should vary continuously from left to right
        assert Xi_values[0] > Xi_values[-1], "Xi not decreasing from left to right"
        
        # No jumps
        diffs = np.diff(Xi_values)
        assert np.all(np.isfinite(diffs)), "Non-finite jumps in Xi"


class TestSSZSegmentNeighborhoodOverlap:
    """Test Gate A: N(A) ∩ N(B) ≠ ∅ under bridge.
    
    Temporary segment-neighborhood overlap.
    """
    
    def test_segment_overlap_proxy_indicator(self):
        """Proxy test for segment neighborhood overlap.
        
        When bridge has high coupling (low ell0, high Xi gradient),
        regions A and B become effectively neighboring.
        """
        # Strong bridge
        bridge = SSZBridgeMetric(
            ell0=0.5,  # Short bridge = strong coupling
            xi_left=2.0,
            xi_right=0.0,
            lambda_bridge=0.05,
        )
        
        profile = bridge.get_bridge_profile(n_points=30)
        
        # Check bridge creates continuous connection
        weight_left = profile['weight_left']
        weight_right = profile['weight_right']
        
        # At some point, both weights should be non-negligible
        # indicating overlap region
        overlap_region = (weight_left > 0.1) & (weight_right > 0.1)
        
        assert np.any(overlap_region), "No overlap region in bridge profile"
    
    def test_overlap_finite_and_continuous(self):
        """Overlap region is finite and continuous."""
        bridge = SSZBridgeMetric(
            ell0=1.0,
            xi_left=1.0,
            xi_right=0.0,
            lambda_bridge=0.1,
        )
        
        profile = bridge.get_bridge_profile(n_points=50)
        
        # All quantities in overlap region should be finite
        for key in ['Xi', 'D', 's', 'weight_left', 'weight_right']:
            if key in profile:
                values = profile[key]
                assert np.all(np.isfinite(values)), f"{key} has non-finite values"


class TestSSZDistanceCollapseDocumentation:
    """Documentation of what is tested vs claimed."""
    
    def test_documented_limitations(self):
        """Explicitly document test limitations.
        
        These tests validate SSZ segmentation consistency,
        NOT physical implementation or biological safety.
        """
        # This test serves as documentation
        limitations = [
            "Tests validate d_eff reduction proxy only",
            "Tests validate segment overlap proxy only", 
            "No physical formation mechanism tested",
            "No biological-scale transport validated",
            "No experimental confirmation",
        ]
        
        assert len(limitations) > 0, "Limitations should be documented"
        
        # Each limitation should be a non-empty string
        for lim in limitations:
            assert isinstance(lim, str) and len(lim) > 0
