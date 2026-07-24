# AgeLens V2 ARISE Working Abstract

## Background
Phenotypic Age is a blood-chemistry-based aging measure, but its functional-health relevance and incremental prediction across recent NHANES cycles require controlled evaluation. We extended a frozen reproducible implementation to examine serious difficulty walking or climbing stairs as the primary V2 outcome.

## Methods
We analyzed adults in NHANES 2015–2018 using complex-survey weights, strata, and primary sampling units. Survey-weighted modified-Poisson models estimated adjusted prevalence ratios for Phenotypic Age acceleration, with prespecified spline diagnostics and Holm-adjusted secondary outcomes. Transportability used four prespecified global interaction families with Benjamini–Hochberg control. Incremental prediction compared demographic Model B with acceleration-augmented Model C in both cycle directions using Brier score, AUC, calibration, and 500 stratified-PSU bootstrap replicates. A frozen main-effects Explainable Boosting Machine (Model D) was then compared with Model C without interaction or hyperparameter search.

## Results
Among 4,366 adults with 682 mobility-disability cases, the prespecified global linear summary was a prevalence ratio of 1.148 per 5-year higher acceleration (95% CI 1.100–1.197). Spline diagnostics showed nonlinearity (quasi-Poisson p=0.000177; bounded logistic spline p=0.000916), with the steepest increase in the lower-to-middle acceleration range. The global race/ethnicity interaction family was supported after multiplicity control (q=0.0010), with race/ethnicity treated strictly as a social classification; sex, age-group, and cycle families were not. Model C modestly improved pooled out-of-cycle prediction versus Model B: Brier delta C−B -0.0030 (95% CI -0.0052 to -0.0008) and AUC delta C−B 0.0341 (95% CI 0.0165 to 0.0516). Model D did not establish improvement beyond Model C: Brier delta D−C -0.0010 (95% CI -0.0031 to 0.0012) and AUC delta D−C -0.0002 (95% CI -0.0141 to 0.0138).

## Conclusions
Phenotypic Age acceleration was associated with mobility disability and added modest out-of-cycle predictive information within NHANES, although the association was nonlinear and transportability evidence was restricted. The prespecified explainable extension did not demonstrate incremental prediction beyond Model C, which remained preferred. Findings are observational, are not independent external-cohort validation, and do not support causal, clinical, threshold, or individual-risk claims.

**Word count:** 312
