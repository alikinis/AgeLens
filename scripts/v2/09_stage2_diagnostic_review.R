NOTEBOOK_BUILD_R <- "AgeLens-V2-Stage2-Review-20260724"

args <- commandArgs(trailingOnly = TRUE)

weighted_quantile <- function(x, w, probabilities) {
  valid <- is.finite(x) & is.finite(w) & w > 0
  x <- x[valid]
  w <- w[valid]
  ordering <- order(x)
  x <- x[ordering]
  w <- w[ordering]
  cumulative <- cumsum(w) / sum(w)
  vapply(
    probabilities,
    function(probability) {
      index <- which(cumulative >= probability)[1]
      x[[index]]
    },
    numeric(1)
  )
}

rcs_nonlinear_basis <- function(x, all_knots) {
  if (length(all_knots) < 4) {
    stop("At least four knots are required.")
  }
  if (is.unsorted(all_knots, strictly = TRUE)) {
    stop("Knots must be strictly increasing.")
  }
  k <- length(all_knots)
  lower <- all_knots[[1]]
  upper <- all_knots[[k]]
  penultimate <- all_knots[[k - 1]]
  scale <- (upper - lower)^2
  truncated_cube <- function(value, knot) {
    pmax(value - knot, 0)^3 / scale
  }
  basis <- sapply(seq_len(k - 2), function(index) {
    knot <- all_knots[[index]]
    truncated_cube(x, knot) -
      truncated_cube(x, penultimate) *
        ((upper - knot) / (upper - penultimate)) +
      truncated_cube(x, upper) *
        ((penultimate - knot) / (upper - penultimate))
  })
  if (is.null(dim(basis))) {
    basis <- matrix(basis, ncol = 1)
  }
  colnames(basis) <- paste0(
    "accel_nonlinear_",
    seq_len(ncol(basis))
  )
  basis
}

if (length(args) == 1 && args[[1]] == "--self-test") {
  q <- weighted_quantile(
    c(-2, 0, 2, 4),
    c(1, 1, 1, 1),
    c(0.25, 0.5, 0.75)
  )
  stopifnot(identical(as.numeric(q), c(-2, 0, 2)))
  basis <- rcs_nonlinear_basis(
    c(-10, 0, 10),
    c(-30, -10, 0, 10, 40)
  )
  stopifnot(nrow(basis) == 3, ncol(basis) == 3)
  cat("SELF-TEST PASSED\n")
  quit(status = 0)
}

if (length(args) != 4) {
  stop(
    "Expected 4 arguments: private input CSV, output table directory, ",
    "figure directory, log directory."
  )
}

input_path <- normalizePath(args[[1]], mustWork = TRUE)
output_dir <- normalizePath(args[[2]], mustWork = FALSE)
figure_dir <- normalizePath(args[[3]], mustWork = FALSE)
log_dir <- normalizePath(args[[4]], mustWork = FALSE)

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(figure_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("survey", quietly = TRUE)) {
  stop("Missing R package 'survey'.")
}

suppressPackageStartupMessages({
  library(survey)
  library(splines)
})

options(survey.lonely.psu = "fail")

dat <- read.csv(
  input_path,
  stringsAsFactors = FALSE,
  check.names = FALSE,
  na.strings = c("", "NA")
)

required <- c(
  "SEQN",
  "NHANES_CYCLE",
  "chronological_age_years",
  "WTSAF4YR",
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
  "domain_phq9_ge10"
)
missing_columns <- setdiff(required, names(dat))
if (length(missing_columns) > 0) {
  stop("Missing input columns: ", paste(missing_columns, collapse = ", "))
}
if (nrow(dat) != 5223) {
  stop("Expected exactly 5,223 canonical rows.")
}

numeric_columns <- c(
  "chronological_age_years",
  "WTSAF4YR",
  "phenoage_acceleration_years",
  "phenoage_acceleration_per_5_years",
  "mobility_disability",
  "any_disability_six",
  "fair_poor_general_health",
  "phq9_ge10",
  "domain_mobility_disability",
  "domain_any_disability_six",
  "domain_fair_poor_general_health",
  "domain_phq9_ge10"
)
for (column in numeric_columns) {
  dat[[column]] <- suppressWarnings(as.numeric(dat[[column]]))
}

