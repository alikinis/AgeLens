"""Validate the governed AgeLens V2 Stage 4 release."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


EXPECTED_PYTHON_BUILD = "AgeLens-V2-Stage4-Python-20260724c"
EXPECTED_R_BUILD = "AgeLens-V2-Stage4-R-20260724b"
EXPECTED_DIRECTIONS = {
    "train_2015_2016_test_2017_2018",
    "train_2017_2018_test_2015_2016",
}
EXPECTED_FEATURES = {
    "chronological_age_years": 0,
    "sex": 1,
    "race_ethnicity": 2,
    "phenoage_acceleration_per_5_years": 3,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def close(actual: Any, expected: float, tolerance: float = 1e-10) -> bool:
    return math.isfinite(float(actual)) and abs(float(actual) - expected) <= tolerance


def row_map(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def validate(project_root: Path) -> None:
    root = project_root
    tables = root / "results/tables/v2"
    figures = root / "results/figures/v2"
    docs = root / "docs/v2"

    required = [
        root / "config/v2_stage3_release.json",
        root / "config/v2_stage4_method_freeze.json",
        root / "config/v2_stage4_implementation.json",
        root / "config/v2_stage4_release.json",
        root / "scripts/v2/17_prepare_stage4_reference.R",
        root / "scripts/v2/18_run_stage4_ebm.py",
        root / "scripts/v2/19_validate_stage4_results.py",
        root / "scripts/v2/20_validate_stage4_release.py",
        tables / "18_stage4_method_input_audit.csv",
        tables / "18_stage4_direction_metrics.csv",
        tables / "18_stage4_bootstrap_summary.csv",
        tables / "18_stage4_positive_extension_decision.csv",
        tables / "18_stage4_term_importance.csv",
        tables / "18_stage4_age_shape.csv",
        tables / "18_stage4_acceleration_shape.csv",
        tables / "18_stage4_shape_stability.csv",
        tables / "18_stage4_runtime_versions.csv",
        tables / "18_stage4_release_checks.csv",
        tables / "20_stage4_release_summary.csv",
        figures / "18_stage4_model_d_incremental_performance.png",
        figures / "18_stage4_cycle_specific_acceleration_shapes.png",
        docs / "V2_Stage4_Method_Selection.md",
        docs / "V2_Stage4_Method_Freeze_Report.md",
        docs / "V2_Stage4_Implementation.md",
        docs / "V2_Stage4_Human_Review.md",
        docs / "V2_Stage4_Release_Report.md",
        docs / "README.md",
        docs / "V2_Analysis_Plan.md",
        docs / "V2_Decision_Log.md",
        docs / "V2_Evidence_Gap_Register.md",
        docs / "V2_Research_Protocol.md",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing Stage 4 release artifacts: " + ", ".join(missing)
        )

    stage3 = json.loads(
        (root / "config/v2_stage3_release.json").read_text(encoding="utf-8")
    )
    if stage3.get("status") != "released_for_v2_development":
        raise ValueError("Stage 3 release dependency changed.")
    if not stage3["prediction_release"]["positive_incremental_utility_rule_passed"]:
        raise ValueError("Stage 3 Model C utility dependency changed.")

    freeze = json.loads(
        (root / "config/v2_stage4_method_freeze.json").read_text(
            encoding="utf-8"
        )
    )
    if freeze.get("status") != "frozen_implementation_authorized":
        raise ValueError("Stage 4 method freeze changed.")
    if freeze["selected_method"]["interactions"] != 0:
        raise ValueError("Stage 4 interaction freeze changed.")
    if freeze["permissions"]["merge_to_main_authorized"]:
        raise ValueError("Method freeze authorized main merge.")

    implementation = json.loads(
        (root / "config/v2_stage4_implementation.json").read_text(
            encoding="utf-8"
        )
    )
    if implementation.get("python_build") != EXPECTED_PYTHON_BUILD:
        raise ValueError("Stage 4 implementation Python build changed.")
    if implementation.get("r_build") != EXPECTED_R_BUILD:
        raise ValueError("Stage 4 implementation R build changed.")
    if implementation["environment"]["interpret_exact_version"] != "0.7.8":
        raise ValueError("Frozen Interpret version changed.")

    release = json.loads(
        (root / "config/v2_stage4_release.json").read_text(encoding="utf-8")
    )
    if release.get("status") != "released_for_v2_development":
        raise ValueError("Stage 4 release status changed.")
    if release.get("human_review_decision") != "pass_no_positive_extension":
        raise ValueError("Stage 4 human-review decision changed.")
    if not release["relationship_to_v1"]["v1_immutable"]:
        raise ValueError("V1 immutability changed.")

    prediction_release = release["incremental_prediction_release"]
    if prediction_release["positive_extension_claim_authorized"]:
        raise ValueError("A positive Model D extension claim was authorized.")
    if prediction_release["joint_positive_rule_passed"]:
        raise ValueError("Stage 4 joint decision changed.")
    if prediction_release["preferred_prediction_model"] != "Stage3_Model_C":
        raise ValueError("Preferred prediction model changed.")
    if prediction_release["model_d_prediction_role"] != "not_promoted":
        raise ValueError("Model D role changed.")

    permissions = release["permissions"]
    if not permissions["commit_to_v2_development_authorized"]:
        raise ValueError("Stage 4 commit authorization missing.")
    if not permissions["stage5_synthesis_and_arise_authorized"]:
        raise ValueError("Stage 5 authorization missing.")
    for key in (
        "stage4_positive_extension_claim_authorized",
        "model_d_primary_prediction_role_authorized",
        "local_explanation_release_authorized",
        "new_model_or_feature_search_authorized",
        "merge_to_main_authorized",
        "final_manuscript_claims_authorized",
    ):
        if permissions[key]:
            raise ValueError(f"Restricted permission enabled: {key}")

    audit = row_map(read_csv(tables / "18_stage4_method_input_audit.csv"), "check")
    if not all(parse_bool(row["pass"]) for row in audit.values()):
        raise ValueError("A Stage 4 input audit failed.")
    if int(float(audit["canonical_input_n"]["observed"])) != 5223:
        raise ValueError("Canonical input n changed.")
    if int(float(audit["primary_domain_n"]["observed"])) != 4366:
        raise ValueError("Primary domain n changed.")
    if int(float(audit["primary_positive_n"]["observed"])) != 682:
        raise ValueError("Primary positive n changed.")
    if float(audit["model_c_max_abs_reconciliation"]["observed"]) > 1e-7:
        raise ValueError("Model C reconciliation changed.")
    if audit["interpret_exact_version"]["observed"] != "0.7.8":
        raise ValueError("Interpret audit version changed.")
    if int(float(audit["point_model_d_interaction_term_max"]["observed"])) != 0:
        raise ValueError("Point EBM interaction count changed.")

    directions = read_csv(tables / "18_stage4_direction_metrics.csv")
    if set(row["direction"] for row in directions) != EXPECTED_DIRECTIONS:
        raise ValueError("Stage 4 directions changed.")
    if not all(float(row["brier_delta_d_minus_c"]) <= 0 for row in directions):
        raise ValueError("Direction-specific Brier pattern changed.")
    auc_signs = {
        math.copysign(1.0, float(row["auc_delta_d_minus_c"]))
        for row in directions
    }
    if auc_signs != {-1.0, 1.0}:
        raise ValueError("Direction-specific AUC pattern changed.")
    if not all(
        row["result_status"] == "provisional_pending_stage4_review"
        for row in directions
    ):
        raise ValueError("Source direction status changed.")

    bootstrap = row_map(
        read_csv(tables / "18_stage4_bootstrap_summary.csv"), "metric"
    )
    expected = {
        "brier_delta_d_minus_c": (
            -0.0009703249310347439,
            -0.003092809775090476,
            0.001152159913020988,
        ),
        "auc_delta_d_minus_c": (
            -0.00016066806647274667,
            -0.014072678802368638,
            0.013751342669423145,
        ),
        "calibration_intercept_d": (
            0.0024704243324506466,
            -0.036264290657720244,
            0.04120513932262154,
        ),
        "calibration_slope_d": (
            1.0412311250013755,
            0.806892759218198,
            1.275569490784553,
        ),
    }
    for metric, values in expected.items():
        row = bootstrap[metric]
        for column, expected_value in zip(
            ("estimate", "ci_low_95", "ci_high_95"),
            values,
        ):
            if not close(row[column], expected_value):
                raise ValueError(f"{metric} {column} changed.")
        if int(row["replicate_n"]) != 500:
            raise ValueError("Stage 4 replicate count changed.")
        if int(row["failed_replicate_n"]) != 0:
            raise ValueError("Stage 4 failed-replicate count changed.")
        if int(row["design_df"]) != 30:
            raise ValueError("Stage 4 design degrees of freedom changed.")

    brier = bootstrap["brier_delta_d_minus_c"]
    auc = bootstrap["auc_delta_d_minus_c"]
    intercept = bootstrap["calibration_intercept_d"]
    slope = bootstrap["calibration_slope_d"]
    independently_positive = all(
        [
            float(brier["ci_high_95"]) < 0,
            float(auc["estimate"]) >= 0,
            float(intercept["ci_low_95"]) <= 0 <= float(
                intercept["ci_high_95"]
            ),
            float(slope["ci_low_95"]) <= 1 <= float(slope["ci_high_95"]),
            all(
                float(row["brier_delta_d_minus_c"]) <= 0
                for row in directions
            ),
        ]
    )
    if independently_positive:
        raise ValueError("Stage 4 positive rule unexpectedly passed.")

    decision = read_csv(
        tables / "18_stage4_positive_extension_decision.csv"
    )
    if len(decision) != 1:
        raise ValueError("Stage 4 decision row count changed.")
    decision_row = decision[0]
    expected_flags = {
        "brier_improvement_supported": False,
        "auc_directionally_nonworse": False,
        "model_d_calibration_intercept_ci_contains_zero": True,
        "model_d_calibration_slope_ci_contains_one": True,
        "both_directions_brier_nonpositive": True,
        "acceleration_shape_stable": True,
        "all_500_bootstrap_replicates_complete": True,
        "positive_explainable_extension_claim": False,
    }
    for key, expected_value in expected_flags.items():
        if parse_bool(decision_row[key]) is not expected_value:
            raise ValueError(f"Stage 4 decision flag changed: {key}")
    if decision_row["result_status"] != "provisional_pending_stage4_review":
        raise ValueError("Source decision status changed.")

    terms = read_csv(tables / "18_stage4_term_importance.csv")
    if len(terms) != 8:
        raise ValueError("Stage 4 term count changed.")
    per_direction_share: dict[str, float] = {}
    seen: set[tuple[str, str]] = set()
    for row in terms:
        feature = row["feature"]
        direction_name = row["direction"]
        if feature not in EXPECTED_FEATURES:
            raise ValueError("Unexpected Stage 4 feature.")
        if int(row["term_feature_count"]) != 1:
            raise ValueError("An interaction term was released.")
        if int(row["term_feature_indices"]) != EXPECTED_FEATURES[feature]:
            raise ValueError("Term index-to-feature mapping changed.")
        if row["term_features"] != feature:
            raise ValueError("Term name mapping changed.")
        if row["interpretation_role"] != (
            "model_diagnostic_not_scientific_effect"
        ):
            raise ValueError("Importance interpretation role changed.")
        seen.add((direction_name, feature))
        per_direction_share[direction_name] = (
            per_direction_share.get(direction_name, 0.0)
            + float(row["importance_share"])
        )
    if seen != {
        (direction_name, feature)
        for direction_name in EXPECTED_DIRECTIONS
        for feature in EXPECTED_FEATURES
    }:
        raise ValueError("Stage 4 term-direction grid changed.")
    if not all(
        abs(value - 1.0) <= 1e-10 for value in per_direction_share.values()
    ):
        raise ValueError("Term importance shares do not sum to one.")

    age = read_csv(tables / "18_stage4_age_shape.csv")
    acceleration = read_csv(tables / "18_stage4_acceleration_shape.csv")
    if len(age) != 242 or len(acceleration) != 202:
        raise ValueError("Stage 4 shape grid dimensions changed.")
    for row in age + acceleration:
        count = int(row["training_bin_unweighted_n"])
        eligible = parse_bool(row["display_eligible"])
        if eligible is not (count >= 30):
            raise ValueError("Shape display-eligibility rule changed.")
        if not math.isfinite(float(row["term_score_log_odds"])):
            raise ValueError("A Stage 4 term score is non-finite.")

    stability = read_csv(tables / "18_stage4_shape_stability.csv")
    if len(stability) != 1:
        raise ValueError("Stage 4 stability row count changed.")
    stability_row = stability[0]
    if not close(
        stability_row["spearman_correlation"],
        0.9806971522079938,
    ):
        raise ValueError("Acceleration shape stability changed.")
    if int(stability_row["common_grid_n"]) != 101:
        raise ValueError("Common acceleration grid count changed.")
    if not parse_bool(stability_row["stable_shape_supported"]):
        raise ValueError("Stable-rank-shape decision changed.")

    runtime = row_map(read_csv(tables / "18_stage4_runtime_versions.csv"), "component")
    if runtime["python_build"]["version"] != EXPECTED_PYTHON_BUILD:
        raise ValueError("Runtime Python build changed.")
    if runtime["r_build"]["version"] != EXPECTED_R_BUILD:
        raise ValueError("Runtime R build changed.")
    if runtime["interpret"]["version"] != "0.7.8":
        raise ValueError("Runtime Interpret version changed.")

    result_checks = read_csv(tables / "18_stage4_release_checks.csv")
    if not result_checks or not all(
        parse_bool(row["pass"]) for row in result_checks
    ):
        raise ValueError("A Stage 4 source result check failed.")

    summary = row_map(
        read_csv(tables / "20_stage4_release_summary.csv"), "component"
    )
    if set(summary) != {
        "brier_delta_d_minus_c",
        "auc_delta_d_minus_c",
        "calibration_intercept_d",
        "calibration_slope_d",
        "acceleration_shape_spearman",
        "positive_explainable_extension_claim",
        "preferred_prediction_model",
        "stage5_synthesis_and_arise",
        "merge_to_main",
    }:
        raise ValueError("Stage 4 release summary changed.")
    if summary["positive_explainable_extension_claim"]["decision"] != (
        "not_authorized"
    ):
        raise ValueError("Positive extension summary changed.")
    if summary["preferred_prediction_model"]["decision"] != "Stage3_Model_C":
        raise ValueError("Preferred model summary changed.")
    if summary["stage5_synthesis_and_arise"]["decision"] != "authorized":
        raise ValueError("Stage 5 summary changed.")
    if summary["merge_to_main"]["decision"] != "not_authorized":
        raise ValueError("Main merge summary changed.")

    combined = "\n".join(
        (docs / name).read_text(encoding="utf-8")
        for name in (
            "V2_Stage4_Human_Review.md",
            "V2_Stage4_Release_Report.md",
            "V2_Analysis_Plan.md",
            "V2_Decision_Log.md",
            "V2_Evidence_Gap_Register.md",
            "V2_Research_Protocol.md",
        )
    ).lower()
    required_phrases = [
        "no positive explainable-extension claim",
        "model c remains the preferred prediction model",
        "rank stability",
        "not exact curve agreement",
        "stage 5",
        "no additional model",
        "merge to `main`",
    ]
    for phrase in required_phrases:
        if phrase not in combined:
            raise ValueError("Stage 4 release guardrail missing: " + phrase)

    for figure in (
        figures / "18_stage4_model_d_incremental_performance.png",
        figures / "18_stage4_cycle_specific_acceleration_shapes.png",
    ):
        if figure.stat().st_size < 1000:
            raise ValueError(f"Stage 4 figure is unexpectedly small: {figure}")

    forbidden = {
        "SEQN",
        "participant_id",
        "prediction",
        "local_contribution",
    }
    for path in tables.glob("18_stage4_*.csv"):
        rows = read_csv(path)
        header = set(rows[0]) if rows else set()
        if forbidden.intersection(header):
            raise ValueError(
                f"Participant-level field found in public output: {path}"
            )

    print("STAGE 4 RELEASE VALIDATION PASSED")
    print("Human review decision: pass, no positive EBM extension.")
    print("Model D did not demonstrate incremental benefit beyond Model C.")
    print("Model C remains the preferred prediction model.")
    print("Global acceleration rank stability may be reported with guardrails.")
    print("Stage 5 synthesis and ARISE preparation are authorized.")
    print("Merge to main remains unauthorized.")


def self_test() -> None:
    assert parse_bool("TRUE") is True
    assert parse_bool("false") is False
    assert close(1.0, 1.0)
    assert not close(1.0, 1.1)
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    validate(args.project_root.resolve())


if __name__ == "__main__":
    main()
