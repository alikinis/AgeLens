# AgeLens V2 Evidence Gap Register

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-EG-001 |
| Version | 0.1 |
| Status | Open |
| Date | 2026-07-23 |

## Status Vocabulary

- **Open:** unresolved and may affect design or implementation.
- **Under Review:** evidence collection is active.
- **Dispositioned:** uncertainty remains but a governed handling rule is approved.
- **Closed:** sufficiently resolved for the authorized V2 scope.

## Register

| ID | Priority | Question | Why it matters | Required evidence or analysis | Status |
| --- | --- | --- | --- | --- | --- |
| V2-EG-001 | Core | Which non-mortality aging-related outcome family will be primary? | Defines the scientific claim and model family. | Official NHANES module documentation, cycle availability, construct validity, event/prevalence feasibility. | Open |
| V2-EG-002 | Core | Which exact variables and coding rules define each candidate outcome? | Prevents post-hoc endpoint construction. | Data dictionaries, codebooks, prior validated definitions. | Open |
| V2-EG-003 | Core | What is the eligible age range and analytic population? | Changes generalizability, sample size, and survey design. | Outcome-specific eligibility documentation and feasibility counts. | Open |
| V2-EG-004 | Core | Which survey weights, strata, and PSUs apply to each outcome? | Incorrect weights invalidate population inference. | Official NHANES analytic guidance and module-specific documentation. | Open |
| V2-EG-005 | Core | How will missing outcome and covariate data be handled? | Missingness can bias associations and prediction comparisons. | Missingness audit, complete-case feasibility, justified sensitivity strategy. | Open |
| V2-EG-006 | Core | What is the primary estimand and adjustment set? | Distinguishes prognostic association from causal interpretation. | Directed scientific rationale and prespecified model formula. | Open |
| V2-EG-007 | Core | How will multiple outcomes, subgroups, and interactions be controlled? | Prevents selective reporting and inflated false-positive risk. | Hierarchical testing or multiplicity plan. | Open |
| V2-EG-008 | Core | Which baseline and comparison models are scientifically justified? | Required to support incremental-utility claims. | Prespecified chronological-age, demographic, and PhenoAge model definitions. | Open |
| V2-EG-009 | Core | Which performance metrics and validation thresholds will be used? | Avoids choosing favorable metrics after seeing results. | Metric definitions for discrimination, calibration, and uncertainty. | Open |
| V2-EG-010 | Core | How will resampling or data splitting respect survey structure and prevent leakage? | Standard random splitting may distort design-based inference. | Primary methodological sources and simulation/feasibility assessment. | Open |
| V2-EG-011 | Important | Which subgroup analyses are sufficiently powered and ethically interpretable? | Sparse estimates can mislead and amplify disparity claims. | Weighted/unweighted support thresholds and reporting rules. | Open |
| V2-EG-012 | Important | Which single explainable extension, if any, is justified? | Controls scope and prevents model shopping. | Clear target, baseline comparison, interpretability rationale. | Open |
| V2-EG-013 | Important | Which Python and R tools will be used and reconciled? | Software choices affect reproducibility and survey methods. | Package documentation and independent reconciliation plan. | Open |
| V2-EG-014 | Core | What exact V2 scope must be frozen for the ARISE submission? | Prevents deadline-driven scope expansion. | Approved minimum release specification and cutoff date. | Open |

## Current Blocking Rule

No final outcome model may be fit until V2-EG-001 through V2-EG-010 and V2-EG-014 are closed or explicitly dispositioned.
