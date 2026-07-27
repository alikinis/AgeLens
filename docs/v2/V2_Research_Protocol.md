# AgeLens V2 Research Protocol

## Document Control

| Field | Value |
| --- | --- |
| Document title | AgeLens V2 Research Protocol |
| Document ID | AL-V2-RP-001 |
| Version | 1.6 |
| Status | Final public maintenance release `v2.0.4`; V2.0.3, V2.0.2, V2.0.1, and V2.0.0 preserved; V1 frozen on `main` |
| Date | 2026-07-27 |
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

## 9. Historical Authorization Sequence

The protocol previously authorized Stage 1 design work:

- methodological source review;
- missingness and covariate feasibility audits;
- model and estimand specification;
- multiplicity and subgroup-support rules;
- performance-metric and validation design;
- governance-document updates.

At the pre-final Stage 5 point, Gate 1 was closed and Stage 2, restricted Stage 3, aggregate Stage 4, and the reviewed Stage 5 working package were released for V2 development. The frozen EBM did not pass the positive incremental-extension rule, and Model C remained the preferred prediction model. The then-pending final-release gate was later resolved by D2-027 for V2.0.0. D2-028 authorized the V2.0.1 public-integrity corrections, D2-029 authorized only the V2.0.2 documentation and repository-tooling corrections, D2-030 authorizes only the V2.0.3 invariant-coverage correction, and D2-031 authorizes only the V2.0.4 CI-runtime correction. ARISE submission, final manuscript claims, and merge to `main` remain separate.


## 10. Stage 1 Design Draft

The current design draft specifies an adjusted prevalence ratio per
5-year higher canonical Phenotypic Age acceleration, estimated using a
survey-weighted quasi-Poisson log-link model.

The draft conventional hierarchy is:

1. flexible chronological age;
2. flexible chronological age plus sex, race/ethnicity, and cycle;
3. the demographic model plus canonical acceleration.

These elements remain provisional until the aggregate covariate and
transportability support audit is reviewed. No outcome model is authorized.


## 11. Gate 1 Freeze

The frozen primary estimand, models, multiplicity hierarchy,
transportability plan, cross-cycle validation design, and software roles
are recorded in `config/v2_stage1_freeze.json` and
`docs/v2/V2_Stage1_Freeze_Report.md`.

Stage 2 may fit only the frozen conventional association models. Any
departure requires a documented amendment before results are inspected.


## 12. Stage 2 Implementation Authorization

The governed Stage 2 implementation is recorded in `config/v2_stage2_implementation.json` and `docs/v2/V2_Stage2_Implementation.md`.

Stage 2 may reconstruct private model input, fit Models A–C for the primary outcome, fit governed Model C secondary analyses, and run the frozen acceleration-linearity sensitivity. Only aggregate outputs may enter the public repository.

Stage 2 results are not automatically released by a successful software run. Human review and a separate decision are required. Transportability, cross-cycle prediction, and explainable modeling remain outside this implementation step.


## 13. Stage 2 Release Decision

Stage 2 conventional association results passed implementation, diagnostic,
and release validation.

The primary linear prevalence ratio is retained as a prespecified global
summary. Scientific interpretation must acknowledge strong nonlinearity and
use the bounded adjusted-prevalence curve to describe shape.

Stage 3 transportability and cross-cycle validation implementation is
authorized. Explainable modeling remains blocked.


## 14. Stage 3 Implementation Authorization

The four prespecified transportability dimensions and bidirectional
cross-cycle Model B versus Model C comparison may now be implemented.

The cross-cycle uncertainty analysis uses 500 survey bootstrap replicates and
refits both training directions in every replicate. Participant-level
predictions remain private and are not exported.

Stage 3 results remain provisional. Transportability claims, incremental
prediction claims, explainable modeling, and merge to `main` require separate
release decisions.

## 15. Stage 3 Release Decision

Race/ethnicity was supported after BH control (q = 0.001023); sex,
age-group, and cycle interaction families were not. This is a global-linear
summary under known nonlinearity, not a causal or biological subgroup claim.

Model C showed modest incremental out-of-cycle performance within NHANES:
Brier delta C−B = -0.003034 (95% CI -0.005222 to
-0.000845) and AUC delta C−B = 0.034051 (95% CI
0.016474 to 0.051628). Calibration met the frozen rule and all 500
replicates completed.

