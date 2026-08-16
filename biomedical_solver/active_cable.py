"""Spatial Hodgkin-Huxley cable model for an unmyelinated axon.

The cable coefficient is derived from axon radius, intracellular axial
resistivity, and membrane capacitance. Voltage and gate dynamics are integrated
together with fixed-step RK4 and sealed-end boundaries.
"""

from dataclasses import dataclass, field

import numpy as np

from .hodgkin_huxley import HodgkinHuxleyConfig, steady_state_gates


@dataclass(frozen=True)
class ActiveCableConfig:
    length_cm: float = 5.0
    num_nodes: int = 101
    axon_radius_cm: float = 0.0238
    axial_resistivity_ohm_cm: float = 35.4
    membrane: HodgkinHuxleyConfig = field(
        default_factory=lambda: HodgkinHuxleyConfig(temperature_c=18.5)
    )
    dt_ms: float = 0.001
    duration_ms: float = 8.0
    stimulus_amplitude_ua_per_cm2: float = 50.0
    stimulus_start_ms: float = 0.5
    stimulus_duration_ms: float = 1.0
    stimulus_length_cm: float = 0.2

    @property
    def dx_cm(self) -> float:
        return self.length_cm / (self.num_nodes - 1)

    @property
    def cable_diffusivity_cm2_per_ms(self) -> float:
        capacitance_f_per_cm2 = self.membrane.capacitance_uf_per_cm2 * 1e-6
        diffusivity_cm2_per_s = self.axon_radius_cm / (
            2.0 * self.axial_resistivity_ohm_cm * capacitance_f_per_cm2
        )
        return diffusivity_cm2_per_s / 1000.0

    @property
    def diffusion_number(self) -> float:
        return self.cable_diffusivity_cm2_per_ms * self.dt_ms / self.dx_cm**2

    def validate(self) -> None:
        if self.length_cm <= 0 or self.num_nodes < 5:
            raise ValueError("length_cm must be positive and num_nodes at least 5")
        if self.axon_radius_cm <= 0 or self.axial_resistivity_ohm_cm <= 0:
            raise ValueError("axon geometry and resistivity must be positive")
        if self.dt_ms <= 0 or self.duration_ms <= 0:
            raise ValueError("time parameters must be positive")
        if self.stimulus_duration_ms < 0 or self.stimulus_length_cm <= 0:
            raise ValueError("stimulus dimensions must be positive")
        if self.diffusion_number > 0.5:
            raise ValueError(
                "unstable explicit cable step: D*dt/dx^2 must be <= 0.5"
            )


@dataclass(frozen=True)
class ActiveCableResult:
    x_cm: np.ndarray
    time_ms: np.ndarray
    voltage_mv: np.ndarray
    m: np.ndarray
    h: np.ndarray
    n: np.ndarray
    diffusion_number: float

    def activation_times_ms(self, threshold_mv: float = 0.0) -> np.ndarray:
        """Return first upward threshold crossing at every node, or NaN."""

        below = self.voltage_mv[:-1] < threshold_mv
        above = self.voltage_mv[1:] >= threshold_mv
        crossings = below & above
        activation = np.full(self.voltage_mv.shape[1], np.nan)
        for node in range(self.voltage_mv.shape[1]):
            indices = np.flatnonzero(crossings[:, node])
            if indices.size:
                index = int(indices[0])
                v0 = self.voltage_mv[index, node]
                v1 = self.voltage_mv[index + 1, node]
                fraction = (threshold_mv - v0) / (v1 - v0)
                activation[node] = self.time_ms[index] + fraction * (
                    self.time_ms[index + 1] - self.time_ms[index]
                )
        return activation

    def conduction_velocity_m_per_s(
        self, start_cm: float = 1.0, end_cm: float = 4.0, threshold_mv: float = 0.0
    ) -> float:
        start = int(np.argmin(np.abs(self.x_cm - start_cm)))
        end = int(np.argmin(np.abs(self.x_cm - end_cm)))
        activation = self.activation_times_ms(threshold_mv)
        elapsed_ms = activation[end] - activation[start]
        if not np.isfinite(elapsed_ms) or elapsed_ms <= 0:
            return float("nan")
        # cm/ms multiplied by 10 equals m/s.
        return float((self.x_cm[end] - self.x_cm[start]) / elapsed_ms * 10.0)


