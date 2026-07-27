from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

FORBIDDEN_EXTENSIONS = {
    ".parquet", ".xpt", ".dat", ".sas7bdat", ".feather",
    ".rds", ".rdata", ".pkl", ".pickle", ".joblib",
}

FORBIDDEN_DIRECTORIES = {
    "raw", "interim", "processed", "participant_level",
    "participant-level", "manuscript",
}

FORBIDDEN_FILENAMES = {
    "agelens_v1_final_report.md",
    "agelens_v1_release_20260722.zip",
    "release_manifest.csv",
    "release_package_metadata.json",
}

FORBIDDEN_NAME_FRAGMENTS = {
    "agelens_v1_independent_research_article",
}

SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    "GitHub fine-grained token": re.compile(
        r"\bgithub_pat_[A-Za-z0-9_]{30,}\b"
    ),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
}

PERSONAL_PATH_PATTERNS = {
    "Windows user-home path": re.compile(
        r"(?i)\b[A-Z]:\\Users\\[^\\\r\n\"]+\\"
    ),
    "macOS user-home path": re.compile(r"/Users/[^/\s\"']+/"),
    "Linux user-home path": re.compile(r"/home/[^/\s\"']+/"),
}

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".r", ".json", ".csv", ".yml",
    ".yaml", ".cff", ".ps1", ".ipynb",
}

MAX_FILE_BYTES = 50 * 1024 * 1024

NOTEBOOK_PARTICIPANT_IDENTIFIERS = (
    re.compile(r"(?<![A-Za-z0-9_])SEQN(?![A-Za-z0-9_])"),
    re.compile(
        r"(?i)(?<![A-Za-z0-9_])participant_id(?![A-Za-z0-9_])"
    ),
    re.compile(
        r"(?i)(?<![A-Za-z0-9_])local_contribution(?![A-Za-z0-9_])"
    ),
    re.compile(r"(?i)(?<![A-Za-z0-9_])risk_score(?![A-Za-z0-9_])"),
)


PRIVATE_KEY_LITERAL = '"' + "BEGIN " + "PRIVATE KEY" + '"'

INTENTIONAL_SCANNER_LITERALS: dict[str, tuple[str, ...]] = {
    "scripts/v2/21_build_stage5_synthesis.py": (
        PRIVATE_KEY_LITERAL,
    ),
    "scripts/v2/22_validate_stage5_release_candidate.py": (
        PRIVATE_KEY_LITERAL,
        r'r"(?:[A-Za-z]:\\Users\\|/Users/|/home/)"',
    ),
}


def mask_intentional_scanner_literals(
    text: str,
    rel: str,
    errors: list[str],
) -> str:
    """Mask only exact, governed security-scanner definition literals."""
    for literal in INTENTIONAL_SCANNER_LITERALS.get(rel, ()):
        count = text.count(literal)
        if count != 1:
            errors.append(
                "Intentional scanner literal count changed in "
                f"{rel}: expected 1, found {count} for {literal!r}"
            )
            continue
        text = text.replace(literal, "", 1)
    return text

def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def forbidden_filename(name: str) -> bool:
    lowered = name.lower()
    return (
        lowered in FORBIDDEN_FILENAMES
        or any(part in lowered for part in FORBIDDEN_NAME_FRAGMENTS)
    )


