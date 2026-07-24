# AgeLens V2 Stage 3 Human Review

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S3H-001 |
| Version | 1.0 |
| Status | Complete — pass with guardrails |
| Date | 2026-07-24 |
| Reviewed build | `AgeLens-V2-Stage3-20260724e` |

## 1. Review Scope

Human review covered the four global transportability tests, all 13
level-specific estimates, transportability diagnostics, both cross-cycle
prediction directions, the 500-replicate survey bootstrap, calibration,
software reconciliation, figures, and aggregate-only release checks.

## 2. Integrity Findings

- The primary domain reconciled to 4,366 participants and 682 positive outcomes.
- All four interaction models converged with finite coefficients and covariance matrices and no warnings.
- Both cross-cycle prediction directions converged without warnings.
- All 500 stratified-PSU bootstrap replicates completed; none failed.
- Authoritative `svyglm` and stabilized weighted-`glm` Brier/AUC metrics reconciled within `1e-7`.
- Public outputs are aggregate tables and figures only.
- V1 remained unmodified.

## 3. Transportability Review

Only race/ethnicity passed the frozen BH interaction rule:

- raw p = 0.00025587275;
- BH q = 0.001023491.

Sex, age group, and NHANES cycle did not pass BH q=0.10.

The supported result is restricted to heterogeneity in the prespecified global
linear acceleration summary. It does not establish a constant association over
the acceleration range, a causal interaction, an innate biological difference,
or a pairwise ranking of racial/ethnic groups.

Stage 2 established strong acceleration nonlinearity. In Stage 3, the
modified-Poisson interaction models produced fitted values above one for 6–14
observations depending on the model, including 14 in the race/ethnicity model.
These fitted values are not probabilities. The race/ethnicity level with the
fewest positive outcomes had 35 events, so the widest subgroup intervals
require restraint.

**Transportability decision:** release the global race/ethnicity interaction
finding with these restrictions. Retain all other dimension estimates as
descriptive null interaction results.

## 4. Cross-Cycle Prediction Review

Pooled out-of-cycle results:

- Brier delta C−B = -0.003034 (95% CI -0.005222 to -0.000845);
- AUC delta C−B = 0.034051 (95% CI 0.016474 to 0.051628);
- Model C calibration intercept = -0.000693 (95% CI -0.029543 to 0.028158);
- Model C calibration slope = 0.954494 (95% CI 0.818917 to 1.090071).

Both cycle directions showed lower Brier score and higher AUC for Model C.
The frozen joint incremental-utility rule passed.

The authorized interpretation is a **modest incremental out-of-cycle
predictive improvement within NHANES 2015–2018**. This is not independent
external-cohort validation, a clinical decision-utility result, or an
individual risk-product release.

## 5. Figure Review

The performance figure correctly displays the Brier interval below zero and
the AUC interval above zero. The transportability forest plot contains all
prespecified levels; the table reporting roles and this report govern
interpretation. Only race/ethnicity is a supported interaction family.

## 6. Gate Decision

Stage 3 passes human review with guardrails.

- Stage 3 aggregate results may be committed to `v2-development`.
- Restricted transportability and prediction claims are authorized.
- Stage 4 method selection may begin.
- No explainable model is yet authorized for implementation.
- Merge to `main` and final manuscript claims remain unauthorized.
