"""Validate provisional AgeLens V2 Stage 4 EBM results."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any


EXPECTED_INTERPRET_VERSION = "0.7.8"
EXPECTED_FEATURES = {
    "chronological_age_years",
    "sex",
    "race_ethnicity",
    "phenoage_acceleration_per_5_years",
}
EXPECTED_DIRECTIONS = {
    "train_2015_2016_test_2017_2018",
    "train_2017_2018_test_2015_2016",
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


def finite(value: Any) -> bool:
    return math.isfinite(float(value))


def parse_term_indices(value: Any) -> tuple[int, ...]:
    text = str(value).strip()
    if not text:
        raise ValueError("A Stage 4 term has no feature index.")
    try:
        indices = tuple(int(part) for part in text.split("|"))
    except ValueError as exc:
        raise ValueError(
            f"Invalid Stage 4 term feature indices: {value!r}"
        ) from exc
    if len(set(indices)) != len(indices):
        raise ValueError("A Stage 4 term repeats a feature index.")
    return indices


def validate(project_root: Path) -> None:
    tables = project_root / "results/tables/v2"
    figures = project_root / "results/figures/v2"
    required = [
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
        figures / "18_stage4_model_d_incremental_performance.png",
        figures / "18_stage4_cycle_specific_acceleration_shapes.png",
        project_root / "config/v2_stage4_method_freeze.json",
        project_root / "config/v2_stage4_implementation.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Stage 4 artifacts: " + ", ".join(missing))

    audit = read_csv(tables / "18_stage4_method_input_audit.csv")
    if not audit or not all(parse_bool(row["pass"]) for row in audit):
        raise ValueError("A Stage 4 input audit failed.")
    audit_map = {row["check"]: row for row in audit}
    if int(float(audit_map["primary_domain_n"]["observed"])) != 4366:
        raise ValueError("Stage 4 primary n changed.")
    if int(float(audit_map["primary_positive_n"]["observed"])) != 682:
        raise ValueError("Stage 4 positive n changed.")
    if audit_map["interpret_exact_version"]["observed"] != EXPECTED_INTERPRET_VERSION:
        raise ValueError("Interpret exact version changed.")
    if float(audit_map["model_c_max_abs_reconciliation"]["observed"]) > 1e-7:
        raise ValueError("Model C reconciliation exceeded tolerance.")

    directions = read_csv(tables / "18_stage4_direction_metrics.csv")
    if set(row["direction"] for row in directions) != EXPECTED_DIRECTIONS:
        raise ValueError("Stage 4 directions changed.")
    numeric_direction = [
        "brier_b", "brier_c", "brier_d",
        "brier_delta_d_minus_c", "auc_b", "auc_c", "auc_d",
        "auc_delta_d_minus_c", "calibration_intercept_d",
        "calibration_slope_d",
    ]
    for row in directions:
        if row["result_status"] != "provisional_pending_stage4_review":
            raise ValueError("A direction result was released prematurely.")
        if not all(finite(row[column]) for column in numeric_direction):
            raise ValueError("A direction metric is non-finite.")

    bootstrap = read_csv(tables / "18_stage4_bootstrap_summary.csv")
    expected_metrics = {
        "brier_c", "brier_d", "brier_delta_d_minus_c",
        "auc_c", "auc_d", "auc_delta_d_minus_c",
        "calibration_intercept_d", "calibration_slope_d",
        "brier_delta_d_minus_c_train_2015_2016_test_2017_2018",
        "auc_delta_d_minus_c_train_2015_2016_test_2017_2018",
        "brier_delta_d_minus_c_train_2017_2018_test_2015_2016",
        "auc_delta_d_minus_c_train_2017_2018_test_2015_2016",
    }
    if set(row["metric"] for row in bootstrap) != expected_metrics:
        raise ValueError("Stage 4 bootstrap metrics changed.")
    for row in bootstrap:
        if int(row["replicate_n"]) != 500 or int(row["failed_replicate_n"]) != 0:
            raise ValueError("Stage 4 bootstrap did not complete 500/500.")
        if int(row["design_df"]) != 30:
            raise ValueError("Stage 4 design degrees of freedom changed.")
        if not all(finite(row[column]) for column in (
            "estimate", "standard_error", "ci_low_95", "ci_high_95"
        )):
            raise ValueError("A Stage 4 bootstrap result is non-finite.")

    decision = read_csv(tables / "18_stage4_positive_extension_decision.csv")
    if len(decision) != 1:
        raise ValueError("Stage 4 decision row count changed.")
    decision_row = decision[0]
    if decision_row["result_status"] != "provisional_pending_stage4_review":
        raise ValueError("Stage 4 decision was released prematurely.")
    required_decision_fields = [
        "brier_improvement_supported",
        "auc_directionally_nonworse",
        "model_d_calibration_intercept_ci_contains_zero",
        "model_d_calibration_slope_ci_contains_one",
        "both_directions_brier_nonpositive",
        "acceleration_shape_stable",
        "all_500_bootstrap_replicates_complete",
        "positive_explainable_extension_claim",
    ]
    for field in required_decision_fields:
        parse_bool(decision_row[field])

    importance = read_csv(tables / "18_stage4_term_importance.csv")
    if len(importance) != 8:
        raise ValueError("Stage 4 term-importance row count changed.")
    if set(row["feature"] for row in importance) != EXPECTED_FEATURES:
        raise ValueError("Stage 4 term set changed.")
    if set(row["direction"] for row in importance) != EXPECTED_DIRECTIONS:
        raise ValueError("Stage 4 term directions changed.")
    feature_index = {
        "chronological_age_years": 0,
        "sex": 1,
        "race_ethnicity": 2,
        "phenoage_acceleration_per_5_years": 3,
    }
    for row in importance:
        indices = parse_term_indices(row["term_feature_indices"])
        if int(row["term_feature_count"]) != len(indices):
            raise ValueError("Stage 4 term feature count is inconsistent.")
        if len(indices) != 1:
            raise ValueError("An interaction term was released.")
        if indices[0] != feature_index[row["feature"]]:
            raise ValueError("Stage 4 term index-to-feature mapping changed.")
        if row["term_features"] != row["feature"]:
            raise ValueError("Stage 4 term name-to-feature mapping changed.")
        if row["interpretation_role"] != "model_diagnostic_not_scientific_effect":
            raise ValueError("Term importance interpretation role changed.")
        if not finite(row["importance_avg_weight"]):
            raise ValueError("A term importance is non-finite.")

    age = read_csv(tables / "18_stage4_age_shape.csv")
    acceleration = read_csv(tables / "18_stage4_acceleration_shape.csv")
    if len(age) != 242 or len(acceleration) != 202:
        raise ValueError("Stage 4 shape grid dimensions changed.")
    for rows, score_column in (
        (age, "term_score_log_odds"),
        (acceleration, "term_score_log_odds"),
    ):
        if set(row["direction"] for row in rows) != EXPECTED_DIRECTIONS:
            raise ValueError("Stage 4 shape directions changed.")
        if not all(finite(row[score_column]) for row in rows):
            raise ValueError("A Stage 4 shape score is non-finite.")
        if not any(parse_bool(row["display_eligible"]) for row in rows):
            raise ValueError("No Stage 4 shape point is display eligible.")

    stability = read_csv(tables / "18_stage4_shape_stability.csv")
    if len(stability) != 1 or not finite(stability[0]["spearman_correlation"]):
        raise ValueError("Stage 4 shape stability is invalid.")
    if int(stability[0]["common_grid_n"]) < 25:
        raise ValueError("Too few eligible common shape points.")
    if float(stability[0]["minimum_required"]) != 0.70:
        raise ValueError("Shape-stability threshold changed.")

    versions = read_csv(tables / "18_stage4_runtime_versions.csv")
    version_map = {row["component"]: row["version"] for row in versions}
    if version_map.get("python_build") != "AgeLens-V2-Stage4-Python-20260724c":
        raise ValueError("Stage 4 Python build changed.")
    if version_map.get("r_build") != "AgeLens-V2-Stage4-R-20260724b":
        raise ValueError("Stage 4 R build changed.")
    if version_map.get("interpret") != EXPECTED_INTERPRET_VERSION:
        raise ValueError("Runtime interpret version changed.")

    checks = read_csv(tables / "18_stage4_release_checks.csv")
    if not checks or not all(parse_bool(row["pass"]) for row in checks):
        failed = [row["check"] for row in checks if not parse_bool(row["pass"])]
        raise ValueError("Stage 4 release checks failed: " + "; ".join(failed))

    forbidden = {"SEQN", "participant_id", "prediction", "local_contribution"}
    for path in tables.glob("18_stage4_*.csv"):
        header = set(read_csv(path)[0]) if read_csv(path) else set()
        if forbidden.intersection(header):
            raise ValueError(f"Participant-level field found in public output: {path}")

    print("STAGE 4 RESULT VALIDATION PASSED")
    print("Frozen main-effects EBM and both cross-cycle directions were validated.")
    print("All 500 PSU-bootstrap replicates completed without failures.")
    print("Only aggregate global explanation outputs were written.")
    print("Results remain provisional pending Stage 4 human review and release gate.")


def self_test() -> None:
    assert parse_bool("TRUE") is True
    assert parse_bool("false") is False
    assert finite("0.5") is True
    assert parse_term_indices("0") == (0,)
    assert parse_term_indices("1|3") == (1, 3)
    # A Python singleton tuple string contains a comma, but public term
    # validation no longer uses punctuation as an interaction detector.
    assert "," in str((0,))
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    validate(args.project_root.resolve())


if __name__ == "__main__":
    main()
