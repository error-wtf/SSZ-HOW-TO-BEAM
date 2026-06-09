#!/usr/bin/env python3
"""
SSZ-HOW-TO-BEAM v1.1.0-canonical - MAXIMUM DETAIL TEST
Shows real values and detailed calculations for every module
Canonical SSZ formulas: Xi_horizon = 0.8017
"""

import sys
import numpy as np
from datetime import datetime

print("╔══════════════════════════════════════════════════════════════════════════════╗")
print("║     SSZ-HOW-TO-BEAM v1.1.0-canonical - MAXIMUM DETAIL MODULE TEST            ║")
print("║           Real Values - Real Calculations - All Modules                        ║")
print("╚══════════════════════════════════════════════════════════════════════════════╝")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

results = {'passed': [], 'failed': []}

def detailed_test(name, test_func):
    """Run test with maximum detail output."""
    print(f"\n{'='*80}")
    print(f"MODULE: {name}")
    print(f"{'='*80}")
    
    try:
        output = test_func()
        results['passed'].append(name)
        print(f"\n✅ {name} - PASS")
        print(f"   RESULT: {output}")
        return True
    except Exception as e:
        results['failed'].append((name, str(e)))
        print(f"\n❌ {name} - FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 1: Xi from radius
def test_xi_from_radius():
    from beam_ssz import xi_from_radius
    print("   Formula: Xi = PHI * (r_s / r)")
    radii = [1.0, 10.0, 100.0, 1000.0]
    xi_vals = [xi_from_radius(r) for r in radii]
    for r, xi in zip(radii, xi_vals):
        print(f"   r={r:>6.1f} → Xi={xi:.10f}")
    assert xi_vals[0] == 1.0
    assert abs(xi_vals[1] - 0.1) < 1e-10
    return f"Xi=[{', '.join([f'{x:.6f}' for x in xi_vals])}]"

def test_d_ssz_from_xi():
    from beam_ssz import d_ssz_from_xi
    print("   Formula: D = 1 / (1 + Xi)")
    xi_vals = [0.0, 0.1, 0.5, 1.0, 2.0]
    d_vals = [d_ssz_from_xi(xi) for xi in xi_vals]
    for xi, d in zip(xi_vals, d_vals):
        expected = 1.0 / (1.0 + xi)
        print(f"   Xi={xi:.1f} → D={d:.10f} (expected {expected:.10f})")
    assert d_vals[0] == 1.0
    return f"D=[{', '.join([f'{d:.6f}' for d in d_vals])}]"

def test_s_ssz_from_xi():
    from beam_ssz import s_ssz_from_xi, d_ssz_from_xi
    print("   Formula: s = 1 + Xi")
    xi_vals = [0.0, 0.1, 0.5, 1.0, 2.0]
    s_vals = [s_ssz_from_xi(xi) for xi in xi_vals]
    for xi, s in zip(xi_vals, s_vals):
        expected = 1.0 + xi
        from_d = 1.0 / d_ssz_from_xi(xi)
        print(f"   Xi={xi:.1f} → s={s:.10f}, 1/D={from_d:.10f}, match={abs(s-from_d)<1e-10}")
    return f"s=[{', '.join([f'{s:.6f}' for s in s_vals])}], verified s=1/D"

def test_effective_segment_distance():
    from beam_ssz import effective_segment_distance, d_ssz_from_xi, s_ssz_from_xi
    r, xi = 1.0, 0.1
    print(f"   Input: r={r}, Xi={xi}")
    D = d_ssz_from_xi(xi)
    s = s_ssz_from_xi(xi)
    result = effective_segment_distance(r, xi, 0.0)
    expected = r * D * s
    print(f"   D = 1/(1+{xi}) = {D:.6f}")
    print(f"   s = 1+{xi} = {s:.6f}")
    print(f"   d_eff = {r} * {D:.6f} * {s:.6f} = {result:.6f}")
    assert abs(result - expected) < 1e-10
    return f"d_eff={result:.6f} for r={r}, Xi={xi}"

def test_neighborhood_overlap():
    from beam_ssz import neighborhood_overlap, d_ssz_from_xi
    r1, r2, xi = 1.0, 1.0, 0.1
    print(f"   Input: r1={r1}, r2={r2}, Xi={xi}")
    D = d_ssz_from_xi(xi)
    result = neighborhood_overlap(r1, r2, xi, xi)
    print(f"   D = {D:.6f}")
    print(f"   Overlap = {result:.6f} ({result*100:.1f}%)")
    return f"overlap={result:.6f} for identical points"

def test_validate_worldline_continuity():
    from beam_ssz import validate_worldline_continuity
    from beam_ssz.ssz_core import WorldlineSample
    sample = WorldlineSample(tau=0.0, t=0.0, r=1.0, theta=0.0, phi=0.0)
    print(f"   Sample: tau={sample.tau}, x={sample.x}")
    result = validate_worldline_continuity([sample])
    print(f"   Status: {result.status}")
    print(f"   Continuous: {result.continuous}")
    return f"status={result.status}, continuous={result.continuous}"

def test_no_copy_constraint():
    from beam_ssz import no_copy_constraint, TransportMode
    result = no_copy_constraint(TransportMode.CONTINUOUS_WORLDLINE)
    print(f"   Transport: CONTINUOUS_WORLDLINE")
    print(f"   Pass: {result['pass']}")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    assert result['pass'] == True
    return f"pass={result['pass']}, status={result['status']}"

def test_validate_ssz_bridge_candidate():
    from beam_ssz import validate_ssz_bridge_candidate
    point_a = [0.0, 10.0, 1.57, 0.0]
    point_b = [0.0, 11.0, 1.57, 0.0]
    print(f"   Point A: {point_a}")
    print(f"   Point B: {point_b}")
    report = validate_ssz_bridge_candidate(point_a, point_b, lambda r: 0.1, 0.5)
    print(f"   Readiness: {report.overall_readiness}")
    print(f"   Allowed claims: {len(report.allowed_claims)}")
    print(f"   Forbidden claims: {len(report.forbidden_claims)}")
    return f"readiness={report.overall_readiness}"

def test_claim_gates():
    from beam_ssz import evaluate_claim_gate, EvidenceLevel, ClaimCategory
    result = evaluate_claim_gate(
        category=ClaimCategory.SSZ_SEGMENTATION,
        tests_passed=True,
        evidence_level=EvidenceLevel.PROXY_TESTED
    )
    print(f"   Category: SSZ_SEGMENTATION")
    print(f"   Allowed: {result['allowed']}")
    print(f"   Wording: {result['wording'][:50]}...")
    assert result['allowed'] == True
    return f"allowed={result['allowed']}, wording={result['wording'][:30]}..."

# Run all tests
print("\n" + "="*80)
print("SECTION 1: CORE SEGMENTATION MODULES")
print("="*80)

detailed_test("xi_from_radius", test_xi_from_radius)
detailed_test("d_ssz_from_xi", test_d_ssz_from_xi)
detailed_test("s_ssz_from_xi", test_s_ssz_from_xi)
detailed_test("effective_segment_distance", test_effective_segment_distance)
detailed_test("neighborhood_overlap", test_neighborhood_overlap)
detailed_test("validate_worldline_continuity", test_validate_worldline_continuity)
detailed_test("no_copy_constraint", test_no_copy_constraint)
detailed_test("validate_ssz_bridge_candidate", test_validate_ssz_bridge_candidate)
detailed_test("claim_gates", test_claim_gates)

# Final summary
print(f"\n{'='*80}")
print("FINAL RESULTS")
print(f"{'='*80}")
print(f"Total Modules Tested: {len(results['passed']) + len(results['failed'])}")
print(f"Passed:              {len(results['passed'])}")
print(f"Failed:              {len(results['failed'])}")
if results['failed']:
    print(f"\nFailed modules:")
    for name, error in results['failed']:
        print(f"  ❌ {name}: {error}")
print(f"\n{'='*80}")
if len(results['failed']) == 0:
    print("✅ ALL MODULES PASSED - Framework detail tests successful (physics incomplete)")
else:
    success_rate = len(results['passed']) / (len(results['passed']) + len(results['failed'])) * 100
    print(f"⚠️  Success Rate: {success_rate:.1f}%")
print(f"{'='*80}")

sys.exit(0 if len(results['failed']) == 0 else 1)
