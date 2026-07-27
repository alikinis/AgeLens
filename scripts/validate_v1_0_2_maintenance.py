"""Validate the AgeLens V1.0.2 dependency-documentation patch."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

RELEASE = "v1.0.2"
DATE = "2026-07-27"


class ValidationError(RuntimeError):
    """Raised when the V1.0.2 maintenance package is inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def run_validator(root: Path, relative_script: str) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(root / relative_script),
            "--project-root",
            str(root),
        ],
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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise ValidationError(
                f"Required wording missing in {path.as_posix()}: {phrase}"
            )


def validate(root: Path) -> None:
    root = root.resolve()
    required = (
        "CITATION.cff",
        "README.md",
        "R_PACKAGES.md",
        "release/v1_0_1_maintenance.json",
        "release/v1_0_2_maintenance.json",
        "scripts/prepare_repository.py",
        "scripts/validate_v1_0_1_maintenance.py",
        "scripts/validate_v1_0_2_maintenance.py",
    )
    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        raise ValidationError(
            "Missing V1.0.2 artifacts: " + ", ".join(missing)
        )

    run_validator(root, "scripts/validate_v1_0_1_maintenance.py")

    config = read_json(root / "release/v1_0_2_maintenance.json")
    expected = {
        "release": RELEASE,
        "release_tag": RELEASE,
        "date": DATE,
        "status": "public_documentation_maintenance_authorized",
        "base_release": "v1.0.1",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValidationError(
                f"Unexpected V1.0.2 maintenance value: {key}"
            )

    scope = config.get("scope", {})
    for key in (
        "r_dependency_documentation_completed",
        "readme_citation_updated",
        "citation_metadata_updated",
        "public_snapshot_validation_updated",
        "ci_validation_updated",
    ):
        if scope.get(key) is not True:
            raise ValidationError("Maintenance scope flag missing: " + key)

    for key in (
        "scientific_code_changed",
        "scientific_calculations_changed",
        "scientific_results_changed",
        "aggregate_tables_or_figures_changed",
        "notebooks_changed",
    ):
        if scope.get(key) is not False:
            raise ValidationError("Scientific no-change flag invalid: " + key)

    require_phrases(
        root / "CITATION.cff",
        (
            "version: 1.0.2",
            "date-released: 2026-07-27",
        ),
    )
    require_phrases(
        root / "README.md",
        (
            "Maintenance release:** `v1.0.2`",
            "Version 1.0.2. 2026.",
            "R dependency documentation",
        ),
    )
    require_phrases(
        root / "R_PACKAGES.md",
        (
            '"survey"',
            '"survival"',
            '"dplyr"',
            '"remotes"',
            '"flexsurv"',
            'dayoonkwon/BioAge@b1f9fc0',
            'upgrade = "never"',
        ),
    )
    require_phrases(
        root / "scripts/prepare_repository.py",
        (
            "validate_v1_0_2_maintenance.py",
            "V1.0.2 maintenance validation failed.",
        ),
    )
    require_phrases(
        root / ".github/workflows/repository-safety-check.yml",
        (
            "scripts/validate_v1_0_2_maintenance.py",
            "Check V1.0.2 maintenance package",
            "Check public snapshot builder",
        ),
    )

    print("V1.0.2 MAINTENANCE VALIDATION PASSED")
    print("R dependency documentation is complete and pinned where governed.")
    print("README and CITATION metadata reconcile to V1.0.2.")
    print("The public snapshot builder and CI use the current validator.")
    print(
        "V1 scientific code, notebooks, calculations, results, "
        "tables, and figures are unchanged."
    )


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
