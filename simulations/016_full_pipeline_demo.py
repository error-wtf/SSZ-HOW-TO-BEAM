"""Full Pipeline Demonstration - Integration Test.

Demonstrates the complete BEAM-SSZ pipeline from bridge candidate
to classification and readiness assessment.
"""
import sys
sys.path.insert(0, 'src')

from beam_ssz.bridge_metric import SSZBridgeMetric
from beam_ssz.candidate_classifier import CandidateClassifier, CandidateClass
from beam_ssz.no_go_filters import NoGoFilters
from beam_ssz.real_beam_readiness_score import RealBeamReadinessScorer


def main():
    print("BEAM-SSZ v0.6 - Full Pipeline Demonstration")
    print("=" * 70)
    print("Complete workflow: Bridge Metric → Classification → Readiness")
    print("=" * 70)
    
    # Step 1: Create bridge candidate
    print("\n[STEP 1] Creating Bridge Candidate")
    print("-" * 70)
    
    bridge = SSZBridgeMetric(
        xi_left=0.15,
        xi_right=0.15,
        lambda_bridge=0.8,
        ell0=5e-4,
        throat_radius=5e-3,
    )
    
    print(f"Parameters:")
    print(f"  Ξ_A = {bridge.xi_left}")
    print(f"  Ξ_B = {bridge.xi_right}")
    print(f"  λ = {bridge.lambda_bridge}")
    print(f"  ℓ₀ = {bridge.ell0:.3e} m")
    print(f"  R₀ = {bridge.throat_radius:.3e} m")
    
    # Step 2: Evaluate bridge
    print("\n[STEP 2] Bridge Evaluation")
    print("-" * 70)
    
    l_normal = 1.0  # 1 meter
    eval_result = bridge.evaluate_candidate(l_normal)
    
    print(f"Regular: {eval_result.is_regular}")
    print(f"Worldline OK: {eval_result.worldline_norm_ok}")
    print(f"Causality OK: {eval_result.causality_ok}")
    print(f"Distance ratio η: {eval_result.distance_ratio:.6e}")
    print(f"Tidal proxy: {eval_result.tidal_proxy:.3e} m/s²")
    print(f"Energy class: {eval_result.energy_class}")
    
    # Step 3: Classify candidate
    print("\n[STEP 3] Candidate Classification")
    print("-" * 70)
    
    from beam_ssz.metric_bridge import BridgeParameters
    params = BridgeParameters(
        alpha=0.5,
        lambda_segment=0.8,
        k_min=0.01,
        k_max=1.0,
    )
    
    # Create a mock BridgeCandidate (simplified for demo)
    class MockBridgeCandidate:
        def __init__(self):
            self.L_eff = bridge.bridge_distance()
            self.L_coordinate = l_normal
            self.reduction_factor = self.L_eff / self.L_coordinate
            self.tidal_max = eval_result.tidal_proxy
            self.ctc_flag = not eval_result.causality_ok
            self.singularity_flag = not eval_result.is_regular
            self.worldline_continuous = eval_result.worldline_norm_ok
    
    candidate = MockBridgeCandidate()
    
    report = CandidateClassifier.classify(
        candidate,
        requires_nec_violation=eval_result.energy_class in ["GR_EXOTIC", "SSZ_EXTENSION"],
        is_toy_model=False,
        candidate_id="demo_candidate_001",
    )
    
    print(f"Candidate ID: {report.candidate_id}")
    print(f"Class: {report.candidate_class.value}")
    print(f"Canonical: {report.canonical}")
    print(f"NEC satisfied: {report.nec_satisfied}")
    print(f"CTC-free: {report.ctc_free}")
    print(f"Singularity-free: {report.singularity_free}")
    print(f"Worldline continuous: {report.worldline_continuous}")
    print(f"Tidal safe: {report.tidal_safe}")
    print(f"Reduction significant: {report.reduction_significant}")
    print(f"Reasons:")
    for reason in report.reasons:
        print(f"  • {reason}")
    
    # Step 4: No-go filter check
    print("\n[STEP 4] No-Go Filter Analysis")
    print("-" * 70)
    
    no_go_reports = NoGoFilters.run_all_filters(
        scan_copy_model=False,
        unknown_quantum_state_copy=False,
        claim_human_identity=False,
        destructive=False,
        superluminal_signal=False,
        nec_violation=not report.nec_satisfied,
        claimed_classification=report.candidate_class.value,
        biological_experiment=False,
    )
    
    print("Filter Results:")
    for r in no_go_reports:
        symbol = "✓" if r.result.value == "PASS" else "⚠" if r.result.value == "WARNING" else "✗"
        print(f"  {symbol} {r.filter_name:<30} {r.result.value}")
    
    overall_no_go = NoGoFilters.get_overall_result(no_go_reports)
    print(f"\nOverall No-Go Result: {overall_no_go.value}")
    
    # Step 5: Readiness assessment
    print("\n[STEP 5] Real-Beam Readiness Assessment")
    print("-" * 70)
    
    readiness = RealBeamReadinessScorer.assess_readiness(
        math_consistency=0.95 if eval_result.is_regular else 0.5,
        ssz_guardrails=0.95,
        no_go_compliance=0.95 if overall_no_go.value == "PASS" else 0.5,
        energy_condition_status=0.90 if report.nec_satisfied else 0.70,
        causality_status=0.95 if eval_result.causality_ok else 0.5,
        tidal_status=0.90 if report.tidal_safe else 0.6,
        experimental_ladder_level=1,  # Photon test ready
        reproducibility_level=0.90,
    )
    
    print(f"Overall Level: {readiness.overall_level.value}")
    print(f"Summary: {readiness.summary}")
    
    print("\nAxis Scores:")
    for name, axis in readiness.axes.items():
        print(f"  {name:<25} {axis.score:.2f} ({axis.status})")
    
    if readiness.blockers:
        print(f"\nBlockers:")
        for blocker in readiness.blockers:
            print(f"  ⚠ {blocker}")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("[FINAL SUMMARY]")
    print("=" * 70)
    print(f"Bridge Candidate: {'PASS' if eval_result.is_regular else 'FAIL'}")
    print(f"Classification: {report.candidate_class.value}")
    print(f"No-Go Compliance: {overall_no_go.value}")
    print(f"Readiness Level: {readiness.overall_level.value}")
    print(f"Distance Reduction: η = {eval_result.distance_ratio:.6e}")
    print(f"\nConclusion:")
    if (readiness.overall_level.value != "NOT_READY" and 
        overall_no_go.value == "PASS" and
        report.candidate_class != CandidateClass.INCONSISTENT):
        print("  ✓ This candidate passes all pipeline stages.")
        print("  → Ready for next level of testing.")
    else:
        print("  ✗ This candidate has issues that must be resolved.")
        print("  → See blockers and warnings above.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
