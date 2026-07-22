# Decision Log

## Document Control

| Field             | Value                          |
| ------------------ | ------------------------------ |
| Document Title    | AgeLens Decision Log           |
| Project            | AgeLens                        |
| Document ID        | AL-GOV-001                     |
| Version            | 2.1|
| Status              | Approved — current through D-017 |
| Author              | Project Team                   |
| Reviewer            | —                               |
| Last Updated        | 2026-07-22                     |
| Related Documents  | Research Protocol (AL-RP-001), Assumption_Register.md, Evidence_Gap_Register.md, Literature_Matrix.xlsx, NHANES_Harmonization_Report.md, Replication_Protocol.md, Validation_Protocol.md, Evidence_Matrix.xlsx |

---

## Revision History

| Version | Date       | Summary of Changes                                      |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1     | 2026-07-16 | Initialized empty template (D-001 placeholder)             |
| 0.2     | 2026-07-16 | D-001 approved (canonical Phenotypic Age formula), per Paper_001/Paper_002 review |
| 0.3     | 2026-07-16 | D-002 approved (V1 target NHANES cycle range: 2015-2020)   |
| 0.4     | 2026-07-16 | D-003 approved (apply NCHS hs-CRP bridging equations), resolving EG-006 |
| 0.5     | 2026-07-16 | D-004 approved (apply NCHS BIOPRO bridging equations for albumin/creatinine/ALP), resolving EG-003 and downgrading EG-004 |
| 0.6     | 2026-07-16 | D-005 approved (bridging direction: 2015-2016 onto 2017+ scale) and D-006 approved (missing-data policy: complete-case exclusion), resolving EG-007 and EG-008 - clears both implementation blockers from Replication_Protocol.md |
| 0.7     | 2026-07-16 | Factual correction: D-003's Notes incorrectly named the CRP panel's in-cycle instrument swap as "DxC 800 to DxC 660i" (that pairing belongs to the BIOPRO panel under D-004); corrected to "DxC 600 to DxC 660i" for CRP, and both entries now explicitly cross-reference each other to prevent re-confusion |
| 0.8     | 2026-07-16 | CRITICAL: Added caveat note to D-001 flagging EG-009 - a newly discovered, unresolved question about which measurement units the formula's coefficients were fit on. D-001's coefficient values remain correct; the units they apply to require resolution before implementation |
| 0.9     | 2026-07-16 | D-007 approved (confirmed unit conversions for all 9 biomarkers, including the unusual CRP mg/dL convention), resolving EG-009 via two independent primary-source confirmations (main text Table 1 + user-provided Supplementary Table S1) |
| 1.0     | 2026-07-16 | D-007 further corroborated by a third, independent source: the BioAge package's own Methods text confirms the identical CRP conversion factor, arrived at by a different research team |
| 1.1     | 2026-07-17 | Added D-001 caveat for EG-010 (Core, Critical, open): a genuine, unresolved discrepancy between the erratum's 0.09165 and Supplement 1's 0.090165 formula constant, worth ~1.8 years per score. Identified following user's detailed mathematical challenge to an earlier incorrect dismissal. |
| 1.2     | 2026-07-17 | D-004's Related Evidence Gaps corrected to reflect EG-004 reinstatement as Core, following user's detailed technical review |
| 1.3     | 2026-07-19 | D-008 approved: confirmed NCHS bridging equations for hs-CRP and BIOPRO panel, directly verified against primary source, resolving EG-013. |
| 1.4     | 2026-07-19 | D-009 added (supersedes D-002): narrowed AgeLens V1 scope to 2015-2016 + 2017-2018 only, dropping the 2017-March 2020 pre-pandemic cycle, per user's explicit decision to avoid unequal-duration pooling complexity |
| 1.5     | 2026-07-19 | Added EG-014 caveat to D-001's notes (highest-magnitude open gap, age top-coding mismatch); found during follow-up audit that EG-014 had never been referenced in Decision_Log despite being fully cascaded elsewhere. |
| 1.6     | 2026-07-19 | Minor completeness fix: D-009's Related Evidence Gaps now mentions EG-014 alongside EG-004/EG-010, found during follow-up cross-file check for the 'lists only some blockers' bug pattern. |
| 1.7 | 2026-07-22 | Approved D-010 through D-014; dispositioned EG-002, EG-004, EG-010, and EG-014 after completed validation, source inspection, EG-004 sensitivity, and XPT ingestion audit. |
| 1.8 | 2026-07-22 | Approved D-015: mortality cohort, all-cause outcome, MEC-based follow-up, acceleration exposure, survey Cox model scope, required sensitivities, and mortality release gate. |
| 1.9 | 2026-07-22 | Approved D-016: mortality models completed, validated, reconciled, and released for reporting. |
| 2.0 | 2026-07-22 | Approved D-017: final AgeLens V1 scientific report, aggregate-only release package, provenance manifest, and archive. |
| 2.1 | 2026-07-22 | Synchronized D-001's current Notes and Evidence Gap references with D-010 through D-013; historical revision entries remain unchanged. |

