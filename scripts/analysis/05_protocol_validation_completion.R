args <- commandArgs(trailingOnly = TRUE)

project_root <- if (length(args) >= 1) {
  normalizePath(args[[1]], mustWork = TRUE)
} else {
  normalizePath(".", mustWork = TRUE)
}

if (!requireNamespace("survey", quietly = TRUE)) {
  stop(
    "The R package 'survey' is required. Install it with ",
    "install.packages('survey')."
  )
}

suppressPackageStartupMessages(library(survey))

options(
  survey.lonely.psu = "fail",
  warn = 1
)

input_path <- file.path(
  project_root,
  "results",
  "tables",
  "05_protocol_validation_input.csv"
)
table_dir <- file.path(project_root, "results", "tables")
log_dir <- file.path(project_root, "logs")

dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)

progress_log_path <- file.path(
  log_dir,
  "05_r_progress.log"
)
error_audit_path <- file.path(
  table_dir,
  "05_r_analysis_error_audit.csv"
)

log_step <- function(message) {
  line <- paste0(
    format(Sys.time(), tz = "UTC", usetz = TRUE),
    " | ",
    message
  )
  message(line)
  cat(
    line,
    "\n",
    file = progress_log_path,
    append = TRUE
  )
}

if (file.exists(progress_log_path)) {
  invisible(file.remove(progress_log_path))
}

log_step("Starting Validation Protocol Checks 3 and 4.")

if (!file.exists(input_path)) {
  stop("Validation input not found: ", input_path)
}

dat <- read.csv(
  input_path,
  stringsAsFactors = FALSE,
  check.names = FALSE
)

required_columns <- c(
  "SEQN",
  "NHANES_CYCLE",
  "age",
  "age_topcoded",
  "RIAGENDR",
  "RIDRETH3",
  "WTSAF4YR",
  "SDMVSTRA",
  "SDMVPSU",
  "bridge_complete_case",
  "prebridge_erratum",
  "prebridge_supplement",
  "harmonized_erratum",
  "harmonized_supplement",
  "LBXSAL",
  "LBXSCR",
  "LBXHSCRP",
  "LBXLYPCT",
  "LBXMCVSI",
  "LBXRDW",
  "LBXSAPSI",
  "LBXWBCSI"
)

missing_columns <- setdiff(required_columns, names(dat))

if (length(missing_columns) > 0) {
  stop(
    "Input is missing columns: ",
    paste(missing_columns, collapse = ", ")
  )
}

parse_binary_flag <- function(x, column_name) {
  if (is.logical(x)) {
    if (any(is.na(x))) {
      stop(column_name, " contains missing values.")
    }
    return(x)
  }

  if (is.numeric(x) || is.integer(x)) {
    if (any(is.na(x)) || any(!x %in% c(0, 1))) {
      stop(column_name, " must contain only 0/1 when numeric.")
    }
    return(x == 1)
  }

  normalized <- tolower(trimws(as.character(x)))
  result <- rep(NA, length(normalized))

  result[normalized %in% c(
    "true", "t", "1", "yes", "y"
  )] <- TRUE
  result[normalized %in% c(
    "false", "f", "0", "no", "n"
  )] <- FALSE

  if (any(is.na(result))) {
    stop(
      column_name,
      " contains unrecognized values: ",
      paste(
        unique(normalized[is.na(result)]),
        collapse = ", "
      )
    )
  }

  result
}

dat$age_topcoded <- parse_binary_flag(
  dat$age_topcoded,
  "age_topcoded"
)
dat$bridge_complete_case <- parse_binary_flag(
  dat$bridge_complete_case,
  "bridge_complete_case"
)

numeric_columns <- c(
  "age",
  "WTSAF4YR",
  "SDMVSTRA",
  "SDMVPSU",
  "prebridge_erratum",
  "prebridge_supplement",
  "harmonized_erratum",
  "harmonized_supplement",
  "LBXSAL",
  "LBXSCR",
  "LBXHSCRP",
  "LBXLYPCT",
  "LBXMCVSI",
  "LBXRDW",
  "LBXSAPSI",
  "LBXWBCSI"
)