dat$sex <- factor(dat$sex, levels = c("Male", "Female"))
dat$race_ethnicity <- factor(
  dat$race_ethnicity,
  levels = c(
    "Non-Hispanic White",
    "Mexican American",
    "Other Hispanic",
    "Non-Hispanic Black",
    "Non-Hispanic Asian",
    "Other or multiracial"
  )
)
dat$NHANES_CYCLE <- factor(
  dat$NHANES_CYCLE,
  levels = c("2015_2016", "2017_2018")
)
dat$pooled_stratum <- factor(dat$pooled_stratum)
dat$pooled_psu <- factor(dat$pooled_psu)

acceleration_knots <- c(-30, -10, 0, 10, 40)
basis <- rcs_nonlinear_basis(
  dat$phenoage_acceleration_years,
  acceleration_knots
)
for (index in seq_len(ncol(basis))) {
  dat[[colnames(basis)[[index]]]] <- basis[, index]
}

full_design <- svydesign(
  ids = ~pooled_psu,
  strata = ~pooled_stratum,
  weights = ~WTSAF4YR,
  nest = TRUE,
  data = dat
)

age_term <- paste0(
  "splines::ns(chronological_age_years, ",
  "knots=c(35,50,65), Boundary.knots=c(20,80), intercept=FALSE)"
)

fit_with_warnings <- function(formula, design, family) {
  captured <- character(0)
  fitted <- withCallingHandlers(
    svyglm(formula, design = design, family = family),
    warning = function(condition) {
      captured <<- c(captured, conditionMessage(condition))
      invokeRestart("muffleWarning")
    }
  )
  list(model = fitted, warnings = unique(captured))
}

extract_effect <- function(model, term, design_df) {
  coefficient_table <- summary(
    model,
    df.resid = design_df
  )$coefficients
  if (!term %in% rownames(coefficient_table)) {
    stop("Term absent: ", term)
  }
  estimate <- coefficient_table[term, "Estimate"]
  standard_error <- coefficient_table[term, "Std. Error"]
  critical <- qt(0.975, df = design_df)
  statistic <- estimate / standard_error
  data.frame(
    estimate = estimate,
    standard_error = standard_error,
    prevalence_ratio = exp(estimate),
    ci_low_95 = exp(estimate - critical * standard_error),
    ci_high_95 = exp(estimate + critical * standard_error),
    p_value = 2 * pt(abs(statistic), df = design_df, lower.tail = FALSE)
  )
}

extract_regterm_p <- function(object) {
  candidates <- c("p", "p.value", "pval")
  for (candidate in candidates) {
    if (!is.null(object[[candidate]])) {
      value <- suppressWarnings(as.numeric(object[[candidate]]))
      if (length(value) > 0 && is.finite(value[[1]])) {
        return(value[[1]])
      }
    }
  }
  printed <- paste(capture.output(print(object)), collapse = " ")
  match <- regexpr(
    "p[[:space:]]*=[[:space:]]*[-+0-9.eE]+",
    printed
  )
  if (match[[1]] > 0) {
    token <- regmatches(printed, match)
    value <- as.numeric(sub(".*=", "", token))
    if (is.finite(value)) {
      return(value)
    }
  }
  stop("Could not extract regTermTest p-value.")
}

primary_rows <- dat$domain_mobility_disability == 1
primary_data <- dat[primary_rows, , drop = FALSE]
primary_design <- subset(
  full_design,
  domain_mobility_disability == 1
)
if (nrow(primary_data) != 4366) {
  stop("Primary domain count changed.")
}
if (sum(primary_data$mobility_disability) != 682) {
  stop("Primary positive count changed.")
}
primary_df <- degf(primary_design)

linear_formula <- as.formula(
  paste(
    "mobility_disability ~",
    age_term,
    "+ sex + race_ethnicity + NHANES_CYCLE",
    "+ phenoage_acceleration_per_5_years"
  )
)
linear_fit <- fit_with_warnings(
  linear_formula,
  primary_design,
  quasipoisson(link = "log")
)
linear_effect <- extract_effect(
  linear_fit$model,
  "phenoage_acceleration_per_5_years",
  primary_df
)

existing_primary_path <- file.path(
  output_dir,
  "06_stage2_primary_result.csv"
)
if (!file.exists(existing_primary_path)) {
  stop("Existing Stage 2 primary result not found.")
}
existing_primary <- read.csv(existing_primary_path)
existing_pr <- existing_primary$prevalence_ratio[[1]]
if (abs(existing_pr - linear_effect$prevalence_ratio[[1]]) > 1e-10) {
  stop("Primary linear prevalence ratio did not reproduce.")
}

