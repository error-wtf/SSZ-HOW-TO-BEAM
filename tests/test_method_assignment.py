import pytest

from beam_ssz.method_assignment import Method, assert_method, assign_method
from beam_ssz.observables import ObservableType


def test_null_light_requires_ppn():
    assert assign_method(ObservableType.NULL_LIGHT).method == Method.PPN
    with pytest.raises(ValueError):
        assert_method(ObservableType.NULL_LIGHT, Method.XI_DIRECT)


def test_worldline_transfer_method():
    assert assign_method(ObservableType.TIMELIKE_WORLDLINE_TRANSFER).method == Method.SSZ_METRIC_WORLDLINE
