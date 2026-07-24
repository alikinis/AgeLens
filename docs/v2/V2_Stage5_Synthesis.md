# AgeLens V2 Stage 5 Scientific Synthesis

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5S-001 |
| Version | 1.0 |
| Status | Release candidate pending human review |
| Date | 2026-07-24 |
| Build | AgeLens-V2-Stage5-20260724b |

## Scope

This synthesis uses only released aggregate Stage 2–4 artifacts. It fits no model, performs no search or tuning, opens no participant-level data, and does not alter V1.

## Scientific Progression

V1 established a governed and reproducible Phenotypic Age implementation and survey-weighted mortality baseline. Stage 2 evaluated the frozen non-mortality outcome of serious difficulty walking or climbing stairs. Stage 3 evaluated prespecified transportability and bidirectional cross-cycle incremental prediction. Stage 4 tested one frozen main-effects explainable extension. Stage 5 integrates those results without creating a new estimate.

## Stage 2 — Functional-health Association

The primary domain contained 4,366 adults and 682 positive responses. The prespecified global linear summary was PR 1.148 per 5-year higher acceleration (95% CI 1.100–1.197). This is an observational global summary, not a constant effect or individual probability.

Nonlinearity was supported by the prespecified quasi-Poisson test (p=0.000176975) and bounded logistic-spline test (p=0.000916263). The governed interpretation is that adjusted prevalence rose most steeply from lower-to-middle acceleration values and the relative increase attenuated at higher positive acceleration. No protective low-tail claim or clinical threshold is authorized.

All three prespecified secondary outcomes showed positive Holm-adjusted associations. They are supportive secondary evidence rather than independent primary validations.

## Stage 3 — Transportability and Incremental Prediction

The race/ethnicity interaction family was supported under BH q=0.10 (raw p=0.000255873; q=0.00102349); sex, age-group, and cycle families were unsupported. This concerns only the frozen global linear acceleration summary under known nonlinearity. Race/ethnicity is a social classification and the result does not authorize biological, causal, pairwise-ranking, or group-risk claims.

Model C showed modest incremental cross-cycle prediction beyond Model B within NHANES 2015–2018. Brier delta C−B was -0.003034 (95% CI -0.005222 to -0.000845); AUC delta C−B was 0.034051 (95% CI 0.016474 to 0.051628). This is not independent external-cohort validation or clinical utility.

## Stage 4 — Controlled Explainable Extension

The frozen main-effects EBM used the Model C information set, zero interactions, no hyperparameter search, both cross-cycle directions, and 500 stratified-PSU bootstrap replicates. It did not demonstrate incremental predictive improvement beyond Model C. Brier delta D−C was -0.000970 (95% CI -0.003093 to 0.001152); AUC delta D−C was -0.000161 (95% CI -0.014073 to 0.013751). Failure of the positive rule is not evidence that Model D is harmful.

The acceleration-term functions had Spearman rank correlation 0.980697 over 101 eligible common-support points. This is a descriptive global rank-shape result, not exact curve agreement, a prevalence ratio, a causal effect, a threshold, or a local participant explanation.

## Final Model-role Decision

Model C remains the preferred prediction model. Model D is retained only as a negative incremental-prediction result and descriptive global-shape sensitivity. Null and negative findings remain visible.

## Release Boundary

This document is a release candidate. Human review is pending. Final V2 release, final manuscript claims, ARISE submission, and merge to `main` remain unauthorized.
