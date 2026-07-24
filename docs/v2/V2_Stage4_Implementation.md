# AgeLens V2 Stage 4 Implementation

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S4I-002 |
| Version | 1.0 |
| Status | Implementation ready — results pending |
| Date | 2026-07-24 |
| Python build | `AgeLens-V2-Stage4-Python-20260724c` |
| R build | `AgeLens-V2-Stage4-R-20260724b` |

## 1. Authorized Scope

This implementation executes the single frozen Model D:

- `interpret.glassbox.ExplainableBoostingClassifier`;
- exact package version `interpret==0.7.8`;
- the same four predictors as Stage 3 Model C;
- main effects only;
- `interactions=0`;
- no hyperparameter search;
- no local explanations.

No NHANES result is authorized until the completed outputs pass software
validation, human review, and a separate release gate.

## 2. Isolated Python Environment

The installer creates a dedicated virtual environment outside the repository:

```text
<project parent>/.venv-stage4
```

The global Python environment is not modified. The installer pins and checks
`interpret==0.7.8` and runs a synthetic EBM self-test using the
frozen feature types, sample weights, and zero interactions.

## 3. R Reference Preparation

`scripts/v2/17_prepare_stage4_reference.R`:

1. validates the 5,223-row canonical private input;
2. reconciles the 4,366-person, 682-positive primary domain;
3. constructs the pooled survey design;
4. generates 500 bootstrap replicate weights with `survey`;
5. refits conventional Model C in both cycle directions for every replicate;
6. reconciles Model C point metrics to released Stage 3 results;
7. writes participant-level replicate weights only to the private data tree.

The private work directory is outside the public repository and is never
staged by the release workflow.

## 4. Python Model D Execution

`scripts/v2/18_run_stage4_ebm.py`:

- fits Model D separately in each training cycle;
- filters to positive training weights and rescales them to the effective
  training count;
- validates exactly four singleton terms and zero interactions;
- predicts only in the opposite cycle;
- extracts aggregate age and acceleration functions;
- evaluates Model D in all 500 survey replicates;
- supports restart from an aggregate private checkpoint;
- calculates replicate covariance using the R-provided scale and rscales;
- writes only aggregate tables and figures.

## 5. Model C–Model D Comparison

R remains authoritative for conventional Model C. Python receives only
private aggregate Model C metrics and survey replicate weights.

The primary Stage 4 contrast is pooled weighted Brier delta D−C. Secondary
contrasts are AUC delta D−C, calibration, and direction-specific deltas.

Model C point metrics must reproduce Stage 3 within `1e-7` or execution stops.

## 6. Explanation Outputs

Model D exposes additive term scores through `eval_terms`. The implementation
uses these scores only to produce governed global functions:

- age function from 20 to 80 years;
- acceleration function on the intersection of cycle-specific weighted
  1st–99th percentile support;
- no point whose EBM training bin contains fewer than 30 unweighted training
  observations is marked display eligible;
- cycle-trained acceleration functions are compared by Spearman correlation.

The scores are centered log-odds contributions. They are not prevalence
ratios, causal effects, clinical thresholds, or individual explanations.

## 7. Bootstrap and Resume Behavior

The full run contains 500 replicates, with two Model C and two Model D fits in
each replicate. It can therefore take substantially longer than Stage 3.

Private R reference files and an aggregate EBM checkpoint permit a rerun to
continue after interruption. Public results are written only after all 500
replicates complete.

## 8. Public Outputs

Tables:

- `18_stage4_method_input_audit.csv`;
- `18_stage4_direction_metrics.csv`;
- `18_stage4_bootstrap_summary.csv`;
- `18_stage4_positive_extension_decision.csv`;
- `18_stage4_term_importance.csv`;
- `18_stage4_age_shape.csv`;
- `18_stage4_acceleration_shape.csv`;
- `18_stage4_shape_stability.csv`;
- `18_stage4_runtime_versions.csv`;
- `18_stage4_release_checks.csv`.

Figures:

- `18_stage4_model_d_incremental_performance.png`;
- `18_stage4_cycle_specific_acceleration_shapes.png`.

No `SEQN`, participant prediction, or local contribution is written publicly.

## 9. Result Status

Successful execution produces provisional results only:

```text
provisional_pending_stage4_review
```

Commit, scientific interpretation, and release require a separate human-review
package. Merge to `main` remains unauthorized.


## Synthetic Survey Self-Test Correction

The initial synthetic fixture generated strata and PSU labels with aliased
repetition periods, which unintentionally left one PSU in each stratum. The
fixture now explicitly crosses cycle, stratum, and PSU and verifies that every
pooled and cycle-specific stratum contains exactly two PSUs before the
bootstrap conversion.

This correction changes only the synthetic installation test. The frozen
production design, Model C reference analysis, EBM method, hyperparameters,
validation directions, and 500-replicate analysis are unchanged.


## Support-Quantile Compatibility and Recovery

The installed `survey` version returns a `newsvyquantile` list. Point
quantiles are now extracted through the public `coef()` method rather than
attempting to coerce the list itself.

The failed run had already completed and written all 500 Model C reference
replicates before reaching this final support-range step. The recovery path:

1. computes only the four missing cycle-specific 1st/99th percentiles;
2. validates metadata, 500 replicate metrics, 500 rscales, 4,366 replicate-
   weight rows, Model C point metrics, diagnostics, and the repaired quantiles;
3. creates the private manifest without refitting Model C;
4. resumes with Stage 4 point EBM fitting and the checkpointed Model D
   bootstrap.

No frozen method, predictor, hyperparameter, performance metric, survey
bootstrap, or scientific gate is changed.


## Interaction-Validator Correction

The first completed Stage 4 run fitted four main effects and zero interactions,
completed 500/500 EBM bootstrap replicates, and generated both aggregate
figures. Final validation nevertheless failed because the validator inspected
the string form of `model.term_features_`.

Python represents a one-element tuple as `(0,)`. The trailing comma is tuple
syntax, not evidence that a second feature is present. The punctuation-based
check therefore produced a false interaction failure.

Public term output now records:

- the exact feature name;
- pipe-delimited numeric feature indices;
- an explicit `term_feature_count`.

A term passes the no-interaction gate only when its explicit count is one and
its index and feature name match the frozen four-feature mapping. The 500
completed EBM bootstrap replicates remain in the private checkpoint and are
not refitted when the analysis command is resumed.

No EBM fit, predictor, hyperparameter, bootstrap estimate, performance metric,
shape estimate, or scientific decision rule is changed by this correction.