# Weighted exposure quantiles.
quantile_probabilities <- c(
  0.01, 0.025, 0.05, 0.10, 0.25, 0.50,
  0.75, 0.90, 0.95, 0.975, 0.99
)
quantile_values <- weighted_quantile(
  primary_data$phenoage_acceleration_years,
  primary_data$WTSAF4YR,
  quantile_probabilities
)
quantile_table <- data.frame(
  probability = quantile_probabilities,
  percentile = quantile_probabilities * 100,
  acceleration_years = quantile_values
)

# Audit fitted values outside the probability range.
outcomes <- c(
  "mobility_disability",
  "any_disability_six",
  "fair_poor_general_health",
  "phq9_ge10"
)
outcome_labels <- c(
  mobility_disability = "Serious mobility disability",
  any_disability_six = "Any six-domain disability",
  fair_poor_general_health = "Fair or poor general health",
  phq9_ge10 = "PHQ-9 score at least 10"
)
bound_rows <- list()

for (outcome in outcomes) {
  domain_column <- paste0("domain_", outcome)
  domain_rows <- dat[[domain_column]] == 1
  domain_data <- dat[domain_rows, , drop = FALSE]
  outcome_design <- subset(full_design, dat[[domain_column]] == 1)
  formula <- as.formula(
    paste(
      outcome,
      "~",
      age_term,
      "+ sex + race_ethnicity + NHANES_CYCLE",
      "+ phenoage_acceleration_per_5_years"
    )
  )
  fitted <- fit_with_warnings(
    formula,
    outcome_design,
    quasipoisson(link = "log")
  )
  predicted <- as.numeric(predict(fitted$model, type = "response"))
  flagged <- predicted > 1
  flagged_acceleration <- domain_data$phenoage_acceleration_years[flagged]
  flagged_weight <- domain_data$WTSAF4YR[flagged]

  bound_rows[[outcome]] <- data.frame(
    outcome = outcome,
    outcome_label = outcome_labels[[outcome]],
    n = nrow(domain_data),
    predicted_above_one_n = sum(flagged),
    predicted_above_one_weighted_percent = if (
      any(flagged)
    ) {
      100 * sum(flagged_weight) / sum(domain_data$WTSAF4YR)
    } else {
      0
    },
    predicted_max = max(predicted),
    flagged_acceleration_min = if (
      any(flagged)
    ) min(flagged_acceleration) else NA_real_,
    flagged_acceleration_median = if (
      any(flagged)
    ) median(flagged_acceleration) else NA_real_,
    flagged_acceleration_max = if (
      any(flagged)
    ) max(flagged_acceleration) else NA_real_,
    warning_n = length(fitted$warnings),
    warnings = paste(fitted$warnings, collapse = " | "),
    stringsAsFactors = FALSE
  )
}
bound_audit <- do.call(rbind, bound_rows)

existing_diagnostics <- read.csv(
  file.path(output_dir, "06_stage2_model_diagnostics.csv")
)
existing_model_c <- existing_diagnostics[
  existing_diagnostics$model == "model_c",
  c("outcome", "predicted_above_one_n", "predicted_max")
]
reconciled <- merge(
  bound_audit,
  existing_model_c,
  by = "outcome",
  suffixes = c("_review", "_stage2"),
  all.x = TRUE
)
if (
  any(
    reconciled$predicted_above_one_n_review !=
      reconciled$predicted_above_one_n_stage2
  )
) {
  stop("Fitted-above-one counts did not reconcile.")
}
if (
  any(
    abs(
      reconciled$predicted_max_review -
        reconciled$predicted_max_stage2
    ) > 1e-8
  )
) {
  stop("Fitted maxima did not reconcile.")
}

