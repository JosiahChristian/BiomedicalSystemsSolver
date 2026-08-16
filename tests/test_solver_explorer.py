import tempfile
import unittest
from pathlib import Path

from experiments.export_solver_explorer import build_payload, export


class SolverExplorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build_payload()

    def test_payload_is_solver_identified_and_bounded(self):
        self.assertEqual(self.payload["schema"], "biomedical-solver-explorer/v1")
        self.assertEqual(len(self.payload["axon"]["voltage_mv"]), 401)
        self.assertEqual(len(self.payload["axon"]["voltage_mv"][0]), 101)
        self.assertEqual(len(self.payload["flow"]["velocity_cm_per_s"]), 201)
        self.assertGreater(self.payload["axon"]["peak_voltage_mv"], 30.0)
        self.assertAlmostEqual(self.payload["axon"]["conduction_velocity_m_per_s"], 18.742156, places=5)

    def test_export_is_standalone_and_discloses_model_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            export(output)
            html = output.read_text(encoding="utf-8")
        self.assertNotIn("__SOLVER_DATA__", html)
        self.assertIn("simulate_active_cable", html)
        self.assertIn("No vessel contraction is shown", html)
        self.assertNotIn("fetch(", html)


if __name__ == "__main__":
    unittest.main()
