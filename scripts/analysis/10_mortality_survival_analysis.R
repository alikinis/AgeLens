NOTEBOOK_BUILD_R <- "10-v8-r-string-concat-fixed"
cat(sprintf("R script build: %s\n", NOTEBOOK_BUILD_R))

args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 6) {
  stop("Expected 6 command-line arguments.")
}

input_path <- args[[1]]
coefficients_path <- args[[2]]
diagnostics_path <- args[[3]]
ph_path <- args[[4]]
reconciliation_path <- args[[5]]
versions_path <- args[[6]]

required_packages <- c("survey", "survival")

missing_packages <- required_packages[
  !vapply(
    required_packages,
    requireNamespace,
    logical(1),
    quietly = TRUE
  )
]

if (length(missing_packages) > 0) {
  stop(
    paste0(
      "Missing required R packages: ",
      paste(missing_packages, collapse = ", "),
      ". Install with install.packages(c(",
      paste(
        sprintf('"%s"', missing_packages),
        collapse = ", "
      ),
      "))"
    )
  )
}

suppressPackageStartupMessages({
  library(survey)
  library(survival)
})

options(survey.lonely.psu = "fail")

df <- read.csv(
  input_path,
  stringsAsFactors = FALSE,
  check.names = FALSE
)

required_columns <- c(
  "SEQN",
  "NHANES_CYCLE",
  "chronological_age_years",
  "RIAGENDR",
  "RIDRETH3",
  "WTSAF4YR",
  "pooled_stratum",
  "pooled_psu",
  "phenoage_acceleration_per_5_years",
  "phenoage_acceleration_per_sd",
  "sensitivity_erratum_acceleration_per_5_years",
  "sensitivity_creatinine_plus_0_11_acceleration_per_5_years",
  "sensitivity_creatinine_plus_0_17_acceleration_per_5_years",
  "sensitivity_creatinine_plus_0_23_acceleration_per_5_years",
  "mortality_event",
  "followup_months",
  "no_topcode_sensitivity_eligible",
  "early_death_exclusion_eligible"
)

missing_columns <- setdiff(
  required_columns,
  names(df)
)

if (length(missing_columns) > 0) {
  stop(
    paste(
      "R model input is missing required columns:",
      paste(missing_columns, collapse = ", ")
    )
  )
}

numeric_columns <- c(
  "chronological_age_years",
  "RIAGENDR",
  "RIDRETH3",
  "WTSAF4YR",
  "phenoage_acceleration_per_5_years",
  "phenoage_acceleration_per_sd",
  "sensitivity_erratum_acceleration_per_5_years",
  "sensitivity_creatinine_plus_0_11_acceleration_per_5_years",
  "sensitivity_creatinine_plus_0_17_acceleration_per_5_years",
  "sensitivity_creatinine_plus_0_23_acceleration_per_5_years",
  "mortality_event",
  "followup_months"
)

for (column in numeric_columns) {
  df[[column]] <- as.numeric(df[[column]])
}

as_logical_safe <- function(x) {
  if (is.logical(x)) {
    x[is.na(x)] <- FALSE
    return(x)
  }

  text <- toupper(trimws(as.character(x)))
  result <- text %in% c(
    "TRUE",
    "T",
    "1",
    "YES",
    "Y"
  )
  result[is.na(result)] <- FALSE
  result
}

df$no_topcode_sensitivity_eligible <- as_logical_safe(
  df$no_topcode_sensitivity_eligible
)
df$early_death_exclusion_eligible <- as_logical_safe(
  df$early_death_exclusion_eligible
)

df$sex_factor <- factor(
  df$RIAGENDR,
  levels = sort(unique(df$RIAGENDR))
)
df$race_factor <- factor(
  df$RIDRETH3,
  levels = sort(unique(df$RIDRETH3))
)
df$cycle_factor <- factor(
  df$NHANES_CYCLE,
  levels = sort(unique(df$NHANES_CYCLE))
)
df$pooled_stratum <- factor(df$pooled_stratum)
df$pooled_psu <- factor(df$pooled_psu)

# PH diagnostics use a separate weighted Cox fit when
# cox.zph cannot operate directly on svycoxph. Normalizing
# weights preserves coefficients while avoiding numerical
# dependence on the raw NHANES weight magnitude.
df$ph_weight <- df$WTSAF4YR / mean(df$WTSAF4YR)

