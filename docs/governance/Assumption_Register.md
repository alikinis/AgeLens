# Assumption Register

## Document Control

| Field             | Value                          |
| ------------------ | ------------------------------ |
| Document Title    | AgeLens Assumption Register    |
| Project             | AgeLens                        |
| Document ID         | AL-GOV-002                     |
| Version              | 0.3                             |
| Status               | Draft                          |
| Author               | Project Team                   |
| Reviewer             | —                               |
| Last Updated          | 2026-07-16                     |
| Related Documents  | Research Protocol (AL-RP-001), Decision_Log.md, Evidence_Gap_Register.md, NHANES_Harmonization_Report.md, Paper_002_BioAge.md, Paper_003_LiuEtAl2018.md |

---

## Revision History

| Version | Date       | Summary of Changes                                      |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1     | 2026-07-16 | Initialized empty template (A-001 placeholder)             |
| 0.2     | 2026-07-16 | A-001 populated (formula provenance assumption); Status converted to "Converted to Decision (D-001)" once D-001 was approved |
| 0.3     | 2026-07-16 | Staleness cleanup: "Missing Evidence" field updated to reflect resolution confirmed by Paper_002/Paper_003 (previously described an already-resolved gap as outstanding); Related Documents completed |

*This file is a single authoritative document per DP-1 (Protocol Section 8.2) — never duplicated under a new filename. Update in place and bump the version above.*

---

## Purpose

This register tracks every temporary working hypothesis (Assumption) adopted per Section 6.2 of the Research Protocol, used only when implementation cannot reasonably continue without a provisional choice. Assumptions are inherently temporary and shall never be treated as established evidence.

---

## How to Use This Register

- Add one entry per Assumption, in the order they are adopted.
- Assumption IDs follow the pattern `A-NNN` (e.g., A-001, A-002).
- Every assumption must define the conditions under which it will be re-evaluated (Expected Resolution).
- Status may be `Active`, `Converted to Decision`, or `Reclassified as Evidence Gap`. When status changes, keep the entry and note the resulting Decision ID or Evidence Gap ID rather than deleting the row.

---

## Assumption Entries

### A-001

| Field                | Value |
| --------------------- | ----- |
| Description             | For Version 1 baseline replication, the corrected Phenotypic Age equation published in Liu et al.'s 2019 PLOS Medicine erratum is provisionally treated as the authoritative formula. |
| Justification            | The equation as printed in the original Levine et al. (2018) *Aging* article is missing a step and cannot be resolved as stated. A complete, resolvable version was published in a correction notice for a companion paper by an overlapping author group (including Levine as co-author). |
| Missing Evidence         | **Resolved.** Paper_002_BioAge.md confirmed convergent (Category C) evidence that validated implementations reproduce the corrected coefficients; Paper_003_LiuEtAl2018.md subsequently confirmed the correction is a direct erratum to Liu et al.'s own paper, not an inferred companion-paper relationship. No missing evidence remains for this assumption. |
| Expected Resolution      | Cross-check against BioAge R package source code during the Paper_002_BioAge.md review; check for a direct erratum notice on the *Aging* journal article page. |
| Related Decision          | D-001 |
| Review Date                | Before NHANES Harmonization Report is finalized |
| Status                      | Converted to Decision (D-001), 2026-07-16 |

---

*Add new entries below using the same template, incrementing the Assumption ID.*
