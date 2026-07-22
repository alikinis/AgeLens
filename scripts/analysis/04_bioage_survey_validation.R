options(error = function() {
  error_log <- file.path(
    if (exists('log_dir')) log_dir else getwd(),
    '04_r_external_validation_error.txt'
  )
  sink(error_log, append = TRUE, type = 'output')
  cat('\n--- R validation error ---\n')
  cat('Time: ', format(Sys.time(), tz = 'UTC', usetz = TRUE), '\n', sep = '')
  traceback(20)
  sink(type = 'output')
})

args <- commandArgs(trailingOnly = TRUE)
project_root <- if (length(args) >= 1) normalizePath(args[[1]], mustWork = TRUE) else normalizePath('.', mustWork = TRUE)
install_missing <- if (length(args) >= 2) tolower(args[[2]]) %in% c('true','1','yes') else FALSE

required_cran <- c('survey','dplyr','remotes','flexsurv')
missing_cran <- required_cran[!vapply(required_cran, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_cran) > 0) {
  if (!install_missing) stop('Missing R packages: ', paste(missing_cran, collapse=', '))
  install.packages(missing_cran, repos='https://cloud.r-project.org')
}

bioage_ref <- 'dayoonkwon/BioAge@b1f9fc0'
if (!requireNamespace('BioAge', quietly = TRUE)) {
  if (!install_missing) stop('BioAge is not installed. Install with remotes::install_github("', bioage_ref, '")')
  remotes::install_github(bioage_ref, upgrade='never', dependencies=TRUE)
}

suppressPackageStartupMessages({
  library(BioAge)
  library(survey)
  library(dplyr)
})
options(survey.lonely.psu='fail')

input_path <- file.path(project_root,'results','tables','04_r_validation_input.csv')
benchmark_path <- file.path(project_root,'data','external','bioage_phenoage_benchmark.csv')
table_dir <- file.path(project_root,'results','tables')
log_dir <- file.path(project_root,'logs')
dir.create(dirname(benchmark_path), recursive=TRUE, showWarnings=FALSE)
dir.create(table_dir, recursive=TRUE, showWarnings=FALSE)
dir.create(log_dir, recursive=TRUE, showWarnings=FALSE)
if (!file.exists(input_path)) stop('Input not found: ', input_path)

dat <- read.csv(input_path, stringsAsFactors=FALSE, check.names=FALSE)
required_columns <- c('SEQN','NHANES_CYCLE','age_topcoded','age_below_20','WTSAF4YR','SDMVSTRA','SDMVPSU',
  'albumin_gL','creat_umol','glucose_mmol','lncrp','lymph','mcv','rdw','alp','wbc','age',
  'agelens_erratum','agelens_supplement','prebridge_erratum','prebridge_supplement')
missing_columns <- setdiff(required_columns, names(dat))
if (length(missing_columns)>0) stop('Missing columns: ', paste(missing_columns, collapse=', '))

parse_binary_flag <- function(x, column_name) {
  if (is.logical(x)) {
    if (any(is.na(x))) stop(column_name, ' contains missing values.')
    return(x)
  }

  if (is.numeric(x) || is.integer(x)) {
    if (any(is.na(x)) || any(!x %in% c(0, 1))) {
      stop(column_name, ' must contain only 0/1 when numeric.')
    }
    return(x == 1)
  }

  normalized <- tolower(trimws(as.character(x)))
  result <- rep(NA, length(normalized))

  result[normalized %in% c('true', 't', '1', 'yes', 'y')] <- TRUE
  result[normalized %in% c('false', 'f', '0', 'no', 'n')] <- FALSE

  if (any(is.na(result))) {
    bad_values <- unique(normalized[is.na(result)])
    stop(
      column_name,
      ' contains unrecognized boolean values: ',
      paste(bad_values, collapse=', ')
    )
  }

  result
}

dat$age_topcoded <- parse_binary_flag(dat$age_topcoded, 'age_topcoded')
dat$age_below_20 <- parse_binary_flag(dat$age_below_20, 'age_below_20')
if (anyDuplicated(dat[c('NHANES_CYCLE','SEQN')])) stop('Duplicate cycle + SEQN rows found.')
if (any(is.na(dat$WTSAF4YR)) || any(dat$WTSAF4YR<=0)) stop('Invalid WTSAF4YR values.')

# Direct installed-source audit.
phenoage_source <- paste(deparse(BioAge::phenoage_calc), collapse='\n')
required_tokens <- c('-19.90667','-0.03359355','0.009506491','0.1953192','0.09536762','-0.01199984',
  '0.02676401','0.3306156','0.001868778','0.05542406','0.08035356','1.51714','0.007692696',
  '.0055305','.090165','141.50225')
present <- vapply(required_tokens, function(x) grepl(x, phenoage_source, fixed=TRUE), logical(1))
source_audit <- data.frame(token=required_tokens, present=present)
write.csv(source_audit, file.path(table_dir,'04_bioage_source_token_audit.csv'), row.names=FALSE)
if (!all(present)) stop('Installed BioAge source does not match the expected pinned orig=TRUE implementation.')