**Current-state interpretation:** Revision History records the status that applied at each earlier version and therefore may use terms such as *open*, *unresolved*, or *blocking*. Those historical entries do not override the current operative sections, the latest Review Status fields, or Decisions D-010 through D-017.

*This file is a single authoritative document per DP-1 (Protocol Section 8.2) — never duplicated under a new filename. Update in place and bump the version above; prior states remain visible in this table and in each entry's Status field (e.g., Superseded), never deleted.*

---

## Purpose

This document records every officially adopted methodological Decision within the AgeLens project, per Section 6.3 of the Research Protocol. No decision is considered final unless it appears here with documented supporting evidence.

---

## How to Use This Log

- Add one entry per Decision, in the order decisions are made.
- Decision IDs follow the pattern `D-NNN` (e.g., D-001, D-002), assigned sequentially.
- A Decision's Status may be `Draft`, `Approved`, or `Superseded`. A superseded decision is never deleted — a new entry supersedes it and both remain, cross-referenced.
- Category D decisions (single-source, per Protocol Section 7.4) must be flagged in the Notes field and carry a Review Date.

---

## Decision Entries

### D-001

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Canonical Phenotypic Age formula for AgeLens V1 |
| Description                 | Adopt the corrected coefficient set published in Liu et al.'s 2019 *PLOS Medicine* erratum as the canonical Phenotypic Age formula for AgeLens Version 1, superseding the unresolvable equation as originally printed in Levine et al. (2018), *Aging*. |
| Related Research Question   | RQ1, RQ2, RQ3, RQ5 |
| Supporting Evidence          | Levine et al. (2018), *Aging* (E1, original but unresolvable equation); Liu et al. (2019) correction, *PLOS Medicine* (E1/E3); independent peer-reviewed replication using the BioAge package reproducing identical coefficients (E3); multiple independent third-party calculator implementations reproducing the same coefficients (E5) |
| Evidence Level               | E1 (primary), corroborated by E3/E5 |
| Confidence Rating            | High for the governed V1 implementation after direct BioAge source inspection and D-013 cross-implementation checks |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-16 |
| Related Assumptions          | A-001 (resolved by this decision) |
| Related Evidence Gaps        | EG-001 closed through D-001; EG-002 closed through direct source inspection/D-013; EG-010 closed through D-010; EG-014 closed through D-011; EG-004 closed through D-012 |
| Notes                         | See Paper_001_Levine2018.md and Paper_002_BioAge.md for full review detail. D-007 governs the required biomarker units. D-010 governs the canonical final conversion pair (`141.50225 / 0.090165`) and the named Erratum sensitivity. D-011 governs retention, flagging, and no-topcode sensitivity for RIDAGEYR == 80. D-012 governs canonical observed modern creatinine and the three mandatory scale-shift sensitivities. Direct BioAge inspection and D-013 checks closed EG-002. No Core Evidence Gap remains open for D-001 within the approved V1 scope. |

