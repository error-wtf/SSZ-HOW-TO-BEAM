"""Feasibility Analysis - Under what conditions are open problems solvable?

This module systematically tests parameter combinations to find
regions where the open problems become tractable.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum

from .bridge_metric import SSZBridgeMetric, create_canonical_bridge
from .proof_framework import BeamingProofFramework
from .einstein_solver import estimate_energy_requirements
from .stability_analysis import BridgeStabilityAnalyzer
from .quantum_consistency import BridgeQuantumAnalyzer
from .thermodynamics import BridgeThermodynamicAnalyzer
from .proofs import Theorem4EnergyProof


class FeasibilityLevel(str, Enum):
    """Feasibility classification."""
    FULLY_SOLVABLE = "FULLY_SOLVABLE"  # All open problems solvable
    PARTIALLY_SOLVABLE = "PARTIALLY_SOLVABLE"  # Some problems solvable
    CHALLENGING = "CHALLENGING"  # Difficult but not impossible
    PROBLEMATIC = "PROBLEMATIC"  # Major issues remain
    IMPOSSIBLE = "IMPOSSIBLE"  # Physics forbids


@dataclass
class FeasibilityResult:
    """Result of feasibility analysis."""
    parameters: dict
    
    # Solvability of each open problem
    nonlinear_stability_solvable: bool
    exotic_matter_avoidable: bool
    energy_achievable: bool
    tidal_safe: bool
    quantum_valid: bool
    thermodynamically_sound: bool
    
    # Overall
    overall_feasibility: FeasibilityLevel
    limiting_factors: List[str]
    recommendations: List[str]
    
    # Trade-offs
    distance_reduction: float
    tidal_acceleration: float
    max_energy_density: float


class OpenProblemSolver:
    """Analyzes under what conditions open problems become solvable."""
    
    @staticmethod
    def find_nec_safe_region(
        xi_a: float,
        xi_b: float,
        lambda_max: float = 5.0,
        n_samples: int = 50,
    ) -> Tuple[float, dict]:
        """
        Find the critical λ where NEC transitions from satisfied to violated.
        
        For λ < λ_crit: Exotic matter NOT needed (solvable)
        For λ > λ_crit: Exotic matter required (problematic)
        """
        proof = Theorem4EnergyProof()
        
        lambda_values = np.linspace(0.01, lambda_max, n_samples)
        nec_status = []
        
        for lam in lambda_values:
            test_bridge = SSZBridgeMetric(
                xi_left=xi_a,
                xi_right=xi_b,
                lambda_bridge=lam,
                ell0=1e-3,
                throat_radius=1e-2,
            )
            
            nec_sat, _, _ = proof.analyze_nec_analytically(test_bridge)
            nec_status.append((lam, nec_sat))
        
        # Find transition
        lambda_crit = None
        for i in range(len(nec_status) - 1):
            if nec_status[i][1] and not nec_status[i+1][1]:
                lambda_crit = (nec_status[i][0] + nec_status[i+1][0]) / 2
                break
        
        analysis = {
            'lambda_values': lambda_values,
            'nec_status': nec_status,
            'lambda_critical': lambda_crit,
            'safe_range': (0, lambda_crit) if lambda_crit else (0, lambda_max),
            'conclusion': f"NEC satisfied for λ < {lambda_crit:.3f}" if lambda_crit else "NEC satisfied for all tested λ",
        }
        
        return lambda_crit if lambda_crit else lambda_max, analysis
    
    @staticmethod
    def find_tidal_safe_scale(
        bridge: SSZBridgeMetric,
        a_max: float = 98.1,  # 10g
    ) -> Tuple[float, float, dict]:
        """
        Find ℓ₀ that makes tidal forces acceptable.
        
        Trade-off: Large ℓ₀ → safe tidal but large L_bridge
        """
        from .proofs import Theorem5TidalProof
        
        proof5 = Theorem5TidalProof()
        
        # Current tidal
        current_max_tidal = proof5.compute_tidal_bound(bridge)
        
        # Required ℓ₀ for safety
        result = proof5.prove_tidal_safety(bridge, a_max)
        required_ell0 = result.optimal_ell0
        
        # Distance at safe scale
        safe_bridge = SSZBridgeMetric(
            xi_left=bridge.xi_left,
            xi_right=bridge.xi_right,
            lambda_bridge=bridge.lambda_bridge,
            ell0=required_ell0,
            throat_radius=bridge.throat_radius,
        )
        l_bridge_safe = safe_bridge.bridge_distance()
        
        analysis = {
            'current_tidal': current_max_tidal,
            'safety_threshold': a_max,
            'currently_safe': current_max_tidal < a_max,
            'required_ell0': required_ell0,
            'current_ell0': bridge.ell0,
            'scale_factor': required_ell0 / bridge.ell0,
            'l_bridge_at_safe_scale': l_bridge_safe,
            'conclusion': f"Need ℓ₀ > {required_ell0:.3e} m for tidal safety",
        }
        
        return required_ell0, l_bridge_safe, analysis
    
    @staticmethod
    def find_energy_optimal_parameters(
        target_energy_density: float = 1e35,  # Nuclear density
        xi_range: Tuple[float, float] = (0.01, 0.5),
        lambda_range: Tuple[float, float] = (0.01, 1.0),
    ) -> List[dict]:
        """
        Find parameter combinations with acceptable energy requirements.
        """
        feasible_configs = []
        
        xi_values = np.linspace(xi_range[0], xi_range[1], 10)
        lambda_values = np.linspace(lambda_range[0], lambda_range[1], 10)
        
        for xi in xi_values:
            for lam in lambda_values:
                bridge = SSZBridgeMetric(
                    xi_left=xi,
                    xi_right=xi,
                    lambda_bridge=lam,
                    ell0=1e-3,
                    throat_radius=1e-2,
                )
                
                energy = estimate_energy_requirements(bridge, verbose=False)
                
                if energy['status'] == 'SUCCESS':
                    max_rho = energy['max_energy_density']
                    
                    if max_rho < target_energy_density:
                        feasible_configs.append({
                            'xi': xi,
                            'lambda': lam,
                            'max_energy_density': max_rho,
                            'vs_nuclear': max_rho / 1e35,
                        })
        
        return feasible_configs
    
    @staticmethod
    def find_stable_parameter_region(
        xi_range: Tuple[float, float] = (0.01, 0.3),
        lambda_range: Tuple[float, float] = (0.01, 2.0),
        n_samples: int = 20,
    ) -> Tuple[List[dict], dict]:
        """
        Map parameter space for linear stability.
        
        Returns regions where stability analysis shows no unstable modes.
        """
        stable_regions = []
        
        xi_values = np.linspace(xi_range[0], xi_range[1], n_samples)
        lambda_values = np.linspace(lambda_range[0], lambda_range[1], n_samples)
        
        analyzer = BridgeStabilityAnalyzer()
        
        for xi in xi_values:
            for lam in lambda_values:
                bridge = SSZBridgeMetric(
                    xi_left=xi,
                    xi_right=xi,
                    lambda_bridge=lam,
                    ell0=1e-3,
                    throat_radius=1e-2,
                )
                
                result = analyzer.analyze_stability_proxy(bridge)
                
                if result.linearly_stable and result.unstable_modes == 0:
                    stable_regions.append({
                        'xi': xi,
                        'lambda': lam,
                        'stable': True,
                    })
        
        analysis = {
            'total_tested': n_samples * n_samples,
            'stable_count': len(stable_regions),
            'stability_fraction': len(stable_regions) / (n_samples * n_samples),
            'xi_range_stable': (min(r['xi'] for r in stable_regions), max(r['xi'] for r in stable_regions)) if stable_regions else None,
            'lambda_range_stable': (min(r['lambda'] for r in stable_regions), max(r['lambda'] for r in stable_regions)) if stable_regions else None,
        }
        
        return stable_regions, analysis
    
    @classmethod
    def comprehensive_feasibility_analysis(
        cls,
        xi_a: float = 0.1,
        xi_b: float = 0.1,
        lambda_val: float = 0.5,
        ell0: float = 1e-3,
        throat_radius: float = 1e-2,
        l_normal: float = 1.0,
    ) -> FeasibilityResult:
        """
        Complete feasibility analysis for given parameters.
        
        Determines which open problems are solvable and which are not.
        """
        bridge = SSZBridgeMetric(
            xi_left=xi_a,
            xi_right=xi_b,
            lambda_bridge=lambda_val,
            ell0=ell0,
            throat_radius=throat_radius,
        )
        
        limiting_factors = []
        recommendations = []
        
        # 1. Nonlinear stability (assume linear is proxy)
        stab_analyzer = BridgeStabilityAnalyzer()
        stab_result = stab_analyzer.analyze_stability_proxy(bridge)
        stability_solvable = stab_result.linearly_stable
        if not stability_solvable:
            limiting_factors.append("Linear instability suggests nonlinear problems")
            recommendations.append("Reduce λ or increase ℓ₀ for stability")
        
        # 2. Exotic matter
        proof4 = Theorem4EnergyProof()
        nec_sat, _, _ = proof4.analyze_nec_analytically(bridge)
        exotic_avoidable = nec_sat
        if not exotic_avoidable:
            limiting_factors.append("NEC violation requires exotic matter")
            recommendations.append("Reduce λ below critical value")
        
        # 3. Energy
        energy = estimate_energy_requirements(bridge, verbose=False)
        if energy['status'] == 'SUCCESS':
            max_rho = energy['max_energy_density']
            vs_planck = max_rho / 1e113
            energy_achievable = vs_planck < 1.0 and max_rho < 1e40  # Within some bounds
            if not energy_achievable:
                limiting_factors.append(f"Energy density {max_rho:.3e} J/m³ too high")
                recommendations.append("Reduce Ξ and λ, increase ℓ₀")
        else:
            max_rho = float('inf')
            energy_achievable = False
            limiting_factors.append("Could not compute energy requirements")
        
        # 4. Tidal safety
        from .proofs import Theorem5TidalProof
        proof5 = Theorem5TidalProof()
        tidal_result = proof5.prove_tidal_safety(bridge, a_max=98.1)
        tidal_safe = tidal_result.is_safe
        if not tidal_safe:
            limiting_factors.append(f"Tidal acceleration {tidal_result.max_tidal_acceleration:.3e} m/s² exceeds safety")
            recommendations.append(f"Increase ℓ₀ to > {tidal_result.optimal_ell0:.3e} m")
        
        # 5. Quantum validity
        q_analyzer = BridgeQuantumAnalyzer()
        q_result = q_analyzer.analyze_quantum_consistency(bridge)
        quantum_valid = q_result.semiclassical_valid and q_result.quantum_inequalities_satisfied
        if not quantum_valid:
            limiting_factors.append("Semiclassical approximation may break down")
            recommendations.append("Ensure ℓ₀ >> Planck length")
        
        # 6. Thermodynamics
        t_analyzer = BridgeThermodynamicAnalyzer()
        t_result = t_analyzer.analyze_thermodynamics(bridge)
        thermo_sound = not t_result.violation_of_standard_physics
        if not thermo_sound:
            limiting_factors.append("Thermodynamic violations detected")
            recommendations.append("Reduce energy density below Planck scale")
        
        # Overall assessment
        solvable_count = sum([stability_solvable, exotic_avoidable, energy_achievable, 
                             tidal_safe, quantum_valid, thermo_sound])
        
        if solvable_count == 6:
            overall = FeasibilityLevel.FULLY_SOLVABLE
        elif solvable_count >= 4:
            overall = FeasibilityLevel.PARTIALLY_SOLVABLE
        elif solvable_count >= 3:
            overall = FeasibilityLevel.CHALLENGING
        elif solvable_count >= 1:
            overall = FeasibilityLevel.PROBLEMATIC
        else:
            overall = FeasibilityLevel.IMPOSSIBLE
        
        return FeasibilityResult(
            parameters={
                'xi_a': xi_a,
                'xi_b': xi_b,
                'lambda': lambda_val,
                'ell0': ell0,
                'throat_radius': throat_radius,
            },
            nonlinear_stability_solvable=stability_solvable,
            exotic_matter_avoidable=exotic_avoidable,
            energy_achievable=energy_achievable,
            tidal_safe=tidal_safe,
            quantum_valid=quantum_valid,
            thermodynamically_sound=thermo_sound,
            overall_feasibility=overall,
            limiting_factors=limiting_factors,
            recommendations=recommendations,
            distance_reduction=bridge.bridge_distance() / l_normal,
            tidal_acceleration=tidal_result.max_tidal_acceleration,
            max_energy_density=max_rho if isinstance(max_rho, float) else float('inf'),
        )
    
    @classmethod
    def find_fully_solvable_configuration(
        cls,
        verbose: bool = True,
    ) -> Optional[FeasibilityResult]:
        """
        Search for parameter combinations where ALL open problems are solvable.
        
        This is the holy grail - a configuration that satisfies all constraints.
        """
        # Search strategy: Start with weak parameters, gradually increase
        
        test_configs = [
            # Weak, safe configurations
            (0.01, 0.01, 0.01, 1e-2, 1e-2),
            (0.05, 0.05, 0.1, 1e-2, 1e-2),
            (0.1, 0.1, 0.2, 1e-2, 1e-2),
            # Try larger scales
            (0.01, 0.01, 0.01, 1e-1, 1e-1),
            (0.05, 0.05, 0.1, 1e-1, 1e-1),
            # Try moderate coupling
            (0.1, 0.1, 0.3, 1e-2, 1e-2),
            (0.1, 0.1, 0.5, 5e-2, 5e-2),
        ]
        
        best_result = None
        best_score = 0
        
        for xi_a, xi_b, lam, ell0, r0 in test_configs:
            result = cls.comprehensive_feasibility_analysis(
                xi_a, xi_b, lam, ell0, r0, l_normal=1.0,
            )
            
            score = sum([
                result.nonlinear_stability_solvable,
                result.exotic_matter_avoidable,
                result.energy_achievable,
                result.tidal_safe,
                result.quantum_valid,
                result.thermodynamically_sound,
            ])
            
            if score > best_score:
                best_score = score
                best_result = result
            
            if result.overall_feasibility == FeasibilityLevel.FULLY_SOLVABLE:
                if verbose:
                    print(f"\n✓ FOUND FULLY SOLVABLE CONFIGURATION!")
                    print(f"   Parameters: Ξ={xi_a}, λ={lam}, ℓ₀={ell0:.3e}")
                return result
        
        # Return best found
        if best_result and verbose:
            print(f"\n✗ No fully solvable configuration found")
            print(f"   Best score: {best_score}/6")
            print(f"   Best config: {best_result.parameters}")
        
        return best_result


if __name__ == "__main__":
    print("=" * 70)
    print("FEASIBILITY ANALYSIS: When are open problems solvable?")
    print("=" * 70)
    
    solver = OpenProblemSolver()
    
    # Find critical lambda for NEC
    print("\n[1] Finding NEC-safe region...")
    lambda_crit, nec_analysis = solver.find_nec_safe_region(0.1, 0.1)
    print(f"   Critical λ: {lambda_crit:.3f}")
    print(f"   {nec_analysis['conclusion']}")
    
    # Find tidal-safe scale
    print("\n[2] Finding tidal-safe configuration...")
    bridge = create_canonical_bridge()
    req_ell0, l_bridge_safe, tidal_analysis = solver.find_tidal_safe_scale(bridge)
    print(f"   Required ℓ₀: {req_ell0:.3e} m")
    print(f"   L_bridge at safe scale: {l_bridge_safe:.3e} m")
    
    # Find energy-optimal
    print("\n[3] Finding energy-optimal configurations...")
    energy_configs = solver.find_energy_optimal_parameters(target_energy_density=1e36)
    print(f"   Found {len(energy_configs)} configurations below target energy")
    if energy_configs:
        print(f"   Best: Ξ={energy_configs[0]['xi']:.2f}, λ={energy_configs[0]['lambda']:.2f}")
    
    # Find stable regions
    print("\n[4] Mapping stability regions...")
    stable_regions, stability_analysis = solver.find_stable_parameter_region()
    print(f"   Stable fraction: {stability_analysis['stability_fraction']:.1%}")
    
    # Comprehensive search for fully solvable config
    print("\n[5] Searching for FULLY SOLVABLE configuration...")
    best = solver.find_fully_solvable_configuration(verbose=True)
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    if best and best.overall_feasibility == FeasibilityLevel.FULLY_SOLVABLE:
        print("✓ Found configuration where all open problems are solvable!")
        print(f"  Parameters: {best.parameters}")
    else:
        print("✗ No fully solvable configuration found in tested parameter space")
        print("  Trade-offs prevent simultaneous satisfaction of all constraints")
    print("=" * 70)
