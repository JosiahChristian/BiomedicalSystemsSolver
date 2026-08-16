"""Reproduce the pinned Physiome Hodgkin-Huxley stimulus protocol."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from biomedical_solver.hodgkin_huxley import (
    HodgkinHuxleyConfig,
    simulate_hodgkin_huxley,
    square_current,
)


ROOT = Path(__file__).parents[1]
REFERENCE_PATH = ROOT / "references" / "hodgkin_huxley_1952.json"


def run_reference_experiment() -> dict[str, object]:
    reference_bytes = REFERENCE_PATH.read_bytes()
    reference = json.loads(reference_bytes)
    parameters = reference["modern_absolute_voltage_parameters"]
    protocol = reference["reference_protocol"]
    config = HodgkinHuxleyConfig(
        **parameters,
        dt_ms=0.01,
        duration_ms=protocol["duration_ms"],
    )
    stimulus = square_current(
        protocol["stimulus_amplitude_ua_per_cm2"],
        protocol["stimulus_start_ms"],
        protocol["stimulus_duration_ms"],
        protocol["stimulus_end_inclusive"],
    )
    result = simulate_hodgkin_huxley(config, stimulus)
    peak_index = int(np.argmax(result.voltage_mv))
    resting_mv = config.initial_voltage_mv
    half_amplitude_mv = resting_mv + (
        result.voltage_mv[peak_index] - resting_mv
    ) / 2.0
    above_half = np.flatnonzero(result.voltage_mv >= half_amplitude_mv)
    width_ms = result.time_ms[above_half[-1]] - result.time_ms[above_half[0]]
    voltage_hash = hashlib.sha256(result.voltage_mv.astype("<f8").tobytes()).hexdigest()

    return {
        "experiment": "hh_1952_physiome_protocol",
        "reference_sha256": hashlib.sha256(reference_bytes).hexdigest(),
        "executable_reference_revision": reference["executable_reference"]["revision"],
        "integration": {"method": "RK4", "dt_ms": config.dt_ms},
        "metrics": {
            "peak_voltage_mv": float(result.voltage_mv[peak_index]),
            "peak_time_ms": float(result.time_ms[peak_index]),
            "amplitude_from_initial_mv": float(result.voltage_mv[peak_index] - resting_mv),
            "minimum_voltage_mv": float(np.min(result.voltage_mv)),
            "half_amplitude_width_ms": float(width_ms),
            "final_voltage_mv": float(result.voltage_mv[-1]),
        },
        "bounds": {
            "m": [float(np.min(result.m)), float(np.max(result.m))],
            "h": [float(np.min(result.h)), float(np.max(result.h))],
            "n": [float(np.min(result.n)), float(np.max(result.n))],
        },
        "voltage_trace_sha256_float64_le": voltage_hash,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    serialized = json.dumps(run_reference_experiment(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
