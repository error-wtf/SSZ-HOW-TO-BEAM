# Allow running this demo directly from the repository root without installation.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from beam_ssz.bridge_candidate import BridgeCandidate
from beam_ssz.energy_conditions import classify_energy_conditions
from beam_ssz.reports import render_candidate_report
from beam_ssz.validators import validate_candidate
from beam_ssz.worldline import WorldlineSegment


def main():
    """Demo: Candidate rejection based on no-go filters."""
    candidate = BridgeCandidate(
        candidate_id="demo-pass-effective",
        effective_distance=1.0,
        normal_distance=10_000.0,
        max_tidal_delta_a=1.0,
        tidal_limit=10.0,
        worldline=WorldlineSegment(0.0, 1.0, (0,0,0,0), (1,1,0,0)),
        energy=classify_energy_conditions(nec_satisfied=True, sec_satisfied=False, effective_only=True),
    )
    report = validate_candidate(candidate)
    print(render_candidate_report(candidate, report))

    bad = BridgeCandidate(
        candidate_id="demo-reject-warp",
        effective_distance=1.0,
        normal_distance=10_000.0,
        max_tidal_delta_a=1.0,
        tidal_limit=10.0,
        worldline=WorldlineSegment(0.0, 1.0, (0,0,0,0), (1,1,0,0)),
        energy=classify_energy_conditions(nec_satisfied=True, claims_warp_drive=True),
    )
    print(render_candidate_report(bad, validate_candidate(bad)))


if __name__ == "__main__":
    main()
