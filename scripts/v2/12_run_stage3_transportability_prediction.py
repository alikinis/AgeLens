"""Run AgeLens V2 Stage 3 transportability and cross-cycle validation."""

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
        "Private Stage 2 model input was not found. Searched:\n" + searched
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

    raise FileNotFoundError("Rscript was not found. Install R or pass --rscript.")


def run_stage3(project_root: Path, private_input: Path, rscript: Path) -> None:
    r_file = project_root / "scripts/v2/13_stage3_transportability_prediction.R"
    validator = project_root / "scripts/v2/14_validate_stage3_results.py"
    tables = project_root / "results/tables/v2"
    figures = project_root / "results/figures/v2"
    logs = project_root / "results/logs/v2"

    for directory in (tables, figures, logs):
        directory.mkdir(parents=True, exist_ok=True)

    command = [
        str(rscript),
        str(r_file),
        str(private_input),
        str(tables),
        str(figures),
    ]
    print("Running Stage 3 R analysis. The 500-replicate bootstrap prints progress.")
    completed = subprocess.run(
        command,
        cwd=project_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError("Stage 3 R analysis failed.")

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
            "Stage 3 validation failed.\n" + checked.stdout + checked.stderr
        )
    print("\n" + checked.stdout.strip())

    global_tests = pd.read_csv(
        tables / "13_stage3_transportability_global_tests.csv"
    )
    decision = pd.read_csv(
        tables / "13_stage3_incremental_utility_decision.csv"
    )
    metrics = pd.read_csv(
        tables / "13_stage3_prediction_bootstrap_summary.csv"
    )

    print("\nSTAGE 3 PROVISIONAL RESULTS")
    print("\nTransportability global tests:")
    print(global_tests.to_string(index=False))
    print("\nIncremental-utility decision:")
    print(decision.to_string(index=False))
    key = metrics.loc[
        metrics["metric"].isin(["brier_delta_c_minus_b", "auc_delta_c_minus_b"])
    ]
    print("\nPooled out-of-cycle performance deltas:")
    print(key.to_string(index=False))
    print("\nResults remain provisional pending Stage 3 human review and release gate.")


def run_self_test() -> None:
    candidate = Path("x") / "data" / "processed" / "v2" / PRIVATE_FILENAME
    assert candidate.name == PRIVATE_FILENAME
    assert "processed" in candidate.parts
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
    run_stage3(root, private_input, rscript)


if __name__ == "__main__":
    main()
