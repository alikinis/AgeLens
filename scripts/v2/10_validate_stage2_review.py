"""Validate AgeLens V2 Stage 2 diagnostic-review outputs."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import pandas as pd


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


def run_validation(project_root: Path) -> None:
    tables = project_root / "results/tables/v2"
    figure = (
        project_root
        / "results/figures/v2/09_stage2_adjusted_prevalence_curve.png"
    )
    paths = {
        "quantiles": tables / "09_stage2_acceleration_quantiles.csv",
        "bounds": tables / "09_stage2_prediction_bound_audit.csv",
        "trimmed": tables / "09_stage2_trimmed_linear_sensitivity.csv",
        "curve": tables / "09_stage2_adjusted_prevalence_curve.csv",
        "local": tables / "09_stage2_local_five_year_ratios.csv",
        "nonlinearity": tables / "09_stage2_nonlinearity_review.csv",
        "checks": tables / "09_stage2_review_checks.csv",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing review outputs: " + ", ".join(missing))
    if not figure.is_file() or figure.stat().st_size <= 0:
        raise FileNotFoundError("Adjusted-prevalence figure is missing.")

    quantiles = pd.read_csv(paths["quantiles"])
    require(
        quantiles,
        {"probability", "percentile", "acceleration_years"},
        "Quantiles",
    )
    if len(quantiles) != 11:
        raise ValueError("Expected 11 weighted acceleration quantiles.")
    acceleration = pd.to_numeric(
        quantiles["acceleration_years"],
        errors="raise",
    )
    if not acceleration.is_monotonic_increasing:
        raise ValueError("Acceleration quantiles are not ordered.")

    bounds = pd.read_csv(paths["bounds"])
    require(
        bounds,
        {
            "outcome",
            "n",
            "predicted_above_one_n",
            "predicted_above_one_weighted_percent",
            "predicted_max",
        },
        "Prediction-bound audit",
    )
    expected = {
        "mobility_disability": 6,
        "any_disability_six": 20,
        "fair_poor_general_health": 12,
        "phq9_ge10": 2,
    }
    if set(bounds["outcome"]) != set(expected):
        raise ValueError("Prediction-bound outcome family changed.")
    indexed = bounds.set_index("outcome")
    for outcome, expected_count in expected.items():
        if int(indexed.loc[outcome, "predicted_above_one_n"]) != expected_count:
            raise ValueError(f"{outcome} fitted-above-one count changed.")
        maximum = float(indexed.loc[outcome, "predicted_max"])
        if not math.isfinite(maximum) or maximum <= 0:
            raise ValueError(f"{outcome} fitted maximum is invalid.")

    trimmed = pd.read_csv(paths["trimmed"])
    require(
        trimmed,
        {
            "sensitivity",
            "n",
            "positive_n",
            "prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
            "p_value",
            "predicted_above_one_n",
        },
        "Trimmed sensitivity",
    )
    if set(trimmed["sensitivity"]) != {
        "full",
        "weighted_1_to_99_percent",
        "weighted_2.5_to_97.5_percent",
    }:
        raise ValueError("Trimmed sensitivity family changed.")
    full = trimmed.set_index("sensitivity").loc["full"]
    if int(full["n"]) != 4366 or int(full["positive_n"]) != 682:
        raise ValueError("Full primary sensitivity counts changed.")
    if not math.isclose(
        float(full["prevalence_ratio"]),
        1.1475644343644,
        abs_tol=1e-10,
        rel_tol=0,
    ):
        raise ValueError("Full primary prevalence ratio did not reproduce.")
    for _, row in trimmed.iterrows():
        values = [
            float(row["prevalence_ratio"]),
            float(row["ci_low_95"]),
            float(row["ci_high_95"]),
            float(row["p_value"]),
        ]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Trimmed sensitivity contains non-finite values.")
        if not 0 < values[1] <= values[0] <= values[2]:
            raise ValueError("Trimmed confidence interval is invalid.")
        if not 0 <= values[3] <= 1:
            raise ValueError("Trimmed p-value is invalid.")

    curve = pd.read_csv(paths["curve"])
    require(
        curve,
        {
            "acceleration_years",
            "adjusted_prevalence",
            "ci_low_95",
            "ci_high_95",
        },
        "Adjusted-prevalence curve",
    )
    if len(curve) < 40:
        raise ValueError("Adjusted-prevalence curve is too sparse.")
    for _, row in curve.iterrows():
        prevalence = float(row["adjusted_prevalence"])
        low = float(row["ci_low_95"])
        high = float(row["ci_high_95"])
        if not (0 < low <= prevalence <= high < 1):
            raise ValueError("Curve contains an invalid probability interval.")
    if not pd.to_numeric(
        curve["acceleration_years"],
        errors="raise",
    ).is_monotonic_increasing:
        raise ValueError("Curve acceleration grid is not ordered.")

    local = pd.read_csv(paths["local"])
    require(
        local,
        {
            "anchor_percentile",
            "start_acceleration_years",
            "end_acceleration_years",
            "local_five_year_prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
        },
        "Local ratios",
    )
    if len(local) != 5:
        raise ValueError("Expected five local five-year ratios.")
    for _, row in local.iterrows():
        ratio = float(row["local_five_year_prevalence_ratio"])
        low = float(row["ci_low_95"])
        high = float(row["ci_high_95"])
        if not 0 < low <= ratio <= high:
            raise ValueError("Local ratio interval is invalid.")

    nonlinearity = pd.read_csv(paths["nonlinearity"])
    require(
        nonlinearity,
        {
            "prespecified_quasipoisson_nonlinearity_p",
            "logistic_spline_nonlinearity_p",
            "linear_primary_result_retained",
            "linear_primary_result_released",
        },
        "Nonlinearity review",
    )
    if len(nonlinearity) != 1:
        raise ValueError("Nonlinearity review must contain one row.")
    row = nonlinearity.iloc[0]
    for column in (
        "prespecified_quasipoisson_nonlinearity_p",
        "logistic_spline_nonlinearity_p",
    ):
        value = float(row[column])
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{column} is invalid.")
    if not parse_bool(row["linear_primary_result_retained"]):
        raise ValueError("Prespecified primary result was not retained.")
    if parse_bool(row["linear_primary_result_released"]):
        raise ValueError("Prespecified primary result was released prematurely.")

    checks = pd.read_csv(paths["checks"])
    require(checks, {"check", "pass", "observed"}, "Review checks")
    failed = checks.loc[~checks["pass"].map(parse_bool)]
    if not failed.empty:
        raise ValueError(
            "Review checks failed: "
            + "; ".join(failed["check"].astype(str))
        )

    for path in paths.values():
        header = pd.read_csv(path, nrows=0)
        forbidden = {"SEQN", "participant_id", "subject_id"}
        if forbidden.intersection(header.columns):
            raise ValueError(
                f"Participant identifier found in public output: {path.name}"
            )

    print("STAGE 2 DIAGNOSTIC REVIEW VALIDATION PASSED")
    print(
        "The original linear PR remains provisional; "
        "the bounded nonlinear curve is diagnostic."
    )
    print(f"Figure: {figure.relative_to(project_root)}")


def run_self_test() -> None:
    assert parse_bool("TRUE")
    assert not parse_bool("false")
    print("SELF-TEST PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    run_validation(args.project_root.resolve())


if __name__ == "__main__":
    main()
