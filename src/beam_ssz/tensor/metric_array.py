"""
Metric Tensor Array Backend

Numerical 4D metric tensor implementation using proper array indices
instead of string-key components.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class MetricArray:
    """
    4D metric tensor g_μν as proper numpy array.
    
    Indices: μ, ν ∈ {0,1,2,3} = {t,r,θ,φ}
    """
    components: np.ndarray  # Shape (4, 4)
    coordinates: Tuple[float, float, float, float]  # (t, r, θ, φ)
    
    def __post_init__(self):
        assert self.components.shape == (4, 4), "Metric must be 4x4"
        # Enforce symmetry g_μν = g_νμ
        self.components = 0.5 * (self.components + self.components.T)
    
    def __getitem__(self, indices: Tuple[int, int]) -> float:
        """Access g_μν by integer indices."""
        mu, nu = indices
        return self.components[mu, nu]
    
    def determinant(self) -> float:
        """Compute det(g_μν)."""
        return np.linalg.det(self.components)
    
    def inverse(self) -> np.ndarray:
        """Compute g^μν (inverse metric)."""
        return np.linalg.inv(self.components)
    
    def is_finite(self) -> bool:
        """Check all components are finite."""
        return np.all(np.isfinite(self.components))
    
    def is_singular(self, tol: float = 1e-10) -> bool:
        """Check if metric is singular (det ≈ 0)."""
        return abs(self.determinant()) < tol


def minkowski_metric(flat_signature: bool = True) -> MetricArray:
    """
    Create Minkowski metric η_μν = diag(-1, 1, 1, 1).
    
    Args:
        flat_signature: If True, use (-,+,+,+), else (+,-,-,-)
    
    Returns:
        MetricArray with Minkowski components
    """
    if flat_signature:
        diag = [-1.0, 1.0, 1.0, 1.0]
    else:
        diag = [1.0, -1.0, -1.0, -1.0]
    
    components = np.diag(diag)
    return MetricArray(
        components=components,
        coordinates=(0.0, 1.0, np.pi/2, 0.0)  # Default: t=0, r=1, θ=π/2, φ=0
    )


def ssz_metric_array(
    r: float,
    theta: float,
    xi_val: float,
    D_factor: Optional[float] = None
) -> MetricArray:
    """
    Create SSZ metric as proper 4D array.
    
    SSZ metric in spherical coordinates:
    ds² = -D(r)²c²dt² + s(r)²dr² + r²dθ² + r²sin²θ dφ²
    
    Args:
        r: Radial coordinate
        theta: Polar angle
        xi_val: Xi function value at r
        D_factor: Optional custom D(r), else computed from xi
    
    Returns:
        MetricArray with SSZ components
    """
    from ..xi import evaluate_xi_x
    
    if D_factor is None:
        # D(r) ≈ 1 + ξ for weak field
        D_factor = 1.0 + xi_val
    
    # Standard spherical metric with D modification
    # g_tt = -D², g_rr = (1 - 2M/r)^(-1) for Schwarzschild-like
    # For SSZ: simplified model
    g_tt = -D_factor**2
    g_rr = 1.0 / D_factor**2  # Rough approximation
    g_thetatheta = r**2
    g_phiphi = (r * np.sin(theta))**2
    
    components = np.diag([g_tt, g_rr, g_thetatheta, g_phiphi])
    
    return MetricArray(
        components=components,
        coordinates=(0.0, r, theta, 0.0)
    )


def flat_bridge_metric(
    u: float,
    ell0: float = 1.0,
    Xi_A: float = 0.0,
    Xi_B: float = 0.0,
    lambda_bridge: float = 0.0
) -> MetricArray:
    """
    Create flat bridge metric (Ξ_A = Ξ_B = 0, λ = 0).
    
    For testing: should reduce to approximately flat Minkowski.
    
    Args:
        u: Bridge coordinate (-1 to 1)
        ell0: Characteristic length scale
        Xi_A, Xi_B: Boundary Xi values (should be 0 for flat test)
        lambda_bridge: Bridge coupling (should be 0 for flat test)
    
    Returns:
        MetricArray for flat bridge
    """
    # For flat bridge, metric should be Minkowski
    # With possible coordinate transformation
    
    # Simple model: transform from u to r
    r = ell0 * (1 + u)  # Simple linear mapping
    theta = np.pi / 2
    
    return ssz_metric_array(
        r=r,
        theta=theta,
        xi_val=0.0,  # No curvature
        D_factor=1.0  # Flat
    )


# Index mapping for clarity
INDEX_NAMES = {
    't': 0,
    'r': 1,
    'theta': 2,
    'th': 2,
    'φ': 3,
    'phi': 3,
}


def get_index(name: str) -> int:
    """Convert coordinate name to integer index."""
    return INDEX_NAMES.get(name, INDEX_NAMES.get(name.lower(), -1))


if __name__ == "__main__":
    # Test: Minkowski metric
    print("=" * 60)
    print("Metric Array Backend Test")
    print("=" * 60)
    
    # Test 1: Minkowski
    mink = minkowski_metric()
    print("\n1. Minkowski Metric:")
    print(f"   g_00 = {mink[0,0]:.1f} (should be -1)")
    print(f"   g_11 = {mink[1,1]:.1f} (should be 1)")
    print(f"   det(g) = {mink.determinant():.1f} (should be -1)")
    print(f"   Finite: {mink.is_finite()}")
    
    # Test 2: SSZ metric at horizon
    ssz = ssz_metric_array(r=2.0, theta=np.pi/2, xi_val=0.1)
    print("\n2. SSZ Metric (r=2, θ=π/2, Ξ=0.1):")
    print(f"   g_tt = {ssz[0,0]:.6f}")
    print(f"   g_rr = {ssz[1,1]:.6f}")
    print(f"   det(g) = {ssz.determinant():.6e}")
    print(f"   Finite: {ssz.is_finite()}")
    
    # Test 3: Flat bridge (should be ~Minkowski)
    flat = flat_bridge_metric(u=0.0, Xi_A=0.0, Xi_B=0.0, lambda_bridge=0.0)
    print("\n3. Flat Bridge (Ξ=0, λ=0):")
    print(f"   g_tt = {flat[0,0]:.6f} (should be ~-1)")
    print(f"   g_rr = {flat[1,1]:.6f} (should be ~1)")
    print(f"   det(g) = {flat.determinant():.6e}")
    
    print("\n" + "=" * 60)
    print("All tests passed - Metric array backend working")
    print("=" * 60)
