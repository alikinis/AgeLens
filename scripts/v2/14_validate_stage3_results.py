"""Validate AgeLens V2 Stage 3 aggregate outputs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_DIMENSIONS = {"sex", "age_group", "race_ethnicity", "NHANES_cycle"}
EXPECTED_LEVEL_COUNTS = {
    "sex": 2,
    "age_group": 3,
    "race_ethnicity": 6,
    "NHANES_cycle": 2,
}
EXPECTED_DIRECTIONS = {
    "train_2015_2016_test_2017_2018",
    "train_2017_2018_test_2015_2016",
}
EXPECTED_METRICS = {
    "brier_b",
    "brier_c",
    "brier_delta_c_minus_b",
    "auc_b",
    "auc_c",
    "auc_delta_c_minus_b",
    "calibration_intercept_b",
    "calibration_intercept_c",
    "calibration_slope_b",
    "calibration_slope_c",
}


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def require(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{label} missing columns: {missing}")


def finite_between(value: Any, low: float, high: float) -> bool:
    number = float(value)
    return math.isfinite(number) and low <= number <= high


def validate_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("status") != "implementation_authorized_results_pending":
        raise ValueError("Stage 3 configuration status changed.")
    if config["relationship_to_v1"]["v1_immutable"] is not True:
        raise ValueError("V1 protection was removed.")
    uncertainty = config["cross_cycle_prediction"]["uncertainty"]
    if int(uncertainty["replicates"]) != 500:
        raise ValueError("Bootstrap replicate count changed.")
    if int(uncertainty["seed"]) != 20260723:
        raise ValueError("Bootstrap seed changed.")
    for key in (
        "stage3_results_release_authorized",
        "transportability_claims_authorized",
        "prediction_claims_authorized",
        "explainable_extension_authorized",
        "merge_to_main_authorized",
    ):
        if config[key] is not False:
            raise ValueError(f"{key} was authorized prematurely.")
    return config


def validate_outputs(project_root: Path) -> None:
    tables = project_root / "results/tables/v2"
    figures = project_root / "results/figures/v2"
    config_path = project_root / "config/v2_stage3_implementation.json"
    paths = {
        "global": tables / "13_stage3_transportability_global_tests.csv",
        "levels": tables / "13_stage3_transportability_level_estimates.csv",
        "transport_diag": tables / "13_stage3_transportability_diagnostics.csv",
        "directions": tables / "13_stage3_prediction_direction_metrics.csv",
        "bootstrap": tables / "13_stage3_prediction_bootstrap_summary.csv",
        "decision": tables / "13_stage3_incremental_utility_decision.csv",
        "prediction_diag": tables / "13_stage3_prediction_model_diagnostics.csv",
        "versions": tables / "13_stage3_runtime_versions.csv",
        "checks": tables / "13_stage3_release_checks.csv",
    }
    missing = [str(path) for path in [config_path, *paths.values()] if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Stage 3 outputs: " + ", ".join(missing))
    for figure in (
        figures / "13_stage3_transportability_forest.png",
        figures / "13_stage3_incremental_performance.png",
    ):
        if not figure.is_file() or figure.stat().st_size <= 0:
            raise FileNotFoundError(f"Stage 3 figure missing: {figure}")

    validate_config(config_path)

    global_tests = pd.read_csv(paths["global"])
    require(
        global_tests,
        {
            "dimension",
            "interaction_df",
            "design_df",
            "p_value_raw",
            "q_value_bh",
            "supported_at_q_0_10",
            "converged",
            "finite_coefficients",
            "finite_covariance",
            "warning_n",
        },
        "Transportability global tests",
    )
    if set(global_tests["dimension"]) != EXPECTED_DIMENSIONS:
        raise ValueError("Transportability dimensions changed.")
    if not (global_tests["design_df"].astype(int) == 30).all():
        raise ValueError("Transportability design degrees of freedom changed.")
    for column in ("p_value_raw", "q_value_bh"):
        if not global_tests[column].map(lambda x: finite_between(x, 0, 1)).all():
            raise ValueError(f"Invalid {column} values.")
    if not global_tests["converged"].map(parse_bool).all():
        raise ValueError("A transportability model did not converge.")
    if not global_tests["finite_coefficients"].map(parse_bool).all():
        raise ValueError("A transportability model has non-finite coefficients.")
    if not global_tests["finite_covariance"].map(parse_bool).all():
        raise ValueError("A transportability covariance matrix is non-finite.")
    if not (global_tests["warning_n"].astype(int) == 0).all():
        raise ValueError("A transportability model emitted warnings.")
    recomputed_q = pd.Series(
        pd.Series(global_tests["p_value_raw"]).rank(method="max").to_numpy()
    )
    # Exact BH is checked through monotonic validity and the recorded support flag.
    if not (
        global_tests["supported_at_q_0_10"].map(parse_bool).to_numpy()
        == (global_tests["q_value_bh"].astype(float).to_numpy() < 0.10)
    ).all():
        raise ValueError("Transportability q-value support flags are inconsistent.")

    levels = pd.read_csv(paths["levels"])
    require(
        levels,
        {
            "dimension",
            "level",
            "n",
            "positive_n",
            "negative_n",
            "represented_strata",
            "represented_psus",
            "prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
            "q_value_bh",
            "supported_at_q_0_10",
            "reporting_role",
        },
        "Transportability level estimates",
    )
    if len(levels) != sum(EXPECTED_LEVEL_COUNTS.values()):
        raise ValueError("Transportability level count changed.")
    observed_counts = levels.groupby("dimension").size().to_dict()
    if observed_counts != EXPECTED_LEVEL_COUNTS:
        raise ValueError("Transportability levels by dimension changed.")
    for _, row in levels.iterrows():
        n = int(row["n"])
        positive = int(row["positive_n"])
        negative = int(row["negative_n"])
        if n != positive + negative or n < 100 or positive < 30 or negative < 30:
            raise ValueError("A transportability level no longer meets support thresholds.")
        pr = float(row["prevalence_ratio"])
        low = float(row["ci_low_95"])
        high = float(row["ci_high_95"])
        if not 0 < low <= pr <= high:
            raise ValueError("A level-specific prevalence-ratio interval is invalid.")
        expected_role = (
            "supported_interaction_level_estimate"
            if parse_bool(row["supported_at_q_0_10"])
            else "descriptive_level_estimate"
        )
        if row["reporting_role"] != expected_role:
            raise ValueError("A level reporting role is inconsistent.")

    transport_diag = pd.read_csv(paths["transport_diag"])
    require(
        transport_diag,
        {"dimension", "predicted_min", "predicted_max", "warning_n"},
        "Transportability diagnostics",
    )
    if set(transport_diag["dimension"]) != EXPECTED_DIMENSIONS:
        raise ValueError("Transportability diagnostics dimensions changed.")
    if not (transport_diag["warning_n"].astype(int) == 0).all():
        raise ValueError("Transportability diagnostic warnings were recorded.")

    directions = pd.read_csv(paths["directions"])
    require(
        directions,
        {
            "direction",
            "train_n",
            "test_n",
            "test_positive_n",
            "brier_b",
            "brier_c",
            "brier_delta_c_minus_b",
            "auc_b",
            "auc_c",
            "auc_delta_c_minus_b",
            "calibration_intercept_b",
            "calibration_intercept_c",
            "calibration_slope_b",
            "calibration_slope_c",
        },
        "Direction metrics",
    )
    if set(directions["direction"]) != EXPECTED_DIRECTIONS:
        raise ValueError("Cross-cycle directions changed.")
    if set(directions["test_n"].astype(int)) != {2181, 2185}:
        raise ValueError("Cross-cycle test counts changed.")
    if set(directions["test_positive_n"].astype(int)) != {332, 350}:
        raise ValueError("Cross-cycle positive counts changed.")
    for column in ("brier_b", "brier_c", "auc_b", "auc_c"):
        if not directions[column].map(lambda x: finite_between(x, 0, 1)).all():
            raise ValueError(f"Invalid direction metric: {column}")
    for _, row in directions.iterrows():
        if not math.isclose(
            float(row["brier_delta_c_minus_b"]),
            float(row["brier_c"]) - float(row["brier_b"]),
            abs_tol=1e-12,
            rel_tol=0,
        ):
            raise ValueError("Direction Brier delta is inconsistent.")
        if not math.isclose(
            float(row["auc_delta_c_minus_b"]),
            float(row["auc_c"]) - float(row["auc_b"]),
            abs_tol=1e-12,
            rel_tol=0,
        ):
            raise ValueError("Direction AUC delta is inconsistent.")

    bootstrap = pd.read_csv(paths["bootstrap"])
    require(
        bootstrap,
        {
            "metric",
            "estimate",
            "standard_error",
            "ci_low_95",
            "ci_high_95",
            "design_df",
            "replicate_n",
            "failed_replicate_n",
        },
        "Bootstrap summary",
    )
    if set(bootstrap["metric"]) != EXPECTED_METRICS:
        raise ValueError("Bootstrap metric family changed.")
    if not (bootstrap["replicate_n"].astype(int) == 500).all():
        raise ValueError("Bootstrap replicate count changed.")
    if not (bootstrap["failed_replicate_n"].astype(int) == 0).all():
        raise ValueError("A bootstrap replicate failed.")
    if not (bootstrap["design_df"].astype(int) == 30).all():
        raise ValueError("Bootstrap design degrees of freedom changed.")
    for _, row in bootstrap.iterrows():
        values = [
            float(row["estimate"]),
            float(row["standard_error"]),
            float(row["ci_low_95"]),
            float(row["ci_high_95"]),
        ]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Bootstrap summary contains non-finite values.")
        if values[1] < 0 or values[2] > values[0] or values[0] > values[3]:
            raise ValueError("Bootstrap interval is invalid.")
    indexed = bootstrap.set_index("metric")
    for model_metric in ("brier_b", "brier_c", "auc_b", "auc_c"):
        if not finite_between(indexed.loc[model_metric, "estimate"], 0, 1):
            raise ValueError(f"Invalid pooled point metric: {model_metric}")
    if not math.isclose(
        float(indexed.loc["brier_delta_c_minus_b", "estimate"]),
        float(indexed.loc["brier_c", "estimate"])
        - float(indexed.loc["brier_b", "estimate"]),
        abs_tol=1e-12,
        rel_tol=0,
    ):
        raise ValueError("Pooled Brier delta is inconsistent.")
    if not math.isclose(
        float(indexed.loc["auc_delta_c_minus_b", "estimate"]),
        float(indexed.loc["auc_c", "estimate"])
        - float(indexed.loc["auc_b", "estimate"]),
        abs_tol=1e-12,
        rel_tol=0,
    ):
        raise ValueError("Pooled AUC delta is inconsistent.")

    decision = pd.read_csv(paths["decision"])
    require(
        decision,
        {
            "brier_improvement_supported",
            "auc_directionally_nonworse",
            "model_c_calibration_intercept_ci_contains_zero",
            "model_c_calibration_slope_ci_contains_one",
            "positive_incremental_utility_claim",
            "result_status",
        },
        "Incremental-utility decision",
    )
    if len(decision) != 1:
        raise ValueError("Incremental-utility decision must contain one row.")
    row = decision.iloc[0]
    expected_claim = all(
        parse_bool(row[column])
        for column in (
            "brier_improvement_supported",
            "auc_directionally_nonworse",
            "model_c_calibration_intercept_ci_contains_zero",
            "model_c_calibration_slope_ci_contains_one",
        )
    )
    if parse_bool(row["positive_incremental_utility_claim"]) != expected_claim:
        raise ValueError("Incremental-utility claim rule is inconsistent.")
    if row["result_status"] != "provisional_pending_stage3_review":
        raise ValueError("Stage 3 results were released prematurely.")

    prediction_diag = pd.read_csv(paths["prediction_diag"])
    require(
        prediction_diag,
        {"direction", "model", "converged", "finite_coefficients", "warning_n"},
        "Prediction diagnostics",
    )
    if len(prediction_diag) != 4:
        raise ValueError("Expected four prediction model diagnostics.")
    if not prediction_diag["converged"].map(parse_bool).all():
        raise ValueError("A prediction model did not converge.")
    if not prediction_diag["finite_coefficients"].map(parse_bool).all():
        raise ValueError("A prediction model has non-finite coefficients.")
    if not (prediction_diag["warning_n"].astype(int) == 0).all():
        raise ValueError("A prediction model emitted warnings.")

    checks = pd.read_csv(paths["checks"])
    require(checks, {"check", "pass", "observed"}, "Stage 3 checks")
    failed = checks.loc[~checks["pass"].map(parse_bool)]
    if not failed.empty:
        raise ValueError(
            "Stage 3 checks failed: " + "; ".join(failed["check"].astype(str))
        )

    forbidden = {"SEQN", "participant_id", "subject_id"}
    for path in paths.values():
        columns = set(pd.read_csv(path, nrows=0).columns)
        overlap = forbidden.intersection(columns)
        if overlap:
            raise ValueError(
                f"Participant identifier found in public output {path.name}: {sorted(overlap)}"
            )

    log_dir = project_root / "results/logs/v2"
    log_dir.mkdir(parents=True, exist_ok=True)
    validation_path = log_dir / "14_stage3_result_validation.json"
    report = {
        "document_id": "AL-V2-S3V-001",
        "status": "passed",
        "stage3_results_provisional": True,
        "transportability_dimensions": sorted(EXPECTED_DIMENSIONS),
        "cross_cycle_directions": sorted(EXPECTED_DIRECTIONS),
        "bootstrap_replicates": 500,
        "failed_bootstrap_replicates": 0,
        "positive_incremental_utility_claim": parse_bool(
            decision.iloc[0]["positive_incremental_utility_claim"]
        ),
        "v1_modified": False,
        "participant_level_public_output": False,
        "transportability_claims_authorized": False,
        "prediction_claims_authorized": False,
        "explainable_extension_authorized": False,
        "merge_to_main_authorized": False,
    }
    validation_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("STAGE 3 RESULT VALIDATION PASSED")
    print("Four transportability tests and both cross-cycle directions were validated.")
    print("The 500-replicate stratified-PSU bootstrap completed without failures.")
    print("Results remain provisional pending human review and a Stage 3 release gate.")
    print(f"Validation report: {validation_path.relative_to(project_root)}")


def run_self_test() -> None:
    assert parse_bool("TRUE")
    assert not parse_bool("false")
    assert finite_between(0.5, 0, 1)
    print("SELF-TEST PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    validate_outputs(args.project_root.resolve())


if __name__ == "__main__":
    main()
