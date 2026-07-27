"""Validate the AgeLens V2.0.0 final public-release package."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

RELEASE_TAG = "v2.0.0"
SOURCE_COMMIT = "b8216019fee4aea339ba1eae8fdd3e17e530fbd9"

EXPECTED_CHANGE_SCOPE = {
    "config/v2_final_release.json",
    "docs/v2/README.md",
    "docs/v2/V2_ARISE_Presentation.md",
    "docs/v2/V2_Decision_Log.md",
    "docs/v2/V2_Evidence_Gap_Register.md",
    "docs/v2/V2_Final_Release.md",
    "docs/v2/V2_Research_Protocol.md",
    "scripts/v2/24_validate_v2_final_release.py",
}


class ValidationError(RuntimeError):
    """Raised when the V2 final-release package is inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def run_git(
    root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
    )

    if check and completed.returncode != 0:
        raise ValidationError(
            "Git command failed: git "
            + " ".join(args)
            + "\n"
            + (completed.stdout + "\n" + completed.stderr).strip()
        )

    return completed


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def changed_paths(root: Path) -> set[str]:
    completed = run_git(root, "status", "--porcelain")
    paths: set[str] = set()

    for line in completed.stdout.splitlines():
        if not line.strip():
            continue

        path = line[3:]

        if " -> " in path:
            path = path.split(" -> ", 1)[1]

        paths.add(path.replace("\\", "/"))

    return paths


def require_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")

    for phrase in phrases:
        if phrase not in text:
            raise ValidationError(
                f"Required wording missing in {path.as_posix()}: {phrase}"
            )


