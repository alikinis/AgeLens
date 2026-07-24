STAGE4_R_BUILD <- "AgeLens-V2-Stage4-R-20260724b"

args <- commandArgs(trailingOnly = TRUE)

weighted_mean <- function(x, w) {
  valid <- is.finite(x) & is.finite(w) & w > 0
  if (!any(valid) || sum(w[valid]) <= 0) {
    stop("Weighted mean has no positive finite support.")
  }
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
    stop("Weighted AUC lacks support for both outcome classes.")
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
  pmin(pmax(as.numeric(value), epsilon), 1 - epsilon)
}

calibration_metrics <- function(y, prediction, w) {
  valid <- y %in% c(0, 1) & is.finite(prediction) & is.finite(w) & w > 0
  y <- y[valid]
  prediction <- clip_probability(prediction[valid])
  w <- w[valid]
  if (length(unique(y)) != 2 || sum(w) <= 0) {
    stop("Calibration data lack both outcome classes.")
  }
  scaled <- w * length(w) / sum(w)
  frame <- data.frame(
    y = y,
    linear_predictor = qlogis(prediction),
    .weight = scaled
  )
  control <- glm.control(epsilon = 1e-8, maxit = 100)
  intercept_fit <- suppressWarnings(glm(
    y ~ 1 + offset(linear_predictor),
    data = frame,
    weights = .weight,
    family = quasibinomial(),
    control = control,
    na.action = na.fail
  ))
  slope_fit <- suppressWarnings(glm(
    y ~ linear_predictor,
    data = frame,
    weights = .weight,
    family = quasibinomial(),
    control = control,
    na.action = na.fail
  ))
  if (
    !isTRUE(intercept_fit$converged) || !isTRUE(slope_fit$converged) ||
      any(!is.finite(coef(intercept_fit))) ||
      any(!is.finite(coef(slope_fit)))
  ) {
    stop("Calibration model failed.")
  }
  c(
    intercept = unname(coef(intercept_fit)[[1]]),
    slope = unname(coef(slope_fit)[["linear_predictor"]])
  )
}

