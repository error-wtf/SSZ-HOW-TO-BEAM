#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from beam_ssz.geodesics import radial_freefall_velocity
from beam_ssz.geodesic_deviation import radial_tidal_acceleration_proxy


def main():
    """Demo: Geodesic corridor scan across x values."""
    for x in [1.0, 1.5, 2.0, 3.0, 10.0]:
        v = radial_freefall_velocity(x, c=1.0)
        tidal = radial_tidal_acceleration_proxy(x, separation=1.0)
        print(f"x={x:4.1f} v_fall/c={v:.6f} tidal_proxy={tidal:.6e}")


if __name__ == "__main__":
    main()
