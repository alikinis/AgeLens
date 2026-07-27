# AgeLens V2 Workspace

This directory contains the controlled transition from the completed V1 replication and mortality release to V2 external health validation and limited explainable innovation.

Current status: **Current public maintenance release: `v2.0.4`; prior public maintenance release: `v2.0.3`; earlier public maintenance releases: `v2.0.2` and `v2.0.1`; original scientific release: `v2.0.0`; V1 remains frozen on `main`**.

Gate 0 is closed. The governed primary non-mortality outcome is serious difficulty walking or climbing stairs (`DLQ050`) among canonical V1 participants age 20 years or older with positive `WTSAF4YR` and a valid outcome response.

Stage 2, restricted Stage 3, aggregate Stage 4, and the reviewed Stage 5 synthesis form the unchanged scientific V2 release. V2.0.1 corrected public-release integrity and portability; V2.0.2 completed repository documentation and snapshot tooling; V2.0.3 added cryptographic no-change coverage for public notebooks and scientific execution scripts; V2.0.4 repairs the GitHub Actions Python/dependency setup for those validators. The frozen EBM did not demonstrate incremental predictive benefit beyond Model C; Model C remains the preferred prediction model. Final ARISE submission, final manuscript claims, and merge to `main` remain separate and unauthorized.

## Documents

- `V2_0_4_Maintenance_Release.md`
- `V2_0_3_Maintenance_Release.md`
- `V2_0_2_Maintenance_Release.md`
- `V2_0_1_Maintenance_Release.md`
- `V2_ARISE_Abstract.md`
- `V2_ARISE_Alignment.md`
- `V2_ARISE_Presentation.md`
- `V2_Aggregate_Validation_Report.md`
- `V2_Analysis_Plan.md`
- `V2_Decision_Log.md`
- `V2_Environment.md`
- `V2_Evidence_Gap_Register.md`
- `V2_Final_Release.md`
- `V2_Outcome_Feasibility_Matrix.md`
- `V2_Research_Protocol.md`
- `V2_Stage0_Evidence_Audit.md`
- `V2_Stage1_Design_Rationale.md`
- `V2_Stage1_Freeze_Report.md`
- `V2_Stage2_Diagnostic_Review.md`
- `V2_Stage2_Implementation.md`
- `V2_Stage2_Release_Report.md`
- `V2_Stage3_Human_Review.md`
- `V2_Stage3_Implementation.md`
- `V2_Stage3_Release_Report.md`
- `V2_Stage4_Human_Review.md`
- `V2_Stage4_Implementation.md`
- `V2_Stage4_Method_Freeze_Report.md`
- `V2_Stage4_Method_Selection.md`
- `V2_Stage4_Release_Report.md`
- `V2_Stage5_Human_Review.md`
- `V2_Stage5_Implementation.md`
- `V2_Stage5_Release_Candidate.md`
- `V2_Stage5_Release_Report.md`
- `V2_Stage5_Synthesis.md`

## Governed Configurations

- `config/v2_0_4_maintenance.json`
- `config/v2_0_3_maintenance.json`
- `config/v2_0_2_maintenance.json`
- `config/v2_0_1_maintenance.json`
- `config/v2_final_release.json`
- `config/v2_gate0_freeze.json`
- `config/v2_outcome_candidates.json`
- `config/v2_stage1_design_draft.json`
- `config/v2_stage1_freeze.json`
- `config/v2_stage1_support_audit.json`
- `config/v2_stage2_implementation.json`
- `config/v2_stage2_release.json`
- `config/v2_stage2_review.json`
- `config/v2_stage3_implementation.json`
- `config/v2_stage3_release.json`
- `config/v2_stage4_implementation.json`
- `config/v2_stage4_method_freeze.json`
- `config/v2_stage4_release.json`
- `config/v2_stage5_release.json`
- `config/v2_stage5_release_candidate.json`
- `config/v2_stage5_synthesis.json`

## Validation Scripts

