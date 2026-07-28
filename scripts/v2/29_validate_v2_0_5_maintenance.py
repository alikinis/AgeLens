"""Validate the AgeLens V2.0.5 release-date metadata maintenance."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

RELEASE = "v2.0.5"
DATE = "2026-07-28"
BASE_RELEASE = "v2.0.4"
BASE_RELEASE_COMMIT = "7dddcf03f2cc7ca3ed0b78afd4de52b3d1f11c95"
V204_PUBLISHED_AT = "2026-07-28T06:06:29Z"
LEGACY_TREE = "f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940"
EXPANDED_TREE = "e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef"


class ValidationError(RuntimeError):
    """Raised when V2.0.5 metadata maintenance is inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise ValidationError(
                f"Required wording missing in {path.as_posix()}: {phrase}"
            )


def run_validator(root: Path, relative_script: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(root / relative_script), "--project-root", str(root)],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ValidationError(
            f"Dependency validation failed: {relative_script}\n"
            + (completed.stdout + "\n" + completed.stderr).strip()
        )
    if completed.stdout.strip():
        print(completed.stdout.strip())


def validate(root: Path) -> None:
    root = root.resolve()
    required = (
        ".github/workflows/repository-safety-check.yml",
        "CITATION.cff",
        "PUBLIC_CLEANUP_REPORT.md",
        "README.md",
        "config/v2_0_4_maintenance.json",
        "config/v2_0_5_maintenance.json",
        "docs/v2/README.md",
        "docs/v2/V2_0_4_Maintenance_Release.md",
        "docs/v2/V2_0_5_Maintenance_Release.md",
        "docs/v2/V2_Decision_Log.md",
        "docs/v2/V2_Evidence_Gap_Register.md",
        "docs/v2/V2_Research_Protocol.md",
        "release/v2_0_5_scientific_invariants.json",
        "scripts/prepare_repository.py",
        "scripts/v2/28_validate_v2_0_4_maintenance.py",
        "scripts/v2/29_validate_v2_0_5_maintenance.py",
    )
    missing = [relative for relative in required if not (root / relative).is_file()]
    if missing:
        raise ValidationError("Missing V2.0.5 artifacts: " + ", ".join(missing))

    run_validator(root, "scripts/v2/28_validate_v2_0_4_maintenance.py")

    config = read_json(root / "config/v2_0_5_maintenance.json")
    expected = {
        "release": RELEASE,
        "release_tag": RELEASE,
        "date": DATE,
        "status": "public_release_date_metadata_correction_authorized",
        "base_release": BASE_RELEASE,
        "base_release_commit": BASE_RELEASE_COMMIT,
        "corrected_release": "v2.0.4",
        "corrected_github_release_published_at": V204_PUBLISHED_AT,
        "portable_validator": "scripts/v2/29_validate_v2_0_5_maintenance.py",
        "legacy_scientific_invariant_tree_sha256": LEGACY_TREE,
        "legacy_scientific_invariant_file_count": 79,
        "expanded_scientific_invariant_tree_sha256": EXPANDED_TREE,
        "expanded_scientific_invariant_file_count": 108,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValidationError("Unexpected V2.0.5 maintenance value: " + key)

    for key in (
        "v2_0_4_publication_date_metadata_corrected",
        "citation_and_current_release_metadata_updated",
        "ci_and_snapshot_current_validator_updated",
        "historical_v2_0_1_validator_compatibility_updated",
        "historical_v2_0_2_validator_compatibility_updated",
        "historical_v2_0_3_validator_compatibility_updated",
        "historical_v2_0_4_validator_compatibility_updated",
    ):
        if config.get("scope", {}).get(key) is not True:
            raise ValidationError("Maintenance scope flag missing: " + key)

    for key in (
        "scientific_analysis_changed",
        "scientific_results_changed",
        "scientific_configs_changed",
        "aggregate_scientific_tables_or_figures_changed",
        "models_or_features_changed",
        "notebooks_changed",
        "analysis_or_execution_scripts_changed",
    ):
        if config.get("scope", {}).get(key) is not False:
            raise ValidationError("Scientific no-change flag invalid: " + key)

    v204 = read_json(root / "config/v2_0_4_maintenance.json")
    corrected = {
        "date": DATE,
        "maintenance_work_date": "2026-07-27",
        "github_release_published_at": V204_PUBLISHED_AT,
        "publication_metadata_corrected_in": RELEASE,
    }
    for key, value in corrected.items():
        if v204.get(key) != value:
            raise ValidationError("V2.0.4 publication metadata mismatch: " + key)

    invariant = read_json(root / "release/v2_0_5_scientific_invariants.json")
    for key, value in {
        "release": RELEASE,
        "base_release": BASE_RELEASE,
        "legacy_file_count": 79,
        "legacy_tree_sha256": LEGACY_TREE,
        "expanded_file_count": 108,
        "expanded_tree_sha256": EXPANDED_TREE,
    }.items():
        if invariant.get(key) != value:
            raise ValidationError("V2.0.5 invariant record mismatch: " + key)

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    if "version: 2.0.5" not in citation or "date-released: 2026-07-28" not in citation:
        raise ValidationError("CITATION.cff is not synchronized to V2.0.5.")

    require_phrases(root / "README.md", (
        "AgeLens V2.0.5",
        "V2_0_5_Maintenance_Release.md",
        "Version 2.0.5. 2026.",
    ))
    require_phrases(root / "docs/v2/README.md", (
        "Current public maintenance release: `v2.0.5`",
        "prior public maintenance release: `v2.0.4`",
        "V2_0_5_Maintenance_Release.md",
        "config/v2_0_5_maintenance.json",
        "29_validate_v2_0_5_maintenance.py",
    ))
    require_phrases(root / "docs/v2/V2_0_4_Maintenance_Release.md", (
        V204_PUBLISHED_AT,
        "maintenance work was completed on 2026-07-27",
        "V2.0.5",
    ))
    require_phrases(root / "docs/v2/V2_Decision_Log.md", (
        "| Version | 2.0 |",
        "| Date | 2026-07-28 |",
        "D2-032",
        "Authorize the V2.0.5 release-date metadata maintenance release",
    ))
    require_phrases(root / "docs/v2/V2_Evidence_Gap_Register.md", (
        "| Version | 2.0 |",
        "V2-EG-025",
        "V2.0.5 Release-Date Metadata Integrity Disposition",
    ))
    require_phrases(root / "docs/v2/V2_Research_Protocol.md", (
        "| Version | 1.7 |",
        "Final public maintenance release `v2.0.5`",
        "D2-032",
    ))
    require_phrases(root / "PUBLIC_CLEANUP_REPORT.md", (
        "V2.0.5",
        V204_PUBLISHED_AT,
        "2026-07-28",
    ))
    require_phrases(root / ".github/workflows/repository-safety-check.yml", (
        "scripts/v2/29_validate_v2_0_5_maintenance.py",
        "Check V2.0.5 maintenance release",
        "Check public snapshot builder",
    ))
    require_phrases(root / "scripts/prepare_repository.py", (
        "29_validate_v2_0_5_maintenance.py",
        "V2.0.5 maintenance validation",
    ))

    print("V2.0.5 MAINTENANCE VALIDATION PASSED")
    print("The V2.0.4 public publication timestamp is recorded as 2026-07-28T06:06:29Z.")
    print("The V2.0.4 maintenance-work date remains explicitly recorded as 2026-07-27.")
    print("The 79-file and expanded 108-file scientific invariants are unchanged.")
    print("Hosted GitHub Actions must pass before the v2.0.5 tag and release are created.")


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
