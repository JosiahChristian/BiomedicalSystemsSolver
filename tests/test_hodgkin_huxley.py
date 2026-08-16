import unittest

import numpy as np

from biomedical_solver.hodgkin_huxley import (
    HodgkinHuxleyConfig,
    gating_rates,
    ionic_currents,
    simulate_hodgkin_huxley,
)


class HodgkinHuxleyTests(unittest.TestCase):
    def test_reference_temperature_has_unit_rate_scale(self) -> None:
        self.assertEqual(HodgkinHuxleyConfig().gating_rate_scale, 1.0)

    def test_q10_temperature_scaling(self) -> None:
        config = HodgkinHuxleyConfig(temperature_c=16.3, gating_q10=3.0)
        self.assertAlmostEqual(config.gating_rate_scale, 3.0)

    def test_rate_singularities_are_finite(self) -> None:
        for voltage in (-55.0, -40.0):
            self.assertTrue(np.isfinite(gating_rates(voltage)).all())

    def test_unstimulated_rest_is_stable(self) -> None:
        config = HodgkinHuxleyConfig(duration_ms=50.0)
        result = simulate_hodgkin_huxley(config, lambda _t: 0.0)
        self.assertLess(float(np.max(np.abs(result.voltage_mv + 65.0))), 0.02)

    def test_gating_probabilities_remain_bounded(self) -> None:
        result = simulate_hodgkin_huxley(HodgkinHuxleyConfig())
        for gate in (result.m, result.h, result.n):
            self.assertGreaterEqual(float(gate.min()), 0.0)
            self.assertLessEqual(float(gate.max()), 1.0)

    def test_standard_stimulus_evokes_action_potential(self) -> None:
        result = simulate_hodgkin_huxley(HodgkinHuxleyConfig())
        self.assertGreater(float(result.voltage_mv.max()), 20.0)
        self.assertLess(float(result.voltage_mv.min()), -70.0)
        upward_crossings = np.flatnonzero(
            (result.voltage_mv[:-1] < 0.0) & (result.voltage_mv[1:] >= 0.0)
        )
        self.assertGreaterEqual(len(upward_crossings), 1)

    def test_each_ionic_current_is_zero_at_its_reversal_potential(self) -> None:
        config = HodgkinHuxleyConfig()
        sodium, _, _ = ionic_currents(config.sodium_reversal_mv, 0.5, 0.5, 0.5, config)
        _, potassium, _ = ionic_currents(config.potassium_reversal_mv, 0.5, 0.5, 0.5, config)
        _, _, leak = ionic_currents(config.leak_reversal_mv, 0.5, 0.5, 0.5, config)
        self.assertAlmostEqual(sodium, 0.0)
        self.assertAlmostEqual(potassium, 0.0)
        self.assertAlmostEqual(leak, 0.0)

    def test_simulation_is_deterministic(self) -> None:
        config = HodgkinHuxleyConfig(duration_ms=5.0)
        first = simulate_hodgkin_huxley(config)
        second = simulate_hodgkin_huxley(config)
        np.testing.assert_array_equal(first.voltage_mv, second.voltage_mv)

    def test_peak_converges_when_time_step_is_halved(self) -> None:
        coarse = simulate_hodgkin_huxley(HodgkinHuxleyConfig(dt_ms=0.01))
        fine = simulate_hodgkin_huxley(HodgkinHuxleyConfig(dt_ms=0.005))
        coarse_peak = int(np.argmax(coarse.voltage_mv))
        fine_peak = int(np.argmax(fine.voltage_mv))
        self.assertLess(
            abs(coarse.voltage_mv[coarse_peak] - fine.voltage_mv[fine_peak]),
            0.01,
        )
        self.assertLessEqual(
            abs(coarse.time_ms[coarse_peak] - fine.time_ms[fine_peak]),
            0.01,
        )


if __name__ == "__main__":
    unittest.main()
