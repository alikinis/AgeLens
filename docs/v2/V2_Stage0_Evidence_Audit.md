# AgeLens V2 Stage 0 Evidence Audit

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-EA-001 |
| Version | 1.0 |
| Status | Complete — Gate 0 closed |
| Date | 2026-07-23 |

## 1. Documentary Findings

Official NCHS documentation showed that `DLQ050` is available with stable wording and coding in both target cycles and has no substantive routing complication in the age-20-plus domain.

The V1 exposure depends on fasting-subsample laboratory data, so `WTSAF4YR` governs the merged analysis.

The six-domain disability composite, fair/poor general health, and complete PHQ-9 score ≥10 were retained as prespecified secondary candidates.

Detailed PFQ activity items remain held because of route-dependent structural missingness. Multimorbidity remains deferred.

## 2. Corrected Empirical Findings

The corrected local audit found:

- 4,367 eligible canonical adults;
- 4,366 valid primary-outcome responses;
- one missing primary-outcome response;
- 682 positive primary outcomes;
- 11.77% survey-weighted prevalence;
- full representation of 30 strata and 60 PSUs.

Cycle-specific prevalence was similar:

- 2015–2016: 11.63%;
- 2017–2018: 11.90%.

Secondary pooled results were:

- any six-domain disability: n = 4,358 valid, 1,247 positive, 24.47%;
- fair/poor general health: n = 4,076 valid, 1,025 positive, 18.33%;
- PHQ-9 ≥10: n = 4,021 valid, 345 positive, 7.45%.

## 3. XPORT Zero Correction

The initial PHQ-9 result was invalid because valid zero item responses were decoded as the exact IBM XPORT sentinel `5.397605346934028e-79`.

The governed correction:

1. converts exact sentinel matches to zero immediately after XPT import;
2. does not apply a near-zero threshold;
3. records replacement counts by source file;
4. supersedes all initial PHQ-9 feasibility rows.

## 4. Gate 0 Conclusion

`DLQ050` satisfies the Gate 0 requirements for primary-outcome relevance, cross-cycle comparability, overlap, positive support, and survey-design representation.

V2-EG-001 through V2-EG-004 are closed. Stage 1 design work is authorized. Final scientific modeling remains unauthorized.
