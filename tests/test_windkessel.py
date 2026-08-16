import unittest

import numpy as np

from biomedical_solver.windkessel import WindkesselConfig, pulsatile_inflow, simulate_windkessel


class WindkesselTests(unittest.TestCase):
    def test_default_cycle_has_physiologic_illustrative_bounds(self) -> None:
        result = simulate_windkessel()
        self.assertGreater(result.systolic_mmhg, 115.0)
        self.assertLess(result.systolic_mmhg, 130.0)
        self.assertGreater(result.diastolic_mmhg, 70.0)
        self.assertLess(result.diastolic_mmhg, 85.0)
        self.assertGreater(result.systolic_mmhg - result.diastolic_mmhg, 35.0)

    def test_inflow_is_nonnegative_and_mean_normalized(self) -> None:
        config = WindkesselConfig()
        flow = pulsatile_inflow(config)
        samples = np.array([flow(t) for t in np.linspace(0, config.period_s, 10001, endpoint=False)])
        self.assertGreaterEqual(float(samples.min()), 0.0)
        self.assertAlmostEqual(float(samples.mean()), config.mean_flow_ml_per_s, places=2)

    def test_constant_flow_converges_to_analytic_equilibrium(self) -> None:
        config = WindkesselConfig(cycles=20)
        flow = 60.0
        result = simulate_windkessel(config, inflow=lambda _time: flow)
        expected = config.venous_pressure_mmhg + config.resistance_mmhg_s_per_ml * flow
        self.assertAlmostEqual(result.pressure_mmhg[-1], expected, places=2)

    def test_rejects_unstable_time_step(self) -> None:
        with self.assertRaisesRegex(ValueError, "time step"):
            simulate_windkessel(WindkesselConfig(dt_s=1.0))


if __name__ == "__main__":
    unittest.main()
