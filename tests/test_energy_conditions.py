from beam_ssz.energy_conditions import CandidateClass, classify_energy_conditions


def test_nec_violation_is_gr_exotic():
    report = classify_energy_conditions(nec_satisfied=False)
    assert report.candidate_class == CandidateClass.GR_EXOTIC
    assert report.requires_exotic_matter


def test_warp_claim_rejected_even_with_nec():
    report = classify_energy_conditions(nec_satisfied=True, claims_warp_drive=True)
    assert report.candidate_class == CandidateClass.REJECTED


def test_effective_only_class():
    report = classify_energy_conditions(nec_satisfied=True, effective_only=True)
    assert report.candidate_class == CandidateClass.SSZ_EFFECTIVE_ONLY


def test_sec_violation_can_be_canonical_when_nec_ok():
    report = classify_energy_conditions(nec_satisfied=True, sec_satisfied=False)
    assert report.candidate_class == CandidateClass.SSZ_CANONICAL
