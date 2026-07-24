NOTEBOOK_BUILD_R <- "AgeLens-V2-Stage3-20260724e"

args <- commandArgs(trailingOnly = TRUE)

weighted_mean <- function(x, w) {
  valid <- is.finite(x) & is.finite(w) & w > 0
  sum(x[valid] * w[valid]) / sum(w[valid])
}

weighted_auc <- function(y, score, w) {
  valid <- y %in% c(0, 1) & is.finite(score) & is.finite(w) & w > 0
  y <- y[valid]
  score <- score[valid]
  w <- w[valid]
  positive_total <- sum(w[y == 1])
  negative_total <- sum(w[y == 0])
  if (positive_total <= 0 || negative_total <= 0) {
    return(NA_real_)
  }
  ordering <- order(score, y)
  y <- y[ordering]
  score <- score[ordering]
  w <- w[ordering]
  groups <- split(seq_along(score), match(score, unique(score)))
  cumulative_negative <- 0
  concordance <- 0
  for (indices in groups) {
    positive_weight <- sum(w[indices][y[indices] == 1])
    negative_weight <- sum(w[indices][y[indices] == 0])
    concordance <- concordance + positive_weight * (
      cumulative_negative + 0.5 * negative_weight
    )
    cumulative_negative <- cumulative_negative + negative_weight
  }
  concordance / (positive_total * negative_total)
}

clip_probability <- function(value, epsilon = 1e-6) {
  pmin(pmax(value, epsilon), 1 - epsilon)
}

predict_response_numeric <- function(
  model,
  newdata,
  fit_label = "prediction_model"
) {
  prediction <- predict(
    model,
    newdata = newdata,
    type = "response",
    se.fit = FALSE
  )
  prediction <- as.numeric(prediction)

  if (length(prediction) != nrow(newdata)) {
    stop(
      fit_label,
      ": prediction length changed (",
      length(prediction),
      " versus ",
      nrow(newdata),
      ")."
    )
  }
  if (any(!is.finite(prediction))) {
    stop(
      fit_label,
      ": response predictions contain non-finite values."
    )
  }

  clip_probability(prediction)
}

prediction_core_metrics <- function(pooled) {
  required <- c(
    "y",
    "weight",
    "prediction_b",
    "prediction_c"
  )
  missing <- setdiff(required, names(pooled))
  if (length(missing) > 0) {
    stop(
      "Prediction metric input is missing columns: ",
      paste(missing, collapse = ", ")
    )
  }

  brier_b <- weighted_mean(
    (pooled$prediction_b - pooled$y)^2,
    pooled$weight
  )
  brier_c <- weighted_mean(
    (pooled$prediction_c - pooled$y)^2,
    pooled$weight
  )
  auc_b <- weighted_auc(
    pooled$y,
    pooled$prediction_b,
    pooled$weight
  )
  auc_c <- weighted_auc(
    pooled$y,
    pooled$prediction_c,
    pooled$weight
  )

  result <- c(
    brier_b = unname(brier_b),
    brier_c = unname(brier_c),
    brier_delta_c_minus_b = unname(brier_c - brier_b),
    auc_b = unname(auc_b),
    auc_c = unname(auc_c),
    auc_delta_c_minus_b = unname(auc_c - auc_b)
  )
  if (any(!is.finite(result))) {
    failed <- names(result)[!is.finite(result)]
    stop(
      "Core prediction metrics contain non-finite values: ",
      paste(failed, collapse = ", ")
    )
  }
  result
}

reconcile_prediction_metrics <- function(
  authoritative,
  stabilized,
  tolerance = 1e-7
) {
  expected <- c(
    "brier_b",
    "brier_c",
    "brier_delta_c_minus_b",
    "auc_b",
    "auc_c",
    "auc_delta_c_minus_b"
  )

  missing_authoritative <- setdiff(expected, names(authoritative))
  missing_stabilized <- setdiff(expected, names(stabilized))
  if (
    length(missing_authoritative) > 0 ||
      length(missing_stabilized) > 0
  ) {
    stop(
      "Prediction reconciliation metric names changed. ",
      "Missing authoritative: ",
      paste(missing_authoritative, collapse = ", "),
      "; missing stabilized: ",
      paste(missing_stabilized, collapse = ", "),
      "."
    )
  }

  authoritative_values <- as.numeric(authoritative[expected])
  stabilized_values <- as.numeric(stabilized[expected])
  difference <- abs(authoritative_values - stabilized_values)

  reconciliation <- data.frame(
    metric = expected,
    authoritative_svyglm = authoritative_values,
    stabilized_weighted_glm = stabilized_values,
    absolute_difference = difference,
    tolerance = tolerance,
    pass = is.finite(authoritative_values) &
      is.finite(stabilized_values) &
      is.finite(difference) &
      difference <= tolerance,
    stringsAsFactors = FALSE
  )

  if (!all(reconciliation$pass)) {
    failed <- reconciliation[!reconciliation$pass, , drop = FALSE]
    details <- apply(
      failed,
      1,
      function(row) {
        paste0(
          row[["metric"]],
          " [svyglm=", row[["authoritative_svyglm"]],
          ", weighted_glm=", row[["stabilized_weighted_glm"]],
          ", abs_diff=", row[["absolute_difference"]],
          "]"
        )
      }
    )
    stop(
      "Authoritative svyglm and stabilized weighted-GLM metrics ",
      "did not reconcile: ",
      paste(details, collapse = "; ")
    )
  }

  reconciliation
}

capture_fit <- function(expression) {
  captured <- character(0)
  fitted <- withCallingHandlers(
    expression,
    warning = function(condition) {
      captured <<- c(captured, conditionMessage(condition))
      invokeRestart("muffleWarning")
    }
  )
  list(model = fitted, warnings = unique(captured))
}

extract_regterm_p <- function(object) {
  for (candidate in c("p", "p.value", "pval")) {
    if (!is.null(object[[candidate]])) {
      value <- suppressWarnings(as.numeric(object[[candidate]]))
      if (length(value) > 0 && is.finite(value[[1]])) {
        return(value[[1]])
      }
    }
  }
  printed <- paste(capture.output(print(object)), collapse = " ")
  matched <- regexpr(
    "p[[:space:]]*=[[:space:]]*[-+0-9.eE]+",
    printed
  )
  if (matched[[1]] > 0) {
    value <- as.numeric(sub(".*=", "", regmatches(printed, matched)))
    if (is.finite(value)) {
      return(value)
    }
  }
  stop("Could not extract regTermTest p-value.")
}

