"""Validate the AgeLens V2.0.2 documentation and tooling maintenance release."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

RELEASE = "v2.0.2"
DATE = "2026-07-27"
BASE_RELEASE = "v2.0.1"
BASE_RELEASE_COMMIT = "65726b0cd80947f3f724dccccdce7619cb1737b5"
SCIENCE_TREE_SHA256 = "f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940"
SCIENCE_FILE_COUNT = 79


class ValidationError(RuntimeError):
    """Raised when the V2.0.2 maintenance package is inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


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
    excluded_configs = {
        "config/v2_stage5_release_candidate.json",
        "config/v2_0_1_maintenance.json",
        "config/v2_0_2_maintenance.json",
        "config/v2_0_3_maintenance.json",
    }
    for path in sorted((root / "config").glob("v2_*.json")):
        if path.relative_to(root).as_posix() in excluded_configs:
            continue
        paths.append(path)
    for path in sorted((root / "results/tables/v2").glob("*.csv")):
        if path.name == "21_stage5_source_manifest.csv":
            continue
        paths.append(path)
    paths.extend(sorted((root / "results/figures/v2").glob("*.png")))
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def science_digest(root: Path) -> tuple[int, str]:
    paths = scientific_paths(root)
    digest = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(root).as_posix()
        sha256 = hashlib.sha256(canonical_bytes(path)).hexdigest()
        digest.update(
            relative.encode("utf-8")
            + b"\0"
            + sha256.encode("ascii")
            + b"\0"
        )
    return len(paths), digest.hexdigest()


def require_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise ValidationError(
                f"Required wording missing in {path.as_posix()}: {phrase}"
            )


def run_script(
    root: Path,
    relative_script: str,
    *,
    project_root_flag: bool,
) -> None:
    command = [sys.executable, str(root / relative_script)]
    if project_root_flag:
        command.extend(["--project-root", str(root)])
    else:
        command.append(str(root))
    completed = subprocess.run(
        command,
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


def copy_source_without_git(root: Path, destination: Path) -> None:
    if (root / ".git").exists():
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "-co",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
        )
        if completed.returncode != 0:
            raise ValidationError(
                "Unable to enumerate repository files:\n"
                + completed.stderr.decode("utf-8", errors="replace")
            )
        names = [
            item.decode("utf-8", errors="strict")
            for item in completed.stdout.split(b"\0")
            if item
        ]
        for relative in names:
            source = root / relative
            if not source.is_file():
                continue
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        return

    shutil.copytree(
        root,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            ".mypy_cache",
        ),
    )


def validate_v2_0_1_baseline_portably(root: Path) -> None:
    with tempfile.TemporaryDirectory(
        prefix="agelens_v2_0_2_baseline_"
    ) as temporary:
        source_copy = Path(temporary) / "AgeLens-v2.0.2-source"
        copy_source_without_git(root, source_copy)
        run_script(
            source_copy,
            "scripts/v2/25_validate_v2_0_1_maintenance.py",
            project_root_flag=True,
        )


