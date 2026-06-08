#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from beam_ssz.radial_scaling import coordinate_distance_x, rho_between_x, segmentation_excess_x


def main():
    """Demo: Radial scaling distance map across coordinate ranges."""
    for a, b in [(2.2, 10.0), (10.0, 100.0), (1.0, 2.0)]:
        coord = coordinate_distance_x(a, b)
        rho = rho_between_x(a, b, steps=1024)
        excess = segmentation_excess_x(a, b, steps=1024)
        print(f"x={a:.1f}->{b:.1f}: coord={coord:.6f} rho={rho:.6f} excess={excess:.6f}")


if __name__ == "__main__":
    main()
