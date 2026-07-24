# AgeLens V2 Decision Log

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-DL-001 |
| Version | 0.9 |
| Status | Active — Gate 0 closed |
| Date | 2026-07-23 |

## D2-001 — Preserve V1 as the immutable baseline

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | V2 shall not alter the canonical V1 formula, governed V1 cohorts, V1 mortality estimand, or released V1 results. |
| Consequence | V2 code, protocols, outputs, and claims remain version-separated from V1. |

## D2-002 — Use a gated validation-before-innovation workflow

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Outcome feasibility, design freeze, and conventional external validation precede any explainable modeling extension. |
| Consequence | Machine-learning or AI work remains unauthorized before the relevant gates close. |

## D2-003 — Freeze the primary V2 outcome

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Serious difficulty walking or climbing stairs (`DLQ050`) is the primary V2 non-mortality outcome. Yes = 1, No = 0; refused, do-not-know, and missing responses are excluded. |
| Rationale | The item is directly aging-relevant, stable across both cycles, has no adult routing complication, and demonstrated nearly complete overlap, adequate positive support, similar cycle-specific prevalence, and full survey-design representation. |
| Empirical support | Pooled n = 4,366 valid of 4,367 eligible; 682 positive; weighted prevalence = 11.77%; 30 strata and 60 PSUs. |
| Consequence | The primary outcome may not be replaced after Stage 1 modeling begins. |

## D2-004 — Limit the explainable extension

| Field | Value |
| --- | --- |
| Status | Pending |
| Decision | At most one extension may be approved after conventional baselines are frozen. |
| Required closure | Resolve V2-EG-008 through V2-EG-012. |

## D2-005 — Govern the V2 survey weight

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Analyses retaining canonical V1 Phenotypic Age acceleration shall use `WTSAF4YR`, cycle-unique strata, and cycle-unique PSUs. |
| Consequence | Interview and full MEC weights are not substitutes for the primary V2 analytic dataset. |

## D2-006 — Freeze the common adult domain

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | The primary V2 domain is canonical V1 participants age 20 years or older with positive `WTSAF4YR` and a valid primary outcome response. |
| Empirical support | 4,367 eligible canonical adults and 4,366 valid `DLQ050` responses. |

## D2-007 — Normalize exact IBM XPORT zero sentinels

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Every V2 XPT file shall convert exact matches to `5.397605346934028e-79` to numeric zero immediately after import. No general near-zero threshold is permitted. |
| Consequence | The initial PHQ-9 aggregate is invalid and superseded; corrected results are governed. |

## D2-008 — Freeze the secondary outcome hierarchy

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | The six-domain disability composite is the secondary functional-health outcome; fair/poor general health is the secondary general-health outcome; PHQ-9 ≥10 is the secondary neuropsychiatric outcome. |
| Rationale | Each is available in both cycles and has adequate corrected support, but none is as direct and complete as `DLQ050` for the primary V2 claim. |
| Consequence | Secondary findings remain subordinate to the primary outcome and will be governed by the Stage 1 multiplicity hierarchy. |

## D2-009 — Close Gate 0

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | V2-EG-001 through V2-EG-004 are closed. Stage 1 design work is authorized; final modeling is not. |
| Validation | `scripts/v2/02_validate_gate0_freeze.py` must pass against the corrected aggregate outputs. |


## D2-010 — Protect V1 during Stage 1

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Stage 1 may write only V2 configuration, documentation, scripts, aggregate tables, and aggregate logs. |
| Consequence | Canonical V1, V1 mortality, and `main` release artifacts remain immutable. |

## D2-011 — Draft the primary prevalence-ratio estimand

| Field | Value |
| --- | --- |
| Status | Provisional pending support audit |
| Decision | The primary effect measure is an adjusted prevalence ratio per 5-year higher canonical Phenotypic Age acceleration. |
| Estimator | Survey-weighted quasi-Poisson log-link regression with design-based robust standard errors. |
| Interpretation | Associational and population-descriptive; not causal. |

## D2-012 — Draft the conventional model hierarchy

