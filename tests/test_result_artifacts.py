import json
from pathlib import Path
import unittest

import numpy as np

from experiments.active_axon_reference import run_experiment as run_active_axon
from experiments.hh_1952_reference import run_reference_experiment as run_hh


ROOT = Path(__file__).parents[1]


class ResultArtifactTests(unittest.TestCase):
    def test_hodgkin_huxley_summary_matches_regenerated_metrics(self) -> None:
        stored = json.loads(
            (ROOT / "results" / "hh_1952_reference_summary.json").read_text()
        )
        regenerated = run_hh()
        self.assertEqual(
            stored["executable_reference_revision"],
            regenerated["executable_reference_revision"],
        )
        for name, value in stored["metrics"].items():
            self.assertTrue(np.isclose(value, regenerated["metrics"][name], rtol=1e-10, atol=1e-10))

    def test_active_axon_summary_matches_regenerated_metrics(self) -> None:
        stored = json.loads(
            (ROOT / "results" / "active_axon_reference_summary.json").read_text()
        )
        regenerated = run_active_axon()
        for name, value in stored["metrics"].items():
            self.assertTrue(np.isclose(value, regenerated["metrics"][name], rtol=1e-10, atol=1e-10))


if __name__ == "__main__":
    unittest.main()
