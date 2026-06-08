#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from beam_ssz.holonomy import closed_loop_invariant, edge_modulated_loop_invariant


def main():
    """Demo: Bridge holonomy calculation."""
    xs = [2.0, 3.0, 5.0, 8.0]
    print(f"static_loop={closed_loop_invariant(xs):.15f}")
    print(f"edge_modulated_loop={edge_modulated_loop_invariant(xs, [1.001, 1.0, 1.0, 0.999]):.15f}")


if __name__ == "__main__":
    main()
