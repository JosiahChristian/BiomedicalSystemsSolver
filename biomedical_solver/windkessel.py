"""Reduced-order arterial pressure model.

The two-element Windkessel equation is

    C dP/dt = Q_in(t) - (P - P_v) / R

with pressure in mmHg, flow in mL/s, resistance in mmHg*s/mL, and compliance
in mL/mmHg.  This is a research/education baseline, not a clinical model.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class WindkesselConfig:
    resistance_mmhg_s_per_ml: float = 1.0
    compliance_ml_per_mmhg: float = 1.0
    venous_pressure_mmhg: float = 15.0
    heart_rate_bpm: float = 72.0
    mean_flow_ml_per_s: float = 83.33
    ejection_fraction: float = 0.35
    dt_s: float = 0.001
    cycles: int = 10
    initial_pressure_mmhg: float = 95.0

    @property
    def period_s(self) -> float:
        return 60.0 / self.heart_rate_bpm

    def validate(self) -> None:
        positive = (
            self.resistance_mmhg_s_per_ml,
            self.compliance_ml_per_mmhg,
            self.heart_rate_bpm,
            self.mean_flow_ml_per_s,
            self.dt_s,
            self.initial_pressure_mmhg,
        )
        if any(value <= 0 for value in positive) or self.cycles < 2:
            raise ValueError("Windkessel parameters must be positive and cycles at least 2")
        if not 0 < self.ejection_fraction < 1:
            raise ValueError("ejection_fraction must lie between zero and one")
        if self.dt_s / (
            self.resistance_mmhg_s_per_ml * self.compliance_ml_per_mmhg
        ) > 0.1:
            raise ValueError("time step is too large for stable pressure integration")


@dataclass(frozen=True)
class WindkesselResult:
    time_s: np.ndarray
    inflow_ml_per_s: np.ndarray
    pressure_mmhg: np.ndarray

    @property
    def systolic_mmhg(self) -> float:
        return float(np.max(self.pressure_mmhg))

    @property
    def diastolic_mmhg(self) -> float:
        return float(np.min(self.pressure_mmhg))


def pulsatile_inflow(config: WindkesselConfig) -> Callable[[float], float]:
    """Return a half-sine ejection waveform normalized to the requested mean flow."""
    peak = config.mean_flow_ml_per_s * np.pi / (2.0 * config.ejection_fraction)

    def flow(time_s: float) -> float:
        phase = (time_s % config.period_s) / config.period_s
        if phase >= config.ejection_fraction:
            return 0.0
        return float(peak * np.sin(np.pi * phase / config.ejection_fraction))

    return flow


def simulate_windkessel(
    config: WindkesselConfig = WindkesselConfig(),
    inflow: Callable[[float], float] | None = None,
) -> WindkesselResult:
    """Integrate the Windkessel model and return its converged final cardiac cycle."""
    config.validate()
    inflow = inflow or pulsatile_inflow(config)
    total_steps = int(round(config.cycles * config.period_s / config.dt_s))
    pressure = config.initial_pressure_mmhg
    pressures = np.empty(total_steps + 1)
    flows = np.empty(total_steps + 1)
    times = np.arange(total_steps + 1, dtype=float) * config.dt_s
    pressures[0] = pressure
    flows[0] = inflow(0.0)
    resistance = config.resistance_mmhg_s_per_ml
    compliance = config.compliance_ml_per_mmhg

    for index in range(total_steps):
        flow = inflow(times[index])
        pressure += config.dt_s * (
            flow - (pressure - config.venous_pressure_mmhg) / resistance
        ) / compliance
        pressures[index + 1] = pressure
        flows[index + 1] = inflow(times[index + 1])

    cycle_steps = int(round(config.period_s / config.dt_s))
    start = len(times) - cycle_steps - 1
    cycle_time = times[start:] - times[start]
    return WindkesselResult(cycle_time, flows[start:], pressures[start:])
