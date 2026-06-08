"""Tests for problem_solutions module - testing concrete solutions."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.problem_solutions import (
    ProblemSolver,
    SolutionProposal,
)


def test_solve_high_energy_density():
    """Test finding solutions for high energy density."""
    solutions = ProblemSolver.solve_high_energy_density(target_density=1e36)
    
    assert len(solutions) > 0
    assert all(isinstance(s, SolutionProposal) for s in solutions)
    
    # Should have at least parameter adjustment and exotic matter solutions
    types = [s.solution_type for s in solutions]
    assert 'parameter_adjustment' in types or 'physics_mechanism' in types
    
    print(f"\n   Found {len(solutions)} solutions for high energy density")
    for i, sol in enumerate(solutions, 1):
        print(f"   {i}. {sol.solution_type}: TRL={sol.technical_readiness}, risk={sol.physics_risk}")


def test_solve_extreme_tidal_forces():
    """Test finding solutions for extreme tidal forces."""
    solutions = ProblemSolver.solve_extreme_tidal_forces(a_max=98.1)
    
    assert len(solutions) > 0
    
    # Should have large scale and workaround solutions
    descriptions = [s.mechanism_description.lower() for s in solutions]
    assert any('scale' in d or 'large' in d for d in descriptions)
    
    print(f"\n   Found {len(solutions)} solutions for tidal forces")
    for i, sol in enumerate(solutions, 1):
        print(f"   {i}. {sol.solution_type}: {sol.estimated_timeline}")


def test_solve_energy_source():
    """Test finding solutions for energy source."""
    solutions = ProblemSolver.solve_energy_source()
    
    assert len(solutions) > 0
    
    print(f"\n   Found {len(solutions)} solutions for energy source")


def test_solve_formation_dynamics():
    """Test finding solutions for formation dynamics."""
    solutions = ProblemSolver.solve_formation_dynamics()
    
    assert len(solutions) > 0
    
    print(f"\n   Found {len(solutions)} solutions for formation dynamics")


def test_find_all_solutions():
    """Test finding all solutions."""
    all_solutions = ProblemSolver.find_all_solutions(verbose=False)
    
    assert 'high_energy' in all_solutions
    assert 'tidal_forces' in all_solutions
    assert 'energy_source' in all_solutions
    assert 'formation' in all_solutions
    
    total = sum(len(sols) for sols in all_solutions.values())
    print(f"\n   Total solutions found: {total}")
    
    for category, solutions in all_solutions.items():
        tested = sum(1 for s in solutions if s.tested)
        print(f"   - {category}: {len(solutions)} solutions, {tested} tested")


def test_solution_proposal_structure():
    """Test solution proposal has all required fields."""
    solutions = ProblemSolver.solve_high_energy_density()
    
    for sol in solutions:
        assert hasattr(sol, 'problem_name')
        assert hasattr(sol, 'solution_type')
        assert hasattr(sol, 'mechanism_description')
        assert hasattr(sol, 'technical_readiness')
        assert hasattr(sol, 'physics_risk')
        assert hasattr(sol, 'remaining_issues')
        
        # TRL should be 1-9
        assert 1 <= sol.technical_readiness <= 9
        
        # Physics risk should be valid
        assert sol.physics_risk in ['low', 'medium', 'high', 'unknown']


def test_test_proposed_solution():
    """Test testing a proposed solution."""
    solutions = ProblemSolver.solve_high_energy_density()
    
    # Find a tested solution with parameters
    tested_sols = [s for s in solutions if s.tested and s.proposed_parameters]
    
    if tested_sols:
        sol = tested_sols[0]
        result = ProblemSolver.test_proposed_solution(sol)
        
        # Should return a FeasibilityResult or None
        assert result is None or hasattr(result, 'overall_feasibility')


def test_solution_categories():
    """Test that solutions cover different categories."""
    all_solutions = ProblemSolver.find_all_solutions(verbose=False)
    
    all_types = []
    for solutions in all_solutions.values():
        all_types.extend([s.solution_type for s in solutions])
    
    # Should have diverse solution types
    unique_types = set(all_types)
    print(f"\n   Solution types: {', '.join(unique_types)}")
    
    assert len(unique_types) >= 2  # At least some variety


def test_timeline_realism():
    """Test that timelines are realistic descriptions."""
    all_solutions = ProblemSolver.find_all_solutions(verbose=False)
    
    for solutions in all_solutions.values():
        for sol in solutions:
            # Timeline should be a string with some indication
            assert len(sol.estimated_timeline) > 0
            assert isinstance(sol.estimated_timeline, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
