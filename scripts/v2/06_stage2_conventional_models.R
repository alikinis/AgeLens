NOTEBOOK_BUILD_R <- "AgeLens-V2-Stage2-20260723"
cat(sprintf("R script build: %s\n", NOTEBOOK_BUILD_R))

options(error = function() {
  error_log <- file.path(
    if (exists("log_dir")) log_dir else getwd(),
    "06_stage2_r_error.txt"
  )
  sink(error_log, append = TRUE, type = "output")
  cat("\n--- Stage 2 R error ---\n")
  cat("Time: ", format(Sys.time(), tz = "UTC", usetz = TRUE), "\n", sep = "")
  traceback(30)
  sink(type = "output")
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
  stop("Expected 3 arguments: input CSV, output table directory, log directory.")
}

input_path <- normalizePath(args[[1]], mustWork = TRUE)
output_dir <- normalizePath(args[[2]], mustWork = FALSE)
log_dir <- normalizePath(args[[3]], mustWork = FALSE)
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("survey", quietly = TRUE)) {
  stop(
    "Missing R package 'survey'. Install it with: ",
    "install.packages('survey', repos='https://cloud.r-project.org')"
  )
}

suppressPackageStartupMessages({
  library(survey)
  library(splines)
})
options(survey.lonely.psu = "fail")

