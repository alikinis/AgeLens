# AgeLens V2 Stage 4 Release Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S4R-002 |
| Version | 1.0 |
| Status | Released for V2 development |
| Date | 2026-07-24 |

## 1. Release Decision

The frozen main-effects Explainable Boosting Machine passed implementation,
result validation, and human review. The scientific gate decision is:

> **Pass for aggregate release; no positive explainable-extension claim.**

Negative and null findings are retained under the V2 protocol.

## 2. Incremental Performance

| Metric, Model D minus Model C | Estimate | 95% CI | Frozen decision |
| --- | ---: | ---: | --- |
| Brier score | -0.000970 | -0.003093 to 0.001152 | Improvement not supported |
| AUC | -0.000161 | -0.014073 to 0.013751 | Non-worse direction condition failed |

Model D calibration remained acceptable:

- intercept 0.002470
  (95% CI -0.036264 to 0.041205);
- slope 1.041231
  (95% CI 0.806893 to 1.275569).

Both direction-specific Brier point estimates were nonpositive, while AUC
differences were mixed. All 500 bootstrap replicates completed.

Authorized wording:

> Under the frozen bidirectional cross-cycle rule, the main-effects EBM did
> not demonstrate incremental predictive improvement beyond Model C within
> NHANES 2015–2018.

Model C remains the preferred prediction model. The result does not establish
that Model D is harmful; the intervals permit small benefit or small harm.

## 3. Global Acceleration Shape

The cycle-trained acceleration functions had Spearman correlation
0.980697 across 101
common eligible grid points, exceeding the frozen 0.70 threshold.

Authorized wording:

> The two cycle-trained acceleration term functions were highly
> rank-correlated over the governed common support.

This is a global descriptive shape result. It is not exact curve agreement,
a causal effect, a prevalence ratio, a clinical threshold, or a local
participant explanation.

## 4. Model and Reproducibility Controls

- exact `interpret==0.7.8`;
- Model C information set only;
- four main effects and zero interactions;
- no hyperparameter search;
- bidirectional cycle holdout;
- 500 stratified-PSU bootstrap replicates;
- Model C reconciliation within `1e-7`;
- aggregate-only public outputs;
- V1 immutable.

## 5. Authorization

Authorized:

- commit Stage 4 aggregate artifacts to `v2-development`;
- use the restricted negative-result and global-shape wording above;
- retain Model C as the preferred prediction model;
- begin Stage 5 synthesis, validation-report, and ARISE deliverables.

Not authorized:

- positive incremental-utility wording for Model D;
- Model D promotion as the primary prediction model;
- local explanation, individual risk, or clinical-utility products;
- further model, interaction, feature, or tuning searches;
- merge to `main`;
- final manuscript release.
