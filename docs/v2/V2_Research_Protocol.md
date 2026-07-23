# AgeLens V2 Research Protocol

## Document Control

| Field | Value |
| --- | --- |
| Document title | AgeLens V2 Research Protocol |
| Document ID | AL-V2-RP-001 |
| Version | 0.1 |
| Status | Scoping Draft — no outcome analysis authorized |
| Date | 2026-07-23 |
| Relationship to V1 | V1 remains frozen as the canonical replication and mortality-validation baseline |

## 1. Purpose

AgeLens V2 moves from faithful replication toward controlled validation and innovation while preserving the evidence, traceability, proportional-complexity, and reproducibility principles established in V1.

V2 shall not retrospectively alter the canonical V1 formula, governed V1 cohort, V1 mortality estimand, or released V1 results. Any correction to V1 must follow the V1 governance process and remain distinct from V2 development.

## 2. Rationale

V1 established a reproducible implementation of Levine Phenotypic Age in NHANES 2015–2018, reconciled Python and R outputs, and completed survey-weighted all-cause mortality validation. The original V1 protocol reserved methodological improvements, alternative configurations, machine-learning extensions, and additional external validation for future work.

Because mortality validation has already been completed in V1, V2 will prioritize non-mortality aging-related validation, transportability, comparative performance, and a limited explainable modeling extension.

## 3. Primary Objective

To evaluate whether canonical V1 Phenotypic Age acceleration is associated with prespecified non-mortality aging-related health outcomes in NHANES 2015–2018 under the complex survey design.

## 4. Secondary Objectives

1. Evaluate transportability across prespecified demographic and survey-cycle groups.
2. Quantify incremental information beyond chronological age and a parsimonious demographic baseline.
3. Compare association, discrimination, and calibration across governed baseline models.
4. Evaluate one limited explainable modeling extension only after conventional models are frozen.
5. Produce an independently auditable, aggregate-only V2 release suitable for scientific review and ARISE presentation.

## 5. Research Questions

### RQ2-1 — External health validation

Is canonical V1 Phenotypic Age acceleration associated with prespecified morbidity, functional-health, or general-health outcomes after adjustment for chronological age and demographic covariates?

### RQ2-2 — Incremental utility

Does adding Phenotypic Age acceleration improve prespecified model-performance measures beyond chronological age and demographics?

### RQ2-3 — Transportability

Are effect estimates and model performance reasonably stable across sex, age groups, race/ethnicity groups, and NHANES cycle, subject to sample-size and multiplicity constraints?

### RQ2-4 — Controlled innovation

Does one prespecified explainable modeling extension provide reproducible out-of-sample improvement over governed conventional baselines without sacrificing interpretability?

### RQ2-5 — Reproducibility

Can all V2 findings be reconstructed from public-use NHANES data using documented, deterministic, aggregate-only workflows?

## 6. Scope

### 6.1 In Scope

- official outcome-module and variable-availability audit;
- morbidity, functional-health, or general-health external validation;
- complex-survey descriptive and regression analyses;
- prespecified transportability analyses;
- comparison with chronological-age and demographic baselines;
- survey-aware evaluation of discrimination and calibration where methodologically justified;
- one limited explainable modeling extension after baseline-model freeze;
- Python/R reconciliation where feasible;
- aggregate-only tables, figures, logs, and validation artifacts.

### 6.2 Out of Scope

- causal-effect claims;
- treatment or diagnostic recommendations;
- personalized clinical decision support;
- deep learning;
- unrestricted biomarker search;
- multi-omics or wearable integration;
- restricted-use NHANES data;
- post-hoc subgroup mining;
- silent replacement or retraining of the V1 canonical formula;
- outcome analysis before the required evidence gaps are dispositioned.

## 7. V2 Stages and Gates

### Stage 0 — Feasibility and evidence audit

Inventory candidate outcomes, cycles, variables, eligibility, survey weights, missingness, and official documentation.

**Gate 0:** approve the primary outcome family and analytic population.

### Stage 1 — Protocol freeze

Freeze outcome definitions, estimands, covariates, weights, subgroup hierarchy, missing-data policy, multiplicity strategy, and validation thresholds.

**Gate 1:** no primary modeling before all core design gaps are closed or explicitly dispositioned.

### Stage 2 — Conventional external validation

Run governed survey-aware descriptive and association models. Reconcile cohort counts and design variables.

**Gate 2:** conventional baseline results and checks pass.

### Stage 3 — Transportability and incremental performance

Run prespecified subgroup/interaction analyses and compare governed baseline models.

**Gate 3:** transportability limitations and performance metrics are documented without selective reporting.

### Stage 4 — Controlled explainable extension

Implement at most one prespecified extension. Use leakage-resistant training and evaluation procedures and compare it against frozen baselines.

**Gate 4:** extension must demonstrate reproducible value or be reported transparently as a negative result.

### Stage 5 — Release and ARISE package

Create aggregate outputs, validation report, concise research abstract, and a 5–10 minute presentation.

## 8. Non-Negotiable Principles

1. V1 remains immutable as the canonical baseline.
2. Evidence precedes implementation.
3. Primary outcomes and metrics are frozen before model fitting.
4. Survey design is part of the estimand, not an optional correction.
5. Negative and null findings are retained.
6. No subgroup claim is made without prespecification and adequate support.
7. Predictive performance and association are reported as distinct questions.
8. Explainability does not convert an observational association into a causal conclusion.
9. Only aggregate, disclosure-safe outputs enter the public release.

## 9. Immediate Authorization

This v0.1 protocol authorizes only:

- official documentation review;
- variable and cycle inventory;
- feasibility counts that do not expose participant-level data;
- creation and review of V2 governance documents.

It does not authorize final outcome modeling, subgroup testing, machine learning, or public scientific claims.
