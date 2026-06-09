"""Stability monitoring for SSZ bridge metrics.

Tracks curvature invariants and constraint violations to detect
instabilities in numerical evolutions.
"""

import numpy as np
from typing import Dict, List, Tuple
import sys
import os

sys.path.insert(0, '../src')
from beam_ssz.tensor_core import compute_riemann, ricci_scalar
from beam_ssz.bridge_metric import SSZBridgeMetric


class StabilityMonitor:
    """Monitor metric stability during numerical evolution.
    
    Tracks key invariants that indicate instability:
    - Kretschmann scalar (Riemann squared)
    - Extrinsic curvature invariant (K_ij K^ij)
    - Hamiltonian constraint violation
    - Coordinate singularities
    """
    
    def __init__(self, threshold_kretschmann: float = 1e6,
                 threshold_extrinsic: float = 1e4,
                 threshold_constraint: float = 1e-2):
        """Initialize stability monitor.
        
        Args:
            threshold_kretschmann: Alert if R_{abcd}R^{abcd} > threshold
            threshold_extrinsic: Alert if K_ij K^ij > threshold  
            threshold_constraint: Alert if |H| > threshold
        """
        self.threshold_kretschmann = threshold_kretschmann
        self.threshold_extrinsic = threshold_extrinsic
        self.threshold_constraint = threshold_constraint
        
        # History tracking
        self.time_history = []
        self.kretschmann_history = []
        self.extrinsic_history = []
        self.constraint_history = []
        self.alerts = []
        
    def compute_kretschmann(self, g: np.ndarray, position: np.ndarray,
                           h: float = 1e-5) -> float:
        """Compute Kretschmann scalar R_{abcd} R^{abcd}.
        
        Args:
            g: Metric tensor at position (4,4)
            position: [t, r, theta, phi]
            h: Numerical differentiation step
            
        Returns:
            Kretschmann scalar value
        """
        try:
            # Compute Riemann tensor
            Riemann = compute_riemann(lambda x: g, position, h)
            
            # Raise indices: R^{abcd} = g^{ae} g^{bf} g^{cg} g^{dh} R_{efgh}
            g_inv = np.linalg.inv(g)
            
            R_upper = np.zeros((4, 4, 4, 4))
            for a in range(4):
                for b in range(4):
                    for c in range(4):
                        for d in range(4):
                            for e in range(4):
                                for f in range(4):
                                    for gg in range(4):
                                        for hh in range(4):
                                            R_upper[a, b, c, d] += (
                                                g_inv[a, e] * g_inv[b, f] * 
                                                g_inv[c, gg] * g_inv[d, hh] * 
                                                Riemann[e, f, gg, hh]
                                            )
            
            # Kretschmann = R_{abcd} R^{abcd}
            kretschmann = np.sum(Riemann * R_upper)
            
            return float(kretschmann)
            
        except (np.linalg.LinAlgError, ValueError):
            return np.inf
    
    def compute_extrinsic_invariant(self, K_ij: np.ndarray, 
                                   gamma_ij: np.ndarray) -> float:
        """Compute K_ij K^ij = gamma^{ik} gamma^{jl} K_{ij} K_{kl}.
        
        Args:
            K_ij: Extrinsic curvature (3,3)
            gamma_ij: 3-metric (3,3)
            
        Returns:
            K_ij K^ij invariant
        """
        try:
            gamma_inv = np.linalg.inv(gamma_ij)
            
            # K^ij = gamma^{ik} gamma^{jl} K_{kl}
            K_upper = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        for l in range(3):
                            K_upper[i, j] += gamma_inv[i, k] * gamma_inv[j, l] * K_ij[k, l]
            
            # K_ij K^ij
            invariant = np.sum(K_ij * K_upper)
            
            return float(invariant)
            
        except np.linalg.LinAlgError:
            return np.inf
    
    def compute_hamiltonian_constraint(self, R: float, K_ij: np.ndarray,
                                      gamma_ij: np.ndarray,
                                      rho: float) -> float:
        """Compute Hamiltonian constraint violation.
        
        H = R + (tr K)^2 - K_{ij} K^{ij} - 16πρ
        
        For physical solutions: H = 0
        
        Args:
            R: Ricci scalar of 3-metric
            K_ij: Extrinsic curvature (3,3)
            gamma_ij: 3-metric (3,3)
            rho: Energy density
            
        Returns:
            Constraint violation (should be ~0)
        """
        try:
            gamma_inv = np.linalg.inv(gamma_ij)
            
            # tr K = gamma^{ij} K_{ij}
            tr_K = np.sum(gamma_inv * K_ij)
            
            # K_{ij} K^{ij}
            K_squared = self.compute_extrinsic_invariant(K_ij, gamma_ij)
            
            # Hamiltonian constraint
            H = R + tr_K**2 - K_squared - 16 * np.pi * rho
            
            return float(H)
            
        except np.linalg.LinAlgError:
            return np.inf
    
    def check_stability(self, time: float, g: np.ndarray, 
                       K_ij: np.ndarray = None,
                       gamma_ij: np.ndarray = None,
                       R: float = None,
                       rho: float = 0.0,
                       position: np.ndarray = None) -> Dict:
        """Full stability check at given time.
        
        Args:
            time: Evolution time
            g: 4-metric
            K_ij: Extrinsic curvature (optional)
            gamma_ij: 3-metric (optional)
            R: Ricci scalar (optional)
            rho: Energy density
            position: Position [t, r, theta, phi]
            
        Returns:
            Stability report dictionary
        """
        report = {
            'time': time,
            'position': position,
            'status': 'STABLE',
            'alerts': [],
        }
        
        # Compute Kretschmann if position provided
        if position is not None:
            kretschmann = self.compute_kretschmann(g, position)
            report['kretschmann'] = kretschmann
            self.kretschmann_history.append(kretschmann)
            
            if kretschmann > self.threshold_kretschmann:
                alert = f"Kretschmann {kretschmann:.2e} > threshold {self.threshold_kretschmann:.2e}"
                report['alerts'].append(alert)
                self.alerts.append((time, alert))
        
        # Compute extrinsic invariant
        if K_ij is not None and gamma_ij is not None:
            extrinsic = self.compute_extrinsic_invariant(K_ij, gamma_ij)
            report['extrinsic_invariant'] = extrinsic
            self.extrinsic_history.append(extrinsic)
            
            if extrinsic > self.threshold_extrinsic:
                alert = f"Extrinsic K^2 {extrinsic:.2e} > threshold {self.threshold_extrinsic:.2e}"
                report['alerts'].append(alert)
                self.alerts.append((time, alert))
        
        # Compute constraint violation
        if R is not None and K_ij is not None and gamma_ij is not None:
            constraint = self.compute_hamiltonian_constraint(R, K_ij, gamma_ij, rho)
            report['hamiltonian_constraint'] = constraint
            self.constraint_history.append(constraint)
            
            if abs(constraint) > self.threshold_constraint:
                alert = f"Constraint violation |H| = {abs(constraint):.2e}"
                report['alerts'].append(alert)
                self.alerts.append((time, alert))
        
        # Determine overall status
        if report['alerts']:
            report['status'] = 'UNSTABLE'
        
        self.time_history.append(time)
        
        return report
    
    def get_stability_timescale(self) -> Dict:
        """Estimate stability timescale from history.
        
        Returns:
            Dictionary with estimated timescales
        """
        if len(self.time_history) < 2:
            return {'tau_stability': np.inf, 'confidence': 'LOW'}
        
        # Check for exponential growth in invariants
        if len(self.kretschmann_history) > 10:
            # Fit log(K) vs time
            log_K = np.log(np.maximum(self.kretschmann_history, 1e-20))
            times = np.array(self.time_history[:len(log_K)])
            
            # Linear regression
            if len(times) > 1:
                coeffs = np.polyfit(times, log_K, 1)
                growth_rate = coeffs[0]  # d(ln K)/dt
                
                if growth_rate > 0:
                    tau = 1.0 / growth_rate
                    return {
                        'tau_stability': float(tau),
                        'growth_rate': float(growth_rate),
                        'confidence': 'MEDIUM' if len(times) > 50 else 'LOW',
                        'assessment': f'Exponential growth detected, tau = {tau:.2f}'
                    }
        
        return {
            'tau_stability': np.inf,
            'growth_rate': 0.0,
            'confidence': 'LOW',
            'assessment': 'No exponential growth detected or insufficient data'
        }
    
    def generate_report(self) -> str:
        """Generate human-readable stability report."""
        timescale = self.get_stability_timescale()
        
        lines = [
            "=" * 60,
            "STABILITY MONITOR REPORT",
            "=" * 60,
            f"Evolution steps: {len(self.time_history)}",
            f"Total alerts: {len(self.alerts)}",
            "",
            "TIMESCALE ANALYSIS:",
            f"  tau_stability: {timescale['tau_stability']:.2e}",
            f"  growth_rate: {timescale['growth_rate']:.2e}",
            f"  confidence: {timescale['confidence']}",
            f"  assessment: {timescale['assessment']}",
            "",
        ]
        
        if self.alerts:
            lines.append("ALERTS:")
            for time, alert in self.alerts[-10:]:  # Last 10 alerts
                lines.append(f"  t={time:.4f}: {alert}")
        else:
            lines.append("No stability alerts detected.")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)


def quick_stability_check(bridge: SSZBridgeMetric, 
                         n_points: int = 50) -> Dict:
    """Quick stability assessment for SSZ bridge.
    
    Scans along bridge coordinate and checks for pathological curvature.
    
    Args:
        bridge: SSZBridgeMetric instance
        n_points: Number of evaluation points
        
    Returns:
        Stability assessment dictionary
    """
    monitor = StabilityMonitor()
    
    u_values = np.linspace(-1, 1, n_points)
    
    for u in u_values:
        # Get metric at this point
        g_list = bridge.metric_tensor(u)
        g = np.array(g_list)
        
        position = np.array([0.0, u, np.pi/2, 0.0])
        
        # Simple stability check
        report = monitor.check_stability(
            time=u,  # Use u as proxy for time
            g=g,
            position=position
        )
    
    # Generate summary
    max_kretschmann = max(monitor.kretschmann_history) if monitor.kretschmann_history else 0
    
    return {
        'max_kretschmann': max_kretschmann,
        'alerts': len(monitor.alerts),
        'stable_along_bridge': len(monitor.alerts) == 0,
        'stability_timescale': monitor.get_stability_timescale(),
        'full_report': monitor.generate_report(),
    }