prediction_formula_c <- function() {
  age_term <- paste0(
    "splines::ns(chronological_age_years, ",
    "knots=c(35,50,65), Boundary.knots=c(20,80), intercept=FALSE)"
  )
  as.formula(paste(
    "mobility_disability ~", age_term,
    "+ sex + race_ethnicity",
    "+ phenoage_acceleration_per_5_years"
  ))
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

fit_weighted_model_c <- function(
  formula,
  data,
  analysis_weights,
  start,
  label
) {
  if (length(analysis_weights) != nrow(data)) {
    stop(label, ": weights and rows differ.")
  }
  if (
    any(!is.finite(analysis_weights)) ||
      any(analysis_weights < 0) ||
      sum(analysis_weights) <= 0
  ) {
    stop(label, ": invalid analysis weights.")
  }
  scaled <- as.numeric(analysis_weights)
  scaled <- scaled * nrow(data) / sum(scaled)
  frame <- data
  frame$.analysis_weight <- scaled
  matrix <- model.matrix(formula, data = frame)
  effective <- matrix[scaled > 0, , drop = FALSE]
  if (qr(effective)$rank < ncol(effective)) {
    stop(label, ": positive-weight model matrix is rank deficient.")
  }
  fitted <- suppressWarnings(glm(
    formula,
    data = frame,
    weights = .analysis_weight,
    family = quasibinomial(link = "logit"),
    start = start,
    control = glm.control(epsilon = 1e-8, maxit = 200),
    na.action = na.fail
  ))
  if (!isTRUE(fitted$converged) || any(!is.finite(coef(fitted)))) {
    stop(label, ": weighted Model C failed to converge.")
  }
  fitted
}

predict_numeric <- function(model, newdata, label) {
  prediction <- as.numeric(predict(
    model,
    newdata = newdata,
    type = "response",
    se.fit = FALSE
  ))
  if (length(prediction) != nrow(newdata) || any(!is.finite(prediction))) {
    stop(label, ": invalid response prediction.")
  }
  clip_probability(prediction)
}

point_and_replicate_metrics <- function(weights, data, starts) {
  formula <- prediction_formula_c()
  directions <- list(
    train_2015_2016_test_2017_2018 = c("2015_2016", "2017_2018"),
    train_2017_2018_test_2015_2016 = c("2017_2018", "2015_2016")
  )
  pooled <- list()
  direction_values <- list()
  for (direction in names(directions)) {
    train_cycle <- directions[[direction]][[1]]
    test_cycle <- directions[[direction]][[2]]
    train <- data$NHANES_CYCLE == train_cycle
    test <- data$NHANES_CYCLE == test_cycle
    model <- fit_weighted_model_c(
      formula,
      data[train, , drop = FALSE],
      weights[train],
      starts[[direction]],
      paste(direction, "model_c")
    )
    prediction <- predict_numeric(
      model,
      data[test, , drop = FALSE],
      paste(direction, "model_c")
    )
    y <- data$mobility_disability[test]
    w <- weights[test]
    direction_values[[direction]] <- c(
      brier = weighted_mean((prediction - y)^2, w),
      auc = weighted_auc(y, prediction, w)
    )
    pooled[[direction]] <- data.frame(
      y = y,
      weight = w,
      prediction = prediction
    )
  }
  combined <- do.call(rbind, pooled)
  c(
    brier_c = weighted_mean(
      (combined$prediction - combined$y)^2,
      combined$weight
    ),
    auc_c = weighted_auc(
      combined$y,
      combined$prediction,
      combined$weight
    ),
    brier_c_train_2015_2016_test_2017_2018 =
      direction_values[["train_2015_2016_test_2017_2018"]][["brier"]],
    auc_c_train_2015_2016_test_2017_2018 =
      direction_values[["train_2015_2016_test_2017_2018"]][["auc"]],
    brier_c_train_2017_2018_test_2015_2016 =
      direction_values[["train_2017_2018_test_2015_2016"]][["brier"]],
    auc_c_train_2017_2018_test_2015_2016 =
      direction_values[["train_2017_2018_test_2015_2016"]][["auc"]]
  )
}

prepare_primary <- function(input_path) {
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
  missing <- setdiff(required, names(raw))
  if (length(missing) > 0) {
    stop("Missing input columns: ", paste(missing, collapse = ", "))
  }
  if (nrow(raw) != 5223) {
    stop("Private input must contain 5,223 rows.")
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
  raw$pooled_stratum <- factor(raw$pooled_stratum)
  raw$pooled_psu <- factor(raw$pooled_psu)
  primary <- raw[raw$domain_mobility_disability == 1, , drop = FALSE]
  if (nrow(primary) != 4366) {
    stop("Primary domain count changed.")
  }
  if (sum(primary$mobility_disability) != 682) {
    stop("Primary positive count changed.")
  }
  variables <- c(
    "NHANES_CYCLE", "chronological_age_years", "WTSAF4YR",
    "pooled_stratum", "pooled_psu", "SDMVSTRA", "SDMVPSU", "sex",
    "race_ethnicity", "phenoage_acceleration_per_5_years",
    "mobility_disability"
  )
  if (anyNA(primary[variables])) {
    stop("Primary Stage 4 variables contain missing values.")
  }
  if (any(primary$WTSAF4YR <= 0)) {
    stop("Primary Stage 4 weights must be positive.")
  }
  primary$primary_row_index <- seq_len(nrow(primary))
  primary
}

weighted_cycle_quantiles <- function(design, variable) {
  output <- list()
  for (cycle in c("2015_2016", "2017_2018")) {
    cycle_design <- subset(design, NHANES_CYCLE == cycle)
    value <- svyquantile(
      as.formula(paste0("~", variable)),
      cycle_design,
      quantiles = c(0.01, 0.99),
      ci = FALSE,
      na.rm = TRUE
    )

    # survey >= 4.1 returns a newsvyquantile list.  coef() is the
    # version-stable public extractor for its quantile point estimates.
    numeric_value <- as.numeric(coef(value))
    if (
      length(numeric_value) != 2 ||
        any(!is.finite(numeric_value)) ||
        numeric_value[[1]] > numeric_value[[2]]
    ) {
      stop(
        "Weighted quantile extraction failed for ",
        variable,
        " in cycle ",
        cycle,
        "."
      )
    }

    output[[cycle]] <- data.frame(
      cycle = cycle,
      variable = variable,
      quantile_01 = numeric_value[[1]],
      quantile_99 = numeric_value[[2]],
      stringsAsFactors = FALSE
    )
  }
  do.call(rbind, output)
}

write_support_quantiles <- function(input_path, private_dir) {
  if (!requireNamespace("survey", quietly = TRUE)) {
    stop("Missing R package 'survey'.")
  }
  suppressPackageStartupMessages({
    library(survey)
  })
  options(survey.lonely.psu = "fail")

  primary <- prepare_primary(input_path)
  full_design <- svydesign(
    ids = ~pooled_psu,
    strata = ~pooled_stratum,
    weights = ~WTSAF4YR,
    nest = TRUE,
    data = primary
  )
  quantiles <- rbind(
    weighted_cycle_quantiles(
      full_design,
      "phenoage_acceleration_per_5_years"
    ),
    weighted_cycle_quantiles(
      full_design,
      "chronological_age_years"
    )
  )
  if (
    nrow(quantiles) != 4 ||
      any(!is.finite(quantiles$quantile_01)) ||
      any(!is.finite(quantiles$quantile_99))
  ) {
    stop("Stage 4 support-quantile audit failed.")
  }

  dir.create(private_dir, recursive = TRUE, showWarnings = FALSE)
  write.csv(
    quantiles,
    file.path(private_dir, "stage4_support_quantiles.csv"),
    row.names = FALSE
  )
  invisible(quantiles)
}

run_self_test <- function() {
  if (!requireNamespace("survey", quietly = TRUE)) {
    stop("Missing R package 'survey'.")
  }
  suppressPackageStartupMessages({
    library(survey)
    library(splines)
  })
  set.seed(20260724)
  race_levels <- c(
    "Non-Hispanic White", "Mexican American", "Other Hispanic",
    "Non-Hispanic Black", "Non-Hispanic Asian", "Other or multiracial"
  )
  # Build the survey structure explicitly so every stratum contains
  # both PSUs in the pooled design and within each cycle-specific design.
  grid <- expand.grid(
    NHANES_CYCLE = c("2015_2016", "2017_2018"),
    SDMVSTRA = seq_len(6),
    SDMVPSU = c(1, 2),
    race_ethnicity = race_levels,
    sex = c("Male", "Female"),
    age_index = seq_len(6),
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  n <- nrow(grid)
  grid$chronological_age_years <- seq(22, 78, length.out = 6)[grid$age_index]
  grid$phenoage_acceleration_per_5_years <- rnorm(n)
  grid$sex <- factor(grid$sex, levels = c("Male", "Female"))
  grid$race_ethnicity <- factor(grid$race_ethnicity, levels = race_levels)
  grid$NHANES_CYCLE <- factor(
    grid$NHANES_CYCLE,
    levels = c("2015_2016", "2017_2018")
  )
  grid$WTSAF4YR <- seq(100, 1000, length.out = n)
  grid$pooled_stratum <- interaction(
    grid$NHANES_CYCLE,
    grid$SDMVSTRA,
    drop = TRUE
  )
  grid$pooled_psu <- interaction(
    grid$NHANES_CYCLE,
    grid$SDMVSTRA,
    grid$SDMVPSU,
    drop = TRUE
  )

  pooled_psu_counts <- tapply(
    grid$pooled_psu,
    grid$pooled_stratum,
    function(value) length(unique(value))
  )
  stopifnot(all(pooled_psu_counts == 2))
  for (cycle in levels(grid$NHANES_CYCLE)) {
    cycle_rows <- grid$NHANES_CYCLE == cycle
    cycle_psu_counts <- tapply(
      grid$SDMVPSU[cycle_rows],
      grid$SDMVSTRA[cycle_rows],
      function(value) length(unique(value))
    )
    stopifnot(all(cycle_psu_counts == 2))
  }
  eta <- -2.2 + 0.035 * (grid$chronological_age_years - 50) +
    0.2 * (grid$sex == "Female") +
    0.25 * grid$phenoage_acceleration_per_5_years
  grid$mobility_disability <- rbinom(n, 1, plogis(eta))
  for (cycle in levels(grid$NHANES_CYCLE)) {
    index <- which(grid$NHANES_CYCLE == cycle)
    grid$mobility_disability[index[[1]]] <- 0
    grid$mobility_disability[index[[2]]] <- 1
  }
  design <- svydesign(
    ids = ~pooled_psu,
    strata = ~pooled_stratum,
    weights = ~WTSAF4YR,
    nest = TRUE,
    data = grid
  )
  set.seed(20260724)
  replicate_design <- as.svrepdesign(
    design,
    type = "bootstrap",
    replicates = 5,
    mse = TRUE
  )
  replicate_weights <- weights(replicate_design, type = "analysis")
  stopifnot(nrow(replicate_weights) == n, ncol(replicate_weights) == 5)
  formula <- prediction_formula_c()
  starts <- list()
  for (direction in c(
    "train_2015_2016_test_2017_2018",
    "train_2017_2018_test_2015_2016"
  )) {
    train_cycle <- if (grepl("train_2015", direction)) "2015_2016" else "2017_2018"
    train_data <- grid[grid$NHANES_CYCLE == train_cycle, , drop = FALSE]
    train_design <- svydesign(
      ids = ~SDMVPSU,
      strata = ~SDMVSTRA,
      weights = ~WTSAF4YR,
      nest = TRUE,
      data = train_data
    )
    fit <- suppressWarnings(svyglm(
      formula,
      design = train_design,
      family = quasibinomial(link = "logit")
    ))
    stopifnot(isTRUE(fit$converged), all(is.finite(coef(fit))))
    starts[[direction]] <- coef(fit)
  }
  metrics <- point_and_replicate_metrics(
    weights(design),
    grid,
    starts
  )
  stopifnot(all(is.finite(metrics)))

  test_quantiles <- rbind(
    weighted_cycle_quantiles(
      design,
      "phenoage_acceleration_per_5_years"
    ),
    weighted_cycle_quantiles(
      design,
      "chronological_age_years"
    )
  )
  stopifnot(
    nrow(test_quantiles) == 4,
    all(is.finite(test_quantiles$quantile_01)),
    all(is.finite(test_quantiles$quantile_99)),
    all(test_quantiles$quantile_01 <= test_quantiles$quantile_99)
  )

  cat("SELF-TEST PASSED\n")
}

if (length(args) == 1 && args[[1]] == "--self-test") {
  run_self_test()
  quit(status = 0)
}

if (length(args) == 1 && args[[1]] == "--build") {
  cat(STAGE4_R_BUILD, "\n", sep = "")
  quit(status = 0)
}

if (length(args) == 3 && args[[1]] == "--quantiles-only") {
  input_path <- normalizePath(args[[2]], mustWork = TRUE)
  private_dir <- normalizePath(args[[3]], mustWork = FALSE)
  write_support_quantiles(input_path, private_dir)
  cat("STAGE 4 SUPPORT QUANTILES PASSED\n")
  quit(status = 0)
}

if (length(args) == 3 && args[[1]] == "--plot") {
  table_dir <- normalizePath(args[[2]], mustWork = TRUE)
  figure_dir <- normalizePath(args[[3]], mustWork = FALSE)
  dir.create(figure_dir, recursive = TRUE, showWarnings = FALSE)
  bootstrap <- read.csv(
    file.path(table_dir, "18_stage4_bootstrap_summary.csv"),
    stringsAsFactors = FALSE
  )
  plot_data <- bootstrap[bootstrap$metric %in% c(
    "brier_delta_d_minus_c", "auc_delta_d_minus_c"
  ), , drop = FALSE]
  labels <- c(
    brier_delta_d_minus_c = "Brier delta D-C",
    auc_delta_d_minus_c = "AUC delta D-C"
  )
  png(
    file.path(figure_dir, "18_stage4_model_d_incremental_performance.png"),
    width = 1700,
    height = 1000,
    res = 170
  )
  par(mar = c(5, 10, 3, 2))
  y <- rev(seq_len(nrow(plot_data)))
  xlim <- range(c(plot_data$ci_low_95, plot_data$ci_high_95, 0))
  plot(
    plot_data$estimate,
    y,
    xlim = xlim,
    ylim = c(0.5, nrow(plot_data) + 0.5),
    yaxt = "n",
    ylab = "",
    xlab = "Model D minus Model C",
    pch = 19,
    main = "Stage 4 pooled out-of-cycle performance"
  )
  axis(2, at = y, labels = labels[plot_data$metric], las = 1)
  segments(plot_data$ci_low_95, y, plot_data$ci_high_95, y, lwd = 2)
  abline(v = 0, lty = 2)
  dev.off()

  shape <- read.csv(
    file.path(table_dir, "18_stage4_acceleration_shape.csv"),
    stringsAsFactors = FALSE
  )
  eligible <- shape$display_eligible %in% c(TRUE, "TRUE", "True", 1)
  shape <- shape[eligible, , drop = FALSE]
  directions <- unique(shape$direction)
  png(
    file.path(figure_dir, "18_stage4_cycle_specific_acceleration_shapes.png"),
    width = 1700,
    height = 1100,
    res = 170
  )
  ranges <- range(shape$term_score_log_odds, finite = TRUE)
  x_ranges <- range(shape$acceleration_per_5_years, finite = TRUE)
  first <- shape[shape$direction == directions[[1]], , drop = FALSE]
  plot(
    first$acceleration_per_5_years,
    first$term_score_log_odds,
    type = "l",
    lwd = 2,
    xlim = x_ranges,
    ylim = ranges,
    xlab = "PhenoAge acceleration per 5 years",
    ylab = "Centered EBM log-odds contribution",
    main = "Cycle-trained Model D acceleration functions"
  )
  if (length(directions) > 1) {
    second <- shape[shape$direction == directions[[2]], , drop = FALSE]
    lines(
      second$acceleration_per_5_years,
      second$term_score_log_odds,
      lwd = 2,
      lty = 2
    )
  }
  abline(h = 0, lty = 3)
  legend(
    "topleft",
    legend = directions,
    lty = seq_along(directions),
    lwd = 2,
    bty = "n"
  )
  dev.off()
  cat("PLOTS PASSED\n")
  quit(status = 0)
}

if (length(args) != 3) {
  stop(
    "Expected: private input CSV, private work directory, Stage 3 table directory; ",
    "or --plot TABLE_DIR FIGURE_DIR; or --self-test."
  )
}

input_path <- normalizePath(args[[1]], mustWork = TRUE)
private_dir <- normalizePath(args[[2]], mustWork = FALSE)
stage3_dir <- normalizePath(args[[3]], mustWork = TRUE)
dir.create(private_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("survey", quietly = TRUE)) {
  stop("Missing R package 'survey'.")
}
suppressPackageStartupMessages({
  library(survey)
  library(splines)
})
options(survey.lonely.psu = "fail")

primary <- prepare_primary(input_path)
full_design <- svydesign(
  ids = ~pooled_psu,
  strata = ~pooled_stratum,
  weights = ~WTSAF4YR,
  nest = TRUE,
  data = primary
)
design_df <- degf(full_design)
if (design_df != 30) {
  stop("Stage 4 design degrees of freedom changed: ", design_df)
}

formula <- prediction_formula_c()
directions <- list(
  train_2015_2016_test_2017_2018 = c("2015_2016", "2017_2018"),
  train_2017_2018_test_2015_2016 = c("2017_2018", "2015_2016")
)
starts <- list()
point_predictions <- list()
point_direction_rows <- list()
model_diagnostics <- list()

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
  fitted <- capture_fit(svyglm(
    formula,
    design = train_design,
    family = quasibinomial(link = "logit")
  ))
  if (
    !isTRUE(fitted$model$converged) ||
      any(!is.finite(coef(fitted$model))) ||
      length(fitted$warnings) > 0
  ) {
    stop("Authoritative Model C point fit failed: ", direction)
  }
  starts[[direction]] <- coef(fitted$model)
  prediction <- predict_numeric(
    fitted$model,
    test_data,
    paste(direction, "authoritative_model_c")
  )
  y <- test_data$mobility_disability
  w <- test_data$WTSAF4YR
  calibration <- calibration_metrics(y, prediction, w)
  point_direction_rows[[direction]] <- data.frame(
    direction = direction,
    train_cycle = train_cycle,
    test_cycle = test_cycle,
    train_n = nrow(train_data),
    test_n = nrow(test_data),
    test_positive_n = sum(y),
    brier_c = weighted_mean((prediction - y)^2, w),
    auc_c = weighted_auc(y, prediction, w),
    calibration_intercept_c = calibration[["intercept"]],
    calibration_slope_c = calibration[["slope"]],
    stringsAsFactors = FALSE
  )
  point_predictions[[direction]] <- data.frame(
    y = y,
    weight = w,
    prediction = prediction
  )
  model_diagnostics[[direction]] <- data.frame(
    direction = direction,
    converged = isTRUE(fitted$model$converged),
    finite_coefficients = all(is.finite(coef(fitted$model))),
    warning_n = length(fitted$warnings),
    warnings = paste(fitted$warnings, collapse = " | "),
    stringsAsFactors = FALSE
  )
}

point_direction <- do.call(rbind, point_direction_rows)
pooled <- do.call(rbind, point_predictions)
point_calibration <- calibration_metrics(
  pooled$y,
  pooled$prediction,
  pooled$weight
)
point_pooled <- data.frame(
  brier_c = weighted_mean(
    (pooled$prediction - pooled$y)^2,
    pooled$weight
  ),
  auc_c = weighted_auc(
    pooled$y,
    pooled$prediction,
    pooled$weight
  ),
  calibration_intercept_c = point_calibration[["intercept"]],
  calibration_slope_c = point_calibration[["slope"]],
  stringsAsFactors = FALSE
)

stage3_direction <- read.csv(
  file.path(stage3_dir, "13_stage3_prediction_direction_metrics.csv"),
  stringsAsFactors = FALSE
)
stage3_bootstrap <- read.csv(
  file.path(stage3_dir, "13_stage3_prediction_bootstrap_summary.csv"),
  stringsAsFactors = FALSE
)
merged <- merge(
  point_direction,
  stage3_direction[c("direction", "brier_c", "auc_c")],
  by = "direction",
  suffixes = c("_stage4_r", "_stage3")
)
max_direction_difference <- max(abs(c(
  merged$brier_c_stage4_r - merged$brier_c_stage3,
  merged$auc_c_stage4_r - merged$auc_c_stage3
)))
stage3_brier <- stage3_bootstrap$estimate[
  stage3_bootstrap$metric == "brier_c"
]
stage3_auc <- stage3_bootstrap$estimate[
  stage3_bootstrap$metric == "auc_c"
]
max_pooled_difference <- max(abs(c(
  point_pooled$brier_c - stage3_brier,
  point_pooled$auc_c - stage3_auc
)))
if (
  !is.finite(max_direction_difference) ||
    !is.finite(max_pooled_difference) ||
    max_direction_difference > 1e-7 ||
    max_pooled_difference > 1e-7
) {
  stop(
    "Stage 4 R Model C did not reconcile with Stage 3. Direction max=",
    max_direction_difference,
    ", pooled max=",
    max_pooled_difference
  )
}

set.seed(20260724)
replicate_design <- as.svrepdesign(
  full_design,
  type = "bootstrap",
  replicates = 500,
  mse = TRUE
)
replicate_weights <- weights(replicate_design, type = "analysis")
if (ncol(replicate_weights) != 500 || nrow(replicate_weights) != 4366) {
  stop("Stage 4 replicate-weight dimensions changed.")
}

replicate_metrics <- matrix(
  NA_real_,
  nrow = ncol(replicate_weights),
  ncol = 6,
  dimnames = list(NULL, c(
    "brier_c", "auc_c",
    "brier_c_train_2015_2016_test_2017_2018",
    "auc_c_train_2015_2016_test_2017_2018",
    "brier_c_train_2017_2018_test_2015_2016",
    "auc_c_train_2017_2018_test_2015_2016"
  ))
)
cat("\nPreparing 500 Model C reference bootstrap replicates.\n")
for (index in seq_len(ncol(replicate_weights))) {
  estimate <- point_and_replicate_metrics(
    replicate_weights[, index],
    primary,
    starts
  )
  replicate_metrics[index, ] <- estimate
  if (index %% 25 == 0 || index == ncol(replicate_weights)) {
    cat(sprintf("Model C reference progress: %d/%d\n", index, ncol(replicate_weights)))
    flush.console()
  }
}
if (any(!is.finite(replicate_metrics))) {
  stop("A Model C reference replicate contains a non-finite metric.")
}

weights_frame <- data.frame(
  primary_row_index = primary$primary_row_index,
  replicate_weights,
  check.names = FALSE
)
names(weights_frame)[-1] <- sprintf("replicate_%03d", seq_len(500))
write.csv(
  weights_frame,
  gzfile(file.path(private_dir, "stage4_replicate_weights.csv.gz")),
  row.names = FALSE
)
write.csv(
  data.frame(replicate = seq_len(500), replicate_metrics),
  gzfile(file.path(private_dir, "stage4_model_c_replicate_metrics.csv.gz")),
  row.names = FALSE
)
write.csv(
  point_direction,
  file.path(private_dir, "stage4_model_c_point_direction_metrics.csv"),
  row.names = FALSE
)
write.csv(
  point_pooled,
  file.path(private_dir, "stage4_model_c_point_pooled_metrics.csv"),
  row.names = FALSE
)
write.csv(
  do.call(rbind, model_diagnostics),
  file.path(private_dir, "stage4_model_c_diagnostics.csv"),
  row.names = FALSE
)
write.csv(
  data.frame(replicate = seq_len(500), rscale = replicate_design$rscales),
  file.path(private_dir, "stage4_rscales.csv"),
  row.names = FALSE
)
write.csv(
  data.frame(
    key = c(
      "r_build", "scale", "mse", "design_df", "replicate_n",
      "primary_n", "positive_n", "seed", "max_direction_reconciliation",
      "max_pooled_reconciliation"
    ),
    value = c(
      STAGE4_R_BUILD,
      replicate_design$scale,
      replicate_design$mse,
      design_df,
      ncol(replicate_weights),
      nrow(primary),
      sum(primary$mobility_disability),
      20260724,
      max_direction_difference,
      max_pooled_difference
    ),
    stringsAsFactors = FALSE
  ),
  file.path(private_dir, "stage4_reference_metadata.csv"),
  row.names = FALSE
)
write_support_quantiles(input_path, private_dir)
cat("STAGE 4 R REFERENCE PREPARATION PASSED\n")
