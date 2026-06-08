from beam_ssz.tidal import evaluate_tidal_safety, tidal_acceleration_proxy


def test_tidal_proxy_abs():
    assert tidal_acceleration_proxy(-2.0, 3.0) == 6.0


def test_tidal_safety_pass_fail():
    assert evaluate_tidal_safety(2.0, 3.0, 7.0).passes
    assert not evaluate_tidal_safety(2.0, 3.0, 5.0).passes
