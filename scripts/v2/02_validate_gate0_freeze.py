"""Validate the governed AgeLens V2 Gate 0 outcome freeze."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_SUMMARY_ROWS = {
    ("mobility_disability", "2015_2016"): {
        "adult_canonical_n": 2181,
        "valid_n": 2181,
        "positive_n": 332,
        "weighted_prevalence_percent": 11.628807,
        "strata_with_valid_data": 15,
        "psus_with_valid_data": 30,
    },
    ("mobility_disability", "2017_2018"): {
        "adult_canonical_n": 2186,
        "valid_n": 2185,
        "positive_n": 350,
        "weighted_prevalence_percent": 11.904922,
        "strata_with_valid_data": 15,
        "psus_with_valid_data": 30,
    },
    ("mobility_disability", "pooled"): {
        "adult_canonical_n": 4367,
        "valid_n": 4366,
        "positive_n": 682,
        "weighted_prevalence_percent": 11.767896,
        "strata_with_valid_data": 30,
        "psus_with_valid_data": 60,
    },
    ("any_disability_six", "pooled"): {
        "adult_canonical_n": 4367,
        "valid_n": 4358,
        "positive_n": 1247,
        "weighted_prevalence_percent": 24.470093,
        "strata_with_valid_data": 30,
        "psus_with_valid_data": 60,
    },
    ("fair_poor_general_health", "pooled"): {
        "adult_canonical_n": 4367,
        "valid_n": 4076,
        "positive_n": 1025,
        "weighted_prevalence_percent": 18.332982,
        "strata_with_valid_data": 30,
        "psus_with_valid_data": 60,
    },
    ("phq9_ge10", "pooled"): {
        "adult_canonical_n": 4367,
        "valid_n": 4021,
        "positive_n": 345,
        "weighted_prevalence_percent": 7.452012,
        "strata_with_valid_data": 30,
        "psus_with_valid_data": 60,
    },
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
    raise ValueError(f"Cannot interpret boolean value: {value!r}")


def require_columns(
    frame: pd.DataFrame,
    columns: set[str],
    label: str,
) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def validate_summary(summary: pd.DataFrame) -> list[dict[str, Any]]:
    require_columns(
        summary,
        {
            "candidate",
            "cycle",
            "adult_canonical_n",
            "valid_n",
            "positive_n",
            "weighted_prevalence_percent",
            "strata_with_valid_data",
            "psus_with_valid_data",
        },
        "Outcome feasibility summary",
    )

    records: list[dict[str, Any]] = []
    for key, expected in REQUIRED_SUMMARY_ROWS.items():
        candidate, cycle = key
        selected = summary.loc[
            summary["candidate"].eq(candidate)
            & summary["cycle"].eq(cycle)
        ]
        if len(selected) != 1:
            raise ValueError(
                f"Expected one summary row for {candidate}/{cycle}; "
                f"found {len(selected)}."
            )
        row = selected.iloc[0]

        for field, expected_value in expected.items():
            observed = row[field]
            if field == "weighted_prevalence_percent":
                if not math.isclose(
                    float(observed),
                    float(expected_value),
                    abs_tol=PREVALENCE_TOLERANCE,
                    rel_tol=0,
                ):
                    raise ValueError(
                        f"{candidate}/{cycle} {field} changed: "
                        f"{observed} vs {expected_value}."
                    )
            elif int(observed) != int(expected_value):
                raise ValueError(
                    f"{candidate}/{cycle} {field} changed: "
                    f"{observed} vs {expected_value}."
                )

        records.append(
            {
                "candidate": candidate,
                "cycle": cycle,
                "status": "pass",
            }
        )

    pooled = summary.loc[
        summary["cycle"].eq("pooled")
    ].set_index("candidate")
    if float(
        pooled.loc["mobility_disability", "valid_fraction"]
    ) < 0.99:
        raise ValueError(
            "Primary outcome valid fraction is below 0.99."
        )
    if int(
        pooled.loc["mobility_disability", "positive_n"]
    ) < 500:
        raise ValueError(
            "Primary outcome has insufficient positive support."
        )
    return records


def validate_checks(checks: pd.DataFrame) -> None:
    require_columns(checks, {"check", "pass", "observed"}, "Checks")
    failed = checks.loc[
        ~checks["pass"].map(parse_bool)
    ]
    if not failed.empty:
        raise ValueError(
            "Stage 0 checks failed: "
            + "; ".join(failed["check"].astype(str))
        )


def validate_manifest(manifest: pd.DataFrame) -> int:
    require_columns(
        manifest,
        {
            "cycle",
            "component",
            "sha256",
            "rows",
            "xport_zero_replacements",
        },
        "Source manifest",
    )
    total = int(
        pd.to_numeric(
            manifest["xport_zero_replacements"],
            errors="raise",
        ).sum()
    )
    if total <= 0:
        raise ValueError(
            "No exact XPORT zero replacements were audited."
        )

    dpq = manifest.loc[manifest["component"].eq("DPQ")]
    if dpq.empty or int(
        pd.to_numeric(
            dpq["xport_zero_replacements"],
            errors="raise",
        ).sum()
    ) <= 0:
        raise ValueError(
            "DPQ exact XPORT zero replacements were not recorded."
        )
    return total


def validate_freeze_config(config: dict[str, Any]) -> None:
    if config.get("status") != "frozen":
        raise ValueError("Gate 0 config is not frozen.")
    if config.get("modeling_authorized") is not False:
        raise ValueError(
            "Gate 0 must not authorize final modeling."
        )
    primary = config.get("primary_outcome", {})
    if primary.get("candidate") != "mobility_disability":
        raise ValueError("Unexpected primary outcome candidate.")
    if primary.get("variable") != "DLQ050":
        raise ValueError("Unexpected primary outcome variable.")
    if primary.get("governed_weight") != "WTSAF4YR":
        raise ValueError("Unexpected governed survey weight.")


def run_validation(project_root: Path) -> Path:
    tables = project_root / "results/tables/v2"
    summary_path = tables / "01_outcome_feasibility_summary.csv"
    checks_path = tables / "01_outcome_feasibility_checks.csv"
    manifest_path = tables / "01_outcome_source_manifest.csv"
    freeze_path = project_root / "config/v2_gate0_freeze.json"

    required = [
        summary_path,
        checks_path,
        manifest_path,
        freeze_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Gate 0 inputs are missing: " + ", ".join(missing)
        )

    summary = pd.read_csv(summary_path)
    checks = pd.read_csv(checks_path)
    manifest = pd.read_csv(manifest_path)
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))

    validated_rows = validate_summary(summary)
    validate_checks(checks)
    replacements = validate_manifest(manifest)
    validate_freeze_config(freeze)

    output_dir = project_root / "results/logs/v2"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "02_gate0_freeze_validation.json"
    report = {
        "document_id": "AL-V2-G0V-001",
        "status": "passed",
        "primary_outcome": "mobility_disability",
        "primary_variable": "DLQ050",
        "pooled_valid_n": 4366,
        "pooled_positive_n": 682,
        "weighted_prevalence_percent": 11.767896,
        "represented_strata": 30,
        "represented_psus": 60,
        "xport_zero_replacements_audited": replacements,
        "validated_rows": validated_rows,
        "participant_level_output_written": False,
        "absolute_personal_path_recorded": False,
        "modeling_authorized": False,
    }
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output


def run_self_test() -> None:
    rows = []
    for (candidate, cycle), values in REQUIRED_SUMMARY_ROWS.items():
        row = {
            "candidate": candidate,
            "cycle": cycle,
            "valid_fraction": (
                4366 / 4367
                if candidate == "mobility_disability"
                and cycle == "pooled"
                else 1.0
            ),
        }
        row.update(values)
        rows.append(row)
    validate_summary(pd.DataFrame(rows))

    validate_checks(
        pd.DataFrame(
            [{"check": "synthetic", "pass": True, "observed": 1}]
        )
    )
    assert validate_manifest(
        pd.DataFrame(
            [
                {
                    "cycle": "2015_2016",
                    "component": "DPQ",
                    "sha256": "a" * 64,
                    "rows": 10,
                    "xport_zero_replacements": 5,
                }
            ]
        )
    ) == 5
    validate_freeze_config(
        {
            "status": "frozen",
            "modeling_authorized": False,
            "primary_outcome": {
                "candidate": "mobility_disability",
                "variable": "DLQ050",
                "governed_weight": "WTSAF4YR",
            },
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
    print("GATE 0 FREEZE VALIDATION PASSED")
    print(f"Primary outcome: DLQ050 mobility disability")
    print(f"Validation report: {output.relative_to(root)}")
    print("Final outcome modeling remains unauthorized.")


if __name__ == "__main__":
    main()
