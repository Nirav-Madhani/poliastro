# coding: utf-8
import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal

from astropy import units as u

from poliastro.bodies import Earth
from poliastro.twobody import State

from poliastro.twobody.propagation import cowell

from poliastro.util import norm


def test_cowell_propagation_with_zero_acceleration_equals_kepler():
    # Data from Vallado, example 2.4
    k = Earth.k.to(u.km**3 / u.s**2).value

    r0 = np.array([1131.340, -2282.343, 6672.423])  # km
    v0 = np.array([-5.64305, 4.30333, 2.42879])  # km/s
    tof = 40 * 60.0  # s

    expected_r = np.array([-4219.7527, 4363.0292, -3958.7666])
    expected_v = np.array([3.689866, -1.916735, -6.112511])

    r, v = cowell(k, r0, v0, tof, None)

    assert_array_almost_equal(r, expected_r, decimal=1)
    assert_array_almost_equal(v, expected_v, decimal=4)


def test_cowell_propagation_circle_to_circle():
    # From [Edelbaum, 1961]
    accel = 1e-7

    def constant_accel(t0, u, k):
        v = u[3:]
        norm_v = (v[0]**2 + v[1]**2 + v[2]**2)**.5
        return accel * v / norm_v

    ss = State.circular(Earth, 500 * u.km)
    tof = 20 * ss.period

    r0, v0 = ss.rv()
    k = ss.attractor.k

    r, v = cowell(k.to(u.km**3 / u.s**2).value,
                  r0.to(u.km).value,
                  v0.to(u.km / u.s).value,
                  tof.to(u.s).value,
                  constant_accel)

    ss_final = State.from_vectors(Earth,
                                  r * u.km,
                                  v * u.km / u.s,
                                  ss.epoch + tof)

    da_a0 = (ss_final.a - ss.a) / ss.a
    dv_v0 = abs(norm(ss_final.v) - norm(ss.v)) / norm(ss.v)
    assert_almost_equal(da_a0.value, 2 * dv_v0.value, decimal=4)

    dv = abs(norm(ss_final.v) - norm(ss.v))
    accel_dt = accel * u.km / u.s**2 * tof
    assert_almost_equal(dv.value, accel_dt.value, decimal=4)