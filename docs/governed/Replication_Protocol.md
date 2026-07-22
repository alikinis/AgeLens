# Replication Protocol

## Document Control

| Field             | Value                          |
| ------------------ | ------------------------------ |
| Document Title    | AgeLens Replication Protocol   |
| Project             | AgeLens                        |
| Document ID         | AL-METH-001                    |
| Version              | 1.3|
| Status               | Approved for canonical V1 rebuild                          |
| Author               | Project Team                   |
| Reviewer             | —                               |
| Last Updated          | 2026-07-22                     |
| Related Documents  | Research Protocol (AL-RP-001), Decision_Log.md, NHANES_Harmonization_Report.md, Variable_Mapping_Table.xlsx, Paper_001_Levine2018.md, Paper_002_BioAge.md |

---

## Revision History

| Version | Date       | Summary of Changes                                      |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1     | 2026-07-16 | Initial draft — full 9-biomarker pipeline specified end-to-end, governed entirely by prior Decisions |
| 0.2     | 2026-07-16 | D-005 (bridging direction) and D-006 (missing-data policy) approved, resolving the two implementation-blocking gaps (EG-007, EG-008) flagged in v0.1 |
| 0.3     | 2026-07-16 | CRITICAL: Step C (Unit Standardization) was wrong. Direct primary-source verification (Levine et al. 2018, Table 1) shows the formula requires SI/metric units (g/L, umol/L, mmol/L), not the unconverted NHANES LBX units (g/dL, mg/dL) this document previously specified. Opened EG-009 (Core, Critical). Table rewritten with correct conversion factors; CRP unit left explicitly unresolved pending further verification. |
| 0.4     | 2026-07-16 | Full sentence-by-sentence internal consistency review: (1) EG-009 resolution via D-007 (user-provided Supplement 1) reflected in Section 7 and Section 12, which had gone stale; (2) corrected a false claim that fasting sample weights were "addressed in Validation_Protocol.md" — they were not; now flagged accurately and actually added to Validation_Protocol.md Section 8; (3) Section 13 corrected — Validation Protocol already exists, next step is Implementation |
| 0.5     | 2026-07-17 | CRITICAL CORRECTION: the "Note on formula constants" previously and incorrectly dismissed the 0.09165 vs 0.090165 discrepancy as a rounding difference. Following the user's detailed mathematical challenge (proving a ~1.8 year systematic impact), this is now correctly flagged as EG-010 (Core, Critical, open), with 0.09165 retained as a provisional default pending empirical resolution. |
| 0.6     | 2026-07-17 | CRITICAL: flagged EG-013 - the literal NCHS bridging equations were never recorded anywhere in this project, only referenced conceptually |
| 0.7     | 2026-07-19 | Pipeline order corrected: Step D (bridging) now runs before Step C (unit standardization) - user's worked example (0.3824 vs 0.1165 mg/dL) confirmed the original order was wrong. User-supplied bridging equations recorded in Step D with an explicit unverified-provenance warning (Claude cannot confirm cdc.gov access claim or corroborate the coefficients). |
| 0.8     | 2026-07-19 | RESOLVED: EG-013 closed via D-008. User provided exact official CDC source URLs (BIOPRO_J.htm, HSCRP_J.htm); Claude fetched both directly and verified every coefficient word-for-word - all confirmed correct. Equations in Step D are now confirmed, cited primary-source values, including the previously-unknown CRP validity range (<=23 mg/L). |
| 0.9     | 2026-07-19 | Added step-discontinuity warning for the CRP bridging boundary (23 mg/L) - a naive threshold implementation would create an artificial ~2.8 mg/L jump; added flagging guidance instead. Added confirmed pooled fasting-weight formula (WTSAF2YR x2/5.2 + WTSAFPRP x3.2/5.2) for combining the two unequal-duration D-002 cycles - both per user's detailed technical review. |
| 1.0     | 2026-07-19 | CRITICAL SELF-CONSISTENCY FIX: Sections 12-13 falsely claimed 'no Core gap blocks implementation' while Evidence_Gap_Register.md listed EG-004 and EG-010 as Core/Open - a direct violation of Research Protocol Section 6.6 ('Block implementation until resolved'). Corrected to accurately state these two Core gaps must be resolved before Implementation proceeds to producing final scores. Identified by user's detailed cross-document consistency review. |
| 1.1     | 2026-07-19 | MAJOR: D-009 narrowed scope to 2015-2016 + 2017-2018 only, dropping 2017-March 2020. Removed P_DEMO/P_BIOPRO/P_GLU/P_HSCRP/P_CBC file references; simplified pooled-weight section to standard 2-cycle combination (WTSAF2YR/2), removing the fractional WTSAFPRP approach entirely. |
| 1.2     | 2026-07-19 | CRITICAL: EG-014 (age top-coding) added to Step B, Section 12, and Section 13 - highest-magnitude open gap identified to date (~6-9 years). Sections 12-13 now list three open Core blockers (EG-004, EG-010, EG-014). |
| 1.2     | 2026-07-19 | CRITICAL: EG-014 opened - NHANES age top-coding at 80 (vs NHANES III's 90 in D-001's training data) creates a ~6-9 year systematic understatement for genuinely 80+ participants, the largest-magnitude issue found to date. Added age_topcoded indicator requirement to Step B; updated Section 12/13 blocker list to include EG-014. |
| 1.3 | 2026-07-22 | Incorporated D-010 through D-014 and removed the former Core-gap blockers after completed governance resolution. |

