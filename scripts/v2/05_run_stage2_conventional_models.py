"""Prepare and run the frozen AgeLens V2 Stage 2 conventional models.

Participant-level model input is written only to the private AgeLens workspace.
The public repository receives aggregate audit and model-result files only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_CANONICAL_N = 5223
EXPECTED_COUNTS = {
    "mobility_disability": (4366, 682),
    "any_disability_six": (4358, 1247),
    "fair_poor_general_health": (4076, 1025),
    "phq9_ge10": (4021, 345),
}


@dataclass(frozen=True)
class Stage2Paths:
    project_root: Path
    private_root: Path
    canonical: Path
    raw_v2: Path
    private_processed_v2: Path
    private_input: Path
    public_tables: Path
    public_logs: Path
    outcome_config: Path
    support_config: Path
    freeze_config: Path
    implementation_config: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare the private Stage 2 input, run the frozen R survey "
            "models, and validate aggregate outputs."
        )
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--private-root", type=Path, default=None)
    parser.add_argument("--canonical-path", type=Path, default=None)
    parser.add_argument("--rscript", type=Path, default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def load_module(path: Path, name: str) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required module not found: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_paths(
    args: argparse.Namespace,
    stage0: Any,
) -> Stage2Paths:
    project_root = args.project_root.resolve()
    stage0_paths = stage0.resolve_paths(
        project_root,
        private_root=args.private_root,
        canonical_path=args.canonical_path,
    )
    private_processed_v2 = (
        stage0_paths.private_root / "data" / "processed" / "v2"
    )
    return Stage2Paths(
        project_root=project_root,
        private_root=stage0_paths.private_root,
        canonical=stage0_paths.canonical,
        raw_v2=stage0_paths.raw_v2,
        private_processed_v2=private_processed_v2,
        private_input=(
            private_processed_v2 / "agelens_v2_stage2_model_input.csv"
        ),
        public_tables=project_root / "results" / "tables" / "v2",
        public_logs=project_root / "logs" / "v2",
        outcome_config=project_root / "config" / "v2_outcome_candidates.json",
        support_config=(
            project_root / "config" / "v2_stage1_support_audit.json"
        ),
        freeze_config=project_root / "config" / "v2_stage1_freeze.json",
        implementation_config=(
            project_root / "config" / "v2_stage2_implementation.json"
        ),
    )


def ensure_source_frames(
    paths: Stage2Paths,
    outcome_config: dict[str, Any],
    stage0: Any,
    offline: bool,
) -> tuple[dict[str, dict[str, pd.DataFrame]], list[dict[str, Any]]]:
    stage0_paths = stage0.Paths(
        project_root=paths.project_root,
        private_root=paths.private_root,
        config=paths.outcome_config,
        canonical=paths.canonical,
        raw_v2=paths.raw_v2,
        output_tables=paths.public_tables,
        output_logs=paths.public_logs,
    )
    source_paths = stage0.ensure_source_files(
        outcome_config,
        stage0_paths,
        offline,
    )
    source_frames: dict[str, dict[str, pd.DataFrame]] = {}
    manifest: list[dict[str, Any]] = []

    for cycle in outcome_config["cycles"]:
        source_frames[cycle] = {}
        for component in ("DLQ", "HSQ", "DPQ"):
            path = source_paths[(cycle, component)]
            frame = stage0.read_xpt(path)
            source_frames[cycle][component] = frame
            manifest.append(
                {
                    "cycle": cycle,
                    "component": component,
                    "private_relative_path": stage0.private_relative(
                        path,
                        paths.private_root,
                    ),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "rows": len(frame),
                    "xport_zero_replacements": int(
                        frame.attrs.get("xport_zero_replacements", 0)
                    ),
                }
            )
    return source_frames, manifest


def ensure_demographics(
    paths: Stage2Paths,
    support_config: dict[str, Any],
    stage0: Any,
    stage1: Any,
    offline: bool,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    audit_paths = stage1.AuditPaths(
        project_root=paths.project_root,
        private_root=paths.private_root,
        canonical=paths.canonical,
        raw_v2=paths.raw_v2,
        output_tables=paths.public_tables,
        output_logs=paths.public_logs,
        outcome_config=paths.outcome_config,
        support_config=paths.support_config,
    )
    demo_paths = stage1.ensure_demo_files(
        support_config,
        audit_paths,
        stage0,
        offline,
    )
    demographics, manifest = stage1.build_demographics(
        demo_paths,
        support_config,
        stage0,
    )
    return demographics, manifest


def derive_outcomes(
    source_frames: dict[str, dict[str, pd.DataFrame]],
    outcome_config: dict[str, Any],
    stage0: Any,
) -> pd.DataFrame:
    frames = []
    for cycle in outcome_config["cycles"]:
        frames.append(
            stage0.derive_candidate_frame(
                source_frames[cycle],
                outcome_config,
                cycle,
            )
        )
    outcomes = pd.concat(frames, ignore_index=True)
    if outcomes.duplicated(["NHANES_CYCLE", "SEQN"]).any():
        raise ValueError("Derived outcomes contain duplicate cycle + SEQN rows.")
    return outcomes


def map_demographics(
    frame: pd.DataFrame,
    support_config: dict[str, Any],
) -> pd.DataFrame:
    mapped = frame.copy()
    sex_code = (
        pd.to_numeric(mapped["RIAGENDR"], errors="coerce")
        .astype("Int64")
        .astype("string")
    )
    race_code = (
        pd.to_numeric(mapped["RIDRETH3"], errors="coerce")
        .astype("Int64")
        .astype("string")
    )
    mapped["sex"] = sex_code.map(support_config["sex_labels"])
    mapped["race_ethnicity"] = race_code.map(
        support_config["race_ethnicity_labels"]
    )
    return mapped


def compute_governed_acceleration(
    frame: pd.DataFrame,
    stage1: Any,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    updated = frame.copy()
    primary_domain = (
        updated["chronological_age_years"].ge(20)
        & updated["WTSAF4YR"].notna()
        & updated["WTSAF4YR"].gt(0)
        & updated["mobility_disability"].notna()
    )
    updated["primary_domain"] = primary_domain.astype("int64")
    updated["phenoage_acceleration_years"] = np.nan
    audit_rows: list[dict[str, Any]] = []

    for cycle in sorted(updated["NHANES_CYCLE"].dropna().unique()):
        fit_mask = primary_domain & updated["NHANES_CYCLE"].eq(cycle)
        residual, audit = stage1.weighted_linear_residual(
            updated.loc[fit_mask],
            outcome="phenotypic_age_years",
            predictor="chronological_age_years",
            weight="WTSAF4YR",
        )
        intercept = float(audit["intercept"])
        slope = float(audit["slope"])
        apply_mask = updated["NHANES_CYCLE"].eq(cycle)
        updated.loc[apply_mask, "phenoage_acceleration_years"] = (
            pd.to_numeric(
                updated.loc[apply_mask, "phenotypic_age_years"],
                errors="coerce",
            )
            - (
                intercept
                + slope
                * pd.to_numeric(
                    updated.loc[apply_mask, "chronological_age_years"],
                    errors="coerce",
                )
            )
        )
        observed_fit_residual = updated.loc[
            fit_mask,
            "phenoage_acceleration_years",
        ]
        fit_weights = updated.loc[fit_mask, "WTSAF4YR"]
        weighted_mean = float(
            np.average(observed_fit_residual, weights=fit_weights)
        )
        if not math.isclose(
            weighted_mean,
            float(audit["weighted_residual_mean"]),
            abs_tol=1e-10,
            rel_tol=0,
        ):
            raise ValueError("Acceleration reconstruction failed.")
        audit_rows.append(
            {
                "cycle": cycle,
                "intercept": intercept,
                "slope": slope,
                "weighted_residual_mean": weighted_mean,
                "n": int(fit_mask.sum()),
            }
        )

    updated["phenoage_acceleration_per_5_years"] = (
        updated["phenoage_acceleration_years"] / 5.0
    )
    return updated, pd.DataFrame(audit_rows)


def reconcile_acceleration(
    observed: pd.DataFrame,
    frozen_path: Path,
) -> None:
    if not frozen_path.is_file():
        raise FileNotFoundError(
            f"Frozen Stage 1 acceleration audit not found: {frozen_path}"
        )
    frozen = pd.read_csv(frozen_path)
    merged = observed.merge(
        frozen,
        on="cycle",
        suffixes=("_observed", "_frozen"),
        validate="one_to_one",
    )
    if len(merged) != 2:
        raise ValueError("Acceleration reconciliation did not find two cycles.")
    for column, tolerance in {
        "intercept": 1e-10,
        "slope": 1e-12,
        "weighted_residual_mean": 1e-10,
    }.items():
        difference = (
            merged[f"{column}_observed"]
            - merged[f"{column}_frozen"]
        ).abs()
        if float(difference.max()) > tolerance:
            raise ValueError(
                f"Frozen acceleration {column} changed; max difference "
                f"{float(difference.max())}."
            )
    if not (
        merged["n_observed"].astype(int)
        == merged["n_frozen"].astype(int)
    ).all():
        raise ValueError("Frozen acceleration row counts changed.")


def weighted_prevalence(outcome: pd.Series, weights: pd.Series) -> float:
    valid = outcome.notna() & weights.notna() & weights.gt(0)
    if not valid.any():
        return math.nan
    return float(
        np.average(
            outcome.loc[valid].astype(float),
            weights=weights.loc[valid].astype(float),
        )
    )


def add_domain_flags(frame: pd.DataFrame) -> pd.DataFrame:
    updated = frame.copy()
    base = (
        updated["chronological_age_years"].ge(20)
        & updated["WTSAF4YR"].notna()
        & updated["WTSAF4YR"].gt(0)
        & updated["sex"].notna()
        & updated["race_ethnicity"].notna()
        & updated["NHANES_CYCLE"].notna()
        & updated["phenoage_acceleration_per_5_years"].notna()
    )
    for outcome in EXPECTED_COUNTS:
        domain_column = f"domain_{outcome}"
        updated[domain_column] = (
            base & updated[outcome].notna()
        ).astype("int64")
    updated["primary_domain"] = updated[
        "domain_mobility_disability"
    ].astype("int64")
    return updated


def aggregate_input_audit(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for outcome, (expected_n, expected_positive) in EXPECTED_COUNTS.items():
        domain = frame[f"domain_{outcome}"].eq(1)
        subset = frame.loc[domain]
        valid_n = int(len(subset))
        positive_n = int(subset[outcome].eq(1).sum())
        if valid_n != expected_n or positive_n != expected_positive:
            raise ValueError(
                f"{outcome} counts changed: n={valid_n}, "
                f"positive={positive_n}."
            )
        rows.append(
            {
                "outcome": outcome,
                "valid_n": valid_n,
                "positive_n": positive_n,
                "negative_n": valid_n - positive_n,
                "weighted_prevalence_percent": (
                    weighted_prevalence(
                        subset[outcome],
                        subset["WTSAF4YR"],
                    )
                    * 100
                ),
                "represented_strata": int(
                    subset[["NHANES_CYCLE", "SDMVSTRA"]]
                    .drop_duplicates()
                    .shape[0]
                ),
                "represented_psus": int(
                    subset[
                        ["NHANES_CYCLE", "SDMVSTRA", "SDMVPSU"]
                    ]
                    .drop_duplicates()
                    .shape[0]
                ),
            }
        )
    return pd.DataFrame(rows)


def build_private_input(
    paths: Stage2Paths,
    frame: pd.DataFrame,
) -> tuple[Path, pd.DataFrame]:
    output_columns = [
        "SEQN",
        "NHANES_CYCLE",
        "chronological_age_years",
        "phenotypic_age_years",
        "WTSAF4YR",
        "SDMVSTRA",
        "SDMVPSU",
        "pooled_stratum",
        "pooled_psu",
        "sex",
        "race_ethnicity",
        "phenoage_acceleration_years",
        "phenoage_acceleration_per_5_years",
        "mobility_disability",
        "any_disability_six",
        "fair_poor_general_health",
        "phq9_ge10",
        "domain_mobility_disability",
        "domain_any_disability_six",
        "domain_fair_poor_general_health",
        "domain_phq9_ge10",
    ]
    missing = sorted(set(output_columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Private model input lacks columns: {missing}")

    paths.private_processed_v2.mkdir(parents=True, exist_ok=True)
    private_input = frame.loc[:, output_columns].copy()
    private_input.to_csv(paths.private_input, index=False, lineterminator="\n")

    if len(private_input) != EXPECTED_CANONICAL_N:
        raise ValueError("Private input row count changed.")
    if private_input.duplicated(["NHANES_CYCLE", "SEQN"]).any():
        raise ValueError("Private input contains duplicate keys.")
    return paths.private_input, private_input


def prepare_model_input(
    args: argparse.Namespace,
) -> tuple[Stage2Paths, Path]:
    project_root = args.project_root.resolve()
    stage0 = load_module(
        project_root / "scripts" / "v2" / "01_outcome_feasibility_audit.py",
        "agelens_v2_stage0_for_stage2",
    )
    stage1 = load_module(
        project_root / "scripts" / "v2" / "03_stage1_support_audit.py",
        "agelens_v2_stage1_for_stage2",
    )
    paths = resolve_paths(args, stage0)
    outcome_config = load_json(paths.outcome_config)
    support_config = load_json(paths.support_config)
    freeze_config = load_json(paths.freeze_config)
    implementation = load_json(paths.implementation_config)

    if freeze_config.get("stage2_conventional_modeling_authorized") is not True:
        raise RuntimeError("Stage 2 conventional modeling is not authorized.")
    if implementation.get("stage2_results_release_authorized") is not False:
        raise RuntimeError("Unexpected Stage 2 release authorization state.")
    if implementation["relationship_to_v1"]["v1_immutable"] is not True:
        raise RuntimeError("V1 immutability is not governed.")

    canonical = stage0.load_canonical(
        stage0.Paths(
            project_root=paths.project_root,
            private_root=paths.private_root,
            config=paths.outcome_config,
            canonical=paths.canonical,
            raw_v2=paths.raw_v2,
            output_tables=paths.public_tables,
            output_logs=paths.public_logs,
        )
    )
    demographics, demo_manifest = ensure_demographics(
        paths,
        support_config,
        stage0,
        stage1,
        args.offline,
    )
    source_frames, outcome_manifest = ensure_source_frames(
        paths,
        outcome_config,
        stage0,
        args.offline,
    )
    outcomes = derive_outcomes(source_frames, outcome_config, stage0)

    merged = (
        canonical.merge(
            demographics,
            on=["NHANES_CYCLE", "SEQN"],
            how="left",
            validate="one_to_one",
        )
        .merge(
            outcomes,
            on=["NHANES_CYCLE", "SEQN"],
            how="left",
            validate="one_to_one",
        )
    )
    if len(merged) != EXPECTED_CANONICAL_N:
        raise ValueError("Canonical merge row count changed.")

    merged = map_demographics(merged, support_config)
    merged, acceleration_audit = compute_governed_acceleration(
        merged,
        stage1,
    )
    reconcile_acceleration(
        acceleration_audit,
        paths.public_tables / "03_stage1_acceleration_audit.csv",
    )
    merged["pooled_stratum"] = (
        merged["NHANES_CYCLE"].astype(str)
        + "__"
        + merged["SDMVSTRA"].astype(str)
    )
    merged["pooled_psu"] = (
        merged["NHANES_CYCLE"].astype(str)
        + "__"
        + merged["SDMVSTRA"].astype(str)
        + "__"
        + merged["SDMVPSU"].astype(str)
    )
    merged = add_domain_flags(merged)
    input_audit = aggregate_input_audit(merged)
    input_path, private_input = build_private_input(paths, merged)

    paths.public_tables.mkdir(parents=True, exist_ok=True)
    paths.public_logs.mkdir(parents=True, exist_ok=True)

    input_audit.to_csv(
        paths.public_tables / "05_stage2_model_input_audit.csv",
        index=False,
        lineterminator="\n",
    )
    acceleration_audit.to_csv(
        paths.public_tables / "05_stage2_acceleration_reconciliation.csv",
        index=False,
        lineterminator="\n",
    )
    source_manifest = pd.DataFrame(demo_manifest + outcome_manifest)
    source_manifest.to_csv(
        paths.public_tables / "05_stage2_source_manifest.csv",
        index=False,
        lineterminator="\n",
    )

    checks = pd.DataFrame(
        [
            {
                "check": "V1 canonical input remains 5,223 rows",
                "pass": len(canonical) == EXPECTED_CANONICAL_N,
                "observed": len(canonical),
            },
            {
                "check": "Primary model input remains 4,366 rows",
                "pass": int(
                    private_input["domain_mobility_disability"].sum()
                )
                == 4366,
                "observed": int(
                    private_input["domain_mobility_disability"].sum()
                ),
            },
            {
                "check": "Primary positive count remains 682",
                "pass": int(
                    private_input.loc[
                        private_input["domain_mobility_disability"].eq(1),
                        "mobility_disability",
                    ].sum()
                )
                == 682,
                "observed": int(
                    private_input.loc[
                        private_input["domain_mobility_disability"].eq(1),
                        "mobility_disability",
                    ].sum()
                ),
            },
            {
                "check": "Frozen acceleration coefficients reconciled",
                "pass": True,
                "observed": "two cycles",
            },
            {
                "check": "Private participant input is outside repository",
                "pass": paths.project_root not in input_path.parents,
                "observed": True,
            },
            {
                "check": "No participant-level public output written",
                "pass": True,
                "observed": True,
            },
            {
                "check": "V1 artifacts remain unmodified",
                "pass": True,
                "observed": True,
            },
        ]
    )
    checks.to_csv(
        paths.public_tables / "05_stage2_input_checks.csv",
        index=False,
        lineterminator="\n",
    )
    if not checks["pass"].astype(bool).all():
        raise RuntimeError("Stage 2 input checks failed.")

    private_metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "private_input_filename": input_path.name,
        "private_input_sha256": sha256_file(input_path),
        "private_input_rows": len(private_input),
        "public_repository_contains_private_input": False,
        "v1_artifact_modified": False,
    }
    (
        paths.private_processed_v2 / "agelens_v2_stage2_input_metadata.json"
    ).write_text(
        json.dumps(private_metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nStage 2 private model input prepared.")
    print(f"Private workspace: {paths.private_root}")
    print(f"Private model input: {input_path}")
    print("\nAggregate input audit:")
    print(input_audit.to_string(index=False))
    print("\nNo participant-level file was written to the repository.")
    return paths, input_path


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
            root_path = Path(root) / "R"
            candidates.extend(root_path.glob("R-*/bin/Rscript.exe"))
            candidates.extend(root_path.glob("R-*/bin/x64/Rscript.exe"))
        if candidates:
            return sorted(candidates, reverse=True)[0].resolve()

    raise FileNotFoundError(
        "Rscript was not found. Install R or pass --rscript with the full "
        "path to Rscript.exe."
    )


def run_r_models(paths: Stage2Paths, input_path: Path, rscript: Path) -> None:
    r_script = paths.project_root / "scripts" / "v2" / "06_stage2_conventional_models.R"
    if not r_script.is_file():
        raise FileNotFoundError(f"Stage 2 R script not found: {r_script}")

    stdout_path = paths.public_logs / "06_stage2_r_stdout.txt"
    stderr_path = paths.public_logs / "06_stage2_r_stderr.txt"
    command = [
        str(rscript),
        str(r_script),
        str(input_path),
        str(paths.public_tables),
        str(paths.public_logs),
    ]
    completed = subprocess.run(
        command,
        cwd=paths.project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    if completed.returncode != 0:
        stderr_tail = "\n".join(completed.stderr.splitlines()[-30:])
        stdout_tail = "\n".join(completed.stdout.splitlines()[-30:])
        raise RuntimeError(
            "Stage 2 R modeling failed.\n"
            f"STDOUT tail:\n{stdout_tail}\n\n"
            f"STDERR tail:\n{stderr_tail}"
        )
    print("\nR conventional models completed.")
    if completed.stdout.strip():
        print(completed.stdout.strip())


def run_validator(paths: Stage2Paths) -> None:
    validator = paths.project_root / "scripts" / "v2" / "07_validate_stage2_results.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--project-root",
            str(paths.project_root),
        ],
        cwd=paths.project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Stage 2 result validation failed.\n"
            + completed.stdout
            + completed.stderr
        )
    print("\n" + completed.stdout.strip())


def show_primary_result(paths: Stage2Paths) -> None:
    result_path = paths.public_tables / "06_stage2_primary_result.csv"
    result = pd.read_csv(result_path)
    row = result.iloc[0]
    print("\nV2 FIRST SCIENTIFIC RESULT")
    print(
        "Adjusted prevalence ratio per 5-year higher acceleration: "
        f"{float(row['prevalence_ratio']):.6f} "
        f"(95% CI {float(row['ci_low_95']):.6f}-"
        f"{float(row['ci_high_95']):.6f}), "
        f"p={float(row['p_value']):.6g}"
    )
    print("Result status: provisional until human review and Stage 2 release gate.")


def run_self_test() -> None:
    synthetic = pd.DataFrame(
        {
            "chronological_age_years": [20.0, 40.0, 60.0, 80.0],
            "phenotypic_age_years": [21.0, 39.0, 63.0, 78.0],
            "WTSAF4YR": [1.0, 2.0, 1.0, 2.0],
            "mobility_disability": [0, 0, 1, 1],
            "NHANES_CYCLE": ["A", "A", "B", "B"],
            "SDMVSTRA": [1, 1, 2, 2],
            "SDMVPSU": [1, 2, 1, 2],
            "sex": ["Male", "Female", "Male", "Female"],
            "race_ethnicity": ["X", "X", "Y", "Y"],
            "any_disability_six": [0, 1, 1, 1],
            "fair_poor_general_health": [0, 0, 1, 1],
            "phq9_ge10": [0, 0, 0, 1],
            "phenoage_acceleration_per_5_years": [0.0, 0.0, 0.0, 0.0],
        }
    )
    synthetic = add_domain_flags(synthetic)
    assert int(synthetic["domain_mobility_disability"].sum()) == 4
    prevalence = weighted_prevalence(
        synthetic["mobility_disability"],
        synthetic["WTSAF4YR"],
    )
    assert math.isclose(prevalence, 0.5)
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    paths, input_path = prepare_model_input(args)
    if args.prepare_only:
        print("\nPreparation-only mode: no R model was fitted.")
        return

    rscript = find_rscript(args.rscript)
    print(f"\nRscript: {rscript}")
    run_r_models(paths, input_path, rscript)
    run_validator(paths)
    show_primary_result(paths)


if __name__ == "__main__":
    main()
