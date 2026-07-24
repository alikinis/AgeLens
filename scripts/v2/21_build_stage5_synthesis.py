"""Build the governed AgeLens V2 Stage 5 aggregate synthesis package."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

BUILD = "AgeLens-V2-Stage5-20260724b"
TOLERANCE = 1e-10
STAGE5_MARKER_BEGIN = "<!-- AGELENS_STAGE5_BEGIN -->"
STAGE5_MARKER_END = "<!-- AGELENS_STAGE5_END -->"


class Stage5Error(RuntimeError):
    """Raised when governed Stage 5 inputs are missing or inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def close(actual: Any, expected: Any, tolerance: float = TOLERANCE) -> bool:
    try:
        a = float(actual)
        e = float(expected)
    except (TypeError, ValueError):
        return False
    return math.isfinite(a) and math.isfinite(e) and abs(a - e) <= tolerance


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def row_map(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    mapped = {row[key]: row for row in rows}
    if len(mapped) != len(rows):
        raise Stage5Error(f"Duplicate values in key column {key!r}.")
    return mapped


def require_files(root: Path, relative_paths: list[str]) -> list[Path]:
    paths = [root / item for item in relative_paths]
    missing = [path.relative_to(root).as_posix() for path in paths if not path.is_file()]
    if missing:
        raise Stage5Error("Missing governed Stage 5 source files: " + ", ".join(missing))
    return paths


def run_prior_validator(root: Path, relative_script: str) -> None:
    command = [sys.executable, str(root / relative_script), "--project-root", str(root)]
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
    if completed.returncode != 0:
        message = (completed.stdout + "\n" + completed.stderr).strip()
        raise Stage5Error(f"Prior release validator failed: {relative_script}\n{message}")
    if completed.stdout.strip():
        print(completed.stdout.strip())


def reconcile_sources(root: Path) -> dict[str, Any]:
    source_relpaths = [
        "config/v2_stage2_release.json",
        "config/v2_stage3_release.json",
        "config/v2_stage4_release.json",
        "results/tables/v2/11_stage2_release_summary.csv",
        "results/tables/v2/09_stage2_nonlinearity_review.csv",
        "results/tables/v2/15_stage3_release_summary.csv",
        "results/tables/v2/13_stage3_transportability_global_tests.csv",
        "results/tables/v2/13_stage3_prediction_bootstrap_summary.csv",
        "results/tables/v2/20_stage4_release_summary.csv",
        "results/tables/v2/18_stage4_bootstrap_summary.csv",
        "results/tables/v2/18_stage4_shape_stability.csv",
        "docs/v2/V2_Stage2_Release_Report.md",
        "docs/v2/V2_Stage3_Release_Report.md",
        "docs/v2/V2_Stage4_Release_Report.md",
    ]
    source_paths = require_files(root, source_relpaths)

    stage2 = read_json(root / "config/v2_stage2_release.json")
    stage3 = read_json(root / "config/v2_stage3_release.json")
    stage4 = read_json(root / "config/v2_stage4_release.json")
    for label, config in (("Stage 2", stage2), ("Stage 3", stage3), ("Stage 4", stage4)):
        if config.get("status") != "released_for_v2_development":
            raise Stage5Error(f"{label} is not released for V2 development.")
        if config.get("relationship_to_v1", config.get("v1_protection", {})).get("v1_immutable") is not True:
            raise Stage5Error(f"{label} no longer protects V1 immutability.")

    if not stage4["permissions"]["stage5_synthesis_and_arise_authorized"]:
        raise Stage5Error("Stage 5 synthesis authorization is missing.")
    restricted_permissions = [
        "stage4_positive_extension_claim_authorized",
        "model_d_primary_prediction_role_authorized",
        "local_explanation_release_authorized",
        "new_model_or_feature_search_authorized",
        "merge_to_main_authorized",
        "final_manuscript_claims_authorized",
    ]
    enabled = [key for key in restricted_permissions if stage4["permissions"].get(key)]
    if enabled:
        raise Stage5Error("Restricted Stage 4 permissions unexpectedly enabled: " + ", ".join(enabled))

    stage2_rows = read_csv(root / "results/tables/v2/11_stage2_release_summary.csv")
    stage2_primary_rows = [row for row in stage2_rows if row["role"] == "primary"]
    if len(stage2_primary_rows) != 1:
        raise Stage5Error("Stage 2 release summary must contain one primary row.")
    s2_primary = stage2_primary_rows[0]
    s2_cfg = stage2["primary_result"]["prespecified_global_linear_summary"]
    for column, key in (
        ("prevalence_ratio", "prevalence_ratio_per_5_years"),
        ("ci_low_95", "ci_low_95"),
        ("ci_high_95", "ci_high_95"),
        ("p_value", "p_value"),
    ):
        if not close(s2_primary[column], s2_cfg[key]):
            raise Stage5Error(f"Stage 2 primary value conflicts: {column}.")
    if int(s2_primary["n"]) != int(stage2["primary_result"]["n"]):
        raise Stage5Error("Stage 2 primary n conflicts.")
    if int(s2_primary["positive_n"]) != int(stage2["primary_result"]["positive_n"]):
        raise Stage5Error("Stage 2 primary positive count conflicts.")

    s2_nonlinearity_rows = read_csv(root / "results/tables/v2/09_stage2_nonlinearity_review.csv")
    if len(s2_nonlinearity_rows) != 1:
        raise Stage5Error("Stage 2 nonlinearity review row count changed.")
    s2_nonlin = s2_nonlinearity_rows[0]
    if not close(s2_nonlin["prespecified_quasipoisson_nonlinearity_p"], stage2["nonlinearity"]["prespecified_quasipoisson_p"]):
        raise Stage5Error("Stage 2 quasi-Poisson nonlinearity value conflicts.")
    if not close(s2_nonlin["logistic_spline_nonlinearity_p"], stage2["nonlinearity"]["bounded_logistic_spline_p"]):
        raise Stage5Error("Stage 2 logistic-spline nonlinearity value conflicts.")
    if parse_bool(s2_nonlin["linear_primary_result_released"]):
        raise Stage5Error("Stage 2 source unexpectedly releases the linear result without restriction.")

    stage2_secondary = {row["outcome"]: row for row in stage2_rows if row["role"] == "secondary"}
    expected_secondary = {item["outcome"]: item for item in stage2["secondary_results"]}
    if set(stage2_secondary) != set(expected_secondary):
        raise Stage5Error("Stage 2 secondary outcome set conflicts.")
    for outcome, row in stage2_secondary.items():
        cfg = expected_secondary[outcome]
        for column, key in (
            ("prevalence_ratio", "prevalence_ratio"),
            ("ci_low_95", "ci_low_95"),
            ("ci_high_95", "ci_high_95"),
            ("p_value", "holm_p_value"),
        ):
            if not close(row[column], cfg[key]):
                raise Stage5Error(f"Stage 2 secondary value conflicts: {outcome} {column}.")

    stage3_summary = row_map(read_csv(root / "results/tables/v2/15_stage3_release_summary.csv"), "component")
    s3_pred = stage3["prediction_release"]
    for component, config_key in (
        ("prediction_brier_delta_c_minus_b", "brier_delta_c_minus_b"),
        ("prediction_auc_delta_c_minus_b", "auc_delta_c_minus_b"),
    ):
        row = stage3_summary[component]
        cfg = s3_pred[config_key]
        for column, key in (("estimate", "estimate"), ("ci_low_95", "ci_low_95"), ("ci_high_95", "ci_high_95")):
            if not close(row[column], cfg[key]):
                raise Stage5Error(f"Stage 3 prediction value conflicts: {component} {column}.")
    if not s3_pred["positive_incremental_utility_rule_passed"]:
        raise Stage5Error("Stage 3 Model C incremental-utility decision changed.")

    s3_global = row_map(read_csv(root / "results/tables/v2/13_stage3_transportability_global_tests.csv"), "dimension")
    supported = {name for name, row in s3_global.items() if parse_bool(row["supported_at_q_0_10"])}
    if supported != {"race_ethnicity"}:
        raise Stage5Error("Stage 3 supported transportability family changed.")
    race_row = s3_global["race_ethnicity"]
    tr = stage3["transportability_release"]
    if not close(race_row["p_value_raw"], tr["race_ethnicity_global_p_raw"], 1e-14):
        raise Stage5Error("Stage 3 race/ethnicity interaction p-value conflicts.")
    if not close(race_row["q_value_bh"], tr["race_ethnicity_global_q_bh"], 1e-14):
        raise Stage5Error("Stage 3 race/ethnicity interaction q-value conflicts.")

    stage3_bootstrap = row_map(read_csv(root / "results/tables/v2/13_stage3_prediction_bootstrap_summary.csv"), "metric")
    if int(stage3_bootstrap["brier_delta_c_minus_b"]["replicate_n"]) != 500:
        raise Stage5Error("Stage 3 bootstrap replicate count changed.")
    if int(stage3_bootstrap["brier_delta_c_minus_b"]["failed_replicate_n"]) != 0:
        raise Stage5Error("Stage 3 bootstrap failures changed.")

    stage4_summary = row_map(read_csv(root / "results/tables/v2/20_stage4_release_summary.csv"), "component")
    s4_pred = stage4["incremental_prediction_release"]
    for component, config_key in (
        ("brier_delta_d_minus_c", "brier_delta_d_minus_c"),
        ("auc_delta_d_minus_c", "auc_delta_d_minus_c"),
    ):
        row = stage4_summary[component]
        cfg = s4_pred[config_key]
        for column, key in (("estimate", "estimate"), ("ci_low_95", "ci_low_95"), ("ci_high_95", "ci_high_95")):
            if not close(row[column], cfg[key]):
                raise Stage5Error(f"Stage 4 prediction value conflicts: {component} {column}.")
    if s4_pred["joint_positive_rule_passed"]:
        raise Stage5Error("Stage 4 positive EBM extension decision changed.")
    if s4_pred["preferred_prediction_model"] != "Stage3_Model_C":
        raise Stage5Error("Stage 4 preferred prediction model changed.")

    stage4_bootstrap = row_map(read_csv(root / "results/tables/v2/18_stage4_bootstrap_summary.csv"), "metric")
    if int(stage4_bootstrap["brier_delta_d_minus_c"]["replicate_n"]) != 500:
        raise Stage5Error("Stage 4 bootstrap replicate count changed.")
    if int(stage4_bootstrap["brier_delta_d_minus_c"]["failed_replicate_n"]) != 0:
        raise Stage5Error("Stage 4 bootstrap failures changed.")

    stability_rows = read_csv(root / "results/tables/v2/18_stage4_shape_stability.csv")
    if len(stability_rows) != 1:
        raise Stage5Error("Stage 4 shape-stability row count changed.")
    stability = stability_rows[0]
    ge = stage4["global_explanation_release"]
    if not close(stability["spearman_correlation"], ge["acceleration_shape_spearman"]):
        raise Stage5Error("Stage 4 acceleration-shape stability conflicts.")
    if not parse_bool(stability["stable_shape_supported"]):
        raise Stage5Error("Stage 4 global rank-shape stability is no longer supported.")

    return {
        "source_relpaths": source_relpaths,
        "source_paths": source_paths,
        "stage2": stage2,
        "stage3": stage3,
        "stage4": stage4,
        "stage2_rows": stage2_rows,
        "stage2_primary": s2_primary,
        "stage2_secondary": stage2_secondary,
        "stage2_nonlinearity": s2_nonlin,
        "stage3_summary": stage3_summary,
        "stage3_global": s3_global,
        "stage3_bootstrap": stage3_bootstrap,
        "stage4_summary": stage4_summary,
        "stage4_bootstrap": stage4_bootstrap,
        "stage4_stability": stability,
    }


def make_scientific_summary(data: dict[str, Any]) -> list[dict[str, Any]]:
    s2 = data["stage2_primary"]
    s2n = data["stage2_nonlinearity"]
    s3 = data["stage3_summary"]
    s3g = data["stage3_global"]
    s4 = data["stage4_summary"]
    rows: list[dict[str, Any]] = []

    def add(**kwargs: Any) -> None:
        rows.append(kwargs)

    add(
        research_question="RQ2-1 functional-health validation",
        analysis_stage="Stage 2",
        estimand_or_metric="Adjusted prevalence ratio per 5-year higher acceleration",
        estimate=s2["prevalence_ratio"], uncertainty_low=s2["ci_low_95"], uncertainty_high=s2["ci_high_95"],
        multiplicity_or_decision_rule="Primary prespecified global linear summary",
        governed_conclusion="Positive adjusted association with serious mobility disability, interpreted with strong nonlinearity.",
        authorized_wording="Higher acceleration was associated with higher mobility-disability prevalence; the global linear summary was PR 1.148 (95% CI 1.100–1.197).",
        prohibited_interpretation="Constant effect, causal effect, individual probability, or clinical threshold.",
        source_artifact="config/v2_stage2_release.json::primary_result.prespecified_global_linear_summary; results/tables/v2/11_stage2_release_summary.csv::role=primary",
    )
    add(
        research_question="RQ2-1 shape diagnostic",
        analysis_stage="Stage 2",
        estimand_or_metric="Nonlinearity tests",
        estimate=f"quasi-Poisson p={float(s2n['prespecified_quasipoisson_nonlinearity_p']):.15g}; logistic spline p={float(s2n['logistic_spline_nonlinearity_p']):.15g}",
        uncertainty_low="", uncertainty_high="",
        multiplicity_or_decision_rule="Prespecified spline diagnostic",
        governed_conclusion="Strong evidence that the acceleration association is nonlinear.",
        authorized_wording="The association was nonlinear and strongest in the lower-to-middle acceleration range.",
        prohibited_interpretation="Uniform 5-year effect, protective low-tail claim, or threshold discovery.",
        source_artifact="results/tables/v2/09_stage2_nonlinearity_review.csv::outcome=mobility_disability",
    )
    labels = {
        "any_disability_six": "Any six-domain disability",
        "fair_poor_general_health": "Fair or poor general health",
        "phq9_ge10": "PHQ-9 score ≥10",
    }
    for outcome in sorted(data["stage2_secondary"]):
        row = data["stage2_secondary"][outcome]
        add(
            research_question="RQ2-2 secondary health validation",
            analysis_stage="Stage 2",
            estimand_or_metric=f"Adjusted prevalence ratio: {labels[outcome]}",
            estimate=row["prevalence_ratio"], uncertainty_low=row["ci_low_95"], uncertainty_high=row["ci_high_95"],
            multiplicity_or_decision_rule="Holm-adjusted secondary family",
            governed_conclusion="Supportive positive secondary association.",
            authorized_wording=f"Acceleration was positively associated with {labels[outcome].lower()} after Holm adjustment.",
            prohibited_interpretation="Independent primary confirmation, causal effect, or clinical prediction.",
            source_artifact=f"results/tables/v2/11_stage2_release_summary.csv::role=secondary,outcome={outcome}",
        )
    race = s3g["race_ethnicity"]
    add(
        research_question="RQ2-4 transportability",
        analysis_stage="Stage 3",
        estimand_or_metric="Global race/ethnicity interaction test for frozen linear acceleration summary",
        estimate=race["p_value_raw"], uncertainty_low="", uncertainty_high="",
        multiplicity_or_decision_rule=f"BH q=0.10 across four families; q={float(race['q_value_bh']):.15g}",
        governed_conclusion="Race/ethnicity family supported; sex, age-group, and cycle families unsupported.",
        authorized_wording="Heterogeneity was supported only for the prespecified global race/ethnicity interaction family, with strict social-classification guardrails.",
        prohibited_interpretation="Biological difference, causality, pairwise ranking, or subgroup risk ordering.",
        source_artifact="config/v2_stage3_release.json::transportability_release; results/tables/v2/13_stage3_transportability_global_tests.csv::dimension=race_ethnicity",
    )
    for component, metric_label in (
        ("prediction_brier_delta_c_minus_b", "Brier delta C−B"),
        ("prediction_auc_delta_c_minus_b", "AUC delta C−B"),
    ):
        row = s3[component]
        add(
            research_question="RQ2-3 incremental utility",
            analysis_stage="Stage 3",
            estimand_or_metric=metric_label,
            estimate=row["estimate"], uncertainty_low=row["ci_low_95"], uncertainty_high=row["ci_high_95"],
            multiplicity_or_decision_rule="Frozen bidirectional cross-cycle rule with 500 stratified-PSU bootstrap replicates",
            governed_conclusion="Model C showed modest incremental out-of-cycle prediction within NHANES beyond Model B.",
            authorized_wording="Adding acceleration modestly improved pooled cross-cycle Brier score and AUC within NHANES 2015–2018.",
            prohibited_interpretation="Independent-cohort validation, clinical utility, or individual risk prediction.",
            source_artifact=f"config/v2_stage3_release.json::prediction_release.{component}; results/tables/v2/15_stage3_release_summary.csv::component={component}",
        )
    for component, metric_label in (
        ("brier_delta_d_minus_c", "Brier delta D−C"),
        ("auc_delta_d_minus_c", "AUC delta D−C"),
    ):
        row = s4[component]
        add(
            research_question="RQ2-5 controlled innovation",
            analysis_stage="Stage 4",
            estimand_or_metric=metric_label,
            estimate=row["estimate"], uncertainty_low=row["ci_low_95"], uncertainty_high=row["ci_high_95"],
            multiplicity_or_decision_rule="Frozen joint positive-extension rule with 500 stratified-PSU bootstrap replicates",
            governed_conclusion="The main-effects EBM did not demonstrate incremental predictive improvement beyond Model C.",
            authorized_wording="The EBM did not establish improvement beyond Model C; Model C remained preferred.",
            prohibited_interpretation="EBM superiority, EBM harm, clinical utility, or post-result model search.",
            source_artifact=f"config/v2_stage4_release.json::incremental_prediction_release.{component}; results/tables/v2/20_stage4_release_summary.csv::component={component}",
        )
    stable = data["stage4_stability"]
    add(
        research_question="RQ2-5 explainability sensitivity",
        analysis_stage="Stage 4",
        estimand_or_metric="Cycle-trained acceleration-term Spearman rank correlation",
        estimate=stable["spearman_correlation"], uncertainty_low="", uncertainty_high="",
        multiplicity_or_decision_rule=f"Frozen minimum {stable['minimum_required']} over {stable['common_grid_n']} eligible grid points",
        governed_conclusion="Global acceleration rank-shape stability passed the governed rule.",
        authorized_wording="The cycle-trained acceleration term functions were highly rank-correlated over common support.",
        prohibited_interpretation="Exact curve agreement, prevalence ratio, causal effect, threshold, or local explanation.",
        source_artifact="results/tables/v2/18_stage4_shape_stability.csv::single_row",
    )
    add(
        research_question="Final model-role synthesis",
        analysis_stage="Stage 5",
        estimand_or_metric="Governed model-role decision",
        estimate="Stage3_Model_C", uncertainty_low="", uncertainty_high="",
        multiplicity_or_decision_rule="Stage 3 positive incremental rule plus Stage 4 failed positive extension rule",
        governed_conclusion="Model C remains the preferred prediction model; Model D is descriptive global-shape sensitivity only.",
        authorized_wording="Model C remained preferred after the controlled EBM extension failed to establish incremental benefit.",
        prohibited_interpretation="Model D promotion, diagnostic ranking as scientific effect, or clinical deployment.",
        source_artifact="config/v2_stage4_release.json::incremental_prediction_release.preferred_prediction_model",
    )
    return rows


def make_claims_matrix() -> list[dict[str, str]]:
    return [
        {"claim_id": "C-01", "topic": "Stage 2 primary association", "status": "authorized_with_restrictions", "authorized_wording": "Higher acceleration was associated with higher serious mobility-disability prevalence; report the global PR with explicit nonlinearity.", "restriction_or_reason": "Observational, survey-weighted association; not constant across the acceleration range.", "source": "config/v2_stage2_release.json::primary_result"},
        {"claim_id": "C-02", "topic": "Stage 2 nonlinearity", "status": "authorized", "authorized_wording": "The adjusted association was nonlinear and strongest in the lower-to-middle acceleration range.", "restriction_or_reason": "No threshold or protective-tail interpretation.", "source": "config/v2_stage2_release.json::nonlinearity"},
        {"claim_id": "C-03", "topic": "Secondary outcomes", "status": "authorized_with_restrictions", "authorized_wording": "Positive Holm-adjusted associations were observed for the three prespecified secondary outcomes.", "restriction_or_reason": "Supportive secondary evidence; not separate primary validation claims.", "source": "results/tables/v2/11_stage2_release_summary.csv::role=secondary"},
        {"claim_id": "C-04", "topic": "Race/ethnicity interaction", "status": "authorized_with_restrictions", "authorized_wording": "The prespecified global race/ethnicity interaction family was supported after BH control.", "restriction_or_reason": "Global linear summary only; race/ethnicity is a social classification; no biological, causal, or ranking claim.", "source": "config/v2_stage3_release.json::transportability_release"},
        {"claim_id": "C-05", "topic": "Sex, age-group, cycle interactions", "status": "unsupported", "authorized_wording": "No supported interaction-family conclusion for sex, age group, or NHANES cycle.", "restriction_or_reason": "Families did not pass the frozen BH q=0.10 rule.", "source": "results/tables/v2/13_stage3_transportability_global_tests.csv::dimension=sex|age_group|NHANES_cycle"},
        {"claim_id": "C-06", "topic": "Model C incremental prediction", "status": "authorized_with_restrictions", "authorized_wording": "Model C modestly improved bidirectional cross-cycle prediction within NHANES 2015–2018 beyond Model B.", "restriction_or_reason": "Not independent external-cohort validation, clinical utility, or individual risk prediction.", "source": "config/v2_stage3_release.json::prediction_release"},
        {"claim_id": "C-07", "topic": "Model D incremental prediction", "status": "unsupported", "authorized_wording": "The main-effects EBM did not demonstrate incremental predictive improvement beyond Model C.", "restriction_or_reason": "Intervals permit small benefit or small harm; failure is not evidence of harm.", "source": "config/v2_stage4_release.json::incremental_prediction_release"},
        {"claim_id": "C-08", "topic": "Model D as preferred model", "status": "prohibited", "authorized_wording": "Model C remains the preferred prediction model.", "restriction_or_reason": "The frozen positive extension rule failed.", "source": "config/v2_stage4_release.json::incremental_prediction_release"},
        {"claim_id": "C-09", "topic": "Global EBM acceleration shape", "status": "authorized_with_restrictions", "authorized_wording": "Cycle-trained acceleration-term functions were highly rank-correlated over governed common support.", "restriction_or_reason": "Descriptive global-shape sensitivity only; no exact curve agreement, threshold, causality, or local explanation.", "source": "config/v2_stage4_release.json::global_explanation_release"},
        {"claim_id": "C-10", "topic": "Causality", "status": "prohibited", "authorized_wording": "Use associational language only.", "restriction_or_reason": "Observational NHANES design.", "source": "docs/v2/V2_Research_Protocol.md::causal-boundary"},
        {"claim_id": "C-11", "topic": "Clinical or participant-level product", "status": "prohibited", "authorized_wording": "No clinical threshold, treatment rule, individual risk score, or participant-level explanation is released.", "restriction_or_reason": "Outside governed scope and absent clinical-utility evaluation.", "source": "config/v2_stage4_release.json::incremental_prediction_release.guardrails"},
        {"claim_id": "C-12", "topic": "Final V2 release and main merge", "status": "pending_final_review", "authorized_wording": "Stage 5 is a release candidate pending separate human review.", "restriction_or_reason": "Final V2 release, final manuscript claims, ARISE submission, and merge to main remain unauthorized.", "source": "config/v2_stage5_release_candidate.json::release-controls"},
    ]


def abstract_text(data: dict[str, Any]) -> tuple[str, int]:
    s2 = data["stage2_primary"]
    s2n = data["stage2_nonlinearity"]
    s3 = data["stage3_summary"]
    s4 = data["stage4_summary"]
    race = data["stage3_global"]["race_ethnicity"]
    text = f"""# AgeLens V2 ARISE Working Abstract

## Background
Phenotypic Age is a blood-chemistry-based aging measure, but its functional-health relevance and incremental prediction across recent NHANES cycles require controlled evaluation. We extended a frozen reproducible implementation to examine serious difficulty walking or climbing stairs as the primary V2 outcome.

## Methods
We analyzed adults in NHANES 2015–2018 using complex-survey weights, strata, and primary sampling units. Survey-weighted modified-Poisson models estimated adjusted prevalence ratios for Phenotypic Age acceleration, with prespecified spline diagnostics and Holm-adjusted secondary outcomes. Transportability used four prespecified global interaction families with Benjamini–Hochberg control. Incremental prediction compared demographic Model B with acceleration-augmented Model C in both cycle directions using Brier score, AUC, calibration, and 500 stratified-PSU bootstrap replicates. A frozen main-effects Explainable Boosting Machine (Model D) was then compared with Model C without interaction or hyperparameter search.

## Results
Among {int(s2['n']):,} adults with {int(s2['positive_n']):,} mobility-disability cases, the prespecified global linear summary was a prevalence ratio of {float(s2['prevalence_ratio']):.3f} per 5-year higher acceleration (95% CI {float(s2['ci_low_95']):.3f}–{float(s2['ci_high_95']):.3f}). Spline diagnostics showed nonlinearity (quasi-Poisson p={float(s2n['prespecified_quasipoisson_nonlinearity_p']):.3g}; bounded logistic spline p={float(s2n['logistic_spline_nonlinearity_p']):.3g}), with the steepest increase in the lower-to-middle acceleration range. The global race/ethnicity interaction family was supported after multiplicity control (q={float(race['q_value_bh']):.4f}), with race/ethnicity treated strictly as a social classification; sex, age-group, and cycle families were not. Model C modestly improved pooled out-of-cycle prediction versus Model B: Brier delta C−B {float(s3['prediction_brier_delta_c_minus_b']['estimate']):.4f} (95% CI {float(s3['prediction_brier_delta_c_minus_b']['ci_low_95']):.4f} to {float(s3['prediction_brier_delta_c_minus_b']['ci_high_95']):.4f}) and AUC delta C−B {float(s3['prediction_auc_delta_c_minus_b']['estimate']):.4f} (95% CI {float(s3['prediction_auc_delta_c_minus_b']['ci_low_95']):.4f} to {float(s3['prediction_auc_delta_c_minus_b']['ci_high_95']):.4f}). Model D did not establish improvement beyond Model C: Brier delta D−C {float(s4['brier_delta_d_minus_c']['estimate']):.4f} (95% CI {float(s4['brier_delta_d_minus_c']['ci_low_95']):.4f} to {float(s4['brier_delta_d_minus_c']['ci_high_95']):.4f}) and AUC delta D−C {float(s4['auc_delta_d_minus_c']['estimate']):.4f} (95% CI {float(s4['auc_delta_d_minus_c']['ci_low_95']):.4f} to {float(s4['auc_delta_d_minus_c']['ci_high_95']):.4f}).

## Conclusions
Phenotypic Age acceleration was associated with mobility disability and added modest out-of-cycle predictive information within NHANES, although the association was nonlinear and transportability evidence was restricted. The prespecified explainable extension did not demonstrate incremental prediction beyond Model C, which remained preferred. Findings are observational, are not independent external-cohort validation, and do not support causal, clinical, threshold, or individual-risk claims.
"""
    body_words = [word for line in text.splitlines() if not line.startswith("#") for word in line.split()]
    return text.rstrip() + f"\n\n**Word count:** {len(body_words)}\n", len(body_words)


def build_docs(data: dict[str, Any], word_count: int) -> dict[str, str]:
    s2 = data["stage2_primary"]
    s2n = data["stage2_nonlinearity"]
    s3 = data["stage3_summary"]
    race = data["stage3_global"]["race_ethnicity"]
    s4 = data["stage4_summary"]
    stable = data["stage4_stability"]
    synthesis = f"""# AgeLens V2 Stage 5 Scientific Synthesis

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5S-001 |
| Version | 1.0 |
| Status | Release candidate pending human review |
| Date | 2026-07-24 |
| Build | {BUILD} |

## Scope

This synthesis uses only released aggregate Stage 2–4 artifacts. It fits no model, performs no search or tuning, opens no participant-level data, and does not alter V1.

## Scientific Progression

V1 established a governed and reproducible Phenotypic Age implementation and survey-weighted mortality baseline. Stage 2 evaluated the frozen non-mortality outcome of serious difficulty walking or climbing stairs. Stage 3 evaluated prespecified transportability and bidirectional cross-cycle incremental prediction. Stage 4 tested one frozen main-effects explainable extension. Stage 5 integrates those results without creating a new estimate.

## Stage 2 — Functional-health Association

The primary domain contained {int(s2['n']):,} adults and {int(s2['positive_n']):,} positive responses. The prespecified global linear summary was PR {float(s2['prevalence_ratio']):.3f} per 5-year higher acceleration (95% CI {float(s2['ci_low_95']):.3f}–{float(s2['ci_high_95']):.3f}). This is an observational global summary, not a constant effect or individual probability.

Nonlinearity was supported by the prespecified quasi-Poisson test (p={float(s2n['prespecified_quasipoisson_nonlinearity_p']):.6g}) and bounded logistic-spline test (p={float(s2n['logistic_spline_nonlinearity_p']):.6g}). The governed interpretation is that adjusted prevalence rose most steeply from lower-to-middle acceleration values and the relative increase attenuated at higher positive acceleration. No protective low-tail claim or clinical threshold is authorized.

All three prespecified secondary outcomes showed positive Holm-adjusted associations. They are supportive secondary evidence rather than independent primary validations.

## Stage 3 — Transportability and Incremental Prediction

The race/ethnicity interaction family was supported under BH q=0.10 (raw p={float(race['p_value_raw']):.6g}; q={float(race['q_value_bh']):.6g}); sex, age-group, and cycle families were unsupported. This concerns only the frozen global linear acceleration summary under known nonlinearity. Race/ethnicity is a social classification and the result does not authorize biological, causal, pairwise-ranking, or group-risk claims.

Model C showed modest incremental cross-cycle prediction beyond Model B within NHANES 2015–2018. Brier delta C−B was {float(s3['prediction_brier_delta_c_minus_b']['estimate']):.6f} (95% CI {float(s3['prediction_brier_delta_c_minus_b']['ci_low_95']):.6f} to {float(s3['prediction_brier_delta_c_minus_b']['ci_high_95']):.6f}); AUC delta C−B was {float(s3['prediction_auc_delta_c_minus_b']['estimate']):.6f} (95% CI {float(s3['prediction_auc_delta_c_minus_b']['ci_low_95']):.6f} to {float(s3['prediction_auc_delta_c_minus_b']['ci_high_95']):.6f}). This is not independent external-cohort validation or clinical utility.

## Stage 4 — Controlled Explainable Extension

The frozen main-effects EBM used the Model C information set, zero interactions, no hyperparameter search, both cross-cycle directions, and 500 stratified-PSU bootstrap replicates. It did not demonstrate incremental predictive improvement beyond Model C. Brier delta D−C was {float(s4['brier_delta_d_minus_c']['estimate']):.6f} (95% CI {float(s4['brier_delta_d_minus_c']['ci_low_95']):.6f} to {float(s4['brier_delta_d_minus_c']['ci_high_95']):.6f}); AUC delta D−C was {float(s4['auc_delta_d_minus_c']['estimate']):.6f} (95% CI {float(s4['auc_delta_d_minus_c']['ci_low_95']):.6f} to {float(s4['auc_delta_d_minus_c']['ci_high_95']):.6f}). Failure of the positive rule is not evidence that Model D is harmful.

The acceleration-term functions had Spearman rank correlation {float(stable['spearman_correlation']):.6f} over {int(stable['common_grid_n'])} eligible common-support points. This is a descriptive global rank-shape result, not exact curve agreement, a prevalence ratio, a causal effect, a threshold, or a local participant explanation.

## Final Model-role Decision

Model C remains the preferred prediction model. Model D is retained only as a negative incremental-prediction result and descriptive global-shape sensitivity. Null and negative findings remain visible.

## Release Boundary

This document is a release candidate. Human review is pending. Final V2 release, final manuscript claims, ARISE submission, and merge to `main` remain unauthorized.
"""
    report = f"""# AgeLens V2 Aggregate Validation Report

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5V-001 |
| Version | 1.0 |
| Status | Aggregate validation candidate |
| Date | 2026-07-24 |
| Build | {BUILD} |

## 1. Objectives and Frozen Governance

AgeLens V2 evaluated functional-health association, secondary outcomes, transportability, incremental prediction, and one controlled explainable extension while preserving V1 immutability. Outcomes, estimands, model hierarchy, multiplicity rules, validation directions, metrics, and the Stage 4 method were frozen before the corresponding result inspection. Stage 5 performs synthesis only.

## 2. Cohort and Survey-design Reconciliation

The primary Stage 2 domain contained {int(s2['n']):,} adults, {int(s2['positive_n']):,} positive responses, and the governed NHANES complex-survey design. Stage 2–4 release validators reconcile counts, weights, strata, PSUs, metrics, and bootstrap completion. Stage 5 reads aggregate outputs and does not reconstruct participant-level cohorts.

## 3. Association

The primary survey-weighted modified-Poisson global summary was PR {float(s2['prevalence_ratio']):.6f} per 5-year higher acceleration (95% CI {float(s2['ci_low_95']):.6f}–{float(s2['ci_high_95']):.6f}). This addresses adjusted association, not causality or predictive discrimination.

## 4. Nonlinearity

The quasi-Poisson nonlinearity p-value was {float(s2n['prespecified_quasipoisson_nonlinearity_p']):.15g}; the bounded logistic-spline nonlinearity p-value was {float(s2n['logistic_spline_nonlinearity_p']):.15g}. The global linear PR remains a prespecified summary, but it must not be interpreted as a uniform effect across the acceleration distribution. No clinical threshold is identified.

## 5. Secondary Outcomes and Multiplicity

The six-domain disability composite, fair/poor general health, and PHQ-9 ≥10 analyses were governed secondary outcomes and used Holm adjustment. Each showed a positive association. These results support breadth of association but do not replace the primary outcome or establish independent causal validation.

## 6. Transportability

Four prespecified global interaction families were controlled with Benjamini–Hochberg q=0.10. Race/ethnicity was supported (raw p={float(race['p_value_raw']):.15g}; q={float(race['q_value_bh']):.15g}); sex, age group, and NHANES cycle were unsupported. Because Stage 2 established nonlinearity, the interaction result is restricted to the frozen global linear acceleration summary. It is not biological, causal, or a basis for pairwise ranking.

## 7. Predictive Discrimination and Error

Model C versus Model B used bidirectional cycle holdout and 500 stratified-PSU bootstrap replicates. Brier delta C−B was {float(s3['prediction_brier_delta_c_minus_b']['estimate']):.15g} (95% CI {float(s3['prediction_brier_delta_c_minus_b']['ci_low_95']):.15g} to {float(s3['prediction_brier_delta_c_minus_b']['ci_high_95']):.15g}); AUC delta C−B was {float(s3['prediction_auc_delta_c_minus_b']['estimate']):.15g} (95% CI {float(s3['prediction_auc_delta_c_minus_b']['ci_low_95']):.15g} to {float(s3['prediction_auc_delta_c_minus_b']['ci_high_95']):.15g}). The released conclusion is modest incremental cross-cycle prediction within NHANES, not independent external-cohort validation.

## 8. Calibration

Stage 3 Model C calibration met the frozen rule. Stage 4 Model D calibration also remained acceptable, but acceptable calibration did not override the failed joint positive-extension rule. Calibration, discrimination, and overall prediction error are reported as distinct properties.

## 9. Controlled Explainability

Model D was a main-effects-only Explainable Boosting Machine using the Model C information set, with zero interactions and no search or tuning. Brier delta D−C was {float(s4['brier_delta_d_minus_c']['estimate']):.15g} (95% CI {float(s4['brier_delta_d_minus_c']['ci_low_95']):.15g} to {float(s4['brier_delta_d_minus_c']['ci_high_95']):.15g}); AUC delta D−C was {float(s4['auc_delta_d_minus_c']['estimate']):.15g} (95% CI {float(s4['auc_delta_d_minus_c']['ci_low_95']):.15g} to {float(s4['auc_delta_d_minus_c']['ci_high_95']):.15g}). Incremental improvement was not supported.

The global acceleration term showed Spearman rank correlation {float(stable['spearman_correlation']):.15g} across {int(stable['common_grid_n'])} common eligible points. Explainability here means a restricted aggregate model-shape diagnostic. It does not create causal interpretation, exact curve agreement, a clinical threshold, or a local explanation.

## 10. Model-role Synthesis

Model C remains preferred. Model D is not promoted and is retained only for the negative incremental result and descriptive global-shape sensitivity.

## 11. Reproducibility Controls

The build validates the released Stage 2–4 dependencies, reconciles JSON and CSV values within absolute tolerance {TOLERANCE:g}, hashes every authoritative source, records runtime metadata, uses deterministic row ordering, and writes UTF-8 aggregate outputs. It fits no model and requires no network access.

## 12. Disclosure Controls

Stage 5 tables and figures are aggregate-only. No SEQN, participant identifier, participant-level prediction, local contribution, private NHANES path, raw data, or unpublished participant-level material is written.

## 13. Limitations

The analysis is observational. Cross-cycle validation remains internal to NHANES 2015–2018. Modified-Poisson fitted values are not individual probabilities. Transportability evidence is restricted and must be interpreted under established nonlinearity. No decision-curve, treatment-threshold, independent-cohort, clinical-utility, or individual-risk evaluation was performed.

## 14. Authorized Conclusions

1. Acceleration was associated with serious mobility disability, with strong nonlinearity.
2. Prespecified secondary outcomes showed supportive positive associations after Holm adjustment.
3. Model C added modest out-of-cycle predictive information within NHANES beyond Model B.
4. The race/ethnicity global interaction family was supported with strict social-classification guardrails; other families were unsupported.
5. Model D did not establish incremental predictive improvement beyond Model C.
6. The global acceleration rank-shape sensitivity passed its restricted governed rule.
7. Model C remains preferred.

## 15. Prohibited Conclusions and Unresolved Actions

Causal, biological subgroup, clinical threshold, individual-risk, local-explanation, EBM-superiority, and independent external-cohort claims are prohibited. Human review remains pending. Final V2 release, final manuscript claims, ARISE submission, and merge to `main` remain unauthorized.
"""
    presentation = f"""# AgeLens V2 ARISE Presentation — Working Outline

**Target duration:** approximately 8 minutes 20 seconds
**Status:** working material pending human review

## Slide 1 — Title and Research Question (0:45)

**Title:** From reproducible Phenotypic Age replication to controlled functional-health validation

**Content:**
- Can Phenotypic Age acceleration inform functional-health association and cross-cycle prediction beyond chronological age and demographics?
- NHANES 2015–2018; governed, survey-aware, aggregate-only workflow.

**Recommended visual:** project title with one-sentence research question.

**Speaker notes:** Introduce AgeLens as a replication-first project. State that V2 was designed before modeling and separates association, prediction, transportability, and explainability.

## Slide 2 — V1-to-V2 Scientific Progression (0:55)

**Content:**
- V1: reproducible Phenotypic Age construction and mortality baseline.
- Stage 2: functional-health association.
- Stage 3: transportability and cross-cycle incremental prediction.
- Stage 4: one frozen explainable extension.
- Final role decision: Model C preferred.

**Recommended visual:** `21_stage5_v1_to_v2_progression.png`.

**Speaker notes:** Emphasize evidence before implementation and that negative findings were retained.

## Slide 3 — Data, Outcome, and Survey-aware Design (0:55)

**Content:**
- Primary outcome: serious difficulty walking or climbing stairs.
- Primary domain: {int(s2['n']):,} adults; {int(s2['positive_n']):,} positive responses.
- Complex-survey weights, strata, and PSUs were part of the estimand.
- No participant-level outputs entered the public release.

**Recommended visual:** concise design schematic.

**Speaker notes:** State that this is observational NHANES analysis and not a clinical prediction product.

## Slide 4 — Conventional Functional-health Validation (1:05)

**Content:**
- Global linear summary: PR {float(s2['prevalence_ratio']):.3f} per 5-year higher acceleration.
- 95% CI {float(s2['ci_low_95']):.3f}–{float(s2['ci_high_95']):.3f}.
- Three prespecified secondary outcomes were positive after Holm adjustment.

**Recommended visual:** existing Stage 2 adjusted-prevalence curve, not a conventional-regression-as-AI graphic.

**Speaker notes:** Present the PR as a global summary and immediately transition to nonlinearity.

## Slide 5 — Nonlinearity Changes the Interpretation (1:00)

**Content:**
- Quasi-Poisson nonlinearity p={float(s2n['prespecified_quasipoisson_nonlinearity_p']):.3g}.
- Bounded logistic-spline p={float(s2n['logistic_spline_nonlinearity_p']):.3g}.
- Steepest adjusted-prevalence increase occurred in the lower-to-middle acceleration range.
- No constant effect, protective low tail, or clinical threshold claim.

**Recommended visual:** existing bounded Stage 2 adjusted-prevalence curve.

**Speaker notes:** Explain why a single per-5-year coefficient cannot describe the full association shape.

## Slide 6 — Transportability and Incremental Prediction (1:15)

**Content:**
- Race/ethnicity global interaction family supported after BH control; sex, age-group, and cycle families unsupported.
- Model C vs Model B: Brier delta {float(s3['prediction_brier_delta_c_minus_b']['estimate']):.4f}; AUC delta {float(s3['prediction_auc_delta_c_minus_b']['estimate']):.4f}.
- Both are bidirectional cross-cycle results within NHANES.

**Recommended visual:** existing Stage 3 incremental-performance figure plus a small guardrail callout.

**Speaker notes:** Race/ethnicity is a social classification. Do not interpret the interaction biologically or rank groups. Clarify that this is not independent external-cohort validation.

## Slide 7 — Controlled EBM Extension: Negative Incremental Result (1:05)

**Content:**
- One prespecified main-effects EBM; same information set as Model C.
- Zero interactions; no hyperparameter search.
- Brier delta D−C {float(s4['brier_delta_d_minus_c']['estimate']):.4f}; AUC delta D−C {float(s4['auc_delta_d_minus_c']['estimate']):.4f}.
- Incremental improvement not supported; Model C remained preferred.

**Recommended visual:** existing Stage 4 incremental-performance figure.

**Speaker notes:** The EBM was the explainable machine-learning extension. Its negative result is part of the contribution because the method and gate were frozen in advance. Failure to establish benefit is not evidence of harm.

## Slide 8 — Conclusions, Limitations, and Reproducibility (1:20)

**Content:**
- Association with mobility disability was supported but nonlinear.
- Acceleration added modest cross-cycle prediction within NHANES.
- Transportability evidence was restricted.
- The EBM did not improve upon Model C.
- Aggregate-only, source-hashed, governed release workflow.

**Recommended visual:** `21_stage5_evidence_synthesis.png`.

**Speaker notes:** Close with observational and internal-NHANES limitations. No causal, clinical, threshold, or individual-risk claim is made. Human review and final release remain pending.

## Take-home Message

A reproducibly derived Phenotypic Age acceleration measure was associated with mobility disability and modestly improved cross-cycle prediction within NHANES, while a prespecified explainable extension did not outperform the simpler governed Model C.
"""
    release_candidate = f"""# AgeLens V2 Stage 5 Release Candidate

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5RC-002 |
| Version | 1.0 |
| Status | Pending human review |
| Date | 2026-07-24 |
| Build | {BUILD} |

## Candidate Contents

- deterministic aggregate Stage 2–4 scientific synthesis;
- independently runnable Stage 5 validator;
- source-hash manifest and runtime record;
- aggregate scientific and claims tables;
- V1-to-V2 progression and evidence-synthesis figures;
- aggregate validation report;
- ARISE working abstract ({word_count} words) and 8-slide working presentation;
- pending human-review form.

## Scientific Decision State

Model C remains the preferred prediction model. Model D did not demonstrate incremental benefit and is retained only as a negative result and descriptive global-shape sensitivity. Stage 2 nonlinearity and Stage 3 transportability restrictions remain explicit. No new model was fitted.

## Machine-checkable Status

- Stage 5 synthesis implementation: complete
- Aggregate validation: pass
- Human review: pending
- Final V2 release: unauthorized
- Merge to `main`: unauthorized
- Final manuscript claims: unauthorized
- ARISE final submission: unauthorized
"""
    human_review = """# AgeLens V2 Stage 5 Human Review

## Document Control

| Field | Value |
| --- | --- |
| Document ID | AL-V2-S5HR-001 |
| Version | 1.0 |
| Status | Pending human review |
| Date | 2026-07-24 |

## Review Checklist

| Review item | Reviewer decision | Notes |
| --- | --- | --- |
| Stage 2 primary association and nonlinearity are both represented accurately | Pending | |
| Secondary outcomes and Holm multiplicity are represented accurately | Pending | |
| Stage 3 transportability restrictions are retained | Pending | |
| Model C versus Model B prediction conclusion is accurate | Pending | |
| Model D versus Model C negative incremental conclusion is retained | Pending | |
| Model C remains preferred | Pending | |
| Global EBM shape result is described only as restricted aggregate rank stability | Pending | |
| Causal, biological subgroup, clinical, threshold, and individual-risk claims are absent | Pending | |
| Figures do not compare incomparable metrics on a common numerical scale | Pending | |
| Abstract and presentation are appropriate working materials | Pending | |
| Aggregate-only disclosure and V1 immutability controls pass | Pending | |
| Final release and merge to main remain unauthorized | Pending | |

## Decision

**Pending human review.** No approval, final V2 release, ARISE submission, manuscript release, or merge authorization has been issued.
"""
    return {
        "V2_Stage5_Synthesis.md": synthesis,
        "V2_Aggregate_Validation_Report.md": report,
        "V2_ARISE_Presentation.md": presentation,
        "V2_Stage5_Release_Candidate.md": release_candidate,
        "V2_Stage5_Human_Review.md": human_review,
    }


def update_governance_docs(root: Path) -> None:
    updates = {
        "docs/v2/README.md": """## Stage 5 Aggregate Synthesis

Stage 5 builds a deterministic aggregate synthesis, validation report, ARISE working abstract and presentation, two publication-safe figures, source manifest, claims matrix, and release candidate. It fits no model and reads no participant-level data. Model C remains preferred. Human review, final V2 release, ARISE final submission, and merge to `main` remain unauthorized.

Run:

```powershell
python .\\scripts\\v2\\21_build_stage5_synthesis.py --project-root .
python .\\scripts\\v2\\22_validate_stage5_release_candidate.py --project-root .
```""",
        "docs/v2/V2_Research_Protocol.md": """## Stage 5 Release-candidate Implementation

Stage 5 aggregate synthesis is implemented using only released Stage 2–4 artifacts. No model fitting, refitting, feature or interaction search, hyperparameter tuning, participant-level output, local explanation, clinical threshold, or causal interpretation is authorized. Model C remains preferred. The Stage 5 package is a release candidate pending human review; final V2 release, final manuscript claims, ARISE submission, and merge to `main` remain unauthorized.""",
        "docs/v2/V2_Analysis_Plan.md": """## Stage 5 Synthesis Plan

Stage 5 extracts released values programmatically, reconciles machine-readable sources, records source hashes and runtime metadata, produces aggregate synthesis tables and non-comparative evidence figures, and prepares working ARISE materials. Stage 5 introduces no new estimand, metric, model, threshold, subgroup analysis, or optimization.""",
        "docs/v2/V2_Decision_Log.md": """## Stage 5 Decision — Aggregate Synthesis Release Candidate

**Decision:** Build the Stage 5 synthesis and ARISE working package from released Stage 2–4 aggregate evidence only. Retain Model C as the preferred prediction model and retain the negative Model D result. Human review is required before any final release decision. Merge to `main` remains unauthorized.""",
        "docs/v2/V2_Evidence_Gap_Register.md": """## Stage 5 Evidence-gap Disposition

Stage 5 does not close gaps by inference or new analysis. Remaining limits—including observational design, internal NHANES cross-cycle validation, restricted transportability, absence of clinical utility, and absence of independent external-cohort validation—remain explicit limitations and do not block preparation of a review candidate. They continue to block unsupported claims.""",
        "docs/v2/V2_ARISE_Alignment.md": """## Stage 5 ARISE Working Alignment

The working ARISE package emphasizes a governed progression from reproducible replication to functional-health association, restricted transportability, modest cross-cycle prediction, and a negative controlled explainable extension. Conventional regression is not labeled AI. The EBM is described as one prespecified explainable machine-learning extension that did not establish improvement beyond Model C. Final submission remains unauthorized pending human review and verification of current ARISE requirements.""",
    }
    for relpath, section in updates.items():
        path = root / relpath
        if not path.is_file():
            raise Stage5Error(f"Cannot update missing governance document: {relpath}")
        original = path.read_text(encoding="utf-8")
        block = f"{STAGE5_MARKER_BEGIN}\n{section.rstrip()}\n{STAGE5_MARKER_END}"
        if STAGE5_MARKER_BEGIN in original and STAGE5_MARKER_END in original:
            prefix, rest = original.split(STAGE5_MARKER_BEGIN, 1)
            _, suffix = rest.split(STAGE5_MARKER_END, 1)
            updated = prefix.rstrip() + "\n\n" + block + suffix
        else:
            updated = original.rstrip() + "\n\n" + block + "\n"
        write_text(path, updated)


def create_figures(root: Path, data: dict[str, Any]) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
    except ImportError as exc:
        raise Stage5Error("matplotlib is required for Stage 5 figures.") from exc

    figures = root / "results/figures/v2"
    figures.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1)
    ax.axis("off")
    titles = ["V1", "Stage 2", "Stage 3", "Stage 4", "Stage 5 role"]
    bodies = [
        "Reproducible Phenotypic Age\nconstruction + mortality baseline",
        "Functional-health association\nMobility disability primary outcome\nNonlinearity retained",
        "Restricted transportability\nPooled out-of-cycle prediction\nModel C modestly improved",
        "Frozen main-effects EBM\nNo incremental benefit\nGlobal rank-shape sensitivity",
        "Model C preferred\nAggregate synthesis\nHuman review pending",
    ]
    for index, (title, body) in enumerate(zip(titles, bodies)):
        x = index + 0.08
        patch = FancyBboxPatch((x, 0.2), 0.84, 0.58, boxstyle="round,pad=0.02", linewidth=1.4, facecolor="white")
        ax.add_patch(patch)
        ax.text(x + 0.42, 0.67, title, ha="center", va="center", fontsize=13, fontweight="bold")
        ax.text(x + 0.42, 0.44, body, ha="center", va="center", fontsize=9.5, linespacing=1.35)
        if index < 4:
            ax.annotate("", xy=(index + 1.03, 0.49), xytext=(index + 0.93, 0.49), arrowprops={"arrowstyle": "->", "linewidth": 1.4})
    ax.set_title("AgeLens scientific progression: replication before controlled innovation", fontsize=15, pad=18)
    fig.tight_layout()
    fig.savefig(figures / "21_stage5_v1_to_v2_progression.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    s2 = data["stage2_primary"]
    s3 = data["stage3_summary"]
    s4 = data["stage4_summary"]
    fig, ax = plt.subplots(figsize=(13, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    sections = [
        (0.68, "Association", f"Stage 2: PR {float(s2['prevalence_ratio']):.3f} per 5 years\n95% CI {float(s2['ci_low_95']):.3f}–{float(s2['ci_high_95']):.3f}\nStrong nonlinearity; observational"),
        (0.42, "Incremental prediction", f"Stage 3 Model C vs B\nBrier Δ {float(s3['prediction_brier_delta_c_minus_b']['estimate']):.4f}\nAUC Δ {float(s3['prediction_auc_delta_c_minus_b']['estimate']):.4f}\nModest out-of-cycle gain within NHANES"),
        (0.16, "Controlled explainable extension", f"Stage 4 Model D vs C\nBrier Δ {float(s4['brier_delta_d_minus_c']['estimate']):.4f}\nAUC Δ {float(s4['auc_delta_d_minus_c']['estimate']):.4f}\nIncremental benefit not supported"),
    ]
    for y, title, body in sections:
        patch = FancyBboxPatch((0.08, y), 0.84, 0.19, boxstyle="round,pad=0.02", linewidth=1.4, facecolor="white")
        ax.add_patch(patch)
        ax.text(0.12, y + 0.145, title, fontsize=13, fontweight="bold", va="center")
        ax.text(0.12, y + 0.075, body, fontsize=10.5, va="center", linespacing=1.35)
    ax.text(0.5, 0.965, "AgeLens V2 evidence synthesis", ha="center", va="top", fontsize=16, fontweight="bold")
    ax.text(0.5, 0.915, "Distinct estimands are shown in separate panels; numerical scales are not pooled.", ha="center", va="top", fontsize=10)
    ax.text(0.5, 0.055, "Governed model role: Model C preferred; Model D retained only as a negative result and global-shape sensitivity.", ha="center", va="center", fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(figures / "21_stage5_evidence_synthesis.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def validate_generated_table_safety(root: Path) -> None:
    forbidden_headers = {"SEQN", "participant_id", "prediction", "local_contribution", "risk_score"}
    forbidden_text_patterns = ("C:\\\\Users\\\\", "/Users/", "/home/", "AKIA", "BEGIN PRIVATE KEY")
    for path in sorted((root / "results/tables/v2").glob("21_stage5_*.csv")):
        rows = read_csv(path)
        header = set(rows[0]) if rows else set()
        overlap = forbidden_headers & header
        if overlap:
            raise Stage5Error(f"Participant-level field in Stage 5 table {path.name}: {sorted(overlap)}")
        text = path.read_text(encoding="utf-8-sig")
        matched = [pattern for pattern in forbidden_text_patterns if pattern in text]
        if matched:
            raise Stage5Error(f"Private path or secret-like text in {path.name}: {matched}")


def build(root: Path) -> None:
    root = root.resolve()
    print(f"AgeLens V2 Stage 5 aggregate synthesis\nRepository: {root}")
    require_files(root, [
        "config/v2_stage5_synthesis.json",
        "config/v2_stage5_release_candidate.json",
        "scripts/v2/21_build_stage5_synthesis.py",
        "scripts/v2/22_validate_stage5_release_candidate.py",
        "scripts/v2/11_validate_stage2_release.py",
        "scripts/v2/15_validate_stage3_release.py",
        "scripts/v2/20_validate_stage4_release.py",
    ])

    for validator in (
        "scripts/v2/11_validate_stage2_release.py",
        "scripts/v2/15_validate_stage3_release.py",
        "scripts/v2/20_validate_stage4_release.py",
    ):
        run_prior_validator(root, validator)

    data = reconcile_sources(root)
    scientific_rows = make_scientific_summary(data)
    claims_rows = make_claims_matrix()
    tables = root / "results/tables/v2"
    write_csv(tables / "21_stage5_scientific_summary.csv", [
        "research_question", "analysis_stage", "estimand_or_metric", "estimate", "uncertainty_low", "uncertainty_high",
        "multiplicity_or_decision_rule", "governed_conclusion", "authorized_wording", "prohibited_interpretation", "source_artifact",
    ], scientific_rows)

    validation_rows = [
        {"validation_domain": "source_release_status", "pass": True, "observed": "Stage 2, Stage 3, and Stage 4 released_for_v2_development", "requirement": "All source stages released"},
        {"validation_domain": "stage2_numeric_reconciliation", "pass": True, "observed": "Primary, secondary, and nonlinearity values reconcile", "requirement": f"Absolute tolerance {TOLERANCE:g}"},
        {"validation_domain": "stage3_numeric_reconciliation", "pass": True, "observed": "Transportability and Model C prediction values reconcile", "requirement": f"Absolute tolerance {TOLERANCE:g}"},
        {"validation_domain": "stage4_numeric_reconciliation", "pass": True, "observed": "Model D comparison and shape stability values reconcile", "requirement": f"Absolute tolerance {TOLERANCE:g}"},
        {"validation_domain": "model_role", "pass": True, "observed": "Stage3_Model_C preferred; Model D not promoted", "requirement": "Model C remains preferred"},
        {"validation_domain": "negative_findings", "pass": True, "observed": "Stage 4 failed positive extension retained", "requirement": "Null and negative results retained"},
        {"validation_domain": "analysis_boundary", "pass": True, "observed": "No model fit, refit, search, tuning, threshold, or local explanation", "requirement": "Synthesis only"},
        {"validation_domain": "disclosure", "pass": True, "observed": "Aggregate tables, figures, and documents only", "requirement": "No participant-level output"},
        {"validation_domain": "release_boundary", "pass": True, "observed": "Human review pending; final release and main merge unauthorized", "requirement": "No fabricated approval"},
    ]
    write_csv(tables / "21_stage5_validation_summary.csv", ["validation_domain", "pass", "observed", "requirement"], validation_rows)
    write_csv(tables / "21_stage5_claims_matrix.csv", ["claim_id", "topic", "status", "authorized_wording", "restriction_or_reason", "source"], claims_rows)

    manifest_rows = []
    for relpath, path in sorted(zip(data["source_relpaths"], data["source_paths"])):
        manifest_rows.append({
            "source_path": relpath,
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
            "role": "authoritative_released_stage2_to_stage4_source",
        })
    write_csv(tables / "21_stage5_source_manifest.csv", ["source_path", "sha256", "size_bytes", "role"], manifest_rows)

    abstract, word_count = abstract_text(data)
    docs = build_docs(data, word_count)
    docs["V2_ARISE_Abstract.md"] = abstract
    for name, text in docs.items():
        write_text(root / "docs/v2" / name, text)

    create_figures(root, data)
    update_governance_docs(root)

    release_checks = [
        {"check": "Released Stage 2–4 source validators pass", "pass": True, "observed": "11, 15, and 20 validators completed"},
        {"check": "All source values reconcile", "pass": True, "observed": f"absolute tolerance {TOLERANCE:g}"},
        {"check": "Stage 2 nonlinearity is retained", "pass": True, "observed": "quasi-Poisson and bounded logistic-spline results included"},
        {"check": "Stage 3 restricted transportability is retained", "pass": True, "observed": "race/ethnicity family only; social-classification guardrails"},
        {"check": "Stage 3 Model C incremental result is retained", "pass": True, "observed": "Brier and AUC C−B reported"},
        {"check": "Stage 4 negative EBM result is retained", "pass": True, "observed": "positive extension not supported"},
        {"check": "Model C remains preferred", "pass": True, "observed": "Stage3_Model_C"},
        {"check": "No new model or optimization", "pass": True, "observed": "aggregate synthesis only"},
        {"check": "Aggregate-only public outputs", "pass": True, "observed": "no participant-level field"},
        {"check": "Human review remains pending", "pass": True, "observed": "no final approval"},
        {"check": "Merge to main remains unauthorized", "pass": True, "observed": "false"},
    ]
    write_csv(tables / "21_stage5_release_checks.csv", ["check", "pass", "observed"], release_checks)

    try:
        import matplotlib
        matplotlib_version = matplotlib.__version__
    except ImportError:
        matplotlib_version = "unavailable"
    runtime_rows = [
        {"component": "stage5_build", "version": BUILD},
        {"component": "python", "version": platform.python_version()},
        {"component": "implementation", "version": platform.python_implementation()},
        {"component": "platform", "version": platform.platform()},
        {"component": "matplotlib", "version": matplotlib_version},
        {"component": "generated_utc", "version": datetime.now(timezone.utc).replace(microsecond=0).isoformat()},
    ]
    write_csv(tables / "21_stage5_runtime_versions.csv", ["component", "version"], runtime_rows)

    release_candidate_path = root / "config/v2_stage5_release_candidate.json"
    release_candidate = read_json(release_candidate_path)
    release_candidate.update({
        "status": "release_candidate_pending_human_review",
        "stage5_synthesis_implementation": "complete",
        "aggregate_validation": "pass",
        "human_review": "pending",
        "final_v2_release_authorized": False,
        "merge_to_main_authorized": False,
        "final_manuscript_claims_authorized": False,
        "arise_final_submission_authorized": False,
        "preferred_prediction_model": "Stage3_Model_C",
        "model_d_role": "descriptive_global_shape_sensitivity_only",
        "generated_metadata": {
            "build": BUILD,
            "source_manifest_sha256": sha256(tables / "21_stage5_source_manifest.csv"),
            "abstract_word_count": word_count,
            "generated_utc": runtime_rows[-1]["version"],
        },
        "released_results": {
            "stage2_primary_prevalence_ratio_per_5_years": float(data["stage2_primary"]["prevalence_ratio"]),
            "stage2_quasipoisson_nonlinearity_p": float(data["stage2_nonlinearity"]["prespecified_quasipoisson_nonlinearity_p"]),
            "stage3_brier_delta_c_minus_b": float(data["stage3_summary"]["prediction_brier_delta_c_minus_b"]["estimate"]),
            "stage3_auc_delta_c_minus_b": float(data["stage3_summary"]["prediction_auc_delta_c_minus_b"]["estimate"]),
            "stage4_brier_delta_d_minus_c": float(data["stage4_summary"]["brier_delta_d_minus_c"]["estimate"]),
            "stage4_auc_delta_d_minus_c": float(data["stage4_summary"]["auc_delta_d_minus_c"]["estimate"]),
            "stage4_acceleration_shape_spearman": float(data["stage4_stability"]["spearman_correlation"]),
        },
    })
    write_text(release_candidate_path, json.dumps(release_candidate, indent=2, ensure_ascii=False))

    validate_generated_table_safety(root)
    run_prior_validator(root, "scripts/v2/22_validate_stage5_release_candidate.py")

    print("\nSTAGE 5 AGGREGATE SYNTHESIS BUILT.")
    print("Released Stage 2–4 evidence was reconciled and synthesized.")
    print("No statistical or machine-learning model was fitted.")
    print("Model C remains the preferred prediction model.")
    print("Human review, final release, ARISE submission, and merge to main remain unauthorized.")


def self_test() -> None:
    assert close("1.0", 1.0)
    assert not close("1.0", 1.1)
    assert parse_bool("TRUE") is True
    assert parse_bool("false") is False
    sample = Path("a/b.txt")
    assert sample.as_posix() == "a/b.txt"
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    build(args.project_root)


if __name__ == "__main__":
    main()
