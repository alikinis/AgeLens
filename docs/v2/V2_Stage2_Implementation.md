# AgeLens V2 Stage 2 Conventional Modeling Implementation

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S2I-001 |
| Version | 1.0 |
| Status | Complete — results released for V2 development |
| Date | 2026-07-23 |

## 1. Purpose

Stage 2 implements the conventional association models frozen at Gate 1. It is the first V2 stage authorized to estimate scientific outcome associations.

Stage 2 does not alter V1 and does not authorize an explainable or machine-learning extension.

## 2. Protected V1 Boundary

The Stage 2 workflow does not modify:

- the canonical V1 Phenotypic Age formula;
- biomarker mappings or harmonization equations;
- the 5,223-participant canonical V1 file;
- V1 mortality data, models, diagnostics, or results;
- the public `main` branch.

Participant-level V2 model input is generated in the private local workspace outside the Git repository.

## 3. Governed Model Input

`scripts/v2/05_run_stage2_conventional_models.py`:

1. reloads the governed canonical V1 participant file;
2. reloads official NHANES demographic and outcome files from the private cache;
3. applies exact XPORT-zero normalization;
4. reconstructs all four governed outcomes;
5. reconstructs the frozen cycle-specific acceleration coefficients;
6. reconciles those coefficients against the Stage 1 audit;
7. writes one participant-level CSV only under `data/processed/v2` in the private workspace;
8. writes aggregate input audits to `results/tables/v2`.

## 4. Primary Association Model

The primary outcome is serious difficulty walking or climbing stairs (`DLQ050`).

The primary estimator is a survey-weighted quasi-Poisson model with log link:

- survey weight: `WTSAF4YR`;
- strata: cycle-unique `SDMVSTRA`;
- PSUs: cycle-unique `SDMVPSU`;
- age basis: fixed natural spline with internal knots 35, 50, and 65 years and boundary knots 20 and 80 years;
- covariates: sex, race/ethnicity, and NHANES cycle;
- exposure: canonical Phenotypic Age acceleration per 5 years.

The reported primary effect is an adjusted prevalence ratio with a 95% confidence interval and two-sided p-value. Interpretation is associational, not causal.

## 5. Model Hierarchy

- **Model A:** fixed natural spline of chronological age.
- **Model B:** Model A plus sex, race/ethnicity, and NHANES cycle.
- **Model C:** Model B plus Phenotypic Age acceleration per 5 years.

Model C is the frozen primary inference model.

## 6. Secondary Outcomes

The same Model C structure is fitted for:

1. any six-domain disability;
2. fair or poor self-rated health;
3. PHQ-9 score at least 10.

Raw p-values are adjusted together using the Holm method. Secondary results remain subordinate to the primary outcome.

## 7. Linearity Sensitivity

The primary linear acceleration effect remains frozen. A restricted cubic spline sensitivity adds three nonlinear basis terms using knots at -30, -10, 0, 10, and 40 acceleration years.

A design-based joint Wald test evaluates the nonlinear terms. This sensitivity cannot replace the primary linear model after results are seen.

## 8. Diagnostics and Validation

The Stage 2 workflow records:

- domain and positive-outcome counts;
- survey design degrees of freedom;
- model convergence;
- finite coefficient and covariance checks;
- fitted-value range and count above one for quasi-Poisson models;
- captured R warnings;
- R and package versions;
- aggregate release checks;
- independent Python validation of every public output.

No significance threshold is used as a software validation requirement.

## 9. Result Status

A successful run produces the first V2 scientific association result. All results remain **provisional pending human review** until the Stage 2 result package is examined and a separate release decision is recorded.

## 10. Execution

Run from the repository root:

```powershell
python .\scripts\v2\05_run_stage2_conventional_models.py --project-root .
```

The Python orchestrator locates `Rscript`, prepares the private model input, runs the R models, validates aggregate outputs, and prints the primary result.


## 11. First-Run Diagnostic Trigger

The first governed run produced a primary adjusted prevalence ratio of
1.147564 per 5-year higher acceleration (95% CI 1.099844–1.197355), with
p = 2.51e-07. All three secondary outcomes were significant after Holm
adjustment.

Release remains blocked because the fixed spline sensitivity detected
nonlinearity (p = 0.00017697) and the modified-Poisson linear models produced
some fitted values above one. These findings trigger
`V2_Stage2_Diagnostic_Review.md`; they do not alter V1 or automatically
invalidate the prespecified coefficient.


## 12. Stage 2 Release

The diagnostic review confirmed robust positive associations, strong
nonlinearity, and probability-bound violations restricted to an extreme,
minimally weighted tail.

The Stage 2 conventional results are released for commit to
`v2-development`. The primary coefficient remains the prespecified global
linear summary; the bounded spline curve describes shape.

Merge to `main`, transportability claims, prediction claims, and explainable
modeling remain separately gated.
