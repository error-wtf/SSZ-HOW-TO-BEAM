"""Tests for candidate_mitigation_strategies module - candidate strategies."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.candidate_mitigation_strategies import (
    MitigationStrategyExplorer,
    FormationStrategy,
    EnergySourceStrategy,
)


def test_explore_formation_strategies():
    """Test formation strategy exploration."""
    explorer = MitigationStrategyExplorer()
    strategies = explorer.explore_formation_strategies()
    
    print(f"\n   Found {len(strategies)} formation strategies")
    
    assert len(strategies) > 0
    assert all(isinstance(s, FormationStrategy) for s in strategies)
    
    for strat in strategies:
        assert strat.formation_time > 0
        assert strat.energy_required > 0
        assert 1 <= strat.physics_readiness <= 9
        assert 0 <= strat.success_probability <= 1
        
        print(f"   - {strat.name}: TRL-{strat.physics_readiness}, P={strat.success_probability:.0%}")


def test_explore_energy_strategies():
    """Test energy source strategy exploration."""
    explorer = MitigationStrategyExplorer()
    strategies = explorer.explore_energy_strategies()
    
    print(f"\n   Found {len(strategies)} energy source strategies")
    
    assert len(strategies) > 0
    assert all(isinstance(s, EnergySourceStrategy) for s in strategies)
    
    for strat in strategies:
        assert strat.energy_density_available > 0
        assert strat.energy_density_needed > 0
        assert 0 <= strat.efficiency_factor <= 1
        assert 0 <= strat.physics_plausibility <= 1
        
        print(f"   - {strat.name}: {strat.source_type}, plausibility={strat.physics_plausibility:.0%}")


def test_get_all_strategies():
    """Test getting all strategies."""
    explorer = MitigationStrategyExplorer()
    formation, energy = explorer.get_all_strategies()
    
    print(f"\n   Complete strategy set:")
    print(f"   - Formation: {len(formation)} strategies")
    print(f"   - Energy: {len(energy)} strategies")
    print(f"   - Total: {len(formation) + len(energy)} strategies")
    
    assert len(formation) > 0
    assert len(energy) > 0


def test_formation_strategies_have_mechanisms():
    """Test that formation strategies have detailed mechanisms."""
    explorer = MitigationStrategyExplorer()
    strategies = explorer.explore_formation_strategies()
    
    for strat in strategies:
        assert len(strat.mechanism) > 100  # Detailed description
        assert len(strat.required_conditions) > 0
        assert len(strat.critical_parameters) > 0


def test_energy_strategies_have_details():
    """Test that energy strategies have all required details."""
    explorer = MitigationStrategyExplorer()
    strategies = explorer.explore_energy_strategies()
    
    for strat in strategies:
        assert len(strat.mechanism) > 100
        assert len(strat.advantages) > 0
        assert len(strat.challenges) > 0
        assert strat.estimated_power_output > 0


def test_formation_probabilities_realistic():
    """Test that success probabilities are realistic."""
    explorer = MitigationStrategyExplorer()
    strategies = explorer.explore_formation_strategies()
    
    for strat in strategies:
        # All should have non-zero but <100% probability
        assert 0 < strat.success_probability < 1
        print(f"   {strat.name}: {strat.success_probability:.0%} success probability")


def test_energy_plausibility_varies():
    """Test that different strategies have different plausibility."""
    explorer = MitigationStrategyExplorer()
    strategies = explorer.explore_energy_strategies()
    
    plausibilities = [s.physics_plausibility for s in strategies]
    
    # Should have variety
    assert max(plausibilities) > min(plausibilities)
    
    print(f"\n   Plausibility range: {min(plausibilities):.0%} to {max(plausibilities):.0%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
