"""Command-line entry point for the verified hemodynamic baseline."""

from biomedical_solver.hemodynamics import HemodynamicConfig, simulate_hemodynamics


def main() -> None:
    config = HemodynamicConfig()
    result = simulate_hemodynamics(config)
    midpoint = config.num_nodes // 2

    print("HEMODYNAMIC MOMENTUM-DIFFUSION BASELINE")
    print(f"nodes={config.num_nodes} dx={config.dx_cm:.4f} cm")
    print(f"duration={config.duration_s:.3f} s dt={config.dt_s:.4f} s")
    print(f"diffusion_number={result.diffusion_number:.6f}")
    print(f"inlet={result.velocity_cm_per_s[-1, 0]:.6f} cm/s")
    print(f"midpoint={result.velocity_cm_per_s[-1, midpoint]:.6f} cm/s")
    print(f"outlet={result.velocity_cm_per_s[-1, -1]:.6f} cm/s")
    print("scope=reduced viscous-diffusion baseline; not full arterial flow")


if __name__ == "__main__":
    main()