def inspect_zip(path: Path, root: Path, errors: list[str]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            damaged = archive.testzip()
            if damaged:
                errors.append(
                    f"Damaged ZIP entry in {relative(path, root)}: "
                    f"{damaged}"
                )
                return

            for info in archive.infolist():
                member = Path(info.filename)
                parts = {part.lower() for part in member.parts[:-1]}

                if member.suffix.lower() in FORBIDDEN_EXTENSIONS:
                    errors.append(
                        f"Forbidden data file inside ZIP "
                        f"{relative(path, root)}: {info.filename}"
                    )

                if parts & FORBIDDEN_DIRECTORIES:
                    errors.append(
                        f"Forbidden directory inside ZIP "
                        f"{relative(path, root)}: {info.filename}"
                    )

                if member.name and forbidden_filename(member.name):
                    errors.append(
                        f"Forbidden public artifact inside ZIP "
                        f"{relative(path, root)}: {info.filename}"
                    )
    except zipfile.BadZipFile:
        errors.append(f"Invalid ZIP file: {relative(path, root)}")


def notebook_output_text(output: object) -> str:
    if not isinstance(output, dict):
        return ""

    parts: list[str] = []
    output_type = output.get("output_type")

    if output_type == "stream":
        value = output.get("text", "")
        parts.append(
            "".join(value) if isinstance(value, list) else str(value)
        )

    data = output.get("data", {})
    if isinstance(data, dict):
        for value in data.values():
            parts.append(
                "".join(value) if isinstance(value, list) else str(value)
            )

    return "\n".join(parts)


def inspect_notebook_outputs(
    path: Path,
    root: Path,
    errors: list[str],
) -> None:
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(
            f"Invalid notebook JSON in {relative(path, root)}: {exc}"
        )
        return

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        for output_index, output in enumerate(cell.get("outputs", [])):
            output_type = (
                output.get("output_type")
                if isinstance(output, dict)
                else None
            )
            if output_type not in {
                "display_data",
                "execute_result",
                "stream",
            }:
                continue

            text = notebook_output_text(output)
            matched = any(
                pattern.search(text)
                for pattern in NOTEBOOK_PARTICIPANT_IDENTIFIERS
            )
            if not matched:
                continue

            if output_type == "stream":
                lines = text.splitlines()
                has_table_like_row = any(
                    re.match(
                        r"^\s*\d+\s+\d{5,}(?:\s+|$)",
                        line,
                    )
                    for line in lines[1:]
                )
                if not has_table_like_row:
                    continue

            errors.append(
                "Possible participant-level rendered notebook output in "
                f"{relative(path, root)} cell {cell_index} "
                f"output {output_index}"
            )


def inspect_workflow(root: Path, errors: list[str]) -> None:
    path = root / ".github/workflows/repository-safety-check.yml"
    if not path.exists():
        errors.append("Missing repository-safety-check workflow.")
        return

    lines = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    required = {
        "jobs:",
        "  preflight:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "        run: python scripts/preflight_repository.py .",
        "        run: python scripts/check_governance_consistency.py .",
    }

    for line in sorted(required):
        if line not in lines:
            errors.append(
                f"Workflow line missing or misindented: {line!r}"
            )

    if any(
        line.startswith("runs-on:") or line.startswith("steps:")
        for line in lines
    ):
        errors.append("Workflow has job fields at the YAML root.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.repository).resolve()
    this_script = Path(__file__).resolve()
    errors: list[str] = []
    inspected_files = 0
    total_bytes = 0

    if not root.exists():
        print(f"Repository does not exist: {root}")
        return 2

    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue

        inspected_files += 1
        total_bytes += path.stat().st_size
        rel = relative(path, root)

        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(f"File exceeds 50 MiB: {rel}")

        if forbidden_filename(path.name):
            errors.append(f"Forbidden public artifact: {rel}")

        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            errors.append(f"Forbidden data extension: {rel}")

        directories = {
            part.lower()
            for part in path.relative_to(root).parts[:-1]
        }
        if directories & FORBIDDEN_DIRECTORIES:
            errors.append(f"Forbidden directory: {rel}")

        lowered_name = path.name.lower()
        if lowered_name == ".env" or lowered_name.startswith(".env."):
            errors.append(f"Environment-secret file: {rel}")

        if path.suffix.lower() == ".zip":
            inspect_zip(path, root, errors)

        if path.suffix.lower() == ".ipynb":
            inspect_notebook_outputs(path, root, errors)

        if (
            path.suffix.lower() in TEXT_EXTENSIONS
            or path.name in {".gitignore", ".gitattributes"}
        ):
            text = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            scan_text = mask_intentional_scanner_literals(
                text,
                rel,
                errors,
            )

            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(scan_text):
                    errors.append(f"Possible {label} in {rel}")

            # The checker source contains the regex definitions themselves.
            if path.resolve() != this_script:
                for label, pattern in PERSONAL_PATH_PATTERNS.items():
                    if pattern.search(scan_text):
                        errors.append(f"Possible {label} in {rel}")

    inspect_workflow(root, errors)

    print(f"Repository: {root}")
    print(f"Files inspected: {inspected_files}")
    print(f"Total size: {total_bytes / 1024 / 1024:.2f} MiB")

    if errors:
        print("\nPREFLIGHT FAILED")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nPREFLIGHT PASSED")
    print(
        "No forbidden raw/participant-level data or rendered notebook "
        "previews, unpublished manuscript artifacts, personal paths, "
        "or common secrets found."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
