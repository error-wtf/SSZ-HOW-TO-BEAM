"""Energy Condition Classification Scan.

Scans parameter space and classifies candidates by energy requirement.
"""
import sys
sys.path.insert(0, 'src')

from beam_ssz.bridge_metric import SSZBridgeMetric


def main():
    print("BEAM-SSZ v0.6 - Energy Classification Scan")
    print("=" * 60)
    
    l_normal = 1.0
    lambda_values = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
    
    print(f"{'λ':<8} {'L_bridge':<12} {'η':<12} {'Tidal':<12} {'Class':<15}")
    print("-" * 60)
    
    for lam in lambda_values:
        bridge = SSZBridgeMetric(
            xi_left=0.1,
            xi_right=0.1,
            lambda_bridge=lam,
            ell0=1e-3,
            throat_radius=1e-2,
        )
        
        result = bridge.evaluate_candidate(l_normal)
        l_bridge = bridge.bridge_distance()
        
        print(f"{lam:<8.2f} {l_bridge:<12.6e} {result.distance_ratio:<12.6e} "
              f"{result.tidal_proxy:<12.3e} {result.energy_class:<15}")
    
    print("\nNote: Higher λ → stronger coupling → exotic energy class")


if __name__ == "__main__":
    main()
