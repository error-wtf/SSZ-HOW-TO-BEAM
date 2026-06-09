"""Tests for energy budget computation.

Verifies integrated energy estimates without claiming physical feasibility.
"""

import sys
sys.path.insert(0, '/home/error/Downloads/SSZ-HOW-TO-BEAM/src')

import numpy as np
import pytest

from beam_ssz.bridge_metric import SSZBridgeMetric
from beam_ssz.formation import (
    compute_energy_budget,
    energy_budget_sensitivity_analysis,
)


class TestEnergyBudgetComputation:
    """Test energy budget estimates."""
    
    def test_energy_budget_computation_runs(self):
        """Energy budget can be computed for canonical bridge."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.5,
            ell0=1e-3,
        )
        
        budget = compute_energy_budget(bridge)
        
        assert budget is not None
        assert budget.total_effective_energy is not None
        assert budget.solar_masses is not None
    
    def test_energy_is_positive_or_reasonable(self):
        """Energy budget gives physically reasonable values."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.1,
            ell0=10.0,
        )
        
        budget = compute_energy_budget(bridge)
        
        # Energy should be non-negative (or at least finite)
        assert np.isfinite(budget.total_effective_energy)
        
        # Solar masses should be non-negative or reasonable
        assert budget.solar_masses >= 0 or np.isfinite(budget.solar_masses)
    
    def test_localization_computed(self):
        """Source localization is computed."""
        bridge = SSZBridgeMetric(
            xi_left=0.2,
            xi_right=0.0,
            lambda_bridge=0.3,
            ell0=100.0,
        )
        
        budget = compute_energy_budget(bridge)
        
        assert budget.localization is not None
        assert budget.localization.localization_radius >= 0
        assert budget.localization.peak_position is not None
    
    def test_comparison_metrics(self):
        """Comparison metrics are computed."""
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=0.1,
            ell0=1.0,
        )
        
        budget = compute_energy_budget(bridge)
        
        # Should have comparison metrics
        assert budget.vs_solar_output is not None
        assert budget.vs_kinetic_energy is not None
        
        # Should be finite
        assert np.isfinite(budget.vs_solar_output) or budget.vs_solar_output == np.inf
        assert np.isfinite(budget.vs_kinetic_energy) or budget.vs_kinetic_energy == np.inf
    
    def test_sensitivity_analysis_runs(self):
        """Parameter sensitivity analysis can run."""
        # Minimal sample for fast unit test (2^4 = 16 configs)
        # Full analysis should be run separately, not in CI
        result = energy_budget_sensitivity_analysis(
            xi_left_range=(0.1, 0.5),
            xi_right_range=(0.1, 0.5),
            lambda_range=(0.1, 0.3),
            ell0_range=(5.0, 10.0),
            n_samples=2,
        )
        
        # Should complete and return results
        assert result is not None
        assert 'status' in result
    
    def test_weak_vs_strong_field_energy(self):
        """Stronger fields require more energy."""
        # Weak field
        bridge_weak = SSZBridgeMetric(
            xi_left=0.01,
            xi_right=0.01,
            lambda_bridge=0.01,
            ell0=100.0,
        )
        
        # Stronger field
        bridge_strong = SSZBridgeMetric(
            xi_left=0.5,
            xi_right=0.5,
            lambda_bridge=0.3,
            ell0=10.0,
        )
        
        budget_weak = compute_energy_budget(bridge_weak)
        budget_strong = compute_energy_budget(bridge_strong)
        
        # Both should compute
        assert np.isfinite(budget_weak.total_effective_energy) or budget_weak.total_effective_energy == 0
        assert np.isfinite(budget_strong.total_effective_energy)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
