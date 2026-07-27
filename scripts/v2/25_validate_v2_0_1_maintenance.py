"""Validate the portable AgeLens V2.0.1 maintenance release."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

RELEASE = "v2.0.1"
RELEASE_DATE = "2026-07-27"
BASE_RELEASE_COMMIT = "d0a0ecfb9335cb5ef9f8c5f6e618db7ebe7ecc7b"
SCIENCE_TREE_SHA256 = "f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940"
SCIENCE_FILE_COUNT = 79


class ValidationError(RuntimeError):
    """Raised when the V2.0.1 maintenance release is inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def run_validator(root: Path, relative_script: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(root / relative_script), "--project-root", str(root)],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ValidationError(
            f"Dependency validator failed: {relative_script}\n"
            + (completed.stdout + "\n" + completed.stderr).strip()
        )
    if completed.stdout.strip():
        print(completed.stdout.strip())


def run_check(root: Path, relative_script: str) -> None:
    completed = subprocess.run(
        [sys.executable, str(root / relative_script), str(root)],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ValidationError(
            f"Repository check failed: {relative_script}\n"
            + (completed.stdout + "\n" + completed.stderr).strip()
        )
    if completed.stdout.strip():
        print(completed.stdout.strip())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in {
        ".csv", ".json", ".md", ".txt", ".py", ".r", ".yml",
        ".yaml", ".cff",
    }:
        text = data.decode("utf-8-sig")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return text.encode("utf-8")
    return data


def scientific_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted((root / "config").glob("v2_*.json")):
        rel = path.relative_to(root).as_posix()
        if rel in {
            "config/v2_stage5_release_candidate.json",
            "config/v2_0_1_maintenance.json",
            "config/v2_0_2_maintenance.json",
            "config/v2_0_3_maintenance.json",
            "config/v2_0_4_maintenance.json",
        }:
            continue
        paths.append(path)
    for path in sorted((root / "results/tables/v2").glob("*.csv")):
        if path.name == "21_stage5_source_manifest.csv":
            continue
        paths.append(path)
    paths.extend(sorted((root / "results/figures/v2").glob("*.png")))
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def science_digest(root: Path) -> tuple[int, str]:
    paths = scientific_paths(root)
    digest = hashlib.sha256()
    for path in paths:
        rel = path.relative_to(root).as_posix()
        sha = hashlib.sha256(canonical_bytes(path)).hexdigest()
        digest.update(rel.encode("utf-8") + b"\0" + sha.encode("ascii") + b"\0")
    return len(paths), digest.hexdigest()


def require_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise ValidationError(
                f"Required wording missing in {path.relative_to(path.parents[2] if len(path.parents) > 2 else path.parent)}: {phrase}"
            )


def parse_requirements(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, version = line.split("==", 1)
        pins[name.strip().lower()] = version.strip()
    return pins


def runtime_versions(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            row["component"].strip().lower(): row["version"].strip()
            for row in csv.DictReader(handle)
        }


def validate(root: Path) -> None:
    root = root.resolve()
    required = (
        "CITATION.cff",
        "README.md",
        "requirements-v2.txt",
        "config/v2_0_1_maintenance.json",
        "docs/v2/V2_0_1_Maintenance_Release.md",
        "docs/v2/V2_Environment.md",
        "release/v2_0_1_scientific_invariants.json",
        "scripts/preflight_repository.py",
        "scripts/check_governance_consistency.py",
        "scripts/v2/23_validate_stage5_release.py",
        "scripts/v2/24_validate_v2_final_release.py",
        "scripts/v2/25_validate_v2_0_1_maintenance.py",
    )
    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        raise ValidationError("Missing V2.0.1 artifacts: " + ", ".join(missing))

    run_check(root, "scripts/preflight_repository.py")
    run_check(root, "scripts/check_governance_consistency.py")
    run_validator(root, "scripts/v2/23_validate_stage5_release.py")
    run_validator(root, "scripts/v2/24_validate_v2_final_release.py")

    config = read_json(root / "config/v2_0_1_maintenance.json")
    expected = {
        "release": RELEASE,
        "release_tag": RELEASE,
        "date": RELEASE_DATE,
        "status": "final_public_maintenance_release_authorized",
        "base_release": "v2.0.0",
        "base_release_commit": BASE_RELEASE_COMMIT,
        "source_manifest_hash_rule": "sha256-canonical-lf-v1",
        "portable_validator": "scripts/v2/25_validate_v2_0_1_maintenance.py",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValidationError(f"Unexpected maintenance config value: {key}")

    scope = config.get("scope", {})
    true_scope = (
        "participant_level_notebook_previews_removed",
        "stage5_line_ending_independent_hashing",
        "citation_metadata_updated",
        "v2_environment_file_added",
        "current_documentation_reconciled",
        "ci_v2_release_checks_added",
        "portable_public_source_validation_added",
        "scientific_invariant_digest_recorded",
    )
    for key in true_scope:
        if scope.get(key) is not True:
            raise ValidationError("Maintenance scope flag missing: " + key)
    for key in (
        "scientific_analysis_changed",
        "scientific_results_changed",
        "aggregate_scientific_tables_or_figures_changed",
        "model_or_feature_search_performed",
    ):
        if scope.get(key) is not False:
            raise ValidationError("Scientific no-change flag invalid: " + key)

    permissions = config.get("permissions", {})
    for key in (
        "commit_to_v2_development_authorized",
        "annotated_v2_0_1_tag_authorized",
        "github_release_authorized",
    ):
        if permissions.get(key) is not True:
            raise ValidationError("Required maintenance permission missing: " + key)
    for key in (
        "merge_to_main_authorized",
        "arise_final_submission_authorized",
        "final_manuscript_claims_authorized",
        "new_model_feature_interaction_subgroup_or_tuning_search_authorized",
    ):
        if permissions.get(key) is not False:
            raise ValidationError("Restricted permission enabled: " + key)

    invariant = read_json(root / "release/v2_0_1_scientific_invariants.json")
    count, digest = science_digest(root)
    if count != SCIENCE_FILE_COUNT or digest != SCIENCE_TREE_SHA256:
        raise ValidationError(
            f"Scientific invariant tree changed: count={count}, digest={digest}"
        )
    if invariant.get("file_count") != count:
        raise ValidationError("Invariant file count does not reconcile.")
    if invariant.get("tree_sha256") != digest:
        raise ValidationError("Invariant tree digest does not reconcile.")

    versions = runtime_versions(root / "results/tables/v2/18_stage4_runtime_versions.csv")
    pins = parse_requirements(root / "requirements-v2.txt")
    expected_pins = {
        "numpy": versions["numpy"],
        "pandas": versions["pandas"],
        "scipy": versions["scipy"],
        "scikit-learn": versions["scikit-learn"],
        "interpret": versions["interpret"],
        "interpret-core": versions["interpret-core"],
    }
    for name, version in expected_pins.items():
        if pins.get(name) != version:
            raise ValidationError(f"V2 requirement pin mismatch: {name}")

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    if re.search(r"(?m)^version: 2\.0\.(?:1|2|3|4)\s*$", citation) is None:
        raise ValidationError(
            "CITATION.cff is not compatible with the V2.0.1 baseline."
        )
    if "date-released: 2026-07-27" not in citation:
        raise ValidationError("CITATION.cff release date changed.")

    require_phrases(
        root / "README.md",
        (
            "docs/v2/V2_0_1_Maintenance_Release.md",
            "requirements-v2.txt",
            "participant-level preview outputs removed",
        ),
    )
    require_phrases(
        root / "docs/v2/README.md",
        (
            "Original scientific release: `v2.0.0`",
            "V2_0_1_Maintenance_Release.md",
            "Historical Stage 5 Reviewed Aggregate Release",
            "scripts/v2/25_validate_v2_0_1_maintenance.py",
            "V2_Environment.md",
        ),
    )
    require_phrases(
        root / "docs/v2/V2_Research_Protocol.md",
        (
            "Historical Authorization Sequence",
            "Historical Stage 5 Authorization",
            "V2.0.1 Maintenance Release",
            "D2-028",
        ),
    )
    require_phrases(
        root / "docs/v2/V2_Decision_Log.md",
        (
            "D2-028",
            "Authorize the V2.0.1 public maintenance release",
        ),
    )
    require_phrases(
        root / "docs/v2/V2_Evidence_Gap_Register.md",
        (
            "V2-EG-021",
            "V2.0.1 Maintenance Integrity Disposition",
        ),
    )

    workflow = (root / ".github/workflows/repository-safety-check.yml").read_text(encoding="utf-8")
    for command in (
        "scripts/v2/23_validate_stage5_release.py",
        "scripts/v2/24_validate_v2_final_release.py",
        "scripts/v2/25_validate_v2_0_1_maintenance.py",
    ):
        if command not in workflow:
            raise ValidationError("CI command missing: " + command)

    print("V2.0.1 MAINTENANCE VALIDATION PASSED")
    print("Public-source validation works without a Git checkout.")
    print("Notebook previews and Stage 5 line-ending portability are corrected.")
    print("V2 citation, environment, documentation, and CI metadata reconcile.")
    print("All governed scientific configs, tables, figures, models, and conclusions are unchanged.")


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
