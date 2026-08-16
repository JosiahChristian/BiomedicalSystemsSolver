# Spatial Active-Axon Validation

## Governing model

The spatial solver couples the validated Hodgkin-Huxley membrane equations to
the unmyelinated cable equation:

```text
C_m dV/dt = I_stim - I_ion + (a / 2 R_i) d2V/dx2
```

The corresponding voltage diffusivity is derived rather than fitted:

```text
D = a / (2 R_i C_m)
```

The baseline uses a 0.0238 cm radius and 35.4 ohm-cm axial resistivity from the
classic squid giant-axon calculation. Sealed boundaries are implemented with
mirrored ghost nodes. Voltage and all gating variables are integrated together
using fixed-step RK4.

## Reproducible baseline result

```bash
python -m experiments.active_axon_reference
```

Current metrics:

- 101 of 101 nodes activated across 5 cm;
- peak membrane potential approximately 42.07 mV;
- conduction velocity approximately 18.74 m/s between 1 and 4 cm at 18.5 C;
- strictly ordered distal activation times;
- stable conduction velocity under time-step halving;
- no spontaneous wave without stimulation;
- all gating variables remain within [0, 1].

The tracked result includes hashes for the complete voltage field and activation
times. These fields can later drive a browser visualization without fabricating
the propagation animation.

## Published propagation comparison

Hodgkin and Huxley's 1952 propagated calculation reports 18.8 m/s at 18.5 C,
compared with an experimental value of 21.2 m/s for the fibre. Applying the
documented Q10=3 temperature scaling to gating kinetics produces approximately
18.74 m/s, a relative difference of about 0.31% from the published calculation.

The agreement emerges from the stated temperature law, axon radius, axial
resistivity, capacitance, and ionic equations. No display speed or fitted axial
coupling constant is used. The original 6.3 C reference trajectory remains
unchanged and separately fingerprinted.

The comparison does not claim reproduction of every point of the published
propagated waveform or clinical applicability to mammalian nerves. This remains
an unmyelinated squid giant-axon reference model.

Primary source:
<https://doi.org/10.1113/jphysiol.1952.sp004764>
