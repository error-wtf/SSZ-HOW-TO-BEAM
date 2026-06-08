"""
Riemann Tensor Array Backend

Numerical 4D Riemann tensor implementation:
R^ρ_σμν = ∂_μ Γ^ρ_νσ - ∂_ν Γ^ρ_μσ + Γ^ρ_μλ Γ^λ_νσ - Γ^ρ_νλ Γ^λ_μσ
"""

import numpy as np
from typing import Tuple


def compute_riemann_from_christoffel(
    gamma: np.ndarray,
    dgamma_dx: np.ndarray
) -> np.ndarray:
    """
    Compute Riemann tensor from Christoffels and their derivatives.
    
    Args:
        gamma: Christoffel symbols Γ^λ_μν, shape (4, 4, 4)
        dgamma_dx: Derivatives ∂_σ Γ^λ_μν, shape (4, 4, 4, 4)
                   dgamma_dx[σ, λ, μ, ν] = ∂_σ Γ^λ_μν
    
    Returns:
        Riemann[ρ, σ, μ, ν] = R^ρ_σμν
    """
    riemann = np.zeros((4, 4, 4, 4))
    
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    # R^ρ_σμν = ∂_μ Γ^ρ_νσ - ∂_ν Γ^ρ_μσ 
                    #           + Γ^ρ_μλ Γ^λ_νσ - Γ^ρ_νλ Γ^λ_μσ
                    
                    term1 = dgamma_dx[mu, rho, nu, sigma]
                    term2 = dgamma_dx[nu, rho, mu, sigma]
                    
                    term3 = 0.0
                    term4 = 0.0
                    for lam in range(4):
                        term3 += gamma[rho, mu, lam] * gamma[lam, nu, sigma]
                        term4 += gamma[rho, nu, lam] * gamma[lam, mu, sigma]
                    
                    riemann[rho, sigma, mu, nu] = term1 - term2 + term3 - term4
    
    return riemann


def lower_riemann_indices(
    riemann_upper: np.ndarray,
    metric: np.ndarray
) -> np.ndarray:
    """
    Lower first index: R_ρσμν = g_ρλ R^λ_σμν
    
    Args:
        riemann_upper: R^ρ_σμν, shape (4, 4, 4, 4)
        metric: g_μν, shape (4, 4)
    
    Returns:
        Riemann[ρ, σ, μ, ν] = R_ρσμν (all lower)
    """
    # R_ρσμν = g_ρλ R^λ_σμν
    return np.einsum('ab,bcdc->acdc', metric, riemann_upper)


def check_riemann_symmetries(riemann: np.ndarray, tol: float = 1e-10) -> dict:
    """
    Verify Riemann tensor symmetries:
    1. R_ρσμν = -R_σμνρ (antisymmetric in first/last pair)
    2. R_ρσμν = R_μνρσ (pair symmetry)
    3. R_ρσμν + R_ρμνσ + R_ρνσμ = 0 (first Bianchi)
    
    Args:
        riemann: R_ρσμν with all lower indices, shape (4, 4, 4, 4)
        tol: Tolerance for equality checks
    
    Returns:
        Dict of symmetry names and whether they hold
    """
    results = {}
    
    # 1. Antisymmetry: R_ρσμν = -R_σμνρ
    antisym = True
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    if abs(riemann[rho, sigma, mu, nu] + riemann[sigma, rho, mu, nu]) > tol:
                        antisym = False
                        break
    results['antisymmetric_first_pair'] = antisym
    
    # 2. Pair symmetry: R_ρσμν = R_μνρσ
    pair_sym = True
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    if abs(riemann[rho, sigma, mu, nu] - riemann[mu, nu, rho, sigma]) > tol:
                        pair_sym = False
                        break
    results['pair_symmetry'] = pair_sym
    
    # 3. First Bianchi: R_ρσμν + R_ρμνσ + R_ρνσμ = 0
    bianchi = True
    for rho in range(4):
        for sigma in range(4):
            for mu in range(4):
                for nu in range(4):
                    cyclic_sum = (
                        riemann[rho, sigma, mu, nu] +
                        riemann[rho, mu, nu, sigma] +
                        riemann[rho, nu, sigma, mu]
                    )
                    if abs(cyclic_sum) > tol:
                        bianchi = False
                        break
    results['first_bianchi'] = bianchi
    
    return results


def check_flatness(riemann: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Check if Riemann tensor vanishes (flat space).
    
    Args:
        riemann: Riemann tensor, shape (4, 4, 4, 4)
        tol: Tolerance for zero check
    
    Returns:
        True if Riemann ≈ 0 (flat)
    """
    return np.max(np.abs(riemann)) < tol


if __name__ == "__main__":
    print("=" * 60)
    print("Riemann Tensor Array Backend Test")
    print("=" * 60)
    
    # Test 1: Zero Christoffels → Zero Riemann
    print("\n1. Flat space test (Γ = 0 → R = 0):")
    gamma = np.zeros((4, 4, 4))
    dgamma = np.zeros((4, 4, 4, 4))
    riemann_flat = compute_riemann_from_christoffel(gamma, dgamma)
    print(f"   Max |R| = {np.max(np.abs(riemann_flat)):.2e}")
    print(f"   Is flat: {check_flatness(riemann_flat)}")
    
    # Test 2: Symmetries on flat Riemann
    print("\n2. Symmetry checks on flat Riemann:")
    syms = check_riemann_symmetries(riemann_flat)
    for name, result in syms.items():
        print(f"   {name}: {result}")
    
    print("\n" + "=" * 60)
    print("Riemann array backend test complete")
    print("=" * 60)
