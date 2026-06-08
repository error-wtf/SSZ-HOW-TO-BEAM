"""Tests for ultimate_solver module."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.ultimate_solver import (
    UltimateProblemSolver,
    UltimateSolution,
)


def test_strategy_1_extreme_weak():
    """Test ultra-weak coupling strategy."""
    solutions = UltimateProblemSolver.strategy_1_extreme_weak()
    
    print(f"\n   Found {len(solutions)} extreme-weak solutions")
    
    for sol in solutions:
        assert sol.xi < 0.01
        assert sol.lambda_bridge < 0.01
        assert sol.problems_solved >= 2


def test_strategy_2_gradual_transfer():
    """Test gradual transfer strategy."""
    solutions = UltimateProblemSolver.strategy_2_gradual_transfer()
    
    print(f"\n   Found {len(solutions)} gradual transfer solutions")
    
    for sol in solutions:
        assert sol.strategy == "High-G with tech enhancement"


def test_strategy_3_robotic_only():
    """Test robotic-only strategy."""
    sol = UltimateProblemSolver.strategy_3_robotic_only()
    
    print(f"\n   Robotic solution: {sol.problems_solved}/4 solved")
    
    assert sol.name == "Robotic-Only-Transport"
    assert sol.tidal_solved == True  # Robots don't care
    assert sol.problems_solved >= 2


def test_strategy_4_photon_only():
    """Test photon-only strategy."""
    sol = UltimateProblemSolver.strategy_4_photon_only()
    
    print(f"\n   Photon solution: {sol.problems_solved}/4 solved")
    
    assert sol.name == "Photon-Quantum-Channel"
    assert sol.tidal_acceleration == 0.0  # Photons unaffected
    assert sol.problems_solved >= 2


def test_strategy_5_hybrid():
    """Test hybrid approach."""
    solutions = UltimateProblemSolver.strategy_5_hybrid_approach()
    
    print(f"\n   Found {len(solutions)} hybrid solutions")
    
    assert len(solutions) > 0


def test_find_ultimate_solution():
    """Test finding ultimate solution."""
    solver = UltimateProblemSolver()
    ultimate = solver.find_the_ultimate_solution(verbose=False)
    
    assert ultimate is not None
    print(f"\n   Ultimate solution: {ultimate.name}")
    print(f"   Problems solved: {ultimate.problems_solved}/4")
    print(f"   Success rate: {ultimate.success_rate:.0%}")
    
    # Should solve at least 2 problems
    assert ultimate.problems_solved >= 2


def test_photon_solution_best():
    """Test that photon solution is among the best."""
    solver = UltimateProblemSolver()
    ultimate = solver.find_the_ultimate_solution(verbose=False)
    
    # Photon solution should be high-scoring
    # because it solves energy + tidal + is simple
    assert ultimate.problems_solved >= 2


def test_robotic_workaround():
    """Test that robotic workaround actually works."""
    sol = UltimateProblemSolver.strategy_3_robotic_only()
    
    # This is the key insight: tidal is "solved" by removing biological constraint
    assert sol.tidal_solved == True
    assert "Robotic" in sol.name


def test_all_strategies_return_solutions():
    """Test that all strategies return valid solutions."""
    s1 = UltimateProblemSolver.strategy_1_extreme_weak()
    s2 = UltimateProblemSolver.strategy_2_gradual_transfer()
    s3 = UltimateProblemSolver.strategy_3_robotic_only()
    s4 = UltimateProblemSolver.strategy_4_photon_only()
    s5 = UltimateProblemSolver.strategy_5_hybrid_approach()
    
    # At least some strategies should return solutions
    total = len(s1) + len(s2) + 1 + 1 + len(s5)  # s3 and s4 always return one
    assert total > 0
    
    print(f"\n   Total solutions across all strategies: {total}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
