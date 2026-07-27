"""Validate the AgeLens V1.0.1 public-safety maintenance patch."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

TARGET_NOTEBOOKS = {
    "01_data_ingestion.ipynb": "display(combined_biomarker.head())",
    "04_external_validation.ipynb": "display(r_input.head())",
    "05_validation_completion.ipynb": "display(r_input.head())",
}
PUBLIC_MESSAGE = "Participant-level preview omitted from the public notebook."
IDENTIFIER = re.compile(r"(?<![A-Za-z0-9_])SEQN(?![A-Za-z0-9_])")


class ValidationError(RuntimeError):
    """Raised when the V1.0.1 maintenance package is inconsistent."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_text(output: object) -> str:
    if not isinstance(output, dict):
        return ""

    parts: list[str] = []
    if output.get("output_type") == "stream":
        value = output.get("text", "")
        parts.append("".join(value) if isinstance(value, list) else str(value))

    data = output.get("data", {})
    if isinstance(data, dict):
        for value in data.values():
            parts.append(
                "".join(value) if isinstance(value, list) else str(value)
            )

    return "\n".join(parts)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> None:
    root = root.resolve()

    required = (
        "CITATION.cff",
        "PUBLIC_CLEANUP_REPORT.md",
        "release/public_notebook_inventory.csv",
        "release/public_notebook_sanitization.json",
        "release/repository_build_manifest.json",
        "release/v1_0_1_maintenance.json",
    )
    missing = [path for path in required if not (root / path).is_file()]
    if missing:
        raise ValidationError(
            "Missing maintenance artifacts: " + ", ".join(missing)
        )

    participant_outputs: list[str] = []
    actual_hashes: dict[str, str] = {}

    for path in sorted((root / "notebooks").glob("*.ipynb")):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        actual_hashes[path.name] = sha256(path)

        for cell_index, cell in enumerate(notebook.get("cells", [])):
            for output_index, output in enumerate(cell.get("outputs", [])):
                if output.get("output_type") not in {
                    "display_data",
                    "execute_result",
                }:
                    continue
                if IDENTIFIER.search(output_text(output)):
                    participant_outputs.append(
                        f"{path.name}: cell {cell_index}, output {output_index}"
                    )

        if path.name in TARGET_NOTEBOOKS:
            source = "\n".join(
                "".join(cell.get("source", []))
                for cell in notebook.get("cells", [])
            )
            if TARGET_NOTEBOOKS[path.name] in source:
                raise ValidationError(
                    f"Participant preview source remains in {path.name}."
                )
            if source.count(PUBLIC_MESSAGE) != 1:
                raise ValidationError(
                    "Expected one public-preview omission message in "
                    f"{path.name}."
                )

    if participant_outputs:
        raise ValidationError(
            "Participant-level rendered outputs remain: "
            + "; ".join(participant_outputs)
        )

    inventory = read_csv(root / "release/public_notebook_inventory.csv")
    if {row["notebook"] for row in inventory} != set(actual_hashes):
        raise ValidationError("Public notebook inventory file set changed.")

    for row in inventory:
        name = row["notebook"]
        if row["public_sha256"] != actual_hashes[name]:
            raise ValidationError(f"Public inventory hash mismatch: {name}")
        expected_changed = name in TARGET_NOTEBOOKS
        observed_changed = (
            row["source_cells_changed"].strip().lower() == "true"
        )
        if observed_changed != expected_changed:
            raise ValidationError(f"Source-change flag mismatch: {name}")

    sanitation = read_json(
        root / "release/public_notebook_sanitization.json"
    )
    entries = {row["notebook"]: row for row in sanitation["notebooks"]}
    if set(entries) != set(actual_hashes):
        raise ValidationError("Sanitation record file set changed.")

    for name, digest in actual_hashes.items():
        row = entries[name]
        if row["public_sha256"] != digest:
            raise ValidationError(f"Sanitation hash mismatch: {name}")
        if bool(row["source_cells_changed"]) != (
            name in TARGET_NOTEBOOKS
        ):
            raise ValidationError(
                f"Sanitation source flag mismatch: {name}"
            )

    manifest = read_json(root / "release/repository_build_manifest.json")
    if manifest.get("release") != "v1.0.1":
        raise ValidationError(
            "Repository manifest release is not v1.0.1."
        )
    if manifest.get("maintenance_base_release") != "v1.0.0":
        raise ValidationError(
            "Repository manifest maintenance base changed."
        )
    if manifest.get("participant_level_data_included") is not False:
        raise ValidationError("Participant-level data flag is not false.")
    if manifest.get("aggregate_only") is not True:
        raise ValidationError("Aggregate-only flag is not true.")
    if (
        manifest.get("participant_level_notebook_output_scan_passed")
        is not True
    ):
        raise ValidationError(
            "Notebook-output scan is not recorded as passed."
        )

    manifest_entries = {
        row["notebook"]: row
        for row in manifest["verified_release_notebooks"]
    }
    if set(manifest_entries) != set(actual_hashes):
        raise ValidationError("Repository manifest notebook set changed.")

    for name, digest in actual_hashes.items():
        row = manifest_entries[name]
        path = root / row["repository_path"]
        if row["public_sha256"] != digest:
            raise ValidationError(
                f"Repository manifest hash mismatch: {name}"
            )
        if int(row["size_bytes"]) != path.stat().st_size:
            raise ValidationError(
                f"Repository manifest size mismatch: {name}"
            )

    maintenance = read_json(root / "release/v1_0_1_maintenance.json")
    if maintenance.get("release") != "v1.0.1":
        raise ValidationError("Maintenance release changed.")
    scope = maintenance.get("scope", {})
    if scope.get("participant_level_notebook_previews_removed") is not True:
        raise ValidationError(
            "Notebook-preview correction not recorded."
        )
    if scope.get("display_only_source_statements_changed") != 3:
        raise ValidationError(
            "Display-only source-change count changed."
        )
    for key in (
        "scientific_calculation_cells_changed",
        "scientific_results_changed",
        "aggregate_tables_or_figures_changed",
    ):
        if scope.get(key) is not False:
            raise ValidationError(
                f"Scientific maintenance flag changed: {key}"
            )

    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    for phrase in (
        "version: 1.0.1",
        "date-released: 2026-07-27",
    ):
        if phrase not in citation:
            raise ValidationError(
                f"Citation metadata missing: {phrase}"
            )

    print("V1.0.1 MAINTENANCE VALIDATION PASSED")
    print("Participant-level notebook previews are absent.")
    print("Public notebook inventories and hashes reconcile.")
    print(
        "V1 scientific calculations, results, tables, and figures "
        "are unchanged."
    )


def main() -> None:
    args = parse_args()
    validate(args.project_root)


if __name__ == "__main__":
    sys.exit(main())
