from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)
    return digest.hexdigest()


def copy_tree(source: Path, destination: Path) -> None:
    destination.mkdir(
        parents=True,
        exist_ok=True,
    )
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        target = destination / relative
        if item.is_dir():
            target.mkdir(
                parents=True,
                exist_ok=True,
            )
        else:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copy2(item, target)


def find_verified_notebook(
    project_root: Path,
    relative_path: str,
    expected_hash: str,
) -> Path:
    normalized = Path(
        relative_path.replace("\\", "/")
    )
    direct = project_root / normalized

    candidates = []

    if direct.exists():
        candidates.append(direct)

    stem = normalized.stem
    search_roots = [
        project_root / "notebooks",
        project_root,
    ]

    for search_root in search_roots:
        if not search_root.exists():
            continue
        candidates.extend(
            sorted(
                search_root.glob(
                    f"{stem}_v*.ipynb"
                )
            )
        )

    seen = set()
    unique_candidates = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_candidates.append(candidate)

    for candidate in unique_candidates:
        if sha256(candidate) == expected_hash:
            return candidate

    observed = [
        {
            "path": str(candidate),
            "sha256": sha256(candidate),
            "size_bytes": candidate.stat().st_size,
        }
        for candidate in unique_candidates
    ]

    raise RuntimeError(
        "No local notebook matched the governed release inventory.\n"
        f"Required: {relative_path}\n"
        f"Expected SHA-256: {expected_hash}\n"
        f"Candidates checked: {json.dumps(observed, indent=2)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        required=True,
    )
    parser.add_argument(
        "--output",
        default=None,
    )
    args = parser.parse_args()

    setup_root = Path(__file__).resolve().parents[1]
    assets = setup_root / "assets"
    project_root = Path(
        args.project_root
    ).expanduser().resolve()

    output_root = (
        Path(args.output).expanduser().resolve()
        if args.output
        else project_root / "github" / "AgeLens"
    )

    if not project_root.exists():
        raise FileNotFoundError(
            f"Project root does not exist: {project_root}"
        )

    release_zip = (
        assets
        / "agelens_v1_release_20260722.zip"
    )

    if output_root.exists():
        raise FileExistsError(
            f"Output already exists: {output_root}\n"
            "Move or delete it before rebuilding."
        )

    output_root.mkdir(
        parents=True,
        exist_ok=False,
    )

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)

            with zipfile.ZipFile(release_zip) as archive:
                bad = archive.testzip()
                if bad:
                    raise RuntimeError(
                        f"Embedded release ZIP is damaged at {bad}"
                    )
                archive.extractall(temp_root)

            extracted_roots = [
                path
                for path in temp_root.iterdir()
                if path.is_dir()
            ]

            if len(extracted_roots) != 1:
                raise RuntimeError(
                    "Unexpected release archive structure."
                )

            release_root = extracted_roots[0]

            # Repository root files.
            for name in [
                "README_TEMPLATE.md",
                "CITATION.cff",
                "LICENSE",
                ".gitignore",
                ".gitattributes",
                "requirements.txt",
                "R_PACKAGES.md",
            ]:
                source = setup_root / name
                target_name = (
                    "README.md"
                    if name == "README_TEMPLATE.md"
                    else name
                )
                shutil.copy2(
                    source,
                    output_root / target_name,
                )

            # Docs and safety tooling.
            copy_tree(
                setup_root / "docs",
                output_root / "docs",
            )
            copy_tree(
                setup_root / "scripts",
                output_root / "scripts",
            )

            # Governed release content.
            shutil.copytree(
                release_root / "config",
                output_root / "config",
            )
            copy_tree(
                release_root / "docs",
                output_root / "docs" / "governed",
            )
            copy_tree(
                release_root / "governance",
                output_root / "docs" / "governance",
            )
            copy_tree(
                release_root / "scripts",
                output_root / "scripts" / "analysis",
            )
            copy_tree(
                release_root / "tables",
                output_root / "results" / "tables",
            )
            copy_tree(
                release_root / "figures",
                output_root / "results" / "figures",
            )

            release_destination = (
                output_root / "release"
            )
            release_destination.mkdir(
                parents=True,
                exist_ok=True,
            )

            for name in [
                "release_manifest.csv",
                "release_package_metadata.json",
            ]:
                shutil.copy2(
                    release_root / name,
                    release_destination / name,
                )

            shutil.copy2(
                release_root
                / "notebook_inventory"
                / "notebook_inventory.csv",
                release_destination
                / "notebook_inventory.csv",
            )

            shutil.copy2(
                release_zip,
                release_destination
                / "agelens_v1_release_20260722.zip",
            )

            # Canonical notebooks verified by final inventory.
            inventory_path = (
                release_root
                / "notebook_inventory"
                / "notebook_inventory.csv"
            )
            notebooks_destination = (
                output_root / "notebooks"
            )
            notebooks_destination.mkdir(
                parents=True,
                exist_ok=True,
            )

            verified_notebooks = []

            with inventory_path.open(
                encoding="utf-8",
                newline="",
            ) as handle:
                rows = list(
                    csv.DictReader(handle)
                )

            for row in rows:
                source = find_verified_notebook(
                    project_root,
                    row["relative_path"],
                    row["sha256"],
                )
                destination = (
                    notebooks_destination
                    / row["notebook"]
                )
                shutil.copy2(
                    source,
                    destination,
                )
                verified_notebooks.append(
                    {
                        "notebook": row["notebook"],
                        "repository_path": f"notebooks/{row['notebook']}",
                        "sha256": sha256(destination),
                        "size_bytes": destination.stat().st_size,
                    }
                )

            # Baseline notebook and aggregate outputs.
            baseline_notebook = (
                project_root
                / "notebooks"
                / "12_baseline_characteristics.ipynb"
            )
            if not baseline_notebook.exists():
                raise FileNotFoundError(
                    baseline_notebook
                )
            shutil.copy2(
                baseline_notebook,
                notebooks_destination
                / baseline_notebook.name,
            )

            baseline_outputs = [
                "12_baseline_characteristics_main_formatted.csv",
                "12_baseline_characteristics_biomarkers_formatted.csv",
                "12_baseline_characteristics_numeric_long.csv",
                "12_baseline_characteristics_checks.csv",
            ]
            local_tables = (
                project_root
                / "results"
                / "tables"
            )

            for name in baseline_outputs:
                source = local_tables / name
                if source.exists():
                    shutil.copy2(
                        source,
                        output_root
                        / "results"
                        / "tables"
                        / name,
                    )
                elif name in {
                    "12_baseline_characteristics_main_formatted.csv",
                    "12_baseline_characteristics_biomarkers_formatted.csv",
                }:
                    raise FileNotFoundError(
                        source
                    )

            # Final manuscript. PDFs go in the normal repo; DOCX sources
            # are retained in a clearly marked source subdirectory.
            manuscript = (
                output_root / "manuscript"
            )
            manuscript_source = (
                manuscript / "source"
            )
            manuscript_source.mkdir(
                parents=True,
                exist_ok=True,
            )

            for name in [
                "AgeLens_V1_Independent_Research_Article_Final.pdf",
                "AgeLens_V1_Independent_Research_Article_Supplement_Final.pdf",
            ]:
                shutil.copy2(
                    assets / name,
                    manuscript / name,
                )

            for name in [
                "AgeLens_V1_Independent_Research_Article_Final.docx",
                "AgeLens_V1_Independent_Research_Article_Supplement_Final.docx",
            ]:
                shutil.copy2(
                    assets / name,
                    manuscript_source / name,
                )

            shutil.copy2(
                assets
                / "AgeLens_V1_Independent_Research_Article_Manifest.json",
                manuscript
                / "AgeLens_V1_Independent_Research_Article_Manifest.json",
            )

            # GitHub workflow.
            workflow_dir = (
                output_root
                / ".github"
                / "workflows"
            )
            workflow_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
            workflow = """name: repository-safety-check

on:
  push:
  pull_request:

jobs:
  preflight:
runs-on: ubuntu-latest
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: "3.12"
  - name: Check for sensitive or forbidden files
    run: python scripts/preflight_repository.py .
"""
            (
                workflow_dir
                / "repository-safety-check.yml"
            ).write_text(
                workflow,
                encoding="utf-8",
            )

            # Build manifest before preflight.
            manifest = {
                "repository": "alikinis/AgeLens",
                "visibility_target": "private",
                "release": "v1.0.0",
                "verified_release_notebooks": verified_notebooks,
                "baseline_notebook_sha256": sha256(
                    notebooks_destination
                    / "12_baseline_characteristics.ipynb"
                ),
                "aggregate_only": True,
                "participant_level_data_included": False,
                "cause_specific_mortality_authorized": False,
            }

            (
                release_destination
                / "repository_build_manifest.json"
            ).write_text(
                json.dumps(
                    manifest,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

        # Run local safety check.
        preflight = (
            output_root
            / "scripts"
            / "preflight_repository.py"
        )
        result = subprocess.run(
            [
                sys.executable,
                str(preflight),
                str(output_root),
            ],
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Repository preflight failed."
            )

        print()
        print("Repository prepared successfully:")
        print(output_root)
        print()
        print("Next:")
        print(
            "Run SETUP_PRIVATE_GITHUB.ps1 "
            "to initialize and push the private repository."
        )
        return 0

    except Exception:
        if output_root.exists():
            shutil.rmtree(
                output_root,
                ignore_errors=True,
            )
        raise


if __name__ == "__main__":
    sys.exit(main())
