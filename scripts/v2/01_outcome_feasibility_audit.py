from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_CANONICAL_COUNTS = {
    "2015_2016": 2645,
    "2017_2018": 2578,
}
EXPECTED_CANONICAL_TOTAL = sum(EXPECTED_CANONICAL_COUNTS.values())
REQUIRED_CANONICAL_COLUMNS = {
    "SEQN",
    "NHANES_CYCLE",
    "chronological_age_years",
    "WTSAF4YR",
    "SDMVSTRA",
    "SDMVPSU",
}


# pandas/read_sas can decode an IBM XPORT numeric zero as this exact
# positive sentinel. Normalize exact matches only; never use a near-zero
# threshold because legitimate small biological values must be preserved.
IBM_XPORT_ZERO_SENTINEL = 5.397605346934028e-79


@dataclass(frozen=True)
class Paths:
    project_root: Path
    private_root: Path
    config: Path
    canonical: Path
    raw_v2: Path
    output_tables: Path
    output_logs: Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit overlap and descriptive feasibility of governed "
            "AgeLens V2 outcome candidates."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="AgeLens repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--private-root",
        type=Path,
        default=None,
        help=(
            "Private AgeLens workspace containing data/. When omitted, "
            "the script searches the repository and its parent folders."
        ),
    )
    parser.add_argument(
        "--canonical-path",
        type=Path,
        default=None,
        help=(
            "Explicit path to the governed V1 canonical Parquet file. "
            "Overrides automatic discovery."
        ),
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Do not download missing official NHANES XPT files.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic synthetic-data tests and exit.",
    )
    return parser.parse_args()


CANONICAL_FILENAME = "agelens_v1_canonical_complete_case.parquet"


def canonical_under(root: Path) -> Path:
    return root / "data" / "processed" / CANONICAL_FILENAME


def discover_private_root(
    project_root: Path,
    requested_private_root: Path | None,
    requested_canonical: Path | None,
) -> tuple[Path, Path, list[Path]]:
    searched: list[Path] = []

    if requested_canonical is not None:
        canonical = requested_canonical.expanduser().resolve()
        if not canonical.is_file():
            raise FileNotFoundError(
                f"Explicit canonical file was not found: {canonical}"
            )
        if requested_private_root is not None:
            private_root = requested_private_root.expanduser().resolve()
        else:
            private_root = canonical.parent.parent.parent
        return private_root, canonical, searched

    if requested_private_root is not None:
        private_root = requested_private_root.expanduser().resolve()
        canonical = canonical_under(private_root)
        searched.append(canonical)
        if not canonical.is_file():
            raise FileNotFoundError(
                "The private workspace does not contain the governed V1 "
                f"canonical file: {canonical}"
            )
        return private_root, canonical, searched

    candidate_roots = [project_root, *project_root.parents]
    for candidate_root in candidate_roots:
        canonical = canonical_under(candidate_root)
        searched.append(canonical)
        if canonical.is_file():
            return candidate_root, canonical, searched

    searched_text = "\n".join(f"  - {path}" for path in searched)
    raise FileNotFoundError(
        "The governed V1 canonical participant file was not found. "
        "The public Git repository intentionally excludes participant-level "
        "data. Keep the file in the private AgeLens workspace and pass "
        "--private-root or --canonical-path. Searched locations:\n"
        f"{searched_text}"
    )


def resolve_paths(
    project_root: Path,
    private_root: Path | None = None,
    canonical_path: Path | None = None,
) -> Paths:
    project_root = project_root.resolve()
    resolved_private_root, canonical, _ = discover_private_root(
        project_root,
        private_root,
        canonical_path,
    )
    return Paths(
        project_root=project_root,
        private_root=resolved_private_root,
        config=project_root / "config" / "v2_outcome_candidates.json",
        canonical=canonical,
        raw_v2=(
            resolved_private_root / "data" / "raw" / "v2_outcomes"
        ),
        output_tables=project_root / "results" / "tables" / "v2",
        output_logs=project_root / "logs" / "v2",
    )


