# AgeLens V2 Analysis Plan

## Version 0.1 — Feasibility Only

This document is intentionally provisional. It defines what may be investigated during Stage 0 and identifies the analyses that must remain locked until protocol freeze.

## 1. V1 Baseline Inputs

V2 will consume the governed V1 canonical Phenotypic Age and cycle-specific survey-weighted Phenotypic Age acceleration definitions without modifying them.

The following V1 features remain fixed:

- target cycles: NHANES 2015–2016 and 2017–2018;
- canonical Supplement conversion pair;
- laboratory bridging and unit transformations;
- exact XPORT zero-sentinel handling;
- age-topcode flag;
- V1 reproducibility and aggregate-release restrictions.

## 2. Stage 0 Candidate Outcome Inventory

Candidate domains to investigate for availability and validity include:

1. general health status;
2. chronic-disease or multimorbidity burden;
3. physical or functional limitation;
4. disability or activities-of-daily-living measures;
5. other aging-relevant health constructs supported in both target cycles.

This list is not an authorization to analyze or combine these outcomes. Each candidate requires an official variable map, eligibility rule, survey-design rule, and construct justification.

## 3. Required Feasibility Table

For each candidate outcome, Stage 0 will record:

- NHANES component and file;
- variable names and labels;
- availability by cycle;
- eligible age range;
- skip-pattern and missing codes;
- unweighted eligible count;
- weighted prevalence or distribution;
- applicable weight;
- strata and PSU compatibility;
- overlap with the V1 canonical cohort;
- scientific rationale;
- known limitations;
- recommendation: retain, secondary only, or exclude.

Only aggregate counts and percentages may be exported.

## 4. Provisional Conventional Model Hierarchy

The exact model family will depend on the selected outcome.

A provisional nested hierarchy is:

- **Model A:** chronological age;
- **Model B:** chronological age plus sex, race/ethnicity, and NHANES cycle;
- **Model C:** Model B plus canonical Phenotypic Age acceleration.

Additional covariates require explicit justification. Model C is intended to evaluate incremental prognostic information, not causal effects.

## 5. Provisional Effect Scale

The default exposure scale remains a 5-year higher canonical Phenotypic Age acceleration, with a weighted-standard-deviation scale considered secondary.

Effect measures must match the outcome type and may include:

- prevalence odds ratios for binary outcomes;
- proportional-odds estimates for defensible ordinal outcomes;
- mean differences for continuous outcomes;
- count-model estimates for count outcomes.

No model family is final until outcome coding and assumptions are approved.

## 6. Transportability

Potential prespecified dimensions are:

- sex;
- age group;
- race/ethnicity;
- NHANES cycle.

Before analysis, the project must define:

- minimum unweighted and survey-design support;
- whether interaction tests or stratified estimates are primary;
- multiplicity control;
- rules for suppressing unstable estimates;
- interpretation limits for health-disparity findings.

## 7. Incremental Performance

Any claim that PhenoAge adds predictive value must compare frozen models using prespecified metrics.

Candidate metric families include:

- discrimination;
- calibration;
- overall prediction error;
- uncertainty intervals.

The project must resolve how survey weights and clustered design enter validation and resampling before computing final performance claims.

## 8. Controlled Explainable Extension

No extension is authorized in v0.1.

A future amendment may approve one interpretable method, provided that:

1. the endpoint and conventional baselines are frozen;
2. data leakage is prevented;
3. tuning is separated from final evaluation;
4. performance improvement is evaluated with uncertainty;
5. explanations are stability-checked;
6. negative results are reported;
7. the method does not generate causal or clinical-treatment claims.

## 9. Release Checks

The final V2 pipeline must include:

- deterministic cohort reconciliation;
- survey-design reconciliation;
- outcome coding checks;
- model convergence and finite covariance checks;
- subgroup support checks;
- multiplicity audit;
- performance-metric reproducibility;
- Python/R or independent-software comparison where feasible;
- aggregate-only release preflight;
- manuscript/abstract consistency checks.

## 10. Stage 0 Deliverable

Stage 0 ends with:

- a completed outcome-feasibility matrix;
- a recommended primary outcome family;
- one or more excluded candidates with documented reasons;
- proposed final estimands and models;
- updated Evidence Gap and Decision records.

No scientific result from candidate-outcome screening will be promoted as a V2 finding.
