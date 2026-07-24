# AgeLens V2 Stage 5 Release Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5R-002 |
| Version | 1.0 |
| Status | Released for V2 development |
| Date | 2026-07-24 |
| Build | AgeLens-V2-Stage5-20260724b |
| Human review | Pass with guardrails after corrective revision |

## 1. Release Decision

Stage 5 passed aggregate build validation and completed review after four corrective revisions: stronger independent validation, row-or-field source locators, an explicit social-classification guardrail in the working abstract, and restricted transportability wording in the progression figure.

The release decision is:

> **Pass for commit to `v2-development` as an aggregate synthesis and ARISE working package.**

This is not a final V2 release or ARISE-submission approval.

## 2. Scientific Synthesis

- Stage 2: Phenotypic Age acceleration was associated with serious mobility disability, but the association was strongly nonlinear.
- Stage 2 secondary outcomes: all three prespecified associations remained positive after Holm adjustment and are supportive evidence only.
- Stage 3 transportability: only the prespecified global race/ethnicity interaction family was supported; race/ethnicity is a social classification and no biological, causal, pairwise-ranking, or group-risk claim is authorized.
- Stage 3 prediction: Model C showed modest pooled out-of-cycle improvement over Model B within NHANES 2015–2018.
- Stage 4: the frozen main-effects EBM did not demonstrate incremental predictive improvement beyond Model C.
- Stage 4 global shape: the acceleration-term functions were highly rank-correlated over governed common support, with descriptive aggregate interpretation only.
- Final model role: Model C remains preferred.

## 3. Validation and Traceability

The corrected independent validator:

- reruns the released Stage 2–4 validators;
- reconciles every scientific-summary estimate and uncertainty interval against released configurations;
- verifies multiplicity and model-role decisions;
- verifies source-file hashes and row-or-field locators;
- recomputes the abstract word count;
- checks required numerical and guardrail content across synthesis, validation report, abstract, presentation, and release candidate;
- validates aggregate-only table schemas, private-path and secret-like text controls, PNG integrity, and governed Git scope.

## 4. Disclosure and Reproducibility

Stage 5 fits no model, opens no participant-level NHANES file, writes no participant-level prediction or local explanation, and changes no V1 artifact. Source hashes and runtime metadata remain recorded. Null and negative findings remain visible.

## 5. Authorization

Authorized:

- commit the corrected Stage 5 implementation, aggregate outputs, review record, and release artifacts to `v2-development`;
- use the governed Stage 5 synthesis and ARISE materials as working drafts;
- retain Model C as the prediction anchor.

Not authorized:

- final V2 release;
- final manuscript claims;
- final ARISE submission;
- merge to `main`;
- new model, feature, interaction, or hyperparameter search;
- clinical, causal, threshold, biological-subgroup, local-explanation, or individual-risk claims.
