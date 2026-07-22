# NHANES Harmonization Report

## Document Control

| Field             | Value                          |
| ------------------ | ------------------------------ |
| Document Title    | AgeLens NHANES Harmonization Report |
| Project             | AgeLens                        |
| Document ID         | AL-HARM-001                    |
| Version              | 0.9|
| Status               | Draft                          |
| Author               | Project Team                   |
| Reviewer             | —                               |
| Last Updated          | 2026-07-16                     |
| Related Documents  | Research Protocol (AL-RP-001), Decision_Log.md, Evidence_Gap_Register.md, Paper_001_Levine2018.md, Paper_004_SelvinEtAl2007.md, Variable_Mapping_Table.xlsx, Replication_Protocol.md, Validation_Protocol.md |

---

## Revision History

| Version | Date       | Summary of Changes                                      |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1     | 2026-07-16 | Initial laboratory-compatibility findings for the 9 PhenoAge biomarkers: albumin, creatinine, CRP |
| 0.2     | 2026-07-16 | D-002 fixed AgeLens V1 scope to NHANES 2015-2016 / 2017-2018 / 2017-March 2020; EG-005 closed as non-issue; new CRP method-change finding (EG-006) added |
| 0.3     | 2026-07-16 | EG-006 resolved via D-003 (NCHS hs-CRP bridging equations); EG-003 resolved and EG-004 downgraded via D-004 (NCHS BIOPRO bridging equations); remaining 6 biomarkers (glucose, lymphocyte %, MCV, RDW, ALP, WBC) reviewed — all clean within D-002 scope |
| 0.4     | 2026-07-16 | Patch: added missing back-reference to Paper_004_SelvinEtAl2007.md in Related Documents (no scientific content change) |
| 0.5     | 2026-07-16 | Factual correction: Section 4 (CRP) incorrectly named the in-cycle instrument swap as "DxC 800 to DxC 660i" — that pairing belongs to the BIOPRO panel (Section 2/3); corrected to "DxC 600 to DxC 660i" for CRP, per NHANES HSCRP_I documentation |
| 0.6     | 2026-07-16 | Sentence-by-sentence review: Related Documents field was missing Variable_Mapping_Table.xlsx, Replication_Protocol.md, Validation_Protocol.md despite Section 9's body text referencing all three; fixed. Added cross-reference note to EG-009/D-007 (unit conversion finding) for completeness |
| 0.7     | 2026-07-17 | Fixed EG-011: added the DxC 800-to-660i in-cycle instrument detail to Section 2 (Albumin), which Decision_Log.md and this report's own Section 4 had referenced as being here but was never actually written, per user's detailed technical review |
| 0.8     | 2026-07-17 | Reverted EG-004 characterization from Peripheral back to Core throughout (Section 3, summary table, Section 9) following user's detailed technical review and confirming simulation |
| 0.9     | 2026-07-19 | MAJOR: D-009 narrowed AgeLens V1 scope to 2015-2016 + 2017-2018 only, dropping the 2017-March 2020 pre-pandemic cycle (unequal-duration pooling complexity avoided). All 8 narrative sections updated; D-002 marked superseded throughout. |

*This file is a single authoritative document per DP-1 (Protocol Section 8.2) — never duplicated under a new filename. Update in place and bump the version above.*

---

## 1. Purpose

This report addresses **RQ2** ("How should NHANES III laboratory variables be harmonized with modern NHANES cycles while preserving methodological consistency?") for all 9 clinical biomarkers required by the D-001 Phenotypic Age formula.

**AgeLens V1 target NHANES cycles, per D-009 (supersedes D-002):** 2015–2016 and 2017–2018 only — both standard 2-year cycles. The 2017–March 2020 pre-pandemic cycle has been dropped from scope (2026-07-19) to avoid unequal-duration cycle pooling complexity. NHANES III remains in scope only as the D-001 training/derivation sample, not as a projection target.

It follows the governance principles of Protocol Section 10 (NHANES Governance and Harmonization Policy), in particular HG-2 (Evidence-Based Harmonization) and Section 10.4 (Laboratory Method Compatibility).

---

## 2. Albumin

