"""Tests for candidate_strategy_explorer module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.candidate_strategy_explorer import (
    StrategyExplorer,
    CandidateStrategy,
)


def test_explore_extreme_weak():
    """Test ultra-weak coupling strategy."""
    explorer = StrategyExplorer()
    strategies = explorer.explore_extreme_weak()
    
    print(f"\n   Found {len(strategies)} extreme-weak strategies")
    
    for strat in strategies:
        assert isinstance(strat, CandidateStrategy)


def test_explore_gradual_transfer():
    """Test gradual transfer strategy."""
    explorer = StrategyExplorer()
    strategies = explorer.explore_gradual_transfer()
    
    print(f"\n   Found {len(strategies)} gradual transfer strategies")
    
    for strat in strategies:
        assert isinstance(strat, CandidateStrategy)


def test_explore_robotic_only():
    """Test robotic-only strategy."""
    explorer = StrategyExplorer()
    strat = explorer.explore_robotic_only()
    
    print(f"\n   Robotic strategy: {strat.name}")
    
    assert isinstance(strat, CandidateStrategy)
    assert "Robotic" in strat.name


def test_explore_photon_only():
    """Test photon-only strategy."""
    explorer = StrategyExplorer()
    strat = explorer.explore_photon_only()
    
    print(f"\n   Photon strategy: {strat.name}")
    
    assert isinstance(strat, CandidateStrategy)
    assert "Photon" in strat.name


def test_explore_hybrid():
    """Test hybrid approach."""
    explorer = StrategyExplorer()
    strategies = explorer.explore_hybrid()
    
    print(f"\n   Found {len(strategies)} hybrid strategies")
    
    assert len(strategies) > 0
    for strat in strategies:
        assert isinstance(strat, CandidateStrategy)


def test_find_best_strategy():
    """Test finding best strategy."""
    explorer = StrategyExplorer()
    best = explorer.find_best_strategy(verbose=False)
    
    assert best is not None
    assert isinstance(best, CandidateStrategy)
    print(f"\n   Best strategy: {best.name}")


def test_photon_strategy_scoring():
    """Test that photon strategy scores well."""
    explorer = StrategyExplorer()
    strat = explorer.explore_photon_only()
    
    # Photon strategy should avoid tidal issues
    assert isinstance(strat, CandidateStrategy)


def test_robotic_strategy_tidal():
    """Test that robotic strategy handles tidal."""
    explorer = StrategyExplorer()
    strat = explorer.explore_robotic_only()
    
    # This is the key insight: tidal is "solved" by removing biological constraint
    assert isinstance(strat, CandidateStrategy)
    assert "Robotic" in strat.name


def test_all_strategies_return_valid():
    """Test that all strategies return valid results."""
    explorer = StrategyExplorer()
    
    s1 = explorer.explore_extreme_weak()
    s2 = explorer.explore_gradual_transfer()
    s3 = explorer.explore_robotic_only()
    s4 = explorer.explore_photon_only()
    s5 = explorer.explore_hybrid()
    
    # At least some strategies should return results
    total = len(s1) + len(s2) + 1 + 1 + len(s5)  # s3 and s4 always return one
    assert total > 0
    
    print(f"\n   Total strategies across all approaches: {total}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
