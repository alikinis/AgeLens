# AgeLens V2 Stage 2 Diagnostic Review

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S2R-001 |
| Version | 1.0 |
| Status | Complete — review passed and release decision recorded |
| Date | 2026-07-24 |

## 1. Trigger

The first Stage 2 run produced a strong and internally consistent primary
association, but also identified two diagnostics that prevent immediate
release:

- a design-based nonlinearity test p-value of 0.00017697;
- modified-Poisson fitted values above one, including six primary-domain
  observations and a primary fitted maximum of 11.93.

The prespecified linear prevalence ratio is retained and remains provisional.
It is not discarded, silently replaced, or released as a uniform effect over
the entire acceleration range.

## 2. Authorized Review

The review is limited to:

1. aggregate reconciliation of fitted values above one;
2. weighted exposure quantiles;
3. central 98% and 95% linear-model sensitivities;
4. a bounded survey-weighted logistic restricted-cubic-spline curve;
5. local five-year prevalence ratios at fixed weighted-percentile anchors.

## 3. Interpretation Guardrail

The quasi-Poisson linear coefficient remains the prespecified global summary.
The bounded logistic-spline curve is a diagnostic visualization of shape and
must not be described as a newly selected primary model.

No causal interpretation, clinical threshold, subgroup claim, predictive
claim, or explainable-AI claim is authorized.

## 4. V1 Protection

The review reads the private V2 Stage 2 model input and writes aggregate V2
tables and one aggregate figure only. It changes no V1 formula, participant
file, mortality analysis, result, or public `main` branch artifact.

## 5. Release Rule

Stage 2 remains unreleased until:

- fitted-value behavior is quantified;
- trimmed sensitivities are reviewed;
- the bounded curve and local ratios are inspected;
- all review validation checks pass;
- a separate human release decision is recorded.


## 6. Review Outcome

The review passed all governed checks.

The prespecified global linear prevalence ratio is retained. Both the
quasi-Poisson and bounded logistic spline models provide strong evidence of
nonlinearity. The bounded curve is accepted as the primary shape
visualization.

The fitted-value bound issue is restricted to six primary observations,
approximately 0.050% weighted, all beyond the weighted 99th percentile of
acceleration.

Stage 2 release for `v2-development` is approved in
`V2_Stage2_Release_Report.md`.
