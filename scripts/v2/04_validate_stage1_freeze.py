"""Validate Stage 1 support outputs and the frozen V2 design."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_MISSINGNESS = {
    "chronological_age_years": 0,
    "RIAGENDR": 0,
    "RIDRETH3": 0,
    "NHANES_CYCLE": 0,
    "phenoage_acceleration_per_5_years": 0,
}

EXPECTED_SUPPORT = {
    ("overall", "All governed adults"): (
        4366, 682, 3684, 11.767896, 30, 60
    ),
    ("sex", "Female"): (
        2259, 403, 1856, 13.883583, 30, 60
    ),
    ("sex", "Male"): (
        2107, 279, 1828, 9.533927, 30, 60
    ),
    ("age_group", "20-49"): (
        2045, 105, 1940, 4.146644, 30, 60
    ),
    ("age_group", "50-64"): (
        1223, 249, 974, 17.743043, 30, 60
    ),
    ("age_group", "65+"): (
        1098, 328, 770, 23.860483, 30, 60
    ),
    ("race_ethnicity", "Mexican American"): (
        691, 94, 597, 9.760212, 27, 49
    ),
    ("race_ethnicity", "Non-Hispanic Asian"): (
        578, 35, 543, 5.945906, 30, 55
    ),
    ("race_ethnicity", "Non-Hispanic Black"): (
        911, 162, 749, 13.701521, 30, 54
    ),
    ("race_ethnicity", "Non-Hispanic White"): (
        1470, 253, 1217, 11.655748, 30, 59
    ),
    ("race_ethnicity", "Other Hispanic"): (
        516, 98, 418, 13.142433, 30, 56
    ),
    ("race_ethnicity", "Other or multiracial"): (
        200, 40, 160, 18.118306, 30, 56
    ),
    ("NHANES_cycle", "2015_2016"): (
        2181, 332, 1849, 11.628807, 15, 30
    ),
    ("NHANES_cycle", "2017_2018"): (
        2185, 350, 1835, 11.904922, 15, 30
    ),
}

PREVALENCE_TOLERANCE = 1e-5


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def validate_missingness(frame: pd.DataFrame) -> None:
    required = {"variable", "n", "missing_n", "missing_percent"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"Missingness table lacks columns: {sorted(missing)}"
        )

    indexed = frame.set_index("variable")
    for variable, expected_missing in EXPECTED_MISSINGNESS.items():
        if variable not in indexed.index:
            raise ValueError(
                f"Missingness row absent: {variable}"
            )
        row = indexed.loc[variable]
        if int(row["n"]) != 4366:
            raise ValueError(
                f"{variable} n changed: {row['n']}"
            )
        if int(row["missing_n"]) != expected_missing:
            raise ValueError(
                f"{variable} missing n changed: "
                f"{row['missing_n']}"
            )
        if not math.isclose(
            float(row["missing_percent"]),
            0.0,
            abs_tol=1e-12,
        ):
            raise ValueError(
                f"{variable} missing percent is nonzero."
            )


def validate_support(frame: pd.DataFrame) -> None:
    required = {
        "dimension",
        "level",
        "n",
        "positive_n",
        "negative_n",
        "weighted_prevalence_percent",
        "represented_strata",
        "represented_psus",
        "support_pass",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"Support table lacks columns: {sorted(missing)}"
        )

    for key, expected in EXPECTED_SUPPORT.items():
        dimension, level = key
        selected = frame.loc[
            frame["dimension"].eq(dimension)
            & frame["level"].eq(level)
        ]
        if len(selected) != 1:
            raise ValueError(
                f"Expected one row for {dimension}/{level}; "
                f"found {len(selected)}."
            )
        row = selected.iloc[0]
        observed = (
            int(row["n"]),
            int(row["positive_n"]),
            int(row["negative_n"]),
            float(row["weighted_prevalence_percent"]),
            int(row["represented_strata"]),
            int(row["represented_psus"]),
        )
        for index, (actual, target) in enumerate(
            zip(observed, expected)
        ):
            if index == 3:
                if not math.isclose(
                    actual,
                    target,
                    abs_tol=PREVALENCE_TOLERANCE,
                    rel_tol=0,
                ):
                    raise ValueError(
                        f"{dimension}/{level} prevalence changed: "
                        f"{actual} vs {target}."
                    )
            elif actual != target:
                raise ValueError(
                    f"{dimension}/{level} support changed: "
                    f"{actual} vs {target}."
                )
        if not parse_bool(row["support_pass"]):
            raise ValueError(
                f"{dimension}/{level} no longer passes support."
            )

    if not frame["support_pass"].map(parse_bool).all():
        failed = frame.loc[
            ~frame["support_pass"].map(parse_bool),
            ["dimension", "level"],
        ]
        raise ValueError(
            "One or more support rows failed: "
            + failed.to_dict(orient="records").__repr__()
        )


def validate_acceleration(frame: pd.DataFrame) -> None:
    required = {
        "cycle",
        "intercept",
        "slope",
        "weighted_residual_mean",
        "n",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"Acceleration audit lacks columns: {sorted(missing)}"
        )
    if set(frame["cycle"]) != {"2015_2016", "2017_2018"}:
        raise ValueError("Unexpected acceleration cycles.")
    if set(frame["n"].astype(int)) != {2181, 2185}:
        raise ValueError(
            "Cycle-specific acceleration row counts changed."
        )
    maximum = float(
        frame["weighted_residual_mean"].abs().max()
    )
    if maximum > 1e-10:
        raise ValueError(
            f"Acceleration weighted mean is not zero: {maximum}"
        )


def validate_checks(frame: pd.DataFrame) -> None:
    required = {"check", "pass", "observed"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"Checks table lacks columns: {sorted(missing)}"
        )
    failed = frame.loc[~frame["pass"].map(parse_bool)]
    if not failed.empty:
        raise ValueError(
            "Stage 1 design checks failed: "
            + "; ".join(failed["check"].astype(str))
        )


def validate_freeze(config: dict[str, Any]) -> None:
    if config.get("status") != "frozen":
        raise ValueError("Stage 1 config is not frozen.")
    if config.get(
        "stage2_conventional_modeling_authorized"
    ) is not True:
        raise ValueError(
            "Stage 2 authorization is missing."
        )
    if config["relationship_to_v1"]["v1_immutable"] is not True:
        raise ValueError("V1 protection is not frozen.")
    if config["primary_outcome"]["variable"] != "DLQ050":
        raise ValueError("Primary outcome changed.")
    estimator = config["primary_association_estimator"]
    if (
        estimator["family"] != "quasipoisson"
        or estimator["link"] != "log"
        or estimator["weight"] != "WTSAF4YR"
    ):
        raise ValueError(
            "Primary association estimator changed."
        )
    validation = config["incremental_prediction"]["validation"]
    if validation["design"] != (
        "bidirectional_cross_cycle_validation"
    ):
        raise ValueError(
            "Prediction validation design changed."
        )
    if config["explainable_extension"]["authorized"] is not False:
        raise ValueError(
            "Explainable extension was authorized too early."
        )


def run_validation(project_root: Path) -> Path:
    tables = project_root / "results/tables/v2"
    required_paths = {
        "missingness": (
            tables / "03_stage1_covariate_missingness.csv"
        ),
        "support": (
            tables / "03_stage1_transportability_support.csv"
        ),
        "acceleration": (
            tables / "03_stage1_acceleration_audit.csv"
        ),
        "checks": (
            tables / "03_stage1_design_checks.csv"
        ),
        "freeze": (
            project_root / "config/v2_stage1_freeze.json"
        ),
    }
    absent = [
        str(path)
        for path in required_paths.values()
        if not path.is_file()
    ]
    if absent:
        raise FileNotFoundError(
            "Stage 1 freeze inputs missing: "
            + ", ".join(absent)
        )

    validate_missingness(
        pd.read_csv(required_paths["missingness"])
    )
    validate_support(
        pd.read_csv(required_paths["support"])
    )
    validate_acceleration(
        pd.read_csv(required_paths["acceleration"])
    )
    validate_checks(
        pd.read_csv(required_paths["checks"])
    )
    freeze = json.loads(
        required_paths["freeze"].read_text(encoding="utf-8")
    )
    validate_freeze(freeze)

    output_dir = project_root / "results/logs/v2"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "04_stage1_freeze_validation.json"
    report = {
        "document_id": "AL-V2-S1V-001",
        "status": "passed",
        "gate1_closed": True,
        "primary_outcome": "DLQ050",
        "primary_valid_n": 4366,
        "primary_positive_n": 682,
        "primary_covariate_missing_n": 0,
        "all_prespecified_subgroup_levels_supported": True,
        "association_estimand": (
            "adjusted prevalence ratio per 5-year "
            "higher acceleration"
        ),
        "prediction_validation": (
            "bidirectional cross-cycle validation"
        ),
        "stage2_conventional_modeling_authorized": True,
        "explainable_extension_authorized": False,
        "v1_artifact_modified": False,
        "participant_level_output_written": False,
    }
    output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def run_self_test() -> None:
    missing = pd.DataFrame(
        [
            {
                "variable": variable,
                "n": 4366,
                "missing_n": 0,
                "missing_percent": 0.0,
            }
            for variable in EXPECTED_MISSINGNESS
        ]
    )
    validate_missingness(missing)

    support_rows = []
    for (dimension, level), values in EXPECTED_SUPPORT.items():
        n, positive, negative, prevalence, strata, psus = values
        support_rows.append(
            {
                "dimension": dimension,
                "level": level,
                "n": n,
                "positive_n": positive,
                "negative_n": negative,
                "weighted_prevalence_percent": prevalence,
                "represented_strata": strata,
                "represented_psus": psus,
                "support_pass": True,
            }
        )
    validate_support(pd.DataFrame(support_rows))

    validate_acceleration(
        pd.DataFrame(
            [
                {
                    "cycle": "2015_2016",
                    "intercept": 1.0,
                    "slope": 1.0,
                    "weighted_residual_mean": 0.0,
                    "n": 2181,
                },
                {
                    "cycle": "2017_2018",
                    "intercept": 1.0,
                    "slope": 1.0,
                    "weighted_residual_mean": 0.0,
                    "n": 2185,
                },
            ]
        )
    )
    validate_checks(
        pd.DataFrame(
            [
                {
                    "check": "synthetic",
                    "pass": True,
                    "observed": 1,
                }
            ]
        )
    )
    validate_freeze(
        {
            "status": "frozen",
            "stage2_conventional_modeling_authorized": True,
            "relationship_to_v1": {"v1_immutable": True},
            "primary_outcome": {"variable": "DLQ050"},
            "primary_association_estimator": {
                "family": "quasipoisson",
                "link": "log",
                "weight": "WTSAF4YR",
            },
            "incremental_prediction": {
                "validation": {
                    "design": (
                        "bidirectional_cross_cycle_validation"
                    )
                }
            },
            "explainable_extension": {"authorized": False},
        }
    )
    print("SELF-TEST PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    root = args.project_root.resolve()
    output = run_validation(root)
    print("GATE 1 FREEZE VALIDATION PASSED")
    print("Gate 1 is closed.")
    print(
        "Stage 2 conventional modeling is authorized; "
        "no model was fitted by this validator."
    )
    print(f"Validation report: {output.relative_to(root)}")


if __name__ == "__main__":
    main()
