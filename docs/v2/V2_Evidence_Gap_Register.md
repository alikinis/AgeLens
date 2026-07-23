# AgeLens V2 Evidence Gap Register

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-EG-001 |
| Version | 0.4 |
| Status | Active — Gate 0 closed; Stage 1 design freeze in progress |
| Date | 2026-07-23 |

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
| V2-EG-005 | Core | How will missing outcome and covariate data be handled? | Primary-outcome missingness is negligible, but covariate missingness, complete-case rules, and sensitivity analyses must be frozen. | Under Review |
| V2-EG-006 | Core | What is the primary estimand and adjustment set? | Define cross-sectional estimand, effect measure, covariates, and interpretation as prognostic association rather than causation. | Open |
| V2-EG-007 | Core | How will multiple outcomes, subgroups, and interactions be controlled? | Freeze hierarchical testing and multiplicity rules before fitting. | Open |
| V2-EG-008 | Core | Which baseline and comparison models are justified? | Freeze chronological-age, demographic, and PhenoAge-augmented conventional models. | Under Review |
| V2-EG-009 | Core | Which performance metrics and thresholds will be used? | Define survey-aware discrimination, calibration, overall-error metrics, uncertainty, and success criteria. | Open |
| V2-EG-010 | Core | How will resampling or data splitting respect survey structure and prevent leakage? | Review primary methods and freeze a survey-aware validation design. | Open |
| V2-EG-011 | Important | Which subgroup analyses are sufficiently powered and ethically interpretable? | Define minimum positive/negative counts, design support, suppression rules, and interpretation limits. | Open |
| V2-EG-012 | Important | Which single explainable extension, if any, is justified? | Select at most one extension only after conventional baselines and validation design are frozen. | Open |
| V2-EG-013 | Important | Which Python and R tools will be used and reconciled? | Freeze packages, versions, and independent reconciliation checks. | Open |
| V2-EG-014 | Core | What exact V2 scope must be frozen for ARISE? | One primary endpoint, governed secondaries, incremental comparison, transportability analysis, and at most one explainable extension; final deliverables and cutoff remain to be frozen. | Under Review |

## Gate Rules

Gate 0 is closed.

No final primary model may be fit until V2-EG-005 through V2-EG-010 and V2-EG-014 are closed or explicitly dispositioned. Subgroup claims additionally require V2-EG-011. Explainable modeling additionally requires V2-EG-012.
