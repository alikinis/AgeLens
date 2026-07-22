# AgeLens

Reproducible implementation of Phenotypic Age in NHANES 2015–2018, including
laboratory harmonization, survey-aware analysis, cross-implementation checks,
and aggregate all-cause mortality results.

**Author:** Ali Kınış  
**Affiliation:** Independent Researcher, İzmir, Türkiye  
**Version:** 1.0.0

## Repository scope

This repository contains:

- public-safe Jupyter notebooks;
- R scripts for survey-weighted validation and mortality analysis;
- governed configuration and methodological documentation;
- aggregate tables and figures;
- notebook-integrity and public-release checks.

It does **not** contain:

- raw NHANES data;
- participant-level or interim datasets;
- public-use mortality source records;
- the unpublished manuscript or supplementary manuscript.

## Reproduction order

Run the notebooks in numerical order:

1. `00_setup_agelens.ipynb`
2. `01_data_ingestion.ipynb`
3. `02_data_preprocessing.ipynb`
4. `03_validation.ipynb`
5. `04_external_validation.ipynb`
6. `05_validation_completion.ipynb`
7. `06_eg004_creatinine_sensitivity.ipynb`
8. `07_governance_resolution.ipynb`
9. `08_canonical_output_rebuild.ipynb`
10. `09_mortality_analysis_authorization.ipynb`
11. `10_mortality_survival_analysis.ipynb`
12. `11_final_reporting_and_release_package.ipynb`
13. `11b_release_package_rebuild.ipynb`
14. `12_baseline_characteristics.ipynb`

R is required for the survey-weighted Cox analysis and selected validation
checks.

## Data policy

Source data are obtained locally from official NCHS channels and are not
redistributed here. The public repository contains aggregate outputs only.
Cause-specific mortality is outside the authorized AgeLens V1 scope.

## Software environment

The final governed execution used Python 3, NumPy 2.4.6, pandas 2.3.3,
R 4.5.1, `survey` 4.5, and `survival` 3.8-3.

## Safety check

Before every push, run:

```powershell
python scripts/preflight_repository.py .
```

The repository also runs this check through GitHub Actions.

## Citation

Until a DOI is assigned, cite the software repository:

> Kınış A. AgeLens. Version 1.0.0. 2026.
> https://github.com/alikinis/AgeLens

## License

Code, notebooks, scripts, and configuration are licensed under the MIT License.
Third-party NHANES data are not distributed and remain subject to their own
terms.
