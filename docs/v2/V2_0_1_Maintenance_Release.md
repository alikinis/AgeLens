# AgeLens V2.0.1 Public Maintenance Release

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-MR-001 |
| Release | `v2.0.1` |
| Date | 2026-07-27 |
| Base release | `v2.0.0` |
| Base release commit | `d0a0ecfb9335cb5ef9f8c5f6e618db7ebe7ecc7b` |
| Status | Final public maintenance release authorized |

## Purpose

V2.0.1 corrects public-release hygiene, portability, metadata, environment,
documentation, and CI coverage defects identified after the immutable V2.0.0
release.

## Corrections

- removed rendered participant-level NHANES preview rows from three inherited
  public notebooks;
- changed only the three display statements that could recreate those rows;
- added fail-closed notebook-output scanning to repository preflight;
- made Stage 5 source-manifest hashing canonical-LF and line-ending
  independent;
- repaired Stage 5 validation in clean LF checkouts and GitHub source archives;
- made the V2.0.0 baseline validator usable without a Git checkout;
- added a portable V2.0.1 validator;
- reconciled current-facing README and protocol language with the superseding
  final-release decisions;
- completed the V2 document/config/script inventory;
- updated `CITATION.cff` to V2.0.1;
- added the recorded V2 analytical environment and `requirements-v2.txt`;
- added V2 release-integrity checks to GitHub Actions.

## Scientific Invariance

No outcome, cohort, exposure, covariate, estimand, model, interaction,
bootstrap result, aggregate scientific table, figure, or scientific conclusion
was changed. No new model, feature, subgroup, interaction, or tuning search was
performed.

The canonical-LF digest of 79 governed scientific configs, tables, and figures
remains:

`f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`

## Release Relationship

The `v2.0.0` tag and GitHub Release remain immutable. V2.0.1 supersedes V2.0.0
for public download and reproducibility use while preserving the original
scientific release history.

V1.0.1 remains separate on `main`. Merge to `main`, final ARISE submission,
final manuscript claims, and new scientific modeling remain unauthorized by
this maintenance decision.

## Portable Validation

From a Git checkout or an extracted GitHub source archive, run:

```bash
python scripts/v2/25_validate_v2_0_1_maintenance.py --project-root .
```
