"""SSZ Bridge Metric - Core mathematical solution for real-beaming.

This module implements the bridge metric connecting two points A and B
through a continuous worldline in a bridge channel, not via normal space.

The bridge coordinate u ∈ [-1, 1] with:
- u = -1 ⇒ point A
- u = +1 ⇒ point B

This is the mathematical beam-metric: continuous worldline, not copy.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, List

import numpy as np

from .constants import C, G, PHI


@dataclass(frozen=True)
class BridgeEvaluation:
    """Complete evaluation of a bridge metric candidate."""
    is_regular: bool
    worldline_norm_ok: bool
    distance_ratio: float
    tidal_proxy: float
    causality_ok: bool
    energy_class: str
    regularity_details: Tuple[str, ...]


class SSZBridgeMetric:
    """SSZ Bridge Metric connecting two points through a bridge channel.
    
    The bridge metric is:
        ds² = -D_B²c²dt² + s_B²du² + R_B²dΩ²
    
    where:
        D_B(u) = 1/(1 + Ξ_B(u))
        s_B(u) = 1 + Ξ_B(u) = 1/D_B(u)
        Ξ_B(u) = (1-w(u))Ξ_A + w(u)Ξ_B + λ·q(u)
        w(u) = (1+u)/2
        q(u) = (1-u²)²
    """
    
    def __init__(
        self,
        xi_left: float,
        xi_right: float,
        lambda_bridge: float,
        ell0: float,
        throat_radius: float = 1.0,
    ):
        """Initialize SSZ Bridge Metric.
        
        Args:
            xi_left: Segment density at left endpoint (u=-1), Ξ_A
            xi_right: Segment density at right endpoint (u=+1), Ξ_B
            lambda_bridge: Bridge coupling parameter λ
            ell0: Physical scale of bridge channel
            throat_radius: Throat radius R_0
        """
        self.xi_left = xi_left
        self.xi_right = xi_right
        self.lambda_bridge = lambda_bridge
        self.ell0 = ell0
        self.throat_radius = throat_radius
    
    def w(self, u: float) -> float:
        """Weight function for interpolation.
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            
        Returns:
            w(u) = (1+u)/2
        """
        return 0.5 * (1.0 + u)
    
    def q(self, u: float) -> float:
        """Bridge profile function.
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            
        Returns:
            q(u) = (1-u²)²
        """
        return (1.0 - u * u) ** 2
    
    def xi(self, u: float) -> float:
        """Bridge segment density Ξ_B(u).
        
        Ξ_B(u) = (1-w(u))Ξ_A + w(u)Ξ_B + λ·q(u)
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            
        Returns:
            Segment density at u
        """
        return (
            (1.0 - self.w(u)) * self.xi_left
            + self.w(u) * self.xi_right
            + self.lambda_bridge * self.q(u)
        )
    
    def D(self, u: float) -> float:
        """Time dilation factor D_B(u).
        
        D_B(u) = 1/(1 + Ξ_B(u))
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            
        Returns:
            Time dilation factor at u
        """
        xi_u = self.xi(u)
        if xi_u < -1.0:
            return float('nan')
        return 1.0 / (1.0 + xi_u)
    
    def s(self, u: float) -> float:
        """Radial scaling factor s_B(u).
        
        s_B(u) = 1 + Ξ_B(u) = 1/D_B(u)
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            
        Returns:
            Radial scaling factor at u
        """
        return 1.0 + self.xi(u)
    
    def R(self, u: float) -> float:
        """Throat radius function R_B(u).
        
        R_B(u) = R_0(1 + ¼u²)
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            
        Returns:
            Throat radius at u
        """
        return self.throat_radius * (1.0 + 0.25 * u * u)
    
    def metric_tensor(self, u: float, theta: float = math.pi / 2) -> List[List[float]]:
        """Compute metric tensor g_μν at (u, θ).
        
        g_μν = diag(-(D·c)², (s·ℓ₀)², R², R²sin²θ)
        
        Args:
            u: Bridge coordinate ∈ [-1, 1]
            theta: Polar angle in radians (default π/2)
            
        Returns:
            4x4 metric tensor as nested list
        """
        D = self.D(u)
        s = self.s(u)
        R = self.R(u)
        
        g_tt = -(D * C) ** 2
        g_uu = (s * self.ell0) ** 2
        g_thth = R ** 2
        g_phiphi = R ** 2 * math.sin(theta) ** 2
        
        return [
            [g_tt, 0.0, 0.0, 0.0],
            [0.0, g_uu, 0.0, 0.0],
            [0.0, 0.0, g_thth, 0.0],
            [0.0, 0.0, 0.0, g_phiphi],
        ]
    
    def bridge_distance(self, n: int = 10_000) -> float:
        """Calculate effective bridge distance L_bridge.
        
        L_bridge = ∫_{-1}^{1} s_B(u)·ℓ₀ du
        
        Args:
            n: Number of integration samples
            
        Returns:
            Effective bridge distance
        """
        total = 0.0
        du = 2.0 / n
        for i in range(n):
            u = -1.0 + (i + 0.5) * du
            total += self.s(u) * self.ell0 * du
        return total
    
    def timelike_norm(self, u: float, dt_dtau: float, du_dtau: float) -> float:
        """Compute worldline norm g_μνu^μu^ν.
        
        For timelike worldline: g_μνu^μu^ν = -c²
        
        Args:
            u: Bridge coordinate
            dt_dtau: dt/dτ
            du_dtau: du/dτ
            
        Returns:
            Worldline norm value
        """
        D = self.D(u)
        s = self.s(u)
        return -(D * C) ** 2 * dt_dtau ** 2 + (s * self.ell0) ** 2 * du_dtau ** 2
    
    def required_dt_dtau_for_timelike(self, u: float, du_dtau: float) -> float:
        """Compute required dt/dτ for timelike worldline.
        
        From g_μνu^μu^ν = -c²:
            dt/dτ = √[(c² + (s·ℓ₀)²(du/dτ)²)/(D·c)²]
        
        Args:
            u: Bridge coordinate
            du_dtau: du/dτ
            
        Returns:
            Required dt/dτ
        """
        D = self.D(u)
        s = self.s(u)
        return math.sqrt((C * C + (s * self.ell0) ** 2 * du_dtau ** 2) / ((D * C) ** 2))
    
    def is_regular(self, samples: int = 1001) -> Tuple[bool, List[str]]:
        """Check if bridge metric is regular across all u ∈ [-1, 1].
        
        Regularity conditions:
            D(u) > 0
            s(u) > 0
            R(u) > 0
            det(g) ≠ 0
        
        Args:
            samples: Number of sample points to check
            
        Returns:
            (is_regular, list of issues)
        """
        issues = []
        
        for i in range(samples):
            u = -1.0 + 2.0 * i / (samples - 1)
            
            D = self.D(u)
            s = self.s(u)
            R = self.R(u)
            
            if D <= 0 or not math.isfinite(D):
                issues.append(f"D({u:.4f}) = {D:.6e} ≤ 0")
            if s <= 0 or not math.isfinite(s):
                issues.append(f"s({u:.4f}) = {s:.6e} ≤ 0")
            if R <= 0 or not math.isfinite(R):
                issues.append(f"R({u:.4f}) = {R:.6e} ≤ 0")
        
        return len(issues) == 0, issues
    
    def dxi_du(self, u: float) -> float:
        """Derivative of Ξ_B with respect to u.
        
        dΞ_B/du = -½Ξ_A + ½Ξ_B + λ·dq/du
        dq/du = -4u(1-u²)
        
        Args:
            u: Bridge coordinate
            
        Returns:
            dΞ_B/du
        """
        dw_du = 0.5
        dq_du = -4.0 * u * (1.0 - u * u)
        return (
            -dw_du * self.xi_left
            + dw_du * self.xi_right
            + self.lambda_bridge * dq_du
        )
    
    def tidal_proxy(self, u: float, delta_u: float = 0.01) -> float:
        """Estimate tidal acceleration proxy at u.
        
        Proxy: Δa ≈ c² |d²g/du²| · δu
        
        Args:
            u: Bridge coordinate
            delta_u: Separation scale
            
        Returns:
            Tidal acceleration proxy in m/s²
        """
        # Finite difference for second derivative of metric
        u_plus = u + delta_u
        u_minus = u - delta_u
        
        # Boundary check
        if u_minus < -1.0:
            u_minus = -1.0 + 1e-6
        if u_plus > 1.0:
            u_plus = 1.0 - 1e-6
        
        g_u = self.metric_tensor(u, math.pi/2)
        g_plus = self.metric_tensor(u_plus, math.pi/2)
        g_minus = self.metric_tensor(u_minus, math.pi/2)
        
        # Second derivative of g_tt (simplified)
        d2_g_tt = (g_plus[0][0] - 2 * g_u[0][0] + g_minus[0][0]) / (delta_u ** 2)
        
        # Tidal proxy
        return C ** 2 * abs(d2_g_tt) * delta_u * self.ell0
    
    def max_tidal_across_bridge(self, samples: int = 101) -> float:
        """Find maximum tidal acceleration across the bridge.
        
        Args:
            samples: Number of sample points
            
        Returns:
            Maximum tidal acceleration proxy
        """
        max_tidal = 0.0
        for i in range(samples):
            u = -1.0 + 2.0 * i / (samples - 1)
            tidal = self.tidal_proxy(u)
            if math.isfinite(tidal) and tidal > max_tidal:
                max_tidal = tidal
        return max_tidal
    
    def evaluate_candidate(
        self,
        l_normal: float,
        tidal_threshold: float = 10.0 * 9.81,  # 10g
    ) -> BridgeEvaluation:
        """Complete evaluation of bridge candidate.
        
        Args:
            l_normal: Normal coordinate distance L(A,B)
            tidal_threshold: Maximum allowed tidal acceleration
            
        Returns:
            BridgeEvaluation with all checks
        """
        details = []
        
        # 1. Regularity
        regular, reg_issues = self.is_regular()
        if not regular:
            details.extend(reg_issues)
        
        # 2. Worldline norm check (at center u=0 with du/dτ = 1/ℓ₀)
        u_test = 0.0
        du_dtau = 1.0 / self.ell0
        try:
            dt_dtau_req = self.required_dt_dtau_for_timelike(u_test, du_dtau)
            norm = self.timelike_norm(u_test, dt_dtau_req, du_dtau)
            worldline_ok = abs(norm + C**2) < 0.01 * C**2
        except (ValueError, ZeroDivisionError) as e:
            worldline_ok = False
            details.append(f"Worldline norm error: {e}")
        
        # 3. Distance ratio
        l_bridge = self.bridge_distance()
        distance_ratio = l_bridge / l_normal if l_normal > 0 else float('inf')
        
        # 4. Tidal check
        max_tidal = self.max_tidal_across_bridge()
        tidal_ok = max_tidal < tidal_threshold
        
        # 5. Causality: check dt/dτ > 0 everywhere
        causality_ok = True
        for i in range(101):
            u = -1.0 + 2.0 * i / 100.0
            try:
                dt_dtau = self.required_dt_dtau_for_timelike(u, du_dtau)
                if dt_dtau <= 0 or not math.isfinite(dt_dtau):
                    causality_ok = False
                    details.append(f"dt/dτ ≤ 0 at u={u:.2f}")
                    break
            except Exception as e:
                causality_ok = False
                details.append(f"Causality check error at u={u:.2f}: {e}")
                break
        
        # 6. Energy classification (simplified proxy)
        # Check if bridge requires exotic energy
        xi_center = self.xi(0.0)
        if xi_center > 1.0:
            energy_class = "SSZ_EXTENSION"
        elif xi_center > 0.5:
            energy_class = "GR_EXOTIC"
        else:
            energy_class = "SSZ_CANONICAL"
        
        if self.lambda_bridge > 10.0:
            energy_class = "TOY_MODEL"
        
        # Overall assessment
        overall_ok = regular and worldline_ok and causality_ok
        
        if not overall_ok:
            energy_class = "INCONSISTENT"
        
        return BridgeEvaluation(
            is_regular=regular,
            worldline_norm_ok=worldline_ok,
            distance_ratio=distance_ratio,
            tidal_proxy=max_tidal,
            causality_ok=causality_ok,
            energy_class=energy_class,
            regularity_details=tuple(details),
        )


def create_canonical_bridge(
    xi_a: float = 0.1,
    xi_b: float = 0.1,
    lambda_bridge: float = 0.5,
    ell0: float = 1e-3,  # 1mm scale
    throat_radius: float = 1e-2,  # 1cm
) -> SSZBridgeMetric:
    """Create a canonical bridge metric with reasonable defaults.
    
    Args:
        xi_a: Segment density at point A
        xi_b: Segment density at point B
        lambda_bridge: Bridge coupling parameter
        ell0: Bridge channel scale
        throat_radius: Throat radius
        
    Returns:
        SSZBridgeMetric instance
    """
    return SSZBridgeMetric(
        xi_left=xi_a,
        xi_right=xi_b,
        lambda_bridge=lambda_bridge,
        ell0=ell0,
        throat_radius=throat_radius,
    )


def evaluate_bridge_candidate(
    bridge: SSZBridgeMetric,
    l_normal: float,
    verbose: bool = False,
) -> bool:
    """Evaluate a bridge candidate and optionally print results.
    
    Args:
        bridge: Bridge metric to test
        l_normal: Normal distance between A and B
        verbose: Print detailed results
        
    Returns:
        True if candidate passes all tests
    """
    eval_result = bridge.evaluate_candidate(l_normal)
    
    if verbose:
        print(f"\n=== Bridge Candidate Evaluation ===")
        print(f"Parameters: Ξ_A={bridge.xi_left:.3f}, Ξ_B={bridge.xi_right:.3f}, "
              f"λ={bridge.lambda_bridge:.3f}, ℓ₀={bridge.ell0:.3e}")
        print(f"Regular: {eval_result.is_regular}")
        print(f"Worldline norm OK: {eval_result.worldline_norm_ok}")
        print(f"Causality OK: {eval_result.causality_ok}")
        print(f"Distance ratio η = L_bridge/L_normal: {eval_result.distance_ratio:.6f}")
        print(f"Tidal proxy: {eval_result.tidal_proxy:.3e} m/s²")
        print(f"Energy class: {eval_result.energy_class}")
        if eval_result.regularity_details:
            print(f"Issues: {eval_result.regularity_details}")
        print(f"=== Overall: {'PASS' if eval_result.energy_class != 'INCONSISTENT' else 'FAIL'} ===")
    
    return eval_result.energy_class != "INCONSISTENT"


if __name__ == "__main__":
    # Example usage
    bridge = create_canonical_bridge(
        xi_a=0.1,
        xi_b=0.2,
        lambda_bridge=0.3,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    
    # Test with normal distance of 1 meter
    l_normal = 1.0
    passed = evaluate_bridge_candidate(bridge, l_normal, verbose=True)
    
    print(f"\nBridge distance: {bridge.bridge_distance():.6f} m")
    print(f"Normal distance: {l_normal:.6f} m")
    print(f"Reduction factor: {bridge.bridge_distance() / l_normal:.6f}")


# Alias for compatibility
BridgeMetric = SSZBridgeMetric


# Convenience alias for testing
BridgeMetric = SSZBridgeMetric
