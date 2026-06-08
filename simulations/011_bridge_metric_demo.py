"""Bridge Metric Demonstration - Core Real-Beaming Solution.

This simulation demonstrates the SSZ bridge metric as the mathematical
solution for real-beaming: continuous worldline through bridge channel,
not scan/copy.
"""
import sys
sys.path.insert(0, 'src')

from beam_ssz.bridge_metric import create_canonical_bridge, evaluate_bridge_candidate, SSZBridgeMetric


def main():
    print("=" * 70)
    print("BEAM-SSZ v0.6 - Bridge Metric Demonstration")
    print("Core Solution: Continuous Worldline, No Copy")
    print("=" * 70)
    
    # Test 1: Canonical bridge with moderate parameters
    print("\n--- Test 1: Canonical Bridge ---")
    bridge1 = create_canonical_bridge(
        xi_a=0.1,
        xi_b=0.1,
        lambda_bridge=0.5,
        ell0=1e-3,
        throat_radius=1e-2,
    )
    l_normal = 1.0  # 1 meter normal distance
    evaluate_bridge_candidate(bridge1, l_normal, verbose=True)
    
    # Test 2: Stronger bridge coupling
    print("\n--- Test 2: Strong Coupling Bridge ---")
    bridge2 = SSZBridgeMetric(
        xi_left=0.1,
        xi_right=0.2,
        lambda_bridge=2.0,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    evaluate_bridge_candidate(bridge2, l_normal, verbose=True)
    
    # Test 3: Weak bridge (almost normal space)
    print("\n--- Test 3: Weak Bridge (near-normal) ---")
    bridge3 = SSZBridgeMetric(
        xi_left=0.01,
        xi_right=0.01,
        lambda_bridge=0.01,
        ell0=1e-2,
        throat_radius=1e-2,
    )
    evaluate_bridge_candidate(bridge3, l_normal, verbose=True)
    
    # Summary comparison
    print("\n" + "=" * 70)
    print("Summary Comparison")
    print("=" * 70)
    
    bridges = [
        ("Canonical", bridge1),
        ("Strong", bridge2),
        ("Weak", bridge3),
    ]
    
    print(f"{'Type':<15} {'L_bridge (m)':<15} {'Ratio η':<15} {'Energy Class':<20}")
    print("-" * 65)
    
    for name, bridge in bridges:
        result = bridge.evaluate_candidate(l_normal)
        l_bridge = bridge.bridge_distance()
        print(f"{name:<15} {l_bridge:<15.6e} {result.distance_ratio:<15.6e} {result.energy_class:<20}")
    
    print("\n" + "=" * 70)
    print("Key Insight: L_bridge << L_normal is the mathematical beam effect.")
    print("Not superluminal. Not copy. But: different effective distance.")
    print("=" * 70)


if __name__ == "__main__":
    main()
