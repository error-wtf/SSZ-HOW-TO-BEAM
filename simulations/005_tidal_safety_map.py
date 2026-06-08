# Allow running this demo directly from the repository root without installation.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from beam_ssz.tidal import evaluate_tidal_safety


def main():
    """Demo: Tidal safety map across curvature values."""
    for curvature in [1e-9, 1e-6, 1e-3]:
        safety = evaluate_tidal_safety(curvature, body_length=2.0, limit=10.0)
        print(curvature, safety.max_delta_a, safety.passes)


if __name__ == "__main__":
    main()
