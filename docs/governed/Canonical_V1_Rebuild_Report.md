# AgeLens V1 Canonical Output Rebuild Report

## Status

Canonical rebuild completed successfully.

## Governing Decisions

- D-010: Supplement conversion pair is canonical.
- D-011: age-topcoded participants retained and flagged; no-topcode sensitivity produced.
- D-012: observed modern harmonized creatinine is canonical; three mandatory shifts produced.
- D-013: validation acceptance and BioAge baseline satisfied.
- D-014: exact XPT IBM-zero sentinel normalization was applied upstream.

## Canonical Sample

| sample                 |     cycle |    n |   weighted_population_sum |   weighted_mean |   taylor_se |   ci_low_95 |   ci_high_95 |
|:-----------------------|----------:|-----:|--------------------------:|----------------:|------------:|------------:|-------------:|
| canonical_full         | 2015_2016 | 2645 |               1.29291e+08 |         42.1409 |    0.830376 |     40.5133 |      43.7684 |
| canonical_full         | 2017_2018 | 2578 |               1.30214e+08 |         43.2259 |    0.66065  |     41.931  |      44.5208 |
| sensitivity_no_topcode | 2015_2016 | 2524 |               1.25189e+08 |         40.8063 |    0.780352 |     39.2768 |      42.3358 |
| sensitivity_no_topcode | 2017_2018 | 2427 |               1.25221e+08 |         41.6157 |    0.584285 |     40.4705 |      42.7609 |

## Regression Checks

All 29 canonical regression checks passed.

## Output Scope

The canonical participant file and survey summaries are reportable for cross-sectional AgeLens V1 analyses.

Mortality analysis remains unauthorized and no mortality data were used.

## Required Sensitivities

- Erratum constant pair.
- No-topcode sample.
- Creatinine shifts of +0.11, +0.17, and +0.23 mg/dL.

## Output Manifest

| path                                                          |   size_bytes | sha256                                                           |
|:--------------------------------------------------------------|-------------:|:-----------------------------------------------------------------|
| data\processed\agelens_v1_canonical_complete_case.parquet     |       404259 | 471c8fcde4f0d93045d427ddf3c070d310be0d18c7c4b85e8deb06502845c1c0 |
| data\processed\agelens_v1_sensitivity_no_topcode.parquet      |       383454 | c9eb1fd77c0abd2563099f25b15b32bae0f0d9324598b3802e0bb503d78d76d7 |
| data\processed\agelens_v1_required_sensitivities_long.parquet |       519078 | 6af5ff34e62894bfed15009deba1188f9c635e03dd03a9a74b77778343e77b1c |
| results\tables\08_canonical_sample_flow.csv                   |          178 | 6f5c085955191af28177193bdfb0ccee2f8ef83aa10056e8382422da067eff6a |
| results\tables\08_canonical_survey_summary.csv                |         4561 | b2d1d22598fe42d545cccfaa107a7f43dde91e296971a381b3d39fc5354bc9be |
| results\tables\08_canonical_regression_checks.csv             |         2541 | e7093a99692a821ba4a129c321451efe4d8f611d50b9e4e046670e9f749ad0e1 |
| results\tables\08_required_sensitivity_summary.csv            |         1290 | cc35c3a8e82f114e27d14c0c3c70c5d115f5a73649fbdbe53e79d444c52fdd91 |