# Exposure-range sensitivities for the prespecified linear summary.
ranges <- list(
  full = c(-Inf, Inf),
  weighted_1_to_99_percent = c(
    quantile_values[[1]],
    quantile_values[[11]]
  ),
  weighted_2.5_to_97.5_percent = c(
    quantile_values[[2]],
    quantile_values[[10]]
  )
)
trimmed_rows <- list()
for (range_name in names(ranges)) {
  limits <- ranges[[range_name]]
  keep <- primary_data$phenoage_acceleration_years >= limits[[1]] &
    primary_data$phenoage_acceleration_years <= limits[[2]]
  trimmed_data <- primary_data[keep, , drop = FALSE]
  trimmed_design <- subset(
    primary_design,
    phenoage_acceleration_years >= limits[[1]] &
      phenoage_acceleration_years <= limits[[2]]
  )
  fitted <- fit_with_warnings(
    linear_formula,
    trimmed_design,
    quasipoisson(link = "log")
  )
  effect <- extract_effect(
    fitted$model,
    "phenoage_acceleration_per_5_years",
    degf(trimmed_design)
  )
  predicted <- as.numeric(predict(fitted$model, type = "response"))
  trimmed_rows[[range_name]] <- data.frame(
    sensitivity = range_name,
    lower_acceleration_years = limits[[1]],
    upper_acceleration_years = limits[[2]],
    n = nrow(trimmed_data),
    positive_n = sum(trimmed_data$mobility_disability),
    design_df = degf(trimmed_design),
    prevalence_ratio = effect$prevalence_ratio,
    ci_low_95 = effect$ci_low_95,
    ci_high_95 = effect$ci_high_95,
    p_value = effect$p_value,
    predicted_above_one_n = sum(predicted > 1),
    predicted_max = max(predicted),
    warning_n = length(fitted$warnings),
    warnings = paste(fitted$warnings, collapse = " | "),
    stringsAsFactors = FALSE
  )
}
trimmed_sensitivity <- do.call(rbind, trimmed_rows)

# Bounded survey-weighted logistic spline for diagnostic visualization.
spline_formula <- as.formula(
  paste(
    "mobility_disability ~",
    age_term,
    "+ sex + race_ethnicity + NHANES_CYCLE",
    "+ phenoage_acceleration_per_5_years",
    "+ accel_nonlinear_1 + accel_nonlinear_2 + accel_nonlinear_3"
  )
)
spline_fit <- fit_with_warnings(
  spline_formula,
  primary_design,
  quasibinomial(link = "logit")
)
spline_test <- regTermTest(
  spline_fit$model,
  ~accel_nonlinear_1 + accel_nonlinear_2 + accel_nonlinear_3,
  method = "Wald"
)
spline_nonlinearity_p <- extract_regterm_p(spline_test)

set_acceleration <- function(frame, acceleration) {
  updated <- frame
  updated$phenoage_acceleration_years <- acceleration
  updated$phenoage_acceleration_per_5_years <- acceleration / 5
  nonlinear <- rcs_nonlinear_basis(
    rep(acceleration, nrow(updated)),
    acceleration_knots
  )
  for (index in seq_len(ncol(nonlinear))) {
    updated[[colnames(nonlinear)[[index]]]] <- nonlinear[, index]
  }
  updated
}

standardized_margin <- function(model, frame, acceleration, design_df) {
  newdata <- set_acceleration(frame, acceleration)
  term_object <- delete.response(terms(model))
  matrix <- model.matrix(
    term_object,
    data = newdata,
    contrasts.arg = model$contrasts,
    xlev = model$xlevels
  )
  coefficients <- coef(model)
  matrix <- matrix[, names(coefficients), drop = FALSE]
  eta <- as.numeric(matrix %*% coefficients)
  probability <- plogis(eta)
  normalized_weight <- newdata$WTSAF4YR / sum(newdata$WTSAF4YR)
  margin <- sum(normalized_weight * probability)
  derivative <- probability * (1 - probability)
  gradient <- colSums(
    matrix * as.numeric(normalized_weight * derivative)
  )
  covariance <- vcov(model)
  variance <- as.numeric(
    t(gradient) %*% covariance %*% gradient
  )
  standard_error <- sqrt(max(variance, 0))
  bounded_margin <- min(max(margin, 1e-8), 1 - 1e-8)
  logit_standard_error <- standard_error /
    (bounded_margin * (1 - bounded_margin))
  critical <- qt(0.975, df = design_df)
  lower <- plogis(
    qlogis(bounded_margin) -
      critical * logit_standard_error
  )
  upper <- plogis(
    qlogis(bounded_margin) +
      critical * logit_standard_error
  )
  list(
    acceleration = acceleration,
    prevalence = margin,
    standard_error = standard_error,
    ci_low_95 = lower,
    ci_high_95 = upper,
    gradient = gradient
  )
}

