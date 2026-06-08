"""Tests for final_solutions module - the last 2 problems solved."""
import sys
sys.path.insert(0, 'src')

import pytest

from beam_ssz.final_solutions import (
    FinalProblemSolver,
    FormationSolution,
    EnergySourceSolution,
)


def test_solve_formation_problem():
    """Test formation problem solutions."""
    solutions = FinalProblemSolver.solve_formation_problem()
    
    print(f"\n   Found {len(solutions)} formation solutions")
    
    assert len(solutions) > 0
    assert all(isinstance(s, FormationSolution) for s in solutions)
    
    for sol in solutions:
        assert sol.formation_time > 0
        assert sol.energy_required > 0
        assert 1 <= sol.physics_readiness <= 9
        assert 0 <= sol.success_probability <= 1
        
        print(f"   - {sol.name}: TRL-{sol.physics_readiness}, P={sol.success_probability:.0%}")


def test_solve_energy_source_problem():
    """Test energy source solutions."""
    solutions = FinalProblemSolver.solve_energy_source_problem()
    
    print(f"\n   Found {len(solutions)} energy source solutions")
    
    assert len(solutions) > 0
    assert all(isinstance(s, EnergySourceSolution) for s in solutions)
    
    for sol in solutions:
        assert sol.energy_density_available > 0
        assert sol.energy_density_needed > 0
        assert 0 <= sol.efficiency_factor <= 1
        assert 0 <= sol.physics_plausibility <= 1
        
        print(f"   - {sol.name}: {sol.source_type}, plausibility={sol.physics_plausibility:.0%}")


def test_get_complete_solution_set():
    """Test getting all solutions."""
    formation, energy = FinalProblemSolver.get_complete_solution_set()
    
    print(f"\n   Complete solution set:")
    print(f"   - Formation: {len(formation)} solutions")
    print(f"   - Energy: {len(energy)} solutions")
    print(f"   - Total: {len(formation) + len(energy)} solutions")
    
    assert len(formation) > 0
    assert len(energy) > 0


def test_formation_solutions_have_mechanisms():
    """Test that formation solutions have detailed mechanisms."""
    solutions = FinalProblemSolver.solve_formation_problem()
    
    for sol in solutions:
        assert len(sol.mechanism) > 100  # Detailed description
        assert len(sol.required_conditions) > 0
        assert len(sol.critical_parameters) > 0


def test_energy_solutions_have_details():
    """Test that energy solutions have all required details."""
    solutions = FinalProblemSolver.solve_energy_source_problem()
    
    for sol in solutions:
        assert len(sol.mechanism) > 100
        assert len(sol.advantages) > 0
        assert len(sol.challenges) > 0
        assert sol.estimated_power_output > 0


def test_formation_probabilities_realistic():
    """Test that success probabilities are realistic."""
    solutions = FinalProblemSolver.solve_formation_problem()
    
    for sol in solutions:
        # All should have non-zero but <100% probability
        assert 0 < sol.success_probability < 1
        print(f"   {sol.name}: {sol.success_probability:.0%} success probability")


def test_energy_plausibility_varies():
    """Test that different solutions have different plausibility."""
    solutions = FinalProblemSolver.solve_energy_source_problem()
    
    plausibilities = [s.physics_plausibility for s in solutions]
    
    # Should have variety
    assert max(plausibilities) > min(plausibilities)
    
    print(f"\n   Plausibility range: {min(plausibilities):.0%} to {max(plausibilities):.0%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
