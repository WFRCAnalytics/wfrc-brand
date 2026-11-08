# Changelog

All notable changes to the wfrc-brand extension. Bump `version` in `_extensions/wfrc-brand/_extension.yml` and add an entry here on every meaningful change.

**1.0.1** — The shared config stops overriding what sites need to set themselves. Found while preparing the migration of the organization's repos.
- **Why.** A value in `wfrc-shared.yml` beats the same key in a site's own `_quarto.yml` (checked on Quarto 1.11), so anything a site legitimately tunes cannot live there. Also, `format: wfrc-brand-html` in a site that loads the shared file makes Quarto render every page twice (as `html` and as `wfrc-brand-html`) and fail, so websites use plain `format: html`.
- **Breaking: removed from `wfrc-shared.yml`.** The GitHub navbar menu (it linked every site to the wfrcanalytics.github.io repository: add your own `navbar.tools`, or `repo-url` with `repo-actions`); `page-navigation` and `back-to-top-navigation`; `execute.freeze`; and the HTML layout defaults `page-layout`, `toc`, `toc-expand`, `smooth-scroll` and `grid.sidebar-width`. The starter's `_quarto.yml` now sets the layout defaults under `format: html:` and `execute.freeze: auto`, where a site can change them. A site migrating from 1.0.0 or 0.x copies that block.
- **Breaking: Contact and Terms of use.** The footer links go to the single pages on wfrcanalytics.github.io (`/contact/`, `/terms/`) instead of site-relative pages, so no site carries or maintains its own copy. The `templates/` folder (contact.qmd, terms.qmd) and the starter's `contact/` and `terms/` pages are removed. The terms wording is still a draft for WFRC communications or legal to confirm.
- **Tests.** `tests/check-starter.sh` now also checks the footer links, that the shared config adds no GitHub menu, and that a site's own `back-to-top-navigation`, `page-layout` and `execute.freeze` values win. The migration page has a new "Overriding the shared defaults" section.

**1.0.0** — Slides, PDF reports, a starter template and a cleaner base. Pages keep their look: classes, `--wfrc-*` and `--brand-*` variables and page structure are unchanged (checked by diffing renders of wfrcanalytics.github.io against 0.5.1). See the [migration guide](https://wfrcanalytics.github.io/wfrc-brand/migrate.html).
- **Breaking: the extension folder.** `quarto add` and `quarto use template` install the extension at `_extensions/WFRCAnalytics/wfrc-brand/` (Quarto namespaces it by owner), so the repo now keeps it there and every documented path includes the owner folder. Earlier setups used `_extensions/wfrc-brand/`. A config path that points at a missing folder is ignored silently and the site renders unthemed, so `tests/check-starter.sh` now checks that every `_extensions/` path in the new site's config exists.
- **Fixes found in review.** The Warning callout icon is now a triangle with an exclamation mark (it was a bare triangle). Scrollbars follow the mode instead of the browser default: slim pill thumbs with no arrow buttons in Chrome, Edge and Safari, and `scrollbar-width`/`scrollbar-color` in Firefox, plus `color-scheme` so native controls match. In PDF reports the top margin is now 1.8 in, because Quarto draws the brand logo on every page and body text ran under it from page 2.
- **Code ligatures on.** Code blocks and inline code now use Fira Code ligatures (`!=`, `>=`, `->`, `|>` and the rest); 0.x switched them off. They are set explicitly so site or Bootstrap rules cannot turn them off.
- **Breaking.** Removed the palette aliases `wfrc-blue`, `wfrc-secondary-blue`, `wfrc-yellow`; the legacy classes `#bio`, `#landing-icons`, `.name-highlight`, `.featured-image` and `.description a`; and `engine: knitr`, `knitr.opts_chunk.dev: ragg_png` and `jupyter: python3` from `wfrc-shared.yml` (Quarto picks the engine from your code cells; set it in your own `_quarto.yml` if you need it).
- **Slides.** New `format: wfrc-brand-revealjs` (`assets/theme/wfrc-revealjs.scss`): brand colors and fonts, brick title-slide bar, bright-blue slide-title rule, brand logo, readable callouts and tables. Light only.
- **PDF.** `wfrc-brand-typst` now sets US Letter, 1 in margins and 10.5pt text. Logo, colors and fonts come from `brand.yml`.
- **Bundled fonts.** `brand-offline.yml` is `brand.yml` with Poppins, Inter and Fira Code as files in `assets/fonts/` (OFL; woff2 for the web, ttf for Typst), for offline builds. `brand.yml` still uses Google Fonts, because Quarto 1.11 does not copy bundled fonts for revealjs. Both come from `scripts/fetch-fonts.py` and `scripts/build-brand-offline.py`; edit `brand.yml`, then re-run the second.
- **Components from wfrcanalytics.github.io.** `.wfrc-chip` states (`.chip-live`, `.chip-internal`, `.chip-archived`), `.wfrc-stat-num`, rounded `type: table` listings, `.wfrc-cite`, `.wfrc-shot`, and a fix for the repo-actions navbar dropdown running off the screen. Status chip colors now come from role variables, so they follow dark mode.
- **`brand-flat.yml`.** The Python and R brand.yml packages reject `light:`/`dark:` pairs, so Shiny (R and Python), bslib and great-tables could not read `brand.yml`. `brand-flat.yml` (generated, light values) validates against the official schema and builds a Shiny theme. `scripts/build-brand-offline.py` is now `scripts/build-brand-variants.py` and writes both files.
- **Tests.** `tests/test_extension.py` (palette and alias checks, every `$brand-*` used in the SCSS exists, logo paths, variants in sync, the brand.yml schema, a Shiny theme, the Python chart helpers) and `tests/test-charts.R` (ggplot2 helpers, R brand.yml, bslib). CI runs them and renders the starter.
- **Starter template.** `quarto use template WFRCAnalytics/wfrc-brand` creates a site from this repo's `_quarto.yml`, `index.qmd`, `contact/` and `terms/` and installs the extension; `.quartoignore` keeps the documentation pages out. The documentation site is the same project rendered with `quarto render --profile docs` (`_quarto-docs.yml`), and it gains a **Brand guide** (swatches drawn from the theme's CSS variables), slide and PDF examples, and a **Migrating** page. `index.qmd` is now "Get started".
- **CI and Pages.** `.github/workflows/check.yml` runs the Python and R tests and the starter check (`tests/check-starter.sh`: `quarto use template`, then render a page in every format and check that the bundled fonts reach the PDF). `.github/workflows/pages.yml` builds the docs profile and deploys it to GitHub Pages; `docs/` is no longer committed.
- **Housekeeping.** The tracked `_site/` build output and `filetree.txt` are removed.
- Tested: a Quarto 1.11 `contributes.brand` entry does not make a project discover the brand, so `project.brand` is still required (documented).