calibration_metrics <- function(y, prediction, w) {
  valid <- y %in% c(0, 1) & is.finite(prediction) &
    is.finite(w) & w > 0
  y <- y[valid]
  prediction <- clip_probability(prediction[valid])
  w <- w[valid]

  if (
    length(y) == 0 ||
      length(unique(y)) != 2 ||
      sum(w) <= 0
  ) {
    stop("Calibration data do not contain weighted support for both outcomes.")
  }

  # Match svyglm's default numerical scaling: weights sum to sample size.
  calibration_weights <- w * length(w) / sum(w)
  calibration_data <- data.frame(
    y = y,
    linear_predictor = qlogis(prediction),
    .__calibration_weight__ = calibration_weights
  )
  control <- glm.control(epsilon = 1e-8, maxit = 100)

  intercept_fit <- suppressWarnings(
    glm(
      y ~ 1 + offset(linear_predictor),
      data = calibration_data,
      weights = .__calibration_weight__,
      family = quasibinomial(),
      control = control,
      na.action = na.fail
    )
  )
  slope_fit <- suppressWarnings(
    glm(
      y ~ linear_predictor,
      data = calibration_data,
      weights = .__calibration_weight__,
      family = quasibinomial(),
      control = control,
      na.action = na.fail
    )
  )

  if (
    !isTRUE(intercept_fit$converged) ||
      !isTRUE(slope_fit$converged) ||
      any(!is.finite(coef(intercept_fit))) ||
      any(!is.finite(coef(slope_fit)))
  ) {
    stop("Weighted calibration model failed to converge.")
  }

  intercept <- unname(coef(intercept_fit)[[1]])
  slope <- unname(coef(slope_fit)[["linear_predictor"]])
  c(intercept = intercept, slope = slope)
}

prediction_formulas <- function() {
  age_term <- paste0(
    "splines::ns(chronological_age_years, ",
    "knots=c(35,50,65), Boundary.knots=c(20,80), intercept=FALSE)"
  )
  list(
    model_b = as.formula(
      paste(
        "mobility_disability ~",
        age_term,
        "+ sex + race_ethnicity"
      )
    ),
    model_c = as.formula(
      paste(
        "mobility_disability ~",
        age_term,
        "+ sex + race_ethnicity",
        "+ phenoage_acceleration_per_5_years"
      )
    )
  )
}

fit_weighted_prediction_model <- function(
  formula,
  data,
  analysis_weights,
  start = NULL,
  fit_label = "prediction_model"
) {
  if (length(analysis_weights) != nrow(data)) {
    stop(fit_label, ": weights and data rows do not match.")
  }
  if (
    any(!is.finite(analysis_weights)) ||
      any(analysis_weights < 0) ||
      sum(analysis_weights) <= 0
  ) {
    stop(fit_label, ": prediction-model weights are invalid.")
  }

  # survey::svyglm(rescale=TRUE) rescales weights to sum to sample size.
  # Matching that convention improves numerical stability and preserves
  # coefficient estimates under constant weight rescaling.
  scaled_weights <- as.numeric(analysis_weights)
  scaled_weights <- scaled_weights * nrow(data) / sum(scaled_weights)

  model_data <- data
  model_data$.__analysis_weight__ <- scaled_weights

  design_matrix <- model.matrix(formula, data = model_data)
  positive_weight_rows <- scaled_weights > 0
  effective_matrix <- design_matrix[
    positive_weight_rows,
    ,
    drop = FALSE
  ]
  effective_qr <- qr(effective_matrix)
  if (effective_qr$rank < ncol(effective_matrix)) {
    aliased_columns <- colnames(effective_matrix)[
      effective_qr$pivot[
        seq.int(effective_qr$rank + 1, ncol(effective_matrix))
      ]
    ]
    stop(
      fit_label,
      ": positive-weight model matrix is rank deficient (",
      effective_qr$rank,
      "/",
      ncol(effective_matrix),
      "). Aliased columns: ",
      paste(aliased_columns, collapse = ", "),
      "."
    )
  }

  control_primary <- glm.control(epsilon = 1e-8, maxit = 100)
  control_retry <- glm.control(epsilon = 1e-8, maxit = 200)

  fit_once <- function(start_value, control_value) {
    captured <- character(0)
    fitted <- tryCatch(
      withCallingHandlers(
        glm(
          formula,
          data = model_data,
          weights = .__analysis_weight__,
          family = quasibinomial(),
          start = start_value,
          control = control_value,
          na.action = na.fail
        ),
        warning = function(condition) {
          captured <<- c(captured, conditionMessage(condition))
          invokeRestart("muffleWarning")
        }
      ),
      error = function(condition) condition
    )
    list(fitted = fitted, warnings = unique(captured))
  }

  first <- fit_once(start, control_primary)
  first_ok <- (
    inherits(first$fitted, "glm") &&
      isTRUE(first$fitted$converged) &&
      all(is.finite(coef(first$fitted)))
  )
  if (first_ok) {
    attr(first$fitted, "agelens_fit_warnings") <- first$warnings
    attr(first$fitted, "agelens_fit_attempt") <- "primary"
    return(first$fitted)
  }

  # Retry from an unweighted finite fit if the survey-point start was not
  # sufficient for an unusual bootstrap replicate.
  fallback_start <- start
  unweighted <- tryCatch(
    suppressWarnings(
      glm(
        formula,
        data = model_data,
        family = quasibinomial(),
        control = control_primary,
        na.action = na.fail
      )
    ),
    error = function(condition) NULL
  )
  if (
    inherits(unweighted, "glm") &&
      isTRUE(unweighted$converged) &&
      all(is.finite(coef(unweighted)))
  ) {
    fallback_start <- coef(unweighted)
  }

  second <- fit_once(fallback_start, control_retry)
  second_ok <- (
    inherits(second$fitted, "glm") &&
      isTRUE(second$fitted$converged) &&
      all(is.finite(coef(second$fitted)))
  )
  if (second_ok) {
    attr(second$fitted, "agelens_fit_warnings") <- unique(c(
      first$warnings,
      second$warnings
    ))
    attr(second$fitted, "agelens_fit_attempt") <- "retry"
    return(second$fitted)
  }

  fit_diagnostic <- function(object) {
    if (inherits(object, "condition")) {
      return(conditionMessage(object))
    }
    coefficients <- coef(object)
    nonfinite <- names(coefficients)[!is.finite(coefficients)]
    paste0(
      "converged=", isTRUE(object$converged),
      ", iter=", object$iter,
      ", rank=", object$rank,
      "/",
      length(coefficients),
      ", nonfinite=",
      if (length(nonfinite) == 0) {
        "none"
      } else {
        paste(nonfinite, collapse = "|")
      }
    )
  }

  first_message <- fit_diagnostic(first$fitted)
  second_message <- fit_diagnostic(second$fitted)

  stop(
    fit_label,
    ": weighted prediction model failed after stabilized retry. ",
    "Primary attempt: ", first_message, ". ",
    "Retry: ", second_message, ". ",
    "Weight sum=", signif(sum(scaled_weights), 8),
    ", positive-weight n=", sum(scaled_weights > 0),
    ", min positive weight=",
    signif(min(scaled_weights[scaled_weights > 0]), 8),
    ", max weight=", signif(max(scaled_weights), 8),
    "."
  )
}