def validate(root: Path) -> None:
    root = root.resolve()
    required = (
        ".github/workflows/repository-safety-check.yml",
        "CITATION.cff",
        "PUBLIC_CLEANUP_REPORT.md",
        "README.md",
        "R_PACKAGES.md",
        "requirements-v2.txt",
        "config/v2_0_1_maintenance.json",
        "config/v2_0_2_maintenance.json",
        "docs/v2/README.md",
        "docs/v2/V2_0_1_Maintenance_Release.md",
        "docs/v2/V2_0_2_Maintenance_Release.md",
        "docs/v2/V2_Decision_Log.md",
        "docs/v2/V2_Evidence_Gap_Register.md",
        "docs/v2/V2_Research_Protocol.md",
        "release/v2_0_1_scientific_invariants.json",
        "release/v2_0_2_scientific_invariants.json",
        "scripts/prepare_repository.py",
        "scripts/v2/25_validate_v2_0_1_maintenance.py",
        "scripts/v2/26_validate_v2_0_2_maintenance.py",
    )
    missing = [relative for relative in required if not (root / relative).is_file()]
    if missing:
        raise ValidationError(
            "Missing V2.0.2 artifacts: " + ", ".join(missing)
        )

    validate_v2_0_1_baseline_portably(root)

    config = read_json(root / "config/v2_0_2_maintenance.json")
    expected = {
        "release": RELEASE,
        "release_tag": RELEASE,
        "date": DATE,
        "status": "public_documentation_tooling_maintenance_authorized",
        "base_release": BASE_RELEASE,
        "base_release_commit": BASE_RELEASE_COMMIT,
        "portable_validator": "scripts/v2/26_validate_v2_0_2_maintenance.py",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValidationError(
                f"Unexpected V2.0.2 maintenance value: {key}"
            )

    scope = config.get("scope", {})
    for key in (
        "v2_root_quick_start_corrected",
        "r_dependency_documentation_completed",
        "public_snapshot_builder_completed",
        "readme_citation_updated",
        "citation_metadata_updated",
        "ci_snapshot_validation_added",
        "historical_v2_0_1_validator_compatibility_updated",
        "scientific_invariant_digest_recorded",
    ):
        if scope.get(key) is not True:
            raise ValidationError("Maintenance scope flag missing: " + key)

    for key in (
        "scientific_analysis_changed",
        "scientific_results_changed",
        "scientific_configs_changed",
        "aggregate_scientific_tables_or_figures_changed",
        "models_or_features_changed",
        "notebooks_changed",
    ):
        if scope.get(key) is not False:
            raise ValidationError("Scientific no-change flag invalid: " + key)

    permissions = config.get("permissions", {})
    for key in (
        "commit_to_v2_development_authorized",
        "annotated_v2_0_2_tag_authorized",
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

    count, digest = science_digest(root)
    if count != SCIENCE_FILE_COUNT or digest != SCIENCE_TREE_SHA256:
        raise ValidationError(
            f"Scientific invariant tree changed: count={count}, digest={digest}"
        )

    old_invariant = read_json(
        root / "release/v2_0_1_scientific_invariants.json"
    )
    new_invariant = read_json(
        root / "release/v2_0_2_scientific_invariants.json"
    )
    for invariant, label in (
        (old_invariant, "V2.0.1"),
        (new_invariant, "V2.0.2"),
    ):
        if invariant.get("file_count") != count:
            raise ValidationError(f"{label} invariant file count mismatch.")
        if invariant.get("tree_sha256") != digest:
            raise ValidationError(f"{label} invariant digest mismatch.")

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    if not any(
        marker in citation
        for marker in ("version: 2.0.2", "version: 2.0.3")
    ):
        raise ValidationError(
            "CITATION.cff is not compatible with the V2.0.2 baseline."
        )
    if "date-released: 2026-07-27" not in citation:
        raise ValidationError("CITATION.cff release date changed.")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "AgeLens V2.0.2",
        "docs/v2/V2_0_2_Maintenance_Release.md",
        "AgeLens V2.0.1",
        "docs/v2/V2_0_1_Maintenance_Release.md",
        "V1.0.2",
        "Python-3.13.14",
        "](requirements-v2.txt)",
        "pip install -r requirements-v2.txt",
        "| Python | 3.13.14 |",
        "| pandas | 3.0.5 |",
        "| SciPy | 1.18.0 |",
        "| scikit-learn | 1.9.0 |",
        "| `interpret` | 0.7.8 |",
    ):
        if phrase not in readme:
            raise ValidationError("README correction missing: " + phrase)
    for forbidden in (
        "pip install -r requirements.txt",
        "| Python | 3.x |",
        "| pandas | 2.3.3 |",
        "Version 1.0.0. 2026.",
        "](requirements.txt)",
    ):
        if forbidden in readme:
            raise ValidationError(
                "Stale V1-oriented README instruction remains: " + forbidden
            )

    require_phrases(
        root / "R_PACKAGES.md",
        (
            '"survey"',
            '"survival"',
            '"dplyr"',
            '"remotes"',
            '"flexsurv"',
            "dayoonkwon/BioAge@b1f9fc0",
            'upgrade = "never"',
        ),
    )
    require_phrases(
        root / "scripts/prepare_repository.py",
        (
            '"requirements-v2.txt"',
        ),
    )
    require_phrases(
        root / ".github/workflows/repository-safety-check.yml",
        (
            "scripts/v2/26_validate_v2_0_2_maintenance.py",
            "Check V2.0.2 maintenance release",
            "Check public snapshot builder",
        ),
    )
    require_phrases(
        root / "docs/v2/README.md",
        (
            "Prior public maintenance release: `v2.0.2`",
            "Earlier public maintenance release: `v2.0.1`",
            "V2_0_2_Maintenance_Release.md",
            "config/v2_0_2_maintenance.json",
            "scripts/v2/26_validate_v2_0_2_maintenance.py",
        ),
    )
    require_phrases(
        root / "docs/v2/V2_Research_Protocol.md",
        (
            "V2.0.2 documentation and repository-tooling corrections",
            "D2-029",
        ),
    )
    require_phrases(
        root / "docs/v2/V2_Decision_Log.md",
        (
            "D2-029",
            "Authorize the V2.0.2 documentation and tooling maintenance release",
        ),
    )
    require_phrases(
        root / "docs/v2/V2_Evidence_Gap_Register.md",
        (
            "V2-EG-022",
            "V2.0.2 Documentation and Tooling Integrity Disposition",
        ),
    )
    require_phrases(
        root / "PUBLIC_CLEANUP_REPORT.md",
        (
            "V2.0.2",
            "public-snapshot builder",
            "R dependency",
        ),
    )

    print("V2.0.2 MAINTENANCE VALIDATION PASSED")
    print("The V2 root quick-start and governed environment instructions reconcile.")
    print("R dependency documentation is complete and the public snapshot builder is portable.")
    print("CI validates both the current release and a generated public snapshot.")
    print("All governed scientific configs, tables, figures, models, notebooks, and conclusions are unchanged.")


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
