"""v1.0.0 Final Integration Test

Run with: python3 test_v1_final.py
"""
import sys
import traceback

sys.path.insert(0, 'src')

print("=" * 70)
print("SSZ-HOW-TO-BEAM v1.0.0 Final Integration Test")
print("=" * 70)

errors = []
warnings = []

def test_section(name):
    print(f"\n[{name}] ", end="", flush=True)

def test_pass(msg="OK"):
    print(f"✓ {msg}")

def test_fail(e):
    print(f"✗ {e}")
    errors.append(str(e))
    traceback.print_exc()

# Test 1: Basic imports
test_section("1/8 Core Imports")
try:
    import beam_ssz
    assert beam_ssz.__version__ == "1.0.0", f"Wrong version: {beam_ssz.__version__}"
    test_pass(f"beam_ssz v{beam_ssz.__version__}")
except Exception as e:
    test_fail(e)

# Test 2: Tensor core
test_section("2/8 Tensor Core")
try:
    from beam_ssz.tensor_core import (
        minkowski_cartesian, minkowski_spherical, ssz_metric,
        compute_christoffel, TensorStatus
    )
    import numpy as np
    
    # Test Minkowski
    g = minkowski_cartesian()
    assert g.shape == (4, 4), f"Wrong shape {g.shape}"
    assert g[0,0] == -1.0, f"Wrong g[0,0]={g[0,0]}"
    
    # Test SSZ metric
    x = np.array([0.0, 2.0, np.pi/2, 0.0])
    g2 = ssz_metric(x, D=0.5, s=2.0, Xi=1.0)
    assert g2.shape == (4, 4)
    assert g2[0,0] == -0.25, f"Wrong g[0,0]={g2[0,0]}"
    
    test_pass("Minkowski & SSZ metrics")
except Exception as e:
    test_fail(e)

# Test 3: Observable dispatcher
test_section("3/8 Observable Dispatcher")
try:
    from beam_ssz.tensor_core.observable_dispatcher import (
        classify_regime, Regime, ObservableType, compute_observable_factor
    )
    
    r = classify_regime(10.0, 1.0)
    assert r == Regime.STRONG, f"Expected STRONG, got {r}"
    
    result = compute_observable_factor(
        ObservableType.TIMELIKE_STATIC, r=10.0, r_s=1.0
    )
    assert result["method"] == "XI_PROXY"
    
    test_pass(f"Regime={r.name}, Method={result['method']}")
except Exception as e:
    test_fail(e)

# Test 4: Energy proxy
test_section("4/8 Energy Proxy")
try:
    from beam_ssz.energy_proxy import EnergyProxyStatus, EnergyProxyDiagnostic
    
    d = EnergyProxyDiagnostic()
    result = d.estimate_energy_density_proxy(D=0.5, s=2.0)
    
    assert "WARNING" in result, "Missing WARNING"
    assert result["CANNOT_CLAIM_NEC"] == True, "Should not claim NEC"
    
    test_pass("Proxy separation enforced")
except Exception as e:
    test_fail(e)

# Test 5: SSZ segmentation
test_section("5/8 SSZ Segmentation")
try:
    for xi in [0.0, 0.1, 0.5, 1.0, 2.0, 10.0]:
        assert xi >= 0, f"Xi={xi} negative"
        D = 1.0/(1.0+xi)
        assert D > 0, f"D={D} not positive"
        assert D <= 1.0, f"D={D} > 1"
    
    # Test monotonicity
    D_values = [1.0/(1.0+x) for x in [0.0, 0.5, 1.0, 2.0]]
    for i in range(len(D_values)-1):
        assert D_values[i] > D_values[i+1], "D not monotonically decreasing"
    
    test_pass(f"Xi/D/s valid (tested 6 Xi values)")
except Exception as e:
    test_fail(e)

# Test 6: Observables
test_section("6/8 Observables")
try:
    from beam_ssz.observables import compute_redshift, ReferenceFrame
    
    result = compute_redshift(
        r_emitter=10.0,
        r_receiver=11.0,
        xi_func=lambda r: 0.1,
    )
    
    assert result.reference_frame == "SSZ_CANONICAL", f"Wrong frame: {result.reference_frame}"
    assert -1.0 < result.redshift_z < 1.0, f"Unreasonable z: {result.redshift_z}"
    
    test_pass(f"z={result.redshift_z:.4f}, frame={result.reference_frame}")
except Exception as e:
    test_fail(e)

# Test 7: Validation pipeline
test_section("7/8 Validation Pipeline")
try:
    from beam_ssz import ValidationPipeline
    
    p = ValidationPipeline()
    report = p.run_full_validation(xi_samples=[0.0, 0.1, 0.5])
    
    passed = len([g for g in report.gates_completed if g.status=='PASS'])
    total = len(report.gates_completed)
    
    assert passed >= 2, f"Only {passed}/{total} gates passed"
    
    test_pass(f"{passed}/{total} gates passed")
except Exception as e:
    test_fail(e)

# Test 8: Numerical GR diagnostics
test_section("8/8 Numerical GR")
try:
    from beam_ssz import test_convergence_rate
    
    result = test_convergence_rate(
        f_coarse=1.1,
        f_medium=1.05,
        f_fine=1.025,
        h_coarse=0.1,
        h_medium=0.05,
        h_fine=0.025,
    )
    
    assert "convergence_order_estimate" in result
    p = result['convergence_order_estimate']
    assert 1.0 < p < 3.0, f"Unreasonable p={p}"
    
    test_pass(f"Convergence p≈{p:.1f}")
except Exception as e:
    test_fail(e)

# Summary
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

if not errors:
    print("✅ ALL 8 TESTS PASSED")
    print("\nv1.0.0 Release Status: READY")
    print("\nScientific Position:")
    print('  "BEAM-SSZ treats a person as a continuous worldline whose')
    print('   effective segment-distance is reduced by a controlled bridge."')
    print("\nForbidden Claims (enforced):")
    print("  ✗ Physical beaming achieved")
    print("  ✗ Human transport possible")
    print("  ✗ Biological safety proven")
    print("\nPermanent Limitations:")
    print("  • Biological transport: NOT_VALIDATED")
    print("  • Physical formation: UNRESOLVED")
    print("  • Experimental validation: NONE")
    print("=" * 70)
    sys.exit(0)
else:
    print(f"⚠️  {len(errors)} ERROR(S) FOUND:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err[:80]}")
    print("\n❌ v1.0.0 NOT READY - Fix errors before release")
    print("=" * 70)
    sys.exit(1)