*This file is a single authoritative document per DP-1 (Protocol Section 8.2) — never duplicated under a new filename. Update in place and bump the version above.*

---

## 1. Purpose

This document specifies the exact, reproducible procedure for computing AgeLens Version 1 Phenotypic Age scores from NHANES data. It is a **methodology specification**, not source code — per Section 10 of the Research Protocol ("Implementation has intentionally not yet started"), this document exists to fully determine *what* the implementation must do before any code is written, per SP-2 (Evidence Before Implementation).

Every step below is governed by a specific prior Decision. No step in this protocol may be altered without a corresponding Decision Log update.

---

## 2. Scope

**In scope:** the complete computational path from raw NHANES data files to a Phenotypic Age value per participant, for the two D-009 target cycles (2015–2016, 2017–2018).

**Out of scope:** DNAm PhenoAge (methylation-based), KDM Biological Age, Homeostatic Dysregulation, and any biomarker outside the 9-variable D-001 formula. Per Protocol Section 4.2.

---

## 3. Governing Decisions (Summary)

| Decision | Governs |
| -------- | ------- |
| D-001 | The canonical Phenotypic Age formula and coefficients (Liu et al. 2019-corrected) |
| D-009 (supersedes D-002) | Target NHANES cycles: 2015–2016, 2017–2018 |
| D-003 | hs-CRP bridging equations between 2015–2016 and 2017+ cycles |
| D-004 | BIOPRO (albumin, creatinine, ALP) bridging equations between 2015–2016 and 2017+ cycles |
| D-005 | Bridging direction: adjust 2015–2016 values onto the 2017+ reference scale |
| D-006 | Missing-data policy: complete-case exclusion |

---

## 4. Pipeline Overview

**NOTE:** Step C and Step D are numbered by document section below (Section 7 = Step C, Section 8 = Step D) for historical continuity, but **execute in the reverse of that section order** — Step D (bridging, native units) runs before Step C (unit standardization, Levine units). See Section 7's correction note for the reasoning.

