# Changelog

All notable changes to BiomedicalSystemsSolver are recorded here. Releases use
semantic versioning and must identify the validated scientific scope.

## Unreleased

## v2.1.0 - 2026-08-15

### Added

- Standalone solver-driven browser playback for the active-axon voltage field
  and hemodynamic velocity field.
- Deterministic exporter and tests that bind the visual data to the Python
  solvers and disclose the cardiovascular model boundary.

## v2.0.0 — 2026-08-15

### Added

- Importable cardiovascular and neural solver modules.
- Explicit unit-bearing configuration objects and numerical stability guards.
- Passive neural cable model with transient stimulation and sealed boundaries.
- Classical single-compartment Hodgkin-Huxley active membrane reference.
- Pinned 1952 publication and Physiome CellML provenance manifest.
- Reproducible reference experiment with trace hashing and morphology metrics.
- Spatial Hodgkin-Huxley active-axon solver with activation-time and emergent
  conduction-velocity measurement.
- Explicit Q10 temperature scaling and reproduction of the published 18.8 m/s
  propagated velocity to within the declared benchmark tolerance.
- Reproducible voltage-field and activation-time fingerprints.
- Independent 5,001-sample voltage-and-gate trajectory comparison using pinned
  libOpenCOR and CellML revisions.
- Thirty-five numerical, boundary, regression, electrophysiology, provenance,
  propagation, and convergence tests.
- Reproducible command-line experiments for all three current models.

### Changed

- Cardiovascular output is now correctly identified as a reduced
  momentum-diffusion baseline rather than complete arterial hemodynamics.
- Neural output distinguishes passive electrotonic spread from an active action
  potential.
- CI now runs numerical assertions and each smoke experiment exactly once.
- Documentation states current limitations and the validated progression.

### Corrected

- Hemodynamic outlet-boundary handling.
- Neural stimulus duration and sealed-end treatment.
- Node counts, spatial dimensions, units, and terminus reporting.
- Previous documentation claims that were not implemented by the solver.

### Release blockers

- Confirm a clean GitHub Actions run on the release candidate commit.

## v1.0.0

- Original cardiovascular diffusion and passive neural demonstration scripts.
- Initial biomedical simulation matrix and GitHub Actions smoke execution.
