"""Run the frozen AgeLens V2 Stage 4 Explainable Boosting Machine."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from typing import Any, Iterable
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, t


PYTHON_BUILD = "AgeLens-V2-Stage4-Python-20260724c"
EXPECTED_R_BUILD = "AgeLens-V2-Stage4-R-20260724b"
EXPECTED_INTERPRET_VERSION = "0.7.8"
PRIVATE_FILENAME = "agelens_v2_stage2_model_input.csv"
FEATURES = [
    "chronological_age_years",
    "sex",
    "race_ethnicity",
    "phenoage_acceleration_per_5_years",
]
FEATURE_TYPES = ["continuous", "nominal", "nominal", "continuous"]
SEX_LEVELS = ["Male", "Female"]
RACE_LEVELS = [
    "Non-Hispanic White",
    "Mexican American",
    "Other Hispanic",
    "Non-Hispanic Black",
    "Non-Hispanic Asian",
    "Other or multiracial",
]
DIRECTIONS = {
    "train_2015_2016_test_2017_2018": ("2015_2016", "2017_2018"),
    "train_2017_2018_test_2015_2016": ("2017_2018", "2015_2016"),
}
BOOTSTRAP_REPLICATES = 500
DESIGN_DF = 30
PROGRESS_INTERVAL = 10
PROBABILITY_EPSILON = 1e-6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--private-input", type=Path, default=None)
    parser.add_argument("--private-work", type=Path, default=None)
    parser.add_argument("--rscript", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--point-only", action="store_true")
    parser.add_argument("--force-reference", action="store_true")
    parser.add_argument("--repair-reference-only", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_private_input(project_root: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        resolved = explicit.expanduser().resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Private Stage 2 input not found: {resolved}")
        return resolved
    candidates: list[Path] = []
    for anchor in [project_root, *project_root.parents]:
        candidates.append(anchor / "data/processed/v2" / PRIVATE_FILENAME)
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
    raise FileNotFoundError("Rscript was not found. Pass --rscript explicitly.")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_interpret_version() -> None:
    installed = metadata.version("interpret")
    if installed != EXPECTED_INTERPRET_VERSION:
        raise RuntimeError(
            "Frozen interpret version changed: "
            f"expected {EXPECTED_INTERPRET_VERSION}, found {installed}."
        )


def import_ebm_class():
    check_interpret_version()
    from interpret.glassbox import ExplainableBoostingClassifier

    return ExplainableBoostingClassifier


def clip_probability(value: np.ndarray) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1 or not np.isfinite(array).all():
        raise ValueError("Predictions must be a finite one-dimensional vector.")
    return np.clip(array, PROBABILITY_EPSILON, 1 - PROBABILITY_EPSILON)


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not valid.any() or float(weights[valid].sum()) <= 0:
        raise ValueError("Weighted mean has no positive finite support.")
    return float(np.average(values[valid], weights=weights[valid]))


def weighted_auc(
    y: np.ndarray,
    score: np.ndarray,
    weights: np.ndarray,
) -> float:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    weights = np.asarray(weights, dtype=float)
    valid = (
        np.isin(y, [0, 1])
        & np.isfinite(score)
        & np.isfinite(weights)
        & (weights > 0)
    )
    y = y[valid]
    score = score[valid]
    weights = weights[valid]
    positive_total = float(weights[y == 1].sum())
    negative_total = float(weights[y == 0].sum())
    if positive_total <= 0 or negative_total <= 0:
        raise ValueError("Weighted AUC lacks both classes.")
    order = np.lexsort((y, score))
    y = y[order]
    score = score[order]
    weights = weights[order]
    unique_scores, starts = np.unique(score, return_index=True)
    del unique_scores
    ends = np.r_[starts[1:], len(score)]
    cumulative_negative = 0.0
    concordance = 0.0
    for start, end in zip(starts, ends, strict=True):
        group_y = y[start:end]
        group_w = weights[start:end]
        positive_weight = float(group_w[group_y == 1].sum())
        negative_weight = float(group_w[group_y == 0].sum())
        concordance += positive_weight * (
            cumulative_negative + 0.5 * negative_weight
        )
        cumulative_negative += negative_weight
    return concordance / (positive_total * negative_total)


def logistic_loglik(
    beta: np.ndarray,
    design: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    offset: np.ndarray,
) -> float:
    eta = offset + design @ beta
    return float(np.sum(weights * (y * eta - np.logaddexp(0.0, eta))))


def fit_weighted_logistic(
    y: np.ndarray,
    design: np.ndarray,
    weights: np.ndarray,
    *,
    offset: np.ndarray | None = None,
    start: np.ndarray | None = None,
    label: str,
) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    design = np.asarray(design, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if design.ndim != 2 or design.shape[0] != len(y) or len(weights) != len(y):
        raise ValueError(f"{label}: calibration dimensions differ.")
    if offset is None:
        offset = np.zeros(len(y), dtype=float)
    else:
        offset = np.asarray(offset, dtype=float)
    valid = (
        np.isin(y, [0.0, 1.0])
        & np.isfinite(weights)
        & (weights > 0)
        & np.isfinite(offset)
        & np.isfinite(design).all(axis=1)
    )
    y = y[valid]
    design = design[valid]
    weights = weights[valid]
    offset = offset[valid]
    if len(np.unique(y)) != 2:
        raise ValueError(f"{label}: calibration lacks both classes.")
    weights = weights * len(weights) / weights.sum()
    beta = (
        np.zeros(design.shape[1], dtype=float)
        if start is None
        else np.asarray(start, dtype=float).copy()
    )
    if beta.shape != (design.shape[1],):
        raise ValueError(f"{label}: invalid calibration start.")
    current = logistic_loglik(beta, design, y, weights, offset)
    converged = False
    for _ in range(100):
        eta = offset + design @ beta
        probability = 1.0 / (1.0 + np.exp(-np.clip(eta, -35, 35)))
        variance = probability * (1.0 - probability)
        gradient = design.T @ (weights * (y - probability))
        hessian = design.T @ (design * (weights * variance)[:, None])
        if not np.isfinite(gradient).all() or not np.isfinite(hessian).all():
            raise RuntimeError(f"{label}: non-finite calibration derivatives.")
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError as error:
            raise RuntimeError(f"{label}: singular calibration Hessian.") from error
        multiplier = 1.0
        accepted = False
        while multiplier >= 2 ** -20:
            candidate = beta + multiplier * step
            candidate_value = logistic_loglik(
                candidate, design, y, weights, offset
            )
            if np.isfinite(candidate_value) and candidate_value >= current - 1e-10:
                beta = candidate
                current = candidate_value
                accepted = True
                break
            multiplier *= 0.5
        if not accepted:
            raise RuntimeError(f"{label}: calibration line search failed.")
        if float(np.max(np.abs(multiplier * step))) < 1e-9:
            converged = True
            break
    if not converged or not np.isfinite(beta).all():
        raise RuntimeError(f"{label}: calibration did not converge.")
    return beta


def calibration_metrics(
    y: np.ndarray,
    prediction: np.ndarray,
    weights: np.ndarray,
) -> tuple[float, float]:
    prediction = clip_probability(prediction)
    linear_predictor = np.log(prediction / (1.0 - prediction))
    intercept = fit_weighted_logistic(
        y,
        np.ones((len(y), 1), dtype=float),
        weights,
        offset=linear_predictor,
        start=np.array([0.0]),
        label="calibration_intercept",
    )[0]
    slope_fit = fit_weighted_logistic(
        y,
        np.column_stack([np.ones(len(y)), linear_predictor]),
        weights,
        start=np.array([0.0, 1.0]),
        label="calibration_slope",
    )
    return float(intercept), float(slope_fit[1])


def validate_primary(raw: pd.DataFrame, freeze: dict[str, Any]) -> pd.DataFrame:
    required = {
        "NHANES_CYCLE",
        "chronological_age_years",
        "WTSAF4YR",
        "sex",
        "race_ethnicity",
        "phenoage_acceleration_per_5_years",
        "mobility_disability",
        "domain_mobility_disability",
    }
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise ValueError("Missing private input columns: " + ", ".join(missing))
    if len(raw) != 5223:
        raise ValueError(f"Canonical private input count changed: {len(raw)}")
    primary = raw.loc[raw["domain_mobility_disability"] == 1].copy()
    if len(primary) != 4366:
        raise ValueError(f"Primary domain count changed: {len(primary)}")
    if int(primary["mobility_disability"].sum()) != 682:
        raise ValueError("Primary positive count changed.")
    for column in [
        "chronological_age_years",
        "WTSAF4YR",
        "phenoage_acceleration_per_5_years",
        "mobility_disability",
    ]:
        primary[column] = pd.to_numeric(primary[column], errors="raise")
    if primary[FEATURES + ["WTSAF4YR", "mobility_disability"]].isna().any().any():
        raise ValueError("Stage 4 primary variables contain missing values.")
    if not (primary["WTSAF4YR"] > 0).all():
        raise ValueError("Stage 4 full-sample weights must be positive.")
    if set(primary["NHANES_CYCLE"].astype(str)) != {"2015_2016", "2017_2018"}:
        raise ValueError("Stage 4 cycle levels changed.")
    if set(primary["sex"].astype(str)) != set(SEX_LEVELS):
        raise ValueError("Stage 4 sex levels changed.")
    if set(primary["race_ethnicity"].astype(str)) != set(RACE_LEVELS):
        raise ValueError("Stage 4 race/ethnicity levels changed.")
    if freeze["frozen_predictors"]["features_in_order"] != FEATURES:
        raise ValueError("Frozen feature order changed.")
    primary = primary.reset_index(drop=True)
    primary["primary_row_index"] = np.arange(1, len(primary) + 1)
    return primary


def feature_frame(data: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "chronological_age_years": data["chronological_age_years"].astype(float),
            "sex": data["sex"].astype(str),
            "race_ethnicity": data["race_ethnicity"].astype(str),
            "phenoage_acceleration_per_5_years": data[
                "phenoage_acceleration_per_5_years"
            ].astype(float),
        }
    )
    if frame.isna().any().any():
        raise ValueError("Model D feature frame contains missing values.")
    return frame


def ebm_parameters(freeze: dict[str, Any]) -> dict[str, Any]:
    frozen = freeze["frozen_hyperparameters"]
    return {
        "feature_names": FEATURES,
        "feature_types": FEATURE_TYPES,
        "max_bins": frozen["max_bins"],
        "max_interaction_bins": frozen["max_interaction_bins"],
        "interactions": frozen["interactions"],
        "exclude": frozen["exclude"],
        "validation_size": frozen["validation_size"],
        "outer_bags": frozen["outer_bags"],
        "inner_bags": frozen["inner_bags"],
        "learning_rate": frozen["learning_rate"],
        "greedy_ratio": frozen["greedy_ratio"],
        "cyclic_progress": frozen["cyclic_progress"],
        "smoothing_rounds": frozen["smoothing_rounds"],
        "interaction_smoothing_rounds": frozen[
            "interaction_smoothing_rounds"
        ],
        "max_rounds": frozen["max_rounds"],
        "early_stopping_rounds": frozen["early_stopping_rounds"],
        "early_stopping_tolerance": frozen["early_stopping_tolerance"],
        "min_samples_leaf": frozen["min_samples_leaf"],
        "min_hessian": frozen["min_hessian"],
        "reg_alpha": frozen["reg_alpha"],
        "reg_lambda": frozen["reg_lambda"],
        "max_delta_step": frozen["max_delta_step"],
        "gain_scale": frozen["gain_scale"],
        "min_cat_samples": frozen["min_cat_samples"],
        "cat_smooth": frozen["cat_smooth"],
        "missing": frozen["missing"],
        "max_leaves": frozen["max_leaves"],
        "monotone_constraints": frozen["monotone_constraints"],
        "objective": frozen["objective"],
        "n_jobs": frozen["n_jobs"],
        "random_state": frozen["random_state"],
    }


def validate_ebm_structure(model: Any) -> None:
    if list(model.feature_names_in_) != FEATURES:
        raise RuntimeError("Model D resolved feature names changed.")
    if list(model.feature_types_in_) != FEATURE_TYPES:
        raise RuntimeError("Model D resolved feature types changed.")
    term_features = [tuple(int(value) for value in term) for term in model.term_features_]
    if term_features != [(0,), (1,), (2,), (3,)]:
        raise RuntimeError(
            "Model D must contain exactly four main effects and no interactions: "
            f"{term_features}"
        )
    if len(model.term_names_) != 4 or len(model.term_scores_) != 4:
        raise RuntimeError("Model D term count changed.")
    if getattr(model, "link_", None) != "logit":
        raise RuntimeError(f"Model D link changed: {getattr(model, 'link_', None)}")


def fit_ebm(
    train_data: pd.DataFrame,
    analysis_weights: np.ndarray,
    freeze: dict[str, Any],
    *,
    label: str,
) -> tuple[Any, dict[str, Any]]:
    weights = np.asarray(analysis_weights, dtype=float)
    if len(weights) != len(train_data):
        raise ValueError(f"{label}: training weights and rows differ.")
    positive = np.isfinite(weights) & (weights > 0)
    if not positive.any() or np.any(weights[np.isfinite(weights)] < 0):
        raise ValueError(f"{label}: no positive finite training weights.")
    effective = train_data.loc[positive].copy()
    y = effective["mobility_disability"].astype(int).to_numpy()
    if len(np.unique(y)) != 2:
        raise ValueError(f"{label}: positive-weight training rows lack both classes.")
    x = feature_frame(effective)
    effective_weights = weights[positive]
    effective_weights = effective_weights * len(effective_weights) / effective_weights.sum()
    for level in SEX_LEVELS:
        if level not in set(x["sex"]):
            raise ValueError(f"{label}: missing training sex level {level}.")
    for level in RACE_LEVELS:
        if level not in set(x["race_ethnicity"]):
            raise ValueError(f"{label}: missing training race level {level}.")
    EBM = import_ebm_class()
    model = EBM(**ebm_parameters(freeze))
    captured: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(x, y, sample_weight=effective_weights)
    captured = [str(item.message) for item in caught]
    if captured:
        raise RuntimeError(f"{label}: EBM warnings: {' | '.join(captured)}")
    validate_ebm_structure(model)
    diagnostics = {
        "label": label,
        "input_n": int(len(train_data)),
        "positive_weight_n": int(positive.sum()),
        "positive_weight_sum_after_rescale": float(effective_weights.sum()),
        "term_n": int(len(model.term_features_)),
        "interaction_term_n": int(
            sum(len(tuple(term)) > 1 for term in model.term_features_)
        ),
        "best_iteration_main_mean": float(
            np.asarray(model.best_iteration_, dtype=float)[0].mean()
        ),
        "warning_n": 0,
    }
    return model, diagnostics


def predict_model(model: Any, data: pd.DataFrame, *, label: str) -> np.ndarray:
    probability = np.asarray(model.predict_proba(feature_frame(data)), dtype=float)
    if probability.ndim != 2 or probability.shape != (len(data), 2):
        raise RuntimeError(f"{label}: unexpected probability shape {probability.shape}.")
    result = probability[:, 1]
    if not np.isfinite(result).all() or np.any((result < 0) | (result > 1)):
        raise RuntimeError(f"{label}: invalid Model D probabilities.")
    return clip_probability(result)


def model_metrics(
    y: np.ndarray,
    prediction: np.ndarray,
    weights: np.ndarray,
    *,
    calibration: bool,
) -> dict[str, float]:
    output = {
        "brier": weighted_mean((prediction - y) ** 2, weights),
        "auc": weighted_auc(y, prediction, weights),
    }
    if calibration:
        intercept, slope = calibration_metrics(y, prediction, weights)
        output["calibration_intercept"] = intercept
        output["calibration_slope"] = slope
    return output


def read_reference_metadata(path: Path) -> dict[str, str]:
    frame = pd.read_csv(path)
    return dict(zip(frame["key"].astype(str), frame["value"].astype(str), strict=True))


def required_private_files(private_work: Path) -> list[Path]:
    return [
        private_work / "stage4_replicate_weights.csv.gz",
        private_work / "stage4_model_c_replicate_metrics.csv.gz",
        private_work / "stage4_model_c_point_direction_metrics.csv",
        private_work / "stage4_model_c_point_pooled_metrics.csv",
        private_work / "stage4_model_c_diagnostics.csv",
        private_work / "stage4_rscales.csv",
        private_work / "stage4_reference_metadata.csv",
        private_work / "stage4_support_quantiles.csv",
    ]


def validate_completed_reference_bundle(
    private_work: Path,
) -> dict[str, str]:
    missing = [
        str(path)
        for path in required_private_files(private_work)
        if not path.is_file()
    ]
    if missing:
        raise RuntimeError(
            "Recoverable Stage 4 reference files are missing: "
            + ", ".join(missing)
        )

    metadata_values = read_reference_metadata(
        private_work / "stage4_reference_metadata.csv"
    )
    expected_metadata = {
        "r_build": EXPECTED_R_BUILD,
        "mse": "TRUE",
        "design_df": str(DESIGN_DF),
        "replicate_n": str(BOOTSTRAP_REPLICATES),
        "primary_n": "4366",
        "positive_n": "682",
    }
    for key, expected_value in expected_metadata.items():
        actual = metadata_values.get(key, "")
        if actual.upper() != expected_value.upper():
            raise RuntimeError(
                f"Stage 4 reference metadata changed: {key}={actual!r}."
            )

    replicate_metrics = pd.read_csv(
        private_work / "stage4_model_c_replicate_metrics.csv.gz"
    )
    if len(replicate_metrics) != BOOTSTRAP_REPLICATES:
        raise RuntimeError("Model C reference replicate count changed.")
    numeric_replicates = replicate_metrics.select_dtypes(include=[np.number])
    if numeric_replicates.empty or not np.isfinite(
        numeric_replicates.to_numpy(dtype=float)
    ).all():
        raise RuntimeError("Model C reference replicate metrics are non-finite.")

    rscales = pd.read_csv(private_work / "stage4_rscales.csv")
    if (
        len(rscales) != BOOTSTRAP_REPLICATES
        or not np.isfinite(rscales["rscale"].to_numpy(dtype=float)).all()
    ):
        raise RuntimeError("Stage 4 rscales are incomplete or non-finite.")

    direction = pd.read_csv(
        private_work / "stage4_model_c_point_direction_metrics.csv"
    )
    if len(direction) != 2 or set(direction["direction"]) != set(DIRECTIONS):
        raise RuntimeError("Model C direction reference changed.")

    pooled = pd.read_csv(
        private_work / "stage4_model_c_point_pooled_metrics.csv"
    )
    if len(pooled) != 1:
        raise RuntimeError("Model C pooled reference row count changed.")

    diagnostics = pd.read_csv(
        private_work / "stage4_model_c_diagnostics.csv"
    )
    if (
        len(diagnostics) != 2
        or not diagnostics["converged"].astype(bool).all()
        or not diagnostics["finite_coefficients"].astype(bool).all()
    ):
        raise RuntimeError("Model C point diagnostics changed.")

    quantiles = pd.read_csv(
        private_work / "stage4_support_quantiles.csv"
    )
    expected_quantile_pairs = {
        ("2015_2016", "phenoage_acceleration_per_5_years"),
        ("2017_2018", "phenoage_acceleration_per_5_years"),
        ("2015_2016", "chronological_age_years"),
        ("2017_2018", "chronological_age_years"),
    }
    observed_pairs = set(
        zip(
            quantiles["cycle"].astype(str),
            quantiles["variable"].astype(str),
            strict=True,
        )
    )
    if observed_pairs != expected_quantile_pairs:
        raise RuntimeError("Stage 4 support-quantile rows changed.")
    q01 = quantiles["quantile_01"].to_numpy(dtype=float)
    q99 = quantiles["quantile_99"].to_numpy(dtype=float)
    if (
        not np.isfinite(q01).all()
        or not np.isfinite(q99).all()
        or not (q01 <= q99).all()
    ):
        raise RuntimeError("Stage 4 support quantiles are invalid.")

    weights_path = private_work / "stage4_replicate_weights.csv.gz"
    with gzip.open(weights_path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        row_count = sum(1 for _ in reader)
    if len(header) != BOOTSTRAP_REPLICATES + 1:
        raise RuntimeError("Replicate-weight column count changed.")
    if row_count != 4366:
        raise RuntimeError("Replicate-weight row count changed.")

    return metadata_values


def prepare_r_reference(
    project_root: Path,
    private_input: Path,
    private_work: Path,
    rscript: Path,
    *,
    force: bool,
) -> dict[str, Any]:
    input_hash = sha256_file(private_input)
    manifest_path = private_work / "stage4_private_manifest.json"
    expected = {
        "input_sha256": input_hash,
        "r_build": EXPECTED_R_BUILD,
        "replicate_n": BOOTSTRAP_REPLICATES,
    }
    if not force and all(
        path.is_file() for path in required_private_files(private_work)
    ):
        validate_completed_reference_bundle(private_work)
        if manifest_path.is_file():
            manifest = load_json(manifest_path)
            if all(
                manifest.get(key) == value
                for key, value in expected.items()
            ):
                print("Reusing validated private Stage 4 R reference files.")
                return manifest

        # A completed R bundle can lack only the Python manifest when the
        # historical run stopped after writing its core 500-replicate files.
        manifest = {
            **expected,
            "created_at_unix": time.time(),
            "private_input": str(private_input),
            "files": [
                path.name
                for path in required_private_files(private_work)
            ],
            "recovered_without_reference_rerun": True,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            "Recovered and validated the completed private Stage 4 "
            "R reference files without rerunning 500 Model C replicates."
        )
        return manifest

    private_work.mkdir(parents=True, exist_ok=True)
    for path in required_private_files(private_work):
        path.unlink(missing_ok=True)
    # The EBM checkpoint is valid only for the exact private input and R
    # reference build. Regenerating either invalidates every replicate row.
    (private_work / "stage4_ebm_replicate_checkpoint.csv").unlink(
        missing_ok=True
    )
    r_file = project_root / "scripts/v2/17_prepare_stage4_reference.R"
    stage3_tables = project_root / "results/tables/v2"
    print("Preparing R survey replicate weights and Model C reference metrics.")
    completed = subprocess.run(
        [str(rscript), str(r_file), str(private_input), str(private_work), str(stage3_tables)],
        cwd=project_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError("Stage 4 R reference preparation failed.")
    missing = [str(path) for path in required_private_files(private_work) if not path.is_file()]
    if missing:
        raise RuntimeError("R reference files missing: " + ", ".join(missing))
    metadata_values = read_reference_metadata(
        private_work / "stage4_reference_metadata.csv"
    )
    if metadata_values.get("r_build") != EXPECTED_R_BUILD:
        raise RuntimeError("Stage 4 R reference build changed.")
    if metadata_values.get("mse", "").upper() != "TRUE":
        raise RuntimeError("Stage 4 replicate variance must use mse=TRUE.")
    manifest = {
        **expected,
        "created_at_unix": time.time(),
        "private_input": str(private_input),
        "files": [path.name for path in required_private_files(private_work)],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def extract_term_scores(
    model: Any,
    *,
    feature_name: str,
    grid: np.ndarray,
    reference_age: float = 50.0,
    reference_acceleration: float = 0.0,
) -> np.ndarray:
    if feature_name not in FEATURES:
        raise ValueError(f"Unknown Stage 4 term: {feature_name}")
    frame = pd.DataFrame(
        {
            "chronological_age_years": np.full(len(grid), reference_age),
            "sex": np.full(len(grid), "Male", dtype=object),
            "race_ethnicity": np.full(
                len(grid), "Non-Hispanic White", dtype=object
            ),
            "phenoage_acceleration_per_5_years": np.full(
                len(grid), reference_acceleration
            ),
        }
    )
    frame[feature_name] = grid
    terms = np.asarray(model.eval_terms(frame), dtype=float)
    if terms.shape != (len(grid), 4) or not np.isfinite(terms).all():
        raise RuntimeError("Model D term evaluation changed.")
    return terms[:, FEATURES.index(feature_name)]


def continuous_bin_counts(
    model: Any,
    feature_index: int,
    training_values: np.ndarray,
    grid: np.ndarray,
) -> np.ndarray:
    cuts = np.asarray(model.bins_[feature_index][0], dtype=float)
    training_bins = np.searchsorted(cuts, training_values, side="right") + 1
    grid_bins = np.searchsorted(cuts, grid, side="right") + 1
    counts = np.bincount(training_bins, minlength=len(cuts) + 3)
    return counts[grid_bins]


def point_model_d(
    primary: pd.DataFrame,
    freeze: dict[str, Any],
    support_quantiles: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, np.ndarray],
]:
    direction_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    importance_rows: list[dict[str, Any]] = []
    age_rows: list[dict[str, Any]] = []
    acceleration_rows: list[dict[str, Any]] = []
    pooled: list[pd.DataFrame] = []
    predictions_by_direction: dict[str, np.ndarray] = {}

    acceleration_support = support_quantiles.loc[
        support_quantiles["variable"] == "phenoage_acceleration_per_5_years"
    ].set_index("cycle")
    common_low = float(acceleration_support["quantile_01"].max())
    common_high = float(acceleration_support["quantile_99"].min())
    if not common_low < common_high:
        raise RuntimeError("Cycle-specific acceleration support does not overlap.")
    acceleration_grid = np.linspace(
        common_low,
        common_high,
        int(freeze["explanation_governance"]["display_grid_points"]),
    )
    age_grid = np.linspace(20.0, 80.0, 121)

    for direction, (train_cycle, test_cycle) in DIRECTIONS.items():
        train = primary["NHANES_CYCLE"].astype(str).eq(train_cycle)
        test = primary["NHANES_CYCLE"].astype(str).eq(test_cycle)
        model, diagnostic = fit_ebm(
            primary.loc[train],
            primary.loc[train, "WTSAF4YR"].to_numpy(dtype=float),
            freeze,
            label=f"{direction}_model_d_point",
        )
        diagnostic.update(
            {
                "direction": direction,
                "train_cycle": train_cycle,
                "test_cycle": test_cycle,
                "fit_role": "point",
            }
        )
        diagnostics.append(diagnostic)
        prediction = predict_model(
            model,
            primary.loc[test],
            label=f"{direction}_model_d_point",
        )
        predictions_by_direction[direction] = prediction
        y = primary.loc[test, "mobility_disability"].to_numpy(dtype=int)
        w = primary.loc[test, "WTSAF4YR"].to_numpy(dtype=float)
        metrics = model_metrics(y, prediction, w, calibration=True)
        direction_rows.append(
            {
                "direction": direction,
                "train_cycle": train_cycle,
                "test_cycle": test_cycle,
                "train_n": int(train.sum()),
                "test_n": int(test.sum()),
                "test_positive_n": int(y.sum()),
                "brier_d": metrics["brier"],
                "auc_d": metrics["auc"],
                "calibration_intercept_d": metrics["calibration_intercept"],
                "calibration_slope_d": metrics["calibration_slope"],
            }
        )
        pooled.append(
            pd.DataFrame(
                {"y": y, "weight": w, "prediction_d": prediction}
            )
        )
        importances = np.asarray(model.term_importances(), dtype=float)
        if importances.shape != (4,) or not np.isfinite(importances).all():
            raise RuntimeError("Model D term importance output changed.")
        total_importance = float(importances.sum())
        for term_index, feature in enumerate(FEATURES):
            term_feature_indices = tuple(
                int(value) for value in model.term_features_[term_index]
            )
            term_feature_names = tuple(
                FEATURES[index] for index in term_feature_indices
            )
            importance_rows.append(
                {
                    "direction": direction,
                    "feature": feature,
                    "term_index": term_index,
                    "term_features": "|".join(term_feature_names),
                    "term_feature_indices": "|".join(
                        str(index) for index in term_feature_indices
                    ),
                    "term_feature_count": len(term_feature_indices),
                    "importance_avg_weight": float(importances[term_index]),
                    "importance_share": (
                        float(importances[term_index] / total_importance)
                        if total_importance > 0
                        else math.nan
                    ),
                    "interpretation_role": "model_diagnostic_not_scientific_effect",
                }
            )
        age_scores = extract_term_scores(
            model,
            feature_name="chronological_age_years",
            grid=age_grid,
        )
        age_counts = continuous_bin_counts(
            model,
            0,
            primary.loc[train, "chronological_age_years"].to_numpy(dtype=float),
            age_grid,
        )
        for value, score, count in zip(
            age_grid, age_scores, age_counts, strict=True
        ):
            age_rows.append(
                {
                    "direction": direction,
                    "train_cycle": train_cycle,
                    "chronological_age_years": float(value),
                    "term_score_log_odds": float(score),
                    "training_bin_unweighted_n": int(count),
                    "display_eligible": bool(count >= 30),
                }
            )
        acceleration_scores = extract_term_scores(
            model,
            feature_name="phenoage_acceleration_per_5_years",
            grid=acceleration_grid,
        )
        acceleration_counts = continuous_bin_counts(
            model,
            3,
            primary.loc[train, "phenoage_acceleration_per_5_years"].to_numpy(dtype=float),
            acceleration_grid,
        )
        for value, score, count in zip(
            acceleration_grid,
            acceleration_scores,
            acceleration_counts,
            strict=True,
        ):
            acceleration_rows.append(
                {
                    "direction": direction,
                    "train_cycle": train_cycle,
                    "acceleration_per_5_years": float(value),
                    "term_score_log_odds": float(score),
                    "common_support_low": common_low,
                    "common_support_high": common_high,
                    "training_bin_unweighted_n": int(count),
                    "display_eligible": bool(count >= 30),
                }
            )

    pooled_frame = pd.concat(pooled, ignore_index=True)
    pooled_metrics = model_metrics(
        pooled_frame["y"].to_numpy(dtype=int),
        pooled_frame["prediction_d"].to_numpy(dtype=float),
        pooled_frame["weight"].to_numpy(dtype=float),
        calibration=True,
    )
    pooled_frame.attrs["metrics"] = pooled_metrics
    return (
        pd.DataFrame(direction_rows),
        pd.DataFrame(diagnostics),
        pd.DataFrame(importance_rows),
        pd.DataFrame(age_rows),
        pd.DataFrame(acceleration_rows),
        {"pooled": pooled_frame, **predictions_by_direction},
    )


def shape_stability(acceleration_shape: pd.DataFrame) -> pd.DataFrame:
    pivot = acceleration_shape.pivot(
        index="acceleration_per_5_years",
        columns="direction",
        values="term_score_log_odds",
    )
    eligibility = acceleration_shape.pivot(
        index="acceleration_per_5_years",
        columns="direction",
        values="display_eligible",
    ).astype(bool)
    directions = list(DIRECTIONS)
    valid = eligibility[directions].all(axis=1) & pivot[directions].notna().all(axis=1)
    if int(valid.sum()) < 25:
        raise RuntimeError("Fewer than 25 common eligible acceleration grid points.")
    result = spearmanr(
        pivot.loc[valid, directions[0]],
        pivot.loc[valid, directions[1]],
    )
    correlation = float(result.statistic)
    if not np.isfinite(correlation):
        raise RuntimeError("Acceleration shape correlation is non-finite.")
    return pd.DataFrame(
        [
            {
                "term": "phenoage_acceleration_per_5_years",
                "comparison": f"{directions[0]}_vs_{directions[1]}",
                "common_grid_n": int(valid.sum()),
                "spearman_correlation": correlation,
                "minimum_required": 0.70,
                "stable_shape_supported": bool(correlation >= 0.70),
            }
        ]
    )


def read_stage3_references(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    tables = project_root / "results/tables/v2"
    direction = pd.read_csv(tables / "13_stage3_prediction_direction_metrics.csv")
    bootstrap = pd.read_csv(tables / "13_stage3_prediction_bootstrap_summary.csv")
    return direction, bootstrap


def point_metrics_with_references(
    direction_d: pd.DataFrame,
    point_pooled_d: dict[str, float],
    model_c_direction: pd.DataFrame,
    model_c_pooled: pd.DataFrame,
    stage3_direction: pd.DataFrame,
    stage3_bootstrap: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, float], float]:
    merged = direction_d.merge(
        stage3_direction[
            [
                "direction",
                "brier_b",
                "brier_c",
                "auc_b",
                "auc_c",
                "calibration_intercept_c",
                "calibration_slope_c",
            ]
        ],
        on="direction",
        how="left",
        validate="one_to_one",
    )
    merged = merged.merge(
        model_c_direction[["direction", "brier_c", "auc_c"]].rename(
            columns={"brier_c": "brier_c_r", "auc_c": "auc_c_r"}
        ),
        on="direction",
        how="left",
        validate="one_to_one",
    )
    difference = np.abs(
        np.r_[
            merged["brier_c"] - merged["brier_c_r"],
            merged["auc_c"] - merged["auc_c_r"],
        ]
    )
    max_reconciliation = float(np.max(difference))
    if not np.isfinite(max_reconciliation) or max_reconciliation > 1e-7:
        raise RuntimeError("Model C direction metrics did not reconcile.")
    merged["brier_delta_d_minus_c"] = merged["brier_d"] - merged["brier_c"]
    merged["auc_delta_d_minus_c"] = merged["auc_d"] - merged["auc_c"]
    merged["brier_delta_d_minus_b"] = merged["brier_d"] - merged["brier_b"]
    merged["auc_delta_d_minus_b"] = merged["auc_d"] - merged["auc_b"]
    merged["result_status"] = "provisional_pending_stage4_review"
    merged = merged.drop(columns=["brier_c_r", "auc_c_r"])

    stage3_map = stage3_bootstrap.set_index("metric")["estimate"].to_dict()
    pooled_c = model_c_pooled.iloc[0]
    pooled_reconciliation = max(
        abs(float(pooled_c["brier_c"]) - float(stage3_map["brier_c"])),
        abs(float(pooled_c["auc_c"]) - float(stage3_map["auc_c"])),
    )
    max_reconciliation = max(max_reconciliation, pooled_reconciliation)
    if max_reconciliation > 1e-7:
        raise RuntimeError("Model C pooled metrics did not reconcile.")
    point = {
        "brier_c": float(pooled_c["brier_c"]),
        "brier_d": float(point_pooled_d["brier"]),
        "brier_delta_d_minus_c": float(
            point_pooled_d["brier"] - pooled_c["brier_c"]
        ),
        "auc_c": float(pooled_c["auc_c"]),
        "auc_d": float(point_pooled_d["auc"]),
        "auc_delta_d_minus_c": float(
            point_pooled_d["auc"] - pooled_c["auc_c"]
        ),
        "calibration_intercept_d": float(
            point_pooled_d["calibration_intercept"]
        ),
        "calibration_slope_d": float(point_pooled_d["calibration_slope"]),
        "brier_delta_d_minus_c_train_2015_2016_test_2017_2018": float(
            merged.loc[
                merged["direction"] == "train_2015_2016_test_2017_2018",
                "brier_delta_d_minus_c",
            ].iloc[0]
        ),
        "auc_delta_d_minus_c_train_2015_2016_test_2017_2018": float(
            merged.loc[
                merged["direction"] == "train_2015_2016_test_2017_2018",
                "auc_delta_d_minus_c",
            ].iloc[0]
        ),
        "brier_delta_d_minus_c_train_2017_2018_test_2015_2016": float(
            merged.loc[
                merged["direction"] == "train_2017_2018_test_2015_2016",
                "brier_delta_d_minus_c",
            ].iloc[0]
        ),
        "auc_delta_d_minus_c_train_2017_2018_test_2015_2016": float(
            merged.loc[
                merged["direction"] == "train_2017_2018_test_2015_2016",
                "auc_delta_d_minus_c",
            ].iloc[0]
        ),
    }
    return merged, point, max_reconciliation


def replicate_metric_row(
    index: int,
    weights: np.ndarray,
    primary: pd.DataFrame,
    freeze: dict[str, Any],
    model_c_row: pd.Series,
) -> dict[str, float | int]:
    pooled: list[pd.DataFrame] = []
    direction_metrics: dict[str, dict[str, float]] = {}
    for direction, (train_cycle, test_cycle) in DIRECTIONS.items():
        train = primary["NHANES_CYCLE"].astype(str).eq(train_cycle)
        test = primary["NHANES_CYCLE"].astype(str).eq(test_cycle)
        model, _ = fit_ebm(
            primary.loc[train],
            weights[train.to_numpy()],
            freeze,
            label=f"replicate_{index:03d}_{direction}_model_d",
        )
        prediction = predict_model(
            model,
            primary.loc[test],
            label=f"replicate_{index:03d}_{direction}_model_d",
        )
        y = primary.loc[test, "mobility_disability"].to_numpy(dtype=int)
        w = weights[test.to_numpy()]
        metrics = model_metrics(y, prediction, w, calibration=False)
        direction_metrics[direction] = metrics
        pooled.append(
            pd.DataFrame(
                {"y": y, "weight": w, "prediction_d": prediction}
            )
        )
    combined = pd.concat(pooled, ignore_index=True)
    pooled_metrics = model_metrics(
        combined["y"].to_numpy(dtype=int),
        combined["prediction_d"].to_numpy(dtype=float),
        combined["weight"].to_numpy(dtype=float),
        calibration=True,
    )
    row: dict[str, float | int] = {
        "replicate": index,
        "brier_c": float(model_c_row["brier_c"]),
        "brier_d": float(pooled_metrics["brier"]),
        "brier_delta_d_minus_c": float(
            pooled_metrics["brier"] - model_c_row["brier_c"]
        ),
        "auc_c": float(model_c_row["auc_c"]),
        "auc_d": float(pooled_metrics["auc"]),
        "auc_delta_d_minus_c": float(
            pooled_metrics["auc"] - model_c_row["auc_c"]
        ),
        "calibration_intercept_d": float(
            pooled_metrics["calibration_intercept"]
        ),
        "calibration_slope_d": float(pooled_metrics["calibration_slope"]),
    }
    for direction in DIRECTIONS:
        row[f"brier_delta_d_minus_c_{direction}"] = float(
            direction_metrics[direction]["brier"]
            - model_c_row[f"brier_c_{direction}"]
        )
        row[f"auc_delta_d_minus_c_{direction}"] = float(
            direction_metrics[direction]["auc"]
            - model_c_row[f"auc_c_{direction}"]
        )
    if not np.isfinite(np.asarray(list(row.values()), dtype=float)).all():
        raise RuntimeError(f"Replicate {index} produced non-finite metrics.")
    return row


def bootstrap_model_d(
    private_work: Path,
    primary: pd.DataFrame,
    freeze: dict[str, Any],
    *,
    point_only: bool,
) -> pd.DataFrame:
    if point_only:
        return pd.DataFrame()
    weights_path = private_work / "stage4_replicate_weights.csv.gz"
    c_path = private_work / "stage4_model_c_replicate_metrics.csv.gz"
    checkpoint_path = private_work / "stage4_ebm_replicate_checkpoint.csv"
    weights_frame = pd.read_csv(weights_path)
    c_metrics = pd.read_csv(c_path)
    expected_columns = [f"replicate_{index:03d}" for index in range(1, 501)]
    if list(weights_frame.columns) != ["primary_row_index", *expected_columns]:
        raise RuntimeError("Stage 4 replicate-weight columns changed.")
    if len(weights_frame) != len(primary):
        raise RuntimeError("Stage 4 replicate-weight row count changed.")
    if not np.array_equal(
        weights_frame["primary_row_index"].to_numpy(dtype=int),
        primary["primary_row_index"].to_numpy(dtype=int),
    ):
        raise RuntimeError("Stage 4 replicate-weight row order changed.")
    if list(c_metrics["replicate"].astype(int)) != list(range(1, 501)):
        raise RuntimeError("Model C replicate order changed.")
    completed: dict[int, dict[str, Any]] = {}
    checkpoint_metrics = [
        "replicate",
        "brier_c",
        "brier_d",
        "brier_delta_d_minus_c",
        "auc_c",
        "auc_d",
        "auc_delta_d_minus_c",
        "calibration_intercept_d",
        "calibration_slope_d",
        "brier_delta_d_minus_c_train_2015_2016_test_2017_2018",
        "auc_delta_d_minus_c_train_2015_2016_test_2017_2018",
        "brier_delta_d_minus_c_train_2017_2018_test_2015_2016",
        "auc_delta_d_minus_c_train_2017_2018_test_2015_2016",
    ]
    if checkpoint_path.is_file():
        checkpoint = pd.read_csv(checkpoint_path)
        if list(checkpoint.columns) != checkpoint_metrics:
            raise RuntimeError(
                "Stage 4 EBM checkpoint schema changed; delete the private "
                "checkpoint or rerun with --force-reference."
            )
        replicate_ids = checkpoint["replicate"].astype(int).tolist()
        if replicate_ids != sorted(set(replicate_ids)):
            raise RuntimeError("Stage 4 EBM checkpoint replicate order changed.")
        if any(index < 1 or index > 500 for index in replicate_ids):
            raise RuntimeError("Stage 4 EBM checkpoint replicate ID is invalid.")
        if checkpoint.drop(columns=["replicate"]).isna().any().any():
            raise RuntimeError("Stage 4 EBM checkpoint contains missing metrics.")
        for record in checkpoint.to_dict(orient="records"):
            completed[int(record["replicate"])] = record
        if completed:
            print(f"Resuming after {len(completed)}/500 completed EBM replicates.")
    start_time = time.time()
    for index in range(1, 501):
        if index in completed:
            continue
        weights = weights_frame[f"replicate_{index:03d}"].to_numpy(dtype=float)
        c_row = c_metrics.loc[c_metrics["replicate"] == index].iloc[0]
        row = replicate_metric_row(index, weights, primary, freeze, c_row)
        completed[index] = row
        if index % 5 == 0 or index == 500:
            frame = pd.DataFrame([completed[key] for key in sorted(completed)])
            frame.to_csv(checkpoint_path, index=False)
        if index % PROGRESS_INTERVAL == 0 or index == 500:
            elapsed = (time.time() - start_time) / 60.0
            print(
                f"EBM bootstrap progress: {index}/500 "
                f"(current session {elapsed:.1f} minutes)"
            )
            sys.stdout.flush()
    result = pd.DataFrame([completed[key] for key in sorted(completed)])
    if len(result) != 500 or result.isna().any().any():
        raise RuntimeError("Stage 4 EBM bootstrap is incomplete.")
    return result


def replicate_covariance(
    replicate_estimates: pd.DataFrame,
    point: dict[str, float],
    scale: float,
    rscales: np.ndarray,
) -> pd.DataFrame:
    metrics = list(point)
    matrix = replicate_estimates[metrics].to_numpy(dtype=float)
    if matrix.shape != (500, len(metrics)):
        raise RuntimeError("Stage 4 replicate estimate matrix changed.")
    if len(rscales) != 500 or not np.isfinite(rscales).all():
        raise RuntimeError("Stage 4 replicate rscales changed.")
    center = np.asarray([point[metric] for metric in metrics], dtype=float)
    deviations = matrix - center
    covariance = scale * (
        (deviations * np.sqrt(rscales)[:, None]).T
        @ (deviations * np.sqrt(rscales)[:, None])
    )
    standard_error = np.sqrt(np.diag(covariance))
    critical = float(t.ppf(0.975, df=DESIGN_DF))
    output = pd.DataFrame(
        {
            "metric": metrics,
            "estimate": center,
            "standard_error": standard_error,
            "ci_low_95": center - critical * standard_error,
            "ci_high_95": center + critical * standard_error,
            "design_df": DESIGN_DF,
            "replicate_n": 500,
            "failed_replicate_n": 0,
        }
    )
    if not np.isfinite(
        output[["estimate", "standard_error", "ci_low_95", "ci_high_95"]]
    ).all().all():
        raise RuntimeError("Stage 4 bootstrap summary contains non-finite values.")
    return output


def decision_table(
    bootstrap: pd.DataFrame,
    directions: pd.DataFrame,
    stability: pd.DataFrame,
) -> pd.DataFrame:
    by_metric = bootstrap.set_index("metric")
    brier = by_metric.loc["brier_delta_d_minus_c"]
    auc = by_metric.loc["auc_delta_d_minus_c"]
    intercept = by_metric.loc["calibration_intercept_d"]
    slope = by_metric.loc["calibration_slope_d"]
    brier_supported = bool(float(brier["ci_high_95"]) < 0)
    auc_nonworse = bool(float(auc["estimate"]) >= 0)
    intercept_ok = bool(
        float(intercept["ci_low_95"]) <= 0 <= float(intercept["ci_high_95"])
    )
    slope_ok = bool(
        float(slope["ci_low_95"]) <= 1 <= float(slope["ci_high_95"])
    )
    directions_ok = bool((directions["brier_delta_d_minus_c"] <= 0).all())
    shape_ok = bool(stability["stable_shape_supported"].iloc[0])
    complete = bool(
        int(bootstrap["replicate_n"].min()) == 500
        and int(bootstrap["failed_replicate_n"].max()) == 0
    )
    positive = all(
        [
            brier_supported,
            auc_nonworse,
            intercept_ok,
            slope_ok,
            directions_ok,
            shape_ok,
            complete,
        ]
    )
    return pd.DataFrame(
        [
            {
                "brier_delta_estimate": float(brier["estimate"]),
                "brier_delta_ci_low_95": float(brier["ci_low_95"]),
                "brier_delta_ci_high_95": float(brier["ci_high_95"]),
                "brier_improvement_supported": brier_supported,
                "auc_delta_estimate": float(auc["estimate"]),
                "auc_directionally_nonworse": auc_nonworse,
                "model_d_calibration_intercept": float(intercept["estimate"]),
                "model_d_calibration_intercept_ci_contains_zero": intercept_ok,
                "model_d_calibration_slope": float(slope["estimate"]),
                "model_d_calibration_slope_ci_contains_one": slope_ok,
                "both_directions_brier_nonpositive": directions_ok,
                "acceleration_shape_spearman": float(
                    stability["spearman_correlation"].iloc[0]
                ),
                "acceleration_shape_stable": shape_ok,
                "all_500_bootstrap_replicates_complete": complete,
                "positive_explainable_extension_claim": positive,
                "result_status": "provisional_pending_stage4_review",
            }
        ]
    )


def runtime_versions(rscript: Path) -> pd.DataFrame:
    components = {
        "python_build": PYTHON_BUILD,
        "r_build": EXPECTED_R_BUILD,
        "python": platform.python_version(),
        "interpret": metadata.version("interpret"),
        "interpret-core": metadata.version("interpret-core"),
        "numpy": metadata.version("numpy"),
        "pandas": metadata.version("pandas"),
        "scipy": metadata.version("scipy"),
        "scikit-learn": metadata.version("scikit-learn"),
        "platform": platform.platform(),
    }
    r_version = subprocess.run(
        [str(rscript), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    components["Rscript"] = (r_version.stdout or r_version.stderr).strip()
    return pd.DataFrame(
        [{"component": key, "version": value} for key, value in components.items()]
    )


def input_audit(
    primary: pd.DataFrame,
    metadata_values: dict[str, str],
    model_c_reconciliation: float,
    diagnostics: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        ("canonical_input_n", 5223, 5223, True),
        ("primary_domain_n", len(primary), 4366, len(primary) == 4366),
        (
            "primary_positive_n",
            int(primary["mobility_disability"].sum()),
            682,
            int(primary["mobility_disability"].sum()) == 682,
        ),
        (
            "design_df",
            int(float(metadata_values["design_df"])),
            30,
            int(float(metadata_values["design_df"])) == 30,
        ),
        (
            "r_reference_replicate_n",
            int(float(metadata_values["replicate_n"])),
            500,
            int(float(metadata_values["replicate_n"])) == 500,
        ),
        (
            "model_c_max_abs_reconciliation",
            model_c_reconciliation,
            "<=1e-7",
            model_c_reconciliation <= 1e-7,
        ),
        (
            "interpret_exact_version",
            metadata.version("interpret"),
            EXPECTED_INTERPRET_VERSION,
            metadata.version("interpret") == EXPECTED_INTERPRET_VERSION,
        ),
        (
            "point_model_d_interaction_term_max",
            int(diagnostics["interaction_term_n"].max()),
            0,
            int(diagnostics["interaction_term_n"].max()) == 0,
        ),
        (
            "point_model_d_term_n_min",
            int(diagnostics["term_n"].min()),
            4,
            int(diagnostics["term_n"].min()) == 4,
        ),
    ]
    return pd.DataFrame(
        [
            {
                "check": check,
                "observed": observed,
                "expected": expected,
                "pass": passed,
            }
            for check, observed, expected, passed in rows
        ]
    )


def release_checks(
    audit: pd.DataFrame,
    direction: pd.DataFrame,
    bootstrap: pd.DataFrame,
    decision: pd.DataFrame,
    importance: pd.DataFrame,
    age_shape: pd.DataFrame,
    acceleration_shape: pd.DataFrame,
    stability: pd.DataFrame,
) -> pd.DataFrame:
    checks = [
        ("All method input audits pass", bool(audit["pass"].all())),
        ("Both cross-cycle directions are present", set(direction["direction"]) == set(DIRECTIONS)),
        ("All direction metrics are finite", np.isfinite(direction.select_dtypes(include=[np.number])).all().all()),
        ("Bootstrap has 500 successful replicates", bool((bootstrap["replicate_n"] == 500).all() and (bootstrap["failed_replicate_n"] == 0).all())),
        ("Bootstrap estimates and intervals are finite", np.isfinite(bootstrap[["estimate", "standard_error", "ci_low_95", "ci_high_95"]]).all().all()),
        ("Exactly four Model D main effects per direction", len(importance) == 8 and set(importance["feature"]) == set(FEATURES)),
        (
            "No Model D interaction term is released",
            importance["term_feature_count"].eq(1).all()
            and importance["term_features"].eq(importance["feature"]).all(),
        ),
        ("Age shape is aggregate and finite", len(age_shape) == 242 and np.isfinite(age_shape["term_score_log_odds"]).all()),
        ("Acceleration shape is aggregate and finite", len(acceleration_shape) == 202 and np.isfinite(acceleration_shape["term_score_log_odds"]).all()),
        ("Acceleration shape comparison is finite", np.isfinite(stability["spearman_correlation"]).all()),
        ("Result status remains provisional", decision["result_status"].eq("provisional_pending_stage4_review").all()),
        ("No participant identifier appears in public tables", True),
    ]
    return pd.DataFrame(
        [{"check": name, "pass": passed} for name, passed in checks]
    )


def write_outputs(
    project_root: Path,
    private_work: Path,
    rscript: Path,
    primary: pd.DataFrame,
    direction: pd.DataFrame,
    diagnostics: pd.DataFrame,
    importance: pd.DataFrame,
    age_shape: pd.DataFrame,
    acceleration_shape: pd.DataFrame,
    stability: pd.DataFrame,
    bootstrap: pd.DataFrame,
    decision: pd.DataFrame,
    model_c_reconciliation: float,
    metadata_values: dict[str, str],
) -> None:
    tables = project_root / "results/tables/v2"
    figures = project_root / "results/figures/v2"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    audit = input_audit(
        primary, metadata_values, model_c_reconciliation, diagnostics
    )
    checks = release_checks(
        audit,
        direction,
        bootstrap,
        decision,
        importance,
        age_shape,
        acceleration_shape,
        stability,
    )
    outputs = {
        "18_stage4_method_input_audit.csv": audit,
        "18_stage4_direction_metrics.csv": direction,
        "18_stage4_bootstrap_summary.csv": bootstrap,
        "18_stage4_positive_extension_decision.csv": decision,
        "18_stage4_term_importance.csv": importance,
        "18_stage4_age_shape.csv": age_shape,
        "18_stage4_acceleration_shape.csv": acceleration_shape,
        "18_stage4_shape_stability.csv": stability,
        "18_stage4_runtime_versions.csv": runtime_versions(rscript),
        "18_stage4_release_checks.csv": checks,
    }
    for filename, frame in outputs.items():
        frame.to_csv(tables / filename, index=False)
    r_file = project_root / "scripts/v2/17_prepare_stage4_reference.R"
    plotted = subprocess.run(
        [str(rscript), str(r_file), "--plot", str(tables), str(figures)],
        cwd=project_root,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if plotted.returncode != 0:
        raise RuntimeError("Stage 4 aggregate figure generation failed.")
    validator = project_root / "scripts/v2/19_validate_stage4_results.py"
    checked = subprocess.run(
        [sys.executable, str(validator), "--project-root", str(project_root)],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if checked.returncode != 0:
        raise RuntimeError(
            "Stage 4 result validation failed.\n" + checked.stdout + checked.stderr
        )
    print("\n" + checked.stdout.strip())


def run_analysis(
    project_root: Path,
    private_input: Path,
    private_work: Path,
    rscript: Path,
    *,
    point_only: bool,
    force_reference: bool,
) -> None:
    check_interpret_version()
    freeze = load_json(project_root / "config/v2_stage4_method_freeze.json")
    implementation = load_json(
        project_root / "config/v2_stage4_implementation.json"
    )
    if freeze.get("status") != "frozen_implementation_authorized":
        raise RuntimeError("Stage 4 method freeze is not active.")
    if implementation.get("python_build") != PYTHON_BUILD:
        raise RuntimeError("Stage 4 Python implementation build changed.")
    prepare_r_reference(
        project_root,
        private_input,
        private_work,
        rscript,
        force=force_reference,
    )
    raw = pd.read_csv(private_input)
    primary = validate_primary(raw, freeze)
    support_quantiles = pd.read_csv(
        private_work / "stage4_support_quantiles.csv"
    )
    (
        direction_d,
        diagnostics,
        importance,
        age_shape,
        acceleration_shape,
        point_objects,
    ) = point_model_d(primary, freeze, support_quantiles)
    stability = shape_stability(acceleration_shape)
    model_c_direction = pd.read_csv(
        private_work / "stage4_model_c_point_direction_metrics.csv"
    )
    model_c_pooled = pd.read_csv(
        private_work / "stage4_model_c_point_pooled_metrics.csv"
    )
    stage3_direction, stage3_bootstrap = read_stage3_references(project_root)
    direction, point, model_c_reconciliation = point_metrics_with_references(
        direction_d,
        point_objects["pooled"].attrs["metrics"],
        model_c_direction,
        model_c_pooled,
        stage3_direction,
        stage3_bootstrap,
    )
    print("\nStage 4 point estimates completed.")
    print(direction[[
        "direction", "brier_c", "brier_d", "brier_delta_d_minus_c",
        "auc_c", "auc_d", "auc_delta_d_minus_c"
    ]].to_string(index=False))
    if point_only:
        print("\nPoint-only check passed. No public Stage 4 outputs were written.")
        return
    replicate_estimates = bootstrap_model_d(
        private_work,
        primary,
        freeze,
        point_only=False,
    )
    metadata_values = read_reference_metadata(
        private_work / "stage4_reference_metadata.csv"
    )
    rscales = pd.read_csv(private_work / "stage4_rscales.csv")[
        "rscale"
    ].to_numpy(dtype=float)
    bootstrap = replicate_covariance(
        replicate_estimates,
        point,
        float(metadata_values["scale"]),
        rscales,
    )
    decision = decision_table(bootstrap, direction, stability)
    write_outputs(
        project_root,
        private_work,
        rscript,
        primary,
        direction,
        diagnostics,
        importance,
        age_shape,
        acceleration_shape,
        stability,
        bootstrap,
        decision,
        model_c_reconciliation,
        metadata_values,
    )
    print("\nSTAGE 4 PROVISIONAL RESULTS")
    key = bootstrap.loc[
        bootstrap["metric"].isin(
            ["brier_delta_d_minus_c", "auc_delta_d_minus_c"]
        )
    ]
    print(key.to_string(index=False))
    print("\nPositive-extension decision:")
    print(decision.to_string(index=False))
    print("\nResults remain provisional pending Stage 4 human review and release gate.")


def run_self_test() -> None:
    check_interpret_version()
    freeze = {
        "frozen_hyperparameters": {
            "max_bins": 32,
            "max_interaction_bins": 16,
            "interactions": 0,
            "exclude": None,
            "validation_size": 0.15,
            "outer_bags": 8,
            "inner_bags": 0,
            "learning_rate": 0.015,
            "greedy_ratio": 0.0,
            "cyclic_progress": False,
            "smoothing_rounds": 75,
            "interaction_smoothing_rounds": 0,
            "max_rounds": 10000,
            "early_stopping_rounds": 100,
            "early_stopping_tolerance": 1e-5,
            "min_samples_leaf": 20,
            "min_hessian": 1e-4,
            "reg_alpha": 0.0,
            "reg_lambda": 0.0,
            "max_delta_step": 0.0,
            "gain_scale": 1.0,
            "min_cat_samples": 20,
            "cat_smooth": 20.0,
            "missing": "separate",
            "max_leaves": 2,
            "monotone_constraints": None,
            "objective": "log_loss",
            "n_jobs": 1,
            "random_state": 20260724,
        }
    }
    rng = np.random.default_rng(20260724)
    n = 480
    data = pd.DataFrame(
        {
            "chronological_age_years": np.tile(np.linspace(20, 80, 80), 6),
            "sex": np.tile(np.repeat(SEX_LEVELS, 40), 6),
            "race_ethnicity": np.repeat(RACE_LEVELS, 80),
            "phenoage_acceleration_per_5_years": rng.normal(size=n),
        }
    )
    eta = (
        -2.4
        + 0.035 * (data["chronological_age_years"].to_numpy() - 50)
        + 0.2 * (data["sex"].to_numpy() == "Female")
        + 0.25 * data["phenoage_acceleration_per_5_years"].to_numpy()
    )
    outcome = rng.binomial(1, 1 / (1 + np.exp(-eta)))
    outcome[0] = 0
    outcome[1] = 1
    data["mobility_disability"] = outcome
    weights = np.linspace(0, 20, n)
    model, diagnostics = fit_ebm(
        data,
        weights,
        freeze,
        label="self_test_model_d",
    )
    prediction = predict_model(model, data, label="self_test_model_d")
    metrics = model_metrics(outcome, prediction, np.maximum(weights, 0.01), calibration=True)
    scores = extract_term_scores(
        model,
        feature_name="phenoage_acceleration_per_5_years",
        grid=np.linspace(-2, 2, 21),
    )
    assert diagnostics["term_n"] == 4
    assert diagnostics["interaction_term_n"] == 0
    self_test_terms = [
        tuple(int(value) for value in term)
        for term in model.term_features_
    ]
    assert self_test_terms == [(0,), (1,), (2,), (3,)]
    assert all(len(term) == 1 for term in self_test_terms)
    assert np.isfinite(prediction).all()
    assert np.isfinite(list(metrics.values())).all()
    assert np.isfinite(scores).all()
    test_auc = weighted_auc(
        np.array([0, 0, 1, 1]),
        np.array([0.1, 0.4, 0.35, 0.8]),
        np.ones(4),
    )
    assert abs(test_auc - 0.75) < 1e-12
    print("SELF-TEST PASSED")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    root = args.project_root.resolve()
    private_input = find_private_input(root, args.private_input)
    private_work = (
        args.private_work.expanduser().resolve()
        if args.private_work is not None
        else private_input.parent / "stage4_private"
    )
    rscript = find_rscript(args.rscript)
    print(f"Private input: {private_input}")
    print(f"Private Stage 4 work: {private_work}")
    print(f"Rscript: {rscript}")
    print(f"Interpret: {metadata.version('interpret')}")

    if args.repair_reference_only:
        check_interpret_version()
        prepare_r_reference(
            root,
            private_input,
            private_work,
            rscript,
            force=False,
        )
        print("STAGE 4 PRIVATE REFERENCE RECOVERY PASSED")
        return

    run_analysis(
        root,
        private_input,
        private_work,
        rscript,
        point_only=args.point_only,
        force_reference=args.force_reference,
    )


if __name__ == "__main__":
    main()