for (column_name in numeric_columns) {
  dat[[column_name]] <- suppressWarnings(
    as.numeric(dat[[column_name]])
  )
}

if (
  any(is.na(dat$WTSAF4YR))
  || any(dat$WTSAF4YR <= 0)
) {
  stop(
    "WTSAF4YR must be present and positive for every row."
  )
}

dat$cycle_binary <- ifelse(
  dat$NHANES_CYCLE == "2017_2018",
  1,
  0
)

dat$age_group <- cut(
  dat$age,
  breaks = c(-Inf, 19, 39, 59, 79, Inf),
  labels = c("<20", "20-39", "40-59", "60-79", "80+"),
  right = TRUE
)

dat$sex <- factor(
  dat$RIAGENDR,
  levels = c(1, 2),
  labels = c("Male", "Female")
)

build_design <- function(frame, analysis_name) {
  frame <- frame[
    is.finite(frame$WTSAF4YR)
      & frame$WTSAF4YR > 0
      & !is.na(frame$SDMVSTRA)
      & !is.na(frame$SDMVPSU),
    ,
    drop = FALSE
  ]

  if (nrow(frame) == 0) {
    stop(analysis_name, ": no eligible rows.")
  }

  frame$design_stratum <- interaction(
    frame$NHANES_CYCLE,
    frame$SDMVSTRA,
    drop = TRUE
  )
  frame$design_psu <- interaction(
    frame$NHANES_CYCLE,
    frame$SDMVSTRA,
    frame$SDMVPSU,
    drop = TRUE
  )

  psu_counts <- aggregate(
    design_psu ~ design_stratum,
    data = unique(
      frame[c("design_stratum", "design_psu")]
    ),
    FUN = length
  )

  lonely <- psu_counts[
    psu_counts$design_psu < 2,
    ,
    drop = FALSE
  ]

  if (nrow(lonely) > 0) {
    stop(
      analysis_name,
      ": one or more strata contain fewer than two observed PSUs: ",
      paste(
        as.character(lonely$design_stratum),
        collapse = ", "
      ),
      ". No unapproved lonely-PSU correction was applied."
    )
  }

  svydesign(
    ids = ~design_psu,
    strata = ~design_stratum,
    weights = ~WTSAF4YR,
    nest = TRUE,
    data = frame
  )
}

safe_confint <- function(model, parameter_name) {
  result <- tryCatch(
    confint(model, parameter_name),
    error = function(e) NULL
  )

  if (is.null(result)) {
    return(c(NA_real_, NA_real_))
  }

  result <- as.matrix(result)

  if (nrow(result) < 1 || ncol(result) < 2) {
    return(c(NA_real_, NA_real_))
  }

  c(
    as.numeric(result[1, 1]),
    as.numeric(result[1, 2])
  )
}

extract_model_p <- function(model, parameter_name) {
  coefficient_table <- summary(model)$coefficients

  if (
    !parameter_name %in% rownames(coefficient_table)
  ) {
    return(NA_real_)
  }

  if ("Pr(>|t|)" %in% colnames(coefficient_table)) {
    return(
      as.numeric(
        coefficient_table[
          parameter_name,
          "Pr(>|t|)"
        ]
      )
    )
  }

  if ("Pr(>|z|)" %in% colnames(coefficient_table)) {
    return(
      as.numeric(
        coefficient_table[
          parameter_name,
          "Pr(>|z|)"
        ]
      )
    )
  }

  NA_real_
}

