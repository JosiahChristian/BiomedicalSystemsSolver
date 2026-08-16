import unittest

import numpy as np

from biomedical_solver.neuro import PassiveCableConfig, simulate_passive_cable


class PassiveCableBaselineTests(unittest.TestCase):
    def test_rejects_unstable_explicit_step(self) -> None:
        with self.assertRaisesRegex(ValueError, "unstable"):
            simulate_passive_cable(PassiveCableConfig(dt_ms=0.1))

    def test_resting_state_is_preserved_without_stimulus(self) -> None:
        config = PassiveCableConfig(duration_ms=1.0)
        result = simulate_passive_cable(config, stimulus_mv_per_ms=lambda _t: 0.0)
        np.testing.assert_allclose(result.voltage_mv, config.resting_potential_mv)

    def test_transient_stimulus_depolarizes_proximal_cable(self) -> None:
        config = PassiveCableConfig(duration_ms=5.0)
        result = simulate_passive_cable(config)
        self.assertGreater(
            float(result.voltage_mv[:, 0].max()),
            config.resting_potential_mv + 1.0,
        )
        self.assertGreater(float(result.voltage_mv[-1, 1]), config.resting_potential_mv)

    def test_solution_is_finite_and_bounded(self) -> None:
        result = simulate_passive_cable(PassiveCableConfig(duration_ms=5.0))
        self.assertTrue(np.isfinite(result.voltage_mv).all())
        self.assertGreaterEqual(float(result.voltage_mv.min()), -70.0)
        self.assertLess(float(result.voltage_mv.max()), 40.0)


if __name__ == "__main__":
    unittest.main()
