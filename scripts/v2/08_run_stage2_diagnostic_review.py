"""Run the governed AgeLens V2 Stage 2 diagnostic review."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pandas as pd


PRIVATE_FILENAME = "agelens_v2_stage2_model_input.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--private-input", type=Path, default=None)
    parser.add_argument("--rscript", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def find_private_input(project_root: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        resolved = explicit.expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Private Stage 2 input not found: {resolved}")
        return resolved

    candidates: list[Path] = []
    for anchor in [project_root, *project_root.parents]:
        candidates.append(
            anchor / "data" / "processed" / "v2" / PRIVATE_FILENAME
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    searched = "\n".join(f"- {path}" for path in candidates)
    raise FileNotFoundError(
        "Private Stage 2 input was not found. Searched:\n" + searched
    )


def find_rscript(explicit: Path | None) -> Path:
    if explicit is not None:
        resolved = explicit.expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Rscript not found: {resolved}")
        return resolved

    on_path = shutil.which("Rscript") or shutil.which("Rscript.exe")
    if on_path:
        return Path(on_path).resolve()

    if os.name == "nt":
        candidates: list[Path] = []
        for environment_name in ("ProgramFiles", "ProgramFiles(x86)"):
            root = os.environ.get(environment_name)
            if not root:
                continue
            r_root = Path(root) / "R"
            candidates.extend(r_root.glob("R-*/bin/Rscript.exe"))
            candidates.extend(r_root.glob("R-*/bin/x64/Rscript.exe"))
        if candidates:
            return sorted(candidates, reverse=True)[0].resolve()

    raise FileNotFoundError(
        "Rscript was not found. Install R or pass --rscript."
    )


def run_review(
    project_root: Path,
    private_input: Path,
    rscript: Path,
) -> None:
    r_file = project_root / "scripts/v2/09_stage2_diagnostic_review.R"
    validator = project_root / "scripts/v2/10_validate_stage2_review.py"
    tables = project_root / "results/tables/v2"
    figures = project_root / "results/figures/v2"
    logs = project_root / "logs/v2"

    for directory in (tables, figures, logs):
        directory.mkdir(parents=True, exist_ok=True)

    command = [
        str(rscript),
        str(r_file),
        str(private_input),
        str(tables),
        str(figures),
        str(logs),
    ]
    completed = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (logs / "09_stage2_review_r_stdout.txt").write_text(
        completed.stdout,
        encoding="utf-8",
    )
    (logs / "09_stage2_review_r_stderr.txt").write_text(
        completed.stderr,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Stage 2 diagnostic review failed.\n"
            + completed.stdout
            + "\n"
            + completed.stderr
        )

    print(completed.stdout.strip())

    checked = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--project-root",
            str(project_root),
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if checked.returncode != 0:
        raise RuntimeError(
            "Stage 2 review validation failed.\n"
            + checked.stdout
            + checked.stderr
        )
    print("\n" + checked.stdout.strip())

    trimmed = pd.read_csv(
        tables / "09_stage2_trimmed_linear_sensitivity.csv"
    )
    curve_review = pd.read_csv(
        tables / "09_stage2_nonlinearity_review.csv"
    )
    print("\nSTAGE 2 DIAGNOSTIC REVIEW")
    print(trimmed.to_string(index=False))
    row = curve_review.iloc[0]
    print(
        "\nBounded logistic-spline nonlinearity p-value: "
        f"{float(row['logistic_spline_nonlinearity_p']):.6g}"
    )
    print(
        "The prespecified linear prevalence ratio remains provisional "
        "and was not replaced."
    )


def run_self_test() -> None:
    fake = Path("x") / "data" / "processed" / "v2" / PRIVATE_FILENAME
    assert fake.name == PRIVATE_FILENAME
    assert "processed" in fake.parts
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    root = args.project_root.resolve()
    private_input = find_private_input(root, args.private_input)
    rscript = find_rscript(args.rscript)
    print(f"Private input: {private_input}")
    print(f"Rscript: {rscript}")
    run_review(root, private_input, rscript)


if __name__ == "__main__":
    main()
