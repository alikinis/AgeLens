# AgeLens V2 Evidence Gap Register

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-EG-001 |
| Version | 1.9 |
| Status | Closed for V2.0.4 public maintenance release — scientific limitations retained |
| Date | 2026-07-27 |

## Status Vocabulary

- **Open:** unresolved and may affect design or implementation.
- **Under Review:** evidence collection is active.
- **Dispositioned:** uncertainty remains but a governed handling rule is approved.
- **Closed:** sufficiently resolved for the authorized V2 scope.

## Register

| ID | Priority | Question | Current resolution or required evidence | Status |
| --- | --- | --- | --- | --- |
| V2-EG-001 | Core | Which non-mortality aging-related outcome family will be primary? | Functional mobility disability is primary; `DLQ050` is frozen by D2-003 after documentary and corrected empirical feasibility review. | Closed |
| V2-EG-002 | Core | Which exact variables and coding rules define each candidate outcome? | Primary and three secondary definitions are frozen in `config/v2_outcome_candidates.json` and `config/v2_gate0_freeze.json`. | Closed |
| V2-EG-003 | Core | What is the eligible age range and analytic population? | Canonical V1 participants age ≥20 with positive `WTSAF4YR` and a valid primary response; 4,366 primary complete cases. | Closed |
| V2-EG-004 | Core | Which survey weights, strata, and PSUs apply? | `WTSAF4YR` with cycle-unique strata and PSUs. | Closed |
| V2-EG-005 | Core | How will missing outcome and covariate data be handled? | Primary complete-case analysis frozen; all primary covariates have zero missingness. Secondary outcomes use outcome-specific complete cases. | Closed |
| V2-EG-006 | Core | What is the primary estimand and adjustment set? | Adjusted prevalence ratio per 5-year acceleration; fixed age spline, sex, race/ethnicity, and cycle. | Closed |
| V2-EG-007 | Core | How will multiple outcomes, subgroups, and interactions be controlled? | Primary alpha 0.05; Holm secondary family; exploratory BH q=0.10 across four global transportability tests. | Closed |
| V2-EG-008 | Core | Which baseline and comparison models are justified? | Frozen Models A–C with fixed age basis and parsimonious demographic adjustment. | Closed |
| V2-EG-009 | Core | Which performance metrics and thresholds will be used? | Weighted Brier difference primary; weighted AUC and calibration secondary; positive-claim rule frozen. | Closed |
| V2-EG-010 | Core | How will resampling or data splitting respect survey structure and prevent leakage? | Bidirectional cross-cycle validation with no random participant split; 500 stratified PSU bootstrap replicates for uncertainty. | Closed |
| V2-EG-011 | Important | Which subgroup analyses are sufficiently powered and ethically interpretable? | All prespecified levels pass support thresholds; global interaction tests and cautious level-specific interpretation frozen. | Closed |
| V2-EG-012 | Important | Which single explainable extension, if any, is justified? | Main-effects-only EBM selected and frozen with `interpret==0.7.8`, the Model C predictor set, zero interactions, no tuning, and global-only explanations. | Closed |
| V2-EG-013 | Important | Which Python and R tools will be used and reconciled? | R authoritative for survey inference; Python authoritative for audit; defined cross-language reconciliation targets and runtime version capture. | Closed |
| V2-EG-014 | Core | What exact V2 scope must be frozen for ARISE? | Primary association, three secondaries, four transportability families, cross-cycle incremental prediction, validation report, figures, and presentation are frozen. | Closed |

## Gate Rules

Gate 0 is closed.

Gate 1 is closed. V2-EG-001 through V2-EG-024 are closed for the governed V2 and public-maintenance scope. The original V2.0.0 scientific release and V2.0.1 through V2.0.3 maintenance releases remain immutable, and V2.0.4 is authorized as the current public maintenance release. Final ARISE submission, final manuscript claims, and merge to `main` remain separate and unauthorized.


## Stage 2 Result-Review Gap

| ID | Priority | Question | Current resolution or required evidence | Status |
| --- | --- | --- | --- | --- |
| V2-EG-015 | Core | Is the prespecified linear acceleration summary adequate for scientific release given significant nonlinearity and fitted values above one? | Retain the prespecified PR as a global linear summary; report strong nonlinearity with a bounded curve; bound violations are restricted to 0.050% weighted beyond p99. | Closed |


## Stage 3 Result-Review Gaps

| ID | Priority | Question | Current resolution or required evidence | Status |
| --- | --- | --- | --- | --- |
| V2-EG-016 | Core | Does the global linear acceleration summary vary across prespecified demographic or cycle dimensions? | Race/ethnicity passed BH control (q = 0.001023); sex, age group, and cycle did not. Release is restricted to the global linear summary under known nonlinearity. | Closed |
| V2-EG-017 | Core | Does acceleration improve prediction beyond age, sex, and race/ethnicity in an unseen NHANES cycle? | The frozen rule passed: Brier delta -0.003034 (95% CI -0.005222 to -0.000845), AUC delta 0.034051; 500/500 replicates completed. | Closed |


| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-018 | Core | Does a frozen main-effects EBM improve out-of-cycle prediction beyond Model C? | No positive extension: Brier delta -0.000970 (95% CI -0.003093 to 0.001152) and AUC delta -0.000161; Model C remains preferred. | Closed |
| V2-EG-019 | Important | Is the learned acceleration function reproducible across cycle-trained models? | Stable rank shape supported: Spearman 0.980697 across 101 common eligible points; descriptive global interpretation only. | Closed |


| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-020 | Important | Which prediction model anchors Stage 5 synthesis after the explainable-extension test? | Retain Stage 3 Model C. Model D did not pass the frozen incremental-benefit gate and remains a descriptive global shape sensitivity only. | Closed |

<!-- AGELENS_STAGE5_BEGIN -->
## Stage 5 Reviewed Evidence-gap Disposition

Stage 5 review does not close scientific limits by inference. Observational design, internal NHANES cross-cycle validation, restricted transportability, absence of independent external-cohort validation, and absence of clinical utility remain explicit limitations. They do not block the reviewed working package but continue to block unsupported final claims.
<!-- AGELENS_STAGE5_END -->


## Final V2 Release Disposition

All governed V2 evidence gaps are closed for the `v2.0.0`
public-release scope.

Closure does not remove the substantive limitations of the work.
Observational design, internal NHANES cross-cycle validation, restricted
transportability, absence of independent external-cohort validation,
and absence of clinical-utility evaluation remain explicit.

Those limitations do not block the final public V2 release, but they
continue to block unsupported causal, clinical, threshold,
individual-risk, and external-validation claims.


## V2.0.1 Maintenance Integrity Gap

| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-021 | Core release integrity | Do public notebooks, source-manifest hashes, release metadata, environment records, and validators remain disclosure-safe and portable across Windows, LF checkouts, detached tags, and GitHub source archives? | Participant previews removed; display statements made aggregate-only; canonical-LF hashing implemented; V2.0.1 citation/environment/current documentation/CI reconciled; portable validators pass; scientific invariant digest unchanged. | Closed |

## V2.0.1 Maintenance Integrity Disposition

The public-release integrity defects are closed without changing the V2.0.0
scientific release. The canonical digest of 79 governed scientific configs,
tables, and figures remains
`f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`.

Observational design, internal NHANES cross-cycle validation, restricted
transportability, absence of independent external-cohort validation, and
absence of clinical-utility evaluation remain substantive scientific
limitations.

## V2.0.2 Documentation and Tooling Integrity Gap

| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-022 | Repository reproducibility | Do the root V2 quick-start, R dependency list, public-snapshot builder, current citation, and CI checks consistently reproduce the V2.0.2 public package? | Root instructions now use `requirements-v2.txt` and the governed Stage 4 runtime versions; the complete required R package list and BioAge pin are documented; generated snapshots include V2 requirements and run the current portable validator; CI exercises the snapshot path. | Closed |

## V2.0.2 Documentation and Tooling Integrity Disposition

The remaining repository documentation and public-snapshot tooling defects are
closed without changing the V2 scientific release. The canonical digest of 79
governed scientific configs, tables, and figures remains
`f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`.

Observational design, internal NHANES cross-cycle validation, restricted
transportability, absence of independent external-cohort validation, and
absence of clinical-utility evaluation remain substantive scientific
limitations.

## V2.0.3 Invariant-Coverage Integrity Gap

| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-023 | Release regression integrity | Does the cryptographic no-change invariant directly cover every artifact category named in the maintenance validator's scientific no-change claim? | The invariant now covers 108 artifacts: 79 governed configs/tables/figures, all 14 public notebooks, four analysis scripts, and 11 V2 scientific execution scripts. Historical V2.0.1 and V2.0.2 validators remain portable and compatible. | Closed |

## V2.0.3 Invariant-Coverage Integrity Disposition

The validator-coverage limitation is closed without changing the V2 scientific
release. The prior 79-file digest remains `f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940`. The expanded
108-file digest is `e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef` and directly covers every artifact
category named in the V2.0.3 no-change assertion.

Observational design, internal NHANES cross-cycle validation, restricted
transportability, absence of independent external-cohort validation, and
absence of clinical-utility evaluation remain substantive scientific
limitations.

## V2.0.4 CI Runtime Integrity Gap

| ID | Priority | Gap | Disposition | Status |
| --- | --- | --- | --- | --- |
| V2-EG-024 | Release automation integrity | Can the GitHub Actions workflow execute the pandas-dependent V2 release-validator chain and historical ancestry checks on a clean hosted runner using a runtime consistent with the governed V2 environment? | The workflow now fetches complete Git history and tags, uses the Node 24-based Python setup action, selects Python 3.13, installs pinned NumPy and pandas validator dependencies from `requirements-ci.txt`, verifies the runtime before validation, and runs the V2.0.4 validator and public snapshot builder. | Closed |

## V2.0.4 CI Runtime Integrity Disposition

The hosted-runner dependency and shallow-history defects are closed without
changing the V2 scientific release. The prior 79-file digest remains
`f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940` and the
expanded 108-file digest remains
`e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef`.

Observational design, internal NHANES cross-cycle validation, restricted
transportability, absence of independent external-cohort validation, and
absence of clinical-utility evaluation remain substantive scientific
limitations.
