# AgeLens V2.0.3 Invariant-Coverage Maintenance Release

## Release status

AgeLens V2.0.3 is authorized as a public maintenance release from
`v2-development`. The immutable V2.0.0, V2.0.1, and V2.0.2 tags and releases
remain unchanged. V1 remains frozen and separate on `main`.

## Reason for the release

The V2.0.2 maintenance validator correctly verified the current repository,
but its cryptographic invariant directly covered 79 governed configs, released
aggregate tables, and figures while its final no-change statement also named
notebooks and models. Independent ZIP comparison showed that the current
V2.0.2 notebooks and scientific scripts were unchanged, but future automated
regression coverage did not directly include those categories.

## Maintenance corrections

- preserve the prior 79-file scientific digest;
- add all 14 public notebooks to the invariant;
- add all four Python/R analysis scripts under `scripts/analysis`;
- add all 11 non-validator V2 scientific execution scripts under `scripts/v2`;
- record category counts and category-specific digests;
- add a portable V2.0.3 validator whose success wording matches its governed
  selection;
- retain portable historical V2.0.1 and V2.0.2 baseline validation;
- update the public snapshot builder and CI to execute the current validator;
- synchronize citation and current release metadata to V2.0.3.

## Cryptographic invariants

Prior governed config/table/figure invariant:

- file count: **79**;
- tree SHA-256: `f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`.

Expanded V2.0.3 invariant:

- file count: **108**;
- public notebooks: **14**;
- analysis scripts: **4**;
- V2 scientific execution scripts: **11**;
- tree SHA-256: `e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef`.

## Scientific boundary

No scientific config, cohort, estimand, model, feature, interaction, subgroup,
tuning exercise, notebook, analysis script, scientific execution script,
aggregate result, table, figure, or conclusion is changed. Model C remains the
preferred prediction model. Model D remains a negative incremental result and a
restricted descriptive global-shape sensitivity only.

Final ARISE submission, final manuscript claims, and merge to `main` remain
separate and unauthorized.

## Validation

```powershell
python .\scripts\v2\27_validate_v2_0_3_maintenance.py --project-root .
```

The validator is designed to run both in a Git checkout and in a GitHub source
archive without a `.git` directory.
