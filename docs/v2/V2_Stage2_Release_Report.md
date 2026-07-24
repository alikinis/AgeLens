# AgeLens V2 Stage 2 Release Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S2REL-001 |
| Version | 1.0 |
| Status | Released for V2 development |
| Date | 2026-07-24 |

## 1. Release Scope

Stage 2 conventional association results are approved for commit to the
`v2-development` branch.

This decision does not authorize:

- merge to `main`;
- a final manuscript claim;
- a final ARISE submission;
- transportability claims;
- cross-cycle prediction claims;
- an explainable or machine-learning extension.

## 2. Primary Result

Among 4,366 governed adults with 682 mobility-disability outcomes, the
prespecified survey-weighted quasi-Poisson model estimated:

- adjusted prevalence ratio per 5-year higher acceleration: **1.1476**;
- 95% confidence interval: **1.0998 to 1.1974**;
- two-sided p-value: **2.51e-07**.

This is an associational, not causal, estimate.

## 3. Nonlinearity and Scientific Interpretation

Both governed spline analyses detected nonlinearity:

- quasi-Poisson spline: p = **0.000177**;
- bounded logistic spline: p = **0.000916**.

Therefore, the primary prevalence ratio is retained as the prespecified
**global linear summary**, not as a constant effect across the full
acceleration range.

The bounded adjusted-prevalence curve indicates:

- a shallow, uncertain low-tail dip;
- a steep rise from lower-to-middle acceleration;
- continued absolute prevalence increase with attenuation of the relative
  five-year ratio at high positive acceleration.

The low-tail dip must not be described as protective.

## 4. Local Five-Year Ratios

At fixed weighted-percentile anchors, the diagnostic spline estimated:

| Anchor | Start acceleration | Local 5-year PR | 95% CI |
| --- | ---: | ---: | ---: |
| 10th percentile | -7.46 years | 1.618 | 1.202–2.177 |
| 25th percentile | -4.47 years | 1.812 | 1.389–2.365 |
| 50th percentile | -1.20 years | 1.582 | 1.371–1.825 |
| 75th percentile | 3.16 years | 1.290 | 1.152–1.443 |
| 90th percentile | 7.81 years | 1.162 | 1.050–1.287 |

These are supportive local contrasts, not replacements for the frozen primary
estimand.

## 5. Modified-Poisson Fitted-Value Diagnostic

Six primary-domain fitted values exceeded one. They represented approximately
0.050% of the weighted primary domain.

The minimum acceleration among these observations was +38.29 years, while the
weighted 99th percentile was +25.76 years. Thus, the bound violations were
restricted to an extreme, minimally weighted tail.

Modified-Poisson fitted values are not interpreted as individual
probabilities. The diagnostic does not invalidate the robust prevalence-ratio
coefficient, but it reinforces the need for the bounded spline figure when
describing shape.

## 6. Secondary Outcomes

All three governed secondary associations were positive and remained
significant after Holm correction:

| Outcome | Adjusted PR | 95% CI | Holm p-value |
| --- | ---: | ---: | ---: |
| Any six-domain disability | 1.1118 | 1.0731–1.1518 | 2.00e-06 |
| Fair or poor general health | 1.1641 | 1.1293–1.2000 | 8.30e-11 |
| PHQ-9 ≥10 | 1.1596 | 1.1019–1.2202 | 2.00e-06 |

These results support consistency across functional, general-health, and
neuropsychiatric domains.

## 7. Approved Scientific Language

> Higher Phenotypic Age acceleration was associated with a higher prevalence
> of serious mobility disability. The prespecified linear model estimated an
> adjusted prevalence ratio of 1.148 per 5-year higher acceleration (95% CI
> 1.100–1.197), while spline analyses showed that the association was
> nonlinear and strongest in the lower-to-middle acceleration range.

Prohibited interpretations include:

- causal language;
- claiming a constant 14.8% increase everywhere;
- claiming that very low acceleration is protective;
- declaring a clinical threshold.

## 8. V1 Protection and Next Gate

No V1 formula, harmonization rule, participant artifact, mortality model, or
result changed.

Stage 3 transportability and cross-cycle validation implementation is
authorized. Claims from those analyses remain blocked until their own
validation and release gates pass. Explainable modeling remains unauthorized.
