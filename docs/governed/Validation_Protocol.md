# Validation Protocol

## Document Control

| Field             | Value                          |
| ------------------ | ------------------------------ |
| Document Title    | AgeLens Validation Protocol    |
| Project             | AgeLens                        |
| Document ID         | AL-METH-002                    |
| Version              | 1.2|
| Status               | Approved — V1 checks completed                          |
| Author               | Project Team                   |
| Reviewer             | —                               |
| Last Updated          | 2026-07-22                     |
| Related Documents  | Research Protocol (AL-RP-001), Replication_Protocol.md, Decision_Log.md, Evidence_Gap_Register.md, Paper_003_LiuEtAl2018.md, NHANES_Harmonization_Report.md |

---

## Revision History

| Version | Date       | Summary of Changes                                      |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1     | 2026-07-16 | Initial draft — formalizes the four checks specified in Replication_Protocol.md Section 11, with methodology and acceptance criteria |
| 0.2     | 2026-07-16 | Added external AUC=0.88 benchmark (Liu et al. 2018/2019, per Paper_003_LiuEtAl2018.md) to Check 2 as a complementary discrimination-based cross-check alongside the correlation-based Check 1 |
| 0.3     | 2026-07-16 | Added Open Item #4: fasting sample weight handling for LBXGLU, which Replication_Protocol.md had incorrectly claimed was already addressed here |
| 0.4     | 2026-07-16 | Sentence-by-sentence review: Section 9 said "both Paper Reviews" (stale — now 4 exist) and described Governance Review as a future gate (stale — conducted extensively across multiple rounds). Corrected to reflect current state: no Core blockers remain, next step is Implementation |
| 0.5     | 2026-07-17 | Fixed missing NHANES_Harmonization_Report.md reference in Related Documents — Check 3 directly tests its bridging equations, per user's detailed technical review |
| 0.6     | 2026-07-17 | CRITICAL: added complex survey design (svy weights/clusters/strata) requirement to all statistical tests, previously entirely absent; clarified fasting-glucose subsample is structurally missing-by-design, not MCAR, in Check 4 |
| 0.7     | 2026-07-19 | Removed stale Open Item #4 (fasting weights), which had already been fully resolved in Check 4's body text - a direct self-contradiction pointed out by the user. |
| 0.8     | 2026-07-19 | Updated Check 4's practical implication note with the confirmed pooled weight formula (WTSAF2YR x2/5.2 + WTSAFPRP x3.2/5.2), replacing the earlier generic 'use fasting weights' note. |
| 0.9     | 2026-07-19 | CRITICAL SELF-CONSISTENCY FIX: Section 9 falsely claimed no open Core Evidence Gap blocks Implementation, contradicting EG-004/EG-010. Corrected per Research Protocol Section 6.6 - identified by user's detailed cross-document consistency review. |
| 1.0     | 2026-07-19 | MAJOR: D-009 narrowed scope to 2015-2016 + 2017-2018 only. Removed all 2017-March 2020 references; simplified pooled weight to standard WTSAF2YR/2 (2-cycle combination), replacing the fractional WTSAFPRP approach. |
| 1.1     | 2026-07-19 | CRITICAL: EG-014 (age top-coding) added to Check 1 (dual correlation computation with/without top-coded participants) and Section 9 (three Core blockers now listed: EG-004, EG-010, EG-014). |
| 1.2 | 2026-07-22 | Checks 1–4 completed; D-013 approved Check 1 tolerance and Check 2 baseline; Core gaps dispositioned. |

*This file is a single authoritative document per DP-1 (Protocol Section 8.2) — never duplicated under a new filename. Update in place and bump the version above.*

---

## 1. Purpose

This document specifies how AgeLens Version 1's implementation output will be verified against Replication_Protocol.md's specification, per Protocol Section 7.6 (Release Readiness: "Validation completed" is a mandatory gate). It defines four checks, their methodology, and the criteria for passing each — before any of these checks are run, this is a specification; the results become the (not yet written) Validation Report.

---

## 2. Scope

Covers verification of the Version 1 pipeline (Replication_Protocol.md Steps A–G) against: (a) internal face validity, (b) an independent third-party implementation, (c) the cross-cycle bridging decisions (D-003 through D-005), and (d) the missing-data policy (D-006).

Out of scope: mortality/morbidity outcome validation (the kind of external clinical validation Levine et al. performed) — AgeLens V1 is a replication project, not a new validation study; this is noted as a possible Version 2+ direction, not a V1 requirement.

---

## 3. Check 1 — Face Validity (Age Correlation)

