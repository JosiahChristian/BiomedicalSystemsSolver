"""Passive cable-equation baseline with explicit units and sealed ends.

The model describes passive electrotonic spread. It deliberately does not call
the result an action potential; active Hodgkin-Huxley currents are a later,
separately validated model.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class PassiveCableConfig:
    length_cm: float = 0.5
    num_nodes: int = 101
    resting_potential_mv: float = -70.0
    diffusion_cm2_per_ms: float = 0.001
    membrane_time_constant_ms: float = 10.0
    dt_ms: float = 0.01
    duration_ms: float = 20.0

    @property
    def dx_cm(self) -> float:
        return self.length_cm / (self.num_nodes - 1)

    @property
    def diffusion_number(self) -> float:
        return self.diffusion_cm2_per_ms * self.dt_ms / self.dx_cm**2

    def validate(self) -> None:
        if self.length_cm <= 0 or self.num_nodes < 3:
            raise ValueError("length_cm must be positive and num_nodes at least 3")
        if self.diffusion_cm2_per_ms <= 0 or self.membrane_time_constant_ms <= 0:
            raise ValueError("cable parameters must be positive")
        if self.dt_ms <= 0 or self.duration_ms <= 0:
            raise ValueError("time parameters must be positive")
        if self.diffusion_number > 0.5:
            raise ValueError(
                "unstable explicit cable step: D*dt/dx^2 must be <= 0.5"
            )


@dataclass(frozen=True)
class PassiveCableResult:
    x_cm: np.ndarray
    time_ms: np.ndarray
    voltage_mv: np.ndarray
    diffusion_number: float


def square_stimulus(
    amplitude_mv_per_ms: float = 25.0,
    start_ms: float = 0.5,
    duration_ms: float = 1.0,
) -> Callable[[float], float]:
    def stimulus(time_ms: float) -> float:
        return amplitude_mv_per_ms if start_ms <= time_ms < start_ms + duration_ms else 0.0

    return stimulus


def simulate_passive_cable(
    config: PassiveCableConfig,
    stimulus_mv_per_ms: Callable[[float], float] | None = None,
) -> PassiveCableResult:
    """Solve a passive cable equation with sealed-end Neumann boundaries."""

    config.validate()
    stimulus_mv_per_ms = stimulus_mv_per_ms or square_stimulus()
    steps = int(round(config.duration_ms / config.dt_ms))
    if steps < 1:
        raise ValueError("duration_ms must contain at least one time step")

    x = np.linspace(0.0, config.length_cm, config.num_nodes)
    time = np.arange(steps + 1, dtype=float) * config.dt_ms
    history = np.full(
        (steps + 1, config.num_nodes), config.resting_potential_mv, dtype=float
    )
    r = config.diffusion_number
    leak_fraction = config.dt_ms / config.membrane_time_constant_ms

    for step in range(steps):
        old = history[step]
        new = old.copy()
        new[1:-1] = (
            old[1:-1]
            + r * (old[2:] - 2.0 * old[1:-1] + old[:-2])
            - leak_fraction * (old[1:-1] - config.resting_potential_mv)
        )
        # Ghost nodes mirror the adjacent interior value: dV/dx = 0.
        new[0] = (
            old[0]
            + 2.0 * r * (old[1] - old[0])
            - leak_fraction * (old[0] - config.resting_potential_mv)
            + config.dt_ms * stimulus_mv_per_ms(time[step])
        )
        new[-1] = (
            old[-1]
            + 2.0 * r * (old[-2] - old[-1])
            - leak_fraction * (old[-1] - config.resting_potential_mv)
        )
        history[step + 1] = new

    return PassiveCableResult(x, time, history, r)
