"""Command-line entry point for the verified passive cable baseline."""

from biomedical_solver.neuro import PassiveCableConfig, simulate_passive_cable


def main() -> None:
    config = PassiveCableConfig()
    result = simulate_passive_cable(config)
    midpoint = config.num_nodes // 2
    peak_index = result.voltage_mv[:, 0].argmax()

    print("PASSIVE NEURAL CABLE BASELINE")
    print(f"nodes={config.num_nodes} dx={config.dx_cm:.6f} cm")
    print(f"duration={config.duration_ms:.3f} ms dt={config.dt_ms:.4f} ms")
    print(f"diffusion_number={result.diffusion_number:.6f}")
    print(f"peak_proximal={result.voltage_mv[peak_index, 0]:.6f} mV")
    print(f"final_midpoint={result.voltage_mv[-1, midpoint]:.6f} mV")
    print(f"final_distal={result.voltage_mv[-1, -1]:.6f} mV")
    print("scope=passive electrotonic spread; not an active action potential")


if __name__ == "__main__":
    main()
