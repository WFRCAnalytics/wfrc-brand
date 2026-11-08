# R checks: the ggplot2 chart helpers, and the flat brand through the R brand.yml and bslib packages.
#   Rscript tests/test-charts.R        (needs ggplot2; brand.yml and bslib are optional)
args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
ext <- file.path(dirname(here), "_extensions", "wfrc-brand")
source(file.path(ext, "assets", "charts", "wfrc-charts.R"))

failures <- 0
check <- function(ok, what) {
  cat(if (isTRUE(ok)) "ok   " else "FAIL ", what, "\n", sep = "")
  if (!isTRUE(ok)) failures <<- failures + 1
}
has <- function(pkg) requireNamespace(pkg, quietly = TRUE)

brand <- file.path(ext, "brand.yml")
check(length(wfrc_colors(brand)) > 50, "wfrc_colors() reads the palette")
check(identical(unname(wfrc_colors(brand)[["wfrc-navy"]]), "#00395B"), "wfrc-navy is #00395B")
check(identical(unname(wfrc_colors(brand)[["blue"]]), unname(wfrc_colors(brand)[["chart-1"]])), "aliases resolve")
light <- wfrc_palette(5, "light", brand)
dark <- wfrc_palette(5, "dark", brand)
check(length(unique(light)) == 5 && all(grepl("^#[0-9A-F]{6}$", light)), "five distinct light colors")
check(!identical(light, dark), "dark palette differs")
check(inherits(try(wfrc_palette(6, path = brand), silent = TRUE), "try-error"), "refuses more than five")
check(identical(wfrc_palette(5, "light", file.path(ext, "brand-flat.yml")), light), "flat brand gives the same palette")

if (has("ggplot2")) {
  library(ggplot2)
  p <- ggplot(mtcars, aes(wt, mpg, color = factor(cyl))) +
    geom_point() + theme_wfrc(path = brand) + scale_color_wfrc()
  png(tempfile(fileext = ".png")); print(p); invisible(dev.off())
  check(inherits(p, "ggplot"), "ggplot2 theme and scale render")
  b <- ggplot_build(p)
  # ggplot lists colors in row order, so compare as a set
  check(setequal(unique(b$data[[1]]$colour), light[1:3]), "scale_color_wfrc uses the first three brand colors")
} else cat("skip ggplot2 not installed\n")

flat <- file.path(ext, "brand-flat.yml")
if (has("brand.yml")) {
  br <- brand.yml::read_brand_yml(flat)
  # the package renames palette entries (wfrc-navy becomes wfrc_navy), so test a role instead
  check(identical(toupper(br$color$primary), "#00395B"), "brand.yml reads brand-flat.yml")
  # The file with light/dark values is for Quarto only: the R package rejects it.
  check(inherits(try(brand.yml::read_brand_yml(brand), silent = TRUE), "try-error"),
        "brand.yml (light/dark) is rejected by the R package, as documented")
} else cat("skip brand.yml not installed\n")

if (has("bslib") && has("brand.yml")) {
  th <- bslib::bs_theme(brand = flat)
  check(tolower(bslib::bs_get_variables(th, "primary")[["primary"]]) == "#00395b", "bslib theme takes primary from the flat brand")
} else cat("skip bslib not installed\n")

if (failures > 0) stop(failures, " check(s) failed", call. = FALSE)
cat("all R checks passed\n")
