# AgeLens V2 Stage 3 Implementation

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S3I-001 |
| Version | 0.1 |
| Status | Implementation authorized — results pending |
| Date | 2026-07-24 |

## 1. Purpose

Stage 3 implements the two remaining conventional-validation components frozen
at Gate 1:

1. transportability of the prespecified global linear acceleration summary;
2. bidirectional cross-cycle incremental prediction.

No Stage 3 scientific claim is released by this implementation package.

## 2. V1 and Stage 2 Protection

Stage 3 reads the private Stage 2 model input. It does not reconstruct or alter
V1, change the Stage 2 primary outcome, replace the Stage 2 global prevalence
ratio, or revise the Stage 2 nonlinear interpretation.

## 3. Transportability

Four global design-based interaction tests are implemented:

- sex;
- age group: 20–49, 50–64, and 65+;
- race/ethnicity;
- NHANES cycle.

Each model uses the frozen survey-weighted quasi-Poisson log-link estimator and
adjustment set. The four global interaction p-values receive Benjamini–Hochberg
control at q = 0.10.

Level-specific prevalence ratios are reported with uncertainty. They are
interpreted as supported interaction estimates only when their dimension's
global test passes the multiplicity rule; otherwise they remain descriptive.

Because Stage 2 detected strong acceleration nonlinearity, these interactions
refer only to transportability of the prespecified global linear summary.

## 4. Cross-Cycle Prediction

Two independent directions are evaluated:

1. train in 2015–2016 and test in 2017–2018;
2. train in 2017–2018 and test in 2015–2016.

Model B contains fixed flexible age, sex, and race/ethnicity. Model C adds
canonical Phenotypic Age acceleration. No cycle term is used because the test
cycle is unseen during training.

## 5. Performance Metrics

Primary incremental metric:

- pooled out-of-cycle survey-weighted Brier-score difference, Model C minus
  Model B; negative values favor Model C.

Secondary metrics:

- pooled out-of-cycle weighted AUC difference;
- calibration-in-the-large;
- calibration slope.

Direction-specific values are descriptive. The pooled estimates receive full
training-and-testing uncertainty.

## 6. Survey Bootstrap

The pooled primary-domain survey design is converted to 500 bootstrap
replicate weights with `survey::as.svrepdesign`. Each replicate refits Models B
and C in both training cycles and reevaluates the opposite test cycle. Variance
is calculated with the replicate design's governed scaling factors.

The deterministic seed is `20260723`. Any failed replicate stops the release
checks.

## 7. Positive Incremental-Utility Rule

A positive claim requires all four conditions:

1. the 95% interval for Brier delta C−B is below zero;
2. the AUC delta point estimate is nonnegative;
3. Model C calibration-intercept interval contains zero;
4. Model C calibration-slope interval contains one.

Failure of this joint rule is reported as no positive incremental-utility
claim; continuous metrics are still retained.

## 8. Public Outputs

Only aggregate tables, two figures, runtime versions, checks, and a validation
JSON are public. Participant identifiers and out-of-cycle participant-level
predictions are never written to the repository.

## 9. Gate Status

Transportability, prediction, explainable-modeling, and merge-to-main claims
remain unauthorized until Stage 3 outputs receive human review and a separate
release decision.
