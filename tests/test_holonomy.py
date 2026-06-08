from beam_ssz.holonomy import closed_loop_invariant, edge_modulated_loop_invariant, frequency_ratio_x


def test_static_closed_loop_holonomy_telescopes_to_one():
    invariant = closed_loop_invariant([2.0, 3.0, 5.0, 8.0])
    assert abs(invariant - 1.0) < 1e-12


def test_frequency_ratios_are_reciprocal():
    ab = frequency_ratio_x(2.0, 5.0)
    ba = frequency_ratio_x(5.0, 2.0)
    assert abs(ab * ba - 1.0) < 1e-12


def test_edge_modulated_loop_detects_dynamic_path_effect():
    invariant = edge_modulated_loop_invariant([2.0, 3.0, 5.0], [1.001, 1.0, 1.0])
    assert invariant > 1.0