- `scripts/v2/01_outcome_feasibility_audit.py`
- `scripts/v2/02_validate_gate0_freeze.py`
- `scripts/v2/03_stage1_support_audit.py`
- `scripts/v2/04_validate_stage1_freeze.py`
- `scripts/v2/05_run_stage2_conventional_models.py`
- `scripts/v2/06_stage2_conventional_models.R`
- `scripts/v2/07_validate_stage2_results.py`
- `scripts/v2/08_run_stage2_diagnostic_review.py`
- `scripts/v2/09_stage2_diagnostic_review.R`
- `scripts/v2/10_validate_stage2_review.py`
- `scripts/v2/11_validate_stage2_release.py`
- `scripts/v2/12_run_stage3_transportability_prediction.py`
- `scripts/v2/13_stage3_transportability_prediction.R`
- `scripts/v2/14_validate_stage3_results.py`
- `scripts/v2/15_validate_stage3_release.py`
- `scripts/v2/16_validate_stage4_method_freeze.py`
- `scripts/v2/17_prepare_stage4_reference.R`
- `scripts/v2/18_run_stage4_ebm.py`
- `scripts/v2/19_validate_stage4_results.py`
- `scripts/v2/20_validate_stage4_release.py`
- `scripts/v2/21_build_stage5_synthesis.py`
- `scripts/v2/22_validate_stage5_release_candidate.py`
- `scripts/v2/23_validate_stage5_release.py`
- `scripts/v2/24_validate_v2_final_release.py`
- `scripts/v2/25_validate_v2_0_1_maintenance.py`
- `scripts/v2/26_validate_v2_0_2_maintenance.py`
- `scripts/v2/27_validate_v2_0_3_maintenance.py`
- `scripts/v2/28_validate_v2_0_4_maintenance.py`

## Gate 0 Result

The corrected pooled feasibility result for the primary outcome was:

- eligible canonical adults: 4,367;
- valid outcome responses: 4,366;
- positive responses: 682;
- survey-weighted prevalence: 11.77%;
- represented design: 30 strata and 60 PSUs.

The six-domain disability composite, fair/poor general health, and PHQ-9 score ≥10 remain secondary outcomes.

## Current Release Boundary

Current public maintenance release: `v2.0.4`.

Prior public maintenance release: `v2.0.3`.
Earlier public maintenance releases: `v2.0.2` and `v2.0.1`.
Original scientific release: `v2.0.0`. All earlier tags remain immutable.
V2.0.1 changed public-release hygiene and portability. V2.0.2 changed only
repository documentation and snapshot tooling. V2.0.3 expanded the invariant
to 108 artifacts: 79 governed configs/tables/figures, 14 public notebooks,
four analysis scripts, and 11 V2 scientific execution scripts. V2.0.4 changes
only CI Python selection, minimal validator dependency installation, runtime
verification, current metadata, historical-validator compatibility, and the
snapshot's current-validator pointer.

V1 remains frozen and separate on `main`. Final ARISE submission remains a
separate gate. Final manuscript claims, merge to `main`, and any new model,
feature, interaction, subgroup, or tuning search remain unauthorized.

Portable release validation:

```powershell
python .\scripts\v2\28_validate_v2_0_4_maintenance.py --project-root .
```

Environment details: `V2_Environment.md` and `requirements-v2.txt`. The minimal CI validator contract is recorded in `requirements-ci.txt`.

## Private Data Separation

Participant-level Parquet and raw XPT files remain outside the public Git repository. Only aggregate tables, validation logs, scripts, and public-safe metadata may be committed.


## Release Chronology Note

The sections below preserve the sequence of Stage 1 through Stage 5
authorizations. Statements that an action was “unauthorized” describe the gate
at that historical stage. D2-027 subsequently authorized V2.0.0, D2-028
authorized V2.0.1, D2-029 authorized the V2.0.2 documentation and tooling
maintenance release, and D2-030 authorizes the V2.0.3 invariant-coverage
maintenance release. No maintenance release alters any scientific result.

## Stage 1 Support Audit

The current Stage 1 package adds:

- `config/v2_stage1_design_draft.json`;
- `config/v2_stage1_support_audit.json`;
- `docs/v2/V2_Stage1_Design_Rationale.md`;
- `scripts/v2/03_stage1_support_audit.py`.

Run:

```powershell
python .\scripts\v2\03_stage1_support_audit.py --project-root .
```

This command reconstructs the governed exposure, audits covariate
completeness and subgroup support, and writes aggregate outputs only. It
does not fit an outcome model.


## Gate 1 Freeze

The frozen design is recorded in:

- `config/v2_stage1_freeze.json`;
- `docs/v2/V2_Stage1_Freeze_Report.md`.

Validate the local Stage 1 audit outputs with:

```powershell
python .\scripts\v2\04_validate_stage1_freeze.py --project-root .
```

This validator fits no model. Gate 1 has passed and the Stage 2 implementation is now available below.


## Stage 2 Conventional Models

The Stage 2 implementation adds:

- `config/v2_stage2_implementation.json`
- `config/v2_stage3_implementation.json`
- `config/v2_stage3_release.json`
- `config/v2_stage4_method_freeze.json`
- `config/v2_stage4_implementation.json`
- `config/v2_stage4_release.json`;
- `docs/v2/V2_Stage2_Implementation.md`;
- `scripts/v2/05_run_stage2_conventional_models.py`;
- `scripts/v2/06_stage2_conventional_models.R`;
- `scripts/v2/07_validate_stage2_results.py`
- `scripts/v2/12_run_stage3_transportability_prediction.py`
- `scripts/v2/13_stage3_transportability_prediction.R`
- `scripts/v2/14_validate_stage3_results.py`
- `scripts/v2/15_validate_stage3_release.py`
- `scripts/v2/16_validate_stage4_method_freeze.py`
- `scripts/v2/17_prepare_stage4_reference.R`
- `scripts/v2/18_run_stage4_ebm.py`
- `scripts/v2/19_validate_stage4_results.py`
- `scripts/v2/20_validate_stage4_release.py`.