def validate(root: Path) -> None:
    root = root.resolve()

    required_files = (
        "config/v2_stage5_release.json",
        "config/v2_final_release.json",
        "docs/v2/V2_Stage5_Human_Review.md",
        "docs/v2/V2_Final_Release.md",
        "scripts/v2/23_validate_stage5_release.py",
        "scripts/v2/24_validate_v2_final_release.py",
    )

    missing = [
        path for path in required_files
        if not (root / path).is_file()
    ]

    if missing:
        raise ValidationError(
            "Missing final-release files: " + ", ".join(missing)
        )

    branch = run_git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "HEAD",
    ).stdout.strip()

    if branch != "v2-development":
        raise ValidationError(
            "Final release must be prepared on v2-development."
        )

    ancestor = run_git(
        root,
        "merge-base",
        "--is-ancestor",
        SOURCE_COMMIT,
        "HEAD",
        check=False,
    )

    if ancestor.returncode != 0:
        raise ValidationError(
            "The governed pre-release commit is not an ancestor of HEAD."
        )

    unexpected = changed_paths(root) - EXPECTED_CHANGE_SCOPE

    if unexpected:
        raise ValidationError(
            "Changes outside final-release scope: "
            + ", ".join(sorted(unexpected))
        )

    stage5 = read_json(root / "config/v2_stage5_release.json")
    historical = stage5.get("permissions", {})

    for key in (
        "final_v2_release_authorized",
        "arise_final_submission_authorized",
        "final_manuscript_claims_authorized",
        "merge_to_main_authorized",
    ):
        if historical.get(key) is not False:
            raise ValidationError(
                "Historical Stage 5 gate was altered: " + key
            )

    release = read_json(root / "config/v2_final_release.json")

    expected_values = {
        "document_version": "1.0",
        "release_version": "2.0.0",
        "release_tag": RELEASE_TAG,
        "status": "final_public_release_authorized",
        "source_branch": "v2-development",
        "pre_release_source_commit": SOURCE_COMMIT,
    }

    for key, expected in expected_values.items():
        if release.get(key) != expected:
            raise ValidationError(
                f"Unexpected final-release value for {key}."
            )

    owner = release.get("project_owner_review", {})

    if owner.get("status") != "completed":
        raise ValidationError("Project-owner final review is incomplete.")

    if owner.get("decision") != "authorize_final_public_v2_release":
        raise ValidationError("Project-owner decision changed.")

    if owner.get("scientific_scope_changed") is not False:
        raise ValidationError("Final review changed scientific scope.")

    if owner.get("new_analysis_or_model_fitted") is not False:
        raise ValidationError("Final review introduced new modeling.")

    scientific = release.get("scientific_decision", {})

    if scientific.get("preferred_prediction_model") != "Stage3_Model_C":
        raise ValidationError("Preferred model changed.")

    if scientific.get("model_d_incremental_benefit_supported") is not False:
        raise ValidationError("Model D decision changed.")

    for key in (
        "stage2_nonlinearity_retained",
        "stage3_transportability_restricted",
        "null_and_negative_findings_retained",
    ):
        if scientific.get(key) is not True:
            raise ValidationError(
                "Required scientific restriction missing: " + key
            )

    relationship = release.get("relationship_to_v1", {})

    if relationship.get("v1_immutable") is not True:
        raise ValidationError("V1 immutability changed.")

    for key in (
        "v1_formula_changed",
        "v1_harmonization_changed",
        "v1_mortality_changed",
        "v1_results_changed",
        "merge_to_main_required",
    ):
        if relationship.get(key) is not False:
            raise ValidationError("Invalid V1 or merge flag: " + key)

    permissions = release.get("permissions", {})

    for key in (
        "final_v2_public_release_authorized",
        "annotated_v2_0_0_tag_authorized",
        "github_release_authorized",
    ):
        if permissions.get(key) is not True:
            raise ValidationError(
                "Required permission missing: " + key
            )

    for key in (
        "arise_final_submission_authorized",
        "final_manuscript_claims_authorized",
        "merge_to_main_authorized",
        "new_model_feature_interaction_subgroup_or_tuning_search_authorized",
    ):
        if permissions.get(key) is not False:
            raise ValidationError(
                "Restricted permission enabled: " + key
            )

    require_phrases(
        root / "docs/v2/V2_Final_Release.md",
        (
            "AgeLens V2.0.0 Final Public Release",
            "Model C remains the preferred prediction model.",
            "did not demonstrate incremental predictive improvement",
            "Race/ethnicity is treated strictly as a social classification.",
            "final ARISE form submission",
            "merge to `main`",
        ),
    )

    require_phrases(
        root / "docs/v2/README.md",
        (
            "AgeLens V2 final public release authorized as `v2.0.0`",
            "V1 remains frozen on `main`",
            "Final ARISE submission remains",
            "scripts/v2/24_validate_v2_final_release.py",
        ),
    )

    require_phrases(
        root / "docs/v2/V2_Research_Protocol.md",
        (
            "| Version | 1.2 |",
            "Final public release `v2.0.0`",
            "AGELENS_V2_FINAL_RELEASE_BEGIN",
        ),
    )

    require_phrases(
        root / "docs/v2/V2_Decision_Log.md",
        (
            "| Version | 1.5 |",
            "D2-027",
            "Authorize the final public AgeLens V2 release as `v2.0.0`",
        ),
    )

    require_phrases(
        root / "docs/v2/V2_Evidence_Gap_Register.md",
        (
            "| Version | 1.5 |",
            "Closed for V2.0.0 public release",
            "Final V2 Release Disposition",
        ),
    )

    require_phrases(
        root / "docs/v2/V2_ARISE_Presentation.md",
        (
            "Final V2 public release is complete; "
            "ARISE submission remains pending",
        ),
    )

    tag = run_git(
        root,
        "rev-parse",
        "-q",
        "--verify",
        f"refs/tags/{RELEASE_TAG}^{{commit}}",
        check=False,
    )

    if tag.returncode == 0:
        tag_commit = tag.stdout.strip()
        head_commit = run_git(root, "rev-parse", "HEAD").stdout.strip()

        if tag_commit != head_commit:
            raise ValidationError(
                f"{RELEASE_TAG} exists but does not point to HEAD."
            )

    print("V2 FINAL RELEASE VALIDATION PASSED")
    print("AgeLens V2.0.0 final public release is authorized.")
    print("Model C remains the preferred prediction model.")
    print("V1 remains frozen and separate on main.")
    print(
        "Final ARISE submission, final manuscript claims, "
        "and merge to main remain unauthorized."
    )


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
