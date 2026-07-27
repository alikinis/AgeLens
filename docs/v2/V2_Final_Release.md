# AgeLens V2.0.0 Final Public Release

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-FR-001 |
| Document version | 1.0 |
| Release | `v2.0.0` |
| Date | 2026-07-27 |
| Status | Final public release authorized |
| Source branch | `v2-development` |
| Pre-release source commit | `b8216019fee4aea339ba1eae8fdd3e17e530fbd9` |
| Relationship to V1 | V1 remains frozen and separate on `main` |

## Project-owner Decision

The project owner authorizes the final public AgeLens V2 release,
annotated Git tag `v2.0.0`, and a public GitHub Release based on that
tag.

No new analysis, model, feature, interaction, subgroup, tuning exercise,
or participant-level public output was introduced during final review.

## Scientific Decision

Model C remains the preferred prediction model.

Model D did not demonstrate incremental predictive improvement beyond
Model C. It is retained only as a negative incremental result and a
restricted descriptive global-shape sensitivity.

The release retains:

- the nonlinear Stage 2 association;
- restricted Stage 3 transportability;
- modest bidirectional cross-cycle prediction within NHANES;
- all null and negative findings;
- observational and internal-NHANES limitations;
- absence of independent external-cohort validation;
- absence of clinical-utility evaluation.

Race/ethnicity is treated strictly as a social classification.

## Public-release Scope

The release includes public-safe source code, governed configurations,
aggregate results, validation scripts, documentation, figures, and
working ARISE materials.

Raw NHANES files and participant-level analytic data remain outside the
public repository.

V1 formulas, cohorts, harmonization, mortality analyses, and released
V1 results remain unchanged.

## Restrictions Retained

This release does not authorize or support:

- final ARISE form submission;
- final manuscript claims;
- merge to `main`;
- causal interpretation;
- clinical thresholds or treatment rules;
- individual-risk prediction;
- participant-level explanations;
- biological interpretation or ranking of race/ethnicity groups;
- independent external-cohort validation claims;
- claims that Model D outperformed Model C;
- new model, feature, interaction, subgroup, or tuning work.
