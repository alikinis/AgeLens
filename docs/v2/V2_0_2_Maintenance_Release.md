# AgeLens V2.0.2 Documentation and Tooling Maintenance Release

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-MR-002 |
| Release | `v2.0.2` |
| Date | 2026-07-27 |
| Base release | `v2.0.1` |
| Base release commit | `65726b0cd80947f3f724dccccdce7619cb1737b5` |
| Status | Final public documentation and tooling maintenance release authorized |

## Purpose

V2.0.2 closes the residual repository documentation and public-snapshot
tooling defects identified by an independent audit of the V2.0.1 GitHub
source archive.

## Corrections

- changed the root V2 quick-start to install `requirements-v2.txt`;
- reconciled the root software table with the governed Stage 4 runtime record;
- linked the Python badge and environment references to the V2 environment;
- completed the manual R dependency list and preserved the governed BioAge
  commit pin;
- included `requirements-v2.txt` in generated public snapshots;
- made the snapshot builder run the current portable V2 validator;
- added CI coverage for the current validator and generated snapshot path;
- synchronized current README and `CITATION.cff` metadata to V2.0.2;
- retained V2.0.1 as the historical public-integrity baseline validator.

## Scientific Invariance

No outcome, cohort, exposure, covariate, estimand, model, interaction,
bootstrap result, notebook analysis, aggregate scientific table, figure, or
scientific conclusion was changed. No new model, feature, subgroup,
interaction, or tuning search was performed.

The canonical-LF digest of 79 governed scientific configs, tables, and figures
remains:

`f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`

## Release Relationship

The `v2.0.0` and `v2.0.1` tags and GitHub Releases remain immutable. V2.0.2
supersedes V2.0.1 only for public documentation, environment guidance, and
repository snapshot tooling.

V1.0.2 remains separate on `main`. Merge to `main`, final ARISE submission,
final manuscript claims, and new scientific modeling remain unauthorized by
this maintenance decision.

## Portable Validation

From a Git checkout or an extracted GitHub source archive, run:

```bash
python scripts/v2/26_validate_v2_0_2_maintenance.py --project-root .
```