**Finding:** Albumin is measured as part of the NHANES Standard Biochemistry Profile (BIOPRO). The BCP (bromocresol purple) method was used in NHANES III and has continued in continuous-cycle NHANES. Within the 2015–2016 cycle itself, the BIOPRO panel's instrument changed mid-cycle from a Beckman Coulter DxC 800 to a DxC 660i (both at Collaborative Laboratory Services, Ottumwa IA) — NCHS's bridging study (see below) confirmed no statistical adjustment is needed for this in-cycle swap. Within the D-009 target range, the lab instrument changed between 2015–2016 (Beckman Coulter DxC 660i) and 2017–2018 (Roche Cobas 6000, University of Minnesota ARDL). **This cross-cycle transition is resolved by D-004**: NCHS conducted an official method-validation (bridging) study (n=248 samples, late 2016) covering the entire BIOPRO panel, including albumin, and published bridging equations.

**Evidence:** NHANES 2017-2018 BIOPRO data documentation (E2, official CDC/NCHS documentation of the bridging study).

**Status:** EG-003 closed, converted to D-004.

---

## 3. Creatinine

**Finding:** Creatinine is also part of the BIOPRO panel, so the within-scope 2015-2016-to-2017+ instrument transition is covered by the same **D-004** bridging equations as albumin. A separate, older issue remains only partially addressed:

**Evidence (E1):** Selvin, E., Manzi, J., Stevens, L.A., Van Lente, F., Lacher, D.A., Levey, A.S., & Coresh, J. (2007). Calibration of serum creatinine in the National Health and Nutrition Examination Surveys (NHANES) 1988–1994, 1999–2004. *American Journal of Kidney Diseases, 50*(6), 918–926.

Key findings:
- NHANES III and NHANES 1999–2000 creatinine values (Jaffé method) showed **substantial bias** relative to a gold-standard traceable Roche enzymatic reference assay.
- NHANES 2001–2002 and 2003–2004 showed **no significant bias**.
- Bias magnitude in the affected cycles was large enough to produce **10–20% differences** in downstream kidney-function estimates.

**Residual question (EG-004, REINSTATED as Core, 2026-07-17):** D-001's coefficients were derived from NHANES III creatinine values — i.e., from data on the *biased* side of the Selvin et al. finding (~0.11-0.23 mg/dL higher than modern enzymatic values). Applying D-001's coefficients to internally-consistent, bridged 2015–2020 creatinine values does **not** automatically correct for this training-era bias — D-004 only harmonizes modern cycles against each other, not against the NHANES III scale D-001 was fit on. An independent simulation (2026-07-17) applying the documented bias range directly to the D-001 formula produced a systematic Phenotypic Age shift of approximately 1.0–2.1 years. This is a Core, unresolved concern requiring an explicit methodological decision (apply a compensating adjustment, or document as an accepted limitation) before final results are reported — not a minor sensitivity check.

---

## 4. C-Reactive Protein (CRP)

**Finding 1 — availability (resolved by D-009, formerly D-002):** CRP was not measured in the NHANES 2011–2014 continuous cycles. AgeLens V1's scope (2015–2016, 2017–2018, per D-009) does not fall in the CRP-less window — this availability concern is **closed as a non-issue (EG-005)**.

**Finding 2 — a within-scope method change:** CDC's own data documentation for the CRP (hs-CRP) component confirms a **laboratory method, equipment, and site change between the 2015–2016 cycle and the 2017–2018 cycle**:
- 2015–2016: measured on Beckman Coulter UniCel DxC 600 Synchron and DxC 660i Synchron Access analyzers.
- 2017–2018: CDC documentation explicitly states there were changes to the lab method, lab equipment, and lab site for this component — testing moved to the University of Minnesota Advanced Research Diagnostics Laboratory.

Both halves of this transition fall **within** the D-002-fixed AgeLens V1 scope. This is registered as **EG-006 (Core)** — the PhenoAge formula uses log-transformed CRP with a coefficient of 0.0954, the largest per-unit-log weight among the 9 biomarkers, so a discontinuity between 2015–2016 and 2017–2020 values could materially affect scoring consistency across the target cycle range if not accounted for.

**Planned Resolution — RESOLVED (D-003):** NCHS conducted and published a formal method-validation (bridging) study comparing the 2015–2016 and 2017–2018 hs-CRP methods, using NHANES samples from late 2016, with published regression equations to adjust between cycles. AgeLens V1 will apply these equations per **D-003**. Separately, NCHS confirmed no adjustment is needed for the mid-2016 in-cycle equipment swap (DxC 600 → DxC 660i, the CRP panel's own starting instrument — not to be confused with the BIOPRO panel's DxC 800 → DxC 660i swap in Section 2/3) within the 2015–2016 cycle itself.

**Status:** EG-006 closed, converted to D-003.

---

## 5. Glucose (Fasting Plasma Glucose)

