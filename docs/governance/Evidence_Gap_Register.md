# Evidence Gap Register

## Document Control

| Field             | Value                          |
| ------------------ | ------------------------------ |
| Document Title    | AgeLens Evidence Gap Register  |
| Project             | AgeLens                        |
| Document ID         | AL-GOV-003                     |
| Version              | 0.21|
| Status               | Approved — all V1 gaps dispositioned |
| Author               | Project Team                   |
| Reviewer             | —                               |
| Last Updated          | 2026-07-23                     |
| Related Documents  | Research Protocol (AL-RP-001), Decision_Log.md, Assumption_Register.md, NHANES_Harmonization_Report.md, Replication_Protocol.md, Validation_Protocol.md, Evidence_Matrix.xlsx, Paper_004_SelvinEtAl2007.md |

---

## Revision History

| Version | Date       | Summary of Changes                                      |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1     | 2026-07-16 | Initialized empty template (EG-001 placeholder)             |
| 0.2     | 2026-07-16 | EG-001 (Core) populated from Paper_001 review                |
| 0.3     | 2026-07-16 | EG-001 closed (converted to D-001); EG-002 (Peripheral) opened from Paper_002 review |
| 0.4     | 2026-07-16 | EG-003, EG-004 (Core), EG-005 (Core/pending) opened from NHANES_Harmonization_Report.md v0.1 |
| 0.5     | 2026-07-16 | D-002 (cycle scope) fixed EG-005 as Closed/non-issue and narrowed EG-003/EG-004; EG-006 (Core) opened for CRP method change within 2015-2020 scope |
| 0.6     | 2026-07-16 | EG-006 closed (converted to D-003) - NCHS published official hs-CRP bridging equations |
| 0.7     | 2026-07-16 | EG-003 closed (converted to D-004); EG-004 downgraded to Peripheral (partially resolved by D-004) - NCHS BIOPRO bridging equations cover albumin/creatinine/ALP |
| 0.8     | 2026-07-16 | EG-007, EG-008 (Core) opened from Replication_Protocol.md v0.1 - both block implementation pending a Decision |
| 0.9     | 2026-07-16 | EG-007 closed (converted to D-005); EG-008 closed (converted to D-006) - both implementation blockers cleared |
| 0.10    | 2026-07-16 | Patch: EG-004 cross-referenced to Paper_004_SelvinEtAl2007.md; Related Documents completed |
| 0.11    | 2026-07-16 | CRITICAL: EG-009 opened - direct primary-source verification (Levine 2018 Table 1) shows the formula requires SI/metric units, not the US conventional NHANES LBX units previously assumed with no conversion. Blocks implementation. |
| 0.12    | 2026-07-16 | EG-009 closed (converted to D-007) - user-provided Supplement 1 independently confirms all unit conventions including the unusual CRP mg/dL convention, ruling out extraction artifact. No longer blocks implementation. |
| 0.13    | 2026-07-17 | CRITICAL: EG-010 opened - a real, unresolved discrepancy (0.09165 vs 0.090165) between the official erratum and Supplement 1, previously mischaracterized as a rounding difference until the user provided a detailed mathematical challenge proving a ~1.8 year systematic impact. EG-011 (Peripheral, DxC 800 dangling cross-reference) and EG-012 (Peripheral, unverified "bone ALP" wording) also opened following user's detailed technical review. |
| 0.14    | 2026-07-17 | EG-004 REINSTATED as Core following user's detailed technical review and confirming simulation (~1-2 year impact); EG-013 (Core, Critical) opened - bridging equation coefficients never recorded anywhere in the project |
| 0.15    | 2026-07-19 | EG-013 updated to 'provisionally populated pending verification' (candidate equations recorded but not confirmed); EG-010 updated with the 141.50 vs 141.50225 intercept note, independently confirmed negligible (~0.00225 years) unlike the denominator issue. |
| 0.16    | 2026-07-19 | EG-013 closed (converted to D-008) - user provided exact source URLs, Claude fetched and verified all coefficients word-for-word against official CDC documentation. |
| 0.17    | 2026-07-19 | D-009 narrowed scope to 2015-2016 + 2017-2018 only; removed 2017-March 2020 references throughout historical (non-revision-history) content, updated D-002 references to D-009 where describing current state. |
| 0.18    | 2026-07-19 | CRITICAL: EG-014 opened - NHANES age top-coding (80 in D-009 cycles vs 90 in NHANES III training data) confirmed via independent simulation to cause a ~6-9 year systematic understatement of Phenotypic Age for the 80+ subgroup - the highest-magnitude gap identified in this project to date. |
| 0.18    | 2026-07-19 | EG-014 (Core, Critical, HIGHEST MAGNITUDE) opened: NHANES age top-coding mismatch (80 in application data vs 90 in D-001 training data) produces ~6-9 year systematic bias for the 80+ subgroup. |
| 0.19 | 2026-07-22 | Closed EG-002 after direct BioAge source inspection; closed EG-004, EG-010, and EG-014 through D-012, D-010, and D-011. |
| 0.20 | 2026-07-22 | Synchronized current Classification, Planned Resolution, and impact wording for EG-004, EG-010, and EG-014 with their approved closure Decisions. |
| 0.21 | 2026-07-23 | Closed EG-012 after direct verification of the published wording, official BioAge interface, and completed D-013 benchmark. The phrase remains documented as a wording ambiguity; no distinct bone-specific ALP substitution was demonstrated in the PhenoAge implementation. |

