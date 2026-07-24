# AgeLens V2 Stage 4 Method Selection

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S4M-001 |
| Version | 1.0 |
| Status | Complete — EBM selected |
| Date | 2026-07-24 |
| Source gate | Stage 3 pass with guardrails |

## 1. Decision

Stage 4 selects exactly one explainable extension:

> `interpret.glassbox.ExplainableBoostingClassifier`, main effects only.

The implementation package must pin `interpret==0.7.8`.

No second machine-learning method, black-box comparator, SHAP analysis,
automatic interaction search, or raw-biomarker expansion is authorized.

## 2. Why This Method

The selected model is an intrinsically interpretable additive classifier. It
learns one flexible function for each feature, then adds the feature
contributions on the log-odds scale.

This is aligned with the observed evidence:

- Stage 2 found strong nonlinearity in Phenotypic Age acceleration;
- Stage 3 showed that linear acceleration added modest cross-cycle predictive
  information;
- Stage 4 should test functional-form flexibility, not change the information
  set or start an unrestricted feature search.

A main-effects-only EBM isolates that question. The model remains a glassbox,
and the learned age and acceleration functions can be inspected directly.

## 3. Frozen Information Set

Model D uses the same information available to Stage 3 Model C:

1. chronological age;
2. sex;
3. race/ethnicity;
4. canonical Phenotypic Age acceleration per five years.

No NHANES cycle term is used. No raw biomarker, participant identifier,
outcome-derived variable, secondary outcome, or post-outcome feature is
permitted.

This restriction makes the primary comparison a method comparison:

> Does flexible additive modeling improve out-of-cycle prediction beyond the
> already released conventional Model C?

## 4. Why Interactions Are Disabled

`interactions=0` is frozen.

Stage 3's race/ethnicity interaction remains an association finding about the
global linear summary. It is not imported into the predictive extension as an
automatically searched interaction.

Disabling interactions:

- limits model complexity;
- avoids data-driven subgroup discovery;
- protects the race/ethnicity interpretation guardrail;
- ensures every Model D term is a directly viewable main-effect function.

## 5. Frozen Hyperparameters

| Parameter | Frozen value |
| --- | ---: |
| `max_bins` | 32 |
| `interactions` | 0 |
| `validation_size` | 0.15 |
| `outer_bags` | 8 |
| `learning_rate` | 0.015 |
| `greedy_ratio` | 0 |
| `smoothing_rounds` | 75 |
| `max_rounds` | 10,000 |
| `early_stopping_rounds` | 100 |
| `min_samples_leaf` | 20 |
| `gain_scale` | 1 |
| `min_cat_samples` | 20 |
| `cat_smooth` | 20 |
| `max_leaves` | 2 |
| `n_jobs` | 1 |
| `random_state` | 20260724 |

No hyperparameter search is authorized. The implementation may not select a
better-looking parameter set after results are observed.

## 6. Weights and Missingness

Model D must fit with positive `WTSAF4YR` weights rescaled within each training
cycle to sum to the training sample size.

The governed four predictors are complete in the primary domain. A missing
value in any Model D predictor is therefore a failure, not an imputation
trigger.

## 7. Validation Design

The Stage 3 cycle holdout is retained unchanged:

1. train in 2015–2016 and test in 2017–2018;
2. train in 2017–2018 and test in 2015–2016.

All EBM binning, early stopping, and fitting occur only inside the training
cycle. The opposite cycle remains untouched until prediction.

The primary comparator is the released conventional Model C. Model B remains
a secondary reference.

## 8. Metrics and Uncertainty

Primary metric:

- pooled survey-weighted Brier difference, Model D minus Model C.

Secondary metrics:

- pooled weighted AUC difference;
- Model D calibration intercept;
- Model D calibration slope;
- direction-specific Brier and AUC differences.

Uncertainty uses 500 stratified-PSU bootstrap replicates. Model C and Model D
are refit in both directions in every replicate. Any failed replicate blocks
release.

## 9. Positive Extension Rule

A positive explainable-extension claim requires all of the following:

1. the 95% interval for pooled Brier delta D−C is below zero;
2. pooled AUC delta D−C is nonnegative;
3. Model D calibration-intercept interval contains zero;
4. Model D calibration-slope interval contains one;
5. direction-specific Brier delta D−C is nonpositive in both directions;
6. the acceleration functions from the two training cycles have Spearman
   correlation at least 0.70 over the governed common display range;
7. all 500 bootstrap replicates complete.

Otherwise continuous metrics and descriptive shapes may be reported, but no
positive extension claim is authorized.

## 10. Explanation Scope

Authorized:

- global term importance as a model diagnostic;
- cycle-specific age and acceleration functions;
- centered log-odds term contributions;
- acceleration shape comparison over common supported values.

Not authorized:

- local or participant-level explanations;
- individual risk scores;
- causal feature effects;
- clinical thresholds;
- biological interpretation of race/ethnicity;
- treating feature-importance rank as scientific effect size.

The acceleration display is restricted to the intersection of the two
cycle-specific survey-weighted 1st–99th percentile ranges. Unsupported
extrapolation is prohibited.

## 11. Method Review Outcome

The method, comparator, predictor set, hyperparameters, leakage controls,
metrics, bootstrap, explanation scope, and failure conditions are now frozen.

Stage 4 implementation is authorized after this freeze is validated and
committed to `v2-development`. Scientific results remain unauthorized until a
separate Stage 4 review and release gate.

## References

- InterpretML Contributors. *Explainable Boosting Machine* documentation.
- Lou Y, Caruana R, Gehrke J, Hooker G. Accurate intelligible models with
  pairwise interactions. KDD, 2013.
- Nori H, Jenkins S, Koch P, Caruana R. InterpretML: A Unified Framework for
  Machine Learning Interpretability. 2019.