**0.5.1** — The footer skyline now follows the wfrc.utah.gov footer silhouette.
- The ridge outline is traced from a screenshot of the wfrc.utah.gov footer with `scripts/trace-ridge.py` (snow patches are filled in, the edge is smoothed and reduced to about 70 straight facets, so it is a clean geometric silhouette). It is 120px tall (was 84px) at the screenshot's proportions. Still one flat mask in `$wfrc-ridge-mask`, so light and dark mode are unchanged. Tune `SMOOTH` and `EPS` in the script (higher `EPS` = fewer, larger facets), then re-run with `--write`.
- The generated Wasatch Front ridge of 0.5.0 (`scripts/make-ridge.mjs`) is removed.

**0.5.0** — The footer ridge is now the Wasatch Front skyline.
- The generic zigzag is replaced by the Wasatch Range as seen from the Salt Lake Valley looking east (north left, south right), from Willard Peak to Provo Peak. Peaks sit at their latitude and rise with their elevation, with saddles between them and midpoint-displaced rock detail; Mt Olympus is a steep pyramid, Twin and Lone Peaks are rugged, Timpanogos is a long massif. The ridge was 84px tall (was 46px). It is still a single flat mask filled with the footer color, so light and dark mode need no changes.
- The path is generated by `scripts/make-ridge.mjs` (deterministic; tune `PEAKS`, `SEED`, `ROUGH`, then `node scripts/make-ridge.mjs --write`) into `$wfrc-ridge-mask` in `wfrc-overrides.scss`. The viewBox height in the script and the `::before` height must match.
- Data checked against Wikipedia and SummitPost: Olympus is 9,030 ft (not 9,026), Mt Ogden 9,579 ft, Willard Peak 9,763 ft, Francis Peak ~9,540 ft; Bountiful Peak is at 40.964N, Twin Peaks 40.594N and Box Elder Peak 40.490N. Farmington Peak's coordinates could not be confirmed (40.99N is an estimate).
- No `_quarto.yml` change is required; run `quarto update WFRCAnalytics/wfrc-brand`.

**0.4.1** — The terms template now assumes CC BY 4.0. Content change only.
- `templates/terms.qmd` is rewritten: content by the team is licensed under CC BY 4.0 (with links to the license and legal code); plain-language credit, change-indication and no-endorsement conditions; a "does not cover" section for the WFRC name and logos, third-party data, models and source code; no warranty. The footer link, label and path are unchanged. The wording is still a draft for WFRC communications or legal to confirm.
- **Migration.** Review your `terms/index.qmd` against the new template and add `<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">` to your own `include-in-header` file. Run `quarto update WFRCAnalytics/wfrc-brand`.