---

### D-002

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | AgeLens V1 target NHANES cycle range |
| Description                 | AgeLens Version 1 targets the most recent NHANES continuous cycles: 2015–2016, 2017–2018, and the 2017–March 2020 pre-pandemic combined sample. Earlier cycles (NHANES III, 1999–2014) are out of scope for V1 projection/validation, though NHANES III remains in scope as the D-001 training sample. |
| Related Research Question   | RQ2 |
| Supporting Evidence          | Project scope decision (not evidence-derived) |
| Evidence Level               | N/A — scope decision, not a methodological claim |
| Confidence Rating            | N/A |
| Reviewer                     | — |
| Status                        | **Superseded by D-009 (2026-07-19)** |
| Date                          | 2026-07-16 |
| Related Assumptions          | — |
| Related Evidence Gaps        | Resolves EG-005 (CRP missing in 2011–2014 is now out of scope); narrows EG-003 and EG-004 to the fixed cycle range |
| Notes                         | This is a project-scope decision rather than a methodological Decision in the strict Section 6.3 sense (no Evidence Level applies), but is logged here per DP-2 Traceability since it directly determines which Evidence Gaps are in scope. **SUPERSEDED 2026-07-19 by D-009**, which narrows the target range further by dropping the 2017–March 2020 pre-pandemic cycle. Per Decision Review Policy (Protocol Section 6.7), this record is preserved rather than deleted. |

---

### D-009

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | AgeLens V1 target NHANES cycle range — NARROWED (supersedes D-002) |
| Description                 | AgeLens Version 1 targets only NHANES 2015–2016 and 2017–2018 — both standard 2-year continuous cycles. The 2017–March 2020 pre-pandemic combined cycle (3.2 years, non-standard duration) is now excluded from scope, per explicit user decision. Rationale: avoids the statistical complexity of pooling two unequal-duration cycles (2-year + 3.2-year) with fractional survey weights, and keeps the analytic sample homogeneous. NHANES III remains in scope only as the D-001 training sample, unaffected by this change. |
| Related Research Question   | RQ2 |
| Supporting Evidence          | User's explicit scope decision (not evidence-derived) |
| Evidence Level               | N/A — scope decision |
| Confidence Rating            | N/A |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-19 |
| Related Assumptions          | — |
| Related Evidence Gaps        | Eliminates the pooled fractional-weight complexity (WTSAF2YR × 2/5.2 + WTSAFPRP × 3.2/5.2) introduced when D-002 included the pre-pandemic cycle — standard equal-duration cycle combination now applies. Does not affect EG-004, EG-010, or EG-014, all three of which are independent of cycle scope (formula/training-data issues, not cross-cycle harmonization issues). |
| Notes                         | Cascades to: Variable_Mapping_Table.xlsx (remove P_* file rows), NHANES_Harmonization_Report.md, Replication_Protocol.md, Validation_Protocol.md, Evidence_Gap_Register.md, Evidence_Matrix.xlsx — all updated 2026-07-19 to remove 2017–March 2020 / pre-pandemic references. |

---

### D-003

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Apply NCHS hs-CRP bridging equations across the D-002 target cycle range |
| Description                 | AgeLens V1 will apply NCHS's published hs-CRP bridging (method-validation) regression equations when combining or comparing CRP values across the 2015-2016 cycle (Beckman Coulter DxC 660i, in-house) and the 2017-2018 cycle (University of Minnesota ARDL). NCHS conducted this bridging study using NHANES samples from late 2016 specifically to support this kind of cross-cycle use. |
| Related Research Question   | RQ2 |
| Supporting Evidence          | NHANES 2017-2018 hs-CRP data documentation (HSCRP_J), official CDC/NCHS publication describing the method-validation bridging study and providing regression equations (E2) |
| Evidence Level               | E2 (official NHANES/CDC documentation) |
| Confidence Rating            | High |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-16 |
| Related Assumptions          | — |
| Related Evidence Gaps        | EG-006 (closed — converted to this decision) |
| Notes                         | Note also: NCHS separately confirmed no statistical adjustment was needed for the mid-2016 in-cycle equipment swap (DxC 600 to DxC 660i — the CRP/HSCRP panel's own in-cycle swap, distinct from the BIOPRO panel's DxC 800-to-660i swap noted under D-004) within the 2015-2016 cycle itself — only the 2015-2016-to-2017+ cross-lab transition requires the bridging equations. See NHANES_Harmonization_Report.md Section 4. |