required_columns <- c(
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

dat <- read.csv(
  input_path,
  stringsAsFactors = FALSE,
  check.names = FALSE,
  na.strings = c("", "NA")
)
missing_columns <- setdiff(required_columns, names(dat))
if (length(missing_columns) > 0) {
  stop("Missing input columns: ", paste(missing_columns, collapse = ", "))
}
if (nrow(dat) != 5223) stop("Stage 2 input must contain exactly 5,223 rows.")
if (anyDuplicated(dat[c("NHANES_CYCLE", "SEQN")])) {
  stop("Duplicate NHANES_CYCLE + SEQN rows found.")
}
if (any(!is.finite(dat$WTSAF4YR)) || any(dat$WTSAF4YR <= 0)) {
  stop("Invalid WTSAF4YR values.")
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

binary_columns <- c(
  "mobility_disability",
  "any_disability_six",
  "fair_poor_general_health",
  "phq9_ge10"
)
for (column in binary_columns) {
  observed <- dat[[column]][!is.na(dat[[column]])]
  if (any(!observed %in% c(0, 1))) {
    stop(column, " contains values outside 0/1/missing.")
  }
}

domain_columns <- paste0("domain_", binary_columns)
for (column in domain_columns) {
  if (any(is.na(dat[[column]])) || any(!dat[[column]] %in% c(0, 1))) {
    stop(column, " must contain only 0/1 without missing values.")
  }
}

sex_levels <- c("Male", "Female")
race_levels <- c(
  "Non-Hispanic White",
  "Mexican American",
  "Other Hispanic",
  "Non-Hispanic Black",
  "Non-Hispanic Asian",
  "Other or multiracial"
)
cycle_levels <- c("2015_2016", "2017_2018")

dat$sex <- factor(dat$sex, levels = sex_levels)
dat$race_ethnicity <- factor(dat$race_ethnicity, levels = race_levels)
dat$NHANES_CYCLE <- factor(dat$NHANES_CYCLE, levels = cycle_levels)
dat$pooled_stratum <- factor(dat$pooled_stratum)
dat$pooled_psu <- factor(dat$pooled_psu)

primary_rows <- dat$domain_mobility_disability == 1
if (sum(primary_rows) != 4366) stop("Primary domain count changed.")
if (sum(dat$mobility_disability[primary_rows]) != 682) {
  stop("Primary positive outcome count changed.")
}
if (any(is.na(dat$sex[primary_rows]))) stop("Primary sex contains missing values.")
if (any(is.na(dat$race_ethnicity[primary_rows]))) {
  stop("Primary race/ethnicity contains missing values.")
}
if (any(is.na(dat$NHANES_CYCLE[primary_rows]))) {
  stop("Primary cycle contains missing values.")
}

# Frozen restricted cubic spline sensitivity for acceleration.
rcs_nonlinear_basis <- function(x, all_knots) {
  if (length(all_knots) < 4) stop("At least four knots are required.")
  if (is.unsorted(all_knots, strictly = TRUE)) stop("Knots must be increasing.")
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
  if (is.null(dim(basis))) basis <- matrix(basis, ncol = 1)
  colnames(basis) <- paste0("accel_nonlinear_", seq_len(ncol(basis)))
  basis
}

acceleration_knots <- c(-30, -10, 0, 10, 40)
nonlinear_basis <- rcs_nonlinear_basis(
  dat$phenoage_acceleration_years,
  acceleration_knots
)
for (index in seq_len(ncol(nonlinear_basis))) {
  dat[[colnames(nonlinear_basis)[[index]]]] <- nonlinear_basis[, index]
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

model_formulas <- list(
  model_a = as.formula(
    paste("mobility_disability ~", age_term)
  ),
  model_b = as.formula(
    paste(
      "mobility_disability ~",
      age_term,
      "+ sex + race_ethnicity + NHANES_CYCLE"
    )
  ),
  model_c = as.formula(
    paste(
      "mobility_disability ~",
      age_term,
      "+ sex + race_ethnicity + NHANES_CYCLE",
      "+ phenoage_acceleration_per_5_years"
    )
  )
)

fit_with_warnings <- function(formula, design, family) {
  captured <- character(0)
  model <- withCallingHandlers(
    svyglm(formula, design = design, family = family),
    warning = function(warning_condition) {
      captured <<- c(captured, conditionMessage(warning_condition))
      invokeRestart("muffleWarning")
    }
  )
  list(model = model, warnings = unique(captured))
}

extract_term <- function(model, term, design_df) {
  model_summary <- summary(model, df.resid = design_df)
  coefficient_table <- model_summary$coefficients
  if (!term %in% rownames(coefficient_table)) {
    stop("Term not found in model: ", term)
  }
  estimate <- unname(coefficient_table[term, "Estimate"])
  standard_error <- unname(coefficient_table[term, "Std. Error"])
  statistic <- estimate / standard_error
  p_value <- 2 * pt(abs(statistic), df = design_df, lower.tail = FALSE)
  critical_value <- qt(0.975, df = design_df)
  c(
    estimate = estimate,
    standard_error = standard_error,
    statistic = statistic,
    p_value = p_value,
    ci_low = estimate - critical_value * standard_error,
    ci_high = estimate + critical_value * standard_error
  )
}

model_diagnostic <- function(
  model,
  model_name,
  outcome,
  domain_data,
  design_df,
  captured_warnings
) {
  predictions <- as.numeric(predict(model, type = "response"))
  covariance <- vcov(model)
  data.frame(
    model = model_name,
    outcome = outcome,
    n = nrow(domain_data),
    positive_n = sum(domain_data[[outcome]] == 1),
    negative_n = sum(domain_data[[outcome]] == 0),
    design_df = design_df,
    model_residual_df = model$df.residual,
    converged = isTRUE(model$converged),
    finite_coefficients = all(is.finite(coef(model))),
    finite_covariance = all(is.finite(covariance)),
    predicted_min = min(predictions),
    predicted_max = max(predictions),
    predicted_above_one_n = sum(predictions > 1),
    warning_n = length(captured_warnings),
    warnings = paste(captured_warnings, collapse = " | "),
    stringsAsFactors = FALSE
  )
}

primary_design <- subset(full_design, domain_mobility_disability == 1)
primary_data <- dat[primary_rows, , drop = FALSE]
primary_design_df <- degf(primary_design)
if (primary_design_df != 30) {
  stop("Primary design degrees of freedom changed: ", primary_design_df)
}

primary_fits <- lapply(model_formulas, function(formula) {
  fit_with_warnings(
    formula,
    primary_design,
    quasipoisson(link = "log")
  )
})

primary_diagnostics <- do.call(
  rbind,
  lapply(names(primary_fits), function(model_name) {
    model_diagnostic(
      primary_fits[[model_name]]$model,
      model_name,
      "mobility_disability",
      primary_data,
      primary_design_df,
      primary_fits[[model_name]]$warnings
    )
  })
)

primary_model <- primary_fits$model_c$model
primary_effect <- extract_term(
  primary_model,
  "phenoage_acceleration_per_5_years",
  primary_design_df
)
primary_result <- data.frame(
  outcome = "mobility_disability",
  outcome_label = "Serious difficulty walking or climbing stairs",
  model = "model_c",
  effect_scale = "per 5-year higher Phenotypic Age acceleration",
  n = nrow(primary_data),
  positive_n = sum(primary_data$mobility_disability == 1),
  design_df = primary_design_df,
  log_prevalence_ratio = primary_effect[["estimate"]],
  standard_error = primary_effect[["standard_error"]],
  t_statistic = primary_effect[["statistic"]],
  prevalence_ratio = exp(primary_effect[["estimate"]]),
  ci_low_95 = exp(primary_effect[["ci_low"]]),
  ci_high_95 = exp(primary_effect[["ci_high"]]),
  p_value = primary_effect[["p_value"]],
  interpretation = "associational_not_causal",
  result_status = "provisional_pending_stage2_review",
  stringsAsFactors = FALSE
)

hierarchy_rows <- do.call(
  rbind,
  lapply(names(primary_fits), function(model_name) {
    model <- primary_fits[[model_name]]$model
    predictions <- as.numeric(predict(model, type = "response"))
    data.frame(
      outcome = "mobility_disability",
      model = model_name,
      formula = paste(deparse(formula(model)), collapse = " "),
      n = nrow(primary_data),
      positive_n = sum(primary_data$mobility_disability == 1),
      design_df = primary_design_df,
      coefficient_n = length(coef(model)),
      predicted_mean = weighted.mean(
        predictions,
        primary_data$WTSAF4YR
      ),
      predicted_min = min(predictions),
      predicted_max = max(predictions),
      stringsAsFactors = FALSE
    )
  })
)

secondary_outcomes <- c(
  "any_disability_six",
  "fair_poor_general_health",
  "phq9_ge10"
)
secondary_labels <- c(
  any_disability_six = "Any six-domain disability",
  fair_poor_general_health = "Fair or poor general health",
  phq9_ge10 = "PHQ-9 score at least 10"
)
expected_secondary_counts <- list(
  any_disability_six = c(n = 4358, positive = 1247),
  fair_poor_general_health = c(n = 4076, positive = 1025),
  phq9_ge10 = c(n = 4021, positive = 345)
)

secondary_designs <- list(
  any_disability_six = subset(
    full_design,
    domain_any_disability_six == 1
  ),
  fair_poor_general_health = subset(
    full_design,
    domain_fair_poor_general_health == 1
  ),
  phq9_ge10 = subset(
    full_design,
    domain_phq9_ge10 == 1
  )
)

secondary_results <- list()
secondary_diagnostics <- list()
for (outcome in secondary_outcomes) {
  domain_column <- paste0("domain_", outcome)
  domain_rows <- dat[[domain_column]] == 1
  domain_data <- dat[domain_rows, , drop = FALSE]
  expected <- expected_secondary_counts[[outcome]]
  if (nrow(domain_data) != expected[["n"]]) {
    stop(outcome, " domain count changed.")
  }
  if (sum(domain_data[[outcome]]) != expected[["positive"]]) {
    stop(outcome, " positive count changed.")
  }

  outcome_design <- secondary_designs[[outcome]]
  outcome_design_df <- degf(outcome_design)
  formula_c <- as.formula(
    paste(
      outcome,
      "~",
      age_term,
      "+ sex + race_ethnicity + NHANES_CYCLE",
      "+ phenoage_acceleration_per_5_years"
    )
  )
  fitted <- fit_with_warnings(
    formula_c,
    outcome_design,
    quasipoisson(link = "log")
  )
  effect <- extract_term(
    fitted$model,
    "phenoage_acceleration_per_5_years",
    outcome_design_df
  )
  secondary_results[[outcome]] <- data.frame(
    outcome = outcome,
    outcome_label = secondary_labels[[outcome]],
    model = "model_c",
    n = nrow(domain_data),
    positive_n = sum(domain_data[[outcome]] == 1),
    design_df = outcome_design_df,
    log_prevalence_ratio = effect[["estimate"]],
    standard_error = effect[["standard_error"]],
    t_statistic = effect[["statistic"]],
    prevalence_ratio = exp(effect[["estimate"]]),
    ci_low_95 = exp(effect[["ci_low"]]),
    ci_high_95 = exp(effect[["ci_high"]]),
    p_value_raw = effect[["p_value"]],
    stringsAsFactors = FALSE
  )
  secondary_diagnostics[[outcome]] <- model_diagnostic(
    fitted$model,
    "model_c",
    outcome,
    domain_data,
    outcome_design_df,
    fitted$warnings
  )
}
secondary_result <- do.call(rbind, secondary_results)
secondary_result$p_value_holm <- p.adjust(
  secondary_result$p_value_raw,
  method = "holm"
)
secondary_result$result_status <- "secondary_provisional_pending_stage2_review"

secondary_diagnostics_frame <- do.call(rbind, secondary_diagnostics)
all_diagnostics <- rbind(primary_diagnostics, secondary_diagnostics_frame)

# Frozen linearity sensitivity: retain linear acceleration and test three
# restricted-cubic-spline nonlinear terms jointly.
linearity_formula <- as.formula(
  paste(
    "mobility_disability ~",
    age_term,
    "+ sex + race_ethnicity + NHANES_CYCLE",
    "+ phenoage_acceleration_per_5_years",
    "+ accel_nonlinear_1 + accel_nonlinear_2 + accel_nonlinear_3"
  )
)
linearity_fit <- fit_with_warnings(
  linearity_formula,
  primary_design,
  quasipoisson(link = "log")
)
linearity_test <- regTermTest(
  linearity_fit$model,
  ~accel_nonlinear_1 + accel_nonlinear_2 + accel_nonlinear_3,
  method = "Wald"
)

extract_regterm_value <- function(object, candidates, default = NA_real_) {
  for (candidate in candidates) {
    if (!is.null(object[[candidate]])) {
      value <- suppressWarnings(as.numeric(object[[candidate]]))
      if (length(value) > 0 && is.finite(value[[1]])) return(value[[1]])
    }
  }
  default
}

linearity_p <- extract_regterm_value(
  linearity_test,
  c("p", "p.value", "pval")
)
if (!is.finite(linearity_p)) {
  printed <- paste(capture.output(print(linearity_test)), collapse = " ")
  match <- regexpr("p[[:space:]]*=[[:space:]]*[-+0-9.eE]+", printed)
  if (match[[1]] > 0) {
    token <- regmatches(printed, match)
    linearity_p <- as.numeric(sub(".*=", "", token))
  }
}
if (!is.finite(linearity_p) || linearity_p < 0 || linearity_p > 1) {
  stop("Could not extract a valid nonlinearity p-value from regTermTest.")
}
linearity_result <- data.frame(
  outcome = "mobility_disability",
  sensitivity = "fixed restricted cubic spline acceleration",
  all_knots_years = "-30|-10|0|10|40",
  nonlinear_df = 3,
  wald_statistic = extract_regterm_value(
    linearity_test,
    c("Ftest", "chisq", "statistic")
  ),
  numerator_df = extract_regterm_value(
    linearity_test,
    c("df", "ndf")
  ),
  denominator_df = extract_regterm_value(
    linearity_test,
    c("ddf")
  ),
  p_value_nonlinearity = linearity_p,
  primary_linear_model_replaced = FALSE,
  warning_n = length(linearity_fit$warnings),
  warnings = paste(linearity_fit$warnings, collapse = " | "),
  stringsAsFactors = FALSE
)

runtime_versions <- data.frame(
  component = c(
    "R",
    "survey",
    "splines",
    "platform",
    "script_build"
  ),
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
    "Primary prevalence ratio is finite and positive",
    "Primary confidence interval is finite and positive",
    "Primary p-value is within [0,1]",
    "All conventional models converged",
    "All conventional model coefficients are finite",
    "All conventional covariance matrices are finite",
    "Secondary Holm p-values are within [0,1]",
    "Linearity sensitivity p-value is within [0,1]",
    "No explainable model was fitted",
    "No participant-level public output was written"
  ),
  pass = c(
    primary_result$n[[1]] == 4366,
    primary_result$positive_n[[1]] == 682,
    is.finite(primary_result$prevalence_ratio[[1]]) &&
      primary_result$prevalence_ratio[[1]] > 0,
    all(is.finite(c(primary_result$ci_low_95[[1]], primary_result$ci_high_95[[1]]))) &&
      primary_result$ci_low_95[[1]] > 0 &&
      primary_result$ci_high_95[[1]] > 0,
    is.finite(primary_result$p_value[[1]]) &&
      primary_result$p_value[[1]] >= 0 &&
      primary_result$p_value[[1]] <= 1,
    all(all_diagnostics$converged),
    all(all_diagnostics$finite_coefficients),
    all(all_diagnostics$finite_covariance),
    all(is.finite(secondary_result$p_value_holm)) &&
      all(secondary_result$p_value_holm >= 0) &&
      all(secondary_result$p_value_holm <= 1),
    is.finite(linearity_p) && linearity_p >= 0 && linearity_p <= 1,
    TRUE,
    TRUE
  ),
  observed = c(
    primary_result$n[[1]],
    primary_result$positive_n[[1]],
    primary_result$prevalence_ratio[[1]],
    paste(primary_result$ci_low_95[[1]], primary_result$ci_high_95[[1]], sep = " | "),
    primary_result$p_value[[1]],
    all(all_diagnostics$converged),
    all(all_diagnostics$finite_coefficients),
    all(all_diagnostics$finite_covariance),
    paste(secondary_result$p_value_holm, collapse = " | "),
    linearity_p,
    "not authorized",
    "aggregate CSV files only"
  ),
  stringsAsFactors = FALSE
)
if (!all(release_checks$pass)) {
  failed <- release_checks$check[!release_checks$pass]
  stop("Stage 2 release checks failed: ", paste(failed, collapse = "; "))
}

write.csv(
  primary_result,
  file.path(output_dir, "06_stage2_primary_result.csv"),
  row.names = FALSE
)
write.csv(
  hierarchy_rows,
  file.path(output_dir, "06_stage2_primary_model_hierarchy.csv"),
  row.names = FALSE
)
write.csv(
  secondary_result,
  file.path(output_dir, "06_stage2_secondary_results.csv"),
  row.names = FALSE
)
write.csv(
  all_diagnostics,
  file.path(output_dir, "06_stage2_model_diagnostics.csv"),
  row.names = FALSE
)
write.csv(
  linearity_result,
  file.path(output_dir, "06_stage2_linearity_sensitivity.csv"),
  row.names = FALSE
)
write.csv(
  runtime_versions,
  file.path(output_dir, "06_stage2_runtime_versions.csv"),
  row.names = FALSE
)
write.csv(
  release_checks,
  file.path(output_dir, "06_stage2_release_checks.csv"),
  row.names = FALSE
)

cat("\nAgeLens V2 Stage 2 conventional models completed.\n")
cat(sprintf("Primary n: %d\n", primary_result$n[[1]]))
cat(sprintf("Primary positive n: %d\n", primary_result$positive_n[[1]]))
cat(sprintf(
  "Adjusted prevalence ratio per 5-year higher acceleration: %.6f\n",
  primary_result$prevalence_ratio[[1]]
))
cat(sprintf(
  "95%% CI: %.6f to %.6f\n",
  primary_result$ci_low_95[[1]],
  primary_result$ci_high_95[[1]]
))
cat(sprintf("p-value: %.8g\n", primary_result$p_value[[1]]))
cat(sprintf("Nonlinearity p-value: %.8g\n", linearity_p))
cat("Result status: provisional pending Stage 2 review.\n")
