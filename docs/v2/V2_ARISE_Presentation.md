# AgeLens V2 ARISE Presentation — Working Outline

**Target duration:** approximately 8 minutes 20 seconds  
**Status:** working material pending human review

## Slide 1 — Title and Research Question (0:45)

**Title:** From reproducible Phenotypic Age replication to controlled functional-health validation

**Content:**
- Can Phenotypic Age acceleration inform functional-health association and cross-cycle prediction beyond chronological age and demographics?
- NHANES 2015–2018; governed, survey-aware, aggregate-only workflow.

**Recommended visual:** project title with one-sentence research question.

**Speaker notes:** Introduce AgeLens as a replication-first project. State that V2 was designed before modeling and separates association, prediction, transportability, and explainability.

## Slide 2 — V1-to-V2 Scientific Progression (0:55)

**Content:**
- V1: reproducible Phenotypic Age construction and mortality baseline.
- Stage 2: functional-health association.
- Stage 3: transportability and cross-cycle incremental prediction.
- Stage 4: one frozen explainable extension.
- Final role decision: Model C preferred.

**Recommended visual:** `21_stage5_v1_to_v2_progression.png`.

**Speaker notes:** Emphasize evidence before implementation and that negative findings were retained.

## Slide 3 — Data, Outcome, and Survey-aware Design (0:55)

**Content:**
- Primary outcome: serious difficulty walking or climbing stairs.
- Primary domain: 4,366 adults; 682 positive responses.
- Complex-survey weights, strata, and PSUs were part of the estimand.
- No participant-level outputs entered the public release.

**Recommended visual:** concise design schematic.

**Speaker notes:** State that this is observational NHANES analysis and not a clinical prediction product.

## Slide 4 — Conventional Functional-health Validation (1:05)

**Content:**
- Global linear summary: PR 1.148 per 5-year higher acceleration.
- 95% CI 1.100–1.197.
- Three prespecified secondary outcomes were positive after Holm adjustment.

**Recommended visual:** existing Stage 2 adjusted-prevalence curve, not a conventional-regression-as-AI graphic.

**Speaker notes:** Present the PR as a global summary and immediately transition to nonlinearity.

## Slide 5 — Nonlinearity Changes the Interpretation (1:00)

**Content:**
- Quasi-Poisson nonlinearity p=0.000177.
- Bounded logistic-spline p=0.000916.
- Steepest adjusted-prevalence increase occurred in the lower-to-middle acceleration range.
- No constant effect, protective low tail, or clinical threshold claim.

**Recommended visual:** existing bounded Stage 2 adjusted-prevalence curve.

**Speaker notes:** Explain why a single per-5-year coefficient cannot describe the full association shape.

## Slide 6 — Transportability and Incremental Prediction (1:15)

**Content:**
- Race/ethnicity global interaction family supported after BH control; sex, age-group, and cycle families unsupported.
- Model C vs Model B: Brier delta -0.0030; AUC delta 0.0341.
- Both are bidirectional cross-cycle results within NHANES.

**Recommended visual:** existing Stage 3 incremental-performance figure plus a small guardrail callout.

**Speaker notes:** Race/ethnicity is a social classification. Do not interpret the interaction biologically or rank groups. Clarify that this is not independent external-cohort validation.

## Slide 7 — Controlled EBM Extension: Negative Incremental Result (1:05)

**Content:**
- One prespecified main-effects EBM; same information set as Model C.
- Zero interactions; no hyperparameter search.
- Brier delta D−C -0.0010; AUC delta D−C -0.0002.
- Incremental improvement not supported; Model C remained preferred.

**Recommended visual:** existing Stage 4 incremental-performance figure.

**Speaker notes:** The EBM was the explainable machine-learning extension. Its negative result is part of the contribution because the method and gate were frozen in advance. Failure to establish benefit is not evidence of harm.

## Slide 8 — Conclusions, Limitations, and Reproducibility (1:20)

**Content:**
- Association with mobility disability was supported but nonlinear.
- Acceleration added modest cross-cycle prediction within NHANES.
- Transportability evidence was restricted.
- The EBM did not improve upon Model C.
- Aggregate-only, source-hashed, governed release workflow.

**Recommended visual:** `21_stage5_evidence_synthesis.png`.

**Speaker notes:** Close with observational and internal-NHANES limitations. No causal, clinical, threshold, or individual-risk claim is made. Human review and final release remain pending.

## Take-home Message

A reproducibly derived Phenotypic Age acceleration measure was associated with mobility disability and modestly improved cross-cycle prediction within NHANES, while a prespecified explainable extension did not outperform the simpler governed Model C.