---

### D-004

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Apply NCHS Standard Biochemistry Profile (BIOPRO) bridging equations for albumin, creatinine, and ALP |
| Description                 | AgeLens V1 will apply NCHS's published BIOPRO bridging (method-validation) equations when combining or comparing albumin, creatinine, and alkaline phosphatase (ALP) values across the 2015-2016 cycle (Beckman Coulter DxC 660i, Collaborative Laboratory Services, Ottumwa IA) and the 2017-2018 cycle (Roche Cobas 6000, University of Minnesota ARDL). NCHS conducted this bridging study using n=248 comparison samples from late 2016. |
| Related Research Question   | RQ2 |
| Supporting Evidence          | NHANES 2017-2018 Standard Biochemistry Profile data documentation (BIOPRO_J), official CDC/NCHS publication describing the bridging study (E2) |
| Evidence Level               | E2 (official NHANES/CDC documentation) |
| Confidence Rating            | High |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-16 |
| Related Assumptions          | — |
| Related Evidence Gaps        | EG-003 (closed — converted to this decision); EG-004 (**REINSTATED as Core, 2026-07-17** — D-004 only resolves the 2015-2016-to-2017+ cross-cycle bridging; it does not address the separate, more fundamental NHANES-III training-era Jaffe bias question, which independent simulation confirmed carries a ~1-2 year impact. See Evidence_Gap_Register.md EG-004.) |
| Notes                         | Same bridging study also confirmed no adjustment needed for the earlier in-cycle DxC 800-to-DxC 660i swap within 2015-2016 itself — this is the BIOPRO panel's own swap, distinct from the CRP/HSCRP panel's DxC 600-to-660i swap noted under D-003. |

---

### D-005

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Bridging direction: adjust 2015-2016 values onto the 2017+ reference scale |
| Description                 | Where D-003 and D-004 bridging equations apply, AgeLens V1 will adjust 2015-2016 biomarker values (Beckman Coulter DxC / in-house lab) onto the 2017-2018 scale (Roche Cobas / University of Minnesota ARDL), rather than the reverse. |
| Related Research Question   | RQ2 |
| Supporting Evidence          | NCHS's own bridging-equation documentation for the August 2021-2023 cycle explicitly frames bridging as adjusting older-instrument data onto the newer-instrument scale (Cobas 6000 to Cobas 8000), establishing this as NCHS's own forward-compatible convention (E2). The 2017+ methods (Cobas/ARDL) are also the ones continued in subsequent NHANES cycles (2021-2023 and, per the same lineage, presumably later), making the 2017+ scale the more durable long-term reference. |
| Evidence Level               | E2 (official NHANES/CDC documentation, by analogy/precedent rather than a direct statement for the 2015-2016-to-2017-2018 pair specifically) |
| Confidence Rating            | Moderate — reasonable and consistent with NCHS's own apparent convention, but not a scientific requirement; either direction is mathematically equivalent given the same bridging equations. |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-16 |
| Related Assumptions          | — |
| Related Evidence Gaps        | EG-007 (closed — converted to this decision) |
| Notes                         | Revisit if a future NHANES cycle changes instrumentation again, which would re-open the question of which scale is most durable. |

---