def _vtrap_array(x: np.ndarray, scale: float) -> np.ndarray:
    ratio = x / scale
    output = np.empty_like(x)
    near = np.abs(ratio) < 1e-7
    output[near] = scale * (1.0 + ratio[near] / 2.0)
    output[~near] = x[~near] / (-np.expm1(-ratio[~near]))
    return output


def _derivative(
    time_ms: float,
    state: np.ndarray,
    config: ActiveCableConfig,
    stimulated_nodes: np.ndarray,
) -> np.ndarray:
    voltage, m, h, n = state
    membrane = config.membrane

    alpha_m = 0.1 * _vtrap_array(voltage + 40.0, 10.0)
    beta_m = 4.0 * np.exp(-(voltage + 65.0) / 18.0)
    alpha_h = 0.07 * np.exp(-(voltage + 65.0) / 20.0)
    beta_h = 1.0 / (1.0 + np.exp(-(voltage + 35.0) / 10.0))
    alpha_n = 0.01 * _vtrap_array(voltage + 55.0, 10.0)
    beta_n = 0.125 * np.exp(-(voltage + 65.0) / 80.0)

    sodium = membrane.sodium_conductance_ms_per_cm2 * m**3 * h * (
        voltage - membrane.sodium_reversal_mv
    )
    potassium = membrane.potassium_conductance_ms_per_cm2 * n**4 * (
        voltage - membrane.potassium_reversal_mv
    )
    leak = membrane.leak_conductance_ms_per_cm2 * (
        voltage - membrane.leak_reversal_mv
    )

    laplacian = np.empty_like(voltage)
    laplacian[1:-1] = (voltage[2:] - 2.0 * voltage[1:-1] + voltage[:-2]) / config.dx_cm**2
    laplacian[0] = 2.0 * (voltage[1] - voltage[0]) / config.dx_cm**2
    laplacian[-1] = 2.0 * (voltage[-2] - voltage[-1]) / config.dx_cm**2

    stimulus = np.zeros_like(voltage)
    if config.stimulus_start_ms <= time_ms < config.stimulus_start_ms + config.stimulus_duration_ms:
        stimulus[stimulated_nodes] = config.stimulus_amplitude_ua_per_cm2

    dv_dt = (
        stimulus - sodium - potassium - leak
    ) / membrane.capacitance_uf_per_cm2 + config.cable_diffusivity_cm2_per_ms * laplacian
    rate_scale = membrane.gating_rate_scale
    dm_dt = rate_scale * (alpha_m * (1.0 - m) - beta_m * m)
    dh_dt = rate_scale * (alpha_h * (1.0 - h) - beta_h * h)
    dn_dt = rate_scale * (alpha_n * (1.0 - n) - beta_n * n)
    return np.stack((dv_dt, dm_dt, dh_dt, dn_dt))


def simulate_active_cable(config: ActiveCableConfig) -> ActiveCableResult:
    config.validate()
    steps = int(round(config.duration_ms / config.dt_ms))
    time = np.arange(steps + 1, dtype=float) * config.dt_ms
    x = np.linspace(0.0, config.length_cm, config.num_nodes)
    history = np.empty((steps + 1, 4, config.num_nodes), dtype=float)
    history[0, 0] = config.membrane.initial_voltage_mv
    steady = steady_state_gates(config.membrane.initial_voltage_mv)
    history[0, 1] = steady[0] if config.membrane.initial_m is None else config.membrane.initial_m
    history[0, 2] = steady[1] if config.membrane.initial_h is None else config.membrane.initial_h
    history[0, 3] = steady[2] if config.membrane.initial_n is None else config.membrane.initial_n
    stimulated = x <= config.stimulus_length_cm + 1e-12

    for step in range(steps):
        current_time = time[step]
        state = history[step]
        half = config.dt_ms / 2.0
        k1 = _derivative(current_time, state, config, stimulated)
        k2 = _derivative(current_time + half, state + half * k1, config, stimulated)
        k3 = _derivative(current_time + half, state + half * k2, config, stimulated)
        k4 = _derivative(current_time + config.dt_ms, state + config.dt_ms * k3, config, stimulated)
        history[step + 1] = state + config.dt_ms * (k1 + 2*k2 + 2*k3 + k4) / 6.0

    return ActiveCableResult(
        x,
        time,
        history[:, 0],
        history[:, 1],
        history[:, 2],
        history[:, 3],
        config.diffusion_number,
    )
