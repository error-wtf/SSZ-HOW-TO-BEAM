from beam_ssz.bridge_candidate import BridgeCandidate
from beam_ssz.energy_conditions import CandidateClass, classify_energy_conditions
from beam_ssz.reports import render_candidate_report
from beam_ssz.validators import validate_candidate
from beam_ssz.worldline import WorldlineSegment


def make_candidate(**overrides):
    base = dict(
        candidate_id="test",
        effective_distance=1.0,
        normal_distance=10_000.0,
        max_tidal_delta_a=1.0,
        tidal_limit=10.0,
        worldline=WorldlineSegment(0.0, 1.0, (0,0,0,0), (1,1,0,0)),
        energy=classify_energy_conditions(nec_satisfied=True),
        singularity_flag=False,
    )
    base.update(overrides)
    return BridgeCandidate(**base)


def test_good_candidate_passes():
    c = make_candidate()
    report = validate_candidate(c)
    assert report.passed
    assert report.candidate_class == CandidateClass.SSZ_CANONICAL


def test_bad_compression_rejected():
    c = make_candidate(effective_distance=50.0)
    report = validate_candidate(c)
    assert not report.passed
    assert any("compressed" in f for f in report.failures)


def test_bad_energy_rejected():
    c = make_candidate(energy=classify_energy_conditions(nec_satisfied=False))
    report = validate_candidate(c)
    assert not report.passed
    assert report.candidate_class == CandidateClass.GR_EXOTIC


def test_report_renders():
    c = make_candidate()
    r = validate_candidate(c)
    text = render_candidate_report(c, r)
    assert "BEAM-SSZ Candidate Report" in text
    assert "PASS" in text