if (any(!is.finite(df$WTSAF4YR)) || any(df$WTSAF4YR <= 0)) {
  stop("R model input contains invalid survey weights.")
}

if (
  any(!is.finite(df$followup_months)) ||
  any(df$followup_months <= 0)
) {
  stop("R model input contains invalid follow-up.")
}

if (!all(df$mortality_event %in% c(0, 1))) {
  stop("R model input contains a non-binary event.")
}

full_design <- svydesign(
  ids = ~pooled_psu,
  strata = ~pooled_stratum,
  weights = ~WTSAF4YR,
  nest = TRUE,
  data = df
)

model_specs <- data.frame(
  model = c(
    "canonical_exposure_only",
    "canonical_primary_adjusted",
    "canonical_adjusted_per_sd",
    "sensitivity_no_topcode",
    "sensitivity_erratum",
    "sensitivity_creatinine_plus_0_11",
    "sensitivity_creatinine_plus_0_17",
    "sensitivity_creatinine_plus_0_23",
    "sensitivity_exclude_early_deaths"
  ),
  sample = c(
    "canonical_full",
    "canonical_full",
    "canonical_full",
    "no_topcode",
    "canonical_full",
    "canonical_full",
    "canonical_full",
    "canonical_full",
    "exclude_early_deaths"
  ),
  exposure = c(
    "phenoage_acceleration_per_5_years",
    "phenoage_acceleration_per_5_years",
    "phenoage_acceleration_per_sd",
    "phenoage_acceleration_per_5_years",
    "sensitivity_erratum_acceleration_per_5_years",
    "sensitivity_creatinine_plus_0_11_acceleration_per_5_years",
    "sensitivity_creatinine_plus_0_17_acceleration_per_5_years",
    "sensitivity_creatinine_plus_0_23_acceleration_per_5_years",
    "phenoage_acceleration_per_5_years"
  ),
  adjusted = c(
    FALSE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE
  ),
  stringsAsFactors = FALSE
)

make_subdesign <- function(sample_name) {
  if (sample_name == "canonical_full") {
    return(full_design)
  }

  if (sample_name == "no_topcode") {
    return(
      subset(
        full_design,
        no_topcode_sensitivity_eligible
      )
    )
  }

  if (sample_name == "exclude_early_deaths") {
    return(
      subset(
        full_design,
        early_death_exclusion_eligible
      )
    )
  }

  stop(paste("Unknown sample:", sample_name))
}

make_formula <- function(exposure, adjusted) {
  terms <- exposure

  if (adjusted) {
    terms <- c(
      terms,
      "chronological_age_years",
      "sex_factor",
      "race_factor",
      "cycle_factor"
    )
  }

  as.formula(
    paste(
      "Surv(followup_months, mortality_event) ~",
      paste(terms, collapse = " + ")
    )
  )
}

extract_coefficients <- function(
  fit,
  model_name,
  sample_name,
  exposure_name,
  adjusted
) {
  beta <- coef(fit)
  covariance <- vcov(fit)
  standard_error <- sqrt(diag(covariance))
  z_value <- beta / standard_error
  p_value <- 2 * pnorm(
    abs(z_value),
    lower.tail = FALSE
  )

  data.frame(
    model = model_name,
    sample = sample_name,
    exposure = exposure_name,
    adjusted = adjusted,
    term = names(beta),
    coefficient = as.numeric(beta),
    standard_error = as.numeric(standard_error),
    z = as.numeric(z_value),
    p_value = as.numeric(p_value),
    hazard_ratio = exp(as.numeric(beta)),
    ci_low_95 = exp(
      as.numeric(beta) - 1.96 * as.numeric(standard_error)
    ),
    ci_high_95 = exp(
      as.numeric(beta) + 1.96 * as.numeric(standard_error)
    ),
    stringsAsFactors = FALSE
  )
}

