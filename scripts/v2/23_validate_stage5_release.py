"""Validate the AgeLens V2 Stage 5 reviewed release."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BUILD = "AgeLens-V2-Stage5-20260724b"
RELEASE_STATUS = "released_for_v2_development"


class ReleaseValidationError(RuntimeError):
    """Raised when the reviewed Stage 5 release is inconsistent."""


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


def run_validator(root: Path, relative_script: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(root / relative_script), "--project-root", str(root)],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ReleaseValidationError(
            f"Dependency validator failed: {relative_script}\n"
            + (completed.stdout + "\n" + completed.stderr).strip()
        )
    if completed.stdout.strip():
        print(completed.stdout.strip())


def require(root: Path, relpaths: tuple[str, ...]) -> None:
    missing = [rel for rel in relpaths if not (root / rel).is_file()]
    if missing:
        raise ReleaseValidationError("Missing Stage 5 release artifacts: " + ", ".join(missing))


def validate(root: Path) -> None:
    root = root.resolve()
    require(root, (
        "config/v2_stage5_synthesis.json",
        "config/v2_stage5_release_candidate.json",
        "config/v2_stage5_release.json",
        "docs/v2/V2_Stage5_Human_Review.md",
        "docs/v2/V2_Stage5_Release_Report.md",
        "results/tables/v2/23_stage5_release_summary.csv",
        "scripts/v2/21_build_stage5_synthesis.py",
        "scripts/v2/22_validate_stage5_release_candidate.py",
        "scripts/v2/23_validate_stage5_release.py",
    ))

    run_validator(root, "scripts/v2/22_validate_stage5_release_candidate.py")

    implementation = read_json(root / "config/v2_stage5_synthesis.json")
    candidate = read_json(root / "config/v2_stage5_release_candidate.json")
    release = read_json(root / "config/v2_stage5_release.json")

    if implementation.get("build") != BUILD or candidate.get("build") != BUILD:
        raise ReleaseValidationError("Corrected Stage 5 build identifier is missing.")
    if release.get("source_build") != BUILD:
        raise ReleaseValidationError("Release source build does not match corrected build.")
    if release.get("status") != RELEASE_STATUS:
        raise ReleaseValidationError("Stage 5 release status changed.")
    if release.get("human_review_decision") != "pass_with_guardrails_after_corrective_revision":
        raise ReleaseValidationError("Stage 5 human-review decision changed.")

    corrections = release.get("corrective_revisions", {})
    required_corrections = (
        "independent_validator_expanded_to_row_level_numeric_reconciliation",
        "scientific_summary_and_claims_matrix_row_or_field_locators_added",
        "abstract_race_ethnicity_social_classification_guardrail_added",
        "progression_figure_transportability_wording_restricted",
    )
    for key in required_corrections:
        if corrections.get(key) is not True:
            raise ReleaseValidationError(f"Required corrective revision is not recorded: {key}")

    relationship = release.get("relationship_to_v1", {})
    if relationship.get("v1_immutable") is not True:
        raise ReleaseValidationError("V1 immutability changed.")
    for key in (
        "v1_formula_changed",
        "v1_harmonization_changed",
        "v1_mortality_changed",
        "v1_results_changed",
    ):
        if relationship.get(key) is not False:
            raise ReleaseValidationError(f"V1 change flag enabled: {key}")

    permissions = release.get("permissions", {})
    for key in (
        "commit_to_v2_development_authorized",
        "stage5_aggregate_synthesis_release_authorized",
        "arise_working_materials_release_authorized",
    ):
        if permissions.get(key) is not True:
            raise ReleaseValidationError(f"Required release permission missing: {key}")
    for key in (
        "final_v2_release_authorized",
        "arise_final_submission_authorized",
        "final_manuscript_claims_authorized",
        "merge_to_main_authorized",
        "new_model_feature_interaction_or_tuning_search_authorized",
    ):
        if permissions.get(key) is not False:
            raise ReleaseValidationError(f"Restricted release permission enabled: {key}")

    decision = release.get("scientific_decision", {})
    if decision.get("preferred_prediction_model") != "Stage3_Model_C":
        raise ReleaseValidationError("Preferred prediction model changed.")
    if decision.get("model_d_incremental_benefit_supported") is not False:
        raise ReleaseValidationError("Model D incremental-benefit decision changed.")
    if decision.get("stage2_nonlinearity_retained") is not True:
        raise ReleaseValidationError("Stage 2 nonlinearity was not retained.")
    if decision.get("stage3_transportability_restricted") is not True:
        raise ReleaseValidationError("Stage 3 transportability restriction changed.")
    if decision.get("null_and_negative_findings_retained") is not True:
        raise ReleaseValidationError("Null or negative findings are not retained.")

    human_review = (root / "docs/v2/V2_Stage5_Human_Review.md").read_text(encoding="utf-8")
    for phrase in (
        "| Status | Completed |",
        "| Decision | Pass with guardrails after corrective revision |",
        "Applying the release package records the project owner's acceptance",
        "final V2 release, final manuscript claims, final ARISE submission, or merge to `main`",
    ):
        if phrase not in human_review:
            raise ReleaseValidationError("Human-review record is incomplete: " + phrase)
    if "| Pass |" not in human_review or "| Pass after revision |" not in human_review:
        raise ReleaseValidationError("Human-review checklist decisions are incomplete.")

    report = (root / "docs/v2/V2_Stage5_Release_Report.md").read_text(encoding="utf-8")
    for phrase in (
        "Pass for commit to `v2-development`",
        "Model C remains preferred",
        "race/ethnicity is a social classification",
        "final ARISE submission",
        "merge to `main`",
    ):
        if phrase not in report:
            raise ReleaseValidationError("Stage 5 release report guardrail missing: " + phrase)

    abstract = (root / "docs/v2/V2_ARISE_Abstract.md").read_text(encoding="utf-8")
    if "treated strictly as a social classification" not in abstract:
        raise ReleaseValidationError("Corrected abstract social-classification guardrail is missing.")
    if "pooled out-of-cycle prediction" not in abstract:
        raise ReleaseValidationError("Corrected abstract out-of-cycle wording is missing.")

    progression_script = (root / "scripts/v2/21_build_stage5_synthesis.py").read_text(encoding="utf-8")
    if "Restricted transportability\\nPooled out-of-cycle prediction" not in progression_script:
        raise ReleaseValidationError("Corrected progression-figure wording is missing from the builder.")

    scientific_rows = read_csv(root / "results/tables/v2/21_stage5_scientific_summary.csv")
    if not scientific_rows or any("::" not in row["source_artifact"] for row in scientific_rows):
        raise ReleaseValidationError("Scientific-summary row/field source locators are incomplete.")
    claims_rows = read_csv(root / "results/tables/v2/21_stage5_claims_matrix.csv")
    if not claims_rows or any("::" not in row["source"] for row in claims_rows):
        raise ReleaseValidationError("Claims-matrix row/field source locators are incomplete.")

    release_rows = read_csv(root / "results/tables/v2/23_stage5_release_summary.csv")
    decisions = {row["component"]: row["decision"] for row in release_rows}
    expected = {
        "stage5_aggregate_synthesis": "released_for_v2_development",
        "arise_working_abstract": "released_with_guardrails",
        "arise_working_presentation": "released_with_guardrails",
        "preferred_prediction_model": "Stage3_Model_C",
        "model_d_incremental_claim": "not_supported",
        "final_v2_release": "not_authorized",
        "arise_final_submission": "not_authorized",
        "merge_to_main": "not_authorized",
    }
    for component, expected_decision in expected.items():
        if decisions.get(component) != expected_decision:
            raise ReleaseValidationError(f"Release-summary decision changed: {component}")

    print("STAGE 5 RELEASE VALIDATION PASSED")
    print("Human review decision: pass with guardrails after corrective revision.")
    print("Stage 5 aggregate synthesis and ARISE working materials may be committed to v2-development.")
    print("Model C remains the preferred prediction model.")
    print("The negative Model D result and restricted global-shape result are retained.")
    print("Final V2 release, final manuscript claims, final ARISE submission, and merge to main remain unauthorized.")


def self_test() -> None:
    assert BUILD.endswith("b")
    assert RELEASE_STATUS == "released_for_v2_development"
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    validate(args.project_root)


if __name__ == "__main__":
    main()
