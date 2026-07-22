args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 1) {
  stop("Expected one R script path.")
}

target_path <- args[[1]]
parse(file = target_path)
cat("R parse check passed\n")
