"""Run the validated single-compartment Hodgkin-Huxley experiment."""

import numpy as np

from biomedical_solver.hodgkin_huxley import HodgkinHuxleyConfig, simulate_hodgkin_huxley


def main() -> None:
    config = HodgkinHuxleyConfig()
    result = simulate_hodgkin_huxley(config)
    peak_index = int(np.argmax(result.voltage_mv))
    crossings = np.flatnonzero(
        (result.voltage_mv[:-1] < 0.0) & (result.voltage_mv[1:] >= 0.0)
    )

    print("HODGKIN-HUXLEY ACTIVE MEMBRANE REFERENCE")
    print(f"duration={config.duration_ms:.3f} ms dt={config.dt_ms:.4f} ms")
    print(f"peak_voltage={result.voltage_mv[peak_index]:.6f} mV")
    print(f"peak_time={result.time_ms[peak_index]:.6f} ms")
    print(f"minimum_voltage={result.voltage_mv.min():.6f} mV")
    print(f"upward_zero_crossings={len(crossings)}")
    print(f"gating_bounds=m[{result.m.min():.6f},{result.m.max():.6f}] "
          f"h[{result.h.min():.6f},{result.h.max():.6f}] "
          f"n[{result.n.min():.6f},{result.n.max():.6f}]")


if __name__ == "__main__":
    main()
