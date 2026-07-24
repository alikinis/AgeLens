# AgeLens V2 Analysis Plan

## Version 1.4 — Stage 3 Release and Stage 4 Method Selection

This document defines the frozen Stage 0 elements and the remaining decisions required before final modeling.

## 1. Frozen V1 Inputs

V2 consumes the governed V1 canonical Phenotypic Age and cycle-specific survey-weighted Phenotypic Age acceleration definitions without modification.

## 2. Frozen Primary Outcome

The primary outcome is serious difficulty walking or climbing stairs (`DLQ050`):

- Yes = 1;
- No = 0;
- refused, do-not-know, and missing = excluded.

The primary domain is canonical V1 participants age ≥20 with positive `WTSAF4YR` and a valid outcome response.

Corrected pooled feasibility:

- eligible n = 4,367;
- valid n = 4,366;
- positive n = 682;
- weighted prevalence = 11.77%;
- 30 strata and 60 PSUs.

## 3. Frozen Secondary Outcomes

1. any six-domain disability;
2. fair/poor self-rated health;
3. complete PHQ-9 score ≥10.

The initial pre-correction PHQ-9 aggregate is invalid and superseded.

## 4. Frozen Survey Design

All analyses retaining canonical V1 exposure shall use:

- `WTSAF4YR`;
- cycle-unique strata;
- cycle-unique PSUs.

## 5. Provisional Primary Estimand and Estimator

The frozen primary estimand is the adjusted prevalence ratio associated with a
5-year higher canonical Phenotypic Age acceleration.

The frozen estimator is `survey::svyglm` with a quasi-Poisson family and log
link, design-based robust standard errors, `WTSAF4YR`, cycle-unique strata and
PSUs, survey-domain analysis, and design degrees of freedom.

## 6. Provisional Conventional Model Hierarchy

- **Model A:** natural spline of chronological age with 4 degrees of freedom;
- **Model B:** Model A plus sex, race/ethnicity, and NHANES cycle;
- **Model C:** Model B plus canonical Phenotypic Age acceleration per 5 years.

Model C is the draft primary inference model. Additional covariates require
explicit scientific justification.

## 7. Stage 1 Decisions Required

Before final modeling, freeze:

- the primary estimand;
- prevalence ratio, odds ratio, or another justified effect measure;
- covariate coding;
- missing-data policy;
- multiplicity hierarchy;
- subgroup and interaction support thresholds;
- incremental-performance metrics;
- survey-aware internal validation or resampling;
- success and failure thresholds;
- software and reconciliation plan;
- ARISE deliverable scope.

## 8. Transportability

Potential dimensions remain:

- sex;
- age group;
- race/ethnicity;
- NHANES cycle.

No subgroup model is authorized before support, multiplicity, and reporting rules are frozen.

## 9. Controlled Explainable Extension

No extension is authorized. A future amendment may approve at most one interpretable method after the endpoint, estimand, conventional baselines, and validation design are frozen.

## 10. Release Checks

The final V2 pipeline must include:

- deterministic cohort reconciliation;
- survey-design reconciliation;
- outcome coding checks;
- missingness audit;
- model convergence and finite covariance checks;
- multiplicity audit;
- subgroup support checks;
- performance-metric reproducibility;
- independent software reconciliation where feasible;
- aggregate-only release preflight;
- manuscript and abstract consistency checks.


## 11. Stage 1 Support Audit

Before Gate 1 closes, `scripts/v2/03_stage1_support_audit.py` must:

- reproduce the 4,366-person primary domain and 682 positive outcomes;
- reconstruct cycle-specific weighted acceleration with mean-zero checks;
- audit demographic covariate missingness;
- enumerate sex, age-group, race/ethnicity, and cycle support;
- apply provisional support thresholds;
- export aggregate tables only;
- fit no outcome model.


## 12. Frozen Cross-Cycle Prediction Design

Prediction uses survey-weighted logistic Models B and C with the same fixed
age spline. Models are trained in one cycle and tested in the other, then
reversed. Pooled out-of-cycle predictions are evaluated using weighted
Brier score, weighted AUC, calibration-in-the-large, and calibration slope.

Uncertainty uses 500 stratified PSU bootstrap replicate weights with seed
`20260723`.

## 13. Stage 2 Authorization

Gate 1 is closed. The frozen conventional association models may now be
implemented. The explainable extension remains blocked.


## 14. Stage 2 Conventional Outputs

The governed Stage 2 run must produce aggregate-only files for:

- the primary Model C prevalence ratio;
- the primary Model A–C hierarchy;
- the three secondary Model C estimates with Holm adjustment;
- model convergence and fitted-value diagnostics;
- the fixed nonlinear acceleration sensitivity;
- runtime versions and release checks.

The participant-level CSV used by R is private and must remain outside the Git repository. Statistical significance is not a software acceptance criterion.


## 16. Stage 2 Interpretation Rule

The prespecified quasi-Poisson prevalence ratio is reported as the global
linear summary.

Because both governed spline tests detect nonlinearity, the adjusted
prevalence curve and fixed local five-year ratios accompany the primary
coefficient. These diagnostics do not replace the frozen primary estimand.

The slight low-tail dip is not interpreted as protective. Modified-Poisson
fitted values are not interpreted as individual probabilities.

## 17. Stage 3 Authorization

Transportability interaction models and bidirectional cross-cycle prediction
validation may now be implemented under the frozen Gate 1 design. Their
scientific claims remain blocked until separate validation and release.


## 18. Stage 3 Implementation

Transportability uses four global design-based acceleration-interaction tests
with BH q=0.10. Level estimates are descriptive unless the corresponding
global test is supported.

Cross-cycle prediction evaluates frozen Models B and C in both cycle
directions. Pooled out-of-cycle Brier difference is primary; AUC and
calibration are secondary. Five hundred stratified-PSU bootstrap replicates
refit both directions and propagate training and testing uncertainty.

Stage 3 claims require result validation, human review, and the restricted wording in the Stage 3 release record.

## 19. Stage 3 Release Decision

Only race/ethnicity passed the four-family BH interaction rule
(q = 0.001023). This finding concerns the frozen global linear summary;
sex, age group, and NHANES cycle interactions were not supported.

Model C improved pooled out-of-cycle Brier score
(delta C−B = -0.003034, 95% CI -0.005222 to -0.000845)
and AUC (delta C−B = 0.034051, 95% CI 0.016474 to
0.051628). Calibration met the frozen rule and 500/500 replicates
completed.

## 20. Stage 3 Interpretation Restrictions

Transportability remains a global-linear-summary analysis under known
nonlinearity. Cross-cycle prediction is within NHANES 2015–2018 under the
governed cycle-specific acceleration definition. No causal, biological,
independent-cohort, individual-risk, threshold-benefit, or clinical-utility
claim is authorized.

## 21. Stage 4 Authorization Boundary

Stage 4 method selection and protocol drafting are authorized. No explainable
model may be implemented until one method, comparator, leakage controls,
metrics, and failure criteria are frozen separately.
