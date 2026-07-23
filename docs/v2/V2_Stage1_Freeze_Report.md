# AgeLens V2 Stage 1 Freeze Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S1FR-001 |
| Version | 1.0 |
| Status | Complete — Gate 1 closed |
| Date | 2026-07-23 |

## 1. V1 Protection

Stage 1 changed no V1 formula, mapping, harmonization rule, canonical cohort, mortality cohort, mortality model, result, or release artifact. Development remains isolated on `v2-development`.

## 2. Empirical Support Audit

The primary domain contained 4,366 adults and 682 positive outcomes.

All five primary model inputs had zero missing values:

- chronological age;
- sex;
- race/ethnicity;
- cycle;
- canonical Phenotypic Age acceleration.

Every prespecified sex, age-group, race/ethnicity, and cycle level passed the frozen support thresholds.

The smallest positive counts were:

- Non-Hispanic Asian: 35;
- Other or multiracial: 40.

These categories remain separate. They will receive cautious interpretation and no unsupported pairwise ranking.

## 3. Frozen Primary Association

The primary effect measure is the adjusted prevalence ratio for serious difficulty walking or climbing stairs per 5-year higher canonical Phenotypic Age acceleration.

The authoritative estimator is a survey-weighted quasi-Poisson log-link model with design-based robust standard errors, `WTSAF4YR`, cycle-unique strata and PSUs, and survey-domain analysis.

Chronological age uses a fixed natural-spline basis with internal knots at 35, 50, and 65 years and boundary knots at 20 and 80 years.

The primary model adjusts for:

- flexible chronological age;
- sex;
- race/ethnicity;
- NHANES cycle;
- canonical acceleration per 5 years.

The estimate remains associational and must not be interpreted causally.

## 4. Frozen Multiplicity Hierarchy

- Primary `DLQ050` test: two-sided alpha 0.05.
- Three secondary outcomes: Holm familywise adjustment.
- Four global transportability interactions: exploratory Benjamini–Hochberg FDR 0.10.
- Sensitivity analyses: supportive only.

## 5. Frozen Cross-Cycle Prediction Validation

Incremental prediction is separate from the prevalence-ratio association model.

Survey-weighted logistic models will be trained in one NHANES cycle and evaluated in the other, then reversed:

1. train 2015–2016, test 2017–2018;
2. train 2017–2018, test 2015–2016.

The fixed age basis is identical in both cycles. Prediction models omit a cycle term because the test cycle is unseen during training.

Primary incremental metric:

- pooled out-of-cycle survey-weighted Brier-score difference, Model C minus Model B.

Secondary metrics:

- weighted AUC difference;
- calibration-in-the-large;
- calibration slope.

Uncertainty uses 500 stratified PSU bootstrap replicate weights with deterministic seed `20260723`.

A positive incremental-utility claim requires favorable Brier improvement with a 95% interval excluding zero, non-worse AUC direction, and no material calibration failure.

## 6. Software Roles

R is authoritative for complex-survey inference and prediction evaluation. Python is authoritative for data audit, cohort reconciliation, outcome coding, exposure reconstruction, and aggregate validation.

Runtime package versions will be recorded automatically. Cross-language agreement is required for counts, weighted prevalence, acceleration construction, and model-input row counts.

## 7. Gate 1 Decision

V2-EG-005 through V2-EG-011, V2-EG-013, and V2-EG-014 are closed.

Gate 1 is closed. Stage 2 conventional modeling is authorized. The explainable extension remains unauthorized.
