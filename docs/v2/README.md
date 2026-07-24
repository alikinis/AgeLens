# AgeLens V2 Workspace

This directory contains the controlled transition from the completed V1 replication and mortality release to V2 external health validation and limited explainable innovation.

Current status: **Stage 4 released — no positive EBM extension; Stage 5 synthesis authorized**.

Gate 0 is closed. The governed primary non-mortality outcome is serious difficulty walking or climbing stairs (`DLQ050`) among canonical V1 participants age 20 years or older with positive `WTSAF4YR` and a valid outcome response.

Stage 2, restricted Stage 3, and aggregate Stage 4 results are released for V2 development. The frozen EBM did not demonstrate incremental predictive benefit beyond Model C; Model C remains the preferred prediction model. Merge to `main` remains unauthorized.

## Documents

- `V2_Research_Protocol.md`
- `V2_Evidence_Gap_Register.md`
- `V2_Decision_Log.md`
- `V2_Analysis_Plan.md`
- `V2_ARISE_Alignment.md`
- `V2_Outcome_Feasibility_Matrix.md`
- `V2_Stage0_Evidence_Audit.md`
- `V2_Stage1_Design_Rationale.md`
- `V2_Stage1_Freeze_Report.md`
- `V2_Stage2_Implementation.md`
- `V2_Stage3_Implementation.md`
- `V2_Stage3_Human_Review.md`
- `V2_Stage3_Release_Report.md`
- `V2_Stage4_Method_Selection.md`
- `V2_Stage4_Method_Freeze_Report.md`
- `V2_Stage4_Implementation.md`
- `V2_Stage4_Human_Review.md`
- `V2_Stage4_Release_Report.md`

## Governed Configurations

- `config/v2_outcome_candidates.json`
- `config/v2_gate0_freeze.json`
- `config/v2_stage1_freeze.json`
- `config/v2_stage2_implementation.json`
- `config/v2_stage3_implementation.json`
- `config/v2_stage3_release.json`
- `config/v2_stage4_method_freeze.json`
- `config/v2_stage4_implementation.json`
- `config/v2_stage4_release.json`

## Validation Scripts

- `scripts/v2/01_outcome_feasibility_audit.py`
- `scripts/v2/02_validate_gate0_freeze.py`
- `scripts/v2/03_stage1_support_audit.py`
- `scripts/v2/04_validate_stage1_freeze.py`
- `scripts/v2/05_run_stage2_conventional_models.py`
- `scripts/v2/06_stage2_conventional_models.R`
- `scripts/v2/07_validate_stage2_results.py`
- `scripts/v2/12_run_stage3_transportability_prediction.py`
- `scripts/v2/13_stage3_transportability_prediction.R`
- `scripts/v2/14_validate_stage3_results.py`
- `scripts/v2/15_validate_stage3_release.py`
- `scripts/v2/16_validate_stage4_method_freeze.py`

## Gate 0 Result

The corrected pooled feasibility result for the primary outcome was:

- eligible canonical adults: 4,367;
- valid outcome responses: 4,366;
- positive responses: 682;
- survey-weighted prevalence: 11.77%;
- represented design: 30 strata and 60 PSUs.

The six-domain disability composite, fair/poor general health, and PHQ-9 score ≥10 remain secondary outcomes.

## Immediate Next Step

Validate and commit the Stage 4 release, then begin Stage 5 aggregate synthesis, validation-report, and ARISE-package work. No further model or feature search is authorized.

## Private Data Separation

Participant-level Parquet and raw XPT files remain outside the public Git repository. Only aggregate tables, validation logs, scripts, and public-safe metadata may be committed.


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
