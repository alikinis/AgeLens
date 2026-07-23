# AgeLens V2 Analysis Plan

## Version 0.4 — Gate 0 Closed; Stage 1 Design Freeze

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

## 5. Provisional Conventional Model Hierarchy

The current nested hierarchy remains provisional until Gate 1:

- **Model A:** chronological age;
- **Model B:** chronological age plus sex, race/ethnicity, and NHANES cycle;
- **Model C:** Model B plus canonical Phenotypic Age acceleration.

Additional covariates require explicit scientific justification.

## 6. Stage 1 Decisions Required

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

## 7. Transportability

Potential dimensions remain:

- sex;
- age group;
- race/ethnicity;
- NHANES cycle.

No subgroup model is authorized before support, multiplicity, and reporting rules are frozen.

## 8. Controlled Explainable Extension

No extension is authorized. A future amendment may approve at most one interpretable method after the endpoint, estimand, conventional baselines, and validation design are frozen.

## 9. Release Checks

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
