#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from beam_ssz.null_geodesics import flat_light_travel_time_x, light_travel_time_x


def main():
    """Demo: Null travel time comparison between flat and SSZ."""
    curved = light_travel_time_x(10.0, 100.0, c=1.0, steps=2048)
    flat = flat_light_travel_time_x(10.0, 100.0, c=1.0)
    print(f"flat_time={flat:.9f}")
    print(f"ssz_null_time={curved:.9f}")
    print(f"delay={curved-flat:.9f}")


if __name__ == "__main__":
    main()
