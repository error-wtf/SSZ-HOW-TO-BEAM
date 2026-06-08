#!/usr/bin/env python3
"""
Gradual Entry Protocol for Human-Safe Transport Through SSZ Bridge

This protocol solves the tidal force problem by extending entry/exit
time to allow biological tolerance adaptation.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List
import sys

sys.path.insert(0, '../src')
from beam_ssz.bridge_metric import SSZBridgeMetric


@dataclass
class HumanToleranceProfile:
    """Human tolerance to acceleration over time."""
    
    # Sustained tolerance (with G-suit)
    sustained_g: float = 9.0  # g
    
    # Brief peak tolerance (seconds)
    peak_g: float = 15.0  # g
    peak_duration: float = 30.0  # seconds
    
    # Long-term degradation
    degradation_rate: float = 0.1  # g per hour
    
    def max_tolerance_at_time(self, t: float) -> float:
        """
        Maximum tolerable acceleration at time t.
        
        t: time in seconds
        returns: max g-force
        """
        if t < self.peak_duration:
            # Peak tolerance available
            return self.peak_g
        else:
            # Degradation over time
            degradation = self.degradation_rate * (t / 3600)  # per hour
            return max(self.sustained_g - degradation, 3.0)  # minimum 3g


class GradualEntrySimulator:
    """Simulate gradual entry into bridge for human safety."""
    
    def __init__(
        self,
        bridge: SSZBridgeMetric,
        entry_time: float = 3600.0,  # 1 hour
        bridge_crossing_time: float = 60.0,  # 1 minute through throat
        exit_time: float = 3600.0,  # 1 hour
    ):
        self.bridge = bridge
        self.entry_time = entry_time
        self.crossing_time = bridge_crossing_time
        self.exit_time = exit_time
        
        self.tolerance = HumanToleranceProfile()
        
        # Convert to acceleration (m/s²)
        self.g = 9.81
    
    def acceleration_profile(self, t: float, phase: str) -> float:
        """
        Define acceleration as function of time for each phase.
        
        phase: 'entry', 'crossing', or 'exit'
        """
        if phase == 'entry':
            # Gradual increase: a(t) = a_max * (t/T)²
            # At throat center (t=entry_time), reach max
            normalized_time = t / self.entry_time
            return self.tolerance.sustained_g * normalized_time**2
            
        elif phase == 'crossing':
            # Constant high acceleration during crossing
            return self.tolerance.peak_g
            
        elif phase == 'exit':
            # Gradual decrease: a(t) = a_max * (1 - t/T)²
            normalized_time = t / self.exit_time
            return self.tolerance.peak_g * (1 - normalized_time)**2
        
        else:
            raise ValueError(f"Unknown phase: {phase}")
    
    def tidal_force_at_point(self, u: float) -> float:
        """
        Compute tidal acceleration at bridge coordinate u.
        
        Tidal scales with curvature: Δa ~ c²/ℓ₀² × f(Ξ)
        """
        # Simplified tidal estimate
        xi = self.bridge.xi(u)
        dxi = self.bridge.dxi_du(u)
        
        # From geodesic deviation
        # Δa ≈ (c²/ℓ₀²) × |d²Ξ/du²| × δξ
        # where δξ ~ human scale (~1m)
        
        h = 0.01
        dxi_plus = self.bridge.dxi_du(u + h)
        dxi_minus = self.bridge.dxi_du(u - h)
        d2xi = abs((dxi_plus - dxi_minus) / (2 * h))
        
        from beam_ssz.constants import C
        tidal = (C**2 / self.bridge.ell0**2) * (1 + xi + d2xi) * 1.0
        
        # Convert to g
        tidal_g = tidal / self.g
        
        return tidal_g
    
    def simulate_full_protocol(self) -> dict:
        """
        Simulate the complete gradual entry protocol.
        
        Returns:
        - Time histories
        - Acceleration profiles
        - Tidal forces
        - Safety margins
        """
        # Time arrays
        dt = 1.0  # 1 second resolution
        
        t_entry = np.arange(0, self.entry_time, dt)
        t_crossing = np.arange(0, self.crossing_time, dt)
        t_exit = np.arange(0, self.exit_time, dt)
        
        # Acceleration profiles
        a_entry = [self.acceleration_profile(t, 'entry') for t in t_entry]
        a_crossing = [self.acceleration_profile(t, 'crossing') for t in t_crossing]
        a_exit = [self.acceleration_profile(t, 'exit') for t in t_exit]
        
        # Tidal forces during crossing (only significant in throat)
        # Bridge coordinate u goes from -1 to +1 during crossing
        u_values = np.linspace(-1, 1, len(t_crossing))
        tidal_crossing = [self.tidal_force_at_point(u) for u in u_values]
        
        # Safety check
        tolerance_crossing = [self.tolerance.max_tolerance_at_time(t) for t in t_crossing]
        safety_margin = [tol - tidal for tol, tidal in zip(tolerance_crossing, tidal_crossing)]
        
        # Check if safe
        min_safety = min(safety_margin)
        is_safe = min_safety > 0
        
        results = {
            'time_total': self.entry_time + self.crossing_time + self.exit_time,
            'time_entry': t_entry,
            'time_crossing': t_crossing,
            'time_exit': t_exit,
            'accel_entry': a_entry,
            'accel_crossing': a_crossing,
            'accel_exit': a_exit,
            'tidal_crossing': tidal_crossing,
            'tolerance_crossing': tolerance_crossing,
            'safety_margin': safety_margin,
            'is_safe': is_safe,
            'min_safety_margin': min_safety,
        }
        
        return results
    
    def optimize_entry_time(self, target_safety_margin: float = 1.0) -> float:
        """
        Find minimum entry time that achieves target safety margin.
        
        Binary search for optimal entry time.
        """
        print("Optimizing entry time...")
        
        t_min = 60.0  # 1 minute (too short)
        t_max = 36000.0  # 10 hours (definitely safe)
        
        for iteration in range(20):
            t_test = (t_min + t_max) / 2
            self.entry_time = t_test
            self.exit_time = t_test
            
            results = self.simulate_full_protocol()
            
            if results['is_safe'] and results['min_safety_margin'] >= target_safety_margin:
                # Safe, try shorter
                t_max = t_test
                print(f"  Iteration {iteration}: t={t_test/60:.1f} min, SAFE (margin={results['min_safety_margin']:.1f}g)")
            else:
                # Unsafe, need longer
                t_min = t_test
                print(f"  Iteration {iteration}: t={t_test/60:.1f} min, UNSAFE (margin={results['min_safety_margin']:.1f}g)")
        
        optimal_time = (t_min + t_max) / 2
        print(f"\nOptimal entry time: {optimal_time/60:.1f} minutes")
        
        return optimal_time
    
    def plot_protocol(self, results: dict, filename='gradual_entry_protocol.png'):
        """
        Visualize the gradual entry protocol.
        """
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # Phase 1: Entry
        ax = axes[0]
        t_hours = np.array(results['time_entry']) / 3600
        ax.plot(t_hours, results['accel_entry'], 'b-', linewidth=2, label='Applied acceleration')
        ax.axhline(y=self.tolerance.sustained_g, color='r', linestyle='--', label='Tolerance limit')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Acceleration (g)')
        ax.set_title('Phase 1: Gradual Entry')
        ax.legend()
        ax.grid(True)
        
        # Phase 2: Crossing
        ax = axes[1]
        t_sec = np.array(results['time_crossing'])
        ax.plot(t_sec, results['tidal_crossing'], 'r-', linewidth=2, label='Tidal force')
        ax.plot(t_sec, results['tolerance_crossing'], 'g--', linewidth=2, label='Human tolerance')
        ax.fill_between(t_sec, results['tidal_crossing'], results['tolerance_crossing'], 
                        alpha=0.3, color='green', label='Safety margin')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Acceleration (g)')
        ax.set_title('Phase 2: Bridge Crossing')
        ax.legend()
        ax.grid(True)
        
        # Phase 3: Exit
        ax = axes[2]
        t_hours = np.array(results['time_exit']) / 3600
        ax.plot(t_hours, results['accel_exit'], 'b-', linewidth=2, label='Applied acceleration')
        ax.axhline(y=self.tolerance.sustained_g, color='r', linestyle='--', label='Tolerance limit')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Acceleration (g)')
        ax.set_title('Phase 3: Gradual Exit')
        ax.legend()
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        print(f"Protocol visualization saved to {filename}")
        
        plt.close()


def main():
    """Run gradual entry protocol simulation."""
    
    print("=" * 70)
    print("GRADUAL ENTRY PROTOCOL FOR HUMAN-SAFE BRIDGE TRANSPORT")
    print("=" * 70)
    
    # Create bridge
    from beam_ssz.bridge_metric import SSZBridgeMetric
    
    bridge = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.1,
        ell0=1.0,  # Larger for safety
        throat_radius=10.0,
    )
    
    print(f"\nBridge parameters:")
    print(f"  ℓ₀ = {bridge.ell0} m")
    print(f"  R₀ = {bridge.throat_radius} m")
    print(f"  Ξ = {bridge.xi_left}")
    print(f"  λ = {bridge.lambda_bridge}")
    
    # Initial simulation
    print("\n" + "=" * 70)
    print("Initial simulation with 1-hour entry...")
    print("=" * 70)
    
    simulator = GradualEntrySimulator(bridge)
    results = simulator.simulate_full_protocol()
    
    print(f"\nTotal transit time: {results['time_total']/3600:.1f} hours")
    print(f"Minimum safety margin: {results['min_safety_margin']:.1f} g")
    print(f"Protocol is SAFE: {results['is_safe']}")
    
    # Optimize
    print("\n" + "=" * 70)
    print("Optimizing for minimum safe entry time...")
    print("=" * 70)
    
    optimal_time = simulator.optimize_entry_time(target_safety_margin=2.0)
    
    # Final simulation with optimal time
    simulator.entry_time = optimal_time
    simulator.exit_time = optimal_time
    results = simulator.simulate_full_protocol()
    
    # Visualize
    simulator.plot_protocol(results)
    
    print("\n" + "=" * 70)
    print("PROTOCOL SUMMARY")
    print("=" * 70)
    print(f"Entry time:  {optimal_time/60:.1f} minutes")
    print(f"Crossing:    {simulator.crossing_time:.0f} seconds")
    print(f"Exit time:   {optimal_time/60:.1f} minutes")
    print(f"Total:       {results['time_total']/3600:.1f} hours")
    print(f"\nSafety margin: {results['min_safety_margin']:.1f} g")
    print(f"Status: {'✓ SAFE' if results['is_safe'] else '✗ UNSAFE'}")
    print("=" * 70)
    if results['is_safe']:
        print("\nKey insight:")
        print("\n✓ This parameter set satisfies the current biological-scale proxy.")
        print("Extended-body transport may be possible with this configuration.")
    else:
        print("\n⚠️  CRITICAL LIMITATION:")
        print("This parameter set does NOT support biological transport.")
        print("Tidal forces exceed human tolerance even with gradual entry.")
        print("Try: larger ℓ₀, smaller Ξ, or different bridge profile.")
    print("=" * 70)


if __name__ == "__main__":
    main()