extract_cycle_effect <- function(
  design_object,
  outcome_name,
  stage_name,
  variant_name,
  sample_name
) {
  analysis_name <- paste(
    "Check 3",
    sample_name,
    stage_name,
    variant_name,
    sep = " | "
  )

  if (nrow(design_object$variables) == 0) {
    stop(analysis_name, ": no eligible rows.")
  }

  if (
    any(!is.finite(design_object$variables[[outcome_name]]))
    || any(!is.finite(design_object$variables$age))
  ) {
    stop(
      analysis_name,
      ": outcome or age contains non-finite values."
    )
  }

  age_formula <- as.formula(
    paste0(outcome_name, " ~ age")
  )

  age_model <- svyglm(
    age_formula,
    design = design_object
  )

  predicted_age_component <- as.numeric(
    predict(
      age_model,
      newdata = design_object$variables,
      type = "response"
    )
  )

  if (
    length(predicted_age_component)
    != nrow(design_object$variables)
  ) {
    stop(
      analysis_name,
      ": prediction vector length does not match design rows."
    )
  }

  acceleration <- (
    design_object$variables[[outcome_name]]
    - predicted_age_component
  )

  if (any(!is.finite(acceleration))) {
    stop(
      analysis_name,
      ": calculated PhenoAgeAccel contains non-finite values."
    )
  }

  design_with_accel <- design_object
  design_with_accel$variables$phenoage_accel <- (
    acceleration
  )

  cycle_model <- svyglm(
    phenoage_accel ~ cycle_binary,
    design = design_with_accel
  )

  coefficient_names <- names(coef(cycle_model))

  if (!"cycle_binary" %in% coefficient_names) {
    stop(
      analysis_name,
      ": cycle_binary coefficient is not estimable."
    )
  }

  estimate <- as.numeric(
    coef(cycle_model)["cycle_binary"]
  )
  covariance_matrix <- as.matrix(
    vcov(cycle_model)
  )
  covariance_diagonal <- diag(covariance_matrix)
  covariance_names <- names(covariance_diagonal)

  if (
    is.null(covariance_names)
    || !"cycle_binary" %in% covariance_names
  ) {
    stop(
      analysis_name,
      ": cycle_binary standard error is not estimable."
    )
  }

  standard_error <- sqrt(
    as.numeric(
      covariance_diagonal["cycle_binary"]
    )
  )
  confidence_interval <- safe_confint(
    cycle_model,
    "cycle_binary"
  )
  p_value <- extract_model_p(
    cycle_model,
    "cycle_binary"
  )

  pooled_variance_object <- svyvar(
    ~phenoage_accel,
    design_with_accel,
    na.rm = TRUE
  )
  pooled_variance_values <- as.numeric(
    pooled_variance_object
  )

  if (
    length(pooled_variance_values) < 1
    || !is.finite(pooled_variance_values[1])
  ) {
    stop(
      analysis_name,
      ": pooled PhenoAgeAccel variance is not estimable."
    )
  }

  pooled_variance <- pooled_variance_values[1]
  pooled_sd <- sqrt(max(pooled_variance, 0))

  cycle_2015_design <- subset(
    design_with_accel,
    NHANES_CYCLE == "2015_2016"
  )
  cycle_2017_design <- subset(
    design_with_accel,
    NHANES_CYCLE == "2017_2018"
  )

  mean_2015 <- as.numeric(
    coef(
      svymean(
        ~phenoage_accel,
        cycle_2015_design,
        na.rm = TRUE
      )
    )
  )
  mean_2017 <- as.numeric(
    coef(
      svymean(
        ~phenoage_accel,
        cycle_2017_design,
        na.rm = TRUE
      )
    )
  )

  data.frame(
    sample = sample_name,
    stage = stage_name,
    formula_variant = variant_name,
    n = nrow(design_object$variables),
    mean_accel_2015_2016 = mean_2015,
    mean_accel_2017_2018 = mean_2017,
    cycle_difference_2017_minus_2015 = estimate,
    taylor_se = standard_error,
    ci_low_95 = confidence_interval[1],
    ci_high_95 = confidence_interval[2],
    p_value = p_value,
    pooled_weighted_sd = pooled_sd,
    cohen_d_design_descriptive = ifelse(
      pooled_sd > 0,
      estimate / pooled_sd,
      NA_real_
    ),
    analysis_status = "OK",
    analysis_error = "",
    stringsAsFactors = FALSE
  )
}

