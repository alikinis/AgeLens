# AgeLens V2 Stage 4 Human Review

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S4H-001 |
| Version | 1.0 |
| Status | Complete — pass, no positive extension |
| Date | 2026-07-24 |
| Python build | `AgeLens-V2-Stage4-Python-20260724c` |
| R build | `AgeLens-V2-Stage4-R-20260724b` |

## 1. Review Scope

Human review covered the frozen EBM specification, exact software version,
both cross-cycle directions, Model C reconciliation, all 500 survey-bootstrap
replicates, calibration, global term structure, age and acceleration shapes,
shape stability, figures, correction history, and disclosure controls.

## 2. Integrity Findings

- The canonical input and primary domain reconciled to 5,223 and 4,366 rows,
  respectively, with 682 positive outcomes.
- Model C reconciled to the released Stage 3 point metrics with maximum
  absolute difference 1.62e-11.
- `interpret==0.7.8` was used.
- Each point EBM contained exactly four singleton main-effect terms and zero
  interactions.
- Both cross-cycle directions were evaluated without test-cycle training,
  binning, or early-stopping leakage.
- All 500 Model C and all 500 Model D replicate evaluations completed without
  failure.
- Public outputs contain aggregate global tables and figures only.
- V1 remained unmodified.

## 3. Incremental Prediction Review

Pooled Model D minus Model C results were:

- Brier delta = -0.000970
  (95% CI -0.003093 to 0.001152);
- AUC delta = -0.000161
  (95% CI -0.014073 to 0.013751);
- Model D calibration intercept = 0.002470
  (95% CI -0.036264 to 0.041205);
- Model D calibration slope = 1.041231
  (95% CI 0.806893 to 1.275569).

The Brier point estimate favored Model D in both directions, but the pooled
confidence interval crossed zero. Pooled AUC was essentially unchanged and
slightly negative; direction-specific AUC differences had opposite signs.

The frozen joint rule therefore failed on both the primary Brier-evidence
condition and the nonnegative pooled-AUC condition. Calibration, directional
Brier, shape stability, and bootstrap completion passed.

**Prediction decision:** no positive explainable-extension claim is
authorized. This is absence of supported incremental benefit, not evidence of
harm. Model C remains the preferred prediction model because the more complex
Model D did not establish added out-of-cycle value.

## 4. Global Explanation Review

The acceleration functions were compared over 101 eligible points within the
intersection of the two cycle-specific weighted 1st–99th percentile ranges.

- Spearman correlation = 0.980697;
- frozen minimum = 0.70;
- stable-rank-shape rule = passed.

The two functions show highly similar ordering across the governed range.
Their absolute levels are not identical, particularly in the low tail
(maximum observed absolute term-score difference
1.081 log-odds units). Rank stability must therefore
not be described as exact curve agreement.

The global acceleration functions may be reported as a descriptive shape
sensitivity. Centered term scores are not prevalence ratios, causal effects,
clinical thresholds, or individual explanations. Term-importance shares
remain model diagnostics only and may not be interpreted as scientific
effect-size rankings.

## 5. Correction-History Review

Three implementation corrections were reviewed:

1. the synthetic survey self-test was rebuilt to contain two PSUs per stratum;
2. current `survey::svyquantile` output was extracted through `coef()`;
3. interaction validation was changed from punctuation inspection to explicit
   term cardinality and feature mapping.

The first correction affected only the synthetic fixture. The second occurred
after all 500 Model C replicates were complete and preserved them. The third
occurred after all 500 EBM replicates were complete and changed only the
validator and public term schema. None changed the frozen predictors,
hyperparameters, fitted EBM models, bootstrap estimates, or scientific rule.

## 6. Figure and Disclosure Review

The performance figure correctly shows both pooled intervals crossing zero.
The acceleration figure displays only the governed common support and
aggregate cycle-trained term functions.

No participant identifier, individual probability, or local contribution is
present in the public Stage 4 tables. Private replicate weights and
participant-level prediction intermediates remain outside the repository.

## 7. Gate Decision

Stage 4 passes software and human review with a **no-positive-extension**
decision.

Authorized:

- commit Stage 4 implementation, aggregate results, and release records to
  `v2-development`;
- report that the frozen EBM did not demonstrate incremental predictive
  benefit beyond Model C;
- report the highly rank-correlated global acceleration functions with the
  stated explanation guardrails;
- retain Model C as the preferred prediction model;
- begin Stage 5 synthesis and ARISE-package preparation.

Not authorized:

- a positive EBM improvement claim;
- promotion of Model D as the primary prediction model;
- local explanations or participant-level risk outputs;
- new feature, model, interaction, or hyperparameter searches;
- clinical, causal, biological, or threshold claims;
- merge to `main` or final manuscript release.
