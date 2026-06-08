# Allow running this demo directly from the repository root without installation.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from beam_ssz.metric import SSZMetric


def main():
    """Demo: Metric component scan across x values."""
    for x in [1.0, 1.5, 2.0, 3.0, 10.0]:
        m = SSZMetric(x=x)
        print(x, m.components(), "finite=", m.is_finite())


if __name__ == "__main__":
    main()