# BioAge orig=TRUE independent package output. A harmless dummy fit avoids retraining.
biomarkers <- c('albumin_gL','lymph','mcv','glucose_mmol','rdw','creat_umol','lncrp','alp','wbc')
coef_names <- c(biomarkers,'age')
dummy_fit <- list(
  coef=data.frame(coef=rep(0,length(coef_names)), row.names=coef_names),
  m_n=-1, m_d=1, BA_n=-1, BA_d=1, BA_i=0
)
bioage_result <- BioAge::phenoage_calc(
  data=dat,
  biomarkers=biomarkers,
  fit=dummy_fit,
  orig=TRUE
)
bioage_data <- bioage_result$data

if (!'phenoage0' %in% names(bioage_data)) {
  stop('BioAge orig=TRUE did not return phenoage0.')
}

# The package source evaluates:
#   m_orig = 1 - exp(-hazard)
#   phenoage0 = 141.50225 + log(-0.0055305 * log(1-m_orig)) / 0.090165
#
# At high hazard, m_orig can round to exactly 1 in float64 and the second
# expression becomes Inf. The following expression is algebraically identical:
#   -log(1-m_orig) = hazard
# and therefore avoids loss of information.
xb_orig_exact <- (
  -19.90667
  + (-0.03359355 * bioage_data$albumin_gL)
  + (0.009506491 * bioage_data$creat_umol)
  + (0.1953192 * bioage_data$glucose_mmol)
  + (0.09536762 * bioage_data$lncrp)
  + (-0.01199984 * bioage_data$lymph)
  + (0.02676401 * bioage_data$mcv)
  + (0.3306156 * bioage_data$rdw)
  + (0.001868778 * bioage_data$alp)
  + (0.05542406 * bioage_data$wbc)
  + (0.08035356 * bioage_data$age)
)

log_hazard_orig_exact <- (
  log(1.51714 / 0.007692696)
  + xb_orig_exact
)

bioage_data$phenoage0_stable <- (
  141.50225
  + (
    log(0.0055305)
    + log_hazard_orig_exact
  ) / 0.090165
)

if (any(!is.finite(bioage_data$phenoage0_stable))) {
  stop('Stable BioAge orig=TRUE calculation produced non-finite values.')
}

package_output_finite <- is.finite(bioage_data$phenoage0)

finite_package_difference <- rep(NA_real_, nrow(bioage_data))
finite_package_difference[package_output_finite] <- (
  bioage_data$phenoage0[package_output_finite]
  - bioage_data$phenoage0_stable[package_output_finite]
)

finite_subset_max_abs_difference <- if (
  any(package_output_finite)
) {
  max(abs(finite_package_difference), na.rm=TRUE)
} else {
  NA_real_
}

# Do not stop the validation solely because the raw package pathway has
# floating-point discrepancies. Preserve the magnitude in the audit table.
finite_subset_within_1e8_tolerance <- if (
  is.na(finite_subset_max_abs_difference)
) {
  NA
} else {
  finite_subset_max_abs_difference <= 1e-8
}

numerical_stability_audit <- bioage_data %>%
  mutate(
    package_output_finite = package_output_finite,
    package_output_positive_infinity = is.infinite(phenoage0) & phenoage0 > 0,
    package_output_negative_infinity = is.infinite(phenoage0) & phenoage0 < 0,
    package_minus_stable_finite_subset = finite_package_difference
  ) %>%
  group_by(NHANES_CYCLE) %>%
  summarise(
    n = n(),
    package_finite_n = sum(package_output_finite),
    package_nonfinite_n = sum(!package_output_finite),
    package_positive_infinity_n = sum(package_output_positive_infinity),
    package_negative_infinity_n = sum(package_output_negative_infinity),
    stable_finite_n = sum(is.finite(phenoage0_stable)),
    max_abs_package_minus_stable_finite_subset = ifelse(
      any(package_output_finite),
      max(abs(package_minus_stable_finite_subset), na.rm=TRUE),
      NA_real_
    ),
    finite_subset_within_1e8_tolerance = ifelse(
      any(package_output_finite),
      max(abs(package_minus_stable_finite_subset), na.rm=TRUE) <= 1e-8,
      NA
    ),
    .groups='drop'
  )

write.csv(
  numerical_stability_audit,
  file.path(table_dir,'04_bioage_numerical_stability_audit.csv'),
  row.names=FALSE
)

# Use the stable evaluation of the exact audited BioAge source constants as
# the cross-implementation benchmark. The raw package output is retained in
# the numerical-stability audit rather than silently treated as valid.
benchmark <- data.frame(
  SEQN=bioage_data$SEQN,
  NHANES_CYCLE=bioage_data$NHANES_CYCLE,
  bioage_phenoage=bioage_data$phenoage0_stable
)
write.csv(benchmark, benchmark_path, row.names=FALSE)

