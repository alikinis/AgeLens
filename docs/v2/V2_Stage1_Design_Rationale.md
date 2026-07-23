# AgeLens V2 Stage 1 Design Rationale

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S1R-001 |
| Version | 0.1 |
| Status | Design draft — empirical support audit pending |
| Date | 2026-07-23 |

## 1. V1 Protection Boundary

Stage 1 does not modify:

- the canonical V1 formula;
- V1 harmonization or biomarker mappings;
- the 5,223-participant canonical V1 output;
- the V1 mortality cohort, estimand, models, or results;
- any file outside the V2 configuration, documentation, script, and aggregate-result namespaces.

The public `main` branch remains the V1 release baseline. V2 development remains isolated on `v2-development`.

## 2. Primary Estimand Draft

The primary V2 estimand is the adjusted prevalence ratio for serious difficulty walking or climbing stairs associated with a 5-year higher canonical Phenotypic Age acceleration.

The target is an associational, population-descriptive estimand, not a causal effect.

## 3. Exposure Construction

Canonical Phenotypic Age acceleration is constructed exactly as in the governed V1 mortality workflow:

1. within each NHANES cycle, fit the WTSAF4YR-weighted linear projection of canonical Supplement Phenotypic Age on chronological age;
2. define acceleration as the participant-level residual;
3. verify a cycle-specific weighted residual mean of zero;
4. scale the primary exposure per 5 years;
5. retain one weighted-standard-deviation scaling as secondary.

The simple difference between Phenotypic Age and chronological age is not substituted for the governed residual definition.

## 4. Estimator Draft

The primary conventional estimator is a survey-weighted generalized linear model with:

- quasi-Poisson variance;
- log link;
- design-based robust standard errors;
- `WTSAF4YR`;
- cycle-unique strata and PSUs;
- survey-domain analysis;
- design degrees of freedom.

This directly estimates a prevalence ratio and avoids interpreting an odds ratio as though it were a prevalence ratio.

## 5. Adjustment and Model Hierarchy Draft

Chronological age is modeled flexibly with a four-degree-of-freedom natural spline.

- Model A: flexible chronological age.
- Model B: Model A plus sex, race/ethnicity, and NHANES cycle.
- Model C: Model B plus canonical Phenotypic Age acceleration per 5 years.

Model C is the draft primary inference model. This parsimonious hierarchy preserves comparability with V1 while distinguishing age information from incremental biological-age information.

## 6. Missing-Data Draft

The primary outcome has one missing response among 4,367 eligible adults. The draft primary analysis therefore uses a complete-case domain without imputing the outcome.

Primary demographic covariates are expected to be nearly complete. The Stage 1 support audit will test this expectation. A missingness rate above 1% or material differential missingness by outcome reopens the policy.

Secondary outcomes use outcome-specific complete-case domains unless a later governed sensitivity is justified.

## 7. Multiplicity Draft

- One primary test: two-sided alpha 0.05.
- Three secondary outcomes: Holm adjustment within the secondary family.
- Transportability interactions: exploratory Benjamini–Hochberg false-discovery rate of 0.10.
- Sensitivity analyses: supportive, not separate confirmatory claims.

## 8. Transportability Draft

Candidate dimensions are:

- sex;
- age group: 20–49, 50–64, and 65+;
- race/ethnicity;
- NHANES cycle.

A level must provisionally have at least:

- 100 participants;
- 30 positive outcomes;
- 30 negative outcomes;
- 8 represented strata;
- 16 represented PSUs.

The support audit will determine whether any level must be collapsed, suppressed, or removed before Gate 1 closes.

## 9. Incremental Performance

Model-performance analysis is not yet frozen. Candidate metrics are weighted Brier score, weighted AUC, calibration-in-the-large, and calibration slope.

No performance claim is authorized until a survey-aware internal-validation design is selected and independently checked.

## 10. Primary Sources

- NCHS, NHANES Tutorials: complex sample design, weighting, variance estimation, and domain analysis.
- Lumley, `survey::svyglm` documentation: survey-weighted generalized linear models and design-based robust standard errors.
- Zou G. A modified Poisson regression approach to prospective studies with binary data. *American Journal of Epidemiology*. 2004;159:702–706. doi:10.1093/aje/kwh090.
