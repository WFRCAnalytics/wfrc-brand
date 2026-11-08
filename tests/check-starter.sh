#!/usr/bin/env bash
# Make a site from this repo with `quarto use template`, render every format, and check the result.
#   bash tests/check-starter.sh [source]    (needs quarto; python with pymupdf is optional)
# source is what `quarto use template` installs from: a local folder (the default, this repo) or a
# GitHub reference such as WFRCAnalytics/wfrc-brand@main. CI uses the GitHub reference, because that
# is how sites install it; Quarto puts an extension from GitHub under the owner's folder
# (_extensions/WFRCAnalytics/wfrc-brand) but one from a local folder directly under _extensions.
# The local default moves it there, so the paths in the starter's config are the ones checked.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir "$work/my-site"
cd "$work/my-site"

fail() { echo "FAIL $*"; exit 1; }
ok() { echo "ok   $*"; }

source="${1:-$repo}"
quarto use template "$source" --no-prompt > /dev/null
quarto --version
# The GitHub menu finds its repository from the git remote (or GITHUB_REPOSITORY in Actions).
git init -q .
git remote add origin https://github.com/WFRCAnalytics/my-site.git
if [ -d "$source" ]; then
  test -d _extensions/wfrc-brand || fail "a local install should have produced _extensions/wfrc-brand"
  mkdir -p _extensions/WFRCAnalytics
  mv _extensions/wfrc-brand _extensions/WFRCAnalytics/wfrc-brand
  echo "note local install: moved the extension under _extensions/WFRCAnalytics, as a GitHub install does"
fi

# 1. The starter has what a new site needs and none of the documentation.
for f in _quarto.yml index.qmd _extensions/WFRCAnalytics/wfrc-brand/_extension.yml _extensions/WFRCAnalytics/wfrc-brand/brand.yml; do
  test -f "$f" || fail "starter is missing $f"
done
for f in _quarto-docs.yml brand-guide.qmd migrate.qmd example.qmd example-landing.qmd example-dashboard.qmd \
         example-slides.qmd example-report.qmd docs scripts tests .github CHANGELOG.md README.md contact terms; do
  test ! -e "$f" || fail "starter should not contain $f"
done
ok "starter has the site files and no documentation files"

# Quarto installs an extension under the owner's name (_extensions/<owner>/<name>), and every path in
# the starter's config has to point there. A wrong path is ignored without an error: the site would
# render unthemed. So check each _extensions/ path the config names.
test -d _extensions/WFRCAnalytics/wfrc-brand || fail "extension is not installed at _extensions/WFRCAnalytics/wfrc-brand"
paths="$(grep -h -v -E '^[[:space:]]*#' _quarto.yml _extensions/WFRCAnalytics/wfrc-brand/wfrc-shared.yml | grep -o -E '_extensions/[A-Za-z0-9_./*-]+' | sed 's/[.]$//' | sort -u)"
test -n "$paths" || fail "found no _extensions paths to check"
for p in $paths; do
  case "$p" in
    *'*'*) ls $p > /dev/null 2>&1 || fail "glob matches nothing: $p" ;;
    *) test -e "$p" || fail "config points at a path that does not exist: $p" ;;
  esac
done
ok "every _extensions path in the config exists"

# 2. One page per format, next to the starter's own pages.
cat > slides.qmd <<'EOF'
---
title: "Slides"
format: wfrc-brand-revealjs
---

## One

- a point
EOF
cat > report.qmd <<'EOF'
---
title: "Report"
format: wfrc-brand-typst
---

## Summary

Some text with `inline code`.

```r
x <- 1
```
EOF
cat > dashboard.qmd <<'EOF'
---
title: "Dashboard"
format: wfrc-brand-dashboard
---

## Row

::: {.card}
Some text.
:::
EOF

env -u GITHUB_REPOSITORY quarto render > render.log 2>&1 || { cat render.log; fail "quarto render failed"; }
grep -E "^(WARN|ERROR)" render.log | grep -v -E "Unable to resolve link target" && fail "render warnings above" || true
for out in index.html slides.html report.pdf dashboard.html; do
  test -f "_site/$out" || fail "missing _site/$out"
done
ok "starter, slides, PDF and dashboard render"