error_rows <- list()
error_index <- 1

record_error <- function(
  component,
  analysis_name,
  error_message
) {
  error_rows[[error_index]] <<- data.frame(
    component = component,
    analysis = analysis_name,
    error = error_message,
    stringsAsFactors = FALSE
  )
  error_index <<- error_index + 1
}

outcome_definitions <- list(
  list(
    stage = "prebridge",
    variant = "erratum",
    column = "prebridge_erratum"
  ),
  list(
    stage = "prebridge",
    variant = "supplement",
    column = "prebridge_supplement"
  ),
  list(
    stage = "harmonized",
    variant = "erratum",
    column = "harmonized_erratum"
  ),
  list(
    stage = "harmonized",
    variant = "supplement",
    column = "harmonized_supplement"
  )
)

log_step("Starting Check 3.")

bridge_required_columns <- c(
  "age",
  "cycle_binary",
  "prebridge_erratum",
  "prebridge_supplement",
  "harmonized_erratum",
  "harmonized_supplement"
)

bridge_complete_mask <- dat$bridge_complete_case

for (column_name in bridge_required_columns) {
  bridge_complete_mask <- (
    bridge_complete_mask
    & is.finite(dat[[column_name]])
  )
}

bridge_frame <- dat[
  bridge_complete_mask,
  ,
  drop = FALSE
]

bridge_design <- build_design(
  bridge_frame,
  "Check 3 full bridge-comparison design"
)

sample_designs <- list(
  all_harmonized_complete_case = bridge_design,
  no_topcode = subset(
    bridge_design,
    !age_topcoded
  )
)

check3_rows <- list()
check3_index <- 1

for (sample_name in names(sample_designs)) {
  sample_design <- sample_designs[[sample_name]]

  for (definition in outcome_definitions) {
    analysis_name <- paste(
      sample_name,
      definition$stage,
      definition$variant,
      sep = " | "
    )

    result <- tryCatch(
      extract_cycle_effect(
        sample_design,
        definition$column,
        definition$stage,
        definition$variant,
        sample_name
      ),
      error = function(e) {
        record_error(
          "Check 3",
          analysis_name,
          conditionMessage(e)
        )

        data.frame(
          sample = sample_name,
          stage = definition$stage,
          formula_variant = definition$variant,
          n = nrow(sample_design$variables),
          mean_accel_2015_2016 = NA_real_,
          mean_accel_2017_2018 = NA_real_,
          cycle_difference_2017_minus_2015 = NA_real_,
          taylor_se = NA_real_,
          ci_low_95 = NA_real_,
          ci_high_95 = NA_real_,
          p_value = NA_real_,
          pooled_weighted_sd = NA_real_,
          cohen_d_design_descriptive = NA_real_,
          analysis_status = "ERROR",
          analysis_error = conditionMessage(e),
          stringsAsFactors = FALSE
        )
      }
    )

    check3_rows[[check3_index]] <- result
    check3_index <- check3_index + 1
  }
}

check3_results <- do.call(
  rbind,
  check3_rows
)

write.csv(
  check3_results,
  file.path(
    table_dir,
    "05_check3_bridging_effectiveness.csv"
  ),
  row.names = FALSE
)

log_step(
  paste0(
    "Check 3 completed; successful rows = ",
    sum(check3_results$analysis_status == "OK"),
    "/",
    nrow(check3_results),
    "."
  )
)

biomarker_columns <- c(
  albumin = "LBXSAL",
  creatinine = "LBXSCR",
  hscrp = "LBXHSCRP",
  lymphocyte_percent = "LBXLYPCT",
  mcv = "LBXMCVSI",
  rdw = "LBXRDW",
  alp = "LBXSAPSI",
  wbc = "LBXWBCSI"
)

