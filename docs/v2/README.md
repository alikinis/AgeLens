# AgeLens V2 Workspace

This directory contains the controlled transition from the completed V1 replication and mortality release to V2 external health validation and limited explainable innovation.

Current status: **Stage 2 conventional results released for V2 development — Stage 3 authorized**.

Gate 0 is closed. The governed primary non-mortality outcome is serious difficulty walking or climbing stairs (`DLQ050`) among canonical V1 participants age 20 years or older with positive `WTSAF4YR` and a valid outcome response.

Stage 2 conventional association models are authorized. Transportability, predictive-performance, subgroup-claim release, and machine-learning models remain unauthorized in this step.

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

## Governed Configurations

- `config/v2_outcome_candidates.json`
- `config/v2_gate0_freeze.json`
- `config/v2_stage1_freeze.json`
- `config/v2_stage2_implementation.json`

## Validation Scripts

- `scripts/v2/01_outcome_feasibility_audit.py`
- `scripts/v2/02_validate_gate0_freeze.py`
- `scripts/v2/03_stage1_support_audit.py`
- `scripts/v2/04_validate_stage1_freeze.py`
- `scripts/v2/05_run_stage2_conventional_models.py`
- `scripts/v2/06_stage2_conventional_models.R`
- `scripts/v2/07_validate_stage2_results.py`

## Gate 0 Result

The corrected pooled feasibility result for the primary outcome was:

- eligible canonical adults: 4,367;
- valid outcome responses: 4,366;
- positive responses: 682;
- survey-weighted prevalence: 11.77%;
- represented design: 30 strata and 60 PSUs.

The six-domain disability composite, fair/poor general health, and PHQ-9 score ≥10 remain secondary outcomes.

## Immediate Next Step

Stage 2 conventional association results and diagnostic review have passed. Validate the release record before commit to `v2-development`.

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

- `config/v2_stage2_implementation.json`;
- `docs/v2/V2_Stage2_Implementation.md`;
- `scripts/v2/05_run_stage2_conventional_models.py`;
- `scripts/v2/06_stage2_conventional_models.R`;
- `scripts/v2/07_validate_stage2_results.py`.

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