**Current-state interpretation:** Revision History records the status that applied at each earlier version and therefore may use terms such as *open*, *unresolved*, or *blocking*. Those historical entries do not override the current operative sections, the latest Review Status fields, or Decisions D-010 through D-017.

*This file is a single authoritative document per DP-1 (Protocol Section 8.2) — never duplicated under a new filename. Update in place and bump the version above; closed gaps remain visible with their resolution, never deleted.*

---

## Purpose

This register tracks every documented methodological uncertainty (Evidence Gap) per Section 6.4 of the Research Protocol — cases where available evidence is currently insufficient to support a definitive decision. Evidence Gaps are managed uncertainties, not project failures.

---

## How to Use This Register

- Add one entry per Evidence Gap, in the order they are identified.
- Evidence Gap IDs follow the pattern `EG-NNN` (e.g., EG-001, EG-002).
- Classification must be `Core` (blocks implementation per Section 7.5) or `Peripheral` (documented but does not block progress).
- Every gap must be reviewed before each major project release (Section 6.6). Review outcome follows one of: Converted to Decision / Documented as Limitation / Deferred to Future Version / Implementation Postponed (Core only).
- Under no circumstances shall an unresolved Core Evidence Gap be silently ignored or left without a Review Status.

---

## Evidence Gap Entries

### EG-001

| Field                 | Value |
| ---------------------- | ----- |
| Description                | The canonical source for the Phenotypic Age equation is ambiguous. The original Levine et al. (2018) *Aging* article prints an equation that is missing a step and cannot be resolved as stated. A complete corrected version appears only in a 2019 erratum to a *companion* paper (Liu et al.), not as a direct correction to the original article. |
| Affected Component         | Core Phenotypic Age formula (biomarker → mortality score → age conversion) |
| Scientific Impact          | High — any coefficient or exponent error in the adopted formula propagates through every biological age estimate the project produces. |
| Classification               | Core |
| Existing Evidence            | Levine et al. (2018), *Aging* (E1, incomplete equation as printed); Liu et al., 2019 correction, *PLOS Medicine* (E1/E3 boundary, complete corrected equation) |
| Missing Evidence             | No confirmation yet that the BioAge R package or other validated implementations use the corrected coefficients; no direct erratum notice located on the *Aging* article's own page. |
| Planned Resolution           | Cross-check against Paper_002_BioAge.md source-code review; if BioAge matches the corrected equation, convert to Decision (D-001). |
| Review Status                 | **Closed — Converted to Decision (D-001)**, 2026-07-16. Resolved via convergent Category C evidence: independent peer-reviewed replication and multiple third-party implementations reproducing the corrected coefficients. |

---

### EG-002

