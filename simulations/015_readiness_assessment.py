"""Real-Beam Readiness Assessment Demonstration.

Demonstrates the readiness scoring system for real-beaming research.
"""
import sys
sys.path.insert(0, 'src')

from beam_ssz.real_beam_readiness_score import RealBeamReadinessScorer, ReadinessLevel


def main():
    print("BEAM-SSZ v0.6 - Real-Beam Readiness Assessment")
    print("=" * 60)
    print("This is a STRICT assessment, not a marketing number.")
    print("=" * 60)
    
    # Assessment 1: Foundational only
    print("\n--- Assessment 1: Foundational Only ---")
    report1 = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.95,
        ssz_guardrails=0.90,
        no_go_compliance=0.95,
        energy_condition_status=0.85,
        causality_status=0.90,
        tidal_status=0.80,
        experimental_ladder_level=0,
        reproducibility_level=0.90,
    )
    
    print(f"Overall Level: {report1.overall_level.value}")
    print(f"Summary: {report1.summary}")
    print(f"Blockers: {report1.blockers if report1.blockers else 'None'}")
    print(f"Recommendations: {report1.recommendations if report1.recommendations else 'None'}")
    
    # Assessment 2: Photon test ready
    print("\n--- Assessment 2: Photon Test Ready ---")
    report2 = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.95,
        ssz_guardrails=0.95,
        no_go_compliance=0.95,
        energy_condition_status=0.90,
        causality_status=0.95,
        tidal_status=0.90,
        experimental_ladder_level=1,
        reproducibility_level=0.95,
    )
    
    print(f"Overall Level: {report2.overall_level.value}")
    print(f"Summary: {report2.summary}")
    
    # Assessment 3: Not ready (blockers)
    print("\n--- Assessment 3: Not Ready (with blockers) ---")
    report3 = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.70,  # FAIL
        ssz_guardrails=0.95,
        no_go_compliance=0.40,  # FAIL
        energy_condition_status=0.90,
        causality_status=0.95,
        tidal_status=0.90,
        experimental_ladder_level=2,
        reproducibility_level=0.95,
    )
    
    print(f"Overall Level: {report3.overall_level.value}")
    print(f"Summary: {report3.summary}")
    print(f"Blockers:")
    for blocker in report3.blockers:
        print(f"  - {blocker}")
    
    # Required scores comparison
    print("\n--- Required Scores by Level ---")
    levels = [
        ReadinessLevel.FOUNDATIONAL_ONLY,
        ReadinessLevel.PHOTON_TEST_READY,
        ReadinessLevel.ATOMIC_TEST_READY,
        ReadinessLevel.MESOSCOPIC_TEST_READY,
    ]
    
    for level in levels:
        required = RealBeamReadinessScorer.get_required_scores_for_level(level)
        print(f"\n{level.value}:")
        for axis, score in required.items():
            print(f"  {axis}: {score:.2f}")
    
    print("\n" + "=" * 60)
    print("Note: These are MINIMUM thresholds. Higher is better.")
    print("=" * 60)


if __name__ == "__main__":
    main()