safe_chisq_p <- function(formula, design) {
  tryCatch(
    as.numeric(
      svychisq(
        formula,
        design,
        statistic = "F"
      )$p.value
    ),
    error = function(e) NA_real_
  )
}

weighted_binary_summary <- function(
  design_object,
  indicator_name = "missing_indicator",
  analysis_name = "weighted binary summary"
) {
  required_variables <- c(
    indicator_name,
    "WTSAF4YR"
  )

  missing_variables <- setdiff(
    required_variables,
    names(design_object$variables)
  )

  if (length(missing_variables) > 0) {
    stop(
      analysis_name,
      ": required design variables are missing: ",
      paste(missing_variables, collapse = ", ")
    )
  }

  indicator <- as.numeric(
    design_object$variables[[indicator_name]]
  )
  raw_weights <- as.numeric(
    design_object$variables$WTSAF4YR
  )
  survey_weights <- as.numeric(
    weights(
      design_object,
      type = "sampling"
    )
  )

  lengths <- c(
    indicator = length(indicator),
    raw_weights = length(raw_weights),
    survey_weights = length(survey_weights)
  )

  if (length(unique(lengths)) != 1) {
    stop(
      analysis_name,
      ": indicator/raw-weight/survey-weight lengths differ: ",
      paste(
        names(lengths),
        lengths,
        sep = "=",
        collapse = ", "
      )
    )
  }

  active <- (
    is.finite(indicator)
    & is.finite(raw_weights)
    & raw_weights > 0
    & is.finite(survey_weights)
    & survey_weights > 0
  )

  if (!any(active)) {
    stop(
      analysis_name,
      ": no rows have a finite indicator and positive raw/survey weights."
    )
  }

  indicator_active <- indicator[active]
  raw_active <- raw_weights[active]
  survey_active <- survey_weights[active]

  if (any(!indicator_active %in% c(0, 1))) {
    stop(
      analysis_name,
      ": indicator must contain only 0/1."
    )
  }

  raw_estimate <- sum(
    raw_active * indicator_active
  ) / sum(raw_active)

  survey_weight_estimate <- sum(
    survey_active * indicator_active
  ) / sum(survey_active)

  ratio_design <- design_object
  ratio_design$variables$ratio_denominator <- 1

  ratio_object <- svyratio(
    as.formula(
      paste0("~", indicator_name)
    ),
    ~ratio_denominator,
    ratio_design,
    na.rm = TRUE
  )

  ratio_estimate <- as.numeric(
    coef(ratio_object)
  )
  ratio_se <- as.numeric(
    SE(ratio_object)
  )

  if (
    length(ratio_estimate) != 1
    || !is.finite(ratio_estimate)
  ) {
    stop(
      analysis_name,
      ": survey ratio estimate is not finite."
    )
  }

  if (
    length(ratio_se) != 1
    || !is.finite(ratio_se)
  ) {
    stop(
      analysis_name,
      ": survey ratio standard error is not finite."
    )
  }

  estimate_differences <- c(
    raw_minus_survey_weight = (
      raw_estimate - survey_weight_estimate
    ),
    raw_minus_svyratio = (
      raw_estimate - ratio_estimate
    ),
    survey_weight_minus_svyratio = (
      survey_weight_estimate - ratio_estimate
    )
  )

  if (
    any(abs(estimate_differences) > 1e-10)
  ) {
    stop(
      analysis_name,
      ": weighted point estimates disagree. ",
      paste(
        names(estimate_differences),
        format(
          estimate_differences,
          scientific = TRUE
        ),
        sep = "=",
        collapse = ", "
      )
    )
  }

  active_missing_n <- sum(
    indicator_active == 1
  )
  weighted_missing_numerator <- sum(
    raw_active * indicator_active
  )

  if (
    active_missing_n > 0
    && (
      raw_estimate <= 0
      || weighted_missing_numerator <= 0
    )
  ) {
    missing_raw_weights <- raw_active[
      indicator_active == 1
    ]
    missing_survey_weights <- survey_active[
      indicator_active == 1
    ]

    stop(
      analysis_name,
      ": positive active missing count produced a non-positive ",
      "weighted numerator/proportion. active_missing_n=",
      active_missing_n,
      ", raw_weight_min=",
      min(missing_raw_weights),
      ", raw_weight_max=",
      max(missing_raw_weights),
      ", survey_weight_min=",
      min(missing_survey_weights),
      ", survey_weight_max=",
      max(missing_survey_weights),
      "."
    )
  }

  if (
    active_missing_n == 0
    && abs(raw_estimate) > 1e-15
  ) {
    stop(
      analysis_name,
      ": zero active missing count produced a non-zero ",
      "weighted missing proportion."
    )
  }

  list(
    estimate = raw_estimate,
    se = ratio_se,
    unweighted_n = length(indicator_active),
    missing_n = active_missing_n,
    source_row_n = length(indicator),
    source_missing_n = sum(
      indicator == 1,
      na.rm = TRUE
    ),
    weighted_denominator = sum(raw_active),
    weighted_missing_numerator = (
      weighted_missing_numerator
    ),
    survey_weighted_denominator = sum(
      survey_active
    ),
    survey_weighted_missing_numerator = sum(
      survey_active * indicator_active
    ),
    max_abs_weight_difference = max(
      abs(raw_active - survey_active)
    )
  )
}

