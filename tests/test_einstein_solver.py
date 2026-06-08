"""Tests for einstein_solver module."""
import sys
sys.path.insert(0, 'src')

import pytest
import numpy as np

from beam_ssz.einstein_solver import (
    BridgeEinsteinSolver,
    estimate_energy_requirements,
    EinsteinSolution,
)
from beam_ssz.bridge_metric import create_canonical_bridge, SSZBridgeMetric


def test_solver_instantiation():
    """Test that solver can be instantiated."""
    solver = BridgeEinsteinSolver()
    assert solver is not None


def test_compute_christoffel_2d():
    """Test 2D Christoffel symbol computation."""
    solver = BridgeEinsteinSolver()
    
    g_tt = -1.0
    g_uu = 1.0
    dg_tt_du = 0.1
    dg_uu_du = 0.2
    
    gamma = solver.compute_christoffel_2d(g_tt, g_uu, dg_tt_du, dg_uu_du)
    
    assert 't_tu' in gamma
    assert 'u_tt' in gamma
    assert 'u_uu' in gamma
    
    # Check symmetries
    assert gamma['t_tu'] == gamma['t_ut']


def test_compute_ricci_2d():
    """Test 2D Ricci tensor computation."""
    solver = BridgeEinsteinSolver()
    
    g_tt = -1.0
    g_uu = 1.0
    dg_tt_du = 0.0
    dg_uu_du = 0.0
    d2g_tt_du2 = 0.1
    d2g_uu_du2 = 0.2
    
    R_tt, R_uu = solver.compute_ricci_2d(
        g_tt, g_uu, dg_tt_du, dg_uu_du, d2g_tt_du2, d2g_uu_du2
    )
    
    assert np.isfinite(R_tt)
    assert np.isfinite(R_uu)


def test_solve_for_bridge():
    """Test solving Einstein equations for bridge."""
    bridge = create_canonical_bridge()
    
    solver = BridgeEinsteinSolver()
    solution = solver.solve_for_bridge(bridge, n_points=51)
    
    assert solution is not None
    assert isinstance(solution, EinsteinSolution)
    assert len(solution.u_points) == 51


def test_solution_structure():
    """Test that solution has correct structure."""
    bridge = create_canonical_bridge()
    solver = BridgeEinsteinSolver()
    solution = solver.solve_for_bridge(bridge)
    
    assert hasattr(solution, 'u_points')
    assert hasattr(solution, 'G_tt')
    assert hasattr(solution, 'T_tt')
    assert hasattr(solution, 'energy_density')
    assert hasattr(solution, 'nec_satisfied')
    assert hasattr(solution, 'max_energy_density')


def test_energy_conditions_check():
    """Test energy condition checking."""
    bridge = create_canonical_bridge()
    solver = BridgeEinsteinSolver()
    solution = solver.solve_for_bridge(bridge)
    
    analysis = solver.analyze_energy_conditions(solution)
    
    assert 'nec' in analysis
    assert 'sec' in analysis
    assert 'wec' in analysis
    assert 'classification' in analysis


def test_estimate_energy_requirements():
    """Test energy requirement estimation."""
    bridge = create_canonical_bridge()
    
    results = estimate_energy_requirements(bridge, verbose=False)
    
    assert results['status'] == 'SUCCESS'
    assert 'solution' in results
    assert 'analysis' in results
    assert 'classification' in results


def test_weak_bridge_energy():
    """Test energy analysis for weak bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    
    results = estimate_energy_requirements(bridge, verbose=False)
    
    assert results['status'] == 'SUCCESS'
    # Weak bridge should have smaller energy requirements
    assert np.isfinite(results['max_energy_density'])


def test_strong_bridge_energy():
    """Test energy analysis for strong bridge."""
    bridge = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=2.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    
    results = estimate_energy_requirements(bridge, verbose=False)
    
    assert results['status'] == 'SUCCESS'
    # Strong bridge may have exotic energy
    assert np.isfinite(results['max_energy_density'])


def test_numerical_stability():
    """Test numerical stability with different resolutions."""
    bridge = create_canonical_bridge()
    solver = BridgeEinsteinSolver()
    
    # Different resolutions should give similar results
    sol_50 = solver.solve_for_bridge(bridge, n_points=50)
    sol_100 = solver.solve_for_bridge(bridge, n_points=100)
    
    assert sol_50 is not None
    assert sol_100 is not None
    
    # Energy densities should be in same order of magnitude
    ratio = sol_50.max_energy_density / sol_100.max_energy_density
    assert 0.1 < ratio < 10.0  # Within factor of 10


def test_solution_arrays_finite():
    """Test that all solution arrays are finite."""
    bridge = create_canonical_bridge()
    solver = BridgeEinsteinSolver()
    solution = solver.solve_for_bridge(bridge)
    
    assert np.all(np.isfinite(solution.G_tt))
    assert np.all(np.isfinite(solution.G_uu))
    assert np.all(np.isfinite(solution.T_tt))
    assert np.all(np.isfinite(solution.T_uu))
    assert np.all(np.isfinite(solution.energy_density))


def test_energy_density_range():
    """Test that energy density has reasonable range."""
    bridge = create_canonical_bridge()
    solver = BridgeEinsteinSolver()
    solution = solver.solve_for_bridge(bridge)
    
    # Energy density should be finite
    assert np.isfinite(solution.max_energy_density)
    assert np.isfinite(solution.min_energy_density)
    
    # Max should be >= min
    assert solution.max_energy_density >= solution.min_energy_density


def test_classification_consistency():
    """Test that classification is consistent with NEC."""
    bridge = create_canonical_bridge()
    results = estimate_energy_requirements(bridge, verbose=False)
    
    classification = results['classification']
    nec_satisfied = results['nec_satisfied']
    
    # If NEC satisfied, should be SSZ_CANONICAL
    if nec_satisfied:
        assert classification == 'SSZ_CANONICAL'
    else:
        assert classification == 'GR_EXOTIC'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