prediction_theta <- function(
  weights,
  data,
  start_values = NULL
) {
  formulas <- prediction_formulas()
  directions <- list(
    train_2015_2016_test_2017_2018 = c("2015_2016", "2017_2018"),
    train_2017_2018_test_2015_2016 = c("2017_2018", "2015_2016")
  )
  pooled <- list()
  for (direction in names(directions)) {
    train_cycle <- directions[[direction]][[1]]
    test_cycle <- directions[[direction]][[2]]
    train <- data$NHANES_CYCLE == train_cycle
    test <- data$NHANES_CYCLE == test_cycle

    direction_starts <- if (is.null(start_values)) {
      list(model_b = NULL, model_c = NULL)
    } else {
      start_values[[direction]]
    }
    if (is.null(direction_starts)) {
      stop("Missing prediction start values for direction: ", direction)
    }

    model_b <- fit_weighted_prediction_model(
      formulas$model_b,
      data[train, , drop = FALSE],
      weights[train],
      start = direction_starts$model_b,
      fit_label = paste(direction, "model_b")
    )
    model_c <- fit_weighted_prediction_model(
      formulas$model_c,
      data[train, , drop = FALSE],
      weights[train],
      start = direction_starts$model_c,
      fit_label = paste(direction, "model_c")
    )
    pooled[[direction]] <- data.frame(
      y = data$mobility_disability[test],
      weight = weights[test],
      prediction_b = predict_response_numeric(
        model_b,
        data[test, , drop = FALSE],
        paste(direction, "model_b")
      ),
      prediction_c = predict_response_numeric(
        model_c,
        data[test, , drop = FALSE],
        paste(direction, "model_c")
      )
    )
  }
  pooled <- do.call(rbind, pooled)
  core_metrics <- prediction_core_metrics(pooled)
  calibration_b <- calibration_metrics(
    pooled$y,
    pooled$prediction_b,
    pooled$weight
  )
  calibration_c <- calibration_metrics(
    pooled$y,
    pooled$prediction_c,
    pooled$weight
  )
  result <- c(
    core_metrics,
    calibration_intercept_b = unname(calibration_b[["intercept"]]),
    calibration_intercept_c = unname(calibration_c[["intercept"]]),
    calibration_slope_b = unname(calibration_b[["slope"]]),
    calibration_slope_c = unname(calibration_c[["slope"]])
  )
  if (any(!is.finite(result))) {
    stop("Prediction statistic contains a non-finite value.")
  }
  result
}

