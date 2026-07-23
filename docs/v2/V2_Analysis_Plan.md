# AgeLens V2 Analysis Plan

## Version 1.0 — Gate 1 Frozen Analysis Design

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
