import unittest

import numpy as np

from biomedical_solver.active_cable import ActiveCableConfig, simulate_active_cable


class ActiveCableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = ActiveCableConfig()
        cls.result = simulate_active_cable(cls.config)

    def test_rejects_unstable_spatial_step(self) -> None:
        with self.assertRaisesRegex(ValueError, "unstable"):
            simulate_active_cable(ActiveCableConfig(num_nodes=201, dt_ms=0.01))

    def test_action_potential_reaches_entire_axon(self) -> None:
        activation = self.result.activation_times_ms()
        self.assertTrue(np.isfinite(activation).all())
        self.assertGreater(float(self.result.voltage_mv.max()), 20.0)

    def test_activation_advances_in_spatial_order_beyond_stimulus(self) -> None:
        activation = self.result.activation_times_ms()
        beyond_stimulus = self.result.x_cm > self.config.stimulus_length_cm
        self.assertTrue(np.all(np.diff(activation[beyond_stimulus]) > 0.0))

    def test_emergent_conduction_velocity_is_finite_and_plausible(self) -> None:
        velocity = self.result.conduction_velocity_m_per_s()
        self.assertTrue(np.isfinite(velocity))
        self.assertGreater(velocity, 5.0)
        self.assertLess(velocity, 30.0)

    def test_conduction_velocity_reproduces_published_calculation(self) -> None:
        self.assertAlmostEqual(
            self.result.conduction_velocity_m_per_s(), 18.8, delta=0.2
        )

    def test_propagation_temperature_is_explicit(self) -> None:
        self.assertEqual(self.config.membrane.temperature_c, 18.5)
        self.assertGreater(self.config.membrane.gating_rate_scale, 1.0)

    def test_gating_probabilities_remain_bounded(self) -> None:
        for gate in (self.result.m, self.result.h, self.result.n):
            self.assertGreaterEqual(float(gate.min()), 0.0)
            self.assertLessEqual(float(gate.max()), 1.0)

    def test_no_stimulus_preserves_spatial_quiescence(self) -> None:
        result = simulate_active_cable(
            ActiveCableConfig(duration_ms=2.0, stimulus_amplitude_ua_per_cm2=0.0)
        )
        spatial_range = np.ptp(result.voltage_mv, axis=1)
        np.testing.assert_allclose(spatial_range, 0.0, atol=1e-12)
        self.assertTrue(np.isnan(result.activation_times_ms()).all())

    def test_conduction_velocity_converges_under_time_refinement(self) -> None:
        refined = simulate_active_cable(ActiveCableConfig(dt_ms=0.0005))
        self.assertAlmostEqual(
            self.result.conduction_velocity_m_per_s(),
            refined.conduction_velocity_m_per_s(),
            delta=0.01,
        )


if __name__ == "__main__":
    unittest.main()