grid <- sort(unique(c(
  seq(
    quantile_values[[1]],
    quantile_values[[11]],
    length.out = 61
  ),
  0
)))
curve_list <- lapply(
  grid,
  function(value) {
    standardized_margin(
      spline_fit$model,
      primary_data,
      value,
      primary_df
    )
  }
)
curve <- do.call(
  rbind,
  lapply(curve_list, function(item) {
    data.frame(
      acceleration_years = item$acceleration,
      adjusted_prevalence = item$prevalence,
      ci_low_95 = item$ci_low_95,
      ci_high_95 = item$ci_high_95
    )
  })
)

anchor_probabilities <- c(0.10, 0.25, 0.50, 0.75, 0.90)
anchor_values <- weighted_quantile(
  primary_data$phenoage_acceleration_years,
  primary_data$WTSAF4YR,
  anchor_probabilities
)
covariance <- vcov(spline_fit$model)
critical <- qt(0.975, df = primary_df)
local_rows <- list()
for (index in seq_along(anchor_values)) {
  start <- anchor_values[[index]]
  end <- start + 5
  first <- standardized_margin(
    spline_fit$model,
    primary_data,
    start,
    primary_df
  )
  second <- standardized_margin(
    spline_fit$model,
    primary_data,
    end,
    primary_df
  )
  ratio <- second$prevalence / first$prevalence
  gradient_log_ratio <- (
    second$gradient / second$prevalence
  ) - (
    first$gradient / first$prevalence
  )
  variance_log_ratio <- as.numeric(
    t(gradient_log_ratio) %*%
      covariance %*%
      gradient_log_ratio
  )
  se_log_ratio <- sqrt(max(variance_log_ratio, 0))
  local_rows[[index]] <- data.frame(
    anchor_percentile = anchor_probabilities[[index]] * 100,
    start_acceleration_years = start,
    end_acceleration_years = end,
    prevalence_start = first$prevalence,
    prevalence_end = second$prevalence,
    local_five_year_prevalence_ratio = ratio,
    ci_low_95 = exp(log(ratio) - critical * se_log_ratio),
    ci_high_95 = exp(log(ratio) + critical * se_log_ratio)
  )
}
local_ratios <- do.call(rbind, local_rows)

existing_linearity <- read.csv(
  file.path(output_dir, "06_stage2_linearity_sensitivity.csv")
)
nonlinearity_review <- data.frame(
  outcome = "mobility_disability",
  prespecified_quasipoisson_nonlinearity_p =
    existing_linearity$p_value_nonlinearity[[1]],
  logistic_spline_nonlinearity_p =
    spline_nonlinearity_p,
  linear_primary_result_retained = TRUE,
  linear_primary_result_released = FALSE,
  bounded_curve_role = "diagnostic_visualization",
  logistic_warning_n = length(spline_fit$warnings),
  logistic_warnings = paste(spline_fit$warnings, collapse = " | ")
)