append_domain_rows <- function(
  output_rows,
  output_index,
  design_object,
  grouping_variable,
  dimension_name,
  cycle_value,
  biomarker_name
) {
  group_values <- design_object$variables[[grouping_variable]]
  if (is.null(group_values)) {
    stop(
      "Check 4 domain variable was not found: ",
      grouping_variable
    )
  }

  levels_present <- unique(
    as.character(
      group_values[!is.na(group_values)]
    )
  )

  for (level_value in levels_present) {
    domain_mask <- (
      !is.na(group_values)
      & as.character(group_values) == level_value
    )

    domain_design <- subset(
      design_object,
      domain_mask
    )

    domain_summary <- weighted_binary_summary(
      domain_design,
      analysis_name = paste(
        "Check 4",
        cycle_value,
        biomarker_name,
        dimension_name,
        level_value,
        sep = " | "
      )
    )

    output_rows[[output_index]] <- data.frame(
      cycle = cycle_value,
      biomarker = biomarker_name,
      dimension = dimension_name,
      level = level_value,
      unweighted_n = domain_summary$unweighted_n,
      unweighted_missing_n = domain_summary$missing_n,
      source_row_n = domain_summary$source_row_n,
      source_missing_n = domain_summary$source_missing_n,
      weighted_missing_percent = (
        domain_summary$estimate * 100
      ),
      standard_error_percent = (
        domain_summary$se * 100
      ),
      weighted_denominator = (
        domain_summary$weighted_denominator
      ),
      weighted_missing_numerator = (
        domain_summary$weighted_missing_numerator
      ),
      survey_weighted_denominator = (
        domain_summary$survey_weighted_denominator
      ),
      survey_weighted_missing_numerator = (
        domain_summary$survey_weighted_missing_numerator
      ),
      max_abs_raw_minus_survey_weight = (
        domain_summary$max_abs_weight_difference
      ),
      analysis_status = "OK",
      stringsAsFactors = FALSE
    )

    output_index <- output_index + 1
  }

  list(
    rows = output_rows,
    next_index = output_index
  )
}

log_step("Starting Check 4.")

cross_tab_rows <- list()
association_rows <- list()
cross_index <- 1
association_index <- 1