if (length(args) == 1 && args[[1]] == "--self-test") {
  test_auc <- weighted_auc(
    c(0, 0, 1, 1),
    c(0.1, 0.4, 0.35, 0.8),
    rep(1, 4)
  )
  stopifnot(abs(test_auc - 0.75) < 1e-12)
  stopifnot(abs(weighted_mean(c(1, 3), c(1, 1)) - 2) < 1e-12)

  set.seed(20260724)
  test_race_levels <- c(
    "Non-Hispanic White",
    "Mexican American",
    "Other Hispanic",
    "Non-Hispanic Black",
    "Non-Hispanic Asian",
    "Other or multiracial"
  )

  # A complete age x sex x race grid within each cycle prevents the
  # accidental sex/race aliasing that occurred in the previous self-test.
  cycle_grid <- expand.grid(
    age_index = seq_len(15),
    sex = c("Male", "Female"),
    race_ethnicity = test_race_levels,
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  stopifnot(nrow(cycle_grid) == 180)

  test_data <- rbind(
    transform(cycle_grid, NHANES_CYCLE = "2015_2016"),
    transform(cycle_grid, NHANES_CYCLE = "2017_2018")
  )
  test_n <- nrow(test_data)

  test_data$chronological_age_years <- seq(
    22,
    78,
    length.out = 15
  )[test_data$age_index]
  test_data$sex <- factor(
    test_data$sex,
    levels = c("Male", "Female")
  )
  test_data$race_ethnicity <- factor(
    test_data$race_ethnicity,
    levels = test_race_levels
  )
  test_data$NHANES_CYCLE <- factor(
    test_data$NHANES_CYCLE,
    levels = c("2015_2016", "2017_2018")
  )

  # Independent, reproducible acceleration values avoid deterministic
  # dependence on age, sex, or race.
  test_data$phenoage_acceleration_per_5_years <- rnorm(
    test_n,
    mean = 0,
    sd = 1.15
  )
  race_effect <- c(
    "Non-Hispanic White" = 0,
    "Mexican American" = 0.08,
    "Other Hispanic" = 0.12,
    "Non-Hispanic Black" = 0.22,
    "Non-Hispanic Asian" = -0.08,
    "Other or multiracial" = 0.15
  )
  test_linear_predictor <- (
    -2.25 +
      0.035 * (test_data$chronological_age_years - 50) +
      0.18 * (test_data$sex == "Female") +
      unname(race_effect[as.character(test_data$race_ethnicity)]) +
      0.22 * test_data$phenoage_acceleration_per_5_years
  )
  test_data$mobility_disability <- rbinom(
    test_n,
    size = 1,
    prob = plogis(test_linear_predictor)
  )

  # Deterministically retain both outcome classes within both cycles.
  for (cycle in levels(test_data$NHANES_CYCLE)) {
    selected <- which(test_data$NHANES_CYCLE == cycle)
    test_data$mobility_disability[selected[[1]]] <- 0
    test_data$mobility_disability[selected[[2]]] <- 1
  }
  test_data$age_index <- NULL

  test_weights_raw <- exp(
    seq(log(1e5), log(9e6), length.out = test_n)
  )

  formulas <- prediction_formulas()
  for (cycle in levels(test_data$NHANES_CYCLE)) {
    selected <- test_data$NHANES_CYCLE == cycle
    for (model_name in names(formulas)) {
      matrix <- model.matrix(
        formulas[[model_name]],
        data = test_data[selected, , drop = FALSE]
      )
      stopifnot(qr(matrix)$rank == ncol(matrix))
    }
  }

  test_theta_raw <- prediction_theta(
    test_weights_raw,
    test_data
  )
  test_theta_scaled <- prediction_theta(
    test_weights_raw / mean(test_weights_raw),
    test_data
  )
  stopifnot(
    all(is.finite(test_theta_raw)),
    all(is.finite(test_theta_scaled)),
    max(abs(test_theta_raw - test_theta_scaled)) < 1e-10
  )

  test_model <- fit_weighted_prediction_model(
    mobility_disability ~ chronological_age_years +
      sex + race_ethnicity +
      phenoage_acceleration_per_5_years,
    test_data,
    test_weights_raw,
    fit_label = "self_test_weight_scaling"
  )
  stopifnot(
    isTRUE(test_model$converged),
    all(is.finite(coef(test_model))),
    test_model$rank == length(coef(test_model)),
    abs(sum(weights(test_model, type = "prior")) - test_n) < 1e-8
  )

  if (!requireNamespace("survey", quietly = TRUE)) {
    stop("The survey package is required for the Stage 3 self-test.")
  }

  test_directions <- list(
    train_2015_2016_test_2017_2018 = c("2015_2016", "2017_2018"),
    train_2017_2018_test_2015_2016 = c("2017_2018", "2015_2016")
  )
  test_point_predictions <- list()
  test_start_values <- list()

  for (direction in names(test_directions)) {
    train_cycle <- test_directions[[direction]][[1]]
    test_cycle <- test_directions[[direction]][[2]]
    train <- test_data$NHANES_CYCLE == train_cycle
    test <- test_data$NHANES_CYCLE == test_cycle

    train_frame <- test_data[train, , drop = FALSE]
    train_frame$.__test_weight__ <- test_weights_raw[train]
    test_design <- survey::svydesign(
      ids = ~1,
      weights = ~.__test_weight__,
      data = train_frame
    )
    test_model_b_svy <- survey::svyglm(
      formulas$model_b,
      design = test_design,
      family = quasibinomial(link = "logit")
    )
    test_model_c_svy <- survey::svyglm(
      formulas$model_c,
      design = test_design,
      family = quasibinomial(link = "logit")
    )
    stopifnot(
      isTRUE(test_model_b_svy$converged),
      isTRUE(test_model_c_svy$converged),
      all(is.finite(coef(test_model_b_svy))),
      all(is.finite(coef(test_model_c_svy)))
    )

    test_start_values[[direction]] <- list(
      model_b = coef(test_model_b_svy),
      model_c = coef(test_model_c_svy)
    )
    test_point_predictions[[direction]] <- data.frame(
      y = test_data$mobility_disability[test],
      weight = test_weights_raw[test],
      prediction_b = predict_response_numeric(
        test_model_b_svy,
        test_data[test, , drop = FALSE],
        paste(direction, "self_test_svyglm_model_b")
      ),
      prediction_c = predict_response_numeric(
        test_model_c_svy,
        test_data[test, , drop = FALSE],
        paste(direction, "self_test_svyglm_model_c")
      )
    )
  }

  test_authoritative <- prediction_core_metrics(
    do.call(rbind, test_point_predictions)
  )
  test_stabilized <- prediction_theta(
    test_weights_raw,
    test_data,
    test_start_values
  )
  test_reconciliation <- reconcile_prediction_metrics(
    test_authoritative,
    test_stabilized,
    tolerance = 1e-7
  )
  stopifnot(all(test_reconciliation$pass))

  cat("SELF-TEST PASSED\n")
  quit(status = 0)
}

if (length(args) != 3) {
  stop("Expected 3 arguments: private input CSV, output table directory, figure directory.")
}

input_path <- normalizePath(args[[1]], mustWork = TRUE)
output_dir <- normalizePath(args[[2]], mustWork = FALSE)
figure_dir <- normalizePath(args[[3]], mustWork = FALSE)
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(figure_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("survey", quietly = TRUE)) {
  stop("Missing R package 'survey'.")
}

suppressPackageStartupMessages({
  library(survey)
  library(splines)
})
options(survey.lonely.psu = "fail")

raw <- read.csv(
  input_path,
  stringsAsFactors = FALSE,
  check.names = FALSE,
  na.strings = c("", "NA")
)
required <- c(
  "SEQN", "NHANES_CYCLE", "chronological_age_years", "WTSAF4YR",
  "SDMVSTRA", "SDMVPSU", "pooled_stratum", "pooled_psu", "sex",
  "race_ethnicity", "phenoage_acceleration_per_5_years",
  "mobility_disability", "domain_mobility_disability"
)
missing_columns <- setdiff(required, names(raw))
if (length(missing_columns) > 0) {
  stop("Missing input columns: ", paste(missing_columns, collapse = ", "))
}
if (nrow(raw) != 5223) {
  stop("Private input must contain 5,223 canonical rows.")
}

numeric_columns <- c(
  "chronological_age_years", "WTSAF4YR", "SDMVSTRA", "SDMVPSU",
  "phenoage_acceleration_per_5_years", "mobility_disability",
  "domain_mobility_disability"
)
for (column in numeric_columns) {
  raw[[column]] <- suppressWarnings(as.numeric(raw[[column]]))
}

raw$sex <- factor(raw$sex, levels = c("Male", "Female"))
raw$race_ethnicity <- factor(
  raw$race_ethnicity,
  levels = c(
    "Non-Hispanic White", "Mexican American", "Other Hispanic",
    "Non-Hispanic Black", "Non-Hispanic Asian", "Other or multiracial"
  )
)
raw$NHANES_CYCLE <- factor(
  raw$NHANES_CYCLE,
  levels = c("2015_2016", "2017_2018")
)
raw$age_group <- cut(
  raw$chronological_age_years,
  breaks = c(20, 50, 65, Inf),
  right = FALSE,
  labels = c("20-49", "50-64", "65+")
)
raw$pooled_stratum <- factor(raw$pooled_stratum)
raw$pooled_psu <- factor(raw$pooled_psu)

primary <- raw[
  raw$domain_mobility_disability == 1,
  ,
  drop = FALSE
]
if (nrow(primary) != 4366) {
  stop("Primary domain count changed.")
}
if (sum(primary$mobility_disability) != 682) {
  stop("Primary positive count changed.")
}
if (anyNA(primary[c(
  "chronological_age_years", "WTSAF4YR", "sex", "race_ethnicity",
  "NHANES_CYCLE", "age_group", "phenoage_acceleration_per_5_years"
)])) {
  stop("Primary analysis variables contain missing values.")
}

full_design <- svydesign(
  ids = ~pooled_psu,
  strata = ~pooled_stratum,
  weights = ~WTSAF4YR,
  nest = TRUE,
  data = primary
)
design_df <- degf(full_design)
if (design_df != 30) {
  stop("Primary design degrees of freedom changed: ", design_df)
}

age_term <- paste0(
  "splines::ns(chronological_age_years, ",
  "knots=c(35,50,65), Boundary.knots=c(20,80), intercept=FALSE)"
)
base_terms <- paste(
  age_term,
  "+ sex + race_ethnicity + NHANES_CYCLE",
  "+ phenoage_acceleration_per_5_years"
)

dimension_specs <- list(
  sex = list(variable = "sex", levels = levels(primary$sex)),
  age_group = list(variable = "age_group", levels = levels(primary$age_group)),
  race_ethnicity = list(
    variable = "race_ethnicity",
    levels = levels(primary$race_ethnicity)
  ),
  NHANES_cycle = list(
    variable = "NHANES_CYCLE",
    levels = levels(primary$NHANES_CYCLE)
  )
)

support_for_level <- function(variable, level) {
  selected <- primary[[variable]] == level
  subset <- primary[selected, , drop = FALSE]
  data.frame(
    n = nrow(subset),
    positive_n = sum(subset$mobility_disability),
    negative_n = nrow(subset) - sum(subset$mobility_disability),
    weighted_prevalence_percent = 100 * weighted_mean(
      subset$mobility_disability,
      subset$WTSAF4YR
    ),
    represented_strata = nrow(unique(subset[c("NHANES_CYCLE", "SDMVSTRA")])),
    represented_psus = nrow(unique(subset[c(
      "NHANES_CYCLE", "SDMVSTRA", "SDMVPSU"
    )]))
  )
}

contrast_for_level <- function(model, variable, level) {
  age_value <- if (variable == "age_group") {
    c("20-49" = 35, "50-64" = 57, "65+" = 70)[[level]]
  } else {
    50
  }
  template <- data.frame(
    chronological_age_years = age_value,
    sex = factor("Male", levels = levels(primary$sex)),
    race_ethnicity = factor(
      "Non-Hispanic White",
      levels = levels(primary$race_ethnicity)
    ),
    NHANES_CYCLE = factor(
      "2015_2016",
      levels = levels(primary$NHANES_CYCLE)
    ),
    age_group = factor("50-64", levels = levels(primary$age_group)),
    phenoage_acceleration_per_5_years = 0
  )
  template[[variable]] <- factor(
    level,
    levels = levels(primary[[variable]])
  )
  first <- template
  second <- template
  second$phenoage_acceleration_per_5_years <- 1
  terms_object <- delete.response(terms(model))
  matrix_first <- model.matrix(
    terms_object,
    data = first,
    contrasts.arg = model$contrasts,
    xlev = model$xlevels
  )
  matrix_second <- model.matrix(
    terms_object,
    data = second,
    contrasts.arg = model$contrasts,
    xlev = model$xlevels
  )
  coefficients <- coef(model)
  matrix_first <- matrix_first[, names(coefficients), drop = FALSE]
  matrix_second <- matrix_second[, names(coefficients), drop = FALSE]
  contrast <- as.numeric(matrix_second - matrix_first)
  estimate <- sum(contrast * coefficients)
  standard_error <- sqrt(
    as.numeric(t(contrast) %*% vcov(model) %*% contrast)
  )
  critical <- qt(0.975, df = design_df)
  statistic <- estimate / standard_error
  data.frame(
    log_prevalence_ratio = estimate,
    standard_error = standard_error,
    prevalence_ratio = exp(estimate),
    ci_low_95 = exp(estimate - critical * standard_error),
    ci_high_95 = exp(estimate + critical * standard_error),
    p_value_descriptive = 2 * pt(
      abs(statistic),
      df = design_df,
      lower.tail = FALSE
    )
  )
}

global_rows <- list()
level_rows <- list()
diagnostic_rows <- list()

for (dimension in names(dimension_specs)) {
  spec <- dimension_specs[[dimension]]
  variable <- spec$variable
  extra_main <- if (variable == "age_group") "+ age_group" else ""
  interaction <- paste0(
    "phenoage_acceleration_per_5_years:",
    variable
  )
  formula <- as.formula(
    paste(
      "mobility_disability ~",
      base_terms,
      extra_main,
      "+",
      interaction
    )
  )
  fitted <- capture_fit(
    svyglm(
      formula,
      design = full_design,
      family = quasipoisson(link = "log")
    )
  )
  model <- fitted$model
  test <- regTermTest(
    model,
    as.formula(paste("~", interaction)),
    method = "Wald"
  )
  global_rows[[dimension]] <- data.frame(
    dimension = dimension,
    interaction_df = length(spec$levels) - 1,
    design_df = design_df,
    p_value_raw = extract_regterm_p(test),
    warning_n = length(fitted$warnings),
    warnings = paste(fitted$warnings, collapse = " | "),
    converged = isTRUE(model$converged),
    finite_coefficients = all(is.finite(coef(model))),
    finite_covariance = all(is.finite(vcov(model))),
    stringsAsFactors = FALSE
  )
  for (level in spec$levels) {
    support <- support_for_level(variable, level)
    effect <- contrast_for_level(model, variable, level)
    level_rows[[paste(dimension, level, sep = "__")]] <- cbind(
      data.frame(
        dimension = dimension,
        level = level,
        stringsAsFactors = FALSE
      ),
      support,
      effect
    )
  }
  predictions <- as.numeric(predict(model, type = "response"))
  diagnostic_rows[[dimension]] <- data.frame(
    dimension = dimension,
    coefficient_n = length(coef(model)),
    predicted_min = min(predictions),
    predicted_max = max(predictions),
    predicted_above_one_n = sum(predictions > 1),
    warning_n = length(fitted$warnings),
    stringsAsFactors = FALSE
  )
}

global_tests <- do.call(rbind, global_rows)
global_tests$q_value_bh <- p.adjust(
  global_tests$p_value_raw,
  method = "BH"
)
global_tests$supported_at_q_0_10 <- global_tests$q_value_bh < 0.10

level_estimates <- do.call(rbind, level_rows)
level_estimates <- merge(
  level_estimates,
  global_tests[c("dimension", "q_value_bh", "supported_at_q_0_10")],
  by = "dimension",
  all.x = TRUE,
  sort = FALSE
)
level_estimates$reporting_role <- ifelse(
  level_estimates$supported_at_q_0_10,
  "supported_interaction_level_estimate",
  "descriptive_level_estimate"
)
interaction_diagnostics <- do.call(rbind, diagnostic_rows)

# Point-estimate cross-cycle predictions with authoritative svyglm fits.
formulas <- prediction_formulas()
directions <- list(
  train_2015_2016_test_2017_2018 = c("2015_2016", "2017_2018"),
  train_2017_2018_test_2015_2016 = c("2017_2018", "2015_2016")
)
direction_rows <- list()
point_predictions <- list()
prediction_diagnostics <- list()
prediction_start_values <- list()

for (direction in names(directions)) {
  train_cycle <- directions[[direction]][[1]]
  test_cycle <- directions[[direction]][[2]]
  train_data <- primary[primary$NHANES_CYCLE == train_cycle, , drop = FALSE]
  test_data <- primary[primary$NHANES_CYCLE == test_cycle, , drop = FALSE]
  train_design <- svydesign(
    ids = ~SDMVPSU,
    strata = ~SDMVSTRA,
    weights = ~WTSAF4YR,
    nest = TRUE,
    data = train_data
  )
  model_b_fit <- capture_fit(
    svyglm(
      formulas$model_b,
      design = train_design,
      family = quasibinomial(link = "logit")
    )
  )
  model_c_fit <- capture_fit(
    svyglm(
      formulas$model_c,
      design = train_design,
      family = quasibinomial(link = "logit")
    )
  )
  if (
    !isTRUE(model_b_fit$model$converged) ||
      !isTRUE(model_c_fit$model$converged) ||
      any(!is.finite(coef(model_b_fit$model))) ||
      any(!is.finite(coef(model_c_fit$model)))
  ) {
    stop("Authoritative svyglm point prediction model failed: ", direction)
  }
  prediction_start_values[[direction]] <- list(
    model_b = coef(model_b_fit$model),
    model_c = coef(model_c_fit$model)
  )
  prediction_b <- predict_response_numeric(
    model_b_fit$model,
    test_data,
    paste(direction, "authoritative_svyglm_model_b")
  )
  prediction_c <- predict_response_numeric(
    model_c_fit$model,
    test_data,
    paste(direction, "authoritative_svyglm_model_c")
  )
  y <- test_data$mobility_disability
  w <- test_data$WTSAF4YR
  brier_b <- weighted_mean((prediction_b - y)^2, w)
  brier_c <- weighted_mean((prediction_c - y)^2, w)
  auc_b <- weighted_auc(y, prediction_b, w)
  auc_c <- weighted_auc(y, prediction_c, w)
  calibration_b <- calibration_metrics(y, prediction_b, w)
  calibration_c <- calibration_metrics(y, prediction_c, w)
  direction_rows[[direction]] <- data.frame(
    direction = direction,
    train_cycle = train_cycle,
    test_cycle = test_cycle,
    train_n = nrow(train_data),
    test_n = nrow(test_data),
    test_positive_n = sum(y),
    test_weighted_prevalence_percent = 100 * weighted_mean(y, w),
    brier_b = brier_b,
    brier_c = brier_c,
    brier_delta_c_minus_b = brier_c - brier_b,
    auc_b = auc_b,
    auc_c = auc_c,
    auc_delta_c_minus_b = auc_c - auc_b,
    calibration_intercept_b = calibration_b[["intercept"]],
    calibration_intercept_c = calibration_c[["intercept"]],
    calibration_slope_b = calibration_b[["slope"]],
    calibration_slope_c = calibration_c[["slope"]],
    stringsAsFactors = FALSE
  )
  point_predictions[[direction]] <- data.frame(
    y = y,
    weight = w,
    prediction_b = prediction_b,
    prediction_c = prediction_c
  )
  prediction_diagnostics[[direction]] <- data.frame(
    direction = direction,
    model = c("model_b", "model_c"),
    converged = c(
      isTRUE(model_b_fit$model$converged),
      isTRUE(model_c_fit$model$converged)
    ),
    finite_coefficients = c(
      all(is.finite(coef(model_b_fit$model))),
      all(is.finite(coef(model_c_fit$model)))
    ),
    warning_n = c(
      length(model_b_fit$warnings),
      length(model_c_fit$warnings)
    ),
    warnings = c(
      paste(model_b_fit$warnings, collapse = " | "),
      paste(model_c_fit$warnings, collapse = " | ")
    ),
    stringsAsFactors = FALSE
  )
}

direction_metrics <- do.call(rbind, direction_rows)
prediction_model_diagnostics <- do.call(rbind, prediction_diagnostics)
pooled_point <- do.call(rbind, point_predictions)
point_from_svyglm <- prediction_core_metrics(pooled_point)

# Survey bootstrap. Every replicate refits both models in both directions.
set.seed(20260723)
replicate_design <- as.svrepdesign(
  full_design,
  type = "bootstrap",
  replicates = 500,
  mse = TRUE
)
replicate_weights <- weights(replicate_design, type = "analysis")
sampling_weights <- weights(full_design)
point_theta <- prediction_theta(
  sampling_weights,
  primary,
  prediction_start_values
)

point_reconciliation <- reconcile_prediction_metrics(
  authoritative = point_from_svyglm,
  stabilized = point_theta,
  tolerance = 1e-7
)

replicate_estimates <- matrix(
  NA_real_,
  nrow = ncol(replicate_weights),
  ncol = length(point_theta),
  dimnames = list(NULL, names(point_theta))
)
failed_replicates <- integer(0)
cat("\nStarting 500-replicate stratified PSU bootstrap.\n")
for (index in seq_len(ncol(replicate_weights))) {
  estimate <- tryCatch(
    prediction_theta(
      replicate_weights[, index],
      primary,
      prediction_start_values
    ),
    error = function(condition) {
      failed_replicates <<- c(failed_replicates, index)
      rep(NA_real_, length(point_theta))
    }
  )
  replicate_estimates[index, ] <- estimate
  if (index %% 25 == 0 || index == ncol(replicate_weights)) {
    cat(sprintf("Bootstrap progress: %d/%d\n", index, ncol(replicate_weights)))
    flush.console()
  }
}
if (length(failed_replicates) > 0) {
  stop(
    "Bootstrap replicate failures: ",
    paste(failed_replicates, collapse = ", ")
  )
}

variance <- svrVar(
  replicate_estimates,
  scale = replicate_design$scale,
  rscales = replicate_design$rscales,
  mse = replicate_design$mse,
  coef = point_theta
)
standard_errors <- sqrt(diag(variance))
critical <- qt(0.975, df = design_df)
bootstrap_summary <- data.frame(
  metric = names(point_theta),
  estimate = as.numeric(point_theta),
  standard_error = as.numeric(standard_errors),
  ci_low_95 = as.numeric(point_theta - critical * standard_errors),
  ci_high_95 = as.numeric(point_theta + critical * standard_errors),
  design_df = design_df,
  replicate_n = nrow(replicate_estimates),
  failed_replicate_n = length(failed_replicates),
  stringsAsFactors = FALSE
)

metric_row <- function(metric) {
  bootstrap_summary[bootstrap_summary$metric == metric, , drop = FALSE]
}
brier_delta <- metric_row("brier_delta_c_minus_b")
auc_delta <- metric_row("auc_delta_c_minus_b")
calibration_intercept_c <- metric_row("calibration_intercept_c")
calibration_slope_c <- metric_row("calibration_slope_c")

brier_support <- brier_delta$ci_high_95 < 0
auc_nonworse <- auc_delta$estimate >= 0
calibration_intercept_ok <- (
  calibration_intercept_c$ci_low_95 <= 0 &
    calibration_intercept_c$ci_high_95 >= 0
)
calibration_slope_ok <- (
  calibration_slope_c$ci_low_95 <= 1 &
    calibration_slope_c$ci_high_95 >= 1
)
positive_claim <- (
  brier_support & auc_nonworse &
    calibration_intercept_ok & calibration_slope_ok
)

incremental_decision <- data.frame(
  brier_delta_estimate = brier_delta$estimate,
  brier_delta_ci_low_95 = brier_delta$ci_low_95,
  brier_delta_ci_high_95 = brier_delta$ci_high_95,
  brier_improvement_supported = brier_support,
  auc_delta_estimate = auc_delta$estimate,
  auc_directionally_nonworse = auc_nonworse,
  model_c_calibration_intercept = calibration_intercept_c$estimate,
  model_c_calibration_intercept_ci_contains_zero = calibration_intercept_ok,
  model_c_calibration_slope = calibration_slope_c$estimate,
  model_c_calibration_slope_ci_contains_one = calibration_slope_ok,
  positive_incremental_utility_claim = positive_claim,
  result_status = "provisional_pending_stage3_review",
  stringsAsFactors = FALSE
)

runtime_versions <- data.frame(
  component = c("R", "survey", "splines", "platform", "script_build"),
  version = c(
    R.version.string,
    as.character(packageVersion("survey")),
    as.character(packageVersion("splines")),
    R.version$platform,
    NOTEBOOK_BUILD_R
  ),
  stringsAsFactors = FALSE
)

release_checks <- data.frame(
  check = c(
    "Primary domain n equals 4,366",
    "Primary positive n equals 682",
    "All four interaction models converged",
    "All interaction coefficients and covariance matrices are finite",
    "All global interaction p-values and BH q-values are valid",
    "Every prespecified transportability level is present",
    "Both cross-cycle directions are present",
    "All prediction models converged with finite coefficients",
    "Bootstrap replicate count equals 500",
    "No bootstrap replicate failed",
    "All bootstrap estimates and intervals are finite",
    "Brier and AUC point estimates are within valid ranges",
    "No participant-level public output was written",
    "V1 remains unmodified",
    "Explainable modeling remains unauthorized"
  ),
  pass = c(
    nrow(primary) == 4366,
    sum(primary$mobility_disability) == 682,
    all(global_tests$converged),
    all(global_tests$finite_coefficients) & all(global_tests$finite_covariance),
    all(is.finite(global_tests$p_value_raw)) &
      all(global_tests$p_value_raw >= 0 & global_tests$p_value_raw <= 1) &
      all(is.finite(global_tests$q_value_bh)) &
      all(global_tests$q_value_bh >= 0 & global_tests$q_value_bh <= 1),
    nrow(level_estimates) == 13,
    nrow(direction_metrics) == 2,
    all(prediction_model_diagnostics$converged) &
      all(prediction_model_diagnostics$finite_coefficients),
    nrow(replicate_estimates) == 500,
    length(failed_replicates) == 0,
    all(is.finite(bootstrap_summary$estimate)) &
      all(is.finite(bootstrap_summary$standard_error)) &
      all(is.finite(bootstrap_summary$ci_low_95)) &
      all(is.finite(bootstrap_summary$ci_high_95)),
    all(bootstrap_summary$estimate[bootstrap_summary$metric %in% c(
      "brier_b", "brier_c", "auc_b", "auc_c"
    )] >= 0) &
      all(bootstrap_summary$estimate[bootstrap_summary$metric %in% c(
        "brier_b", "brier_c", "auc_b", "auc_c"
      )] <= 1),
    TRUE,
    TRUE,
    TRUE
  ),
  observed = c(
    nrow(primary),
    sum(primary$mobility_disability),
    all(global_tests$converged),
    all(global_tests$finite_coefficients) & all(global_tests$finite_covariance),
    paste(global_tests$p_value_raw, global_tests$q_value_bh, sep = "/", collapse = " | "),
    nrow(level_estimates),
    nrow(direction_metrics),
    all(prediction_model_diagnostics$converged) &
      all(prediction_model_diagnostics$finite_coefficients),
    nrow(replicate_estimates),
    length(failed_replicates),
    all(is.finite(as.matrix(bootstrap_summary[c(
      "estimate", "standard_error", "ci_low_95", "ci_high_95"
    )]))),
    paste(
      bootstrap_summary$metric[bootstrap_summary$metric %in% c(
        "brier_b", "brier_c", "auc_b", "auc_c"
      )],
      bootstrap_summary$estimate[bootstrap_summary$metric %in% c(
        "brier_b", "brier_c", "auc_b", "auc_c"
      )],
      collapse = " | "
    ),
    "aggregate tables and figures only",
    "no V1 write operation",
    "not authorized"
  ),
  stringsAsFactors = FALSE
)
if (!all(release_checks$pass)) {
  stop(
    "Stage 3 release checks failed: ",
    paste(release_checks$check[!release_checks$pass], collapse = "; ")
  )
}

write.csv(
  global_tests,
  file.path(output_dir, "13_stage3_transportability_global_tests.csv"),
  row.names = FALSE
)
write.csv(
  level_estimates,
  file.path(output_dir, "13_stage3_transportability_level_estimates.csv"),
  row.names = FALSE
)
write.csv(
  interaction_diagnostics,
  file.path(output_dir, "13_stage3_transportability_diagnostics.csv"),
  row.names = FALSE
)
write.csv(
  direction_metrics,
  file.path(output_dir, "13_stage3_prediction_direction_metrics.csv"),
  row.names = FALSE
)
write.csv(
  point_reconciliation,
  file.path(output_dir, "13_stage3_point_prediction_reconciliation.csv"),
  row.names = FALSE
)
write.csv(
  bootstrap_summary,
  file.path(output_dir, "13_stage3_prediction_bootstrap_summary.csv"),
  row.names = FALSE
)
write.csv(
  incremental_decision,
  file.path(output_dir, "13_stage3_incremental_utility_decision.csv"),
  row.names = FALSE
)
write.csv(
  prediction_model_diagnostics,
  file.path(output_dir, "13_stage3_prediction_model_diagnostics.csv"),
  row.names = FALSE
)
write.csv(
  runtime_versions,
  file.path(output_dir, "13_stage3_runtime_versions.csv"),
  row.names = FALSE
)
write.csv(
  release_checks,
  file.path(output_dir, "13_stage3_release_checks.csv"),
  row.names = FALSE
)

# Transportability forest plot.
plot_levels <- level_estimates
plot_levels$display <- paste(plot_levels$dimension, plot_levels$level, sep = ": ")
plot_levels <- plot_levels[order(plot_levels$dimension, plot_levels$prevalence_ratio), ]
forest_path <- file.path(figure_dir, "13_stage3_transportability_forest.png")
png(forest_path, width = 1900, height = 1500, res = 200)
par(mar = c(5, 15, 4, 2))
y <- seq_len(nrow(plot_levels))
limits <- range(plot_levels$ci_low_95, plot_levels$ci_high_95)
plot(
  plot_levels$prevalence_ratio,
  y,
  xlim = limits,
  ylim = c(0.5, nrow(plot_levels) + 0.5),
  yaxt = "n",
  ylab = "",
  xlab = "Prevalence ratio per 5-year higher acceleration",
  main = "AgeLens V2 Stage 3: transportability estimates",
  pch = 19
)
segments(
  plot_levels$ci_low_95,
  y,
  plot_levels$ci_high_95,
  y
)
abline(v = 1, lty = 2)
axis(2, at = y, labels = plot_levels$display, las = 1, cex.axis = 0.7)
mtext(
  "Level-specific estimates; global interaction tests use BH q=0.10",
  side = 3,
  line = 0.3,
  cex = 0.8
)
dev.off()

# Incremental-performance plot.
performance_path <- file.path(figure_dir, "13_stage3_incremental_performance.png")
plot_metrics <- bootstrap_summary[
  bootstrap_summary$metric %in% c(
    "brier_delta_c_minus_b", "auc_delta_c_minus_b"
  ),
]
plot_metrics$label <- c(
  "Brier delta (C-B; lower is better)",
  "AUC delta (C-B; higher is better)"
)[match(
  plot_metrics$metric,
  c("brier_delta_c_minus_b", "auc_delta_c_minus_b")
)]
png(performance_path, width = 1700, height = 900, res = 200)
par(mar = c(5, 12, 4, 2))
y <- seq_len(nrow(plot_metrics))
limits <- range(plot_metrics$ci_low_95, plot_metrics$ci_high_95, 0)
plot(
  plot_metrics$estimate,
  y,
  xlim = limits,
  ylim = c(0.5, nrow(plot_metrics) + 0.5),
  yaxt = "n",
  ylab = "",
  xlab = "Model C minus Model B",
  main = "AgeLens V2 Stage 3: pooled out-of-cycle performance",
  pch = 19
)
segments(
  plot_metrics$ci_low_95,
  y,
  plot_metrics$ci_high_95,
  y
)
abline(v = 0, lty = 2)
axis(2, at = y, labels = plot_metrics$label, las = 1, cex.axis = 0.8)
mtext(
  "500 stratified-PSU bootstrap replicates; both cycles refit each replicate",
  side = 3,
  line = 0.3,
  cex = 0.8
)
dev.off()

cat("\nAgeLens V2 Stage 3 completed.\n")
cat("Transportability global tests (raw p / BH q):\n")
for (index in seq_len(nrow(global_tests))) {
  cat(sprintf(
    "- %s: p=%.8g, q=%.8g\n",
    global_tests$dimension[[index]],
    global_tests$p_value_raw[[index]],
    global_tests$q_value_bh[[index]]
  ))
}
cat(sprintf(
  "Pooled Brier delta C-B: %.8g (95%% CI %.8g to %.8g)\n",
  brier_delta$estimate,
  brier_delta$ci_low_95,
  brier_delta$ci_high_95
))
cat(sprintf(
  "Pooled AUC delta C-B: %.8g (95%% CI %.8g to %.8g)\n",
  auc_delta$estimate,
  auc_delta$ci_low_95,
  auc_delta$ci_high_95
))
cat(sprintf(
  "Positive incremental-utility claim: %s\n",
  ifelse(positive_claim, "YES", "NO")
))
cat("Result status: provisional pending Stage 3 review.\n")
