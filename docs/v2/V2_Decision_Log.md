# AgeLens V2 Decision Log

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-DL-001 |
| Version | 0.4 |
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
