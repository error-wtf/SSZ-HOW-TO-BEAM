from beam_ssz.null_geodesics import dt_dr_null, flat_light_travel_time_x, light_travel_time_x


def test_null_dt_dr_exceeds_flat_coordinate_value():
    assert dt_dr_null(3.0, c=1.0) > 1.0
    assert dt_dr_null(1000.0, c=1.0) > 1.0


def test_light_travel_time_exceeds_flat_time():
    curved = light_travel_time_x(10.0, 100.0, c=1.0, steps=512)
    flat = flat_light_travel_time_x(10.0, 100.0, c=1.0)
    assert curved > flat
