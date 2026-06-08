# Allow running this demo directly from the repository root without installation.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from beam_ssz.xi import evaluate_xi_x, xi_strong_x, xi_weak_x, dxi_strong_dx, dxi_weak_dx, d2xi_strong_dx2, d2xi_weak_dx2


def main():
    """Demo: Xi blend derivative continuity at boundaries."""
    for x, side in [(1.8, "strong boundary"), (2.2, "weak boundary")]:
        ev = evaluate_xi_x(x)
        print(side)
        print("blend", ev.xi, ev.dxi_dx, ev.d2xi_dx2)
        if x == 1.8:
            print("source", xi_strong_x(x), dxi_strong_dx(x), d2xi_strong_dx2(x))
        else:
            print("source", xi_weak_x(x), dxi_weak_dx(x), d2xi_weak_dx2(x))


if __name__ == "__main__":
    main()