| Field | Value |
| --- | --- |
| Status | Provisional pending support audit |
| Decision | Model A uses a 4-df natural spline for age; Model B adds sex, race/ethnicity, and cycle; Model C adds acceleration per 5 years. |
| Consequence | No additional covariate or alternate functional form may be introduced without a documented amendment. |

## D2-013 — Authorize an aggregate-only Stage 1 support audit

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Covariate missingness and transportability support may be audited without fitting an outcome model. |
| Outputs | Aggregate missingness, support, acceleration, source-manifest, and check tables only. |


## D2-014 — Freeze the primary association design

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Use a survey-weighted quasi-Poisson log-link model to estimate the adjusted prevalence ratio per 5-year higher acceleration. |
| Adjustment | Fixed natural spline for age with knots 35, 50, and 65; sex; race/ethnicity; cycle. |
| Interpretation | Associational, not causal. |

## D2-015 — Retain all prespecified transportability levels

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Retain all prespecified sex, age-group, race/ethnicity, and cycle levels. |
| Evidence | Every level passed n, positive, negative, strata, and PSU support thresholds. |
| Guardrail | Use global interaction tests; avoid unsupported pairwise rankings. |

## D2-016 — Freeze the multiplicity hierarchy

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Primary alpha 0.05; Holm across three secondary outcomes; exploratory BH FDR 0.10 across four global interaction families. |

## D2-017 — Freeze bidirectional cross-cycle prediction validation

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Train survey-weighted logistic Models B and C in one cycle and test in the other, then reverse. |
| Primary metric | Pooled out-of-cycle weighted Brier-score difference, C minus B. |
| Uncertainty | 500 stratified PSU bootstrap replicate weights, seed 20260723. |

## D2-018 — Close Gate 1

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Stage 1 is complete and Stage 2 conventional modeling is authorized. |
| Restriction | Explainable modeling remains unauthorized until conventional and cross-cycle validation gates pass. |


## D2-019 — Authorize the Stage 2 conventional implementation

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Implement the frozen primary and secondary conventional association models using a private participant-level input and aggregate-only public outputs. |
| Primary implementation | Python reconstructs and reconciles the governed input; R `survey::svyglm` performs authoritative survey inference; Python validates aggregate outputs. |
| Restriction | A successful run does not itself authorize scientific release, transportability claims, prediction claims, or explainable modeling. |

## D2-020 — Freeze the acceleration-linearity sensitivity implementation

| Field | Value |
| --- | --- |
| Status | Approved |
| Decision | Retain the linear acceleration Model C as primary and test three nonlinear restricted-cubic-spline basis terms jointly using knots -30, -10, 0, 10, and 40 years. |
| Consequence | The sensitivity may identify nonlinearity but may not replace the primary estimand after results are inspected. |


## D2-021 — Hold Stage 2 release for diagnostic review

| Field | Value |
| --- | --- |
| Status | Approved |
| Trigger | Primary nonlinearity p = 0.00017697 and six primary fitted values above one, with a maximum of 11.93. |
| Decision | Retain the prespecified linear prevalence ratio as provisional and authorize a bounded nonlinear diagnostic review before release. |
| Guardrail | The review may characterize shape and robustness but may not silently replace the frozen primary estimand. |
| V1 consequence | None; V1 remains immutable. |


## D2-022 — Release Stage 2 conventional results for V2 development

| Field | Value |
| --- | --- |
| Status | Approved |
| Primary result | Adjusted PR 1.1476 per 5-year higher acceleration, 95% CI 1.0998–1.1974, p = 2.51e-07. |
| Nonlinearity | Retain the prespecified linear PR as a global summary; use the bounded spline curve to describe shape. |
| Fitted-value diagnostic | Six primary fitted values above one, representing 0.050% weighted and restricted beyond the weighted 99th percentile. |
| Secondary evidence | All three outcomes positive and significant after Holm correction. |
| Scope | Commit to `v2-development` authorized; merge to `main` and final public claims remain unauthorized. |
| Next step | Stage 3 transportability and cross-cycle validation implementation authorized. |
| V1 consequence | None; V1 remains immutable. |
