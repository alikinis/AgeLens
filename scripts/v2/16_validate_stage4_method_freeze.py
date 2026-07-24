"""Validate the frozen AgeLens V2 Stage 4 method selection."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_FEATURES = [
    "chronological_age_years",
    "sex",
    "race_ethnicity",
    "phenoage_acceleration_per_5_years",
]
EXPECTED_TYPES = ["continuous", "nominal", "nominal", "continuous"]
EXPECTED_DIRECTIONS = [
    "train_2015_2016_test_2017_2018",
    "train_2017_2018_test_2015_2016",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate(project_root: Path) -> None:
    config_path = project_root / "config/v2_stage4_method_freeze.json"
    stage3_path = project_root / "config/v2_stage3_release.json"
    matrix_path = (
        project_root
        / "results/tables/v2/16_stage4_method_selection_matrix.csv"
    )
    docs = project_root / "docs/v2"

    required = [
        config_path,
        stage3_path,
        matrix_path,
        docs / "V2_Stage4_Method_Selection.md",
        docs / "V2_Stage4_Method_Freeze_Report.md",
        docs / "README.md",
        docs / "V2_Analysis_Plan.md",
        docs / "V2_Decision_Log.md",
        docs / "V2_Evidence_Gap_Register.md",
        docs / "V2_Research_Protocol.md",
        project_root / "results/tables/v2/15_stage3_release_summary.csv",
        project_root / "scripts/v2/15_validate_stage3_release.py",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing Stage 4 freeze dependencies: " + ", ".join(missing)
        )

    stage3 = load_json(stage3_path)
    if stage3.get("status") != "released_for_v2_development":
        raise ValueError("Stage 3 is not released.")
    if stage3.get("human_review_decision") != "pass_with_guardrails":
        raise ValueError("Stage 3 human-review decision changed.")
    if not stage3["permissions"]["stage4_method_selection_authorized"]:
        raise ValueError("Stage 4 method selection is not authorized.")
    if stage3["permissions"]["merge_to_main_authorized"]:
        raise ValueError("Stage 3 unexpectedly authorized merge to main.")

    config = load_json(config_path)
    if config.get("status") != "frozen_implementation_authorized":
        raise ValueError("Stage 4 freeze status changed.")
    if not config["relationship_to_v1"]["v1_immutable"]:
        raise ValueError("V1 immutability was removed.")

    method = config["selected_method"]
    if method["python_class"] != (
        "interpret.glassbox.ExplainableBoostingClassifier"
    ):
        raise ValueError("Selected Stage 4 method changed.")
    if method["package_version_pin"] != "0.7.8":
        raise ValueError("InterpretML version pin changed.")
    if int(method["interactions"]) != 0:
        raise ValueError("Stage 4 method contains interactions.")
    if method["automatic_interaction_selection"]:
        raise ValueError("Automatic interaction selection was enabled.")
    if method["post_hoc_explainer"]:
        raise ValueError("A post-hoc explainer was enabled.")

    predictors = config["frozen_predictors"]
    if predictors["features_in_order"] != EXPECTED_FEATURES:
        raise ValueError("Frozen predictor set or order changed.")
    if predictors["feature_types_in_order"] != EXPECTED_TYPES:
        raise ValueError("Frozen feature types changed.")
    forbidden_true = [
        "new_biomarkers_authorized",
        "NHANES_cycle_predictor_authorized",
        "participant_identifier_predictor_authorized",
        "outcome_derived_predictor_authorized",
        "missing_feature_values_allowed",
    ]
    for key in forbidden_true:
        if predictors[key]:
            raise ValueError(f"Forbidden predictor permission enabled: {key}")

    hyper = config["frozen_hyperparameters"]
    expected_hyper = {
        "max_bins": 32,
        "interactions": 0,
        "validation_size": 0.15,
        "outer_bags": 8,
        "learning_rate": 0.015,
        "greedy_ratio": 0.0,
        "max_rounds": 10000,
        "early_stopping_rounds": 100,
        "min_samples_leaf": 20,
        "gain_scale": 1.0,
        "min_cat_samples": 20,
        "cat_smooth": 20.0,
        "max_leaves": 2,
        "n_jobs": 1,
        "random_state": 20260724,
    }
    for key, expected in expected_hyper.items():
        if hyper[key] != expected:
            raise ValueError(
                f"Frozen hyperparameter changed: {key}={hyper[key]!r}"
            )
    if hyper["hyperparameter_search_authorized"]:
        raise ValueError("Hyperparameter search was authorized.")

    validation = config["validation"]
    if validation["directions"] != EXPECTED_DIRECTIONS:
        raise ValueError("Cross-cycle directions changed.")
    if validation["primary_comparator"] != "Stage3_Model_C":
        raise ValueError("Primary comparator changed.")
    if validation["primary_metric"] != (
        "pooled_weighted_Brier_delta_D_minus_C"
    ):
        raise ValueError("Primary metric changed.")
    if validation["test_cycle_used_for_training_or_binning"]:
        raise ValueError("Test-cycle leakage was authorized.")
    if validation["participant_random_split_for_performance"]:
        raise ValueError("Participant random performance split was enabled.")
    uncertainty = validation["uncertainty"]
    if int(uncertainty["replicates"]) != 500:
        raise ValueError("Bootstrap replicate count changed.")
    if not uncertainty[
        "refit_model_c_and_model_d_each_direction_each_replicate"
    ]:
        raise ValueError("Bootstrap refit rule changed.")
    if uncertainty["failed_replicate_policy"] != "stop_release":
        raise ValueError("Failed-replicate policy changed.")

    claim = config["positive_extension_claim_rule"]
    if not claim["all_conditions_required"]:
        raise ValueError("Joint positive-claim rule was weakened.")
    if float(
        claim["acceleration_shape_stability_spearman_at_least"]
    ) != 0.70:
        raise ValueError("Shape-stability threshold changed.")
    required_claim_flags = [
        "pooled_Brier_delta_D_minus_C_ci_high_below_zero",
        "pooled_AUC_delta_D_minus_C_point_nonnegative",
        "model_d_calibration_intercept_ci_contains_zero",
        "model_d_calibration_slope_ci_contains_one",
        "both_direction_specific_Brier_delta_D_minus_C_nonpositive",
        "all_500_bootstrap_replicates_complete",
        "no_positive_claim_if_rule_fails",
    ]
    for key in required_claim_flags:
        if not claim[key]:
            raise ValueError(f"Positive-claim condition disabled: {key}")

    explanation = config["explanation_governance"]
    if not explanation["global_explanations_authorized"]:
        raise ValueError("Global explanations were disabled.")
    if explanation["local_explanations_authorized"]:
        raise ValueError("Local explanations were authorized.")
    if explanation["participant_level_contributions_public"]:
        raise ValueError("Participant-level contributions were authorized.")
    if not explanation["main_effect_terms_only"]:
        raise ValueError("Main-effects-only rule was removed.")
    for key in (
        "no_threshold_claim",
        "no_causal_feature_claim",
        "no_biological_race_claim",
        "no_feature_importance_rank_as_scientific_effect",
    ):
        if not explanation[key]:
            raise ValueError(f"Explanation guardrail disabled: {key}")

    permissions = config["permissions"]
    if not permissions["stage4_implementation_authorized"]:
        raise ValueError("Frozen Stage 4 implementation is not authorized.")
    forbidden_permissions = [
        "stage4_results_claims_authorized",
        "local_explanation_release_authorized",
        "new_feature_expansion_authorized",
        "hyperparameter_search_authorized",
        "merge_to_main_authorized",
        "final_manuscript_claims_authorized",
    ]
    for key in forbidden_permissions:
        if permissions[key]:
            raise ValueError(f"Premature permission enabled: {key}")

    matrix = read_csv(matrix_path)
    selected = [row for row in matrix if parse_bool(row["selected"])]
    if len(selected) != 1:
        raise ValueError("Method matrix must select exactly one candidate.")
    if selected[0]["candidate"] != (
        "Explainable Boosting Machine main effects only"
    ):
        raise ValueError("Method matrix selection changed.")
    if parse_bool(selected[0]["automatic_interactions"]):
        raise ValueError("Selected method matrix row enables interactions.")

    combined = "\n".join(
        (docs / name).read_text(encoding="utf-8")
        for name in (
            "V2_Stage4_Method_Selection.md",
            "V2_Stage4_Method_Freeze_Report.md",
            "V2_Analysis_Plan.md",
            "V2_Research_Protocol.md",
        )
    ).lower()
    required_phrases = [
        "main effects only",
        "same four predictors",
        "no hyperparameter search",
        "local explanations",
        "500 stratified-psu bootstrap",
        "model d minus model c",
        "separate stage 4 review and release",
    ]
    for phrase in required_phrases:
        if phrase not in combined:
            raise ValueError(f"Stage 4 guardrail missing: {phrase}")

    print("STAGE 4 METHOD FREEZE VALIDATION PASSED")
    print("Selected method: main-effects Explainable Boosting Machine.")
    print("Predictor set: identical to Stage 3 Model C.")
    print("Interactions and hyperparameter search: prohibited.")
    print("Stage 4 implementation is authorized after commit.")
    print("Stage 4 scientific claims and merge to main remain unauthorized.")


def self_test() -> None:
    assert parse_bool("true") is True
    assert parse_bool("False") is False
    assert EXPECTED_FEATURES[-1] == "phenoage_acceleration_per_5_years"
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    validate(args.project_root.resolve())


if __name__ == "__main__":
    main()
