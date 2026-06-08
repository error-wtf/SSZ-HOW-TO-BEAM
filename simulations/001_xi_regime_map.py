# Allow running this demo directly from the repository root without installation.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from beam_ssz.xi import evaluate_xi_x


def main():
    """Demo: Xi regime map across different x values."""
    for x in [1.0, 1.8, 2.0, 2.2, 3.0, 10.0, 100.0]:
        ev = evaluate_xi_x(x)
        print(f"x={x:6.2f} Xi={ev.xi:.9f} dXi/dx={ev.dxi_dx:.9f} regime={ev.regime.value} domain={ev.formula_domain}")


if __name__ == "__main__":
    main()
