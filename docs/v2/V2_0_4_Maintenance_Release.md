# AgeLens V2.0.4 CI Runtime Maintenance Release

## Release status

AgeLens V2.0.4 is authorized as a public maintenance release from
`v2-development` after the hosted GitHub Actions workflow passes. The immutable
V2.0.0 through V2.0.3 tags and releases remain unchanged. V1 remains frozen and
separate on `main`.

## Publication metadata correction

The V2.0.4 maintenance work was completed on 2026-07-27. The public GitHub
Release was published at `2026-07-28T06:06:29Z`. V2.0.5 records that public
publication date without moving or rewriting the immutable V2.0.4 tag.

## Reason for the release

The V2.0.3 workflow selected Python 3.12 and immediately executed the Stage 5
and maintenance validator chain without installing dependencies. Stage 2 and
Stage 3 release validators import pandas, so a clean hosted runner could fail
with `ModuleNotFoundError` before repository validation began.

The first hosted V2.0.4 candidate run installed and verified the pinned
dependencies successfully, then exposed a separate shallow-checkout defect:
the default one-commit checkout did not contain the governed V2.0.0
pre-release commit required by the historical ancestry check.

## Maintenance corrections

- fetch complete Git history and tags with `fetch-depth: 0` so historical
  release ancestry checks can resolve their governed commits;
- use the Node 24-based `actions/setup-python@v6` action;
- select Python 3.13 in GitHub Actions;
- declare the minimal validator dependency contract in `requirements-ci.txt`;
- pin NumPy 2.4.6 and pandas 3.0.5 to the governed Stage 4 runtime record;
- install those dependencies before compiling or running validators;
- verify the Python minor line and pandas version in the hosted workflow;
- run the V2.0.4 portable validator and public snapshot builder in CI;
- update the snapshot builder to package `requirements-ci.txt` and execute the
  current validator;
- retain portable V2.0.1 through V2.0.3 historical validation.

## Scientific invariants

The 79-file digest remains `f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`. The expanded 108-file digest
remains `e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef`. No scientific config, cohort, estimand, model,
feature, interaction, subgroup, tuning exercise, notebook, analysis script,
scientific execution script, aggregate result, table, figure, or conclusion is
changed.

## Release gate

Commit and push to `v2-development` are authorized. The annotated `v2.0.4` tag
and public GitHub Release must be created only after the hosted
`repository-safety-check` workflow passes for the V2.0.4 commit.

Final ARISE submission, final manuscript claims, and merge to `main` remain
separate and unauthorized.

## Validation

```powershell
python .\scripts\v2\28_validate_v2_0_4_maintenance.py --project-root .
```

The validator is portable to a GitHub source archive without a `.git`
directory. The hosted workflow remains the authoritative test of dependency
installation on a clean GitHub Actions runner.
