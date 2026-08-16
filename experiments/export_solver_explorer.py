"""Export a zero-install browser playback from verified solver trajectories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from biomedical_solver.active_cable import ActiveCableConfig, simulate_active_cable
from biomedical_solver.hemodynamics import HemodynamicConfig, simulate_hemodynamics
from biomedical_solver.windkessel import simulate_windkessel


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web" / "solver-explorer-template.html"
DEFAULT_OUTPUT = ROOT / "docs" / "index.html"
DEFAULT_TELEMETRY_OUTPUT = ROOT / "docs" / "telemetry-playback.json"


def _rounded_rows(values: np.ndarray, stride: int, decimals: int) -> list[list[float]]:
    return np.round(values[::stride], decimals).tolist()


def build_payload() -> dict[str, object]:
    """Run the reference solvers and return a compact, deterministic payload."""
    axon = simulate_active_cable(ActiveCableConfig())
    flow = simulate_hemodynamics(
        HemodynamicConfig(duration_s=1.0),
        inlet_velocity=lambda time_s: 20.0 + 10.0 * np.sin(2.0 * np.pi * time_s),
        initial_velocity_cm_per_s=20.0,
    )
    axon_stride = 20
    flow_stride = 5
    return {
        "schema": "biomedical-solver-explorer/v1",
        "provenance": {
            "axon_solver": "biomedical_solver.active_cable.simulate_active_cable",
            "flow_solver": "biomedical_solver.hemodynamics.simulate_hemodynamics",
            "warning": (
                "Velocity and pressure are separate reduced-order baselines and are "
                "not bidirectionally coupled; vessel contraction is not rendered."
            ),
        },
        "axon": {
            "x_cm": np.round(axon.x_cm, 4).tolist(),
            "time_ms": np.round(axon.time_ms[::axon_stride], 4).tolist(),
            "voltage_mv": _rounded_rows(axon.voltage_mv, axon_stride, 3),
            "conduction_velocity_m_per_s": round(axon.conduction_velocity_m_per_s(), 6),
            "peak_voltage_mv": round(float(np.max(axon.voltage_mv)), 6),
        },
        "flow": {
            "x_cm": np.round(flow.x_cm, 4).tolist(),
            "time_s": np.round(flow.time_s[::flow_stride], 4).tolist(),
            "velocity_cm_per_s": _rounded_rows(flow.velocity_cm_per_s, flow_stride, 3),
            "model": "1D momentum-diffusion baseline",
        },
    }


def build_telemetry_payload() -> dict[str, object]:
    """Return compact midpoint traces for external visualization clients."""
    payload = build_payload()
    axon = payload["axon"]
    flow = payload["flow"]
    axon_midpoint = len(axon["x_cm"]) // 2
    # The momentum-diffusion baseline propagates slowly over a one-second run.
    # Export the first interior node so the visual client receives the solved,
    # time-varying proximal response rather than a still-unreached midpoint.
    flow_probe = 1
    pressure = simulate_windkessel()
    return {
        "schema": "biomedical-telemetry-playback/v1",
        "source": "BiomedicalSystemsSolver v2.1.0",
        "provenance": payload["provenance"],
        "axon": {
            "position_cm": axon["x_cm"][axon_midpoint],
            "time_ms": axon["time_ms"],
            "voltage_mv": [row[axon_midpoint] for row in axon["voltage_mv"]],
        },
        "flow": {
            "position_cm": flow["x_cm"][flow_probe],
            "time_s": flow["time_s"],
            "velocity_cm_per_s": [row[flow_probe] for row in flow["velocity_cm_per_s"]],
            "model": flow["model"],
        },
        "pressure": {
            "time_s": np.round(pressure.time_s, 4).tolist(),
            "pressure_mmhg": np.round(pressure.pressure_mmhg, 3).tolist(),
            "systolic_mmhg": round(pressure.systolic_mmhg, 3),
            "diastolic_mmhg": round(pressure.diastolic_mmhg, 3),
            "model": "two-element Windkessel reduced-order baseline",
        },
    }


def export(output: Path, telemetry_output: Path = DEFAULT_TELEMETRY_OUTPUT) -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(build_payload(), separators=(",", ":"), allow_nan=False)
    if "__SOLVER_DATA__" not in template:
        raise ValueError("template is missing __SOLVER_DATA__ placeholder")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("__SOLVER_DATA__", payload), encoding="utf-8")
    telemetry_output.parent.mkdir(parents=True, exist_ok=True)
    telemetry_output.write_text(
        json.dumps(build_telemetry_payload(), separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--telemetry-output", type=Path, default=DEFAULT_TELEMETRY_OUTPUT)
    args = parser.parse_args()
    export(args.output.resolve(), args.telemetry_output.resolve())
    print(f"exported solver-driven explorer to {args.output.resolve()}")
    print(f"exported compact telemetry to {args.telemetry_output.resolve()}")


if __name__ == "__main__":
    main()
