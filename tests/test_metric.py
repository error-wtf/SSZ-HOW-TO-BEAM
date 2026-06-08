from math import isclose

from beam_ssz.metric import SSZMetric


def test_metric_finite_at_rs():
    m = SSZMetric(x=1.0)
    comps = m.components()
    assert m.is_finite()
    assert comps["tt"] < 0
    assert comps["rr"] > 0


def test_metric_asymptotic_flatness_approx():
    m = SSZMetric(x=1e9)
    comps = m.components()
    assert isclose(comps["tt"], -1.0, rel_tol=1e-8)
    assert isclose(comps["rr"], 1.0, rel_tol=1e-8)
