"""
Christoffel Symbols Array Backend

Numerical 4D Christoffel symbol implementation:
Γ^λ_μν = ½ g^λσ (∂_μ g_νσ + ∂_ν g_μσ - ∂_σ g_μν)
"""

import numpy as np
from typing import Tuple
from .metric_array import MetricArray


def compute_christoffel(
    metric: MetricArray,
    dg_dx: np.ndarray,
    coordinates: Tuple[int, int, int, int] = (0, 1, 2, 3)
) -> np.ndarray:
    """
    Compute Christoffel symbols Γ^λ_μν from metric and its derivatives.
    
    Args:
        metric: MetricArray with g_μν
        dg_dx: Partial derivatives ∂_λ g_μν, shape (4, 4, 4)
               dg_dx[λ, μ, ν] = ∂_λ g_μν
        coordinates: Which coordinates to use (t, r, θ, φ)
    
    Returns:
        Gamma[λ, μ, ν] = Γ^λ_μν, shape (4, 4, 4)
    """
    g_inv = metric.inverse()
    
    # Christoffel: Γ^λ_μν = ½ g^λσ (∂_μ g_νσ + ∂_ν g_μσ - ∂_σ g_μν)
    gamma = np.zeros((4, 4, 4))
    
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                for sigma in range(4):
                    gamma[lam, mu, nu] += 0.5 * g_inv[lam, sigma] * (
                        dg_dx[mu, nu, sigma] +
                        dg_dx[nu, mu, sigma] -
                        dg_dx[sigma, mu, nu]
                    )
    
    # Symmetry in lower indices: Γ^λ_μν = Γ^λ_νμ
    for lam in range(4):
        for mu in range(4):
            for nu in range(mu+1, 4):
                avg = 0.5 * (gamma[lam, mu, nu] + gamma[lam, nu, mu])
                gamma[lam, mu, nu] = avg
                gamma[lam, nu, mu] = avg
    
    return gamma


def christoffel_from_finite_diff(
    metric_func,
    point: Tuple[float, float, float, float],
    h: float = 1e-5
) -> np.ndarray:
    """
    Compute Christoffel symbols using finite differences.
    
    Args:
        metric_func: Function that returns MetricArray at (t, r, θ, φ)
        point: (t, r, θ, φ) where to compute Christoffels
        h: Step size for finite differences
    
    Returns:
        Gamma[λ, μ, ν] = Γ^λ_μν
    """
    t, r, theta, phi = point
    
    # Compute metric derivatives by finite differences
    # dg_dx[λ, μ, ν] = ∂_λ g_μν
    dg_dx = np.zeros((4, 4, 4))
    
    coords = [t, r, theta, phi]
    
    for lam in range(4):
        # Forward and backward points
        coords_plus = coords.copy()
        coords_minus = coords.copy()
        coords_plus[lam] += h
        coords_minus[lam] -= h
        
        g_plus = metric_func(*coords_plus).components
        g_minus = metric_func(*coords_minus).components
        
        # Central difference: ∂g/∂x^λ ≈ (g(x+h) - g(x-h)) / 2h
        dg_dx[lam] = (g_plus - g_minus) / (2 * h)
    
    # Metric at point
    metric = metric_func(*coords)
    
    return compute_christoffel(metric, dg_dx)


def check_christoffel_symmetry(gamma: np.ndarray) -> bool:
    """
    Verify Γ^λ_μν = Γ^λ_νμ (torsion-free).
    
    Args:
        gamma: Christoffel symbols, shape (4, 4, 4)
    
    Returns:
        True if symmetry is satisfied
    """
    for lam in range(4):
        for mu in range(4):
            for nu in range(4):
                if abs(gamma[lam, mu, nu] - gamma[lam, nu, mu]) > 1e-10:
                    return False
    return True


if __name__ == "__main__":
    from .metric_array import minkowski_metric
    
    print("=" * 60)
    print("Christoffel Array Backend Test")
    print("=" * 60)
    
    # Test 1: Minkowski Christoffels should be ~0
    mink = minkowski_metric()
    
    # For Minkowski, derivatives are zero, so Christoffels are zero
    dg_dx = np.zeros((4, 4, 4))
    gamma_mink = compute_christoffel(mink, dg_dx)
    
    print("\n1. Minkowski Christoffels (should be all ~0):")
    print(f"   Γ^t_tr = {gamma_mink[0, 0, 1]:.2e}")
    print(f"   Γ^r_tt = {gamma_mink[1, 0, 0]:.2e}")
    print(f"   Max |Γ| = {np.max(np.abs(gamma_mink)):.2e}")
    
    # Test symmetry
    print(f"\n2. Symmetry check (Γ^λ_μν = Γ^λ_νμ):")
    print(f"   Symmetric: {check_christoffel_symmetry(gamma_mink)}")
    
    print("\n" + "=" * 60)
    print("Christoffel array backend test complete")
    print("=" * 60)
