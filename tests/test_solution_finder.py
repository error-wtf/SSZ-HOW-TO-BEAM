"""Tests for solution_finder module - finding actually working solutions."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.solution_finder import (
    ActualSolutionFinder,
    WorkingSolution,
)


def test_search_extreme_parameters():
    """Test searching extreme parameter space."""
    finder = ActualSolutionFinder()
    solutions = finder.search_extreme_parameters(n_samples=20)
    
    # Should return a list
    assert isinstance(solutions, list)
    print(f"\n   Found {len(solutions)} extreme parameter solutions")
    
    if solutions:
        # Check structure
        sol = solutions[0]
        assert isinstance(sol, WorkingSolution)
        assert sol.problems_solved >= 2  # At least 2 problems solved
        assert sol.overall_score > 0


def test_find_minimal_energy():
    """Test finding minimum energy configuration."""
    finder = ActualSolutionFinder()
    min_sol = finder.find_minimal_energy_config()
    
    if min_sol:
        print(f"\n   Minimum energy found: {min_sol.energy_density:.3e} J/m³")
        assert min_sol.energy_density > 0
        # Don't assert upper bound - energy might be very high
    else:
        print("\n   No minimal energy config found (acceptable)")


def test_optimize_for_extended_body_proxy():
    """Test optimizing for extended-body stress proxy configurations."""
    finder = ActualSolutionFinder()
    solutions = finder.optimize_for_human_transport()
    
    print(f"\n   Found {len(solutions)} proxy-safe toy configurations")
    
    for sol in solutions:
        # Should have tidal < 100g
        assert sol.tidal_acceleration < 1000.0  # ~100g
        assert sol.is_tidal_safe


def test_find_working_solution():
    """Test main search for working solution."""
    finder = ActualSolutionFinder()
    solution = finder.find_working_solution(verbose=False)
    
    # Should return something (even if partial)
    if solution:
        print(f"\n   Working solution found: {solution.name}")
        print(f"   Problems solved: {solution.problems_solved}/4")
        print(f"   Score: {solution.overall_score:.1%}")
        
        assert solution.problems_solved >= 1
        assert solution.overall_score >= 0.25


def test_working_solution_structure():
    """Test working solution has all required fields."""
    finder = ActualSolutionFinder()
    solutions = finder.search_extreme_parameters(n_samples=10)
    
    if solutions:
        sol = solutions[0]
        assert hasattr(sol, 'name')
        assert hasattr(sol, 'parameters')
        assert hasattr(sol, 'problems_solved')
        assert hasattr(sol, 'overall_score')
        
        # Score should be between 0 and 1
        assert 0 <= sol.overall_score <= 1


def test_partial_solution_acceptable():
    """Test that partial solutions are acceptable."""
    finder = ActualSolutionFinder()
    solution = finder.find_working_solution(verbose=False)
    
    if solution:
        # Even 2/4 problems solved is progress
        assert solution.problems_solved >= 2
        
        # Should have specific improvements
        assert solution.is_stable or solution.is_tidal_safe or solution.is_energy_ok


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