### D-006

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Missing-data policy: complete-case exclusion |
| Description                 | AgeLens V1 will exclude a participant's record from Phenotypic Age computation if any of the 9 required biomarkers is missing for that participant, rather than imputing missing values. |
| Related Research Question   | RQ1, RQ4 |
| Supporting Evidence          | Levine et al. (2018) used complete-case exclusion in the original Phenotypic Age derivation and validation (E1, by precedent). Protocol SP-6 (Proportional Complexity) favors the simplest scientifically defensible approach over adding imputation machinery without independent justification. |
| Evidence Level               | E1 (precedent from the original methodology paper) |
| Confidence Rating            | Moderate — faithful to the original methodology (consistent with SP-1 Replication Before Innovation), but not independently tested for whether missingness is random across the 9 D-002-cycle biomarkers; a future Decision could revisit this if missingness proves substantial or non-random. |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-16 |
| Related Assumptions          | — |
| Related Evidence Gaps        | EG-008 (closed — converted to this decision) |
| Notes                         | Recommend a missingness-pattern check (e.g., Little's MCAR test or simple cross-tabulation) in the Validation Protocol before finalizing this as permanent policy. |

---

### D-007

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Confirmed unit conversions for D-001 formula application |
| Description                 | AgeLens V1 will apply the following conversions to NHANES LBX-prefixed source variables before evaluating the D-001 formula: Albumin ×10 (g/dL→g/L), Creatinine ×88.4 (mg/dL→µmol/L), Glucose ×0.0555 (mg/dL→mmol/L), CRP ÷10 (mg/L→mg/dL, before the log transform). No conversion needed for lymphocyte %, MCV, RDW, ALP, or WBC. |
| Related Research Question   | RQ1, RQ2 |
| Supporting Evidence          | Levine et al. (2018), *Aging*, Table 1 (E1, primary source, direct fetch); Levine et al. (2018) Supplementary Table S1, Supplement 1 (E1, primary source, user-provided) — independently confirms identical units including the unusual CRP mg/dL convention, ruling out a transcription/extraction artifact |
| Evidence Level               | E1 (two independent primary-source confirmations) |
| Confidence Rating            | High |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-16 |
| Related Assumptions          | — |
| Related Evidence Gaps        | EG-009 (closed — converted to this decision) |
| Notes                         | This was the single most critical open item in the entire project — applying the formula without these conversions would have produced scientifically invalid Phenotypic Age values. Resolved with high confidence given two independently-typeset primary-source tables agree exactly, including on the unusual CRP unit. See Replication_Protocol.md Section 7 for the full conversion table. **Further independently confirmed 2026-07-16:** the BioAge package's own published Methods text (Kwon & Belsky, 2021, full text) states they divided 2015-2016 CRP values by 10 to match units in previous waves — the identical conversion adopted here, arrived at independently by a different research team. See Paper_002_BioAge.md Section 16. |

---

*Add new entries below using the same template, incrementing the Decision ID.*

---

### D-008

| Field                       | Value |
| --------------------------- | ----- |
| Title                       | Confirmed NCHS bridging regression equations for hs-CRP and BIOPRO panel |
| Description                 | AgeLens V1 will apply the following official NCHS bridging equations, verified directly against primary source: hs-CRP: Y(Cobas)=0.8695×X(DxC660i)+0.2954, valid only for DxC660i ≤23 mg/L; Albumin: X(Cobas)=0.9581×Y(DxC660i)−0.0108; Creatinine: X(Cobas)=0.9515×Y(DxC660i)+0.06608; ALP: log10[X(Cobas)]=0.9986×log10[Y(DxC660i)]+0.04288. Full detail in Replication_Protocol.md Section 8. |
| Related Research Question   | RQ2 |
| Supporting Evidence          | Official CDC/NCHS documentation, directly fetched and verified: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BIOPRO_J.htm and https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/datafiles/HSCRP_J.htm, "Analytic Notes" sections, both provided by the user and fetched directly by Claude 2026-07-19 (E2, official NHANES/CDC documentation) |
| Evidence Level               | E2 (official NHANES/CDC documentation, directly verified — not a secondary summary) |
| Confidence Rating            | High |
| Reviewer                     | — |
| Status                        | Approved |
| Date                          | 2026-07-19 |
| Related Assumptions          | — |
| Related Evidence Gaps        | EG-013 (closed — converted to this decision) |
| Notes                         | The hs-CRP equation has a documented valid range (DxC 660i ≤ 23 mg/L / Cobas ≤ 20 mg/L, n=207 bridging samples); values outside this range should be flagged rather than silently adjusted, per NCHS's own caution (insufficient data, n=7, to recommend an adjustment above this range). BIOPRO equations (albumin, creatinine, ALP) are based on n=248 bridging samples. This also independently re-confirms EG-011's underlying claim (no adjustment needed for the DxC 800-to-660i in-cycle swap) via the same primary source, for both the BIOPRO and HSCRP panels. |

<!-- AGELENS GOVERNANCE RESOLUTION 2026-07-22 -->

---

### D-010

| Field | Value |
| --- | --- |
| Title | Canonical final conversion pair |
| Description | Adopt Supplement 1's `141.50225 / 0.090165` pair as canonical. Retain `141.50 / 0.09165` as a named sensitivity. Hybrid pairs are prohibited. |
| Supporting Evidence | Direct BioAge source inspection; Supplement MAE 0.049726–0.050348 years versus approximately 1.6 years for Erratum; Pearson/Spearman = 1.0. |
| Evidence Level | E4 plus E1/E3 corroboration |
| Confidence Rating | High |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Evidence Gaps | EG-010 — Closed |
| Notes | The remaining approximately 0.05-year difference reflects rounded published coefficients versus BioAge's higher-precision coefficients. |

---

### D-011

| Field | Value |
| --- | --- |
| Title | Handling of age top-coding at 80 |
| Description | Retain `RIDAGEYR == 80`, set `age_topcoded = TRUE`, never invent exact ages, and report full-sample plus no-topcode sensitivities. |
| Supporting Evidence | Official NHANES top-coding documentation and completed full/no-topcode validation. |
| Evidence Level | E2 plus direct V1 validation |
| Confidence Rating | High for handling policy |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Evidence Gaps | EG-014 — Closed as documented limitation |
| Notes | Top-coded records are excluded from the no-topcode face-validity correlation but retained in BioAge agreement checks. |

---

### D-012

| Field | Value |
| --- | --- |
| Title | Creatinine training-scale policy |
| Description | Use observed modern harmonized creatinine in the canonical replication. Report `+0.11`, `+0.17`, and `+0.23 mg/dL` shifts as mandatory sensitivities. |
| Supporting Evidence | Notebook 06 produced Supplement shifts of 1.024544, 1.583386, and 2.142228 years. |
| Evidence Level | E1 plus governed sensitivity analysis |
| Confidence Rating | Moderate |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Evidence Gaps | EG-004 — Closed as accepted and quantified limitation |
| Notes | No compensating shift becomes canonical without a future superseding Decision. |

---

### D-013

| Field | Value |
| --- | --- |
| Title | V1 validation acceptance criteria |
| Description | Approve Check 1 `|Δr| < 0.02`. Check 2 passes when Supplement MAE is below 0.10 years and Pearson/Spearman are at least 0.999999 in each cycle. |
| Supporting Evidence | Completed Checks 1–4 and independent R `survey` verification. |
| Evidence Level | Direct V1 validation evidence |
| Confidence Rating | High for deterministic regression testing |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Evidence Gaps | Supports closure of EG-002 and EG-010 |
| Notes | Check 4 remains a documented limitation; Little's MCAR was not run. |

---

### D-014

| Field | Value |
| --- | --- |
| Title | Exact pandas/XPORT IBM-zero sentinel normalization |
| Description | Convert only exact `5.397605346934028e-79` values to `0.0` immediately after XPT read and audit every replacement. General near-zero thresholding is prohibited. |
| Supporting Evidence | Ingestion audit documented 80,902 replacements, including both fasting-weight files. |
| Evidence Level | Direct implementation audit |
| Confidence Rating | High |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Evidence Gaps | — |
| Notes | Parser correction, not biological imputation. |

<!-- AGE-LENS MORTALITY AUTHORIZATION 2026-07-22 -->

---

### D-015

| Field | Value |
| --- | --- |
| Title | AgeLens V1 linked-mortality cohort and analysis authorization |
| Description | Authorize all-cause mortality analysis among canonical harmonized complete cases aged 20 years or older with `ELIGSTAT == 1`, observed `MORTSTAT`, and positive `PERMTH_EXM`. Use MEC examination as time origin. Use cycle-specific `WTSAF4YR`-weighted residuals of canonical Supplement Phenotypic Age on chronological age as the primary exposure. Fit survey-weighted Cox models with cycle-unique strata and PSUs. |
| Related Research Question | RQ4, RQ5 |
| Supporting Evidence | Canonical V1 rebuild passed 29/29 regression checks; linked mortality ingestion remained separate; authorization cohort contains 4,350 participants and 127 deaths. |
| Evidence Level | Direct governed data audit plus official linked-mortality variable definitions already incorporated in the project |
| Confidence Rating | High for cohort construction and all-cause outcome definition; model estimates remain unvalidated until notebook 10 |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Assumptions | MEC examination is the governed baseline; public-use follow-up months are used as released |
| Related Evidence Gaps | None blocking model execution |
| Notes | Primary HR is reported per 5-year higher acceleration. Adjusted models include chronological age, sex, race/ethnicity, and cycle. Required sensitivities are no-topcode, Erratum constants, three D-012 creatinine shifts, and exclusion of deaths within 12 months. Cause-specific mortality is not authorized. Mortality results remain non-reportable until notebook 10 passes its validation and release gate. |

<!-- AGE-LENS MORTALITY RESULTS RELEASE 2026-07-22 -->

---

### D-016

| Field | Value |
| --- | --- |
| Title | Release AgeLens V1 all-cause mortality model results |
| Description | Release the D-015-authorized survey-weighted Cox results after all required models, sensitivity analyses, reconciliation checks, and proportional-hazards diagnostics passed. |
| Related Research Question | RQ4, RQ5 |
| Supporting Evidence | Authorized cohort: 4,350 participants and 127 deaths. Primary adjusted HR per 5-year higher acceleration: 1.185354 (95% CI 1.128633–1.244926; p=1.06871e-11). PH diagnostic p=0.998565. |
| Evidence Level | Direct governed model execution and validation |
| Confidence Rating | High for the prespecified all-cause mortality analysis within the public-use follow-up window |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Assumptions | D-015 cohort and model specification |
| Related Evidence Gaps | None blocking release |
| Notes | All required sensitivity models were completed. The three creatinine-shift acceleration models reproduced the canonical model because cycle-specific residualization removes constant additive shifts. Cause-specific mortality remains unauthorized. |

<!-- AGE-LENS V1 FINAL RELEASE PACKAGE 2026-07-22 -->

---

### D-017

| Field | Value |
| --- | --- |
| Title | Approve the final AgeLens V1 reporting and release package |
| Description | Approve the final cross-sectional and all-cause mortality report, aggregate scientific tables, figures, provenance manifest, notebook inventory, configuration snapshot, reproducibility scripts, and aggregate-only release archive. |
| Related Research Question | RQ1–RQ5 |
| Supporting Evidence | Canonical validation passed 29/29 checks; mortality validation passed 22/22 checks; D-010 through D-016 are approved; no Core Evidence Gap remains open. |
| Evidence Level | Complete governed replication, model validation, and release-package audit |
| Confidence Rating | High for the prespecified AgeLens V1 scope |
| Reviewer | Project owner |
| Status | Approved |
| Date | 2026-07-22 |
| Related Assumptions | D-010 through D-016 |
| Related Evidence Gaps | None blocking V1 release |
| Notes | The archive excludes raw, interim, and participant-level data. Cause-specific mortality remains unauthorized. The primary adjusted mortality HR per 5-year higher acceleration is 1.185354 (95% CI 1.128633–1.244926; p=1.06871e-11). |
