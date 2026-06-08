# Allow running this demo directly from the repository root without installation.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from beam_ssz.worldline import WorldlineSegment


def main():
    """Demo: Worldline transfer toy example."""
    w = WorldlineSegment(0.0, 1.0, (0,0,0,0), (1,1,0,0))
    print("positive proper time:", w.has_positive_proper_time())
    print("continuous:", w.is_continuous())
    print("no CTC flag:", w.has_no_ctc_flag())


if __name__ == "__main__":
    main()
