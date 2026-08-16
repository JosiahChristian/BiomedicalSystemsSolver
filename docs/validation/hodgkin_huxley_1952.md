# Hodgkin-Huxley 1952 Reference Validation

## Sources

- Hodgkin, A. L. & Huxley, A. F. (1952), *A quantitative description of
  membrane current and its application to conduction and excitation in nerve*,
  The Journal of Physiology 117, 500-544.
  DOI: <https://doi.org/10.1113/jphysiol.1952.sp004764>
- Physiome Model Repository, original-variant CellML model, revision
  `c4bf1ccd5013023efcf79d8ba740fda6f427514b`:
  <https://models.physiomeproject.org/workspace/hodgkin_huxley_1952/file/c4bf1ccd5013023efcf79d8ba740fda6f427514b/hodgkin_huxley_1952_variant01.cellml>

The publication is the primary scientific source. The pinned CellML revision is
the executable specification used to check parameters, initial conditions,
stimulus timing, units, and sign convention.

## Convention transformation

The CellML original variant retains the 1952 convention, in which resting
voltage is zero and depolarization is negative. This repository uses the modern
absolute membrane-potential convention:

```text
V_modern = -V_original - 65 mV
I_modern = -I_original
```

Consequently:

| Quantity | Original convention | Modern convention |
|---|---:|---:|
| Initial voltage | 0 mV | -65 mV |
| Sodium reversal | -115 mV | +50 mV |
| Potassium reversal | +12 mV | -77 mV |
| Leak reversal | -10.613 mV | -54.387 mV |
| Reference stimulus | -20 uA/cm2 | +20 uA/cm2 |

The conversion is checked automatically in
`tests/test_hodgkin_huxley_reference.py`.

## Reproduction protocol

- Capacitance: 1 uF/cm2
- Maximum sodium conductance: 120 mS/cm2
- Maximum potassium conductance: 36 mS/cm2
- Leak conductance: 0.3 mS/cm2
- Initial gates: m=0.05, h=0.6, n=0.325
- Stimulus: 20 uA/cm2 from 10.0 ms through 10.5 ms
- Duration: 50 ms
- Integration: fixed-step RK4, dt=0.01 ms

Run:

```bash
python -m experiments.hh_1952_reference
```

The tracked summary in `results/hh_1952_reference_summary.json` includes the
reference-file hash, voltage-trace hash, output metrics, and gate bounds.

## Current evidence

- parameter and initial-condition agreement with the pinned CellML model;
- exact, tested original-to-modern convention transformation;
- finite rates at removable singularities;
- stable unstimulated resting state;
- an evoked action potential with after-hyperpolarization and recovery;
- gating variables constrained to probability bounds;
- deterministic output and a stable trace fingerprint;
- peak voltage and timing convergence when the time step is halved.

## Independent-engine comparison

The pinned CellML model was independently executed with libOpenCOR 1.20260803.0
using fixed-step RK4 at 0.01 ms. All 5,001 samples of voltage, m, h, and n were
compared point-by-point after applying the documented convention transformation.

- maximum absolute voltage difference: 2.84e-12 mV;
- maximum absolute gate difference: less than 2e-14;
- identical peak time: 12.05 ms;
- peak voltage difference: approximately 1e-14 mV.

The engine source commit, CellML hash, per-state maximum error, and RMS error are
recorded in `results/libopencor_comparison_summary.json`. This clears the
independent-engine scientific validation blocker for the single-cell trajectory.
