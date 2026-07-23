# AgeLens V2 Research Protocol

## Document Control

| Field | Value |
| --- | --- |
| Document title | AgeLens V2 Research Protocol |
| Document ID | AL-V2-RP-001 |
| Version | 0.2 |
| Status | Gate 0 complete — Stage 1 design freeze authorized |
| Date | 2026-07-23 |
| Relationship to V1 | V1 remains frozen as the canonical replication and mortality-validation baseline |

## 1. Purpose

AgeLens V2 moves from faithful replication toward controlled external validation and innovation while preserving the evidence, traceability, proportional-complexity, and reproducibility principles established in V1.

V2 shall not retrospectively alter the canonical V1 formula, governed V1 cohorts, V1 mortality estimand, or released V1 results.

## 2. Rationale

V1 established a reproducible implementation of Levine Phenotypic Age in NHANES 2015–2018, reconciled Python and R outputs, and completed survey-weighted all-cause mortality validation.

V2 prioritizes non-mortality aging-related validation, transportability, incremental performance, and at most one limited explainable modeling extension.

## 3. Frozen Primary Outcome

The primary V2 non-mortality outcome is:

> Serious difficulty walking or climbing stairs (`DLQ050`).

The governed analysis domain is canonical V1 participants age 20 years or older with positive `WTSAF4YR` and a valid `DLQ050` response.

The corrected Stage 0 audit identified 4,366 valid responses among 4,367 eligible canonical adults, 682 positive responses, 11.77% survey-weighted prevalence, and full representation of 30 strata and 60 PSUs.

## 4. Primary Objective

To evaluate whether canonical V1 Phenotypic Age acceleration is associated with serious difficulty walking or climbing stairs under the NHANES complex survey design.

## 5. Secondary Objectives

1. Evaluate the six-domain disability composite, fair/poor general health, and PHQ-9 score ≥10 as secondary outcomes.
2. Evaluate transportability across prespecified demographic and survey-cycle groups.
3. Quantify incremental information beyond chronological age and a parsimonious demographic baseline.
4. Compare association, discrimination, and calibration across governed baseline models.
5. Evaluate one limited explainable modeling extension only after conventional models are frozen.
6. Produce an independently auditable, aggregate-only V2 release suitable for scientific review and ARISE presentation.

## 6. Research Questions

### RQ2-1 — External functional-health validation

Is canonical V1 Phenotypic Age acceleration associated with serious difficulty walking or climbing stairs after governed adjustment?

### RQ2-2 — Secondary health validation

Are associations directionally consistent across broader disability, general-health, and depressive-symptom outcomes?

### RQ2-3 — Incremental utility

Does adding Phenotypic Age acceleration improve prespecified performance measures beyond chronological age and demographics?

### RQ2-4 — Transportability

Are effect estimates and model performance reasonably stable across prespecified groups, subject to support and multiplicity constraints?

### RQ2-5 — Controlled innovation

Does one prespecified explainable extension provide reproducible out-of-sample improvement over governed conventional baselines?

## 7. V2 Stages and Gates

### Stage 0 — Feasibility and evidence audit

**Status: complete.** Primary outcome, adult domain, survey weight, and design variables are frozen.

### Stage 1 — Protocol and estimand freeze

Freeze estimand, effect measure, covariates, missing-data policy, model hierarchy, multiplicity strategy, subgroup support thresholds, performance metrics, and ARISE scope.

**Gate 1:** no primary modeling before all core Stage 1 gaps are closed or explicitly dispositioned.

### Stage 2 — Conventional external validation

Run governed survey-aware descriptive and association models. Reconcile cohort counts and design variables.

### Stage 3 — Transportability and incremental performance

Run prespecified interaction or stratified analyses and compare governed baseline models.

### Stage 4 — Controlled explainable extension

Implement at most one prespecified extension using leakage-resistant evaluation.

### Stage 5 — Release and ARISE package

Create aggregate outputs, validation report, abstract, and a 5–10 minute presentation.

## 8. Non-Negotiable Principles

1. V1 remains immutable.
2. Evidence precedes implementation.
3. Outcomes, estimands, and metrics are frozen before fitting.
4. Survey design is part of the estimand.
5. Negative and null findings are retained.
6. No unsupported subgroup claims are made.
7. Association and predictive performance are distinct questions.
8. Explainability does not create causal interpretation.
9. Only aggregate, disclosure-safe outputs enter the public release.

## 9. Immediate Authorization

This v0.2 protocol authorizes only Stage 1 design work:

- methodological source review;
- missingness and covariate feasibility audits;
- model and estimand specification;
- multiplicity and subgroup-support rules;
- performance-metric and validation design;
- governance-document updates.

It does not authorize final outcome modeling, subgroup testing, predictive-performance claims, machine learning, or public V2 scientific claims.
