#!/usr/bin/env bash
# Make a site from this repo with `quarto use template`, render every format, and check the result.
#   bash tests/check-starter.sh        (needs quarto; python with pymupdf is optional)
# CI runs this in .github/workflows/check.yml.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir "$work/my-site"
cd "$work/my-site"

fail() { echo "FAIL $*"; exit 1; }
ok() { echo "ok   $*"; }

quarto use template "$repo" --no-prompt > /dev/null
quarto --version

# 1. The starter has what a new site needs and none of the documentation.
for f in _quarto.yml index.qmd contact/index.qmd terms/index.qmd _extensions/wfrc-brand/_extension.yml _extensions/wfrc-brand/brand.yml; do
  test -f "$f" || fail "starter is missing $f"
done
for f in _quarto-docs.yml brand-guide.qmd migrate.qmd example.qmd example-landing.qmd example-dashboard.qmd \
         example-slides.qmd example-report.qmd docs scripts tests .github CHANGELOG.md README.md; do
  test ! -e "$f" || fail "starter should not contain $f"
done
ok "starter has the site files and no documentation files"

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

quarto render > render.log 2>&1 || { cat render.log; fail "quarto render failed"; }
grep -E "^(WARN|ERROR)" render.log | grep -v -E "Unable to resolve link target" && fail "render warnings above" || true
for out in index.html contact/index.html terms/index.html slides.html report.pdf dashboard.html; do
  test -f "_site/$out" || fail "missing _site/$out"
done
ok "starter, slides, PDF and dashboard render"

# 3. The theme is applied: brand colors reach the compiled CSS and the footer links resolve.
css="$(ls _site/site_libs/bootstrap/bootstrap-*.min.css | grep -v dark | head -1)"
grep -qi "00395b" "$css" || fail "brand navy is not in the compiled CSS"
grep -q 'href="./contact/index.html"' _site/index.html || fail "footer Contact link is not site-relative"
ok "theme applied and footer links resolve"

# 4. Offline brand: render the PDF with only the bundled fonts and check they are embedded.
sed -i 's#brand: _extensions/wfrc-brand/brand.yml#brand: _extensions/wfrc-brand/brand-offline.yml#' _quarto.yml
grep -q "brand-offline.yml" _quarto.yml || fail "could not switch to the offline brand"
sed -i 's/^format: wfrc-brand-typst/format:\n  wfrc-brand-typst:\n    keep-typ: true/' report.qmd
quarto render report.qmd > render2.log 2>&1 || { cat render2.log; fail "offline brand render failed"; }
if python -c "import pymupdf" 2>/dev/null || python -c "import fitz" 2>/dev/null; then
  quarto typst compile report.typ offline.pdf --ignore-system-fonts --font-path _extensions/wfrc-brand/assets/fonts > /dev/null 2>&1 \
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