def private_relative(path: Path, private_root: Path) -> str:
    try:
        return path.resolve().relative_to(private_root.resolve()).as_posix()
    except ValueError:
        return path.name


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "AgeLens-V2/0.1 "
                "(public NHANES reproducibility audit)"
            )
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            with tempfile.NamedTemporaryFile(
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as temp_handle:
                temp_path = Path(temp_handle.name)
                shutil.copyfileobj(response, temp_handle)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Could not download official NHANES file: {url}"
        ) from exc

    try:
        if temp_path.stat().st_size == 0:
            raise RuntimeError(f"Downloaded file is empty: {url}")
        temp_path.replace(destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def ensure_source_files(
    config: dict[str, Any],
    paths: Paths,
    offline: bool,
) -> dict[tuple[str, str], Path]:
    resolved: dict[tuple[str, str], Path] = {}
    for cycle, cycle_spec in config["cycles"].items():
        suffix = cycle_spec["suffix"]
        for component, url in cycle_spec["files"].items():
            destination = (
                paths.raw_v2
                / cycle
                / f"{component}_{suffix}.xpt"
            )
            if not destination.is_file():
                if offline:
                    raise FileNotFoundError(
                        f"Missing local source in offline mode: {destination}"
                    )
                print(f"Downloading {component} {cycle} from official NCHS...")
                download_file(url, destination)
            resolved[(cycle, component)] = destination
    return resolved


def normalize_exact_xport_zero(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    normalized = frame.copy()
    replacement_count = 0
    numeric_columns = normalized.select_dtypes(include=[np.number]).columns

    for column in numeric_columns:
        exact_zero = normalized[column].eq(IBM_XPORT_ZERO_SENTINEL)
        count = int(exact_zero.sum())
        if count:
            normalized.loc[exact_zero, column] = 0.0
            replacement_count += count

    return normalized, replacement_count


def read_xpt(path: Path) -> pd.DataFrame:
    frame = pd.read_sas(path, format="xport", encoding="latin1")
    frame, replacement_count = normalize_exact_xport_zero(frame)
    frame.attrs["xport_zero_replacements"] = replacement_count

    if "SEQN" not in frame.columns:
        raise ValueError(f"SEQN is missing from {path}")
    frame["SEQN"] = pd.to_numeric(frame["SEQN"], errors="raise").astype(
        "int64"
    )
    if frame["SEQN"].duplicated().any():
        raise ValueError(f"Duplicate SEQN values in {path}")
    return frame


def derive_binary(
    series: pd.Series,
    positive_codes: list[int],
    negative_codes: list[int],
) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    result = pd.Series(pd.NA, index=series.index, dtype="Int64")
    result.loc[numeric.isin(negative_codes)] = 0
    result.loc[numeric.isin(positive_codes)] = 1
    return result


def derive_candidate_frame(
    source_frames: dict[str, pd.DataFrame],
    config: dict[str, Any],
    cycle: str,
) -> pd.DataFrame:
    derived = pd.DataFrame(
        {"SEQN": source_frames["DLQ"]["SEQN"].astype("int64")}
    )

    for name, spec in config["candidates"].items():
        source = source_frames[spec["source"]]
        variables = spec["variables"]
        missing = sorted(set(variables) - set(source.columns))
        if missing:
            raise ValueError(
                f"{cycle} {spec['source']} is missing variables for "
                f"{name}: {missing}"
            )

        candidate_type = spec["type"]
        if candidate_type == "binary":
            candidate = derive_binary(
                source[variables[0]],
                spec["positive_codes"],
                spec["negative_codes"],
            )
        elif candidate_type == "binary_any_complete":
            component_values = pd.DataFrame(
                {
                    variable: derive_binary(
                        source[variable],
                        spec["positive_codes"],
                        spec["negative_codes"],
                    )
                    for variable in variables
                }
            )
            complete = component_values.notna().all(axis=1)
            candidate = pd.Series(
                pd.NA,
                index=source.index,
                dtype="Int64",
            )
            candidate.loc[complete] = (
                component_values.loc[complete]
                .max(axis=1)
                .astype("int64")
            )
        elif candidate_type == "sum_threshold_complete":
            items = source.loc[:, variables].apply(
                pd.to_numeric,
                errors="coerce",
            )
            valid_codes = set(spec["valid_item_codes"])
            complete = items.apply(
                lambda column: column.isin(valid_codes)
            ).all(axis=1)
            total = items.sum(axis=1)
            candidate = pd.Series(
                pd.NA,
                index=source.index,
                dtype="Int64",
            )
            candidate.loc[complete] = (
                total.loc[complete].ge(spec["threshold"]).astype("int64")
            )
        else:
            raise ValueError(
                f"Unsupported candidate type for {name}: {candidate_type}"
            )

        candidate_by_seqn = pd.DataFrame(
            {
                "SEQN": source["SEQN"].astype("int64"),
                name: candidate,
            }
        )
        derived = derived.merge(
            candidate_by_seqn,
            on="SEQN",
            how="outer",
            validate="one_to_one",
        )

    derived["NHANES_CYCLE"] = cycle
    return derived


def weighted_binary_prevalence(
    outcome: pd.Series,
    weights: pd.Series,
) -> float:
    valid = outcome.notna() & weights.notna() & weights.gt(0)
    if not valid.any():
        return math.nan
    values = outcome.loc[valid].astype(float).to_numpy()
    valid_weights = weights.loc[valid].astype(float).to_numpy()
    return float(np.average(values, weights=valid_weights))


def summarize_candidate(
    frame: pd.DataFrame,
    candidate: str,
    cycle_label: str,
) -> dict[str, Any]:
    outcome = frame[candidate]
    valid = outcome.notna()
    positive = outcome.eq(1)
    weights = frame["WTSAF4YR"]
    valid_weights = weights.loc[valid]

    return {
        "candidate": candidate,
        "cycle": cycle_label,
        "adult_canonical_n": int(len(frame)),
        "valid_n": int(valid.sum()),
        "missing_n": int((~valid).sum()),
        "valid_fraction": float(valid.mean()) if len(frame) else math.nan,
        "positive_n": int(positive.sum()),
        "weighted_prevalence": weighted_binary_prevalence(
            outcome,
            weights,
        ),
        "weighted_denominator": float(valid_weights.sum()),
        "strata_with_valid_data": int(
            frame.loc[valid, ["NHANES_CYCLE", "SDMVSTRA"]]
            .drop_duplicates()
            .shape[0]
        ),
        "psus_with_valid_data": int(
            frame.loc[
                valid,
                ["NHANES_CYCLE", "SDMVSTRA", "SDMVPSU"],
            ]
            .drop_duplicates()
            .shape[0]
        ),
    }


def load_canonical(paths: Paths) -> pd.DataFrame:
    if not paths.canonical.is_file():
        raise FileNotFoundError(
            "Canonical V1 participant file was not found. Re-run the "
            "governed V1 pipeline locally before this Stage 0 audit: "
            f"{paths.canonical}"
        )
    canonical = pd.read_parquet(paths.canonical)
    missing = sorted(REQUIRED_CANONICAL_COLUMNS - set(canonical.columns))
    if missing:
        raise ValueError(f"Canonical file is missing columns: {missing}")
    if canonical.duplicated(["NHANES_CYCLE", "SEQN"]).any():
        raise ValueError("Canonical file contains duplicate cycle + SEQN rows.")
    if len(canonical) != EXPECTED_CANONICAL_TOTAL:
        raise ValueError(
            f"Canonical row count changed: {len(canonical)}; "
            f"expected {EXPECTED_CANONICAL_TOTAL}."
        )
    observed = canonical.groupby("NHANES_CYCLE").size().to_dict()
    if observed != EXPECTED_CANONICAL_COUNTS:
        raise ValueError(
            f"Canonical cycle counts changed: {observed}; "
            f"expected {EXPECTED_CANONICAL_COUNTS}."
        )
    canonical["SEQN"] = pd.to_numeric(
        canonical["SEQN"], errors="raise"
    ).astype("int64")
    return canonical


def run_audit(args: argparse.Namespace) -> None:
    paths = resolve_paths(
        args.project_root,
        private_root=args.private_root,
        canonical_path=args.canonical_path,
    )
    config = load_json(paths.config)
    canonical = load_canonical(paths)
    source_paths = ensure_source_files(config, paths, args.offline)

    cycle_outcomes: list[pd.DataFrame] = []
    source_manifest_rows: list[dict[str, Any]] = []

    for cycle in config["cycles"]:
        source_frames: dict[str, pd.DataFrame] = {}
        for component in config["cycles"][cycle]["files"]:
            source_path = source_paths[(cycle, component)]
            source_frames[component] = read_xpt(source_path)
            source_manifest_rows.append(
                {
                    "cycle": cycle,
                    "component": component,
                    "path": private_relative(
                        source_path, paths.private_root
                    ),
                    "size_bytes": source_path.stat().st_size,
                    "sha256": sha256_file(source_path),
                    "rows": len(source_frames[component]),
                    "xport_zero_replacements": int(
                        source_frames[component].attrs.get(
                            "xport_zero_replacements", 0
                        )
                    ),
                }
            )
        cycle_outcomes.append(
            derive_candidate_frame(source_frames, config, cycle)
        )

    outcomes = pd.concat(cycle_outcomes, ignore_index=True)
    if outcomes.duplicated(["NHANES_CYCLE", "SEQN"]).any():
        raise RuntimeError("Derived outcomes contain duplicate cycle + SEQN rows.")

    merged = canonical.merge(
        outcomes,
        on=["NHANES_CYCLE", "SEQN"],
        how="left",
        validate="one_to_one",
    )
    adult_minimum_age = int(config["adult_minimum_age_years"])
    adult = merged.loc[
        merged["chronological_age_years"].ge(adult_minimum_age)
        & merged["WTSAF4YR"].notna()
        & merged["WTSAF4YR"].gt(0)
    ].copy()

    summary_rows: list[dict[str, Any]] = []
    for candidate in config["candidates"]:
        for cycle in config["cycles"]:
            cycle_frame = adult.loc[adult["NHANES_CYCLE"].eq(cycle)]
            summary_rows.append(
                summarize_candidate(cycle_frame, candidate, cycle)
            )
        summary_rows.append(
            summarize_candidate(adult, candidate, "pooled")
        )

    summary = pd.DataFrame(summary_rows)
    summary["weighted_prevalence_percent"] = (
        summary["weighted_prevalence"] * 100
    )

    checks = pd.DataFrame(
        [
            {
                "check": "Canonical V1 total remains 5,223",
                "pass": len(canonical) == EXPECTED_CANONICAL_TOTAL,
                "observed": len(canonical),
            },
            {
                "check": "Canonical V1 cycle counts remain governed",
                "pass": canonical.groupby("NHANES_CYCLE").size().to_dict()
                == EXPECTED_CANONICAL_COUNTS,
                "observed": str(
                    canonical.groupby("NHANES_CYCLE").size().to_dict()
                ),
            },
            {
                "check": "Derived outcomes are unique by cycle and SEQN",
                "pass": not outcomes.duplicated(
                    ["NHANES_CYCLE", "SEQN"]
                ).any(),
                "observed": len(outcomes),
            },
            {
                "check": "Only aggregate tables are exported",
                "pass": True,
                "observed": (
                    "No SEQN or participant-level row is written to results."
                ),
            },
            {
                "check": "Governed fasting weight is used",
                "pass": config["governed_weight"] == "WTSAF4YR",
                "observed": config["governed_weight"],
            },
            {
                "check": "Exact XPORT zero sentinel normalization audited",
                "pass": sum(
                    int(row["xport_zero_replacements"])
                    for row in source_manifest_rows
                ) > 0,
                "observed": sum(
                    int(row["xport_zero_replacements"])
                    for row in source_manifest_rows
                ),
            },
        ]
    )
    if not checks["pass"].all():
        raise RuntimeError("One or more Stage 0 feasibility checks failed.")

    paths.output_tables.mkdir(parents=True, exist_ok=True)
    paths.output_logs.mkdir(parents=True, exist_ok=True)

    summary_path = paths.output_tables / "01_outcome_feasibility_summary.csv"
    checks_path = paths.output_tables / "01_outcome_feasibility_checks.csv"
    manifest_path = paths.output_tables / "01_outcome_source_manifest.csv"
    metadata_path = paths.output_logs / "01_outcome_feasibility_metadata.json"

    summary.to_csv(summary_path, index=False)
    checks.to_csv(checks_path, index=False)
    pd.DataFrame(source_manifest_rows).to_csv(manifest_path, index=False)

    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": str(Path(__file__).resolve().relative_to(paths.project_root)),
        "config": str(paths.config.relative_to(paths.project_root)),
        "canonical_input": private_relative(
            paths.canonical, paths.private_root
        ),
        "private_workspace_absolute_path_recorded": False,
        "canonical_input_sha256": sha256_file(paths.canonical),
        "adult_minimum_age_years": adult_minimum_age,
        "adult_canonical_n": int(len(adult)),
        "weight": config["governed_weight"],
        "outputs": [
            str(summary_path.relative_to(paths.project_root)),
            str(checks_path.relative_to(paths.project_root)),
            str(manifest_path.relative_to(paths.project_root)),
        ],
        "participant_level_output_written": False,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\nAgeLens V2 Stage 0 outcome feasibility audit completed.\n")
    print(f"Private workspace: {paths.private_root}")
    print(f"Canonical input: {paths.canonical}")
    print(f"Raw V2 cache: {paths.raw_v2}")
    display_columns = [
        "candidate",
        "cycle",
        "adult_canonical_n",
        "valid_n",
        "positive_n",
        "valid_fraction",
        "weighted_prevalence_percent",
        "strata_with_valid_data",
        "psus_with_valid_data",
    ]
    print(summary.loc[:, display_columns].to_string(index=False))
    print("\nAggregate outputs:")
    for output in metadata["outputs"]:
        print(f"- {output}")
    print("\nNo participant-level output was written.")


def run_self_test() -> None:
    sentinel_frame = pd.DataFrame(
        {
            "zero_item": [
                IBM_XPORT_ZERO_SENTINEL,
                0.0,
                1.0,
            ],
            "other_item": [2.0, 3.0, 4.0],
        }
    )
    normalized_frame, replacement_count = normalize_exact_xport_zero(
        sentinel_frame
    )
    assert replacement_count == 1
    assert normalized_frame["zero_item"].tolist() == [0.0, 0.0, 1.0]

    source_frames = {
        "DLQ": pd.DataFrame(
            {
                "SEQN": [1, 2, 3, 4],
                "DLQ010": [2, 1, 2, 2],
                "DLQ020": [2, 2, 2, 2],
                "DLQ040": [2, 2, 1, 2],
                "DLQ050": [2, 1, 2, 9],
                "DLQ060": [2, 2, 2, 2],
                "DLQ080": [2, 2, 2, 2],
            }
        ),
        "HSQ": pd.DataFrame(
            {"SEQN": [1, 2, 3, 4], "HSD010": [1, 4, 5, 9]}
        ),
        "DPQ": pd.DataFrame(
            {
                "SEQN": [1, 2, 3, 4],
                **{
                    f"DPQ0{i}0": [0, 1, 2, 9]
                    for i in range(1, 10)
                },
            }
        ),
        "PFQ": pd.DataFrame({"SEQN": [1, 2, 3, 4]}),
    }
    config = {
        "candidates": {
            "mobility_disability": {
                "source": "DLQ",
                "variables": ["DLQ050"],
                "type": "binary",
                "positive_codes": [1],
                "negative_codes": [2],
            },
            "any_disability_six": {
                "source": "DLQ",
                "variables": [
                    "DLQ010",
                    "DLQ020",
                    "DLQ040",
                    "DLQ050",
                    "DLQ060",
                    "DLQ080",
                ],
                "type": "binary_any_complete",
                "positive_codes": [1],
                "negative_codes": [2],
            },
            "fair_poor_general_health": {
                "source": "HSQ",
                "variables": ["HSD010"],
                "type": "binary",
                "positive_codes": [4, 5],
                "negative_codes": [1, 2, 3],
            },
            "phq9_ge10": {
                "source": "DPQ",
                "variables": [
                    "DPQ010",
                    "DPQ020",
                    "DPQ030",
                    "DPQ040",
                    "DPQ050",
                    "DPQ060",
                    "DPQ070",
                    "DPQ080",
                    "DPQ090",
                ],
                "type": "sum_threshold_complete",
                "valid_item_codes": [0, 1, 2, 3],
                "threshold": 10,
            },
        }
    }
    derived = derive_candidate_frame(source_frames, config, "test_cycle")
    assert derived["mobility_disability"].tolist() == [0, 1, 0, pd.NA]
    assert derived["any_disability_six"].tolist() == [0, 1, 1, pd.NA]
    assert derived["fair_poor_general_health"].tolist() == [0, 1, 1, pd.NA]
    assert derived["phq9_ge10"].tolist() == [0, 0, 1, pd.NA]

    prevalence = weighted_binary_prevalence(
        pd.Series([0, 1, pd.NA], dtype="Int64"),
        pd.Series([1.0, 3.0, 10.0]),
    )
    assert np.isclose(prevalence, 0.75)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        repo_root = temp_root / "private" / "github" / "AgeLens"
        private_root = temp_root / "private"
        canonical = canonical_under(private_root)
        repo_root.mkdir(parents=True)
        canonical.parent.mkdir(parents=True)
        canonical.touch()
        detected_root, detected_canonical, _ = discover_private_root(
            repo_root, None, None
        )
        assert detected_root == private_root.resolve()
        assert detected_canonical == canonical.resolve()

    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    run_audit(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