**Finding:** Clean — no harmonization issue within the D-009 scope. NHANES 2017–2018 documentation explicitly states there were **no changes to lab site, lab method, or lab equipment** since 2015–2016; the same Roche Cobas C311 analyzer was used for both cycles. An equipment change (Roche C501 → C311) occurred earlier, in 2015, but this predates and is internal to the 2015–2016 cycle boundary itself, not a cross-cycle discontinuity within D-009 scope.

**Evidence:** NHANES 2015-2016 and 2017-2018 Plasma Fasting Glucose data documentation (GLU_I, GLU_J) (E2).

**Status:** No Evidence Gap required.

---

## 6. Lymphocyte %, Mean Cell Volume (MCV), Red Cell Distribution Width (RDW), White Blood Cell Count (WBC)

**Finding:** Clean — all four are components of the NHANES Complete Blood Count with 5-part Differential (CBC), measured on the Beckman Coulter DxH 800 instrument in the Mobile Examination Center. Official documentation for 2015–2016 and 2017–2018 each explicitly confirms: **"There were no changes to the lab method, lab equipment, or lab site for this component."** Both D-009 target cycles used the identical instrument and method.

**Evidence:** NHANES 2015-2016 and 2017-2018 CBC data documentation (CBC_I, CBC_J) (E2).

**Historical note (out of scope but worth flagging for the Validation Report):** CBC parameters have shown method-driven discontinuities in earlier NHANES history — e.g., a documented instrument change in 2012 (Beckman Coulter HMX → DXH) was associated with significant shifts in weighted-mean RDW (12.84% → 13.55%) and WBC (7.03 → 7.41 ×10³ cells/µL) between the 2011–2012 and 2013–2014 cycles. This predates and does not affect the D-009 scope, but demonstrates that CBC instrument changes are not always negligible — reinforcing why each D-009-cycle CBC file was checked individually rather than assumed stable.

**Status:** No Evidence Gap required.

---

## 7. Alkaline Phosphatase (ALP)

**Finding:** ALP is part of the same BIOPRO panel as albumin and creatinine (Section 2–3). The 2015-2016-to-2017+ instrument transition is covered by the same **D-004** bridging equations.

**Status:** Resolved by D-004, alongside albumin and creatinine.

---

## 8. Summary Table (All 9 Biomarkers)

| Biomarker  | Cross-Cycle Status within D-009 scope | Resolution |
| ---------- | ------------------------------- | ------------- |
| Albumin    | BIOPRO panel; instrument change 2015-16 → 2017+ | Resolved — D-004 (bridging equations) |
| Creatinine | Same BIOPRO transition, plus a REINSTATED Core NHANES-III-era question | Cross-cycle: resolved (D-004). NHANES-III training bias: unresolved (EG-004, Core) — see Section 3 |
| ALP        | Same BIOPRO transition | Resolved — D-004 |
| CRP        | Separate panel; instrument/lab/site change 2015-16 → 2017+ | Resolved — D-003 (bridging equations) |
| Glucose    | Same instrument (Cobas C311) throughout D-009 scope | Clean — no gap |
| Lymphocyte %, MCV, RDW, WBC | Same instrument (Beckman Coulter DxH 800) throughout D-009 scope | Clean — no gap |

---

## 9. Remaining Open Items

1. **EG-002 (Peripheral):** Direct BioAge `phenoage_calc.R` source-code confirmation still pending (from Paper_002_BioAge.md). Still open as of this writing.
2. **EG-004 (Core, REINSTATED 2026-07-17):** NHANES-III-trained coefficients applied to modern, bias-free creatinine data — independent simulation confirms ~1-2 year systematic impact. This is not a minor sensitivity check; it requires an explicit methodological decision before implementation is considered complete. See Evidence_Gap_Register.md EG-004 for the three candidate resolution paths.
3. ~~Obtain and formally record the specific D-003/D-004 bridging equation coefficients into a Variable Mapping Table~~ — **Done.** See Variable_Mapping_Table.xlsx (VM-001 through VM-014).
4. This report's own findings are complete for all 9 D-001 biomarkers within D-009 scope. Downstream documents building on this report: Variable_Mapping_Table.xlsx, Replication_Protocol.md, Validation_Protocol.md — all now exist.
5. **Note (out of this report's direct scope but related):** A separate methodological finding — that the D-001 formula requires SI/metric unit conversion for albumin, creatinine, glucose, and CRP before evaluation — was identified and resolved as EG-009/D-007. This is a units-matching concern between NHANES and the source publication, distinct from the cross-cycle NHANES harmonization concerns this report addresses. See Replication_Protocol.md Section 7 for details.
