"""Compare our 1952 reference trajectory with independent libOpenCOR output."""

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

try:
    import libopencor as loc
except ImportError as exc:  # pragma: no cover - optional release dependency
    raise SystemExit(
        "Install the optional requirements-validation.txt dependencies first"
    ) from exc


ROOT = Path(__file__).parents[1]
REFERENCE = ROOT / "references" / "hodgkin_huxley_1952.json"


def run_comparison(cellml_path: Path) -> dict[str, object]:
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    protocol = reference["reference_protocol"]
    parameters = reference["modern_absolute_voltage_parameters"]

    file = loc.File(str(cellml_path))
    document = loc.SedDocument()
    model = loc.SedModel(document, file)
    model.id = "hh1952"
    document.add_model(model)
    simulation = loc.SedUniformTimeCourse(document)
    simulation.id = "rk4_50ms"
    simulation.initial_time = 0.0
    simulation.output_start_time = 0.0
    simulation.output_end_time = protocol["duration_ms"]
    simulation.number_of_steps = int(protocol["duration_ms"] / 0.01)
    simulation.ode_solver = loc.SolverFourthOrderRungeKutta()
    document.add_simulation(simulation)
    task = loc.SedTask(document, model, simulation)
    task.id = "trajectory"
    document.add_task(task)
    instance = document.instantiate()
    if instance.has_errors:
        raise RuntimeError("libOpenCOR failed to instantiate the CellML model")
    instance.run()
    if instance.has_errors:
        raise RuntimeError("libOpenCOR failed to execute the CellML model")

    independent_task = instance.task(0)
    states = {
        independent_task.state_name(index).split("/")[-1]: np.array(
            independent_task.state(index)
        )
        for index in range(independent_task.state_count)
    }
    independent = {
        "V": -states["V"] - 65.0,
        "m": states["m"],
        "h": states["h"],
        "n": states["n"],
    }

    config = HodgkinHuxleyConfig(
        **parameters, dt_ms=0.01, duration_ms=protocol["duration_ms"]
    )
    stimulus = square_current(
        protocol["stimulus_amplitude_ua_per_cm2"],
        protocol["stimulus_start_ms"],
        protocol["stimulus_duration_ms"],
        protocol["stimulus_end_inclusive"],
    )
    ours_result = simulate_hodgkin_huxley(config, stimulus)
    ours = {
        "V": ours_result.voltage_mv,
        "m": ours_result.m,
        "h": ours_result.h,
        "n": ours_result.n,
    }
    comparisons = {}
    for name in ours:
        difference = ours[name] - independent[name]
        comparisons[name] = {
            "max_absolute_difference": float(np.max(np.abs(difference))),
            "root_mean_square_difference": float(
                np.sqrt(np.mean(difference * difference))
            ),
        }

    return {
        "engine": {
            "name": "libOpenCOR",
            "version": getattr(loc, "__version__", loc.version_string()),
            "source_commit": "423a252b3cfcbbbfb8b3bf2eaacd6e1c24b025f2",
        },
        "cellml": {
            "revision": reference["executable_reference"]["revision"],
            "sha256": hashlib.sha256(cellml_path.read_bytes()).hexdigest(),
        },
        "samples": int(len(ours_result.time_ms)),
        "time_step_ms": config.dt_ms,
        "comparison": comparisons,
        "peak": {
            "ours_voltage_mv": float(np.max(ours["V"])),
            "independent_voltage_mv": float(np.max(independent["V"])),
            "ours_time_ms": float(ours_result.time_ms[np.argmax(ours["V"])]),
            "independent_time_ms": float(
                independent_task.voi[np.argmax(independent["V"])]
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cellml", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    serialized = json.dumps(run_comparison(args.cellml), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
