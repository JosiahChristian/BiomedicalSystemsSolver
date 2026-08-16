# BiomedicalSystemsSolver

A computational-biophysics research project developing verified cardiovascular
and neural solvers that can ultimately drive interactive digital-twin
visualizations.

## Current verified scope

The repository currently contains four deliberately scoped models:

- **Hemodynamic momentum-diffusion baseline:** solves
  $\partial v/\partial t = \nu\,\partial^2v/\partial x^2$ on a one-dimensional
  axial domain with a prescribed inlet and selectable outlet boundary.
- **Passive neural cable baseline:** solves passive electrotonic voltage spread
  with leakage, a transient proximal stimulus, and sealed-end boundaries.
- **Active membrane reference:** solves the classical Hodgkin-Huxley sodium,
  potassium, leak, and gating equations with fourth-order Runge-Kutta integration.
- **Spatial active-axon model:** couples Hodgkin-Huxley membrane dynamics across
  an unmyelinated cable and measures activation time and conduction velocity.

These models establish dimensional consistency, boundary handling, explicit
time-step stability checks, and regression tests. The active membrane and axon
models implement Hodgkin-Huxley dynamics; the cardiovascular model is **not yet**
a complete pulsatile arterial-flow or wall-mechanics model.

## Reproducible execution

Requirements:

- Python 3.10+
- NumPy 1.24 through 2.x

Install the single runtime dependency:

```bash
python -m pip install -r requirements.txt
```

Run the verification suite:

```bash
python -m unittest discover -v
```

Run the command-line demonstrations:

```bash
python hemodynamic_solver.py
python nervous_impulse_solver.py
python hodgkin_huxley_solver.py
python -m experiments.hh_1952_reference
python active_axon_solver.py
python -m experiments.active_axon_reference
python -m experiments.export_solver_explorer
```

The final command generates `docs/index.html`, a standalone, zero-install
playback suitable for GitHub Pages, plus `docs/telemetry-playback.json`, a
compact provenance-bearing midpoint trace for external visualization clients.
Its illumination is indexed directly from
the active-axon voltage field and hemodynamic velocity field. It intentionally
does not render vessel contraction because the current cardiovascular solver
does not calculate pressure, compliance, or wall displacement.

## Numerical safeguards

Both explicit finite-difference solvers calculate their diffusion number and
reject configurations that violate the stability requirement
$D\Delta t/\Delta x^2 \leq 1/2$.

The tests currently verify:

- rejection of unstable configurations;
- preservation of uniform hemodynamic fields;
- enforcement of the configured outlet boundary;
- bounded cardiovascular velocities;
- preservation of neural resting potential without stimulus;
- transient depolarization and spatial propagation;
- finite and bounded neural voltage solutions.
- finite gating rates at removable singularities;
- stable unstimulated Hodgkin-Huxley resting behavior;
- bounded gating probabilities and stimulus-evoked action potentials;
- zero channel current at each corresponding reversal potential;
- deterministic reproduction of the active-membrane trajectory.
- convergence of action-potential peak voltage and timing under time-step refinement.
- full-length active-axon propagation and ordered activation times;
- finite emergent conduction velocity and time-step refinement agreement;
- spatial quiescence without stimulation and bounded cable gating variables.

GitHub Actions runs these numerical assertions on every push and pull request.
The CI matrix covers Python 3.10, 3.11, and 3.12 using the dependency bounds in
`requirements.txt`.

Independent CellML-engine comparison is an optional release-maintainer workflow,
not a normal user requirement. Its pinned dependency is isolated in
`requirements-validation.txt`, and the tracked comparison result allows ordinary
users to inspect the evidence without compiling libOpenCOR.

Release history is recorded in [CHANGELOG.md](CHANGELOG.md). Scientific release
requirements are defined in [docs/RELEASE_POLICY.md](docs/RELEASE_POLICY.md).

The Hodgkin-Huxley parameter and sign-convention provenance is pinned in
[`references/hodgkin_huxley_1952.json`](references/hodgkin_huxley_1952.json).
The reference experiment reports trace hashes and morphology metrics so its exact
output can be reproduced and compared across implementations.
The evidence and remaining limitation are recorded in
[`docs/validation/hodgkin_huxley_1952.md`](docs/validation/hodgkin_huxley_1952.md).
Spatial propagation evidence and its unresolved velocity discrepancy are recorded
in [`docs/validation/active_axon.md`](docs/validation/active_axon.md).

## Planned validated progression

1. Establish convergence studies for the baseline discretizations.
2. Validate the active Hodgkin-Huxley membrane model against published reference traces.
3. Independently reproduce the CellML trajectory and propagated waveform.
4. Add a closed-loop lumped cardiovascular circulation model.
5. Progress to compliant one-dimensional arterial flow with conservation tests.
6. Extend the browser playback to pressure and wall deformation only after the
   compliant-flow model passes conservation and benchmark tests.

Every visualization will be driven by solver state or by a documented reduced
model validated against the reference solver.

## Legacy image

The original demonstration matrix is retained as a historical project artifact;
it should not be interpreted as validation of the upgraded solvers.

![Biomedical Matrix Profile](biomedical_simulation_matrix.png)
