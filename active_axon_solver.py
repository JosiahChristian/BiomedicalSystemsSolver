"""Run the spatial Hodgkin-Huxley active-axon experiment."""

import numpy as np

from biomedical_solver.active_cable import ActiveCableConfig, simulate_active_cable


def main() -> None:
    config = ActiveCableConfig()
    result = simulate_active_cable(config)
    activation = result.activation_times_ms()

    print("SPATIAL HODGKIN-HUXLEY ACTIVE AXON")
    print(f"nodes={config.num_nodes} length={config.length_cm:.3f} cm dx={config.dx_cm:.4f} cm")
    print(f"duration={config.duration_ms:.3f} ms dt={config.dt_ms:.4f} ms")
    print(f"cable_diffusivity={config.cable_diffusivity_cm2_per_ms:.6f} cm^2/ms")
    print(f"diffusion_number={result.diffusion_number:.6f}")
    print(f"peak_voltage={np.max(result.voltage_mv):.6f} mV")
    print(f"activated_nodes={np.count_nonzero(np.isfinite(activation))}/{config.num_nodes}")
    print(f"conduction_velocity={result.conduction_velocity_m_per_s():.6f} m/s")


if __name__ == "__main__":
    main()