Stage 4 method selection is complete. Implementation of the one frozen
main-effects EBM is authorized after freeze validation and commit; Stage 4
result claims, merge to `main`, and final manuscript release remain unauthorized.


## 16. Stage 4 Explainable Method Freeze

The sole explainable extension is Model D, a main-effects-only
`ExplainableBoostingClassifier` pinned to `interpret==0.7.8`.

Model D uses the same information set as Stage 3 Model C. It adds no new
biomarker and no interaction term. The primary question is whether flexible
additive age and acceleration functions improve out-of-cycle prediction beyond
the released conventional Model C.

Validation retains both cycle directions and 500 stratified-PSU bootstrap
replicates. A positive claim requires a favorable Brier interval, non-worse
AUC, acceptable calibration, no Brier deterioration in either direction,
stable acceleration functions across cycle-trained models, and complete
bootstrap execution.

Only global explanations are authorized. Local explanations, individual risk
scores, causal feature effects, clinical thresholds, biological subgroup
interpretation, black-box explainers, feature expansion, and hyperparameter
search remain prohibited.

Implementation of the frozen Model D is authorized after validation and commit
of this freeze. Scientific release requires a separate Stage 4 human review
and release gate.


## 17. Stage 4 Release Decision

The frozen main-effects EBM completed both cross-cycle directions and 500/500
survey-bootstrap replicates.

Model D minus Model C:

- Brier delta = -0.000970
  (95% CI -0.003093 to 0.001152);
- AUC delta = -0.000161
  (95% CI -0.014073 to 0.013751).

The primary interval crossed zero and pooled AUC delta was negative. The
frozen joint positive-extension rule failed. Model D is not promoted as the
primary prediction model, and no positive incremental-benefit claim is
authorized.

The cycle-trained acceleration functions passed the frozen rank-stability rule
(Spearman 0.980697). They may be reported only
as aggregate descriptive global functions. Rank similarity is not exact curve
agreement and does not authorize causal, threshold, biological, clinical, or
individual interpretation.

Model C remains the preferred prediction model. No additional model, feature,
interaction, or tuning search is authorized.

## 18. Historical Stage 5 Authorization

Stage 5 may:

- synthesize released Stage 2–4 findings;
- prepare aggregate validation tables and figures;
- prepare the abstract and ARISE presentation;
- document null and negative findings without suppression;
- prepare a final release candidate for separate review.

Stage 5 may not introduce new fitted models or post-result optimization.
Local explanations, participant-level risk outputs, clinical-utility claims,
merge to `main`, and final manuscript release remain unauthorized pending a
separate final gate.

<!-- AGELENS_STAGE5_BEGIN -->
## Stage 5 Reviewed Release

At the Stage 5 review gate, the aggregate synthesis and ARISE working materials passed corrective review and were released for commit to `v2-development`. That historical gate fit no model, opened no participant-level analytic data, changed no V1 artifact, and retained all null, negative, nonlinear, and transportability restrictions. D2-027 later authorized V2.0.0. D2-028 authorizes the V2.0.1 public maintenance release; final ARISE submission, final manuscript claims, and merge to `main` remain separate unauthorized gates.
<!-- AGELENS_STAGE5_END -->


<!-- AGELENS_V2_FINAL_RELEASE_BEGIN -->
## Original V2.0.0 Final Release

AgeLens V2 final public release `v2.0.0` is authorized from the governed
`v2-development` branch.

The release retains Model C as the preferred prediction model, preserves
the negative Model D incremental result, and retains all observational,
transportability, external-validation, clinical-utility, and disclosure
limitations.

V1 remains frozen and separate on `main`. Final ARISE submission, final
manuscript claims, merge to `main`, and any new model, feature,
interaction, subgroup, or tuning search remain unauthorized through this
release.
<!-- AGELENS_V2_FINAL_RELEASE_END -->


## V2.0.1 Maintenance Release

D2-028 authorizes V2.0.1 as a public maintenance release. It removes rendered
participant-level notebook previews, makes Stage 5 source-manifest hashing
line-ending independent, adds portable release validation, reconciles current
documentation and citation metadata, records the V2 analytical environment,
and expands CI coverage.

The V2.0.0 scientific release remains immutable. No scientific config, cohort,
outcome, estimand, model, aggregate result table, figure, or conclusion is
changed. V1 remains separate on `main`. Final ARISE submission, final
manuscript claims, merge to `main`, and new scientific modeling remain
unauthorized.
