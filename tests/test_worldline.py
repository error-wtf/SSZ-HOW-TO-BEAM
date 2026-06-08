from beam_ssz.worldline import WorldlineSegment, timelike_norm_ok


def test_worldline_positive_continuous_no_ctc():
    w = WorldlineSegment(0.0, 1.0, (0,0,0,0), (1,1,0,0))
    assert w.has_positive_proper_time()
    assert w.is_continuous()
    assert w.has_no_ctc_flag()


def test_worldline_negative_tau_fails():
    w = WorldlineSegment(1.0, 0.0, (0,0,0,0), (1,1,0,0))
    assert not w.has_positive_proper_time()


def test_timelike_norm_scaled():
    assert timelike_norm_ok(-1.0)
    assert not timelike_norm_ok(0.0)
