# AgeLens V2.0.5 Release-Date Metadata Maintenance

## Release status

AgeLens V2.0.5 is authorized as a public metadata-only maintenance release
from `v2-development` after the hosted GitHub Actions workflow passes. The
immutable V2.0.0 through V2.0.4 tags and releases remain unchanged. V1 remains
frozen and separate on `main`.

## Reason for the release

The V2.0.4 maintenance work was recorded as 2026-07-27, while its public
GitHub Release was actually published at `2026-07-28T06:06:29Z`. The previous record
did not distinguish the maintenance-work date from the public publication
timestamp.

## Metadata corrections

- record the V2.0.4 public GitHub publication timestamp as `2026-07-28T06:06:29Z`;
- retain 2026-07-27 explicitly as the V2.0.4 maintenance-work date;
- synchronize current citation and public-maintenance metadata to V2.0.5 with
  release date 2026-07-28;
- retain portable V2.0.1 through V2.0.4 historical validation;
- update CI and the public snapshot builder to execute the V2.0.5 validator.

## Scientific invariants

The 79-file digest remains `f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`. The expanded 108-file digest remains
`e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef`. No scientific config, cohort, estimand, model, feature,
interaction, subgroup, tuning exercise, notebook, analysis script, scientific
execution script, aggregate result, table, figure, or conclusion is changed.

## Release gate

Commit and push to `v2-development` are authorized. The annotated `v2.0.5`
tag and public GitHub Release must be created only after the hosted
`repository-safety-check` workflow passes for the V2.0.5 commit.

Final ARISE submission, final manuscript claims, and merge to `main` remain
separate and unauthorized.

## Validation

```powershell
python .\scripts\v2\29_validate_v2_0_5_maintenance.py --project-root .
```
