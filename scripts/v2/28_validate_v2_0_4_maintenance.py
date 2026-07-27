"""Validate the AgeLens V2.0.4 CI runtime maintenance release."""

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
from typing import Any, Iterable

RELEASE = "v2.0.4"
DATE = "2026-07-27"
BASE_RELEASE = "v2.0.3"
BASE_RELEASE_COMMIT = "01f85816f4de7aa73d1159860733845bc9af95d6"
LEGACY_TREE_SHA256 = "f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940"
LEGACY_FILE_COUNT = 79
EXPANDED_TREE_SHA256 = "e186e85deaf0abc5f7b7cca6d94efcfe1bd07de155f371c7030fece00a4b1fef"
EXPANDED_FILE_COUNT = 108
CATEGORY_COUNTS = {
    "governed_configs_tables_figures": 79,
    "public_notebooks": 14,
    "analysis_scripts": 4,
    "v2_scientific_execution_scripts": 11
}
CATEGORY_DIGESTS = {
    "governed_configs_tables_figures": "f3ab99ccfa6252177d54491729d93fb326246879e8974e1070360d073fc0c940",
    "public_notebooks": "ccd03164f7330e9873b227dd4431ac4077c240694aa973bbb8e6a6fe1228190f",
    "analysis_scripts": "6fd3642b34a90c8bd511fef99f63da4ebaa3c87a754397727884986aebd78914",
    "v2_scientific_execution_scripts": "4071775040bbedda9ac4563a1408e5f4b2d7161127ccf512dc7feece16e3a0db"
}


class ValidationError(RuntimeError):
    """Raised when the V2.0.4 maintenance package is inconsistent."""


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
        ".yaml", ".cff", ".ipynb",
    }:
        text = data.decode("utf-8-sig")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return text.encode("utf-8")
    return data


def invariant_categories(root: Path) -> dict[str, list[Path]]:
    excluded_configs = {
        "config/v2_stage5_release_candidate.json",
        "config/v2_0_1_maintenance.json",
        "config/v2_0_2_maintenance.json",
        "config/v2_0_3_maintenance.json",
        "config/v2_0_4_maintenance.json",
    }
    legacy: list[Path] = []
    for path in sorted((root / "config").glob("v2_*.json")):
        if path.relative_to(root).as_posix() not in excluded_configs:
            legacy.append(path)
    for path in sorted((root / "results/tables/v2").glob("*.csv")):
        if path.name != "21_stage5_source_manifest.csv":
            legacy.append(path)
    legacy.extend(sorted((root / "results/figures/v2").glob("*.png")))
    notebooks = sorted((root / "notebooks").glob("*.ipynb"))
    analysis_scripts = sorted(
        path for path in (root / "scripts/analysis").glob("*")
        if path.is_file() and path.suffix.lower() in {".py", ".r"}
    )
    v2_execution_scripts = sorted(
        path for path in (root / "scripts/v2").glob("*")
        if path.is_file()
        and path.suffix.lower() in {".py", ".r"}
        and "validate" not in path.name.lower()
    )
    return {
        "governed_configs_tables_figures": legacy,
        "public_notebooks": notebooks,
        "analysis_scripts": analysis_scripts,
        "v2_scientific_execution_scripts": v2_execution_scripts,
    }


def digest_paths(root: Path, paths: Iterable[Path]) -> tuple[int, str]:
    ordered = sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())
    digest = hashlib.sha256()
    for path in ordered:
        relative = path.relative_to(root).as_posix()
        sha256 = hashlib.sha256(canonical_bytes(path)).hexdigest()
        digest.update(relative.encode("utf-8") + b"\0" + sha256.encode("ascii") + b"\0")
    return len(ordered), digest.hexdigest()


def require_phrases(path: Path, phrases: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            raise ValidationError(f"Required wording missing in {path.as_posix()}: {phrase}")


def run_script(root: Path, relative_script: str) -> None:
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


def copy_source_without_git(root: Path, destination: Path) -> None:
    if (root / ".git").exists():
        completed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
            capture_output=True,
        )
        if completed.returncode != 0:
            raise ValidationError("Unable to enumerate repository files.")
        names = [
            item.decode("utf-8", errors="strict")
            for item in completed.stdout.split(b"\0") if item
        ]
        for relative in names:
            source = root / relative
            if source.is_file():
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        return
    shutil.copytree(
        root,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".mypy_cache"),
    )