```
Raw NHANES Files (per Variable_Mapping_Table.xlsx)
        ↓
Step A: File Acquisition & Cycle Tagging
        ↓
Step B: Variable Extraction (9 biomarkers + age, per VM-001 to VM-014)
        ↓
Step D: Cross-Cycle Bridging (D-003, D-004) — runs BEFORE Step C; see Section 8
        ↓
Step C: Unit Standardization — runs AFTER Step D; see Section 7
        ↓
Step E: Missing Data Handling
        ↓
Step F: Formula Application (D-001)
        ↓
Step G: Output Validation Checks
        ↓
Phenotypic Age per participant, per cycle
```

---

## 5. Step A — File Acquisition & Cycle Tagging

For each of the two D-009 target cycles, acquire the following public NHANES data files (demographic + laboratory components), tagging every record with its source cycle:

| Cycle | Demographics File | Lab Files Needed |
| ----- | ------------------ | ----------------- |
| 2015–2016 | DEMO_I | BIOPRO_I, GLU_I, HSCRP_I, CBC_I |
| 2017–2018 | DEMO_J | BIOPRO_J, GLU_J, HSCRP_J, CBC_J |

Merge each cycle's files on the NHANES respondent sequence number (SEQN). Records must remain traceable to their source cycle throughout the pipeline (required for Step D).

---

## 6. Step B — Variable Extraction

Extract, per Variable_Mapping_Table.xlsx (VM-001 through VM-014):

- Albumin (LBXSAL), Creatinine (LBXSCR), Alkaline Phosphatase (LBXSAPSI) — from BIOPRO
- Fasting Glucose (LBXGLU — **not** LBXSGL; see VM-005 note) — from GLU
- CRP (LBXHSCRP) — from HSCRP
- Lymphocyte % (LBXLYPCT), MCV (LBXMCVSI), RDW (LBXRDW), WBC (LBXWBCSI) — from CBC
- Chronological age — from the Demographics file (RIDAGEYR)