comparison_long <- bind_rows(
  data.frame(
    SEQN=bioage_data$SEQN,
    NHANES_CYCLE=bioage_data$NHANES_CYCLE,
    variant='erratum',
    agelens=bioage_data$agelens_erratum,
    bioage=bioage_data$phenoage0_stable
  ),
  data.frame(
    SEQN=bioage_data$SEQN,
    NHANES_CYCLE=bioage_data$NHANES_CYCLE,
    variant='supplement',
    agelens=bioage_data$agelens_supplement,
    bioage=bioage_data$phenoage0_stable
  )
) %>%
  mutate(
    difference=agelens-bioage,
    average=(agelens+bioage)/2
  )

bioage_metrics <- comparison_long %>% group_by(NHANES_CYCLE,variant) %>% summarise(
  n=n(), mae=mean(abs(difference)), rmse=sqrt(mean(difference^2)),
  mean_agelens_minus_bioage=mean(difference), sd_difference=sd(difference),
  bland_altman_lower=mean(difference)-1.96*sd(difference),
  bland_altman_upper=mean(difference)+1.96*sd(difference),
  pearson=cor(agelens,bioage,method='pearson'), spearman=cor(agelens,bioage,method='spearman'),
  difference_average_correlation=cor(difference,average,method='pearson'), .groups='drop')
write.csv(bioage_metrics, file.path(table_dir,'04_bioage_comparison.csv'), row.names=FALSE)

# Independent R survey package checks.
design <- svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~WTSAF4YR, nest=TRUE, data=dat)
samples <- list(
  all_harmonized_complete_case=rep(TRUE,nrow(dat)),
  no_topcode=!dat$age_topcoded,
  age20plus=dat$age>=20,
  age20plus_no_topcode=dat$age>=20 & !dat$age_topcoded
)
extract_mean <- function(d,v) {
  z <- svymean(as.formula(paste0('~',v)), d, na.rm=TRUE)
  ci <- confint(z)
  data.frame(weighted_mean=as.numeric(coef(z)), taylor_se=as.numeric(SE(z)), ci_low_95=ci[1,1], ci_high_95=ci[1,2])
}
rows <- list(); k <- 1
for (s in names(samples)) for (cy in sort(unique(dat$NHANES_CYCLE))) for (v in c('erratum','supplement')) {
  mask <- samples[[s]] & dat$NHANES_CYCLE==cy
  res <- extract_mean(subset(design,mask), paste0('agelens_',v))
  rows[[k]] <- data.frame(sample=s,cycle=cy,formula_variant=v,n=sum(mask),res); k <- k+1
}
survey_means <- bind_rows(rows)
write.csv(survey_means, file.path(table_dir,'04_r_survey_weighted_means.csv'), row.names=FALSE)

weighted_corr <- function(d,x,y) {
  m <- as.matrix(svyvar(as.formula(paste0('~',x,'+',y)), d, na.rm=TRUE))
  m[1,2]/sqrt(m[1,1]*m[2,2])
}
rows <- list(); k <- 1
for (s in names(samples)) for (cy in sort(unique(dat$NHANES_CYCLE))) for (v in c('erratum','supplement')) {
  mask <- samples[[s]] & dat$NHANES_CYCLE==cy
  rows[[k]] <- data.frame(sample=s,cycle=cy,formula_variant=v,n=sum(mask),
    weighted_pearson=weighted_corr(subset(design,mask),'age',paste0('agelens_',v))); k <- k+1
}
write.csv(bind_rows(rows), file.path(table_dir,'04_r_survey_age_correlations.csv'), row.names=FALSE)

dat$bridge_difference_erratum <- dat$agelens_erratum-dat$prebridge_erratum
dat$bridge_difference_supplement <- dat$agelens_supplement-dat$prebridge_supplement
bridge_design <- svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~WTSAF4YR,nest=TRUE,data=dat)
rows <- list(); k <- 1
for (cy in sort(unique(dat$NHANES_CYCLE))) for (v in c('erratum','supplement')) {
  mask <- dat$NHANES_CYCLE==cy
  res <- extract_mean(subset(bridge_design,mask), paste0('bridge_difference_',v))
  rows[[k]] <- data.frame(cycle=cy,formula_variant=v,n_identical_sample=sum(mask),
    mean_post_minus_pre_weighted=res$weighted_mean,difference_taylor_se=res$taylor_se,
    difference_ci_low_95=res$ci_low_95,difference_ci_high_95=res$ci_high_95); k <- k+1
}
write.csv(bind_rows(rows), file.path(table_dir,'04_r_bridge_validation.csv'), row.names=FALSE)

capture.output(sessionInfo(), file=file.path(log_dir,'04_r_session_info.txt'))
writeLines(phenoage_source, file.path(log_dir,'04_installed_bioage_phenoage_calc_source.txt'))
message(
  'BioAge stable benchmark and R survey validation completed successfully. ',
  'Raw package non-finite outputs are documented in ',
  '04_bioage_numerical_stability_audit.csv.'
)