for (cycle_value in sort(unique(dat$NHANES_CYCLE))) {
  cycle_frame <- dat[
    dat$NHANES_CYCLE == cycle_value,
    ,
    drop = FALSE
  ]

  cycle_design <- build_design(
    cycle_frame,
    paste("Check 4 cycle", cycle_value)
  )

  for (biomarker_name in names(biomarker_columns)) {
    variable_name <- biomarker_columns[[biomarker_name]]
    analysis_name <- paste(
      cycle_value,
      biomarker_name,
      sep = " | "
    )

    tryCatch(
      {
        missing_indicator <- as.numeric(
          is.na(
            cycle_design$variables[[variable_name]]
          )
        )

        biomarker_design <- cycle_design
        biomarker_design$variables$missing_indicator <- (
          missing_indicator
        )
        biomarker_design$variables$missing_factor <- (
          factor(
            missing_indicator,
            levels = c(0, 1),
            labels = c("observed", "missing")
          )
        )

        overall_summary <- weighted_binary_summary(
          biomarker_design,
          analysis_name = paste(
            "Check 4 overall",
            analysis_name,
            sep = " | "
          )
        )

        cross_tab_rows[[cross_index]] <- data.frame(
          cycle = cycle_value,
          biomarker = biomarker_name,
          dimension = "overall",
          level = "all",
          unweighted_n = overall_summary$unweighted_n,
          unweighted_missing_n = overall_summary$missing_n,
          source_row_n = overall_summary$source_row_n,
          source_missing_n = overall_summary$source_missing_n,
          weighted_missing_percent = (
            overall_summary$estimate * 100
          ),
          standard_error_percent = (
            overall_summary$se * 100
          ),
          weighted_denominator = (
            overall_summary$weighted_denominator
          ),
          weighted_missing_numerator = (
            overall_summary$weighted_missing_numerator
          ),
          survey_weighted_denominator = (
            overall_summary$survey_weighted_denominator
          ),
          survey_weighted_missing_numerator = (
            overall_summary$survey_weighted_missing_numerator
          ),
          max_abs_raw_minus_survey_weight = (
            overall_summary$max_abs_weight_difference
          ),
          analysis_status = "OK",
          stringsAsFactors = FALSE
        )
        cross_index <- cross_index + 1

        age_result <- append_domain_rows(
          cross_tab_rows,
          cross_index,
          biomarker_design,
          "age_group",
          "age_group",
          cycle_value,
          biomarker_name
        )
        cross_tab_rows <- age_result$rows
        cross_index <- age_result$next_index

        sex_result <- append_domain_rows(
          cross_tab_rows,
          cross_index,
          biomarker_design,
          "sex",
          "sex",
          cycle_value,
          biomarker_name
        )
        cross_tab_rows <- sex_result$rows
        cross_index <- sex_result$next_index

        has_variation <- length(
          unique(missing_indicator)
        ) > 1

        age_p <- if (has_variation) {
          safe_chisq_p(
            ~missing_factor + age_group,
            biomarker_design
          )
        } else {
          NA_real_
        }

        sex_p <- if (has_variation) {
          safe_chisq_p(
            ~missing_factor + sex,
            biomarker_design
          )
        } else {
          NA_real_
        }

        association_rows[[association_index]] <- data.frame(
          cycle = cycle_value,
          biomarker = biomarker_name,
          n = overall_summary$unweighted_n,
          missing_n = overall_summary$missing_n,
          source_row_n = overall_summary$source_row_n,
          source_missing_n = overall_summary$source_missing_n,
          weighted_missing_percent = (
            overall_summary$estimate * 100
          ),
          weighted_denominator = (
            overall_summary$weighted_denominator
          ),
          weighted_missing_numerator = (
            overall_summary$weighted_missing_numerator
          ),
          survey_weighted_denominator = (
            overall_summary$survey_weighted_denominator
          ),
          survey_weighted_missing_numerator = (
            overall_summary$survey_weighted_missing_numerator
          ),
          max_abs_raw_minus_survey_weight = (
            overall_summary$max_abs_weight_difference
          ),
          age_group_association_p = age_p,
          sex_association_p = sex_p,
          little_mcar_test_run = FALSE,
          check_scope = paste0(
            "Design-based demographic association; ",
            "Little's MCAR not run"
          ),
          analysis_status = "OK",
          analysis_error = "",
          stringsAsFactors = FALSE
        )
        association_index <- association_index + 1
      },
      error = function(e) {
        record_error(
          "Check 4",
          analysis_name,
          conditionMessage(e)
        )

        association_rows[[association_index]] <<- data.frame(
          cycle = cycle_value,
          biomarker = biomarker_name,
          n = nrow(cycle_frame),
          missing_n = sum(
            is.na(cycle_frame[[variable_name]])
          ),
          source_row_n = nrow(cycle_frame),
          source_missing_n = sum(
            is.na(cycle_frame[[variable_name]])
          ),
          weighted_missing_percent = NA_real_,
          weighted_denominator = NA_real_,
          weighted_missing_numerator = NA_real_,
          survey_weighted_denominator = NA_real_,
          survey_weighted_missing_numerator = NA_real_,
          max_abs_raw_minus_survey_weight = NA_real_,
          age_group_association_p = NA_real_,
          sex_association_p = NA_real_,
          little_mcar_test_run = FALSE,
          check_scope = (
            "Analysis error; see 05_r_analysis_error_audit.csv"
          ),
          analysis_status = "ERROR",
          analysis_error = conditionMessage(e),
          stringsAsFactors = FALSE
        )
        association_index <<- association_index + 1
      }
    )
  }
}

