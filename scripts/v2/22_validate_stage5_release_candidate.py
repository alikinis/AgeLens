"""Independently validate the AgeLens V2 Stage 5 release candidate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

BUILD = "AgeLens-V2-Stage5-20260724b"
TOLERANCE = 1e-10
MARKER_BEGIN = "<!-- AGELENS_STAGE5_BEGIN -->"
MARKER_END = "<!-- AGELENS_STAGE5_END -->"


class ValidationError(RuntimeError):
    """Raised when a governed Stage 5 validation condition fails."""


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


def row_map(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise ValidationError(f"Duplicate values in {key}.")
    return result


def close(actual: Any, expected: Any, tolerance: float = TOLERANCE) -> bool:
    try:
        a = float(actual)
        e = float(expected)
    except (TypeError, ValueError):
        return False
    return math.isfinite(a) and math.isfinite(e) and math.isclose(a, e, rel_tol=0.0, abs_tol=tolerance)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValidationError(f"Invalid boolean: {value!r}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_prior_validator(root: Path, relative_script: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(root / relative_script), "--project-root", str(root)],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ValidationError(
            f"Prior release validator failed: {relative_script}\n"
            + (completed.stdout + "\n" + completed.stderr).strip()
        )


def require(root: Path, relpaths: list[str]) -> None:
    missing = [rel for rel in relpaths if not (root / rel).is_file()]
    if missing:
        raise ValidationError("Missing Stage 5 release-candidate artifacts: " + ", ".join(missing))


def expect_numeric(row: dict[str, str], expected: dict[str, Any], label: str) -> None:
    for column, value in expected.items():
        if not close(row.get(column), value):
            raise ValidationError(f"{label} numeric mismatch: {column}")


def abstract_word_count(text: str) -> int:
    before_count = text.split("**Word count:**", 1)[0]
    return sum(
        len(line.split())
        for line in before_count.splitlines()
        if line.strip() and not line.startswith("#")
    )


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValidationError(f"Invalid PNG header: {path.name}")
    return struct.unpack(">II", header[16:24])


def validate_git_scope(root: Path) -> None:
    if not (root / ".git").exists():
        return
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ValidationError("Unable to inspect Git scope:\n" + completed.stderr.strip())

    allowed_exact = {
        "docs/v2/README.md",
        "docs/v2/V2_ARISE_Alignment.md",
        "docs/v2/V2_Analysis_Plan.md",
        "docs/v2/V2_Decision_Log.md",
        "docs/v2/V2_Evidence_Gap_Register.md",
        "docs/v2/V2_Research_Protocol.md",
        "docs/v2/V2_ARISE_Abstract.md",
        "docs/v2/V2_ARISE_Presentation.md",
        "docs/v2/V2_Aggregate_Validation_Report.md",
        "docs/v2/V2_Stage5_Human_Review.md",
        "docs/v2/V2_Stage5_Implementation.md",
        "docs/v2/V2_Stage5_Release_Candidate.md",
        "docs/v2/V2_Stage5_Release_Report.md",
        "docs/v2/V2_Stage5_Synthesis.md",
    }
    allowed_prefixes = (
        "config/v2_stage5_",
        "results/figures/v2/21_stage5_",
        "results/tables/v2/21_stage5_",
        "results/tables/v2/23_stage5_",
        "scripts/v2/21_",
        "scripts/v2/22_",
        "scripts/v2/23_",
    )
    unexpected: list[str] = []
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().strip('"').replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path in allowed_exact or path.startswith(allowed_prefixes):
            continue
        unexpected.append(path)
    if unexpected:
        raise ValidationError(
            "Working-tree changes outside the governed Stage 5 scope: "
            + ", ".join(sorted(unexpected))
        )


def validate_private_material(root: Path) -> None:
    stage5_paths = [
        *sorted((root / "config").glob("v2_stage5_*.json")),
        *sorted((root / "docs/v2").glob("*Stage5*.md")),
        root / "docs/v2/V2_ARISE_Abstract.md",
        root / "docs/v2/V2_ARISE_Presentation.md",
        root / "docs/v2/V2_Aggregate_Validation_Report.md",
        *sorted((root / "results/tables/v2").glob("21_stage5_*.csv")),
        *sorted((root / "results/tables/v2").glob("23_stage5_*.csv")),
    ]
    private_path = re.compile(r"(?:[A-Za-z]:\\Users\\|/Users/|/home/)")
    secret_patterns = (
        "BEGIN PRIVATE KEY",
        "AKIA",
        "ghp_",
        "github_pat_",
    )
    for path in stage5_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        if private_path.search(text):
            raise ValidationError(f"Private absolute path found in {path.relative_to(root).as_posix()}.")
        for pattern in secret_patterns:
            if pattern in text:
                raise ValidationError(f"Secret-like text found in {path.relative_to(root).as_posix()}.")


def validate(root: Path) -> None:
    root = root.resolve()
    required = [
        "config/v2_stage2_release.json",
        "config/v2_stage3_release.json",
        "config/v2_stage4_release.json",
        "config/v2_stage5_synthesis.json",
        "config/v2_stage5_release_candidate.json",
        "scripts/v2/21_build_stage5_synthesis.py",
        "scripts/v2/22_validate_stage5_release_candidate.py",
        "results/tables/v2/21_stage5_scientific_summary.csv",
        "results/tables/v2/21_stage5_validation_summary.csv",
        "results/tables/v2/21_stage5_claims_matrix.csv",
        "results/tables/v2/21_stage5_source_manifest.csv",
        "results/tables/v2/21_stage5_release_checks.csv",
        "results/tables/v2/21_stage5_runtime_versions.csv",
        "results/figures/v2/21_stage5_v1_to_v2_progression.png",
        "results/figures/v2/21_stage5_evidence_synthesis.png",
        "docs/v2/V2_Stage5_Implementation.md",
        "docs/v2/V2_Stage5_Synthesis.md",
        "docs/v2/V2_Aggregate_Validation_Report.md",
        "docs/v2/V2_ARISE_Abstract.md",
        "docs/v2/V2_ARISE_Presentation.md",
        "docs/v2/V2_Stage5_Release_Candidate.md",
        "docs/v2/V2_Stage5_Human_Review.md",
        "docs/v2/README.md",
        "docs/v2/V2_Research_Protocol.md",
        "docs/v2/V2_Analysis_Plan.md",
        "docs/v2/V2_Decision_Log.md",
        "docs/v2/V2_Evidence_Gap_Register.md",
        "docs/v2/V2_ARISE_Alignment.md",
    ]
    require(root, required)

    for validator in (
        "scripts/v2/11_validate_stage2_release.py",
        "scripts/v2/15_validate_stage3_release.py",
        "scripts/v2/20_validate_stage4_release.py",
    ):
        run_prior_validator(root, validator)

    implementation = read_json(root / "config/v2_stage5_synthesis.json")
    candidate = read_json(root / "config/v2_stage5_release_candidate.json")
    if implementation.get("build") != BUILD or candidate.get("build") != BUILD:
        raise ValidationError("Stage 5 build identifier changed.")
    if implementation.get("status") != "implementation_authorized":
        raise ValidationError("Stage 5 implementation status changed.")

    rules = implementation.get("scientific_rules", {})
    expected_true = ("v1_immutable", "model_c_remains_preferred", "retain_null_and_negative_findings")
    expected_false = (
        "fit_new_model",
        "refit_prior_model",
        "feature_or_interaction_search",
        "hyperparameter_search",
        "participant_level_output",
        "local_explanations",
        "clinical_thresholds",
        "causal_claims",
        "biological_subgroup_claims",
    )
    for key in expected_true:
        if rules.get(key) is not True:
            raise ValidationError(f"Required Stage 5 rule is not true: {key}")
    for key in expected_false:
        if rules.get(key) is not False:
            raise ValidationError(f"Prohibited Stage 5 rule is not false: {key}")

    controls = implementation.get("release_controls", {})
    if controls.get("human_review_required") is not True:
        raise ValidationError("Human review requirement changed.")
    for key in ("final_v2_release_authorized", "merge_to_main_authorized", "arise_final_submission_authorized"):
        if controls.get(key) is not False:
            raise ValidationError(f"Restricted implementation control changed: {key}")

    if candidate.get("status") != "release_candidate_pending_human_review":
        raise ValidationError("Stage 5 candidate status is not pending human review.")
    if candidate.get("stage5_synthesis_implementation") != "complete":
        raise ValidationError("Stage 5 synthesis implementation is not complete.")
    if candidate.get("aggregate_validation") != "pass":
        raise ValidationError("Aggregate validation is not pass.")
    if candidate.get("human_review") != "pending":
        raise ValidationError("Human review must remain pending in the candidate.")
    for key in (
        "final_v2_release_authorized",
        "merge_to_main_authorized",
        "final_manuscript_claims_authorized",
        "arise_final_submission_authorized",
    ):
        if candidate.get(key) is not False:
            raise ValidationError(f"Restricted Stage 5 permission changed: {key}")
    if candidate.get("preferred_prediction_model") != "Stage3_Model_C":
        raise ValidationError("Preferred prediction model changed.")
    if candidate.get("model_d_role") != "descriptive_global_shape_sensitivity_only":
        raise ValidationError("Model D role changed.")

    stage2 = read_json(root / "config/v2_stage2_release.json")
    stage3 = read_json(root / "config/v2_stage3_release.json")
    stage4 = read_json(root / "config/v2_stage4_release.json")

    values = candidate.get("released_results", {})
    expected_candidate = {
        "stage2_primary_prevalence_ratio_per_5_years": stage2["primary_result"]["prespecified_global_linear_summary"]["prevalence_ratio_per_5_years"],
        "stage2_quasipoisson_nonlinearity_p": stage2["nonlinearity"]["prespecified_quasipoisson_p"],
        "stage3_brier_delta_c_minus_b": stage3["prediction_release"]["brier_delta_c_minus_b"]["estimate"],
        "stage3_auc_delta_c_minus_b": stage3["prediction_release"]["auc_delta_c_minus_b"]["estimate"],
        "stage4_brier_delta_d_minus_c": stage4["incremental_prediction_release"]["brier_delta_d_minus_c"]["estimate"],
        "stage4_auc_delta_d_minus_c": stage4["incremental_prediction_release"]["auc_delta_d_minus_c"]["estimate"],
        "stage4_acceleration_shape_spearman": stage4["global_explanation_release"]["acceleration_shape_spearman"],
    }
    for key, expected in expected_candidate.items():
        if not close(values.get(key), expected):
            raise ValidationError(f"Candidate released result changed: {key}")

    summary = row_map(
        read_csv(root / "results/tables/v2/21_stage5_scientific_summary.csv"),
        "estimand_or_metric",
    )
    expected_labels = {
        "Adjusted prevalence ratio per 5-year higher acceleration",
        "Nonlinearity tests",
        "Adjusted prevalence ratio: Any six-domain disability",
        "Adjusted prevalence ratio: Fair or poor general health",
        "Adjusted prevalence ratio: PHQ-9 score ≥10",
        "Global race/ethnicity interaction test for frozen linear acceleration summary",
        "Brier delta C−B",
        "AUC delta C−B",
        "Brier delta D−C",
        "AUC delta D−C",
        "Cycle-trained acceleration-term Spearman rank correlation",
        "Governed model-role decision",
    }
    if set(summary) != expected_labels:
        raise ValidationError("Stage 5 scientific-summary row set changed.")

    s2_primary = stage2["primary_result"]["prespecified_global_linear_summary"]
    expect_numeric(summary["Adjusted prevalence ratio per 5-year higher acceleration"], {
        "estimate": s2_primary["prevalence_ratio_per_5_years"],
        "uncertainty_low": s2_primary["ci_low_95"],
        "uncertainty_high": s2_primary["ci_high_95"],
    }, "Stage 2 primary")

    expected_nonlin = (
        f"quasi-Poisson p={stage2['nonlinearity']['prespecified_quasipoisson_p']:.15g}; "
        f"logistic spline p={stage2['nonlinearity']['bounded_logistic_spline_p']:.15g}"
    )
    if summary["Nonlinearity tests"]["estimate"] != expected_nonlin:
        raise ValidationError("Stage 2 nonlinearity summary changed.")

    secondary_labels = {
        "any_disability_six": "Adjusted prevalence ratio: Any six-domain disability",
        "fair_poor_general_health": "Adjusted prevalence ratio: Fair or poor general health",
        "phq9_ge10": "Adjusted prevalence ratio: PHQ-9 score ≥10",
    }
    for item in stage2["secondary_results"]:
        label = secondary_labels[item["outcome"]]
        expect_numeric(summary[label], {
            "estimate": item["prevalence_ratio"],
            "uncertainty_low": item["ci_low_95"],
            "uncertainty_high": item["ci_high_95"],
        }, label)

    race = stage3["transportability_release"]
    race_row = summary["Global race/ethnicity interaction test for frozen linear acceleration summary"]
    if not close(race_row["estimate"], race["race_ethnicity_global_p_raw"], 1e-14):
        raise ValidationError("Stage 3 race/ethnicity p-value changed.")
    q_text = f"q={race['race_ethnicity_global_q_bh']:.15g}"
    if q_text not in race_row["multiplicity_or_decision_rule"]:
        raise ValidationError("Stage 3 race/ethnicity q-value changed.")

    for label, key in (
        ("Brier delta C−B", "brier_delta_c_minus_b"),
        ("AUC delta C−B", "auc_delta_c_minus_b"),
    ):
        metric = stage3["prediction_release"][key]
        expect_numeric(summary[label], {
            "estimate": metric["estimate"],
            "uncertainty_low": metric["ci_low_95"],
            "uncertainty_high": metric["ci_high_95"],
        }, label)

    for label, key in (
        ("Brier delta D−C", "brier_delta_d_minus_c"),
        ("AUC delta D−C", "auc_delta_d_minus_c"),
    ):
        metric = stage4["incremental_prediction_release"][key]
        expect_numeric(summary[label], {
            "estimate": metric["estimate"],
            "uncertainty_low": metric["ci_low_95"],
            "uncertainty_high": metric["ci_high_95"],
        }, label)

    stability = summary["Cycle-trained acceleration-term Spearman rank correlation"]
    if not close(stability["estimate"], stage4["global_explanation_release"]["acceleration_shape_spearman"]):
        raise ValidationError("Stage 4 shape stability changed.")
    if stability["source_artifact"] != "results/tables/v2/18_stage4_shape_stability.csv::single_row":
        raise ValidationError("Stage 4 shape source locator changed.")
    if summary["Governed model-role decision"]["estimate"] != "Stage3_Model_C":
        raise ValidationError("Stage 5 model-role summary changed.")

    for label, row in summary.items():
        if "::" not in row["source_artifact"]:
            raise ValidationError(f"Scientific-summary row lacks row/field locator: {label}")

    validation_rows = read_csv(root / "results/tables/v2/21_stage5_validation_summary.csv")
    if not validation_rows or not all(parse_bool(row["pass"]) for row in validation_rows):
        raise ValidationError("A Stage 5 validation-summary check failed.")
    release_checks = read_csv(root / "results/tables/v2/21_stage5_release_checks.csv")
    if not release_checks or not all(parse_bool(row["pass"]) for row in release_checks):
        raise ValidationError("A Stage 5 release check failed.")

    claims = row_map(read_csv(root / "results/tables/v2/21_stage5_claims_matrix.csv"), "claim_id")
    if set(claims) != {f"C-{index:02d}" for index in range(1, 13)}:
        raise ValidationError("Stage 5 claims-matrix identifiers changed.")
    expected_status = {
        "C-01": "authorized_with_restrictions",
        "C-02": "authorized",
        "C-03": "authorized_with_restrictions",
        "C-04": "authorized_with_restrictions",
        "C-05": "unsupported",
        "C-06": "authorized_with_restrictions",
        "C-07": "unsupported",
        "C-08": "prohibited",
        "C-09": "authorized_with_restrictions",
        "C-10": "prohibited",
        "C-11": "prohibited",
        "C-12": "pending_final_review",
    }
    for claim_id, status in expected_status.items():
        if claims[claim_id]["status"] != status:
            raise ValidationError(f"Claim status changed: {claim_id}")
        if "::" not in claims[claim_id]["source"]:
            raise ValidationError(f"Claim lacks row/field source locator: {claim_id}")

    manifest = read_csv(root / "results/tables/v2/21_stage5_source_manifest.csv")
    expected_sources = set(implementation["authoritative_sources"])
    observed_sources = {row["source_path"] for row in manifest}
    if observed_sources != expected_sources:
        raise ValidationError("Stage 5 source-manifest file set changed.")
    for row in manifest:
        source = root / row["source_path"]
        if not source.is_file():
            raise ValidationError(f"Manifest source missing: {row['source_path']}")
        if sha256(source) != row["sha256"]:
            raise ValidationError(f"Manifest hash mismatch: {row['source_path']}")
        if int(row["size_bytes"]) != source.stat().st_size:
            raise ValidationError(f"Manifest size mismatch: {row['source_path']}")
    manifest_hash = sha256(root / "results/tables/v2/21_stage5_source_manifest.csv")
    if manifest_hash != candidate["generated_metadata"]["source_manifest_sha256"]:
        raise ValidationError("Source-manifest package hash changed.")

    runtime = row_map(read_csv(root / "results/tables/v2/21_stage5_runtime_versions.csv"), "component")
    if runtime.get("stage5_build", {}).get("version") != BUILD:
        raise ValidationError("Stage 5 runtime build changed.")
    for component in ("python", "implementation", "platform", "matplotlib", "generated_utc"):
        if component not in runtime or not runtime[component].get("version"):
            raise ValidationError(f"Runtime component missing: {component}")

    docs = {
        name: (root / "docs/v2" / name).read_text(encoding="utf-8")
        for name in (
            "V2_Stage5_Synthesis.md",
            "V2_Aggregate_Validation_Report.md",
            "V2_ARISE_Abstract.md",
            "V2_ARISE_Presentation.md",
            "V2_Stage5_Release_Candidate.md",
            "V2_Stage5_Human_Review.md",
        )
    }

    abstract = docs["V2_ARISE_Abstract.md"]
    for heading in ("## Background", "## Methods", "## Results", "## Conclusions", "**Word count:**"):
        if heading not in abstract:
            raise ValidationError("ARISE abstract section missing: " + heading)
    for phrase in (
        "complex-survey",
        "serious difficulty walking or climbing stairs",
        "treated strictly as a social classification",
        "pooled out-of-cycle prediction",
        "did not establish improvement beyond Model C",
        "not independent external-cohort validation",
    ):
        if phrase not in abstract:
            raise ValidationError("ARISE abstract guardrail missing: " + phrase)
    observed_word_count = abstract_word_count(abstract)
    declared_match = re.search(r"\*\*Word count:\*\*\s*(\d+)", abstract)
    if not declared_match or int(declared_match.group(1)) != observed_word_count:
        raise ValidationError("ARISE abstract word count does not reconcile.")
    if candidate["generated_metadata"]["abstract_word_count"] != observed_word_count:
        raise ValidationError("Candidate abstract word count does not reconcile.")

    synthesis = docs["V2_Stage5_Synthesis.md"]
    report = docs["V2_Aggregate_Validation_Report.md"]
    presentation = docs["V2_ARISE_Presentation.md"]
    release_candidate_doc = docs["V2_Stage5_Release_Candidate.md"]
    required_exact_fragments = {
        "synthesis": (
            f"PR {s2_primary['prevalence_ratio_per_5_years']:.3f}",
            f"q={race['race_ethnicity_global_q_bh']:.6g}",
            f"Brier delta C−B was {stage3['prediction_release']['brier_delta_c_minus_b']['estimate']:.6f}",
            f"Brier delta D−C was {stage4['incremental_prediction_release']['brier_delta_d_minus_c']['estimate']:.6f}",
            f"Spearman rank correlation {stage4['global_explanation_release']['acceleration_shape_spearman']:.6f}",
        ),
        "report": (
            f"PR {s2_primary['prevalence_ratio_per_5_years']:.6f}",
            f"Brier delta C−B was {stage3['prediction_release']['brier_delta_c_minus_b']['estimate']:.16g}",
            f"Brier delta D−C was {stage4['incremental_prediction_release']['brier_delta_d_minus_c']['estimate']:.16g}",
            "Model C remains preferred.",
        ),
        "presentation": (
            f"PR {s2_primary['prevalence_ratio_per_5_years']:.3f}",
            "Model C remained preferred",
            "did not improve upon Model C",
            "Race/ethnicity is a social classification",
        ),
        "release_candidate": (
            "- Human review: pending",
            "- Final V2 release: unauthorized",
            "- Merge to `main`: unauthorized",
        ),
    }
    for fragment in required_exact_fragments["synthesis"]:
        if fragment not in synthesis:
            raise ValidationError("Stage 5 synthesis value or guardrail missing: " + fragment)
    for fragment in required_exact_fragments["report"]:
        if fragment not in report:
            raise ValidationError("Aggregate report value or guardrail missing: " + fragment)
    for fragment in required_exact_fragments["presentation"]:
        if fragment not in presentation:
            raise ValidationError("ARISE presentation value or guardrail missing: " + fragment)
    for fragment in required_exact_fragments["release_candidate"]:
        if fragment not in release_candidate_doc:
            raise ValidationError("Release-candidate boundary missing: " + fragment)

    if presentation.count("## Slide ") != 8:
        raise ValidationError("ARISE presentation must contain exactly eight working slides.")
    if "conventional-regression-as-AI" not in presentation:
        raise ValidationError("ARISE presentation conventional-regression guardrail missing.")

    combined_docs = "\n".join(docs.values()).lower()
    for phrase in (
        "human review is pending",
        "model c remains the preferred prediction model",
        "no new model was fitted",
        "final v2 release: unauthorized",
        "merge to `main`: unauthorized",
        "not exact curve agreement",
        "race/ethnicity is a social classification",
    ):
        if phrase not in combined_docs:
            raise ValidationError("Stage 5 document guardrail missing: " + phrase)

    human_review = docs["V2_Stage5_Human_Review.md"].lower()
    # Candidate validator accepts either the original pending form or a later governed release review.
    if "status | pending human review" not in human_review and "status | completed" not in human_review:
        raise ValidationError("Human-review status is missing.")
    if "status | pending human review" in human_review and "no approval" not in human_review:
        raise ValidationError("Pending human-review form fabricates or omits review status.")

    for relpath in (
        "docs/v2/README.md",
        "docs/v2/V2_Research_Protocol.md",
        "docs/v2/V2_Analysis_Plan.md",
        "docs/v2/V2_Decision_Log.md",
        "docs/v2/V2_Evidence_Gap_Register.md",
        "docs/v2/V2_ARISE_Alignment.md",
    ):
        text = (root / relpath).read_text(encoding="utf-8")
        if MARKER_BEGIN not in text or MARKER_END not in text:
            raise ValidationError(f"Stage 5 governed update marker missing: {relpath}")

    forbidden_headers = {"SEQN", "participant_id", "prediction", "local_contribution", "risk_score"}
    for path in sorted((root / "results/tables/v2").glob("21_stage5_*.csv")):
        rows = read_csv(path)
        header = set(rows[0]) if rows else set()
        if forbidden_headers & header:
            raise ValidationError(f"Participant-level header in {path.name}.")

    expected_dimensions = {
        "21_stage5_v1_to_v2_progression.png": (2000, 696),
        "21_stage5_evidence_synthesis.png": (1766, 1020),
    }
    for name, minimum in expected_dimensions.items():
        figure = root / "results/figures/v2" / name
        width, height = png_dimensions(figure)
        if width < minimum[0] * 0.8 or height < minimum[1] * 0.8:
            raise ValidationError(f"Stage 5 figure dimensions are unexpectedly small: {name}")
        if figure.stat().st_size < 5000:
            raise ValidationError(f"Stage 5 figure is unexpectedly small: {name}")

    validate_private_material(root)
    validate_git_scope(root)

    print("STAGE 5 RELEASE-CANDIDATE VALIDATION PASSED")
    print("Stage 2–4 released evidence reconciles with all Stage 5 machine-readable values.")
    print("Abstract word count, source locators, claim restrictions, and governed documents reconcile.")
    print("Model C remains the preferred prediction model.")
    print("The negative Model D result and restricted global-shape result are retained.")
    print("Only aggregate outputs were produced; no new model was fitted.")
    print("Human review remains a separate gate.")
    print("Final V2 release, ARISE submission, and merge to main remain unauthorized.")


def self_test() -> None:
    assert close(1.0, "1")
    assert not close(1.0, 2.0)
    assert parse_bool("yes") is True
    assert parse_bool("0") is False
    sample = "# Title\n\n## Methods\nOne two three.\n\n**Word count:** 3\n"
    assert abstract_word_count(sample) == 3
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    validate(args.project_root)


if __name__ == "__main__":
    main()
