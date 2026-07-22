# AgeLens Mortality Analysis Protocol

## Document Control

| Field | Value |
| --- | --- |
| Document | Mortality Analysis Protocol |
| Version | 1.1 |
| Status | Implemented and validated |
| Last Updated | 2026-07-22 |
| Governing Decision | D-015 |

## 1. Scope

This protocol governs the first AgeLens V1 linked-mortality analysis. It does not alter the released cross-sectional canonical outputs.

## 2. Data Sources

- Canonical participant file: `data/processed/agelens_v1_canonical_complete_case.parquet`
- Public-use linked mortality file: `data/interim/nhanes_2015_2018_mortality_2019_public.parquet`
- NHANES cycles: 2015–2016 and 2017–2018
- Mortality follow-up release: public-use follow-up through 2019

## 3. Primary Cohort

Participants must satisfy all of the following:

1. Canonical harmonized complete-case membership.
2. Chronological age at least 20 years.
3. Positive pooled fasting weight `WTSAF4YR`.
4. `ELIGSTAT == 1`.
5. `MORTSTAT` observed as 0 or 1.
6. Positive `PERMTH_EXM`.

No imputation is permitted.

### Cohort flow

| step | n |
| --- | --- |
| Canonical complete-case participants | 5223 |
| Age 20 years or older | 4367 |
| NCHS linkage eligible | 4351 |
| Observed all-cause mortality outcome | 4351 |
| Positive MEC-based follow-up | 4350 |

### Cycle audit

| NHANES_CYCLE | n | deaths | weighted_population_sum | followup_months_min | followup_months_median | followup_months_max | person_years | age_topcoded_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2015_2016 | 2178 | 83 | 1.12629e+08 | 1 | 47 | 61 | 8485.25 | 121 |
| 2017_2018 | 2172 | 44 | 1.14058e+08 | 1 | 24 | 37 | 4263.5 | 150 |

## 4. Outcome and Time Scale

- Primary outcome: all-cause mortality.
- Event indicator: `MORTSTAT == 1`.
- Time origin: MEC examination.
- Follow-up variable: `PERMTH_EXM`.
- Analysis time unit: months; hazard ratios are invariant to rescaling time to years.
- Survivors remain censored at their released public-use follow-up duration.

Cause-specific mortality is not authorized in V1.

## 5. Primary Exposure

Canonical Phenotypic Age acceleration is the cycle-specific survey-weighted residual from:

`canonical Supplement Phenotypic Age ~ chronological age`

Residualization uses `WTSAF4YR` separately within each cycle.

Primary reporting scale:

- hazard ratio per 5-year higher acceleration.

Secondary reporting scale:

- hazard ratio per one weighted SD higher acceleration.

## 6. Survey Design

- Weight: `WTSAF4YR`
- Strata: cycle-unique combination of `NHANES_CYCLE` and `SDMVSTRA`
- PSU: cycle-unique combination of cycle, stratum, and `SDMVPSU`
- Planned estimator: R `survey::svycoxph`
- Cycles are pooled; cycle is included in adjusted models.

## 7. Models

### Model 0 — minimally adjusted

`Surv(PERMTH_EXM, mortality_event) ~ acceleration_per_5_years`

### Model 1 — primary adjusted model

`Surv(PERMTH_EXM, mortality_event) ~ acceleration_per_5_years + chronological_age_years + sex + race_ethnicity + cycle`

Categorical predictors must be treated as factors.

The analysis is prognostic and replicational, not causal.

## 8. Required Sensitivities

1. Exclude age-topcoded participants.
2. Replace canonical Supplement Phenotypic Age with the Erratum sensitivity.
3. Replace canonical creatinine scale with each D-012 sensitivity:
   - `+0.11 mg/dL`
   - `+0.17 mg/dL`
   - `+0.23 mg/dL`
4. Exclude deaths within the first 12 months.
5. Report cycle-specific event counts and descriptive follow-up.

## 9. Diagnostics

Notebook 10 must report:

- model convergence;
- coefficient, standard error, HR, and 95% CI;
- unweighted participant and event counts;
- weighted population sum;
- strata and PSU counts;
- time-interaction diagnostic for the primary acceleration exposure;
- comparison of Python cohort counts with R model input counts;
- independent verification that no cause-specific outcome was modeled.

A failed diagnostic blocks mortality-result release.

## 10. Release Gate

Model execution is authorized after notebook 09. Mortality results remain non-reportable until notebook 10:

1. completes every required model and sensitivity;
2. records no analysis errors;
3. passes cohort and survey-design reconciliation;
4. writes a model-validation report;
5. explicitly opens `mortality_results_allowed`.

<!-- AGE-LENS MORTALITY AUTHORIZATION 2026-07-22 -->

## 11. Implementation and Validation

Notebook 10 completed all nine required survey-weighted Cox models.

Primary adjusted HR per 5-year higher canonical acceleration:

- HR: 1.185354
- 95% CI: 1.128633 to 1.244926
- p-value: 1.06871e-11

The proportional-hazards diagnostic used `cox.zph_on_svycoxph` and returned `p = 0.998565` for the primary acceleration term.

Python and R cohort counts, event counts, weighted sums, strata, and PSUs reconciled within the governed tolerances.

D-016 releases the prespecified all-cause mortality results for reporting. Cause-specific mortality remains unauthorized.

<!-- AGE-LENS MORTALITY RESULTS RELEASE 2026-07-22 -->

