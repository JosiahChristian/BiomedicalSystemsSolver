"""Generate the reproducible active-axon propagation summary."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from biomedical_solver.active_cable import ActiveCableConfig, simulate_active_cable


def run_experiment() -> dict[str, object]:
    config = ActiveCableConfig()
    result = simulate_active_cable(config)
    activation = result.activation_times_ms()
    return {
        "experiment": "spatial_hodgkin_huxley_active_axon",
        "configuration": {
            "length_cm": config.length_cm,
            "num_nodes": config.num_nodes,
            "dx_cm": config.dx_cm,
            "dt_ms": config.dt_ms,
            "duration_ms": config.duration_ms,
            "axon_radius_cm": config.axon_radius_cm,
            "axial_resistivity_ohm_cm": config.axial_resistivity_ohm_cm,
            "cable_diffusivity_cm2_per_ms": config.cable_diffusivity_cm2_per_ms,
            "diffusion_number": config.diffusion_number,
            "temperature_c": config.membrane.temperature_c,
            "gating_q10": config.membrane.gating_q10,
            "gating_rate_scale": config.membrane.gating_rate_scale,
            "stimulus_amplitude_ua_per_cm2": config.stimulus_amplitude_ua_per_cm2,
            "stimulus_start_ms": config.stimulus_start_ms,
            "stimulus_duration_ms": config.stimulus_duration_ms,
            "stimulus_length_cm": config.stimulus_length_cm,
        },
        "metrics": {
            "peak_voltage_mv": float(np.max(result.voltage_mv)),
            "minimum_voltage_mv": float(np.min(result.voltage_mv)),
            "activated_nodes": int(np.count_nonzero(np.isfinite(activation))),
            "conduction_velocity_m_per_s_1_to_4_cm": result.conduction_velocity_m_per_s(),
            "published_calculated_velocity_m_per_s": 18.8,
            "published_experimental_velocity_m_per_s": 21.2,
            "calculated_velocity_relative_error_percent": float(
                abs(result.conduction_velocity_m_per_s() - 18.8) / 18.8 * 100.0
            ),
            "first_activation_ms": float(np.nanmin(activation)),
            "distal_activation_ms": float(activation[-1]),
        },
        "voltage_field_sha256_float64_le": hashlib.sha256(
            result.voltage_mv.astype("<f8").tobytes()
        ).hexdigest(),
        "activation_times_sha256_float64_le": hashlib.sha256(
            activation.astype("<f8").tobytes()
        ).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    serialized = json.dumps(run_experiment(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