| Field                 | Value |
| ---------------------- | ----- |
| Description                | The literal coefficient values hardcoded in the BioAge package's `phenoage_calc.R` source (`orig = TRUE` branch) have not been directly confirmed by source-code line inspection. D-001 relies on convergent indirect evidence (independent replication, third-party implementations) rather than direct source verification. |
| Affected Component         | BioAge software cross-check supporting D-001 |
| Scientific Impact          | Low-Moderate — D-001 already meets Category C evidence sufficiency; this gap concerns verification thoroughness, not the underlying scientific validity of the adopted formula. |
| Classification               | Peripheral |
| Existing Evidence            | Package documentation, vignette excerpts, independent peer-reviewed replication (E3), third-party calculators (E5) |
| Missing Evidence             | Direct inspection of `phenoage_calc.R` source lines defining the `orig = TRUE` coefficient vector |
| Planned Resolution           | Obtain direct source access (e.g., via package installation or repository clone) during implementation phase; confirm coefficients match D-001 before first production run. |
| Resolution Evidence | Notebook 04 source-token audit: all required coefficients and constants present. |
| Review Status                 | **Closed — direct source inspection completed**, 2026-07-22. |

---

### EG-003

| Field                 | Value |
| ---------------------- | ----- |
| Description                | Serum albumin assay method (bromocresol purple, BCP) has been confirmed consistent between NHANES III and the 2001-2004 continuous cycle, but not yet directly checked against official CDC Laboratory Procedure Manuals for cycles 2015-2020, which are more likely targets for AgeLens modern-data validation. |
| Affected Component         | Albumin variable mapping (NHANES Harmonization) |
| Scientific Impact          | Moderate — no evidence yet of a method change, but absence of contrary evidence is not itself confirmation per HG-2 (Evidence-Based Harmonization). |
| Classification               | Peripheral |
| Existing Evidence            | NHANES III and 2001-2004 cycle documentation both confirm BCP (E2/E3) |
| Missing Evidence             | Direct confirmation for the D-009-fixed target cycles (2015-2016, 2017-2018) via official CDC Laboratory Procedure Manuals |
| Planned Resolution           | Check CDC Laboratory Procedure Manuals specifically for 2015-2016, 2017-2018, |
| Review Status                 | **Closed — Converted to Decision (D-004)**, 2026-07-16. Albumin is part of the NHANES Standard Biochemistry Profile (BIOPRO), which underwent an official NCHS method-validation (bridging) study between the 2015-2016 (Beckman Coulter DxC 660i) and 2017-2018 (Roche Cobas 6000) instruments, with published bridging equations (n=248 comparison samples). |

---

### EG-004

