"""Validate and record the governed AgeLens V2 Stage 2 release."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


PRIMARY_EXPECTED = {
    "n": 4366,
    "positive_n": 682,
    "prevalence_ratio": 1.1475644343644,
    "ci_low_95": 1.09984405187883,
    "ci_high_95": 1.19735532393747,
    "p_value": 2.51174370794198e-07,
}

SECONDARY_EXPECTED = {
    "any_disability_six": {
        "prevalence_ratio": 1.11175768051483,
        "ci_low_95": 1.07313632544011,
        "ci_high_95": 1.15176898860152,
        "p_value_holm": 1.99805939253673e-06,
    },
    "fair_poor_general_health": {
        "prevalence_ratio": 1.16412825764386,
        "ci_low_95": 1.12929810066504,
        "ci_high_95": 1.20003265696351,
        "p_value_holm": 8.29600602077229e-11,
    },
    "phq9_ge10": {
        "prevalence_ratio": 1.15955044738036,
        "ci_low_95": 1.10191745564465,
        "ci_high_95": 1.22019778626104,
        "p_value_holm": 1.99805939253673e-06,
    },
}

ABS_TOL = 1e-10


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def close(actual: float, expected: float, tolerance: float = ABS_TOL) -> bool:
    return math.isclose(
        float(actual),
        float(expected),
        abs_tol=tolerance,
        rel_tol=0,
    )


def require_columns(
    frame: pd.DataFrame,
    columns: set[str],
    label: str,
) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{label} missing columns: {missing}")


def validate_primary(path: Path) -> pd.Series:
    frame = pd.read_csv(path)
    require_columns(
        frame,
        {
            "outcome",
            "n",
            "positive_n",
            "prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
            "p_value",
            "interpretation",
        },
        "Primary result",
    )
    if len(frame) != 1:
        raise ValueError("Primary result must contain exactly one row.")
    row = frame.iloc[0]
    if row["outcome"] != "mobility_disability":
        raise ValueError("Primary outcome changed.")
    for column, expected in PRIMARY_EXPECTED.items():
        if column in {"n", "positive_n"}:
            if int(row[column]) != int(expected):
                raise ValueError(f"Primary {column} changed.")
        elif not close(float(row[column]), expected):
            raise ValueError(f"Primary {column} changed.")
    if row["interpretation"] != "associational_not_causal":
        raise ValueError("Primary causal guardrail changed.")
    return row


def validate_secondary(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    require_columns(
        frame,
        {
            "outcome",
            "prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
            "p_value_holm",
        },
        "Secondary results",
    )
    if set(frame["outcome"]) != set(SECONDARY_EXPECTED):
        raise ValueError("Secondary outcome family changed.")
    indexed = frame.set_index("outcome")
    for outcome, expected_values in SECONDARY_EXPECTED.items():
        row = indexed.loc[outcome]
        for column, expected in expected_values.items():
            if not close(float(row[column]), expected):
                raise ValueError(
                    f"{outcome} {column} changed."
                )
        if float(row["p_value_holm"]) >= 0.05:
            raise ValueError(
                f"{outcome} is not significant after Holm adjustment."
            )
    return frame


def validate_review(
    tables: Path,
    figure: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    nonlinearity = pd.read_csv(
        tables / "09_stage2_nonlinearity_review.csv"
    )
    require_columns(
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
    quasi_p = float(row["prespecified_quasipoisson_nonlinearity_p"])
    logistic_p = float(row["logistic_spline_nonlinearity_p"])
    if not close(quasi_p, 0.000176974908863395):
        raise ValueError("Quasi-Poisson nonlinearity p-value changed.")
    if not close(logistic_p, 0.000916263045884809):
        raise ValueError("Logistic spline nonlinearity p-value changed.")
    if quasi_p >= 0.01 or logistic_p >= 0.01:
        raise ValueError("Nonlinearity evidence no longer meets release rule.")
    if not parse_bool(row["linear_primary_result_retained"]):
        raise ValueError("Prespecified linear result was not retained.")
    if parse_bool(row["linear_primary_result_released"]):
        raise ValueError(
            "Diagnostic file indicates premature release."
        )

    bounds = pd.read_csv(
        tables / "09_stage2_prediction_bound_audit.csv"
    )
    require_columns(
        bounds,
        {
            "outcome",
            "predicted_above_one_n",
            "predicted_above_one_weighted_percent",
            "predicted_max",
            "flagged_acceleration_min",
        },
        "Prediction-bound audit",
    )
    primary_bounds = bounds.loc[
        bounds["outcome"].eq("mobility_disability")
    ]
    if len(primary_bounds) != 1:
        raise ValueError("Primary bound row missing.")
    bound = primary_bounds.iloc[0]
    if int(bound["predicted_above_one_n"]) != 6:
        raise ValueError("Primary fitted-above-one count changed.")
    if not close(
        float(bound["predicted_above_one_weighted_percent"]),
        0.0496138819392451,
    ):
        raise ValueError("Primary weighted bound fraction changed.")
    if not close(
        float(bound["flagged_acceleration_min"]),
        38.2865540289739,
    ):
        raise ValueError("Primary flagged acceleration minimum changed.")

    quantiles = pd.read_csv(
        tables / "09_stage2_acceleration_quantiles.csv"
    )
    require_columns(
        quantiles,
        {"percentile", "acceleration_years"},
        "Acceleration quantiles",
    )
    p99 = quantiles.loc[quantiles["percentile"].eq(99)]
    if len(p99) != 1:
        raise ValueError("Weighted p99 row missing.")
    p99_value = float(p99.iloc[0]["acceleration_years"])
    if not close(p99_value, 25.761430620625):
        raise ValueError("Weighted acceleration p99 changed.")
    if float(bound["flagged_acceleration_min"]) <= p99_value:
        raise ValueError(
            "Primary fitted-bound violations are no longer beyond p99."
        )

    local = pd.read_csv(
        tables / "09_stage2_local_five_year_ratios.csv"
    )
    require_columns(
        local,
        {
            "anchor_percentile",
            "local_five_year_prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
        },
        "Local five-year ratios",
    )
    if list(local["anchor_percentile"].astype(int)) != [10, 25, 50, 75, 90]:
        raise ValueError("Local-ratio anchors changed.")
    ratios = local["local_five_year_prevalence_ratio"].astype(float)
    if not (ratios > 1).all():
        raise ValueError("A local five-year ratio is not positive.")
    if not (
        local["ci_low_95"].astype(float) > 1
    ).all():
        raise ValueError(
            "A local five-year ratio interval includes one."
        )
    post_peak = ratios.iloc[1:].tolist()
    if not all(
        earlier > later
        for earlier, later in zip(post_peak, post_peak[1:])
    ):
        raise ValueError(
            "Expected attenuation after the 25th-percentile anchor "
            "was not reproduced."
        )

    curve = pd.read_csv(
        tables / "09_stage2_adjusted_prevalence_curve.csv"
    )
    require_columns(
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
    for _, curve_row in curve.iterrows():
        low = float(curve_row["ci_low_95"])
        value = float(curve_row["adjusted_prevalence"])
        high = float(curve_row["ci_high_95"])
        if not 0 < low <= value <= high < 1:
            raise ValueError("Adjusted-prevalence curve is invalid.")

    checks = pd.read_csv(
        tables / "09_stage2_review_checks.csv"
    )
    require_columns(checks, {"check", "pass", "observed"}, "Review checks")
    failed = checks.loc[~checks["pass"].map(parse_bool)]
    if not failed.empty:
        raise ValueError(
            "Diagnostic-review checks failed: "
            + "; ".join(failed["check"].astype(str))
        )

    if not figure.is_file() or figure.stat().st_size <= 0:
        raise FileNotFoundError("Diagnostic figure is missing.")

    return nonlinearity, bounds, local


def validate_release_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("status") != "released_for_v2_development":
        raise ValueError("Stage 2 release status changed.")
    if config["scope"]["merge_to_main_authorized"] is not False:
        raise ValueError("Main-branch merge was authorized prematurely.")
    if config["v1_protection"]["v1_immutable"] is not True:
        raise ValueError("V1 protection was removed.")
    if (
        config["next_authorized_stage"][
            "explainable_extension_authorized"
        ]
        is not False
    ):
        raise ValueError(
            "Explainable extension was authorized prematurely."
        )
    return config


def ensure_public_outputs_have_no_identifiers(paths: list[Path]) -> None:
    forbidden = {"SEQN", "participant_id", "subject_id"}
    for path in paths:
        columns = set(pd.read_csv(path, nrows=0).columns)
        overlap = forbidden.intersection(columns)
        if overlap:
            raise ValueError(
                f"Participant identifier in public output {path.name}: "
                f"{sorted(overlap)}"
            )


def run_validation(project_root: Path) -> None:
    tables = project_root / "results/tables/v2"
    figure = (
        project_root
        / "results/figures/v2/09_stage2_adjusted_prevalence_curve.png"
    )
    config_path = project_root / "config/v2_stage2_release.json"

    required = [
        tables / "06_stage2_primary_result.csv",
        tables / "06_stage2_secondary_results.csv",
        tables / "06_stage2_model_diagnostics.csv",
        tables / "06_stage2_release_checks.csv",
        tables / "09_stage2_acceleration_quantiles.csv",
        tables / "09_stage2_prediction_bound_audit.csv",
        tables / "09_stage2_trimmed_linear_sensitivity.csv",
        tables / "09_stage2_adjusted_prevalence_curve.csv",
        tables / "09_stage2_local_five_year_ratios.csv",
        tables / "09_stage2_nonlinearity_review.csv",
        tables / "09_stage2_review_checks.csv",
        config_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing Stage 2 release inputs: " + ", ".join(missing)
        )

    primary = validate_primary(required[0])
    secondary = validate_secondary(required[1])
    nonlinearity, bounds, local = validate_review(tables, figure)
    config = validate_release_config(config_path)

    diagnostics = pd.read_csv(
        tables / "06_stage2_model_diagnostics.csv"
    )
    require_columns(
        diagnostics,
        {
            "converged",
            "finite_coefficients",
            "finite_covariance",
            "warning_n",
        },
        "Model diagnostics",
    )
    if not diagnostics["converged"].map(parse_bool).all():
        raise ValueError("A conventional model did not converge.")
    if not diagnostics["finite_coefficients"].map(parse_bool).all():
        raise ValueError("A model has non-finite coefficients.")
    if not diagnostics["finite_covariance"].map(parse_bool).all():
        raise ValueError("A model has non-finite covariance.")
    if not (diagnostics["warning_n"].astype(int) == 0).all():
        raise ValueError("A conventional model emitted warnings.")

    release_checks = pd.read_csv(
        tables / "06_stage2_release_checks.csv"
    )
    require_columns(
        release_checks,
        {"check", "pass", "observed"},
        "Stage 2 release checks",
    )
    failed_release = release_checks.loc[
        ~release_checks["pass"].map(parse_bool)
    ]
    if not failed_release.empty:
        raise ValueError(
            "Stage 2 release checks failed: "
            + "; ".join(failed_release["check"].astype(str))
        )

    public_csvs = [
        path for path in required if path.suffix.lower() == ".csv"
    ]
    ensure_public_outputs_have_no_identifiers(public_csvs)

    summary_rows = [
        {
            "role": "primary",
            "outcome": primary["outcome"],
            "n": int(primary["n"]),
            "positive_n": int(primary["positive_n"]),
            "prevalence_ratio": float(primary["prevalence_ratio"]),
            "ci_low_95": float(primary["ci_low_95"]),
            "ci_high_95": float(primary["ci_high_95"]),
            "p_value": float(primary["p_value"]),
            "multiplicity": "primary_unadjusted",
            "interpretation": (
                "prespecified_global_linear_summary_with_nonlinearity"
            ),
        }
    ]
    for _, row in secondary.iterrows():
        summary_rows.append(
            {
                "role": "secondary",
                "outcome": row["outcome"],
                "n": int(row["n"]),
                "positive_n": int(row["positive_n"]),
                "prevalence_ratio": float(row["prevalence_ratio"]),
                "ci_low_95": float(row["ci_low_95"]),
                "ci_high_95": float(row["ci_high_95"]),
                "p_value": float(row["p_value_holm"]),
                "multiplicity": "holm_adjusted",
                "interpretation": "supportive_association",
            }
        )

    release_summary = pd.DataFrame(summary_rows)
    summary_path = tables / "11_stage2_release_summary.csv"
    summary_bytes = release_summary.to_csv(
        index=False,
        lineterminator="\n",
    ).encode("utf-8")
    summary_path.write_bytes(summary_bytes)

    log_dir = project_root / "results/logs/v2"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "11_stage2_release_validation.json"
    report = {
        "document_id": "AL-V2-S2REL-V-001",
        "status": "passed",
        "stage2_released_for_v2_development": True,
        "commit_to_v2_development_authorized": True,
        "merge_to_main_authorized": False,
        "primary_result": PRIMARY_EXPECTED,
        "nonlinearity": {
            "quasipoisson_p": float(
                nonlinearity.iloc[0][
                    "prespecified_quasipoisson_nonlinearity_p"
                ]
            ),
            "bounded_logistic_spline_p": float(
                nonlinearity.iloc[0][
                    "logistic_spline_nonlinearity_p"
                ]
            ),
        },
        "primary_bound_diagnostic": {
            "fitted_above_one_n": int(
                bounds.loc[
                    bounds["outcome"].eq("mobility_disability"),
                    "predicted_above_one_n",
                ].iloc[0]
            ),
            "weighted_percent": float(
                bounds.loc[
                    bounds["outcome"].eq("mobility_disability"),
                    "predicted_above_one_weighted_percent",
                ].iloc[0]
            ),
        },
        "local_ratio_anchors": local[
            [
                "anchor_percentile",
                "local_five_year_prevalence_ratio",
                "ci_low_95",
                "ci_high_95",
            ]
        ].to_dict(orient="records"),
        "v1_modified": False,
        "participant_level_public_output": False,
        "transportability_claims_authorized": False,
        "prediction_claims_authorized": False,
        "explainable_extension_authorized": False,
        "next_authorized_stage": config[
            "next_authorized_stage"
        ]["name"],
        "outputs": [
            str(summary_path.relative_to(project_root)),
            str(log_path.relative_to(project_root)),
        ],
    }
    log_path.write_bytes(
        (
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
    )

    print("STAGE 2 RELEASE VALIDATION PASSED")
    print(
        "Stage 2 conventional association results may be committed to "
        "v2-development."
    )
    print(
        "Primary global linear summary: "
        "PR 1.147564 (95% CI 1.099844-1.197355), "
        "with strong evidence of nonlinearity."
    )
    print(
        "Transportability, prediction, explainable modeling, and merge to "
        "main remain unauthorized."
    )
    print(f"Release summary: {summary_path.relative_to(project_root)}")
    print(f"Validation log: {log_path.relative_to(project_root)}")


def run_self_test() -> None:
    assert parse_bool("TRUE")
    assert not parse_bool("false")
    assert close(1.0, 1.0)
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
