# AgeLens V2 Outcome Feasibility Matrix

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-OFM-001 |
| Version | 1.0 |
| Status | Complete — primary outcome frozen |
| Date | 2026-07-23 |
| Target cycles | NHANES 2015–2016 and 2017–2018 |
| Adult domain | Age 20 years and older |

## 1. Governing Weight Rule

Because the V1 Phenotypic Age exposure depends on fasting-subsample laboratory data, all candidate-outcome analyses use `WTSAF4YR` with cycle-unique strata and PSUs.

## 2. Corrected Empirical Feasibility

| Candidate | Cycle | Eligible n | Valid n | Positive n | Valid fraction | Weighted prevalence | Strata | PSUs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Serious mobility disability | 2015–2016 | 2,181 | 2,181 | 332 | 100.00% | 11.63% | 15 | 30 |
| Serious mobility disability | 2017–2018 | 2,186 | 2,185 | 350 | 99.95% | 11.90% | 15 | 30 |
| **Serious mobility disability** | **Pooled** | **4,367** | **4,366** | **682** | **99.98%** | **11.77%** | **30** | **60** |
| Any six-domain disability | Pooled | 4,367 | 4,358 | 1,247 | 99.79% | 24.47% | 30 | 60 |
| Fair/poor general health | Pooled | 4,367 | 4,076 | 1,025 | 93.34% | 18.33% | 30 | 60 |
| PHQ-9 ≥10 | Pooled | 4,367 | 4,021 | 345 | 92.08% | 7.45% | 30 | 60 |

## 3. Final Outcome Hierarchy

| Role | Outcome | Definition | Rationale |
| --- | --- | --- | --- |
| **Primary** | Serious difficulty walking or climbing stairs | `DLQ050`: Yes versus No | Directly aging-relevant; stable coding; nearly complete data; sufficient positive support; full survey design |
| Secondary functional | Any six-domain disability | Any Yes across six DLQ domains, requiring complete valid coding | Broader functional burden but heterogeneous |
| Secondary general health | Fair/poor self-rated health | `HSD010` Fair/Poor versus better health | Relevant and interpretable but subjective and less complete |
| Secondary neuropsychiatric | PHQ-9 ≥10 | Complete nine-item score ≥10 | Standardized but less complete and more distal from the primary physical-aging construct |

## 4. Superseded PHQ-9 Result

The first PHQ-9 feasibility run is invalid. Valid item responses of zero had been decoded as the exact IBM XPORT zero sentinel. The corrected import converts exact sentinel matches only and records replacement counts. Corrected results above supersede the initial run.

## 5. Gate 0 Decision

`DLQ050` is frozen as the primary V2 non-mortality outcome. The analysis domain is canonical V1 participants age ≥20 with positive `WTSAF4YR` and a valid response.

Gate 0 is closed. Final modeling remains blocked pending Stage 1 design decisions.
