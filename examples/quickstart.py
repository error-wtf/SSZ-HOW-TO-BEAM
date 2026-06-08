"""Quickstart example for BEAM-SSZ v0.6.

This example demonstrates basic usage of the BEAM-SSZ framework.
"""
import sys
sys.path.insert(0, '../src')

from beam_ssz import (
    SSZBridgeMetric,
    create_canonical_bridge,
    evaluate_xi_x,
    BeamingProofFramework,
    is_beaming_proven,
)


def main():
    print("=" * 70)
    print("BEAM-SSZ v0.6 - Quickstart Example")
    print("=" * 70)
    
    # 1. Evaluate canonical Xi
    print("\n1. Canonical SSZ Xi Evaluation")
    print("-" * 70)
    x = 2.0  # r/r_s = 2.0
    xi_result = evaluate_xi_x(x)
    print(f"At r/r_s = {x}:")
    print(f"  Ξ(x) = {xi_result.xi:.6f}")
    print(f"  Regime: {xi_result.regime.value}")
    print(f"  dΞ/dx = {xi_result.dxi_dx:.6f}")
    
    # 2. Create bridge metric
    print("\n2. Bridge Metric Creation")
    print("-" * 70)
    bridge = create_canonical_bridge(
        xi_a=0.1,
        xi_b=0.2,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    print(f"Bridge created with:")
    print(f"  Ξ_A = {bridge.xi_left}")
    print(f"  Ξ_B = {bridge.xi_right}")
    print(f"  λ = {bridge.lambda_bridge}")
    
    # 3. Compute bridge properties
    print("\n3. Bridge Properties")
    print("-" * 70)
    l_bridge = bridge.bridge_distance()
    print(f"Bridge distance: {l_bridge:.3e} m")
    
    # 4. Mathematical proof
    print("\n4. Mathematical Proof Analysis")
    print("-" * 70)
    framework = BeamingProofFramework()
    theorems = framework.prove_all_theorems(bridge, l_normal=1.0)
    
    for th in theorems:
        status = "✓" if th.conditions_satisfied else "?"
        print(f"  {status} {th.theorem_name}: {th.status.value}")
    
    # 5. Complete assessment
    print("\n5. Complete Feasibility Assessment")
    print("-" * 70)
    status = is_beaming_proven(bridge, l_normal=1.0)
    print(f"Status: {status['completeness']}")
    print(f"Theorems proven: {status['theorems_proven']}/8")
    print(f"\nConclusion:")
    print(f"  {status['conclusion']}")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