fit_one_model <- function(spec_row) {
  model_name <- spec_row$model[[1]]
  sample_name <- spec_row$sample[[1]]
  exposure_name <- spec_row$exposure[[1]]
  adjusted <- spec_row$adjusted[[1]]

  design_object <- make_subdesign(sample_name)
  analysis_data <- droplevels(design_object$variables)
  formula_object <- make_formula(
    exposure_name,
    adjusted
  )
  warning_messages <- character(0)

  if (model_name == "canonical_exposure_only") {
    cat("Exact svycoxph call: svycoxph(formula_object, design = design_object)\n")
  }

  fit <- tryCatch(
    withCallingHandlers(
      svycoxph(
        formula_object,
        design = design_object
      ),
      warning = function(warning_condition) {
        warning_messages <<- c(
          warning_messages,
          conditionMessage(warning_condition)
        )
        invokeRestart("muffleWarning")
      }
    ),
    error = function(error_condition) {
      structure(
        list(
          message = conditionMessage(error_condition)
        ),
        class = "agelens_model_error"
      )
    }
  )

  psu_groups <- split(
    as.character(analysis_data$pooled_psu),
    as.character(analysis_data$pooled_stratum),
    drop = TRUE
  )
  psu_by_stratum <- vapply(
    psu_groups,
    function(values) length(unique(values)),
    integer(1)
  )

  if (inherits(fit, "agelens_model_error")) {
    diagnostics <- data.frame(
      model = model_name,
      sample = sample_name,
      exposure = exposure_name,
      adjusted = adjusted,
      n = nrow(analysis_data),
      events = sum(analysis_data$mortality_event),
      weighted_population_sum = sum(
        analysis_data$WTSAF4YR
      ),
      strata = length(psu_groups),
      psus = sum(psu_by_stratum),
      minimum_psus_per_stratum = min(psu_by_stratum),
      converged = FALSE,
      finite_coefficients = FALSE,
      finite_covariance = FALSE,
      fatal_warning = FALSE,
      warning_messages = paste(
        warning_messages,
        collapse = " | "
      ),
      error_message = fit$message,
      formula = paste(
        deparse(formula_object),
        collapse = ""
      ),
      stringsAsFactors = FALSE
    )

    return(
      list(
        fit = NULL,
        coefficients = NULL,
        diagnostics = diagnostics
      )
    )
  }

  beta <- coef(fit)
  covariance <- vcov(fit)

  fatal_warning <- any(
    grepl(
      "converg|infinite|singular|NaN|not positive definite",
      warning_messages,
      ignore.case = TRUE
    )
  )

  diagnostics <- data.frame(
    model = model_name,
    sample = sample_name,
    exposure = exposure_name,
    adjusted = adjusted,
    n = nrow(analysis_data),
    events = sum(analysis_data$mortality_event),
    weighted_population_sum = sum(
      analysis_data$WTSAF4YR
    ),
    strata = length(psu_groups),
    psus = sum(psu_by_stratum),
    minimum_psus_per_stratum = min(psu_by_stratum),
    converged = (
      all(is.finite(beta)) &&
      all(is.finite(covariance))
    ),
    finite_coefficients = all(is.finite(beta)),
    finite_covariance = all(is.finite(covariance)),
    fatal_warning = fatal_warning,
    warning_messages = paste(
      warning_messages,
      collapse = " | "
    ),
    error_message = "",
    formula = paste(
      deparse(formula_object),
      collapse = ""
    ),
    stringsAsFactors = FALSE
  )

  coefficients <- extract_coefficients(
    fit,
    model_name,
    sample_name,
    exposure_name,
    adjusted
  )

  list(
    fit = fit,
    coefficients = coefficients,
    diagnostics = diagnostics
  )
}

model_results <- vector(
  "list",
  nrow(model_specs)
)
names(model_results) <- model_specs$model

for (index in seq_len(nrow(model_specs))) {
  specification <- model_specs[index, , drop = FALSE]
  result <- fit_one_model(specification)
  model_results[[specification$model[[1]]]] <- result

  if (is.null(result$fit)) {
    stop(
      paste(
        "Model failed:",
        specification$model[[1]],
        result$diagnostics$error_message[[1]]
      )
    )
  }
}

coefficient_table <- do.call(
  rbind,
  lapply(
    model_results,
    function(result) result$coefficients
  )
)
diagnostic_table <- do.call(
  rbind,
  lapply(
    model_results,
    function(result) result$diagnostics
  )
)

