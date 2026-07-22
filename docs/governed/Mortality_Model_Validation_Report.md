# AgeLens V1 Mortality Model Validation Report

## Status

All required survey-weighted Cox models and release checks passed.

## Authorized Cohort

- Participants: 4,350
- Deaths: 127
- Weighted population sum: 226687150.314204
- Survey strata: 30
- Survey PSUs: 60

## Primary Result

The primary adjusted hazard ratio per 5-year higher canonical Phenotypic Age acceleration was:

- HR: 1.185354
- 95% CI: 1.128633 to 1.244926
- p-value: 1.06871e-11

## Exposure Results

| model | sample | hazard_ratio | ci_low_95 | ci_high_95 | p_value |
| --- | --- | --- | --- | --- | --- |
| canonical_exposure_only | canonical_full | 1.23243 | 1.18511 | 1.28165 | 0 |
| canonical_primary_adjusted | canonical_full | 1.18535 | 1.12863 | 1.24493 | 0 |
| canonical_adjusted_per_sd | canonical_full | 1.285 | 1.19536 | 1.38136 | 0 |
| sensitivity_no_topcode | no_topcode | 1.1791 | 1.11787 | 1.24369 | 0 |
| sensitivity_erratum | canonical_full | 1.18868 | 1.13088 | 1.24943 | 0 |
| sensitivity_creatinine_plus_0_11 | canonical_full | 1.18535 | 1.12863 | 1.24493 | 0 |
| sensitivity_creatinine_plus_0_17 | canonical_full | 1.18535 | 1.12863 | 1.24493 | 0 |
| sensitivity_creatinine_plus_0_23 | canonical_full | 1.18535 | 1.12863 | 1.24493 | 0 |
| sensitivity_exclude_early_deaths | exclude_early_deaths | 1.17665 | 1.10473 | 1.25324 | 0 |

## Proportional-Hazards Diagnostic

| method | term | chi_square | p_value | fallback_reason |
| --- | --- | --- | --- | --- |
| cox.zph_on_svycoxph | phenoage_acceleration_per_5_years | 3e-06 | 0.998565 |  |
| cox.zph_on_svycoxph | chronological_age_years | 0.001656 | 0.967539 |  |
| cox.zph_on_svycoxph | sex_factor | 2e-06 | 0.998771 |  |
| cox.zph_on_svycoxph | race_factor | 0.00049 | 0.98234 |  |
| cox.zph_on_svycoxph | cycle_factor | 0.001649 | 0.967605 |  |
| cox.zph_on_svycoxph | GLOBAL | 0.00448 | 1 |  |

## Reconciliation

| sample | n_python | events_python | weighted_population_sum_python | strata_python | psus_python | n_r | events_r | weighted_population_sum_r | strata_r | psus_r |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| canonical_full | 4350 | 127 | 2.26687e+08 | 30 | 60 | 4350 | 127 | 2.26687e+08 | 30 | 60 |
| no_topcode | 4079 | 88 | 2.17613e+08 | 30 | 60 | 4079 | 88 | 2.17613e+08 | 30 | 60 |
| exclude_early_deaths | 4309 | 86 | 2.24816e+08 | 30 | 60 | 4309 | 86 | 2.24816e+08 | 30 | 60 |

## R Environment

| component | version |
| --- | --- |
| R | 4.5.1 |
| survey | 4.5 |
| survival | 3.8.3 |

## Validation

All 22 release checks passed.

Cause-specific mortality was not modeled.

<!-- AGE-LENS MORTALITY RESULTS RELEASE 2026-07-22 -->