def validate_v2_0_3_baseline_portably(root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="agelens_v2_0_4_baseline_") as temporary:
        source_copy = Path(temporary) / "AgeLens-v2.0.4-source"
        copy_source_without_git(root, source_copy)
        run_script(source_copy, "scripts/v2/27_validate_v2_0_3_maintenance.py")


def parse_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise ValidationError(f"Unpinned CI requirement: {line}")
        name, version = line.split("==", 1)
        pins[name.strip().lower()] = version.strip()
    return pins


def runtime_versions(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["component"]: row["version"] for row in csv.DictReader(handle)}


def validate(root: Path) -> None:
    root = root.resolve()
    required = (
        ".github/workflows/repository-safety-check.yml",
        "CITATION.cff",
        "PUBLIC_CLEANUP_REPORT.md",
        "README.md",
        "requirements-ci.txt",
        "config/v2_0_4_maintenance.json",
        "docs/v2/README.md",
        "docs/v2/V2_0_4_Maintenance_Release.md",
        "docs/v2/V2_Decision_Log.md",
        "docs/v2/V2_Evidence_Gap_Register.md",
        "docs/v2/V2_Research_Protocol.md",
        "release/v2_0_4_scientific_invariants.json",
        "scripts/prepare_repository.py",
        "scripts/v2/25_validate_v2_0_1_maintenance.py",
        "scripts/v2/26_validate_v2_0_2_maintenance.py",
        "scripts/v2/27_validate_v2_0_3_maintenance.py",
        "scripts/v2/28_validate_v2_0_4_maintenance.py",
        "results/tables/v2/18_stage4_runtime_versions.csv",
    )
    missing = [relative for relative in required if not (root / relative).is_file()]
    if missing:
        raise ValidationError("Missing V2.0.4 artifacts: " + ", ".join(missing))

    validate_v2_0_3_baseline_portably(root)

    config = read_json(root / "config/v2_0_4_maintenance.json")
    expected = {
        "release": RELEASE,
        "release_tag": RELEASE,
        "date": DATE,
        "status": "public_ci_runtime_maintenance_authorized",
        "base_release": BASE_RELEASE,
        "base_release_commit": BASE_RELEASE_COMMIT,
        "portable_validator": "scripts/v2/28_validate_v2_0_4_maintenance.py",
        "legacy_scientific_invariant_tree_sha256": LEGACY_TREE_SHA256,
        "legacy_scientific_invariant_file_count": LEGACY_FILE_COUNT,
        "expanded_scientific_invariant_tree_sha256": EXPANDED_TREE_SHA256,
        "expanded_scientific_invariant_file_count": EXPANDED_FILE_COUNT,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValidationError(f"Unexpected V2.0.4 maintenance value: {key}")

    scope = config.get("scope", {})
    for key in (
        "github_actions_python_313_enabled",
        "ci_validator_dependencies_declared",
        "ci_dependency_install_step_added",
        "ci_runtime_verification_step_added",
        "current_release_metadata_updated",
        "ci_and_snapshot_current_validator_updated",
        "historical_v2_0_1_validator_compatibility_updated",
        "historical_v2_0_2_validator_compatibility_updated",
        "historical_v2_0_3_validator_compatibility_updated",
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
        "analysis_or_execution_scripts_changed",
    ):
        if scope.get(key) is not False:
            raise ValidationError("Scientific no-change flag invalid: " + key)

    categories = invariant_categories(root)
    combined: list[Path] = []
    for name, paths in categories.items():
        count, digest = digest_paths(root, paths)
        if count != CATEGORY_COUNTS[name] or digest != CATEGORY_DIGESTS[name]:
            raise ValidationError(f"Invariant category changed: {name}={count}/{digest}")
        combined.extend(paths)
    legacy_count, legacy_digest = digest_paths(root, categories["governed_configs_tables_figures"])
    expanded_count, expanded_digest = digest_paths(root, combined)
    if legacy_count != LEGACY_FILE_COUNT or legacy_digest != LEGACY_TREE_SHA256:
        raise ValidationError("The prior 79-file invariant changed.")
    if expanded_count != EXPANDED_FILE_COUNT or expanded_digest != EXPANDED_TREE_SHA256:
        raise ValidationError("The expanded 108-file invariant changed.")

    invariant = read_json(root / "release/v2_0_4_scientific_invariants.json")
    for key, value in {
        "release": RELEASE,
        "base_release": BASE_RELEASE,
        "hash_rule": "sha256-canonical-lf-v2",
        "legacy_file_count": LEGACY_FILE_COUNT,
        "legacy_tree_sha256": LEGACY_TREE_SHA256,
        "expanded_file_count": EXPANDED_FILE_COUNT,
        "expanded_tree_sha256": EXPANDED_TREE_SHA256,
        "category_counts": CATEGORY_COUNTS,
        "category_sha256": CATEGORY_DIGESTS,
    }.items():
        if invariant.get(key) != value:
            raise ValidationError("Invariant record mismatch: " + key)

    versions = runtime_versions(root / "results/tables/v2/18_stage4_runtime_versions.csv")
    pins = parse_pins(root / "requirements-ci.txt")
    expected_pins = {"numpy": versions["numpy"], "pandas": versions["pandas"]}
    if pins != expected_pins:
        raise ValidationError(f"CI requirement pins do not match governed runtime: {pins}")
    if not versions["python"].startswith("3.13."):
        raise ValidationError("Governed Python runtime is not on the 3.13 minor line.")

    workflow = (root / ".github/workflows/repository-safety-check.yml").read_text(encoding="utf-8")
    for phrase in (
        'python-version: "3.13"',
        'cache-dependency-path: requirements-ci.txt',
        'python -m pip install --disable-pip-version-check -r requirements-ci.txt',
        'assert platform.python_version_tuple()[:2] == ("3", "13")',
        'assert pd.__version__ == "3.0.5"',
        'scripts/v2/28_validate_v2_0_4_maintenance.py',
        'Check V2.0.4 maintenance release',
        'Check public snapshot builder',
    ):
        if phrase not in workflow:
            raise ValidationError("CI runtime correction missing: " + phrase)
    if 'python-version: "3.12"' in workflow:
        raise ValidationError("Stale Python 3.12 CI selection remains.")

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    if "version: 2.0.4" not in citation or "date-released: 2026-07-27" not in citation:
        raise ValidationError("CITATION.cff is not synchronized to V2.0.4.")

    require_phrases(root / "README.md", (
        "AgeLens V2.0.4",
        "docs/v2/V2_0_4_Maintenance_Release.md",
        "AgeLens V2.0.3",
        "requirements-ci.txt",
        "Version 2.0.4. 2026.",
    ))
    require_phrases(root / "scripts/prepare_repository.py", (
        '"requirements-ci.txt"',
        "28_validate_v2_0_4_maintenance.py",
        "V2.0.4 maintenance validation",
    ))
    require_phrases(root / "docs/v2/README.md", (
        "Current public maintenance release: `v2.0.4`",
        "Prior public maintenance release: `v2.0.3`",
        "V2_0_4_Maintenance_Release.md",
        "config/v2_0_4_maintenance.json",
        "scripts/v2/28_validate_v2_0_4_maintenance.py",
        "requirements-ci.txt",
    ))
    require_phrases(root / "docs/v2/V2_Research_Protocol.md", (
        "| Version | 1.6 |",
        "Final public maintenance release `v2.0.4`",
        "D2-031",
    ))
    require_phrases(root / "docs/v2/V2_Decision_Log.md", (
        "| Version | 1.9 |",
        "D2-031",
        "Authorize the V2.0.4 CI runtime maintenance release",
    ))
    require_phrases(root / "docs/v2/V2_Evidence_Gap_Register.md", (
        "| Version | 1.9 |",
        "V2-EG-024",
        "V2.0.4 CI Runtime Integrity Disposition",
    ))
    require_phrases(root / "PUBLIC_CLEANUP_REPORT.md", (
        "V2.0.4",
        "Python 3.13",
        "minimal pinned validator dependencies",
    ))
    require_phrases(root / "scripts/v2/25_validate_v2_0_1_maintenance.py", (
        "config/v2_0_4_maintenance.json",
        "(?:1|2|3|4)",
    ))
    require_phrases(root / "scripts/v2/26_validate_v2_0_2_maintenance.py", (
        "config/v2_0_4_maintenance.json",
        "version: 2.0.4",
    ))
    require_phrases(root / "scripts/v2/27_validate_v2_0_3_maintenance.py", (
        "config/v2_0_4_maintenance.json",
        "version: 2.0.4",
        "V2_0_3_Maintenance_Release.md",
    ))

    print("V2.0.4 MAINTENANCE VALIDATION PASSED")
    print("GitHub Actions selects Python 3.13 and installs pinned validator dependencies.")
    print("The workflow verifies pandas 3.0.5 before running the release-validator chain.")
    print("Historical V2.0.1 through V2.0.3 validation remains portable without a Git checkout.")
    print("The 79-file and expanded 108-file scientific invariants are unchanged.")
    print("Hosted GitHub Actions must pass before the v2.0.4 tag and release are created.")


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
