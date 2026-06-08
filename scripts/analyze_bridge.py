#!/usr/bin/env python3
"""CLI tool for bridge candidate analysis.

Usage:
    python analyze_bridge.py --xi-a 0.1 --xi-b 0.2 --lambda 0.5
"""
import argparse
import sys
sys.path.insert(0, '../src')

from beam_ssz.bridge_metric import SSZBridgeMetric
from beam_ssz.complete_proof import is_beaming_proven


def main():
    parser = argparse.ArgumentParser(description='Analyze SSZ Bridge Metric')
    parser.add_argument('--xi-a', type=float, default=0.1, help='Xi at point A')
    parser.add_argument('--xi-b', type=float, default=0.1, help='Xi at point B')
    parser.add_argument('--lambda', type=float, dest='lambda_bridge', default=0.5,
                        help='Bridge coupling parameter')
    parser.add_argument('--ell0', type=float, default=1e-3, help='Bridge scale [m]')
    parser.add_argument('--radius', type=float, default=1e-2, help='Throat radius [m]')
    parser.add_argument('--l-normal', type=float, default=1.0, help='Normal distance [m]')
    
    args = parser.parse_args()
    
    # Create bridge
    bridge = SSZBridgeMetric(
        xi_left=args.xi_a,
        xi_right=args.xi_b,
        lambda_bridge=args.lambda_bridge,
        ell0=args.ell0,
        throat_radius=args.radius,
    )
    
    # Run analysis
    print(f"\n{'='*70}")
    print("BRIDGE CANDIDATE ANALYSIS")
    print(f"{'='*70}")
    print(f"\nParameters:")
    print(f"  Ξ_A = {args.xi_a}")
    print(f"  Ξ_B = {args.xi_b}")
    print(f"  λ = {args.lambda_bridge}")
    print(f"  ℓ₀ = {args.ell0:.3e} m")
    print(f"  R₀ = {args.radius:.3e} m")
    
    # Complete proof
    status = is_beaming_proven(bridge, args.l_normal)
    print(f"\n{status['full_report']}")
    
    # Quick summary
    print(f"\n{'='*70}")
    print("QUICK SUMMARY")
    print(f"{'='*70}")
    print(f"Bridge distance: {bridge.bridge_distance():.3e} m")
    print(f"Distance ratio η: {bridge.bridge_distance() / args.l_normal:.6f}")
    print(f"Classification: {status['completeness']}")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
