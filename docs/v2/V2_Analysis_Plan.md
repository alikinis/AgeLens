# AgeLens V2 Analysis Plan

## Version 1.7 — Stage 5 Reviewed Synthesis and Finalization Gate

This document records the frozen V2 analysis plan and the reviewed Stage 5 synthesis. No further modeling, feature expansion, interaction search, or tuning is authorized.

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


## 22. Stage 4 Selected Method

Stage 4 selects one intrinsically interpretable method:
`interpret.glassbox.ExplainableBoostingClassifier`, pinned to
`interpret==0.7.8`.

Model D is a main-effects-only additive classifier. Automatic and manual
interaction expansion are not authorized.

## 23. Frozen Model D Information Set

Model D uses the same four predictors as Stage 3 Model C:

- chronological age;
- sex;
- race/ethnicity;
- canonical Phenotypic Age acceleration per five years.

No new biomarker, cycle term, participant identifier, or outcome-derived
feature is authorized. This isolates flexible functional form from feature
expansion.

## 24. Frozen Model D Validation

The two Stage 3 cycle-holdout directions remain primary. The test cycle is not
used for EBM fitting, binning, validation, or early stopping.

The primary contrast is pooled weighted Brier delta D−C. Secondary metrics are
AUC delta D−C and Model D calibration. Five hundred stratified-PSU bootstrap
replicates refit Models C and D in both directions.

## 25. Frozen Positive-Claim Rule

A positive Stage 4 claim requires a favorable pooled Brier interval against
Model C, nonnegative pooled AUC difference, acceptable calibration,
nonpositive direction-specific Brier differences in both directions, stable
acceleration functions across the two cycle-trained models, and 500 completed
bootstrap replicates.

Failure of any condition blocks a positive explainable-extension claim.

## 26. Explanation Restrictions

Only global additive-term summaries are authorized. Term scores are centered
log-odds contributions, not prevalence ratios or causal effects.

No local explanation, individual prediction, clinical threshold, biological
race interpretation, post-hoc SHAP/LIME, or feature-importance ranking as a
scientific effect is authorized.

## 27. Stage 4 Implementation Boundary

The method, comparator, predictors, hyperparameters, leakage controls,
metrics, bootstrap, and failure conditions are frozen. Implementation of the
single Model D is authorized after this freeze is validated and committed to
`v2-development`.

Stage 4 results and merge to `main` remain unauthorized pending separate
review and release.


## 28. Stage 4 Result

The frozen main-effects EBM completed both cycle directions and all 500
stratified-PSU bootstrap replicates.

Pooled Model D minus Model C:

- Brier delta = -0.000970
  (95% CI -0.003093 to 0.001152);
- AUC delta = -0.000161
  (95% CI -0.014073 to 0.013751).

Model D calibration intervals contained the frozen targets. Both
direction-specific Brier point differences were nonpositive; AUC differences
were mixed.

## 29. Stage 4 Joint Decision

The Brier confidence interval crossed zero and pooled AUC delta was negative.
The frozen joint positive-extension rule therefore failed.

No positive incremental-prediction claim is authorized for Model D. Model C
remains the preferred prediction model for Stage 5 synthesis. The result is
not interpreted as evidence of Model D harm.

## 30. Global Shape Result

The two cycle-trained acceleration functions had Spearman correlation
0.980697 over
101 governed common-support points, passing the
0.70 stable-rank-shape rule.

This authorizes only a descriptive global shape statement. Rank similarity is
not exact curve agreement. Term scores are centered log-odds contributions,
and no causal, threshold, individual, biological, or feature-importance effect
interpretation is authorized.

## 31. Model Role After Stage 4

Model D is retained as a descriptive global shape sensitivity and is not
promoted as the primary prediction model. Model C anchors predictive reporting
because Stage 3 established incremental utility over Model B and Stage 4 did
not establish added utility from EBM flexibility.

No additional model, interaction, feature, or hyperparameter search may be
opened after inspection of these results.

## 32. Stage 5 Authorization

Stage 5 may synthesize the released Stage 2–4 evidence, prepare an aggregate
validation report, abstract, figures, and ARISE presentation materials.

Merge to `main`, final manuscript claims, local explanations, individual risk
outputs, and clinical-utility claims remain subject to a separate final
release decision.

<!-- AGELENS_STAGE5_BEGIN -->
## Stage 5 Reviewed Synthesis

Stage 5 completed deterministic extraction, row-level reconciliation, source hashing, aggregate tables, non-comparative evidence figures, and ARISE working materials. The corrected independent validator checks all scientific-summary values and document guardrails. No new estimand, model, threshold, subgroup search, interaction search, or optimization was introduced.
<!-- AGELENS_STAGE5_END -->
