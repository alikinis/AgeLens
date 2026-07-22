from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

FORBIDDEN_EXTENSIONS = {
    ".parquet",
    ".xpt",
    ".dat",
    ".sas7bdat",
    ".feather",
    ".rds",
    ".rdata",
    ".pkl",
    ".pickle",
    ".joblib",
}

FORBIDDEN_DIRECTORY_NAMES = {
    "raw",
    "interim",
    "processed",
    "participant_level",
    "participant-level",
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

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".r",
    ".json",
    ".csv",
    ".yml",
    ".yaml",
    ".cff",
    ".ps1",
    ".gitignore",
    ".gitattributes",
}

MAX_FILE_BYTES = 50 * 1024 * 1024


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def inspect_zip(path: Path, root: Path, errors: list[str]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                errors.append(
                    f"Damaged ZIP entry in {relative(path, root)}: {bad}"
                )
                return

            for info in archive.infolist():
                member = Path(info.filename)

                if member.suffix.lower() in FORBIDDEN_EXTENSIONS:
                    errors.append(
                        "Forbidden file inside ZIP "
                        f"{relative(path, root)}: {info.filename}"
                    )

                lowered_parts = {
                    part.lower()
                    for part in member.parts
                }
                blocked_parts = (
                    lowered_parts
                    & FORBIDDEN_DIRECTORY_NAMES
                )
                if blocked_parts:
                    errors.append(
                        "Forbidden directory inside ZIP "
                        f"{relative(path, root)}: {info.filename}"
                    )
    except zipfile.BadZipFile:
        errors.append(
            f"Invalid ZIP file: {relative(path, root)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository",
        nargs="?",
        default=".",
    )
    args = parser.parse_args()

    root = Path(args.repository).resolve()
    errors: list[str] = []
    inspected_files = 0
    total_bytes = 0

    if not root.exists():
        print(f"Repository does not exist: {root}")
        return 2

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        if ".git" in path.parts:
            continue

        inspected_files += 1
        total_bytes += path.stat().st_size
        rel = relative(path, root)

        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(
                f"File exceeds 50 MiB: {rel}"
            )

        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            errors.append(
                f"Forbidden participant/raw-data extension: {rel}"
            )

        lowered_parts = {
            part.lower()
            for part in path.relative_to(root).parts[:-1]
        }
        blocked_parts = (
            lowered_parts
            & FORBIDDEN_DIRECTORY_NAMES
        )
        if blocked_parts:
            errors.append(
                f"Forbidden data directory: {rel}"
            )

        if path.name.lower() == ".env" or path.name.lower().startswith(
            ".env."
        ):
            errors.append(
                f"Environment-secret file: {rel}"
            )

        if path.suffix.lower() == ".zip":
            inspect_zip(path, root, errors)

        suffix = path.suffix.lower()
        is_special_text = path.name in {
            ".gitignore",
            ".gitattributes",
        }
        if suffix in TEXT_EXTENSIONS or is_special_text:
            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError as exc:
                errors.append(
                    f"Could not read text file {rel}: {exc}"
                )
                continue

            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    errors.append(
                        f"Possible {label} in {rel}"
                    )

    print(f"Repository: {root}")
    print(f"Files inspected: {inspected_files}")
    print(f"Total size: {total_bytes / 1024 / 1024:.2f} MiB")

    if errors:
        print("\nPREFLIGHT FAILED")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nPREFLIGHT PASSED")
    print("No forbidden raw/participant-level data or common secrets found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
