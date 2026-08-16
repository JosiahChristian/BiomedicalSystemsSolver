import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


class IndependentValidationArtifactTests(unittest.TestCase):
    def test_libopencor_comparison_clears_declared_tolerance(self) -> None:
        result = json.loads(
            (ROOT / "results" / "libopencor_comparison_summary.json").read_text()
        )
        self.assertEqual(result["samples"], 5001)
        self.assertEqual(result["engine"]["name"], "libOpenCOR")
        self.assertLess(result["comparison"]["V"]["max_absolute_difference"], 1e-9)
        for gate in ("m", "h", "n"):
            self.assertLess(
                result["comparison"][gate]["max_absolute_difference"], 1e-12
            )
        self.assertEqual(result["peak"]["ours_time_ms"], result["peak"]["independent_time_ms"])


if __name__ == "__main__":
    unittest.main()