**0.4.0** — The footer's "License" link becomes "Terms of use".
- WFRC is a public agency and attaches no license to its material, so the footer label, path and template changed: `wfrc-shared.yml` now links `Terms of use` to `terms/index.qmd`. `templates/license.qmd` (which claimed CC BY-SA 4.0) is replaced by `templates/terms.qmd`: public use, credit and link, a required statement of what you changed, no implied endorsement, third-party data under its own terms, optional Models and Source code sections, no warranty. The wording is a draft for WFRC communications or legal to confirm.
- **Migration.** A site that has `license/index.qmd`: move it to `terms/index.qmd`, add `aliases: [/license/]` to its front matter so old links keep working, and review the text against `templates/terms.qmd` (remove any CC BY-SA statement). Until a site has `terms/index.qmd`, its footer link is dead. Run `quarto update WFRCAnalytics/wfrc-brand`, then render.
- Only the footer changes; no `_quarto.yml` edits are needed.

**0.3.1** — The footer copyright year is no longer hardcoded.
- Added the `{{< year >}}` shortcode (`shortcodes/year.lua`); `wfrc-shared.yml` uses it, so the footer shows the year of the build. Pages rebuild with a full `quarto render`; a page skipped by `freeze` keeps the year it was last rendered with. Sites can use `{{< year >}}` in their own text.

**0.3.0** — Card surface tokens and documentation.
- New brand colors `wfrc-card` (`#E8F5FA`), `wfrc-night-card` (`#17384F`) and `wfrc-night-card-line` (`#2F6286`); roles `$wfrc-card` and `$wfrc-card-line` in the light and dark role maps. Cards were the same tone as `.wfrc-band-alt`, so they vanished on landing pages.
- Grid listing cards, dashboard cards and bslib cards (headers, toolbars, footers) use the card surface and border. CSS variables `--wfrc-card-bg` and `--wfrc-card-line` are exposed for site components.
- Outline buttons inside cards use the link color to hold AA contrast on the light card surface.
- README: card banners need `project.resources` and a page-relative `image:` path; sites should add scripts with `include-in-header` or `include-before-body` (a site `include-after-body` is dropped); new **Footer links** section.
- No `_quarto.yml` change is required. Sites that defined their own card surface (for example `--wfrc-card-bg` in site CSS) can delete it.

**0.2.0** — Callouts, listing cards and shared fixes, moved up from the wfrcanalytics.github.io redesign.
- Callouts now match the design reference: 4px type-color bar, 9% body tint and 16% title strip over the page color, square left and 8px right corners, Inter 700 0.9rem title with 8px 14px padding, body 0.93rem, and a **filled-circle icon** in the type color with the glyph in the page color (replaces Quarto's outline icon).
- Grid listing cards: tinted surface (visible against the page in dark mode), hairline border, overflow hidden, hover lift with shadow (off under reduced motion), `object-fit: cover` images.
- Added `assets/cards/{navy,mid,teal,bright,brick}.svg` banners (use with `image-height: 84px`).
- Added `assets/js/a11y-fixes.html`, included on every page: empty `alt` for listing banners (axe `image-alt`), accessible name and tooltip on the color-scheme toggle, `role="button"` on collapsible callout headers, removal of Plot's invalid `aria-label` on `<g>`, and `tabindex` on scrollable regions.
- Table listings: titles at body size, line-height 1.4, no margin.
- Category chips (`.listing-category`, `.quarto-category`): body color, full opacity, in both modes. Hover now changes the border only, so text keeps its contrast.
- `wfrc-shared.yml`: footer Contact and License links are now site-relative (`contact/index.qmd`, `license/index.qmd`) and no longer open a new tab; added `link-external-newwindow: true` and the accessibility include to `format.html`. Also set on the extension's own `html` and `dashboard` formats.
- Added `templates/contact.qmd` and `templates/license.qmd`.
- **Sites must update their `_quarto.yml`:** delete `link-external-newwindow: true` and their own `decorative-images.html` include (now supplied; leaving them is harmless but redundant); add `contact/index.qmd` and `license/index.qmd` or the footer links 404; and drop site CSS that duplicates the card, table-listing and chip rules.

**0.1.0** — Redesign.
- New palette from the live wfrc.utah.gov tokens: navy `#00395B`, bright blue `#0093C5`, brick `#C85327`, gold `#FEBC46`. Legacy names (`wfrc-blue`, `wfrc-secondary-blue`, `wfrc-yellow`) are kept as aliases. **`wfrc-secondary-blue` changed from `#52b6d5` to `#0093C5`.**
- Dark mode is now a designed palette, not a lightened copy.
- `brand.yml` is the single source for hex codes; the SCSS no longer repeats them (`_wfrc-colors.scss` and `_wfrc-fonts.scss` removed).
- Light and dark SCSS shrank to role maps; all component rules moved to one file, `wfrc-overrides.scss`.
- Cosmo is no longer the light-mode base, so both modes share one Bootstrap base.
- Fixed: org defaults now apply to plain `format: html` through `wfrc-shared.yml`.
- Added: `wfrc-brand-dashboard` format, dashboard value-box and card styling, custom syntax themes, landing-page components, chart helpers, logo alt text, and phone-width fixes for tables and plots.