primary_fit <- model_results[["canonical_primary_adjusted"]]$fit

ph_method <- "cox.zph_on_svycoxph"
ph_error <- ""
ph_result <- tryCatch(
  cox.zph(
    primary_fit,
    transform = "log",
    terms = TRUE,
    singledf = TRUE
  ),
  error = function(error_condition) {
    ph_error <<- conditionMessage(error_condition)
    NULL
  }
)

if (is.null(ph_result)) {
  ph_method <- "cox.zph_on_weighted_cluster_robust_coxph"
  primary_formula <- make_formula(
    "phenoage_acceleration_per_5_years",
    TRUE
  )

  fallback_fit <- coxph(
    primary_formula,
    data = df,
    weights = ph_weight,
    cluster = pooled_psu,
    robust = TRUE,
    ties = "efron",
    x = TRUE,
    model = TRUE
  )

  ph_result <- cox.zph(
    fallback_fit,
    transform = "log",
    terms = TRUE,
    singledf = TRUE
  )
}

ph_table_raw <- as.data.frame(ph_result$table)
ph_table_raw$term <- rownames(ph_table_raw)
rownames(ph_table_raw) <- NULL

chisq_column <- grep(
  "chisq",
  names(ph_table_raw),
  ignore.case = TRUE,
  value = TRUE
)[1]
p_column <- grep(
  "^p$|pvalue|p.value",
  names(ph_table_raw),
  ignore.case = TRUE,
  value = TRUE
)[1]

if (is.na(chisq_column) || is.na(p_column)) {
  stop(
    paste0(
      "Could not identify proportional-hazards ",
      "diagnostic columns."
    )
  )
}

ph_table <- data.frame(
  method = ph_method,
  term = ph_table_raw$term,
  chi_square = ph_table_raw[[chisq_column]],
  p_value = ph_table_raw[[p_column]],
  fallback_reason = ph_error,
  stringsAsFactors = FALSE
)

sample_names <- c(
  "canonical_full",
  "no_topcode",
  "exclude_early_deaths"
)

reconciliation_rows <- lapply(
  sample_names,
  function(sample_name) {
    design_object <- make_subdesign(sample_name)
    analysis_data <- droplevels(design_object$variables)
    psu_groups <- split(
      as.character(analysis_data$pooled_psu),
      as.character(analysis_data$pooled_stratum),
      drop = TRUE
    )
    psu_by_stratum <- vapply(
      psu_groups,
      function(values) length(unique(values)),
      integer(1)
    )

    data.frame(
      sample = sample_name,
      n = nrow(analysis_data),
      events = sum(analysis_data$mortality_event),
      weighted_population_sum = sum(
        analysis_data$WTSAF4YR
      ),
      strata = length(psu_groups),
      psus = sum(psu_by_stratum),
      stringsAsFactors = FALSE
    )
  }
)

reconciliation_table <- do.call(
  rbind,
  reconciliation_rows
)

version_table <- data.frame(
  component = c(
    "R",
    "survey",
    "survival"
  ),
  version = c(
    paste(
      R.version$major,
      R.version$minor,
      sep = "."
    ),
    as.character(
      packageVersion("survey")
    ),
    as.character(
      packageVersion("survival")
    )
  ),
  stringsAsFactors = FALSE
)

write.csv(
  coefficient_table,
  coefficients_path,
  row.names = FALSE,
  na = ""
)
write.csv(
  diagnostic_table,
  diagnostics_path,
  row.names = FALSE,
  na = ""
)
write.csv(
  ph_table,
  ph_path,
  row.names = FALSE,
  na = ""
)
write.csv(
  reconciliation_table,
  reconciliation_path,
  row.names = FALSE,
  na = ""
)
write.csv(
  version_table,
  versions_path,
  row.names = FALSE,
  na = ""
)

cat(
  sprintf(
    "Models completed: %d/%d\n",
    nrow(model_specs),
    nrow(model_specs)
  )
)
cat(
  sprintf(
    "Primary cohort: n=%d, events=%d\n",
    nrow(df),
    sum(df$mortality_event)
  )
)
cat(
  sprintf(
    "PH diagnostic method: %s\n",
    ph_method
  )
)
