# AgeLens V2 Stage 4 Method Freeze Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S4F-002 |
| Version | 1.0 |
| Status | Frozen — implementation authorized |
| Date | 2026-07-24 |

## 1. Frozen Method

One method is frozen:

- Model D: `ExplainableBoostingClassifier`;
- package pin: `interpret==0.7.8`;
- binary log-loss objective;
- four main effects;
- zero interaction terms;
- no hyperparameter search.

## 2. Frozen Comparison

Model D is compared primarily with released Stage 3 Model C. Both use the same
four predictors. The comparison therefore measures flexible additive
functional form rather than feature expansion.

Model B is retained only as a secondary reference.

## 3. Leakage Controls

- No test-cycle row may enter EBM training, binning, validation, or early
  stopping.
- No participant-level random performance split replaces cycle holdout.
- No cycle indicator enters the model.
- No feature may be engineered with the mobility-disability outcome.
- The governed acceleration definition is reused without modification.
- Preprocessing must be fitted independently inside each training direction.

## 4. Complexity Controls

- exactly four main-effect terms;
- `interactions=0`;
- at most 32 main-effect bins per feature;
- two leaves per boosting tree;
- minimum 20 training samples per leaf;
- no tuning, screening, or post-result parameter replacement.

## 5. Release Gates

Software and data gate:

- n = 4,366 and positive n = 682;
- exact package version;
- exact predictors and categorical levels;
- finite probabilities in [0,1];
- exact four-term, zero-interaction model structure;
- Model C reconciliation with Stage 3;
- 500/500 bootstrap replicates;
- aggregate-only public outputs.

Scientific gate:

- favorable pooled Brier interval against Model C;
- non-worse pooled AUC direction;
- acceptable calibration;
- no direction-specific Brier deterioration;
- reproducible acceleration shape across cycle-trained models.

## 6. Authorization

Authorized after validation and commit:

- implementation of the single frozen Model D;
- private participant-level training and bootstrap intermediates;
- aggregate global explanation and performance outputs.

Still unauthorized:

- local explanations;
- new biomarkers or feature selection;
- automatic or manual interaction expansion;
- SHAP/LIME or another explainability method;
- individual-risk or clinical-decision claims;
- merge to `main`;
- final manuscript claims.
