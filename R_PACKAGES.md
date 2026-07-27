# R packages

Final governed execution used R 4.5.1.

Install the CRAN dependencies required by the public validation script:

```r
install.packages(c(
  "survey",
  "survival",
  "dplyr",
  "remotes",
  "flexsurv"
))
```

Install the exact BioAge revision used for the original-model agreement
checks:

```r
remotes::install_github(
  "dayoonkwon/BioAge@b1f9fc0",
  upgrade = "never",
  dependencies = TRUE
)
```

The public script `scripts/analysis/04_bioage_survey_validation.R` checks for
all five CRAN packages and the pinned BioAge implementation before analysis.

Recorded final versions:

- R 4.5.1
- `survey` 4.5
- `survival` 3.8-3

The exact governed run did not separately record the installed versions of
`dplyr`, `remotes`, and `flexsurv`; they are documented here as required
runtime dependencies rather than retrospectively assigned version claims.
