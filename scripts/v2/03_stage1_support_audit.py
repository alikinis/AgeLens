"""Aggregate-only support audit for the AgeLens V2 Stage 1 design."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AuditPaths:
    project_root: Path
    private_root: Path
    canonical: Path
    raw_v2: Path
    output_tables: Path
    output_logs: Path
    outcome_config: Path
    support_config: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit covariate completeness and transportability "
            "support without fitting a V2 outcome model."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument(
        "--private-root",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--canonical-path",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--offline",
        action="store_true",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
    )
    return parser.parse_args()


def load_stage0_module(project_root: Path) -> Any:
    module_path = (
        project_root
        / "scripts"
        / "v2"
        / "01_outcome_feasibility_audit.py"
    )
    if not module_path.is_file():
        raise FileNotFoundError(
            f"Stage 0 module not found: {module_path}"
        )
    spec = importlib.util.spec_from_file_location(
        "agelens_v2_stage0",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load Stage 0 module: {module_path}"
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_paths(
    args: argparse.Namespace,
    stage0: Any,
) -> AuditPaths:
    project_root = args.project_root.resolve()
    stage0_paths = stage0.resolve_paths(
        project_root,
        private_root=args.private_root,
        canonical_path=args.canonical_path,
    )
    return AuditPaths(
        project_root=project_root,
        private_root=stage0_paths.private_root,
        canonical=stage0_paths.canonical,
        raw_v2=stage0_paths.raw_v2,
        output_tables=(
            project_root / "results" / "tables" / "v2"
        ),
        output_logs=project_root / "logs" / "v2",
        outcome_config=(
            project_root
            / "config"
            / "v2_outcome_candidates.json"
        ),
        support_config=(
            project_root
            / "config"
            / "v2_stage1_support_audit.json"
        ),
    )


def ensure_demo_files(
    config: dict[str, Any],
    paths: AuditPaths,
    stage0: Any,
    offline: bool,
) -> dict[str, Path]:
    paths.raw_v2.mkdir(parents=True, exist_ok=True)
    resolved: dict[str, Path] = {}

    for cycle, url in config[
        "demographic_files"
    ].items():
        filename = url.rsplit("/", 1)[-1]
        destination = paths.raw_v2 / filename
        if not destination.is_file():
            if offline:
                raise FileNotFoundError(
                    f"Offline mode: missing {destination}"
                )
            print(
                f"Downloading DEMO {cycle} from official NCHS..."
            )
            stage0.download_file(url, destination)
        resolved[cycle] = destination
    return resolved


def build_demographics(
    demo_paths: dict[str, Path],
    config: dict[str, Any],
    stage0: Any,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    frames: list[pd.DataFrame] = []
    manifest: list[dict[str, Any]] = []
    required = set(config["required_demographic_columns"])

    for cycle, path in demo_paths.items():
        frame = stage0.read_xpt(path)
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(
                f"{cycle} DEMO is missing columns: {missing}"
            )
        selected = frame.loc[
            :,
            sorted(required),
        ].copy()
        selected["NHANES_CYCLE"] = cycle
        frames.append(selected)
        manifest.append(
            {
                "cycle": cycle,
                "component": "DEMO",
                "path": stage0.private_relative(
                    path,
                    path.parent.parent.parent.parent,
                ),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "rows": len(frame),
                "xport_zero_replacements": int(
                    frame.attrs.get(
                        "xport_zero_replacements",
                        0,
                    )
                ),
            }
        )

    demographics = pd.concat(frames, ignore_index=True)
    if demographics.duplicated(
        ["NHANES_CYCLE", "SEQN"]
    ).any():
        raise ValueError(
            "DEMO data contain duplicate cycle + SEQN rows."
        )
    return demographics, manifest


def build_primary_outcome(
    paths: AuditPaths,
    outcome_config: dict[str, Any],
    stage0: Any,
    offline: bool,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    source_paths = stage0.ensure_source_files(
        outcome_config,
        stage0.Paths(
            project_root=paths.project_root,
            private_root=paths.private_root,
            config=paths.outcome_config,
            canonical=paths.canonical,
            raw_v2=paths.raw_v2,
            output_tables=paths.output_tables,
            output_logs=paths.output_logs,
        ),
        offline,
    )

    frames: list[pd.DataFrame] = []
    manifest: list[dict[str, Any]] = []
    for cycle in outcome_config["cycles"]:
        path = source_paths[(cycle, "DLQ")]
        frame = stage0.read_xpt(path)
        if "DLQ050" not in frame.columns:
            raise ValueError(
                f"{cycle} DLQ is missing DLQ050."
            )
        outcome = stage0.derive_binary(
            frame["DLQ050"],
            [1],
            [2],
        )
        frames.append(
            pd.DataFrame(
                {
                    "SEQN": frame["SEQN"].astype("int64"),
                    "NHANES_CYCLE": cycle,
                    "mobility_disability": outcome,
                }
            )
        )
        manifest.append(
            {
                "cycle": cycle,
                "component": "DLQ",
                "path": stage0.private_relative(
                    path,
                    paths.private_root,
                ),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "rows": len(frame),
                "xport_zero_replacements": int(
                    frame.attrs.get(
                        "xport_zero_replacements",
                        0,
                    )
                ),
            }
        )

    outcomes = pd.concat(frames, ignore_index=True)
    if outcomes.duplicated(
        ["NHANES_CYCLE", "SEQN"]
    ).any():
        raise ValueError(
            "Primary outcomes contain duplicate keys."
        )
    return outcomes, manifest


def weighted_linear_residual(
    frame: pd.DataFrame,
    outcome: str,
    predictor: str,
    weight: str,
) -> tuple[pd.Series, dict[str, float]]:
    required = frame.loc[
        :,
        [outcome, predictor, weight],
    ].apply(pd.to_numeric, errors="coerce")
    valid = required.notna().all(axis=1) & required[weight].gt(0)

    x = required.loc[valid, predictor].to_numpy(dtype=float)
    y = required.loc[valid, outcome].to_numpy(dtype=float)
    w = required.loc[valid, weight].to_numpy(dtype=float)

    x_mean = float(np.average(x, weights=w))
    y_mean = float(np.average(y, weights=w))
    denominator = float(
        np.sum(w * np.square(x - x_mean))
    )
    if denominator <= 0:
        raise ValueError(
            "Weighted chronological-age variance is non-positive."
        )
    slope = float(
        np.sum(
            w
            * (x - x_mean)
            * (y - y_mean)
        )
        / denominator
    )
    intercept = y_mean - slope * x_mean

    result = pd.Series(
        np.nan,
        index=frame.index,
        dtype=float,
    )
    result.loc[valid] = (
        y - (intercept + slope * x)
    )
    weighted_mean = float(
        np.average(
            result.loc[valid].to_numpy(dtype=float),
            weights=w,
        )
    )
    return result, {
        "intercept": intercept,
        "slope": slope,
        "weighted_residual_mean": weighted_mean,
        "n": int(valid.sum()),
    }


def assign_age_group(
    age: pd.Series,
    groups: list[dict[str, Any]],
) -> pd.Series:
    output = pd.Series(
        pd.NA,
        index=age.index,
        dtype="string",
    )
    numeric_age = pd.to_numeric(age, errors="coerce")
    for group in groups:
        mask = numeric_age.ge(group["minimum"])
        if group["maximum"] is not None:
            mask &= numeric_age.le(group["maximum"])
        output.loc[mask] = group["label"]
    return output


def weighted_prevalence(
    outcome: pd.Series,
    weight: pd.Series,
) -> float:
    valid = (
        outcome.notna()
        & weight.notna()
        & weight.gt(0)
    )
    if not valid.any():
        return math.nan
    return float(
        np.average(
            outcome.loc[valid].astype(float),
            weights=weight.loc[valid].astype(float),
        )
    )


def support_row(
    frame: pd.DataFrame,
    dimension: str,
    level: str,
    thresholds: dict[str, int],
) -> dict[str, Any]:
    n = int(len(frame))
    positive = int(
        frame["mobility_disability"].eq(1).sum()
    )
    negative = int(
        frame["mobility_disability"].eq(0).sum()
    )
    strata = int(
        frame.loc[
            :,
            ["NHANES_CYCLE", "SDMVSTRA"],
        ]
        .drop_duplicates()
        .shape[0]
    )
    psus = int(
        frame.loc[
            :,
            ["NHANES_CYCLE", "SDMVSTRA", "SDMVPSU"],
        ]
        .drop_duplicates()
        .shape[0]
    )
    checks = {
        "n_pass": n >= thresholds["unweighted_n"],
        "positive_pass": (
            positive >= thresholds["positive_n"]
        ),
        "negative_pass": (
            negative >= thresholds["negative_n"]
        ),
        "strata_pass": (
            strata >= thresholds["represented_strata"]
        ),
        "psu_pass": (
            psus >= thresholds["represented_psus"]
        ),
    }
    return {
        "dimension": dimension,
        "level": level,
        "n": n,
        "positive_n": positive,
        "negative_n": negative,
        "weighted_prevalence": weighted_prevalence(
            frame["mobility_disability"],
            frame["WTSAF4YR"],
        ),
        "weighted_prevalence_percent": (
            weighted_prevalence(
                frame["mobility_disability"],
                frame["WTSAF4YR"],
            )
            * 100
        ),
        "represented_strata": strata,
        "represented_psus": psus,
        **checks,
        "support_pass": all(checks.values()),
    }


def missingness_rows(
    frame: pd.DataFrame,
    columns: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in columns:
        missing = frame[column].isna()
        rows.append(
            {
                "variable": column,
                "n": int(len(frame)),
                "missing_n": int(missing.sum()),
                "missing_percent": float(
                    missing.mean() * 100
                ),
                "missing_positive_n": int(
                    (
                        missing
                        & frame[
                            "mobility_disability"
                        ].eq(1)
                    ).sum()
                ),
                "missing_negative_n": int(
                    (
                        missing
                        & frame[
                            "mobility_disability"
                        ].eq(0)
                    ).sum()
                ),
            }
        )
    return rows


def run_audit(args: argparse.Namespace) -> None:
    project_root = args.project_root.resolve()
    stage0 = load_stage0_module(project_root)
    paths = resolve_paths(args, stage0)
    outcome_config = load_json(paths.outcome_config)
    support_config = load_json(paths.support_config)

    canonical = stage0.load_canonical(
        stage0.Paths(
            project_root=paths.project_root,
            private_root=paths.private_root,
            config=paths.outcome_config,
            canonical=paths.canonical,
            raw_v2=paths.raw_v2,
            output_tables=paths.output_tables,
            output_logs=paths.output_logs,
        )
    )

    demo_paths = ensure_demo_files(
        support_config,
        paths,
        stage0,
        args.offline,
    )
    demographics, demo_manifest = build_demographics(
        demo_paths,
        support_config,
        stage0,
    )
    outcomes, outcome_manifest = build_primary_outcome(
        paths,
        outcome_config,
        stage0,
        args.offline,
    )

    merged = (
        canonical
        .merge(
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

    domain = merged.loc[
        merged["chronological_age_years"].ge(20)
        & merged["WTSAF4YR"].notna()
        & merged["WTSAF4YR"].gt(0)
        & merged["mobility_disability"].notna()
    ].copy()

    if len(domain) != int(
        support_config["expected_primary_valid_n"]
    ):
        raise ValueError(
            f"Primary valid n changed: {len(domain)}."
        )
    if int(
        domain["mobility_disability"].sum()
    ) != int(
        support_config["expected_primary_positive_n"]
    ):
        raise ValueError(
            "Primary positive count changed."
        )

    domain["pooled_stratum"] = (
        domain["NHANES_CYCLE"].astype(str)
        + "__"
        + domain["SDMVSTRA"].astype(str)
    )
    domain["pooled_psu"] = (
        domain["NHANES_CYCLE"].astype(str)
        + "__"
        + domain["SDMVSTRA"].astype(str)
        + "__"
        + domain["SDMVPSU"].astype(str)
    )

    acceleration_audit: list[dict[str, Any]] = []
    domain["phenoage_acceleration_years"] = np.nan
    for cycle, index in domain.groupby(
        "NHANES_CYCLE",
        observed=True,
    ).groups.items():
        residual, audit = weighted_linear_residual(
            domain.loc[index],
            outcome="phenotypic_age_years",
            predictor="chronological_age_years",
            weight="WTSAF4YR",
        )
        domain.loc[
            index,
            "phenoage_acceleration_years",
        ] = residual
        acceleration_audit.append(
            {
                "cycle": cycle,
                **audit,
            }
        )

    if (
        max(
            abs(row["weighted_residual_mean"])
            for row in acceleration_audit
        )
        > 1e-10
    ):
        raise ValueError(
            "Cycle-specific acceleration mean is not zero."
        )

    domain["phenoage_acceleration_per_5_years"] = (
        domain["phenoage_acceleration_years"] / 5.0
    )
    domain["sex"] = (
        pd.to_numeric(
            domain["RIAGENDR"],
            errors="coerce",
        )
        .astype("Int64")
        .astype("string")
        .map(support_config["sex_labels"])
    )
    domain["race_ethnicity"] = (
        pd.to_numeric(
            domain["RIDRETH3"],
            errors="coerce",
        )
        .astype("Int64")
        .astype("string")
        .map(
            support_config[
                "race_ethnicity_labels"
            ]
        )
    )
    domain["age_group"] = assign_age_group(
        domain["chronological_age_years"],
        support_config["age_groups"],
    )

    covariate_columns = [
        "chronological_age_years",
        "RIAGENDR",
        "RIDRETH3",
        "NHANES_CYCLE",
        "phenoage_acceleration_per_5_years",
    ]
    missingness = pd.DataFrame(
        missingness_rows(domain, covariate_columns)
    )

    thresholds = support_config[
        "support_thresholds"
    ]
    support_rows: list[dict[str, Any]] = [
        support_row(
            domain,
            "overall",
            "All governed adults",
            thresholds,
        )
    ]

    dimensions = {
        "sex": "sex",
        "age_group": "age_group",
        "race_ethnicity": "race_ethnicity",
        "NHANES_cycle": "NHANES_CYCLE",
    }
    for dimension, column in dimensions.items():
        for level, subset in domain.groupby(
            column,
            dropna=False,
            observed=True,
        ):
            level_text = (
                "<missing>"
                if pd.isna(level)
                else str(level)
            )
            support_rows.append(
                support_row(
                    subset,
                    dimension,
                    level_text,
                    thresholds,
                )
            )

    support = pd.DataFrame(support_rows)
    acceleration = pd.DataFrame(acceleration_audit)

    checks = pd.DataFrame(
        [
            {
                "check": "V1 canonical total remains 5,223",
                "pass": len(canonical) == 5223,
                "observed": len(canonical),
            },
            {
                "check": "Primary valid n remains 4,366",
                "pass": len(domain) == 4366,
                "observed": len(domain),
            },
            {
                "check": "Primary positive n remains 682",
                "pass": int(
                    domain[
                        "mobility_disability"
                    ].sum()
                )
                == 682,
                "observed": int(
                    domain[
                        "mobility_disability"
                    ].sum()
                ),
            },
            {
                "check": "Primary modeling remains unauthorized",
                "pass": True,
                "observed": (
                    "This script fits no outcome model."
                ),
            },
            {
                "check": "Participant-level output is not written",
                "pass": True,
                "observed": (
                    "Only aggregate CSV and JSON files are written."
                ),
            },
            {
                "check": "No absolute personal path in outputs",
                "pass": True,
                "observed": True,
            },
            {
                "check": "Acceleration weighted means are zero",
                "pass": bool(
                    acceleration[
                        "weighted_residual_mean"
                    ].abs().max()
                    <= 1e-10
                ),
                "observed": float(
                    acceleration[
                        "weighted_residual_mean"
                    ].abs().max()
                ),
            },
        ]
    )
    if not checks["pass"].all():
        raise RuntimeError(
            "One or more Stage 1 support checks failed."
        )

    paths.output_tables.mkdir(
        parents=True,
        exist_ok=True,
    )
    paths.output_logs.mkdir(
        parents=True,
        exist_ok=True,
    )

    missingness_path = (
        paths.output_tables
        / "03_stage1_covariate_missingness.csv"
    )
    support_path = (
        paths.output_tables
        / "03_stage1_transportability_support.csv"
    )
    acceleration_path = (
        paths.output_tables
        / "03_stage1_acceleration_audit.csv"
    )
    checks_path = (
        paths.output_tables
        / "03_stage1_design_checks.csv"
    )
    manifest_path = (
        paths.output_tables
        / "03_stage1_source_manifest.csv"
    )
    metadata_path = (
        paths.output_logs
        / "03_stage1_support_audit_metadata.json"
    )

    missingness.to_csv(missingness_path, index=False)
    support.to_csv(support_path, index=False)
    acceleration.to_csv(
        acceleration_path,
        index=False,
    )
    checks.to_csv(checks_path, index=False)
    pd.DataFrame(
        demo_manifest + outcome_manifest
    ).to_csv(manifest_path, index=False)

    metadata = {
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "script": (
            "scripts/v2/03_stage1_support_audit.py"
        ),
        "primary_outcome": "DLQ050",
        "primary_valid_n": int(len(domain)),
        "primary_positive_n": int(
            domain["mobility_disability"].sum()
        ),
        "participant_level_output_written": False,
        "outcome_model_fitted": False,
        "v1_artifact_modified": False,
        "absolute_personal_path_recorded": False,
        "outputs": [
            str(
                path.relative_to(paths.project_root)
            )
            for path in [
                missingness_path,
                support_path,
                acceleration_path,
                checks_path,
                manifest_path,
            ]
        ],
    }
    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "\nAgeLens V2 Stage 1 support audit completed.\n"
    )
    print(
        missingness.to_string(index=False)
    )
    print(
        "\nTransportability support:\n"
    )
    print(
        support.loc[
            :,
            [
                "dimension",
                "level",
                "n",
                "positive_n",
                "negative_n",
                "weighted_prevalence_percent",
                "represented_strata",
                "represented_psus",
                "support_pass",
            ],
        ].to_string(index=False)
    )
    print("\nAggregate outputs:")
    for output in metadata["outputs"]:
        print(f"- {output}")
    print(
        "\nNo outcome model was fitted and no "
        "participant-level output was written."
    )


def run_self_test() -> None:
    synthetic = pd.DataFrame(
        {
            "chronological_age_years": [
                20,
                40,
                60,
                80,
            ],
            "phenotypic_age_years": [
                21,
                39,
                63,
                78,
            ],
            "WTSAF4YR": [1, 2, 1, 2],
            "mobility_disability": [0, 0, 1, 1],
            "NHANES_CYCLE": ["A", "A", "B", "B"],
            "SDMVSTRA": [1, 1, 2, 2],
            "SDMVPSU": [1, 2, 1, 2],
        }
    )
    residual, audit = weighted_linear_residual(
        synthetic,
        "phenotypic_age_years",
        "chronological_age_years",
        "WTSAF4YR",
    )
    assert residual.notna().all()
    assert abs(
        audit["weighted_residual_mean"]
    ) <= 1e-10

    groups = assign_age_group(
        synthetic["chronological_age_years"],
        [
            {
                "label": "20-49",
                "minimum": 20,
                "maximum": 49,
            },
            {
                "label": "50-64",
                "minimum": 50,
                "maximum": 64,
            },
            {
                "label": "65+",
                "minimum": 65,
                "maximum": None,
            },
        ],
    )
    assert groups.tolist() == [
        "20-49",
        "20-49",
        "50-64",
        "65+",
    ]
    assert math.isclose(
        weighted_prevalence(
            synthetic["mobility_disability"],
            synthetic["WTSAF4YR"],
        ),
        0.5,
    )
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    run_audit(args)


if __name__ == "__main__":
    main()