Run from the repository root:

```powershell
python .\scripts\v2\05_run_stage2_conventional_models.py --project-root .
```

The orchestrator prepares participant-level input only in the private workspace, fits the frozen survey-weighted conventional models in R, writes aggregate results, and validates them in Python. Results remain provisional until reviewed.


## Stage 2 Diagnostic Review

The first conventional run found significant acceleration nonlinearity and a
small number of modified-Poisson fitted values above one. The prespecified
linear prevalence ratio remains provisional.

Run:

```powershell
python .\scripts\v2\08_run_stage2_diagnostic_review.py --project-root .
```

The review produces aggregate fitted-value diagnostics, exposure-range
sensitivities, a bounded adjusted-prevalence curve, and local five-year
prevalence ratios. It does not alter V1 or authorize release.


## Stage 2 Release

The governed Stage 2 release decision is recorded in:

- `config/v2_stage2_release.json`;
- `docs/v2/V2_Stage2_Release_Report.md`.

Validate it with:

```powershell
python .\scripts\v2\11_validate_stage2_release.py --project-root .
```

After validation passes, the aggregate Stage 2 implementation, results,
diagnostics, figure, and release record may be committed to
`v2-development`. Merge to `main` remains unauthorized.


## Stage 3 Implementation

Stage 3 adds four governed global transportability tests and bidirectional
cross-cycle prediction validation with 500 stratified-PSU bootstrap
replicates.

Run:

```powershell
python .\scripts\v2\12_run_stage3_transportability_prediction.py --project-root .
```

The command writes aggregate tables and figures only. Results remain
provisional until a separate Stage 3 review and release gate.

## Stage 3 Release

The governed decision is recorded in `config/v2_stage3_release.json`,
`docs/v2/V2_Stage3_Human_Review.md`, and
`docs/v2/V2_Stage3_Release_Report.md`.

Validate with:

```powershell
python .\scripts\v2\15_validate_stage3_release.py --project-root .
```

The release does not authorize biological subgroup interpretation, clinical
utility, participant-level risk prediction, explainable-model implementation,
or merge to `main`.


## Stage 4 Method Freeze

Stage 4 freezes exactly one explainable extension:

- `interpret.glassbox.ExplainableBoostingClassifier`;
- the same four predictors as Stage 3 Model C;
- main effects only (`interactions=0`);
- no hyperparameter search;
- primary comparison against Model C;
- bidirectional cycle holdout and 500 PSU-bootstrap replicates;
- global explanations only.

Validate with:

```powershell
python .\scripts\v2\16_validate_stage4_method_freeze.py --project-root .
```

After validation and commit to `v2-development`, implementation of this one
frozen model is authorized. No Stage 4 scientific claim, local explanation,
feature expansion, merge to `main`, or final manuscript claim is authorized.


## Stage 4 Release

The governed Stage 4 decision is recorded in:

- `config/v2_stage4_release.json`;
- `docs/v2/V2_Stage4_Human_Review.md`;
- `docs/v2/V2_Stage4_Release_Report.md`.

Validate with:

```powershell
python .\scripts\v2\20_validate_stage4_release.py --project-root .
```

The frozen EBM did not pass the positive incremental-extension rule. Model C
remains the preferred prediction model. The cycle-trained acceleration
functions may be reported only as aggregate descriptive global shapes.

Stage 5 synthesis and ARISE-package preparation are authorized. No local
explanation, new model or feature search, clinical claim, merge to `main`, or
final manuscript release is authorized.

<!-- AGELENS_STAGE5_BEGIN -->
## Historical Stage 5 Reviewed Aggregate Release

At the Stage 5 review gate, the aggregate synthesis and ARISE working
materials passed corrective review and were authorized for commit to
`v2-development`. At that historical point, final V2 release, final manuscript
claims, final ARISE submission, and merge to `main` remained unauthorized.
D2-027 later authorized V2.0.0; D2-028 authorizes the V2.0.1 maintenance
release. Model C remains preferred and Model D remains only a negative
incremental result and restricted descriptive global-shape sensitivity.

Run:

```powershell
python .\scripts\v2\21_build_stage5_synthesis.py --project-root .
python .\scripts\v2\22_validate_stage5_release_candidate.py --project-root .
python .\scripts\v2\23_validate_stage5_release.py --project-root .
```
<!-- AGELENS_STAGE5_END -->
