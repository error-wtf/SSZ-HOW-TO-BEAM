"""Experimental Xi Formulas Playground.

Demonstrates testing of alternative Xi formulas against canonical SSZ.
"""
import sys
sys.path.insert(0, 'src')

from beam_ssz.experimental_xi import (
    compare_against_canonical,
    xi_deprecated_test_only,
    xi_power_exp_test_only,
    FormulaStatus,
)


def main():
    print("BEAM-SSZ v0.6 - Experimental Xi Formulas Playground")
    print("=" * 60)
    print("WARNING: Non-canonical formulas must be explicitly labeled!")
    print("=" * 60)
    
    x_test = 2.0  # r/rs = 2.0
    
    # Test 1: Deprecated formula (FORBIDDEN)
    print(f"\n--- Test 1: Deprecated Formula (x = {x_test}) ---")
    result = compare_against_canonical(
        x_test,
        lambda x: xi_deprecated_test_only(x, r_phi=1.0),
        "deprecated_power_exp",
        FormulaStatus.DEPRECATED_TEST_ONLY,
    )
    
    print(f"Formula: Ξ = (r_s/r)² exp(-r/r_φ)")
    print(f"Status: {result.status.value}")
    print(f"Xi (deprecated): {result.xi:.6f}")
    print(f"Xi (canonical):  {result.canonical_xi:.6f}")
    print(f"Difference:      {result.difference:.6f}")
    print(f"Relative diff:   {result.relative_difference:.2%}")
    print(f"Warnings: {result.warnings}")
    
    # Test 2: Power-exponential toy model
    print(f"\n--- Test 2: Power-Exponential Toy (x = {x_test}) ---")
    result = compare_against_canonical(
        x_test,
        lambda x: xi_power_exp_test_only(x, alpha=1.0, beta=0.5),
        "power_exp_alpha1_beta05",
        FormulaStatus.TOY_MODEL,
    )
    
    print(f"Formula: Ξ = x^(-α) exp(-βx), α=1, β=0.5")
    print(f"Status: {result.status.value}")
    print(f"Xi (toy):        {result.xi:.6f}")
    print(f"Xi (canonical):  {result.canonical_xi:.6f}")
    print(f"Difference:      {result.difference:.6f}")
    print(f"Relative diff:   {result.relative_difference:.2%}")
    
    # Test 3: Comparison across multiple x values
    print(f"\n--- Test 3: Comparison Across x Values ---")
    print(f"{'x':<8} {'Canonical':<12} {'Deprecated':<12} {'Toy':<12} {'Dep.Diff%':<12}")
    print("-" * 60)
    
    for x in [1.0, 1.5, 2.0, 3.0, 5.0, 10.0]:
        from beam_ssz.xi import evaluate_xi_x
        canonical = evaluate_xi_x(x).xi
        deprecated = xi_deprecated_test_only(x)
        toy = xi_power_exp_test_only(x, 1.0, 0.5)
        dep_diff = (deprecated - canonical) / canonical * 100 if canonical != 0 else float('inf')
        
        print(f"{x:<8.1f} {canonical:<12.6f} {deprecated:<12.6f} {toy:<12.6f} {dep_diff:<12.1f}")
    
    print("\n" + "=" * 60)
    print("Note: Deprecated formula deviates significantly from canonical SSZ.")
    print("It is FORBIDDEN in all canonical SSZ calculations.")
    print("=" * 60)


if __name__ == "__main__":
    main()