checks <- data.frame(
  check = c(
    "Canonical private input contains 5,223 rows",
    "Primary domain contains 4,366 rows",
    "Primary positive count equals 682",
    "Original primary linear PR reproduced",
    "Modified-Poisson bound audit reconciles",
    "Bounded curve stays within zero and one",
    "Curve confidence limits stay within zero and one",
    "Trimmed sensitivities are finite and positive",
    "Local five-year ratios are finite and positive",
    "Logistic spline nonlinearity p-value is valid",
    "No participant identifier is written publicly",
    "V1 remains unmodified",
    "Explainable model remains unauthorized"
  ),
  pass = c(
    nrow(dat) == 5223,
    nrow(primary_data) == 4366,
    sum(primary_data$mobility_disability) == 682,
    abs(existing_pr - linear_effect$prevalence_ratio[[1]]) <= 1e-10,
    TRUE,
    all(
      is.finite(curve$adjusted_prevalence) &
        curve$adjusted_prevalence > 0 &
        curve$adjusted_prevalence < 1
    ),
    all(
      curve$ci_low_95 >= 0 &
        curve$ci_high_95 <= 1 &
        curve$ci_low_95 <= curve$adjusted_prevalence &
        curve$adjusted_prevalence <= curve$ci_high_95
    ),
    all(
      is.finite(trimmed_sensitivity$prevalence_ratio) &
        trimmed_sensitivity$prevalence_ratio > 0 &
        trimmed_sensitivity$ci_low_95 > 0 &
        trimmed_sensitivity$ci_high_95 > 0
    ),
    all(
      is.finite(local_ratios$local_five_year_prevalence_ratio) &
        local_ratios$local_five_year_prevalence_ratio > 0
    ),
    is.finite(spline_nonlinearity_p) &
      spline_nonlinearity_p >= 0 &
      spline_nonlinearity_p <= 1,
    TRUE,
    TRUE,
    TRUE
  ),
  observed = c(
    nrow(dat),
    nrow(primary_data),
    sum(primary_data$mobility_disability),
    linear_effect$prevalence_ratio[[1]],
    paste(bound_audit$predicted_above_one_n, collapse = " | "),
    paste(range(curve$adjusted_prevalence), collapse = " | "),
    paste(
      min(curve$ci_low_95),
      max(curve$ci_high_95),
      sep = " | "
    ),
    paste(trimmed_sensitivity$prevalence_ratio, collapse = " | "),
    paste(
      local_ratios$local_five_year_prevalence_ratio,
      collapse = " | "
    ),
    spline_nonlinearity_p,
    "aggregate outputs only",
    "no V1 write operation",
    "not authorized"
  ),
  stringsAsFactors = FALSE
)
if (!all(checks$pass)) {
  stop(
    "Stage 2 diagnostic review checks failed: ",
    paste(checks$check[!checks$pass], collapse = "; ")
  )
}

write.csv(
  quantile_table,
  file.path(output_dir, "09_stage2_acceleration_quantiles.csv"),
  row.names = FALSE
)
write.csv(
  bound_audit,
  file.path(output_dir, "09_stage2_prediction_bound_audit.csv"),
  row.names = FALSE
)
write.csv(
  trimmed_sensitivity,
  file.path(output_dir, "09_stage2_trimmed_linear_sensitivity.csv"),
  row.names = FALSE
)
write.csv(
  curve,
  file.path(output_dir, "09_stage2_adjusted_prevalence_curve.csv"),
  row.names = FALSE
)
write.csv(
  local_ratios,
  file.path(output_dir, "09_stage2_local_five_year_ratios.csv"),
  row.names = FALSE
)
write.csv(
  nonlinearity_review,
  file.path(output_dir, "09_stage2_nonlinearity_review.csv"),
  row.names = FALSE
)
write.csv(
  checks,
  file.path(output_dir, "09_stage2_review_checks.csv"),
  row.names = FALSE
)

figure_path <- file.path(
  figure_dir,
  "09_stage2_adjusted_prevalence_curve.png"
)
png(
  filename = figure_path,
  width = 1800,
  height = 1200,
  res = 200
)
plot(
  curve$acceleration_years,
  curve$adjusted_prevalence,
  type = "n",
  ylim = range(curve$ci_low_95, curve$ci_high_95),
  xlab = "Phenotypic Age acceleration (years)",
  ylab = "Adjusted prevalence of serious mobility disability",
  main = "AgeLens V2: adjusted mobility-disability prevalence"
)
polygon(
  c(curve$acceleration_years, rev(curve$acceleration_years)),
  c(curve$ci_low_95, rev(curve$ci_high_95)),
  border = NA,
  col = gray(0.88)
)
lines(
  curve$acceleration_years,
  curve$adjusted_prevalence,
  lwd = 2
)
abline(v = 0, lty = 2)
mtext(
  "Survey-weighted logistic restricted cubic spline; pointwise 95% CI",
  side = 3,
  line = 0.3,
  cex = 0.8
)
dev.off()

cat("\nAgeLens V2 Stage 2 diagnostic review completed.\n")
cat(sprintf(
  "Primary modified-Poisson fitted values above one: %d\n",
  bound_audit$predicted_above_one_n[
    bound_audit$outcome == "mobility_disability"
  ]
))
cat(sprintf(
  "Prespecified quasi-Poisson nonlinearity p: %.8g\n",
  nonlinearity_review$prespecified_quasipoisson_nonlinearity_p
))
cat(sprintf(
  "Bounded logistic-spline nonlinearity p: %.8g\n",
  spline_nonlinearity_p
))
cat("The prespecified linear primary result was retained but not released.\n")
cat(sprintf("Figure: %s\n", figure_path))