**CRITICAL — Age Top-Coding (added 2026-07-19, following user's detailed technical review):** NHANES top-codes RIDAGEYR at 80 in the D-009 target cycles (2015-2016, 2017-2018) — every participant genuinely aged 80 or older is recorded simply as "80." D-001's coefficients were trained on NHANES III, which top-coded age at 90, not 80. Since chronological age enters the formula directly (coefficient 0.0804), this top-coding artificially compresses xb for the entire 80+ subgroup. Independent simulation confirms this produces an approximately 6-9 year *understatement* of Phenotypic Age for genuinely 87-90-year-old participants recorded as 80 — the largest-magnitude distortion identified in this project to date, exceeding both EG-004 and EG-010. See **EG-014 (Core, Critical)** in Evidence_Gap_Register.md. Do not treat RIDAGEYR == 80 as a normal data point without the flagging described there — this step must construct a dedicated indicator variable (e.g., `age_topcoded`) for all RIDAGEYR == 80 records before proceeding to Step F.

**Note:** LBXGLU is drawn from the dedicated fasting subsample (participants must meet the NHANES fasting-time criterion). This subsample is smaller than the full BIOPRO sample and requires its own NHANES fasting sample weights — a design constraint for the final analytic sample size and for correct variance estimation.

**Pooled Weight Construction — SIMPLIFIED 2026-07-19 (D-009 dropped the pre-pandemic cycle):** With AgeLens V1 now scoped to only 2015-2016 and 2017-2018 (per D-009) — two standard, equal-duration 2-year continuous NHANES cycles — the fractional/unequal-duration pooling complexity previously documented here (combining a 2-year and a 3.2-year cycle) no longer applies. Standard NHANES guidance for combining two adjacent 2-year cycles applies: construct the pooled fasting-subsample weight as `WTSAF4YR = WTSAF2YR / 2` (i.e., each cycle's fasting weight divided by the number of cycles combined), consistent with NCHS's standard multi-cycle combination convention. This is a simpler, well-established procedure — no custom fractional ratios are needed.

---

## 7. Step C — Unit Standardization

**PIPELINE ORDER CORRECTED 2026-07-19 (following user's detailed technical review):** This step **must execute after** Step D (Cross-Cycle Bridging, Section 8), not before, and the pipeline overview in Section 4 has been corrected accordingly. Rationale: NCHS's bridging equations are derived on NHANES's native reporting units (e.g., CRP in mg/L). Applying D-007's unit conversion (e.g., CRP ÷10 to mg/dL) before bridging would apply the bridging equation's additive intercept in the wrong scale, producing a materially different (and wrong) result. Worked example: a raw CRP of 1.0 mg/L, bridged-then-converted, yields ≈0.1165 mg/dL; converted-then-bridged (the error this document previously specified) yields ≈0.3824 mg/dL — over 3x too high, entirely due to sequencing.

**RESOLVED (2026-07-16):** Direct verification against Levine et al. (2018), *Aging*, Table 1 **and** its Supplement 1 (Supplementary Table S1 — user-provided, independently confirms the main text) shows the formula's biomarker weights were fit on SI/metric units, not US conventional clinical units. NHANES's default LBX-prefixed variables report in US conventional units and require conversion. See **D-007** (closing EG-009).

| Biomarker | Formula-Expected Unit (Supplementary Table S1) | NHANES LBX Source Unit | Conversion Needed? | Conversion Factor |
| --------- | ---------------------- | ---------------------- | -------------------- | -------------------- |
| Albumin | g/L | g/dL (LBXSAL) | **Yes** | × 10 |
| Creatinine | µmol/L | mg/dL (LBXSCR) | **Yes** | × 88.4 |
| Glucose | mmol/L | mg/dL (LBXGLU) | **Yes** | × 0.0555 |
| CRP (log-transformed) | **mg/dL** — confirmed twice (main text Table 1 and Supplementary Table S1), not a transcription artifact | mg/L (LBXHSCRP) | **Yes** | ÷ 10 |
| Lymphocyte % | % | % (LBXLYPCT) | No | — |
| MCV | fL | fL (LBXMCVSI) | No | — |
| RDW | % | % (LBXRDW) | No | — |
| ALP | U/L | U/L (LBXSAPSI) | No | — |
| WBC | 1000 cells/µL | 1000 cells/µL (LBXWBCSI) | No | — |

**Note on CRP:** The mg/dL convention for CRP is unusual relative to modern hs-CRP reporting (typically mg/L), but is now confirmed as the paper's deliberate, consistent choice rather than an error — it appears identically in both the main text and the independently-typeset Supplementary Table S1. Apply the ÷10 conversion (LBXHSCRP in mg/L → mg/dL) before the log transform.

**Note on formula constants — CORRECTED 2026-07-17 (previously mischaracterized as a rounding difference):** Supplementary Table S1 gives the PhenotypicAge conversion as `141.50225 + ln(-0.00553 × ln(1 - MortalityScore)) / 0.090165`. The official PLOS Medicine erratum (Liu et al., 2019, the direct correction notice, independently re-verified against PMC6388911) states the denominator as **0.09165** — one fewer digit, not a rounding variant. This is **not a negligible difference**: holding all else constant, a mortality score of 0.01 yields a Phenotypic Age of approximately 34.6 years using 0.09165, versus approximately 32.8 years using 0.090165 — a systematic ~1.8-year discrepancy across every computed score, depending entirely on which of the two values is used. Independent practitioner discussions (e.g., public forum threads maintained by researchers who built their own PhenoAge calculators) confirm this exact discrepancy has been separately noticed and remains disputed outside AgeLens. See **EG-010 (Core, Critical)** in Evidence_Gap_Register.md. D-001 retains **0.09165** (the value from the formally published, peer-reviewed erratum) as the working default, on the grounds that a journal-issued correction notice is the more authoritative source for the exact equation it was issued to fix — but this is a provisional choice pending empirical resolution via Validation_Protocol.md Check 2 (comparison against BioAge package output), which can adjudicate between the two values using real computed data rather than source-authority alone.

---

## 8. Step D — Cross-Cycle Bridging (D-003, D-004)

**RESOLVED 2026-07-19:** The user supplied the exact official CDC/NCHS documentation URLs (BIOPRO_J.htm, HSCRP_J.htm), which Claude fetched and used to directly verify every equation below against the primary source. All previously-unverified coefficients are confirmed correct, word-for-word matching the official NCHS "Analytic Notes" sections. See **D-008** in Decision_Log.md, closing **EG-013**.

**Confirmed equations (source: wwwn.cdc.gov, BIOPRO_J.htm and HSCRP_J.htm, "Analytic Notes" sections, fetched and verified 2026-07-19):**

- **hs-CRP (LBXHSCRP), unit mg/L, apply BEFORE the D-007 ÷10 conversion:**
  `Y (Cobas 6000) = 0.8695 × X (DxC 660i) + 0.2954`
  Method: Weighted Deming regression. **Valid range: DxC 660i values ≤ 23 mg/L (Cobas 6000 ≤ 20 mg/L).** For values above this range, NCHS explicitly states there is insufficient statistical power (n=7) to recommend an adjustment — use unadjusted values with caution for these participants, and flag them in the Validation Report. n=207 bridging samples, r=0.997. On average, 2017-2018 (Cobas) values run ~19.6% lower than 2015-2016 (DxC 660i) values in the adjustable range.

  **CRITICAL — Step-Discontinuity Warning (added 2026-07-19, following user's detailed technical review):** Implementing this boundary as a literal `IF raw ≤ 23 THEN bridge ELSE leave unadjusted` rule creates an artificial discontinuity: a participant at exactly 23.0 mg/L bridges to ≈20.29 mg/L, while a participant at 23.1 mg/L (0.1 mg/L higher, raw) remains unadjusted at 23.1 — an artificial ~2.8 mg/L jump driven entirely by which side of the threshold a participant falls on, not by any real physiological difference. Do not implement the boundary this way. Instead: (a) flag 2015-2016 participants with raw hs-CRP > 23 mg/L (and 2017+ participants with raw hs-CRP > 20 mg/L) as "unadjusted, above validated bridging range" in a dedicated indicator variable, and either exclude them from cross-cycle comparative analyses (Validation Protocol Check 3) or report them separately — do not silently blend adjusted and unadjusted values into a single continuous variable presented as harmonized. This affects a small subset (NCHS's own n=7 in the bridging sample suggests this is a low-single-digit percentage of participants), but the artificial discontinuity it would otherwise create is a real data-quality risk.
- **Albumin (LBXSAL), unit g/dL:**
  `X (Cobas 6000) = 0.9581 × Y (DxC 660i) − 0.0108`
  Method: Non-weighted Deming regression. n=248 bridging samples, r=0.968.
- **Creatinine (LBXSCR), unit mg/dL:**
  `X (Cobas 6000) = 0.9515 × Y (DxC 660i) + 0.06608`
  Method: Non-weighted Deming regression. n=248 bridging samples, r=0.993.
- **Alkaline Phosphatase (LBXSAPSI), unit U/L, Log-Deming regression:**
  `log10[X (Cobas 6000)] = 0.9986 × log10[Y (DxC 660i)] + 0.04288`, i.e. `X (Cobas 6000) = 10^(0.9986 × log10(Y) + 0.04288)`
  n=248 bridging samples, r≈1.
- Glucose, lymphocyte %, MCV, RDW, WBC: no equation needed — no cross-cycle instrument change within D-009 scope (Sections 5–6 of NHANES_Harmonization_Report.md).

Before the equations can be applied:

Before combining or comparing biomarker values across cycles:

1. **CRP (D-003, direction per D-005):** Apply NCHS's published hs-CRP bridging regression equations to adjust 2015–2016 CRP values (Beckman Coulter DxC 600/660i) onto the 2017+ scale (Roche Cobas 6000/8000, University of Minnesota ARDL). 2017+ values require no adjustment.
2. **Albumin, Creatinine, ALP (D-004, direction per D-005):** Apply the analogous NCHS BIOPRO bridging equations, same direction — adjust 2015–2016 values onto the 2017+ scale. 2017+ values require no adjustment.
3. **Glucose, Lymphocyte %, MCV, RDW, WBC:** No bridging needed (Section 5, 6, 7 of NHANES_Harmonization_Report.md) — apply as-is across all three cycles.

---

## 9. Step E — Missing Data Handling

Per Protocol Section 10.6 (Missing Biomarkers) — not applicable in the current form, since D-009 already excludes the only NHANES window (2011–2014) where a required biomarker (CRP) was categorically unavailable. Within the D-009 target cycles, individual-level missingness is handled per **D-006**: a participant's record is excluded from Phenotypic Age computation if any of the 9 required biomarkers is missing for that participant (complete-case exclusion), consistent with the original Levine et al. (2018) approach.

---

## 10. Step F — Formula Application (D-001)

**Canonical constant pair (D-010):** Use `141.50225 / 0.090165`. Retain the Erratum pair only as sensitivity; hybrid pairs are prohibited.

Apply the exact formula specified in Section 6 of Paper_001_Levine2018.md / D-001:

```
xb = -19.907 - 0.0336(Albumin) + 0.0095(Creatinine) + 0.1953(Glucose)
     + 0.0954·ln(CRP) - 0.0120(Lymphocyte%) + 0.0268(MCV)
     + 0.3306(RDW) + 0.00188(ALP) + 0.0554(WBC) + 0.0804(ChronologicalAge)

M = 1 - exp( -1.51714 · exp(xb) / 0.0076927 )

PhenotypicAge = 141.50225 + ln( -0.00553 · ln(1 - M) ) / 0.090165
```

Apply per-participant, using bridged/standardized values from Steps C–E.

---

## 11. Step G — Output Validation Checks

Before accepting pipeline output as valid, per RQS (Protocol Section 7):

1. **Range check:** Phenotypic Age should correlate strongly and approximately linearly with chronological age across the sample (a basic face-validity check used in the original Levine et al. validation).
2. **Cross-implementation check:** Compare a subsample of AgeLens-computed values against BioAge package output (`orig = TRUE` or the bundled `phenoage0` field) for the same NHANES records, per EG-002's residual concern.
3. **Cross-cycle consistency check:** Compare score distributions before and after Step D bridging is applied, to confirm the bridging equations produce the expected effect (removal of the 2015–2016 vs. 2017+ discontinuity).

These checks constitute the core of Validation_Protocol.md (see that document for full methodology and acceptance criteria); their results become the Validation Report once run.

---

## 12. Governance Status

Validation Checks 1–4 are complete. D-010 through D-014 were approved on 2026-07-22. EG-002, EG-004, EG-010, and EG-014 are closed; no Core Evidence Gap remains open for the governed V1 replication path.

Mandatory rules:

- D-010: Supplement pair is canonical; Erratum pair is sensitivity.
- D-011: retain and flag age-topcoded records; report full/no-topcode results.
- D-012: observed modern creatinine is canonical; +0.11/+0.17/+0.23 mg/dL shifts are mandatory sensitivities.
- D-014: normalize only the exact XPT IBM-zero sentinel and audit replacements.

Final release is still blocked until canonical Supplement-primary outputs are regenerated and regression-tested.

## 13. Next Steps

1. Run `08_canonical_output_rebuild.ipynb`.
2. Preserve all named sensitivities.
3. Verify D-013 regression checks.
4. Enable final V1 outputs only after the canonical rebuild gate passes.

<!-- AGELENS GOVERNANCE RESOLUTION 2026-07-22 -->
