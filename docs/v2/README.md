# AgeLens V2 Workspace

This directory contains the controlled transition from the completed V1 replication and mortality release to V2 external health validation and limited explainable innovation.

Current status: **Gate 1 closed — Stage 2 conventional modeling authorized**.

Gate 0 is closed. The governed primary non-mortality outcome is serious difficulty walking or climbing stairs (`DLQ050`) among canonical V1 participants age 20 years or older with positive `WTSAF4YR` and a valid outcome response.

No final V2 association, transportability, predictive-performance, subgroup, or machine-learning model is authorized yet.

## Documents

- `V2_Research_Protocol.md`
- `V2_Evidence_Gap_Register.md`
- `V2_Decision_Log.md`
- `V2_Analysis_Plan.md`
- `V2_ARISE_Alignment.md`
- `V2_Outcome_Feasibility_Matrix.md`
- `V2_Stage0_Evidence_Audit.md`

## Governed Configurations

- `config/v2_outcome_candidates.json`
- `config/v2_gate0_freeze.json`

## Validation Scripts

- `scripts/v2/01_outcome_feasibility_audit.py`
- `scripts/v2/02_validate_gate0_freeze.py`

## Gate 0 Result

The corrected pooled feasibility result for the primary outcome was:

- eligible canonical adults: 4,367;
- valid outcome responses: 4,366;
- positive responses: 682;
- survey-weighted prevalence: 11.77%;
- represented design: 30 strata and 60 PSUs.

The six-domain disability composite, fair/poor general health, and PHQ-9 score ≥10 remain secondary outcomes.

## Immediate Next Step

Stage 1 must freeze:

1. primary estimand and effect measure;
2. adjustment set and nested conventional models;
3. outcome and covariate missing-data rules;
4. multiplicity hierarchy;
5. transportability support thresholds;
6. incremental-performance metrics and survey-aware validation method;
7. the exact ARISE-ready V2 scope.

Final modeling remains blocked until the Stage 1 evidence gaps are closed or explicitly dispositioned.

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

This validator fits no model. After it passes, the next governed step is
implementation of the frozen Stage 2 conventional association models.
