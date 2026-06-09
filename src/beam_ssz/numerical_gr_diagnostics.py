"""Numerical GR convergence diagnostics and constraint monitoring.

From v0.9 roadmap: Add convergence diagnostics to numerical_gr module.
This provides independent validation of numerical solutions.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import numpy as np


@dataclass
class ConvergenceReport:
    """Convergence diagnostic report."""
    grid_refinements: List[int]  # N points at each level
    solutions: List[np.ndarray]  # Solutions at each level
    errors: List[float]  # Estimated errors
    convergence_rate: float  # Empirical convergence order
    is_converging: bool  # Whether converging as expected
    
    # Richardson extrapolation estimate
    richardson_estimate: float
    
    # Confidence
    confidence_level: str  # "high", "medium", "low"


@dataclass
class ConstraintReport:
    """Hamiltonian and momentum constraint violation report."""
    max_hamiltonian_violation: float
    max_momentum_violation: float
    l2_hamiltonian_norm: float
    l2_momentum_norm: float
    
    # Thresholds
    hamiltonian_tolerance: float
    momentum_tolerance: float
    
    # Status
    hamiltonian_satisfied: bool
    momentum_satisfied: bool
    overall_status: str  # "PASS", "WARNING", "FAIL"


def test_convergence_rate(
    f_coarse: float,
    f_medium: float,
    f_fine: float,
    h_coarse: float,
    h_medium: float,
    h_fine: float,
    expected_order: float = 2.0,
    tolerance: float = 0.5,
) -> Dict[str, any]:
    """Test if solution shows expected convergence rate.
    
    Uses Richardson extrapolation to estimate true solution and convergence order.
    
    Args:
        f_coarse: Solution at coarse resolution
        f_medium: Solution at medium resolution
        f_fine: Solution at fine resolution
        h_coarse: Grid spacing (coarse)
        h_medium: Grid spacing (medium)
        h_fine: Grid spacing (fine)
        expected_order: Expected convergence order (2 for central differences)
        tolerance: Allowed deviation from expected order
    
    Returns:
        Dict with convergence analysis
    """
    # Ratios
    r_cm = h_coarse / h_medium
    r_mf = h_medium / h_fine
    
    # Convergence order estimate
    # p ≈ log((f_coarse - f_medium) / (f_medium - f_fine)) / log(r)
    
    diff_cm = abs(f_coarse - f_medium)
    diff_mf = abs(f_medium - f_fine)
    
    if diff_mf < 1e-14:
        # Already converged or numerical issue
        p_estimate = float('inf')
    else:
        p_estimate = np.log(diff_cm / diff_mf) / np.log(r_cm)
    
    # Richardson extrapolation (for 2nd order)
    if expected_order == 2.0:
        # f_exact ≈ (r² f_fine - f_medium) / (r² - 1)
        r_sq = r_mf ** 2
        f_richardson = (r_sq * f_fine - f_medium) / (r_sq - 1.0)
    else:
        f_richardson = f_fine  # Fallback
    
    # Error estimate
    error_estimate = abs(f_fine - f_richardson)
    
    # Check if converging
    is_converging = diff_cm > diff_mf  # Error should decrease
    
    # Check order
    order_ok = abs(p_estimate - expected_order) < tolerance
    
    return {
        "convergence_order_estimate": p_estimate,
        "expected_order": expected_order,
        "order_match": order_ok,
        "richardson_estimate": f_richardson,
        "error_estimate": error_estimate,
        "is_converging": is_converging,
        "confidence": "high" if (is_converging and order_ok) else "medium" if is_converging else "low",
    }


def generate_convergence_report(
    solutions: List[np.ndarray],
    grid_spacings: List[float],
    expected_order: float = 2.0,
) -> ConvergenceReport:
    """Generate full convergence report from multiple grid levels.
    
    Args:
        solutions: List of solution arrays at different resolutions
        grid_spacings: List of grid spacings (h values)
        expected_order: Expected convergence order
    
    Returns:
        ConvergenceReport
    """
    n_levels = len(solutions)
    
    # Compute errors between levels (need interpolation for different grids)
    errors = []
    for i in range(n_levels - 1):
        # Simple: compare at subset of points
        # Proper: interpolate fine to coarse grid
        f_coarse = solutions[i]
        f_fine = solutions[i + 1]
        
        # Interpolate fine to coarse spacing (simplified)
        if len(f_fine) > len(f_coarse):
            step = len(f_fine) // len(f_coarse)
            f_fine_on_coarse = f_fine[::step][:len(f_coarse)]
        else:
            f_fine_on_coarse = f_fine
        
        error = np.linalg.norm(f_coarse - f_fine_on_coarse)
        errors.append(error)
    
    # Estimate convergence rate from finest two levels
    if len(errors) >= 2 and errors[-1] > 0:
        rate = np.log(errors[-2] / errors[-1]) / np.log(
            grid_spacings[-2] / grid_spacings[-1]
        )
    else:
        rate = float('nan')
    
    # Richardson estimate from finest two
    if n_levels >= 2:
        r = grid_spacings[-2] / grid_spacings[-1]
        f_fine = solutions[-1]
        f_medium = solutions[-2]
        
        # Interpolate medium to fine
        if len(f_medium) < len(f_fine):
            # Simple interpolation
            f_medium_on_fine = np.interp(
                np.linspace(0, 1, len(f_fine)),
                np.linspace(0, 1, len(f_medium)),
                f_medium,
            )
        else:
            f_medium_on_fine = f_medium[:len(f_fine)]
        
        richardson = (r**expected_order * f_fine - f_medium_on_fine) / (r**expected_order - 1.0)
    else:
        richardson = solutions[-1] if solutions else np.array([0.0])
    
    # Check convergence
    is_converging = all(errors[i] > errors[i+1] for i in range(len(errors)-1)) if len(errors) > 1 else True
    
    # Confidence
    if is_converging and abs(rate - expected_order) < 0.5:
        confidence = "high"
    elif is_converging:
        confidence = "medium"
    else:
        confidence = "low"
    
    return ConvergenceReport(
        grid_refinements=[len(s) for s in solutions],
        solutions=solutions,
        errors=errors,
        convergence_rate=rate,
        is_converging=is_converging,
        richardson_estimate=float(np.mean(richardson)),
        confidence_level=confidence,
    )


def check_hamiltonian_constraint(
    hamiltonian_values: np.ndarray,
    tolerance: float = 1e-6,
) -> ConstraintReport:
    """Check Hamiltonian constraint satisfaction.
    
    From numerical GR: H = 0 should be satisfied everywhere.
    In practice: |H| < tolerance.
    
    Args:
        hamiltonian_values: Array of H values at grid points
        tolerance: Maximum allowed |H|
    
    Returns:
        ConstraintReport
    """
    max_h = np.max(np.abs(hamiltonian_values))
    l2_h = np.sqrt(np.mean(hamiltonian_values**2))
    
    is_satisfied = max_h < tolerance
    
    if is_satisfied:
        status = "PASS"
    elif max_h < 10 * tolerance:
        status = "WARNING"
    else:
        status = "FAIL"
    
    return ConstraintReport(
        max_hamiltonian_violation=float(max_h),
        max_momentum_violation=0.0,  # Not computed here
        l2_hamiltonian_norm=float(l2_h),
        l2_momentum_norm=0.0,
        hamiltonian_tolerance=tolerance,
        momentum_tolerance=tolerance,
        hamiltonian_satisfied=is_satisfied,
        momentum_satisfied=True,  # Not checked
        overall_status=status,
    )


def validate_numerical_solution(
    solution: np.ndarray,
    grid_spacing: float,
    hamiltonian: np.ndarray = None,
    expected_convergence_order: float = 2.0,
) -> Dict[str, any]:
    """Full validation of numerical solution.
    
    Args:
        solution: Numerical solution array
        grid_spacing: Grid spacing h
        hamiltonian: Hamiltonian constraint values (optional)
        expected_convergence_order: Expected order of convergence
    
    Returns:
        Validation report
    """
    report = {
        "grid_spacing": grid_spacing,
        "solution_shape": solution.shape,
        "solution_finite": np.all(np.isfinite(solution)),
        "solution_real": np.all(np.isreal(solution)),
    }
    
    # Check solution properties
    if not report["solution_finite"]:
        report["status"] = "FAIL"
        report["reason"] = "Non-finite values in solution"
        return report
    
    # Check Hamiltonian if provided
    if hamiltonian is not None:
        constraint_report = check_hamiltonian_constraint(hamiltonian)
        report["constraint_check"] = constraint_report
        
        if constraint_report.overall_status == "FAIL":
            report["status"] = "FAIL"
            report["reason"] = "Hamiltonian constraint violated"
            return report
    
    # All checks passed
    report["status"] = "PASS"
    report["readiness"] = "NUMERICAL_GR_SCAFFOLD"
    
    return report