# 3. The theme is applied: brand colors reach the compiled CSS and the footer links resolve.
css="$(ls _site/site_libs/bootstrap/bootstrap-*.min.css | grep -v dark | head -1)"
grep -qi "00395b" "$css" || fail "brand navy is not in the compiled CSS"
grep -q 'href="https://wfrcanalytics.github.io/contact/"' _site/index.html || fail "footer Contact link does not go to the org page"
grep -q 'href="https://wfrcanalytics.github.io/terms/"' _site/index.html || fail "footer Terms of use link does not go to the org page"
ok "theme applied, footer links go to the org pages"

# 3a. The GitHub menu points at this site's own repository, found from the git remote.
grep -q 'href="https://github.com/WFRCAnalytics/my-site"' _site/index.html || fail "GitHub menu: Source Code does not point at the repository"
grep -q 'href="https://github.com/WFRCAnalytics/my-site/issues/new"' _site/index.html || fail "GitHub menu: Report a Bug does not point at the repository"
if grep -q 'wfrc-repo' _site/index.html; then fail "GitHub menu placeholders were left in the page"; fi
if grep -q "Ask a Question" _site/index.html; then fail "Ask a Question should be left out when the repository has no Discussions"; fi
env GITHUB_REPOSITORY=WFRCAnalytics/from-env quarto render index.qmd > render4.log 2>&1 || { cat render4.log; fail "render with GITHUB_REPOSITORY failed"; }
grep -q 'href="https://github.com/WFRCAnalytics/from-env/issues/new"' _site/index.html || fail "GitHub menu ignored GITHUB_REPOSITORY"
ok "GitHub menu detects the repository (git remote, and GITHUB_REPOSITORY in Actions)"

# 3b. A site can differ from the org defaults with a file listed after the shared one, which beats it.
cp _quarto.yml _quarto.yml.orig
cat > _site.yml <<'EOF'
website:
  back-to-top-navigation: true
format:
  html:
    page-layout: article
    toc-expand: 1
execute:
  freeze: false
EOF
sed -i 's/^  # - _site.yml$/  - _site.yml/' _quarto.yml
grep -q "^  - _site.yml$" _quarto.yml || fail "could not list _site.yml in the starter config"
env -u GITHUB_REPOSITORY quarto render index.qmd > render3.log 2>&1 || { cat render3.log; fail "render with _site.yml failed"; }
grep -q "quarto-back-to-top" _site/index.html || fail "_site.yml did not turn on back-to-top-navigation"
grep -q "page-layout-article" _site/index.html || fail "_site.yml did not override page-layout"
quarto inspect index.qmd | python -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d['formats']['html'].get('execute',{}).get('freeze') is False else 1)"   || fail "_site.yml did not override execute.freeze"
cp _quarto.yml.orig _quarto.yml
rm _site.yml
ok "a site's own _site.yml overrides the shared defaults"

# 4. Offline brand: render the PDF with only the bundled fonts and check they are embedded.
sed -i 's#brand: _extensions/WFRCAnalytics/wfrc-brand/brand.yml#brand: _extensions/WFRCAnalytics/wfrc-brand/brand-offline.yml#' _quarto.yml
grep -q "brand-offline.yml" _quarto.yml || fail "could not switch to the offline brand"
sed -i 's/^format: wfrc-brand-typst/format:\n  wfrc-brand-typst:\n    keep-typ: true/' report.qmd
quarto render report.qmd > render2.log 2>&1 || { cat render2.log; fail "offline brand render failed"; }
if python -c "import pymupdf" 2>/dev/null || python -c "import fitz" 2>/dev/null; then
  quarto typst compile report.typ offline.pdf --ignore-system-fonts --font-path _extensions/WFRCAnalytics/wfrc-brand/assets/fonts > /dev/null 2>&1 \
    || fail "typst compile with bundled fonts failed"
  python - <<'EOF' || fail "bundled fonts are not embedded"
import re, sys
data = open("offline.pdf", "rb").read()
fonts = {m.decode().split("+")[-1] for m in re.findall(rb"/BaseFont\s*/([A-Za-z0-9+\-]+)", data)}
need = {"Poppins-Regular", "Inter-Bold", "FiraCode-Regular"}
missing = need - fonts
print("embedded:", ", ".join(sorted(fonts)))
sys.exit(1 if missing else 0)
EOF
  ok "bundled Poppins, Inter and Fira Code are embedded in the PDF"
else
  echo "skip typst font check (python with pymupdf not available)"
fi

echo "all starter checks passed"
