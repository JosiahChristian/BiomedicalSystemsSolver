import tempfile
import unittest
import json
from pathlib import Path

from experiments.export_solver_explorer import build_payload, build_telemetry_payload, export


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
            telemetry = Path(directory) / "telemetry.json"
            export(output, telemetry)
            html = output.read_text(encoding="utf-8")
            self.assertTrue(telemetry.exists())
        self.assertNotIn("__SOLVER_DATA__", html)
        self.assertIn("simulate_active_cable", html)
        self.assertIn("No vessel contraction is shown", html)
        self.assertNotIn("fetch(", html)

    def test_compact_telemetry_payload_preserves_provenance(self):
        payload = build_telemetry_payload()
        self.assertEqual(payload["schema"], "biomedical-telemetry-playback/v1")
        self.assertEqual(len(payload["axon"]["voltage_mv"]), 401)
        self.assertEqual(len(payload["flow"]["velocity_cm_per_s"]), 201)
        self.assertIn("simulate_active_cable", payload["provenance"]["axon_solver"])

    def test_compact_telemetry_contains_a_live_proximal_flow_trace(self):
        flow = build_telemetry_payload()["flow"]
        velocities = flow["velocity_cm_per_s"]
        self.assertEqual(flow["position_cm"], 0.1)
        self.assertGreater(min(velocities), 0.0)
        self.assertGreater(max(velocities) - min(velocities), 5.0)

    def test_compact_telemetry_contains_reduced_order_pressure(self):
        pressure = build_telemetry_payload()["pressure"]
        self.assertGreater(pressure["systolic_mmhg"], pressure["diastolic_mmhg"])
        self.assertGreater(len(pressure["pressure_mmhg"]), 100)
        self.assertIn("Windkessel", pressure["model"])

    def test_published_schema_tracks_required_playback_channels(self):
        schema_path = Path(__file__).resolve().parents[1] / "docs" / "telemetry-playback.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema"]["const"], "biomedical-telemetry-playback/v1")
        self.assertEqual(set(schema["required"]), {"schema", "source", "provenance", "axon", "flow", "pressure"})


if __name__ == "__main__":
    unittest.main()
