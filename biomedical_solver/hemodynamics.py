"""Verified baseline for a one-dimensional momentum-diffusion model.

This is intentionally labelled as a reduced mathematical baseline. It is not a
complete arterial-flow model: pressure, compliance, convection, and radial wall
physics will be introduced only with matching conservation and benchmark tests.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class HemodynamicConfig:
    length_cm: float = 10.0
    num_nodes: int = 101
    viscosity_poise: float = 0.035
    density_g_per_cm3: float = 1.06
    dt_s: float = 0.001
    duration_s: float = 1.0
    outlet: str = "zero_gradient"

    @property
    def dx_cm(self) -> float:
        return self.length_cm / (self.num_nodes - 1)

    @property
    def kinematic_viscosity_cm2_per_s(self) -> float:
        return self.viscosity_poise / self.density_g_per_cm3

    @property
    def diffusion_number(self) -> float:
        return (
            self.kinematic_viscosity_cm2_per_s
            * self.dt_s
            / self.dx_cm**2
        )

    def validate(self) -> None:
        if self.length_cm <= 0 or self.num_nodes < 3:
            raise ValueError("length_cm must be positive and num_nodes at least 3")
        if self.viscosity_poise <= 0 or self.density_g_per_cm3 <= 0:
            raise ValueError("fluid properties must be positive")
        if self.dt_s <= 0 or self.duration_s <= 0:
            raise ValueError("time parameters must be positive")
        if self.outlet not in {"zero_gradient", "fixed_zero"}:
            raise ValueError("unsupported outlet boundary")
        if self.diffusion_number > 0.5:
            raise ValueError(
                "unstable explicit diffusion step: nu*dt/dx^2 must be <= 0.5"
            )


@dataclass(frozen=True)
class HemodynamicResult:
    x_cm: np.ndarray
    time_s: np.ndarray
    velocity_cm_per_s: np.ndarray
    diffusion_number: float


def constant_inlet(velocity_cm_per_s: float) -> Callable[[float], float]:
    return lambda _time_s: velocity_cm_per_s


def simulate_hemodynamics(
    config: HemodynamicConfig,
    inlet_velocity: Callable[[float], float] | None = None,
    initial_velocity_cm_per_s: float = 0.0,
) -> HemodynamicResult:
    """Solve ``dv/dt = nu*d2v/dx2`` with explicit finite differences."""

    config.validate()
    inlet_velocity = inlet_velocity or constant_inlet(30.0)
    steps = int(round(config.duration_s / config.dt_s))
    if steps < 1:
        raise ValueError("duration_s must contain at least one time step")

    x = np.linspace(0.0, config.length_cm, config.num_nodes)
    time = np.arange(steps + 1, dtype=float) * config.dt_s
    history = np.empty((steps + 1, config.num_nodes), dtype=float)
    history[0] = initial_velocity_cm_per_s
    history[0, 0] = inlet_velocity(0.0)
    if config.outlet == "fixed_zero":
        history[0, -1] = 0.0
    else:
        history[0, -1] = history[0, -2]

    r = config.diffusion_number
    for step in range(steps):
        old = history[step]
        new = old.copy()
        new[1:-1] = old[1:-1] + r * (old[2:] - 2.0 * old[1:-1] + old[:-2])
        new[0] = inlet_velocity(time[step + 1])
        new[-1] = 0.0 if config.outlet == "fixed_zero" else new[-2]
        history[step + 1] = new

    return HemodynamicResult(x, time, history, r)