check4_cross_tabs <- if (
  length(cross_tab_rows) > 0
) {
  do.call(rbind, cross_tab_rows)
} else {
  data.frame(
    cycle = character(),
    biomarker = character(),
    dimension = character(),
    level = character(),
    unweighted_n = integer(),
    unweighted_missing_n = integer(),
    source_row_n = integer(),
    source_missing_n = integer(),
    weighted_missing_percent = numeric(),
    standard_error_percent = numeric(),
    weighted_denominator = numeric(),
    weighted_missing_numerator = numeric(),
    survey_weighted_denominator = numeric(),
    survey_weighted_missing_numerator = numeric(),
    max_abs_raw_minus_survey_weight = numeric(),
    analysis_status = character(),
    stringsAsFactors = FALSE
  )
}

check4_associations <- do.call(
  rbind,
  association_rows
)

write.csv(
  check4_cross_tabs,
  file.path(
    table_dir,
    "05_check4_missingness_demographic_cross_tabs.csv"
  ),
  row.names = FALSE
)

write.csv(
  check4_associations,
  file.path(
    table_dir,
    "05_check4_missingness_association_tests.csv"
  ),
  row.names = FALSE
)

error_audit <- if (length(error_rows) > 0) {
  do.call(rbind, error_rows)
} else {
  data.frame(
    component = character(),
    analysis = character(),
    error = character(),
    stringsAsFactors = FALSE
  )
}

write.csv(
  error_audit,
  error_audit_path,
  row.names = FALSE
)

capture.output(
  sessionInfo(),
  file = file.path(
    log_dir,
    "05_r_session_info.txt"
  )
)

log_step(
  paste0(
    "Check 4 completed; successful association rows = ",
    sum(check4_associations$analysis_status == "OK"),
    "/",
    nrow(check4_associations),
    "."
  )
)

log_step(
  paste0(
    "Validation Protocol Checks 3 and 4 finished. ",
    "Recorded analysis errors = ",
    nrow(error_audit),
    "."
  )
)

check3_error_count <- sum(
  check3_results$analysis_status != "OK"
)
check4_error_count <- sum(
  check4_associations$analysis_status != "OK"
)

if (check3_error_count > 0 || check4_error_count > 0) {
  stop(
    "Validation completion has failed rows: Check 3 = ",
    check3_error_count,
    ", Check 4 = ",
    check4_error_count,
    ". See ",
    error_audit_path,
    "."
  )
}

message(
  "Validation Protocol Checks 3 and 4 completed successfully. ",
  "All weighted-missingness point estimates were independently ",
  "cross-checked against positive-weight sums."
)