**Method:** Compute the Pearson correlation between AgeLens-derived Phenotypic Age and chronological age (RIDAGEYR) within each D-009 target cycle, separately and pooled.

**Important framing note:** Phenotypic Age is *expected* to correlate strongly with chronological age partly because chronological age is itself one of the 10 formula inputs (Section 6 of Paper_001_Levine2018.md). A high correlation is a necessary sanity check, not evidence of correctness on its own — a coding error could still produce a plausible-looking correlation. This check catches gross implementation errors (e.g., a sign error, a misapplied unit) but does not substitute for Check 2.

**CRITICAL — Age Top-Coding Distortion (added 2026-07-19, following user's detailed technical review):** RIDAGEYR is top-coded at 80 in both D-009 target cycles (see EG-014, Evidence_Gap_Register.md). Including RIDAGEYR == 80 participants in this correlation calculation creates a "vertical wall" artifact — a cluster of participants all recorded at chronological age 80 but with widely varying true Phenotypic Age (since their real ages span from 80 into the 90s+) — which distorts and understates the linear correlation coefficient in a way unrelated to implementation correctness. **Compute this check's correlation twice: once on the full sample, once excluding RIDAGEYR == 80 (using the `age_topcoded` indicator constructed in Replication_Protocol.md Step B).** A materially different result between the two strongly suggests the top-coding artifact — not an implementation error — explains any unexpectedly low correlation, and this must not be misdiagnosed as a coding bug.

**Acceptance criterion:** Rather than an absolute threshold (which risks false precision not grounded in a verified source), this check compares AgeLens's correlation coefficient against the corresponding value obtained by running BioAge (`orig = TRUE`) on the identical extracted sample. **Pass condition:** the two correlation coefficients agree within a pre-registered small tolerance (D-013 approved: |Δr| < 0.02), since no independently verified published r-value for the corrected-formula/D-009-cycle combination was located during this review.

---

## 4. Check 2 — Cross-Implementation Agreement (vs. BioAge)

**Method:** On a representative subsample of each D-009 target cycle, compute Phenotypic Age via (a) the AgeLens pipeline and (b) the BioAge R package, using both its `orig = TRUE` mode and its bundled `phenoage0` reference values (per Paper_002_BioAge.md Section 6). Compare AgeLens output to both BioAge outputs.

**Metrics:**
- Mean absolute difference (years) between AgeLens and each BioAge output.
- Bland-Altman plot (difference vs. mean) to check for systematic bias across the age range, rather than relying on a single summary statistic.
- Pearson/Spearman correlation between AgeLens and each BioAge output.

**Acceptance criterion:** Mean absolute difference should be small relative to the biological signal of interest. A precise numeric threshold is deferred — recommend setting it once Check 2 is first run on real data (the first run establishes a baseline; deviations from that baseline in later runs, e.g. after a code change, are what should trigger investigation). This directly addresses **EG-002** (residual BioAge source-code confirmation gap) — if AgeLens and BioAge (`orig=TRUE`) agree closely, this is strong indirect confirmation that D-001's adopted coefficients match BioAge's implementation, even without line-by-line source inspection.

**External benchmark available:** Liu et al. (2018/2019), reviewed in Paper_003_LiuEtAl2018.md, reports Phenotypic Age achieving AUC = 0.88 for all-cause mortality discrimination in NHANES IV (vs. 0.86 for chronological age alone). If AgeLens's own mortality-discrimination AUC (computable once linked mortality data is available for the D-009 cycles) falls far outside this range, that is a stronger signal of an implementation error than the correlation-based Check 1 alone — AUC is a different, complementary metric from Pearson r and is less sensitive to the chronological-age-is-a-formula-input circularity noted in Check 1.

---

## 5. Check 3 — Cross-Cycle Bridging Effectiveness

**Method:** Compare the distribution of PhenoAgeAccel (age-adjusted Phenotypic Age residual) between the 2015–2016 cycle and the 2017–2018 cycle, both **before** and **after** applying the D-003/D-004/D-005 bridging equations.

**CRITICAL — Complex Survey Design Requirement (added 2026-07-17, following user's detailed technical review):** NHANES is not a simple random sample — it uses a stratified, multistage, clustered probability design with unequal selection probabilities, requiring analysis-appropriate sample weights, primary sampling unit (PSU/cluster: SDMVPSU), and stratum (SDMVSTRA) variables. A standard, unweighted two-sample t-test or Mann-Whitney U test **must not** be used directly on NHANES data — doing so ignores the design effect, typically produces artificially narrow standard errors, and can yield falsely significant p-values. All comparisons in this Check must use design-based (a.k.a. "svy" or complex-survey) methods — e.g., R's `survey` package (`svyglm`, `svyttest`) or Python's `statsmodels` with an appropriately specified `SurveyDesign` — with the correct combined-cycle weight construction per NHANES analytic guidelines (weights generally must be adjusted, e.g. divided by the number of cycles combined, when pooling multiple continuous NHANES cycles). This requirement applies to every statistical test in this Validation Protocol, not Check 3 alone — Check 1's correlation and Check 4's cross-tabulation must also use design-based methods.

**Metrics:**
- Design-based two-sample comparison (e.g., `svyttest` or a design-adjusted equivalent of Mann-Whitney U) comparing mean PhenoAgeAccel across the 2015-2016 vs. 2017+ grouping, using correctly constructed combined-cycle weights.
- Effect size (Cohen's d, computed from design-adjusted estimates) alongside the significance test, since NHANES's large sample size can make even small, practically unimportant differences statistically significant.

**Acceptance criterion:** The pre-bridging comparison is expected to show a detectable cycle effect (confirming the bridging equations are addressing a real discontinuity, not a phantom one). The post-bridging comparison should show a materially smaller effect size than pre-bridging. A residual small effect is acceptable and should be documented as a known limitation rather than treated as a failed check, since bridging equations reduce but do not necessarily eliminate all cross-instrument variation.

---

## 6. Check 4 — Missingness Pattern Check

**CRITICAL — Fasting Glucose Subsample is Not MCAR (added 2026-07-17, following user's detailed technical review):** Fasting glucose (LBXGLU) is deliberately collected from only the NHANES fasting morning subsample (roughly half of MEC-examined participants, by survey design — assignment to a fasting session is randomized by NHANES's own design, but the resulting missingness for non-assigned participants is **missing by design**, not missing completely at random in the general sense this Check tests for the *other* 8 biomarkers). Applying D-006's complete-case exclusion rule naively — treating glucose's structural, by-design absence in the non-fasting-subsample half of participants identically to incidental missingness on the other 8 biomarkers — is methodologically correct in outcome (the Phenotypic Age formula requires fasting glucose, so only the fasting subsample can ever be scored, by definition) but must not be conflated with genuine random missingness when interpreting this Check's MCAR test. The fasting-subsample-only structure should be treated as a known, deterministic feature of the analytic sample definition, not a finding requiring imputation or a D-006 policy revision. **Practical implication:** the effective D-009 analytic sample is bounded by the fasting subsample from the outset; the correct pooled NHANES fasting-subsample weight — `WTSAF2YR / 2` (standard equal-duration 2-cycle combination, per D-009 dropping the pre-pandemic cycle; see Replication_Protocol.md Section 6) — must be used for every statistical test in this Validation Protocol, not the standard interview/exam weights.

**Method:** For the *remaining 8 biomarkers* (excluding glucose, whose structural missingness is addressed above), assess whether missingness is consistent with Missing Completely At Random (MCAR) within each D-009 target cycle, among fasting-subsample participants.

**Metrics:**
- Cross-tabulation of missingness by biomarker and by basic demographic strata (age group, sex) available in the Demographics file.
- Little's MCAR test, if software support is available in the eventual implementation environment; otherwise, the cross-tabulation approach alone, documented as a partial check.

**Acceptance criterion:** If missingness appears systematically related to demographic strata (e.g., disproportionately affecting a specific age group), this should be documented as a limitation in the eventual Validation Report and may warrant revisiting **D-006** (complete-case exclusion) in a future Decision — e.g., considering multiple imputation for the affected biomarker. This check does not block Version 1 release on its own; per Protocol Section 6.6, it is logged as an Evidence Gap only if the finding materially affects methodological validity (Core) rather than being a documented limitation (non-blocking).

---

## 7. Reporting

All four checks were executed and documented in `docs/methodology/Validation_Report_Draft.md`.

- Check 1: PASS.
- Check 2: PASS — baseline established.
- Check 3: PASS.
- Check 4: PASS WITH DOCUMENTED LIMITATION.

## 8. Resolved Open Items

1. D-013 approved Check 1 `|Δr| < 0.02`.
2. D-013 established Check 2: Supplement MAE < 0.10 years and Pearson/Spearman >= 0.999999.
3. BioAge direct source inspection completed; EG-002 closed.
4. EG-004, EG-010, and EG-014 were dispositioned through D-012, D-010, and D-011.

## 9. Next Steps

Regenerate canonical Supplement-primary outputs. Final release remains disabled until that rebuild and its D-013 regression checks pass.

<!-- AGELENS GOVERNANCE RESOLUTION 2026-07-22 -->
