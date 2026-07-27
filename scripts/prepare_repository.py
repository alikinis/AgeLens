from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PUBLIC_ROOT_FILES = {
    ".gitattributes",
    ".gitignore",
    "CITATION.cff",
    "LICENSE",
    "PUBLIC_CLEANUP_REPORT.md",
    "README.md",
    "R_PACKAGES.md",
    "requirements.txt",
    "requirements-v2.txt",
}

PUBLIC_DIRECTORIES = {
    ".github",
    "config",
    "docs",
    "notebooks",
    "release",
    "results",
    "scripts",
}

FORBIDDEN_DIRECTORIES = {
    ".git",
    "__pycache__",
    "raw",
    "interim",
    "processed",
    "participant_level",
    "participant-level",
    "manuscript",
}

FORBIDDEN_FILENAMES = {
    "AgeLens_V1_Final_Report.md",
    "agelens_v1_release_20260722.zip",
    "release_manifest.csv",
    "release_package_metadata.json",
}

FORBIDDEN_NAME_FRAGMENTS = {
    "AgeLens_V1_Independent_Research_Article",
}


def is_forbidden(relative: Path) -> bool:
    if any(part in FORBIDDEN_DIRECTORIES for part in relative.parts):
        return True
    if relative.name in FORBIDDEN_FILENAMES:
        return True
    return any(
        fragment.lower() in relative.name.lower()
        for fragment in FORBIDDEN_NAME_FRAGMENTS
    )


def copy_public_files(source: Path, output: Path) -> None:
    for filename in sorted(PUBLIC_ROOT_FILES):
        path = source / filename
        if path.is_file():
            shutil.copy2(path, output / filename)

    for dirname in sorted(PUBLIC_DIRECTORIES):
        source_dir = source / dirname
        if not source_dir.is_dir():
            continue

        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue

            relative = path.relative_to(source)
            if is_forbidden(relative):
                continue

            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def run_check(script: Path, repository: Path, name: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), str(repository)],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{name} failed.")


def run_validator(script: Path, repository: Path, name: str) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(repository),
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{name} failed.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a public-safe AgeLens repository snapshot."
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.project_root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()

    if not source.is_dir():
        raise FileNotFoundError(f"Source does not exist: {source}")
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    if output == source or source in output.parents:
        raise ValueError("Output cannot be inside the source repository.")

    output.mkdir(parents=True)

    try:
        copy_public_files(source, output)

        preflight = output / "scripts/preflight_repository.py"
        governance = output / "scripts/check_governance_consistency.py"
        maintenance = (
            output
            / "scripts/v2/27_validate_v2_0_3_maintenance.py"
        )

        if (
            not preflight.exists()
            or not governance.exists()
            or not maintenance.exists()
        ):
            raise FileNotFoundError(
                "Required public repository checks were not copied."
            )

        run_check(preflight, output, "Repository preflight")
        run_check(governance, output, "Governance consistency")
        run_validator(
            maintenance,
            output,
            "V2.0.3 maintenance validation",
        )

        print()
        print("Public-safe repository prepared successfully:")
        print(output)
        return 0

    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise


if __name__ == "__main__":
    sys.exit(main())
