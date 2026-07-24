# AgeLens V2 Stage 3 Release Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S3R-002 |
| Version | 1.0 |
| Status | Released for V2 development |
| Date | 2026-07-24 |

## 1. Release Decision

Stage 3 transportability and bidirectional cross-cycle prediction passed
software validation and human review. The decision is **pass with guardrails**.

## 2. Transportability Result

| Dimension | Raw p | BH q | Decision |
| --- | ---: | ---: | --- |
| Sex | 0.158775 | 0.264238 | Not supported |
| Age group | 0.198179 | 0.264238 | Not supported |
| Race/ethnicity | 0.000256 | 0.001023 | Supported |
| NHANES cycle | 0.435893 | 0.435893 | Not supported |

Authorized wording:

> The prespecified global linear association summary differed across
> race/ethnicity categories after BH control. No corresponding heterogeneity
> was supported for sex, age group, or NHANES cycle.

This is associational and population-descriptive. Because the acceleration
association is nonlinear, the interaction does not imply a constant
subgroup-specific effect over the full acceleration range. Race/ethnicity must
not be treated as an innate biological category, and pairwise subgroup ranking
is not authorized.

## 3. Incremental Prediction Result

- Brier delta C−B: -0.003034 (95% CI -0.005222 to -0.000845);
- AUC delta C−B: 0.034051 (95% CI 0.016474 to 0.051628);
- Model C calibration intercept: -0.000693 (95% CI -0.029543 to 0.028158);
- Model C calibration slope: 0.954494 (95% CI 0.818917 to 1.090071).

All 500 bootstrap replicates completed and both cycle directions favored
Model C on Brier and AUC.

Authorized wording:

> Canonical Phenotypic Age acceleration provided a modest improvement in
> pooled out-of-cycle prediction of serious mobility disability within NHANES
> 2015–2018 beyond flexible age, sex, and race/ethnicity.

No independent-cohort, individual-risk, threshold-benefit, causal, or clinical
utility claim is authorized.

## 4. Reproducibility and Disclosure

- Point predictions used survey-weighted logistic regression.
- Stabilized weighted-GLM metrics reconciled with authoritative Brier/AUC metrics.
- Uncertainty used 500 stratified-PSU bootstrap replicates and refitted both directions in every replicate.
- No participant-level prediction was written to the public repository.
- V1 remains immutable.

## 5. Authorization

Authorized:

- commit Stage 3 aggregate artifacts to `v2-development`;
- use the restricted Stage 3 wording above;
- begin Stage 4 method-selection governance.

Not authorized:

- implementation of an explainable model before a separate freeze;
- pairwise racial/ethnic ranking or biological interpretation;
- clinical-decision or individual-risk claims;
- merge to `main`;
- final manuscript release.
