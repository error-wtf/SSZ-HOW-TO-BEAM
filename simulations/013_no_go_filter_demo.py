"""No-Go Filter Demonstration.

Demonstrates the no-go theorem filters as mathematical consistency checks.
"""
import sys
sys.path.insert(0, 'src')

from beam_ssz.no_go_filters import NoGoFilters, NoGoFilterResult


def main():
    print("BEAM-SSZ v0.6 - No-Go Filter Demonstration")
    print("=" * 60)
    print("These are MATHEMATICAL filters, not moral prohibitions.")
    print("FAIL = mathematically/physically inconsistent.")
    print("=" * 60)
    
    # Test 1: Canonical SSZ candidate
    print("\n--- Test 1: Canonical SSZ (should PASS) ---")
    reports = NoGoFilters.run_all_filters(
        scan_copy_model=False,
        unknown_quantum_state_copy=False,
        claim_human_identity=False,
        destructive=False,
        superluminal_signal=False,
        nec_violation=False,
        claimed_classification="SSZ_CANONICAL",
        biological_experiment=False,
    )
    
    for r in reports:
        status = "✓" if r.result == NoGoFilterResult.PASS else "✗"
        print(f"  {status} {r.filter_name:<25} {r.result.value}")
    
    overall = NoGoFilters.get_overall_result(reports)
    print(f"  Overall: {overall.value}")
    
    # Test 2: Scan/copy model claiming human identity
    print("\n--- Test 2: Scan/Copy + Human Identity (should FAIL) ---")
    reports = NoGoFilters.run_all_filters(
        scan_copy_model=True,
        unknown_quantum_state_copy=False,
        claim_human_identity=True,
        destructive=False,
        superluminal_signal=False,
        nec_violation=False,
        claimed_classification="SSZ_CANONICAL",
        biological_experiment=False,
    )
    
    for r in reports:
        status = "✓" if r.result == NoGoFilterResult.PASS else "✗"
        print(f"  {status} {r.filter_name:<25} {r.result.value}")
        if r.result == NoGoFilterResult.FAIL:
            print(f"      → {r.details}")
    
    overall = NoGoFilters.get_overall_result(reports)
    print(f"  Overall: {overall.value}")
    
    # Test 3: Biological experiment without validation
    print("\n--- Test 3: Biological Experiment (should FAIL) ---")
    reports = NoGoFilters.run_all_filters(
        scan_copy_model=False,
        unknown_quantum_state_copy=False,
        claim_human_identity=False,
        destructive=False,
        superluminal_signal=False,
        nec_violation=False,
        claimed_classification="SSZ_CANONICAL",
        biological_experiment=True,
        current_readiness_level="PHOTON_TEST_READY",
    )
    
    for r in reports:
        status = "✓" if r.result == NoGoFilterResult.PASS else "✗"
        print(f"  {status} {r.filter_name:<25} {r.result.value}")
        if r.result == NoGoFilterResult.FAIL:
            print(f"      → {r.details}")
    
    overall = NoGoFilters.get_overall_result(reports)
    print(f"  Overall: {overall.value}")
    
    print("\n" + "=" * 60)
    print("Conclusion: No-go filters enforce mathematical consistency.")
    print("They do not forbid research - they classify candidates.")
    print("=" * 60)


if __name__ == "__main__":
    main()
