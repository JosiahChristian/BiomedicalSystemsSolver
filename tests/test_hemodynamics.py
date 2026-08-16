import unittest

import numpy as np

from biomedical_solver.hemodynamics import HemodynamicConfig, constant_inlet, simulate_hemodynamics


class HemodynamicBaselineTests(unittest.TestCase):
    def test_rejects_unstable_explicit_step(self) -> None:
        with self.assertRaisesRegex(ValueError, "unstable"):
            simulate_hemodynamics(HemodynamicConfig(num_nodes=101, dt_s=1.0))

    def test_uniform_field_is_preserved(self) -> None:
        result = simulate_hemodynamics(
            HemodynamicConfig(duration_s=0.1),
            inlet_velocity=constant_inlet(12.5),
            initial_velocity_cm_per_s=12.5,
        )
        np.testing.assert_allclose(result.velocity_cm_per_s, 12.5, atol=1e-12)

    def test_zero_gradient_outlet_is_enforced(self) -> None:
        result = simulate_hemodynamics(HemodynamicConfig(duration_s=0.1))
        np.testing.assert_allclose(result.velocity_cm_per_s[:, -1], result.velocity_cm_per_s[:, -2])

    def test_velocity_remains_bounded_by_boundary_data(self) -> None:
        result = simulate_hemodynamics(HemodynamicConfig(duration_s=0.1))
        self.assertGreaterEqual(float(result.velocity_cm_per_s.min()), 0.0)
        self.assertLessEqual(float(result.velocity_cm_per_s.max()), 30.0)


if __name__ == "__main__":
    unittest.main()
