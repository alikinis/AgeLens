# AgeLens V2 Aggregate Validation Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5V-001 |
| Version | 1.0 |
| Status | Aggregate validation candidate |
| Date | 2026-07-24 |
| Build | AgeLens-V2-Stage5-20260724b |

## 1. Objectives and Frozen Governance

AgeLens V2 evaluated functional-health association, secondary outcomes, transportability, incremental prediction, and one controlled explainable extension while preserving V1 immutability. Outcomes, estimands, model hierarchy, multiplicity rules, validation directions, metrics, and the Stage 4 method were frozen before the corresponding result inspection. Stage 5 performs synthesis only.

## 2. Cohort and Survey-design Reconciliation

The primary Stage 2 domain contained 4,366 adults, 682 positive responses, and the governed NHANES complex-survey design. Stage 2–4 release validators reconcile counts, weights, strata, PSUs, metrics, and bootstrap completion. Stage 5 reads aggregate outputs and does not reconstruct participant-level cohorts.

## 3. Association

The primary survey-weighted modified-Poisson global summary was PR 1.147564 per 5-year higher acceleration (95% CI 1.099844–1.197355). This addresses adjusted association, not causality or predictive discrimination.

## 4. Nonlinearity

The quasi-Poisson nonlinearity p-value was 0.000176974908863395; the bounded logistic-spline nonlinearity p-value was 0.000916263045884809. The global linear PR remains a prespecified summary, but it must not be interpreted as a uniform effect across the acceleration distribution. No clinical threshold is identified.

## 5. Secondary Outcomes and Multiplicity

The six-domain disability composite, fair/poor general health, and PHQ-9 ≥10 analyses were governed secondary outcomes and used Holm adjustment. Each showed a positive association. These results support breadth of association but do not replace the primary outcome or establish independent causal validation.

## 6. Transportability

Four prespecified global interaction families were controlled with Benjamini–Hochberg q=0.10. Race/ethnicity was supported (raw p=0.000255872749735952; q=0.00102349099894381); sex, age group, and NHANES cycle were unsupported. Because Stage 2 established nonlinearity, the interaction result is restricted to the frozen global linear acceleration summary. It is not biological, causal, or a basis for pairwise ranking.

## 7. Predictive Discrimination and Error

Model C versus Model B used bidirectional cycle holdout and 500 stratified-PSU bootstrap replicates. Brier delta C−B was -0.0030339161930044 (95% CI -0.005222375868507 to -0.0008454565175018); AUC delta C−B was 0.0340510458845171 (95% CI 0.0164744275891323 to 0.051627664179902). The released conclusion is modest incremental cross-cycle prediction within NHANES, not independent external-cohort validation.

## 8. Calibration

Stage 3 Model C calibration met the frozen rule. Stage 4 Model D calibration also remained acceptable, but acceptable calibration did not override the failed joint positive-extension rule. Calibration, discrimination, and overall prediction error are reported as distinct properties.

## 9. Controlled Explainability

Model D was a main-effects-only Explainable Boosting Machine using the Model C information set, with zero interactions and no search or tuning. Brier delta D−C was -0.0009703249310347 (95% CI -0.0030928097750904 to 0.0011521599130209); AUC delta D−C was -0.0001606680664727 (95% CI -0.0140726788023686 to 0.0137513426694231). Incremental improvement was not supported.

The global acceleration term showed Spearman rank correlation 0.980697152207994 across 101 common eligible points. Explainability here means a restricted aggregate model-shape diagnostic. It does not create causal interpretation, exact curve agreement, a clinical threshold, or a local explanation.

## 10. Model-role Synthesis

Model C remains preferred. Model D is not promoted and is retained only for the negative incremental result and descriptive global-shape sensitivity.

## 11. Reproducibility Controls

The build validates the released Stage 2–4 dependencies, reconciles JSON and CSV values within absolute tolerance 1e-10, hashes every authoritative source, records runtime metadata, uses deterministic row ordering, and writes UTF-8 aggregate outputs. It fits no model and requires no network access.

## 12. Disclosure Controls

Stage 5 tables and figures are aggregate-only. No SEQN, participant identifier, participant-level prediction, local contribution, private NHANES path, raw data, or unpublished participant-level material is written.

## 13. Limitations

The analysis is observational. Cross-cycle validation remains internal to NHANES 2015–2018. Modified-Poisson fitted values are not individual probabilities. Transportability evidence is restricted and must be interpreted under established nonlinearity. No decision-curve, treatment-threshold, independent-cohort, clinical-utility, or individual-risk evaluation was performed.

## 14. Authorized Conclusions

1. Acceleration was associated with serious mobility disability, with strong nonlinearity.
2. Prespecified secondary outcomes showed supportive positive associations after Holm adjustment.
3. Model C added modest out-of-cycle predictive information within NHANES beyond Model B.
4. The race/ethnicity global interaction family was supported with strict social-classification guardrails; other families were unsupported.
5. Model D did not establish incremental predictive improvement beyond Model C.
6. The global acceleration rank-shape sensitivity passed its restricted governed rule.
7. Model C remains preferred.

## 15. Prohibited Conclusions and Unresolved Actions

Causal, biological subgroup, clinical threshold, individual-risk, local-explanation, EBM-superiority, and independent external-cohort claims are prohibited. Human review remains pending. Final V2 release, final manuscript claims, ARISE submission, and merge to `main` remain unauthorized.
