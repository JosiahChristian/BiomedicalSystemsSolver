import json
from pathlib import Path
import unittest

from biomedical_solver.hodgkin_huxley import HodgkinHuxleyConfig, square_current
from experiments.hh_1952_reference import run_reference_experiment


REFERENCE_PATH = Path(__file__).parents[1] / "references" / "hodgkin_huxley_1952.json"


class HodgkinHuxleyReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))

    def test_doi_and_pinned_executable_reference_are_recorded(self) -> None:
        self.assertEqual(
            self.reference["primary_publication"]["doi"],
            "10.1113/jphysiol.1952.sp004764",
        )
        self.assertEqual(
            len(self.reference["executable_reference"]["revision"]), 40
        )

    def test_configuration_matches_reference_parameters(self) -> None:
        expected = self.reference["modern_absolute_voltage_parameters"]
        config = HodgkinHuxleyConfig(**expected)
        for name, value in expected.items():
            self.assertEqual(getattr(config, name), value)

    def test_original_to_modern_voltage_conversion(self) -> None:
        conversion = self.reference["sign_and_offset_conversion"]
        pairs = (
            (conversion["original_initial_voltage_mv"], -65.0),
            (conversion["original_sodium_reversal_mv"], 50.0),
            (conversion["original_potassium_reversal_mv"], -77.0),
            (conversion["original_leak_reversal_mv"], -54.387),
        )
        for original, modern in pairs:
            self.assertAlmostEqual(-original - 65.0, modern)

    def test_reference_stimulus_protocol_is_reproducible(self) -> None:
        protocol = self.reference["reference_protocol"]
        stimulus = square_current(
            protocol["stimulus_amplitude_ua_per_cm2"],
            protocol["stimulus_start_ms"],
            protocol["stimulus_duration_ms"],
            protocol["stimulus_end_inclusive"],
        )
        self.assertEqual(stimulus(9.99), 0.0)
        self.assertEqual(stimulus(10.0), 20.0)
        self.assertEqual(stimulus(10.49), 20.0)
        self.assertEqual(stimulus(10.5), 20.0)
        self.assertEqual(stimulus(10.51), 0.0)

    def test_propagation_reference_is_recorded(self) -> None:
        propagation = self.reference["propagation_reference"]
        self.assertEqual(propagation["temperature_c"], 18.5)
        self.assertEqual(propagation["published_calculated_velocity_m_per_s"], 18.8)
        self.assertEqual(propagation["published_experimental_velocity_m_per_s"], 21.2)

    def test_reference_experiment_has_expected_action_potential_morphology(self) -> None:
        metrics = run_reference_experiment()["metrics"]
        self.assertGreater(metrics["amplitude_from_initial_mv"], 90.0)
        self.assertLess(metrics["amplitude_from_initial_mv"], 120.0)
        self.assertLess(metrics["minimum_voltage_mv"], -70.0)
        self.assertGreater(metrics["half_amplitude_width_ms"], 1.0)
        self.assertLess(metrics["half_amplitude_width_ms"], 3.0)
        self.assertAlmostEqual(metrics["final_voltage_mv"], -65.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