| Field                 | Value |
| ---------------------- | ----- |
| Description                | A documented, quantitatively significant calibration bias exists between NHANES III / 1999-2000 serum creatinine values (Jaffe method) and later cycles measured against a gold-standard enzymatic reference (Selvin et al. 2007, AJKD: NHANES III creatinine read ~0.11-0.23 mg/dL higher than modern enzymatic values). D-001's coefficients were trained on this biased NHANES III scale. The governing question was whether applying these coefficients to modern, differently calibrated creatinine values required a correction for this training-era bias — this is separate from and not resolved by the D-009-to-D-009-cycle cross-instrument bridging (D-004). |
| Affected Component         | Creatinine variable mapping; directly affects the scientific validity of every D-001 score computed on the D-009 target cycles |
| Scientific Impact          | **High.** Independent simulation (2026-07-17, prompted by user's detailed mathematical challenge) confirmed: applying the documented 0.11-0.23 mg/dL Selvin et al. bias directly to the D-001 formula produces a systematic Phenotypic Age shift of approximately 1.0 to 2.1 years (midpoint ~1.5-1.8 years) across the plausible bias range, holding other biomarkers at typical values. This is not negligible and was previously mischaracterized as "Moderate" when downgraded to Peripheral. |
| Classification               | **Core at identification; closed under D-012 as an accepted and quantified limitation.** D-004 resolves modern cross-cycle comparability, while D-012 separately governs the NHANES-III training-scale issue. |
| Existing Evidence            | Selvin et al. (2007), AJKD (E1) — bias confirmed in NHANES III and 1999-2000 at ~0.11-0.23 mg/dL, absent in 2001-2002 and 2003-2004; published calibration equations exist. Selvin et al. did not study cycles beyond 2003-2004. See Paper_004_SelvinEtAl2007.md for full formal review. Independent AgeLens simulation (2026-07-17) confirms ~1.0-2.1 year impact magnitude using the documented bias range. |
| Missing Evidence             | Whether the Jaffe method (or an updated method) remained free of the documented bias through the D-009 target cycles (2015-2016 onward) — this affects whether *modern* data needs adjustment; separately, whether D-001's NHANES-III-trained coefficients need an *inverse* adjustment to correctly interpret bias-free modern data (i.e., the coefficient may have implicitly calibrated to the inflated NHANES III scale, meaning accurate modern data could be systematically mis-scored without a compensating adjustment) |
| Planned Resolution           | **Completed through D-012.** Use observed modern harmonized creatinine canonically; report `+0.11`, `+0.17`, and `+0.23 mg/dL` shifts as mandatory sensitivities; do not make a compensating shift canonical without a superseding Decision. |
| Resolution Evidence | Notebook 06 Supplement shifts: 1.024544, 1.583386, 2.142228 years. |
| Review Status                 | **Closed — accepted and quantified limitation; converted to D-012**, 2026-07-22. |

---

### EG-005

| Field                 | Value |
| ---------------------- | ----- |
| Description                | CRP was not measured in the NHANES 2011-2014 continuous cycles. Per Protocol Section 10.6 Category B, this requires evaluating alternative cycles or formally excluding the affected window. |
| Affected Component         | CRP variable mapping; NHANES cycle scope for AgeLens V1 |
| Scientific Impact          | None — D-009 fixed AgeLens V1's target cycles to 2015-2016, 2017-2018,, none of which fall in the CRP-less 2011-2014 window. |
| Classification               | Peripheral (downgraded from Core following D-009 (formerly D-002)) |
| Existing Evidence            | BioAge package documentation confirms CRP availability in NHANES 1999-2010 and 2015-2018 (E4); CDC data documentation confirms CRP availability in 2015-2016, 2017-2018, (E2) |
| Missing Evidence             | None — resolved |
| Planned Resolution           | N/A |
| Review Status                 | **Closed — Documented as non-issue following D-009 (formerly D-002)** (V1 scope excludes the affected cycles), 2026-07-16 |

---

### EG-006

| Field                 | Value |
| ---------------------- | ----- |
| Description                | CRP (hs-CRP) laboratory method, equipment, and testing site changed between the NHANES 2015-2016 cycle (Beckman Coulter UniCel DxC 600/660i Synchron) and the 2017-2018 cycle (moved to University of Minnesota Advanced Research Diagnostics Laboratory, with documented changes to lab method and equipment). Both are within the D-009-fixed AgeLens V1 scope. |
| Affected Component         | CRP variable mapping (log-transformed CRP carries a PhenoAge coefficient of 0.0954, the largest per-unit-log-CRP weight in the formula) |
| Scientific Impact          | Moderate-High — a within-scope assay change could introduce a discontinuity in CRP values (and therefore PhenoAge) between the 2015-2016 cycle and the 2017-2020 cycles if not accounted for. |
| Classification               | Core |
| Existing Evidence            | CDC NHANES data documentation for HSCRP_I (2015-2016) and HSCRP_J (2017-2018), both confirming the equipment/site/method change (E2) |
| Missing Evidence             | Whether NCHS has published a cross-cycle comparability or calibration study for hs-CRP specifically bridging 2015-2016 and 2017-2020 methods |
| Planned Resolution           | Search for an NCHS analytic note or published comparability study on this specific hs-CRP method transition; if none exists, consider restricting AgeLens V1 to the 2017-2020 cycles only, or treating 2015-2016 as a separate harmonization stratum |
| Review Status                 | **Closed — Converted to Decision (D-003)**, 2026-07-16. NCHS conducted and published a formal method-validation (bridging) study comparing the 2015-2016 and 2017-2018 hs-CRP methods using NHANES samples from late 2016, with published regression equations to adjust between cycles (Category A/B evidence — official NHANES documentation). |

---

### EG-007

| Field                 | Value |
| ---------------------- | ----- |
| Description                | The D-003/D-004 bridging equations can adjust values in either direction (2015-2016 onto the 2017+ scale, or 2017+ onto the 2015-2016 scale). AgeLens has not yet decided which cycle's scale serves as the project's reference scale. |
| Affected Component         | Replication Protocol Step D (Cross-Cycle Bridging); directly blocks implementation |
| Scientific Impact          | Moderate — either direction is scientifically valid per the NCHS bridging studies, but the choice must be made once and applied consistently. |
| Classification               | Core (blocks implementation, per HG-3 Documentation Before Transformation) |
| Existing Evidence            | D-003, D-004 (bridging equations exist in both directions per NCHS documentation) |
| Missing Evidence             | A project decision on reference-scale direction |
| Planned Resolution           | Decision needed — see Replication_Protocol.md Section 12 |
| Review Status                 | **Closed — Converted to Decision (D-005)**, 2026-07-16. Adjust 2015-2016 values onto the 2017+ scale, following NCHS's own apparent bridging convention. |

---

### EG-008

| Field                 | Value |
| ---------------------- | ----- |
| Description                | AgeLens has not formally adopted a missing-data policy. Replication_Protocol.md Section 9 proposes complete-case exclusion (consistent with Levine et al. 2018's own approach) as a provisional default, but this has not been logged as an approved Decision. |
| Affected Component         | Replication Protocol Step E (Missing Data Handling); directly blocks implementation |
| Scientific Impact          | Moderate — affects final analytic sample size and potentially introduces selection effects if missingness is non-random across the 9 biomarkers. |
| Classification               | Core (blocks implementation, per HG-3) |
| Existing Evidence            | Levine et al. (2018) used complete-case exclusion (E1, by precedent, not explicit methodological argument) |
| Missing Evidence             | A project decision formally adopting (or rejecting) complete-case exclusion for AgeLens V1 |
| Planned Resolution           | Decision needed — see Replication_Protocol.md Section 12 |
| Review Status                 | **Closed — Converted to Decision (D-006)**, 2026-07-16. Complete-case exclusion adopted, consistent with Levine et al.'s original approach and SP-6 (Proportional Complexity). |

---

### EG-009 (CRITICAL)

| Field                 | Value |
| ---------------------- | ----- |
| Description                | Direct verification against Levine et al. (2018), *Aging*, Table 1 (fetched from the primary source) shows the Phenotypic Age formula's biomarker weights were fit on SI/metric units (g/L for albumin, umol/L for creatinine, mmol/L for glucose), not the US conventional clinical units (g/dL, mg/dL, mg/dL respectively) that NHANES's default LBXSAL/LBXSCR/LBXGLU variables report. Replication_Protocol.md previously stated — incorrectly — that no unit conversion was needed. Applying the formula to unconverted values would produce materially wrong Phenotypic Age estimates. |
| Affected Component         | Replication_Protocol.md Step C (Unit Standardization); directly affects every Phenotypic Age computation |
| Scientific Impact          | Critical — this affects the correctness of every score the pipeline would produce. Not a peripheral or cosmetic issue. |
| Classification               | Core — blocks implementation until resolved |
| Existing Evidence            | Levine et al. (2018), *Aging*, Table 1, fetched directly from https://doi.org/10.18632/aging.101414 (E1, primary source, directly verified) |
| Missing Evidence             | (1) Confirmation the Table 1 units are correctly transcribed and not an artifact of automated content extraction — ideally cross-check the original PDF or Supplement 1 directly. (2) The CRP unit specifically is ambiguous — Table 1 states "mg/dL" which is an unusual convention for hs-CRP and could itself be a table error, separate from the already-documented xb-equation erratum. (3) Confirmation that D-001's adopted coefficients (from the Liu et al. correction) were fit under the same unit convention as Levine 2018 Table 1 — this has not been independently verified, only inferred from matching coefficient values. |
| Planned Resolution           | Before implementation: (1) obtain and inspect Levine et al. (2018) Supplement 1 directly; (2) cross-check against BioAge R package source code — if `phenoage_calc()` expects NHANES's native LBX units without conversion, that would be strong evidence the coefficients are actually calibrated for US conventional units despite Table 1, and Table 1 may describe a different intermediate representation. Related to and should be resolved alongside EG-002. |
| Review Status                 | **Closed — Converted to Decision (D-007)**, 2026-07-16. User provided Levine et al. (2018) Supplementary Table S1 (from Supplement 1), which independently confirms the same SI units as the main text Table 1 — including the unusual CRP mg/dL convention, appearing identically in two independently-typeset tables. This rules out a transcription/extraction artifact. All 9 biomarker unit conversions are now confirmed with high confidence. |

---

### EG-010 (CRITICAL)

| Field                 | Value |
| ---------------------- | ----- |
| Description                | The Levine et al. (2018) Supplementary Table S1 gives the PhenotypicAge formula's final conversion denominator as 0.090165, while the official PLOS Medicine erratum (Liu et al., 2019, independently re-verified against PMC6388911) states 0.09165. This is not a rounding difference - a mortality score of 0.01 yields ~34.6 years using 0.09165 versus ~32.8 years using 0.090165, a systematic ~1.8-year discrepancy affecting every computed score depending on which value is adopted. Independent practitioner forum discussions confirm this exact discrepancy is separately known and disputed outside AgeLens. Previously and incorrectly dismissed in Replication_Protocol.md v0.3 as a "minor precision difference" - identified as a real, unresolved discrepancy following the user's detailed mathematical challenge. **UPDATE 2026-07-19:** the same two sources also differ on the formula's leading intercept - Supplement 1 gives 141.50225, the erratum gives 141.50. Unlike the denominator discrepancy, Claude independently checked this and found it genuinely negligible: approximately 0.00225 years (under one day) of impact at a mortality score of 0.01 - not the same category of issue. Logged for completeness per the user's request; this specific sub-point does not itself require resolution before implementation. |
| Affected Component         | D-001's core formula (final age-conversion step); affects every Phenotypic Age value the pipeline would ever produce |
| Scientific Impact          | Critical - a ~1.8 year systematic bias (direction depending on which constant is correct) would affect every score, every analysis, and any conclusion drawn from the resulting data. |
| Classification               | Core at identification; **closed under D-010** after direct BioAge comparison selected the Supplement pair as canonical and retained the Erratum pair as sensitivity |
| Existing Evidence            | Levine et al. (2018) Supplementary Table S1 (E1, user-provided document): 0.090165. Liu et al. (2019) official PLOS Medicine erratum, independently re-verified via PMC6388911 (E1, formally published correction notice): 0.09165. Public practitioner forum discussion (E5) confirms independent awareness of this exact discrepancy, with disagreement among independent researchers about which is correct. |
| Missing Evidence             | No definitive third-party resolution located. Neither source has itself corrected or acknowledged the other's differing value. The BioAge R package's actual hardcoded constant (relevant to EG-002) has not been directly inspected and could adjudicate this empirically if obtained. |
| Planned Resolution           | **Completed through D-010.** Use the Supplement pair `141.50225 / 0.090165` canonically; retain the Erratum pair `141.50 / 0.09165` as a named sensitivity; prohibit hybrid pairs. |
| Resolution Evidence | Supplement MAE 0.049726–0.050348; Pearson/Spearman = 1.0. |
| Review Status                 | **Closed — converted to D-010**, 2026-07-22. |

---

### EG-011

| Field                 | Value |
| ---------------------- | ----- |
| Description                | Decision_Log.md (D-003 and D-004 Notes) and NHANES_Harmonization_Report.md Section 4 (CRP) reference a "DxC 800 to DxC 660i" in-cycle instrument swap as belonging to the BIOPRO panel, "in Section 2/3" of the Harmonization Report - but Sections 2 and 3 (Albumin, Creatinine) do not actually mention DxC 800 anywhere. The cross-reference points to detail that was never written. |
| Affected Component         | NHANES_Harmonization_Report.md Sections 2-3 (documentation completeness only) |
| Scientific Impact          | Low - the underlying fact (BIOPRO's DxC 800-to-660i in-cycle swap) was independently verified via web search during the original harmonization review and is not itself in question; only the written cross-reference is incomplete. |
| Classification               | Peripheral |
| Existing Evidence            | Prior web search confirmed BIOPRO panel's 2015-2016 in-cycle instrument transition as DxC 800 to DxC 660i (E2, official NHANES documentation, previously verified but never written into Sections 2-3) |
| Missing Evidence             | None - resolution is a documentation completeness fix, not new evidence |
| Planned Resolution           | Add the DxC 800-to-660i detail explicitly to NHANES_Harmonization_Report.md Sections 2-3 |
| Review Status                 | **Closed — Documented**, 2026-07-17. DxC 800-to-660i detail added to NHANES_Harmonization_Report.md Section 2 (Albumin), resolving the dangling cross-reference. |

---

### EG-012

| Field                 | Value |
| ---------------------- | ----- |
| Description                | The published BioAge Methods text does use the phrase "bone alkaline phosphatase values" for a 1999–2000 NHANES harmonization step. However, the same article identifies the original Levine PhenoAge biomarker as alkaline phosphatase, and the official BioAge examples and interface use the generic variable `alp`. The wording alone therefore does not demonstrate that the distinct NHANES bone-specific ALP component replaced standard total serum ALP in the PhenoAge algorithm. |
| Affected Component         | Validation_Protocol.md Check 2 and interpretation of the Kwon & Belsky (2021) harmonization description |
| Scientific Impact          | Low after verification. AgeLens supplied standard total ALP to the directly inspected BioAge implementation and satisfied the D-013 agreement threshold. No implementation-level ALP mismatch affecting the completed benchmark was demonstrated. |
| Classification               | Peripheral at identification; closed as a documented wording ambiguity after publication, package-interface, and benchmark verification |
| Existing Evidence            | Kwon & Belsky (2021), GeroScience 43:2795–2808, doi:10.1007/s11357-021-00480-5; official `dayoonkwon/BioAge` examples and interface using `alp`; AgeLens installed-source audit and D-013 BioAge agreement results |
| Missing Evidence             | None required for the approved V1 scope. A future package-history audit could investigate why the harmonization sentence used the word "bone," but this does not alter the governed AgeLens input or completed validation result. |
| Planned Resolution           | Completed. Preserve the phrase as a documented ambiguity, continue using standard total ALP as specified by Levine et al. and Replication_Protocol.md, and treat the completed direct package benchmark as the governing Check 2 evidence. |
| Review Status                 | **Closed — documented wording ambiguity; no implementation mismatch demonstrated**, 2026-07-23. |

---

### EG-013 (CRITICAL)

| Field                 | Value |
| ---------------------- | ----- |
| Description                | The literal, numeric NCHS bridging regression equations for hs-CRP (D-003) and BIOPRO/albumin-creatinine-ALP (D-004) have never been obtained or recorded anywhere in the AgeLens document set. Every reference to these equations (in Decision_Log.md D-003/D-004, Replication_Protocol.md Step D, and Variable_Mapping_Table.xlsx) describes their existence and cites the official NCHS comparability studies that produced them, but none records the actual coefficients (intercept, slope) needed to apply them in code. Per DP-1 (Single Source of Truth) and general reproducibility standards, a Replication Protocol is incomplete if it cannot be executed without external, unrecorded information. |
| Affected Component         | Replication_Protocol.md Step D (Cross-Cycle Bridging); directly blocks implementation of D-003 and D-004 |
| Scientific Impact          | Critical — without these equations, Step D cannot be coded at all. This is not a documentation-location issue (Markdown vs. Excel) but a documentation-existence issue: the equations are absent from every AgeLens document. |
| Classification               | Core — blocks implementation |
| Existing Evidence            | NCHS's own hs-CRP and BIOPRO comparability/bridging study documentation confirms these equations were officially published (E2), but AgeLens's tooling could not access the underlying CDC/NCHS documentation PDFs directly (network restriction) nor locate the literal coefficients via general web search. |
| Missing Evidence             | The literal regression equations themselves (intercept and slope for each biomarker's 2015-2016-to-2017+ adjustment) |
| Planned Resolution           | Obtain the official NCHS comparability/bridging study reports directly from wwwn.cdc.gov (e.g., the HSCRP_J and BIOPRO_J data documentation pages and any linked comparability study PDF) — this requires either the user downloading and sharing these documents, or implementation-phase tooling with access to cdc.gov. Once obtained, record the literal equations in Replication_Protocol.md Step D itself (not only Variable_Mapping_Table.xlsx), consistent with DP-1. |
| Review Status                 | **Closed — Converted to Decision (D-008)**, 2026-07-19. User supplied the exact official CDC/NCHS URLs (BIOPRO_J.htm, HSCRP_J.htm). Claude fetched both directly and independently verified every previously-provisional coefficient word-for-word against the "Analytic Notes" sections — all confirmed correct. The equations are now recorded in Replication_Protocol.md Section 8 as confirmed, cited primary-source values, not provisional ones. |

---

### EG-014 (CRITICAL - HIGHEST MAGNITUDE)

| Field                 | Value |
| ---------------------- | ----- |
| Description                | NHANES top-codes chronological age (RIDAGEYR) for privacy: participants aged 80+ are all recorded as exactly "80" in the D-009 target cycles (2015-2016, 2017-2018) - confirmed via official NHANES demographic data documentation. D-001's coefficients, however, were trained on NHANES III, which top-coded age at 90, not 80. This creates two compounding problems: (1) within the D-009 scope, any participant genuinely aged 81-99+ is coded as 80, directly and artificially lowering their computed xb via the formula's 0.0804 age coefficient, since age enters the formula directly (not merely as a covariate); (2) the top-coding THRESHOLD MISMATCH (90 in training data vs 80 in application data) means the modern data's top-coded subgroup is more severely truncated than what the coefficient was calibrated to expect from NHANES III's own top-coded records. |
| Affected Component         | Chronological age extraction (Replication_Protocol.md Step B); Step F formula application for every participant aged 80+; Validation_Protocol.md Check 1 (age correlation) |
| Scientific Impact          | **Critical and the highest-magnitude gap at the time of identification.** Independent simulation (2026-07-19) showed approximately 6.1 years of understatement for a true age of 87 recorded as 80 and approximately 8.8 years for a true age of 90. D-011 closes the governance gap by defining a retain/flag/no-topcode-sensitivity policy; it does not eliminate the underlying public-use-data limitation. |
| Classification               | Core at identification; **closed under D-011 as an accepted limitation.** Canonical records are retained and flagged, exact ages are never invented, and full/no-topcode results are reported. |
| Existing Evidence            | NHANES 2017-2018 and 2017-March 2020 demographic data documentation (DEMO_J.htm, P_DEMO.htm), confirming top-coding at 80 with weighted mean true age ~85 for the top-coded group (E2, official CDC/NCHS documentation). NHANES III top-coding at 90 confirmed via independent methodology documentation (E2/E5). Independent AgeLens simulation (2026-07-19) confirms ~6-9 year magnitude. |
| Missing Evidence             | Whether Levine et al. (2018) applied any correction or exclusion for NHANES III's own 90-year top-coded participants during original model derivation (would clarify whether the 0.0804 coefficient itself already partially absorbs a top-coding artifact, similar to the EG-004 creatinine question) |
| Planned Resolution           | **Completed through D-011.** Retain RIDAGEYR == 80 records, set `age_topcoded = TRUE`, never invent exact ages, report the canonical full sample and no-topcode sensitivity, and exclude topcoded records only from the no-topcode face-validity correlation. |
| Resolution Evidence | Full and no-topcode validation completed; retain/flag/report policy approved. |
| Review Status                 | **Closed — accepted limitation; converted to D-011**, 2026-07-22. |

<!-- AGELENS GOVERNANCE RESOLUTION 2026-07-22 -->
