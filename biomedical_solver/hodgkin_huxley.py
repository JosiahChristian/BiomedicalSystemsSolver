"""Classical Hodgkin-Huxley single-compartment membrane model.

Voltage is measured in mV, time in ms, conductance in mS/cm^2, capacitance in
uF/cm^2, and current density in uA/cm^2. With these units, current divided by
capacitance has units of mV/ms.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class HodgkinHuxleyConfig:
    capacitance_uf_per_cm2: float = 1.0
    sodium_conductance_ms_per_cm2: float = 120.0
    potassium_conductance_ms_per_cm2: float = 36.0
    leak_conductance_ms_per_cm2: float = 0.3
    sodium_reversal_mv: float = 50.0
    potassium_reversal_mv: float = -77.0
    leak_reversal_mv: float = -54.387
    initial_voltage_mv: float = -65.0
    initial_m: float | None = None
    initial_h: float | None = None
    initial_n: float | None = None
    temperature_c: float = 6.3
    gating_q10: float = 3.0
    dt_ms: float = 0.01
    duration_ms: float = 50.0

    @property
    def gating_rate_scale(self) -> float:
        return self.gating_q10 ** ((self.temperature_c - 6.3) / 10.0)

    def validate(self) -> None:
        if self.capacitance_uf_per_cm2 <= 0:
            raise ValueError("membrane capacitance must be positive")
        if min(
            self.sodium_conductance_ms_per_cm2,
            self.potassium_conductance_ms_per_cm2,
            self.leak_conductance_ms_per_cm2,
        ) < 0:
            raise ValueError("conductances must be nonnegative")
        if self.dt_ms <= 0 or self.duration_ms <= 0:
            raise ValueError("time parameters must be positive")
        if self.dt_ms > 0.05:
            raise ValueError("dt_ms must be <= 0.05 for the reference RK4 integration")
        if self.gating_q10 <= 0:
            raise ValueError("gating_q10 must be positive")
        for name, gate in (("initial_m", self.initial_m), ("initial_h", self.initial_h), ("initial_n", self.initial_n)):
            if gate is not None and not 0.0 <= gate <= 1.0:
                raise ValueError(f"{name} must be within [0, 1]")


@dataclass(frozen=True)
class HodgkinHuxleyResult:
    time_ms: np.ndarray
    voltage_mv: np.ndarray
    m: np.ndarray
    h: np.ndarray
    n: np.ndarray
    stimulus_ua_per_cm2: np.ndarray
    sodium_current_ua_per_cm2: np.ndarray
    potassium_current_ua_per_cm2: np.ndarray
    leak_current_ua_per_cm2: np.ndarray


def square_current(
    amplitude_ua_per_cm2: float = 10.0,
    start_ms: float = 10.0,
    duration_ms: float = 20.0,
    end_inclusive: bool = False,
) -> Callable[[float], float]:
    """Return a deterministic square current-density stimulus."""

    def stimulus(time_ms: float) -> float:
        end_ms = start_ms + duration_ms
        active = start_ms <= time_ms <= end_ms if end_inclusive else start_ms <= time_ms < end_ms
        return amplitude_ua_per_cm2 if active else 0.0

    return stimulus


def _vtrap(numerator: float, denominator_scale: float) -> float:
    """Evaluate x/(1-exp(-x/y)) accurately near x=0."""

    ratio = numerator / denominator_scale
    if abs(ratio) < 1e-7:
        return denominator_scale * (1.0 + ratio / 2.0)
    return numerator / (-np.expm1(-ratio))


def gating_rates(voltage_mv: float) -> tuple[float, float, float, float, float, float]:
    """Return alpha/beta rates for m, h, and n in inverse milliseconds."""

    alpha_m = 0.1 * _vtrap(voltage_mv + 40.0, 10.0)
    beta_m = 4.0 * np.exp(-(voltage_mv + 65.0) / 18.0)
    alpha_h = 0.07 * np.exp(-(voltage_mv + 65.0) / 20.0)
    beta_h = 1.0 / (1.0 + np.exp(-(voltage_mv + 35.0) / 10.0))
    alpha_n = 0.01 * _vtrap(voltage_mv + 55.0, 10.0)
    beta_n = 0.125 * np.exp(-(voltage_mv + 65.0) / 80.0)
    return alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n


def steady_state_gates(voltage_mv: float) -> tuple[float, float, float]:
    rates = gating_rates(voltage_mv)
    return (
        rates[0] / (rates[0] + rates[1]),
        rates[2] / (rates[2] + rates[3]),
        rates[4] / (rates[4] + rates[5]),
    )


def ionic_currents(
    voltage_mv: float,
    m: float,
    h: float,
    n: float,
    config: HodgkinHuxleyConfig,
) -> tuple[float, float, float]:
    sodium = (
        config.sodium_conductance_ms_per_cm2
        * m**3
        * h
        * (voltage_mv - config.sodium_reversal_mv)
    )
    potassium = (
        config.potassium_conductance_ms_per_cm2
        * n**4
        * (voltage_mv - config.potassium_reversal_mv)
    )
    leak = config.leak_conductance_ms_per_cm2 * (
        voltage_mv - config.leak_reversal_mv
    )
    return sodium, potassium, leak


def state_derivative(
    time_ms: float,
    state: np.ndarray,
    config: HodgkinHuxleyConfig,
    stimulus: Callable[[float], float],
) -> np.ndarray:
    voltage, m, h, n = state
    alpha_m, beta_m, alpha_h, beta_h, alpha_n, beta_n = gating_rates(voltage)
    sodium, potassium, leak = ionic_currents(voltage, m, h, n, config)
    dv_dt = (stimulus(time_ms) - sodium - potassium - leak) / config.capacitance_uf_per_cm2
    rate_scale = config.gating_rate_scale
    dm_dt = rate_scale * (alpha_m * (1.0 - m) - beta_m * m)
    dh_dt = rate_scale * (alpha_h * (1.0 - h) - beta_h * h)
    dn_dt = rate_scale * (alpha_n * (1.0 - n) - beta_n * n)
    return np.array([dv_dt, dm_dt, dh_dt, dn_dt], dtype=float)


def simulate_hodgkin_huxley(
    config: HodgkinHuxleyConfig,
    stimulus_ua_per_cm2: Callable[[float], float] | None = None,
) -> HodgkinHuxleyResult:
    """Integrate the membrane equations with fixed-step fourth-order Runge-Kutta."""

    config.validate()
    stimulus = stimulus_ua_per_cm2 or square_current()
    steps = int(round(config.duration_ms / config.dt_ms))
    time = np.arange(steps + 1, dtype=float) * config.dt_ms
    state = np.empty((steps + 1, 4), dtype=float)
    state[0, 0] = config.initial_voltage_mv
    steady_m, steady_h, steady_n = steady_state_gates(config.initial_voltage_mv)
    state[0, 1:] = (
        steady_m if config.initial_m is None else config.initial_m,
        steady_h if config.initial_h is None else config.initial_h,
        steady_n if config.initial_n is None else config.initial_n,
    )

    for step in range(steps):
        current_time = time[step]
        current_state = state[step]
        half_step = config.dt_ms / 2.0
        k1 = state_derivative(current_time, current_state, config, stimulus)
        k2 = state_derivative(current_time + half_step, current_state + half_step * k1, config, stimulus)
        k3 = state_derivative(current_time + half_step, current_state + half_step * k2, config, stimulus)
        k4 = state_derivative(current_time + config.dt_ms, current_state + config.dt_ms * k3, config, stimulus)
        state[step + 1] = current_state + config.dt_ms * (k1 + 2*k2 + 2*k3 + k4) / 6.0

    applied = np.array([stimulus(t) for t in time], dtype=float)
    currents = np.array(
        [ionic_currents(v, m, h, n, config) for v, m, h, n in state],
        dtype=float,
    )
    return HodgkinHuxleyResult(
        time,
        state[:, 0],
        state[:, 1],
        state[:, 2],
        state[:, 3],
        applied,
        currents[:, 0],
        currents[:, 1],
        currents[:, 2],
    )
