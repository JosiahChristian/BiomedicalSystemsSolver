# Scientific Release Policy

A release is created when the repository reaches a reproducible scientific or
software capability checkpoint. Routine documentation edits do not require a
release.

Each release must include:

1. a semantic version and annotated Git tag;
2. the exact governing equations and parameter provenance;
3. a machine-readable configuration for every reference run;
4. automated unit, regression, stability, and convergence results;
5. comparison with an analytical, manufactured, or published reference;
6. generated artifacts traceable to the release commit;
7. GitHub Pages and repository-size checks when browser assets are present;
8. explicit validated claims, limitations, and known discrepancies;
9. migration notes for changed APIs, configurations, or output schemas.

Version meaning:

- **Patch:** correction that does not change the governing model or public schema.
- **Minor:** backward-compatible model, experiment, or visualization capability.
- **Major:** governing-equation, unit-system, schema, or compatibility change.

Because the current refactor corrects model identity, units, boundaries, APIs,
outputs, and validation behavior after `v1.0.0`, its eventual validated release is
a `v2.0.0` candidate rather than a patch-level update.
