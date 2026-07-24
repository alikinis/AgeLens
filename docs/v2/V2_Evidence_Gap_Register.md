# AgeLens V2 Evidence Gap Register

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-EG-001 |
| Version | 1.2 |
| Status | Active — Stage 4 method frozen; implementation pending |
| Date | 2026-07-24 |

## Status Vocabulary

- **Open:** unresolved and may affect design or implementation.
- **Under Review:** evidence collection is active.
- **Dispositioned:** uncertainty remains but a governed handling rule is approved.
- **Closed:** sufficiently resolved for the authorized V2 scope.

## Register

| ID | Priority | Question | Current resolution or required evidence | Status |
| --- | --- | --- | --- | --- |
| V2-EG-001 | Core | Which non-mortality aging-related outcome family will be primary? | Functional mobility disability is primary; `DLQ050` is frozen by D2-003 after documentary and corrected empirical feasibility review. | Closed |
| V2-EG-002 | Core | Which exact variables and coding rules define each candidate outcome? | Primary and three secondary definitions are frozen in `config/v2_outcome_candidates.json` and `config/v2_gate0_freeze.json`. | Closed |
| V2-EG-003 | Core | What is the eligible age range and analytic population? | Canonical V1 participants age ≥20 with positive `WTSAF4YR` and a valid primary response; 4,366 primary complete cases. | Closed |
| V2-EG-004 | Core | Which survey weights, strata, and PSUs apply? | `WTSAF4YR` with cycle-unique strata and PSUs. | Closed |
| V2-EG-005 | Core | How will missing outcome and covariate data be handled? | Primary complete-case analysis frozen; all primary covariates have zero missingness. Secondary outcomes use outcome-specific complete cases. | Closed |
| V2-EG-006 | Core | What is the primary estimand and adjustment set? | Adjusted prevalence ratio per 5-year acceleration; fixed age spline, sex, race/ethnicity, and cycle. | Closed |
| V2-EG-007 | Core | How will multiple outcomes, subgroups, and interactions be controlled? | Primary alpha 0.05; Holm secondary family; exploratory BH q=0.10 across four global transportability tests. | Closed |
| V2-EG-008 | Core | Which baseline and comparison models are justified? | Frozen Models A–C with fixed age basis and parsimonious demographic adjustment. | Closed |
| V2-EG-009 | Core | Which performance metrics and thresholds will be used? | Weighted Brier difference primary; weighted AUC and calibration secondary; positive-claim rule frozen. | Closed |
| V2-EG-010 | Core | How will resampling or data splitting respect survey structure and prevent leakage? | Bidirectional cross-cycle validation with no random participant split; 500 stratified PSU bootstrap replicates for uncertainty. | Closed |
| V2-EG-011 | Important | Which subgroup analyses are sufficiently powered and ethically interpretable? | All prespecified levels pass support thresholds; global interaction tests and cautious level-specific interpretation frozen. | Closed |
| V2-EG-012 | Important | Which single explainable extension, if any, is justified? | Main-effects-only EBM selected and frozen with `interpret==0.7.8`, the Model C predictor set, zero interactions, no tuning, and global-only explanations. | Closed |
| V2-EG-013 | Important | Which Python and R tools will be used and reconciled? | R authoritative for survey inference; Python authoritative for audit; defined cross-language reconciliation targets and runtime version capture. | Closed |
| V2-EG-014 | Core | What exact V2 scope must be frozen for ARISE? | Primary association, three secondaries, four transportability families, cross-cycle incremental prediction, validation report, figures, and presentation are frozen. | Closed |

## Gate Rules

Gate 0 is closed.

Gate 1 is closed. Stage 2 and restricted Stage 3 results are released. V2-EG-012 is closed by the Stage 4 method freeze; implementation of the single frozen EBM may begin, while result claims remain blocked by V2-EG-018 and V2-EG-019.


## Stage 2 Result-Review Gap

| ID | Priority | Question | Current resolution or required evidence | Status |
| --- | --- | --- | --- | --- |
| V2-EG-015 | Core | Is the prespecified linear acceleration summary adequate for scientific release given significant nonlinearity and fitted values above one? | Retain the prespecified PR as a global linear summary; report strong nonlinearity with a bounded curve; bound violations are restricted to 0.050% weighted beyond p99. | Closed |


## Stage 3 Result-Review Gaps

| ID | Priority | Question | Current resolution or required evidence | Status |
| --- | --- | --- | --- | --- |
| V2-EG-016 | Core | Does the global linear acceleration summary vary across prespecified demographic or cycle dimensions? | Race/ethnicity passed BH control (q = 0.001023); sex, age group, and cycle did not. Release is restricted to the global linear summary under known nonlinearity. | Closed |
| V2-EG-017 | Core | Does acceleration improve prediction beyond age, sex, and race/ethnicity in an unseen NHANES cycle? | The frozen rule passed: Brier delta -0.003034 (95% CI -0.005222 to -0.000845), AUC delta 0.034051; 500/500 replicates completed. | Closed |


| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-018 | Core | Does a frozen main-effects EBM improve out-of-cycle prediction beyond Model C? | Implement the two cycle directions and the 500-replicate PSU bootstrap under the Stage 4 joint rule. | Open |
| V2-EG-019 | Important | Is the learned acceleration function reproducible across cycle-trained models? | Compare centered acceleration term functions on the common weighted 1st–99th percentile support; require Spearman correlation at least 0.70 for a stable-shape claim. | Open |
