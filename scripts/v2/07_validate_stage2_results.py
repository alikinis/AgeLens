"""Validate aggregate outputs from AgeLens V2 Stage 2 models."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_COUNTS = {
    "mobility_disability": (4366, 682),
    "any_disability_six": (4358, 1247),
    "fair_poor_general_health": (4076, 1025),
    "phq9_ge10": (4021, 345),
}


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Cannot interpret boolean value: {value!r}")


def require_columns(
    frame: pd.DataFrame,
    columns: set[str],
    label: str,
) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def validate_input_audit(frame: pd.DataFrame) -> None:
    require_columns(
        frame,
        {
            "outcome",
            "valid_n",
            "positive_n",
            "negative_n",
            "weighted_prevalence_percent",
            "represented_strata",
            "represented_psus",
        },
        "Stage 2 input audit",
    )
    indexed = frame.set_index("outcome")
    for outcome, (expected_n, expected_positive) in EXPECTED_COUNTS.items():
        if outcome not in indexed.index:
            raise ValueError(f"Input audit row missing: {outcome}")
        row = indexed.loc[outcome]
        if int(row["valid_n"]) != expected_n:
            raise ValueError(f"{outcome} valid n changed.")
        if int(row["positive_n"]) != expected_positive:
            raise ValueError(f"{outcome} positive n changed.")
        if int(row["negative_n"]) != expected_n - expected_positive:
            raise ValueError(f"{outcome} negative n changed.")
        prevalence = float(row["weighted_prevalence_percent"])
        if not math.isfinite(prevalence) or not 0 <= prevalence <= 100:
            raise ValueError(f"{outcome} prevalence is invalid.")
        if int(row["represented_strata"]) <= 0:
            raise ValueError(f"{outcome} has no represented strata.")
        if int(row["represented_psus"]) <= 0:
            raise ValueError(f"{outcome} has no represented PSUs.")


def validate_input_checks(frame: pd.DataFrame) -> None:
    require_columns(frame, {"check", "pass", "observed"}, "Input checks")
    failed = frame.loc[~frame["pass"].map(parse_bool)]
    if not failed.empty:
        raise ValueError(
            "Stage 2 input checks failed: "
            + "; ".join(failed["check"].astype(str))
        )


def validate_primary(frame: pd.DataFrame) -> dict[str, float]:
    require_columns(
        frame,
        {
            "outcome",
            "model",
            "n",
            "positive_n",
            "design_df",
            "prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
            "p_value",
            "interpretation",
            "result_status",
        },
        "Primary result",
    )
    if len(frame) != 1:
        raise ValueError("Primary result must contain exactly one row.")
    row = frame.iloc[0]
    if row["outcome"] != "mobility_disability":
        raise ValueError("Primary outcome changed.")
    if row["model"] != "model_c":
        raise ValueError("Primary inference model changed.")
    if int(row["n"]) != 4366 or int(row["positive_n"]) != 682:
        raise ValueError("Primary model counts changed.")
    if int(row["design_df"]) != 30:
        raise ValueError("Primary design degrees of freedom changed.")
    values = {
        "prevalence_ratio": float(row["prevalence_ratio"]),
        "ci_low_95": float(row["ci_low_95"]),
        "ci_high_95": float(row["ci_high_95"]),
        "p_value": float(row["p_value"]),
    }
    if not all(math.isfinite(value) for value in values.values()):
        raise ValueError("Primary result contains non-finite values.")
    if values["prevalence_ratio"] <= 0:
        raise ValueError("Primary prevalence ratio is non-positive.")
    if not (
        0 < values["ci_low_95"]
        <= values["prevalence_ratio"]
        <= values["ci_high_95"]
    ):
        raise ValueError("Primary confidence interval is invalid.")
    if not 0 <= values["p_value"] <= 1:
        raise ValueError("Primary p-value is invalid.")
    if row["interpretation"] != "associational_not_causal":
        raise ValueError("Primary interpretation guardrail changed.")
    if row["result_status"] != "provisional_pending_stage2_review":
        raise ValueError("Primary result was released prematurely.")
    return values


def validate_hierarchy(frame: pd.DataFrame) -> None:
    require_columns(
        frame,
        {
            "outcome",
            "model",
            "n",
            "positive_n",
            "design_df",
            "coefficient_n",
            "predicted_mean",
            "predicted_min",
            "predicted_max",
        },
        "Primary model hierarchy",
    )
    if set(frame["model"]) != {"model_a", "model_b", "model_c"}:
        raise ValueError("Primary model hierarchy changed.")
    if not frame["n"].astype(int).eq(4366).all():
        raise ValueError("Hierarchy row counts changed.")
    if not frame["positive_n"].astype(int).eq(682).all():
        raise ValueError("Hierarchy positive counts changed.")
    if not frame["design_df"].astype(int).eq(30).all():
        raise ValueError("Hierarchy design df changed.")
    for column in ("predicted_mean", "predicted_min", "predicted_max"):
        values = pd.to_numeric(frame[column], errors="raise")
        if not values.map(math.isfinite).all():
            raise ValueError(f"Hierarchy {column} contains non-finite values.")


def validate_secondary(frame: pd.DataFrame) -> None:
    require_columns(
        frame,
        {
            "outcome",
            "model",
            "n",
            "positive_n",
            "prevalence_ratio",
            "ci_low_95",
            "ci_high_95",
            "p_value_raw",
            "p_value_holm",
            "result_status",
        },
        "Secondary results",
    )
    expected_outcomes = set(EXPECTED_COUNTS) - {"mobility_disability"}
    if set(frame["outcome"]) != expected_outcomes:
        raise ValueError("Secondary outcome family changed.")
    for _, row in frame.iterrows():
        outcome = str(row["outcome"])
        expected_n, expected_positive = EXPECTED_COUNTS[outcome]
        if int(row["n"]) != expected_n:
            raise ValueError(f"{outcome} secondary n changed.")
        if int(row["positive_n"]) != expected_positive:
            raise ValueError(f"{outcome} secondary positive n changed.")
        if row["model"] != "model_c":
            raise ValueError(f"{outcome} secondary model changed.")
        pr = float(row["prevalence_ratio"])
        low = float(row["ci_low_95"])
        high = float(row["ci_high_95"])
        raw = float(row["p_value_raw"])
        adjusted = float(row["p_value_holm"])
        if not all(math.isfinite(value) for value in (pr, low, high, raw, adjusted)):
            raise ValueError(f"{outcome} contains non-finite results.")
        if not 0 < low <= pr <= high:
            raise ValueError(f"{outcome} confidence interval is invalid.")
        if not 0 <= raw <= 1 or not 0 <= adjusted <= 1:
            raise ValueError(f"{outcome} p-values are invalid.")
        if adjusted + 1e-15 < raw:
            raise ValueError(f"{outcome} Holm p-value is below raw p-value.")
        if row["result_status"] != (
            "secondary_provisional_pending_stage2_review"
        ):
            raise ValueError(f"{outcome} was released prematurely.")


def validate_diagnostics(frame: pd.DataFrame) -> None:
    require_columns(
        frame,
        {
            "model",
            "outcome",
            "n",
            "positive_n",
            "design_df",
            "converged",
            "finite_coefficients",
            "finite_covariance",
            "predicted_min",
            "predicted_max",
            "predicted_above_one_n",
            "warning_n",
        },
        "Model diagnostics",
    )
    if len(frame) != 6:
        raise ValueError("Expected six conventional-model diagnostic rows.")
    for column in ("converged", "finite_coefficients", "finite_covariance"):
        if not frame[column].map(parse_bool).all():
            raise ValueError(f"One or more models failed {column}.")
    for column in ("predicted_min", "predicted_max"):
        values = pd.to_numeric(frame[column], errors="raise")
        if not values.map(math.isfinite).all():
            raise ValueError(f"Diagnostics {column} contains non-finite values.")
    if (pd.to_numeric(frame["predicted_above_one_n"], errors="raise") < 0).any():
        raise ValueError("Negative predicted-above-one count.")


def validate_linearity(frame: pd.DataFrame) -> float:
    require_columns(
        frame,
        {
            "outcome",
            "nonlinear_df",
            "p_value_nonlinearity",
            "primary_linear_model_replaced",
        },
        "Linearity sensitivity",
    )
    if len(frame) != 1:
        raise ValueError("Linearity sensitivity must contain one row.")
    row = frame.iloc[0]
    if row["outcome"] != "mobility_disability":
        raise ValueError("Linearity outcome changed.")
    if int(row["nonlinear_df"]) != 3:
        raise ValueError("Linearity nonlinear df changed.")
    p_value = float(row["p_value_nonlinearity"])
    if not math.isfinite(p_value) or not 0 <= p_value <= 1:
        raise ValueError("Linearity p-value is invalid.")
    if parse_bool(row["primary_linear_model_replaced"]):
        raise ValueError("Linearity sensitivity replaced the primary model.")
    return p_value


def validate_release_checks(frame: pd.DataFrame) -> None:
    require_columns(frame, {"check", "pass", "observed"}, "Release checks")
    failed = frame.loc[~frame["pass"].map(parse_bool)]
    if not failed.empty:
        raise ValueError(
            "Stage 2 release checks failed: "
            + "; ".join(failed["check"].astype(str))
        )


def validate_runtime(frame: pd.DataFrame) -> None:
    require_columns(frame, {"component", "version"}, "Runtime versions")
    required = {"R", "survey", "splines", "platform", "script_build"}
    if not required.issubset(set(frame["component"])):
        raise ValueError("Runtime version records are incomplete.")
    if frame["version"].astype(str).str.strip().eq("").any():
        raise ValueError("Runtime version record contains a blank value.")


def validate_no_public_participant_output(tables_dir: Path) -> None:
    public_files = [
        path
        for path in tables_dir.glob("0[5-7]_stage2_*.csv")
        if path.is_file()
    ]
    for path in public_files:
        header = pd.read_csv(path, nrows=0)
        forbidden = {"SEQN", "participant_id", "subject_id"}
        if forbidden.intersection(header.columns):
            raise ValueError(
                f"Participant identifier found in public output: {path.name}"
            )


def run_validation(project_root: Path) -> Path:
    tables = project_root / "results" / "tables" / "v2"
    paths = {
        "input_audit": tables / "05_stage2_model_input_audit.csv",
        "input_checks": tables / "05_stage2_input_checks.csv",
        "primary": tables / "06_stage2_primary_result.csv",
        "hierarchy": tables / "06_stage2_primary_model_hierarchy.csv",
        "secondary": tables / "06_stage2_secondary_results.csv",
        "diagnostics": tables / "06_stage2_model_diagnostics.csv",
        "linearity": tables / "06_stage2_linearity_sensitivity.csv",
        "runtime": tables / "06_stage2_runtime_versions.csv",
        "release_checks": tables / "06_stage2_release_checks.csv",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Stage 2 aggregate outputs are missing: " + ", ".join(missing)
        )

    validate_input_audit(pd.read_csv(paths["input_audit"]))
    validate_input_checks(pd.read_csv(paths["input_checks"]))
    primary = validate_primary(pd.read_csv(paths["primary"]))
    validate_hierarchy(pd.read_csv(paths["hierarchy"]))
    validate_secondary(pd.read_csv(paths["secondary"]))
    validate_diagnostics(pd.read_csv(paths["diagnostics"]))
    nonlinearity_p = validate_linearity(pd.read_csv(paths["linearity"]))
    validate_runtime(pd.read_csv(paths["runtime"]))
    validate_release_checks(pd.read_csv(paths["release_checks"]))
    validate_no_public_participant_output(tables)

    output_dir = project_root / "results" / "logs" / "v2"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "07_stage2_result_validation.json"
    report = {
        "document_id": "AL-V2-S2V-001",
        "status": "passed",
        "stage2_results_status": "provisional_pending_human_review",
        "primary_outcome": "DLQ050 mobility disability",
        "primary_valid_n": 4366,
        "primary_positive_n": 682,
        "prevalence_ratio_per_5_years": primary["prevalence_ratio"],
        "ci_low_95": primary["ci_low_95"],
        "ci_high_95": primary["ci_high_95"],
        "p_value": primary["p_value"],
        "nonlinearity_p_value": nonlinearity_p,
        "conventional_models_validated": True,
        "explainable_extension_authorized": False,
        "v1_artifact_modified": False,
        "participant_level_public_output_written": False,
    }
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output


def run_self_test() -> None:
    input_audit = pd.DataFrame(
        [
            {
                "outcome": outcome,
                "valid_n": counts[0],
                "positive_n": counts[1],
                "negative_n": counts[0] - counts[1],
                "weighted_prevalence_percent": 10.0,
                "represented_strata": 30,
                "represented_psus": 60,
            }
            for outcome, counts in EXPECTED_COUNTS.items()
        ]
    )
    validate_input_audit(input_audit)
    validate_input_checks(
        pd.DataFrame([{"check": "synthetic", "pass": True, "observed": 1}])
    )
    validate_primary(
        pd.DataFrame(
            [
                {
                    "outcome": "mobility_disability",
                    "model": "model_c",
                    "n": 4366,
                    "positive_n": 682,
                    "design_df": 30,
                    "prevalence_ratio": 1.2,
                    "ci_low_95": 1.1,
                    "ci_high_95": 1.3,
                    "p_value": 0.001,
                    "interpretation": "associational_not_causal",
                    "result_status": "provisional_pending_stage2_review",
                }
            ]
        )
    )
    validate_linearity(
        pd.DataFrame(
            [
                {
                    "outcome": "mobility_disability",
                    "nonlinear_df": 3,
                    "p_value_nonlinearity": 0.5,
                    "primary_linear_model_replaced": False,
                }
            ]
        )
    )
    print("SELF-TEST PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    root = args.project_root.resolve()
    output = run_validation(root)
    primary = pd.read_csv(
        root / "results" / "tables" / "v2" / "06_stage2_primary_result.csv"
    ).iloc[0]
    print("STAGE 2 CONVENTIONAL MODEL VALIDATION PASSED")
    print(
        "Primary adjusted prevalence ratio per 5-year higher acceleration: "
        f"{float(primary['prevalence_ratio']):.6f} "
        f"(95% CI {float(primary['ci_low_95']):.6f}-"
        f"{float(primary['ci_high_95']):.6f}), "
        f"p={float(primary['p_value']):.6g}"
    )
    print("Results remain provisional pending human review.")
    print(f"Validation report: {output.relative_to(root)}")


if __name__ == "__main__":
    main()
