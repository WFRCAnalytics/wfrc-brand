# `wfrc-brand` — Quarto brand extension for WFRC Analytics

One design system for every WFRC Analytics Quarto site: colors, type, logos, light and dark mode, and styling for every Quarto component (navbar, callouts, code, tabsets, cards, tables, dashboards, footer). It is built on Posit's [`brand.yml`](https://posit-dev.github.io/brand-yml/) and Quarto's own theming, so it only uses what Quarto can render. Quarto uses `brand.yml`; Shiny, R and Python use its flat twin `brand-flat.yml` (see **Shiny, R and Python**). The theme itself has no JavaScript.

**Documentation and starter:** <https://wfrcanalytics.github.io/wfrc-brand> (brand guide, examples, migration guide). This repo is also the starter template.

The look is WFRC's marketing site brought to analytics density: Inter headings with Poppins body text, flat navy, blue and brick color blocks, pill buttons, 10px cards, and a ridge line above the footer. Hex codes come from the live wfrc.utah.gov site.

Requires [Quarto](https://quarto.org/docs/get-started/) 1.8 or later (tested on 1.11).

---

## Install

**A new site:** start from the template. It installs the extension and adds `_quarto.yml`, a home page, and the `contact/` and `terms/` pages the footer links to.

```bash
mkdir my-site && cd my-site
quarto use template WFRCAnalytics/wfrc-brand
```

**An existing project** (see also the [migration guide](https://wfrcanalytics.github.io/wfrc-brand/migrate.html)):

```bash
quarto add WFRCAnalytics/wfrc-brand
```

Then your `_quarto.yml` needs these lines, plus whatever is specific to your site:

```yaml
project:
  type: website
  brand: _extensions/wfrc-brand/brand.yml      # required; Quarto does not discover brand.yml inside an extension

metadata-files:
  - _extensions/wfrc-brand/wfrc-shared.yml     # theme, highlight style, layout, navbar social menu, footer

website:
  title: "Your Site"
  site-url: "https://wfrcanalytics.github.io/your-site"
```

That is the whole setup: this repo's own [`_quarto.yml`](_quarto.yml) is the reference.

For a **dashboard** page, use the extension's dashboard format:

```yaml
---
title: "Transit ridership"
format: wfrc-brand-dashboard
---
```

Other formats work the same way:

| Format | Output |
|---|---|
| `wfrc-brand-revealjs` | Slides: brand colors, fonts and logo, brick title-slide bar, bright-blue slide rule. Light only. |
| `wfrc-brand-typst` | PDF report: US Letter, brand logo, colors and fonts. |
| `wfrc-brand-html` | A standalone HTML document outside a website (numbered sections, KaTeX, code links). |
| `wfrc-brand-dashboard` | Dashboards. |

> **Why dashboards use their own format name.** Quarto only applies an extension's `contributes.formats.*` to the extension's own named formats, never to plain `html`. That is why HTML defaults live in `wfrc-shared.yml` (loaded with `metadata-files`) and dashboards use `wfrc-brand-dashboard`. Do not add a `dashboard:` key to `wfrc-shared.yml` or a project-level metadata file: in Quarto 1.10 it breaks the announcement banner render on every HTML page.

---

## What you get automatically

| Area | Result |
|---|---|
| **Theme** | One Bootstrap base for both modes. Light and dark are separate designs, not an inversion. Follows the visitor's OS setting, with a toggle in the navbar. |
| **Type** | Poppins body 16px/1.6, Inter headings and navbar, Fira Code for code. From Google Fonts by default; `brand-offline.yml` bundles the files (see **Fonts**). |
| **Logos** | The brand logo set switches by mode (color on light, white on dark) and carries alt text. |
| **Navbar** | Page-colored with a hairline, Inter 600 links, uppercase site title, bright-blue underline on hover and for the current page. |
| **Buttons** | Pill shaped. `.btn-primary` is the AA-safe action blue. |
| **Cards** | Listings, dashboards and bslib cards: 10px radius, hairline border, soft shadow, Inter header row. All cards share one light-blue (dark: raised-navy) surface, set apart from the page and from `.wfrc-band-alt`. Grid listing cards add a banner image and a hover lift (see **Card banners**). |
| **Callouts** | Five types: a 4px bar in the type color, a 9% tinted body, a 16% title strip, 8px radius on the right, and a filled-circle icon with the glyph cut out in the page color. Text stays in the ink color. |
| **Code** | Cool-tinted blocks, no ligatures, custom syntax palette (`wfrc-light.theme`, `wfrc-dark.theme`) that holds AA contrast. |
| **Tabsets** | The active tab and its pane share one surface. |
| **Tables** | No vertical rules, bright-blue header rule, tabular numerals, scroll inside their own box on phones. |
| **TOC and sidebar** | Active item marked with a bright-blue edge. |
| **Footer** | Navy with the Wasatch Front skyline. The ridge is a CSS mask, so it follows each mode's color. |
| **Dashboards** | Flat navy, mid-blue, teal and brick value boxes in both modes; transparent Observable Plot charts. |
| **Org defaults** | Social menu, footer, external links open in a new tab, `axe` accessibility checking, an accessibility script (decorative listing banners, toggle name, Plot and collapsed-callout ARIA, keyboard-reachable scroll regions), `page-layout: full`, TOC, smooth scroll, freeze `auto`, knitr and jupyter engines. |

---

## Fonts

`brand.yml` loads Poppins, Inter and Fira Code from Google Fonts. For offline builds or no request to a third party, point the project at the offline brand, which is the same file with the fonts bundled in `assets/fonts/` (SIL OFL; woff2 for the web, ttf for Typst):

```yaml
project:
  brand: _extensions/wfrc-brand/brand-offline.yml
```

Quarto 1.11 does not copy bundled fonts for revealjs, so slides always use `brand.yml` (Google Fonts). `brand-offline.yml` is generated: edit `brand.yml`, then run `python scripts/build-brand-variants.py`. `scripts/fetch-fonts.py` re-downloads the font files.

---

## Shiny, R and Python

`brand.yml` uses `light:`/`dark:` values, which Quarto 1.8 added. The R and Python brand.yml packages (so Shiny, bslib and great-tables) do not understand them and reject the file. `brand-flat.yml` is the same brand with each pair replaced by its light value, generated by `scripts/build-brand-variants.py`:

```r
# Shiny for R
bslib::bs_theme(brand = "_extensions/wfrc-brand/brand-flat.yml")
```

```python
# Shiny for Python (pip install "shiny[theme]")
ui.Theme.from_brand("_extensions/wfrc-brand/brand-flat.yml")
```

Checked with the official `brand-yml` Python package (schema), `shiny` 1.9 and R's `brand.yml` and `bslib`.

---

## Card banners

Grid listings (`type: grid`) get the card surface (`wfrc-card` / `wfrc-night-card`), a hairline border and a hover lift (disabled under `prefers-reduced-motion`). Five banner images with contour lines echoing `.wfrc-hero` ship in `assets/cards/`: `navy`, `mid`, `teal`, `bright` and `brick`. Use them as the listing `image:` and set a short `image-height`:

```yaml
listing:
  type: grid
  image-height: 84px
  contents:
    - title: Reliability atlas
      path: atlas/index.qmd
      image: _extensions/wfrc-brand/assets/cards/navy.svg
      categories: [Live, App]
```

**Quarto does not copy extension files into the output**, so a site must publish the banners itself. Add this to `_quarto.yml`, or the images 404 where the page does not resolve them (CSS `url()`, previews, pages that reference them directly):

```yaml
project:
  resources:
    - _extensions/wfrc-brand/assets/cards/*.svg
```

The `image:` path in a listing is relative to the page. For a page in a subfolder, go up to the project root: `../_extensions/wfrc-brand/assets/cards/navy.svg`.

> In a test render with `site-url` set, Quarto 1.10 rewrote listing images to `<site-url>/site_libs/quarto-contrib/...` and copied the files there, so listings worked even without `resources`. That URL points at the live site, which is why images 404 locally or before the first deploy. `resources` is the reliable fix.

**Card colors.** `brand.yml` defines `wfrc-card` (`#E8F5FA`, bright blue 9% over white) and `wfrc-night-card` (`#17384F`), with the card border `wfrc-night-card-line` (`#2F6286`) on dark; on light the border is bright blue mixed 24% into the hairline. The theme exposes them as CSS variables, `--wfrc-card-bg` and `--wfrc-card-line`, so a site's own cards can match:

```css
.my-tile { background: var(--wfrc-card-bg); border: 1px solid var(--wfrc-card-line); }
```

Outline buttons inside `.card` use the link color, because the action blue falls below AA on the light card surface.

Banners are decorative. Quarto drops `image-alt: ""`, so the bundled script (`assets/js/a11y-fixes.html`, included through `wfrc-shared.yml`) sets an empty `alt` on them after render. Table listings keep titles at body size, and category chips use the body color at full opacity so they pass AA in both modes.

---

## Site scripts

`wfrc-shared.yml` sets `format.html.include-after-body` to the accessibility script. Quarto does not merge two `include-after-body` values here: when a site sets its own in `_quarto.yml`, only one applies (in a test render the extension's script won and the site's was dropped).

**Sites should add their own scripts with `include-in-header` or `include-before-body`, not `include-after-body`.** A site that sets both `include-in-header` and `include-before-body` alongside the shared defaults keeps both, and the accessibility script still loads (verified in a Quarto 1.10 test render).

---

## Footer links

The shared footer (`wfrc-shared.yml`) links to `contact/index.qmd` (label "Contact") and `terms/index.qmd` (label "Terms of use") with site-relative paths. The pages are expected to exist: copy `_extensions/wfrc-brand/templates/contact.qmd` and `terms.qmd` to `contact/index.qmd` and `terms/index.qmd`. The templates are meant to be edited per site; the terms wording is a draft that WFRC communications or legal should confirm before a site publishes it. A site without these pages gets dead links.

**License.** Since 0.4.1 the terms template assumes the content is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). CC BY 4.0 already covers what the earlier draft asked for in custom words: it requires credit, requires users to indicate if they modified the material and to keep earlier indications of modification, and forbids implying that the licensor endorses them. CC licenses do not cover trademarks (the WFRC name and logo) and Creative Commons advises against using them for software, so the template excludes both, along with third-party data and models.

A site that wants a different license edits its `terms/index.qmd`. The extension does not add a `rel="license"` tag through `include-in-header`, because a site's own `include-in-header` replaces the extension's. Sites should add `<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">` in their own `include-in-header` file.

A site that does not want them must override the footer, but **setting `website.page-footer.right` in `_quarto.yml` does not replace the list**: Quarto appends it, so the site's links appear next to Contact and Terms of use (verified in a Quarto 1.10 test render). To drop the two links, keep a local copy of `wfrc-shared.yml` with the `right:` block edited and point `metadata-files` at the copy.

---

## Landing-page components

Quarto has no hero or color-block component, so the extension adds a few classes. Use them with Pandoc divs. Full-bleed sections need Quarto's `.column-screen`, and because a full-width hero covers the right-hand TOC, **use them on pages with `toc: false`**. The full example is [`example-landing.qmd`](example-landing.qmd).

```markdown
::: {.wfrc-hero .column-screen}
# Finding the gaps in the Wasatch Front [bike network.]{.accent}

Short supporting paragraph.

[Open the dashboard](#){.btn .btn-light} [Read the methods](#){.btn .btn-outline-light}
:::

::: {.wfrc-band .column-screen}
## What's in this project

::: {.wfrc-blocks}
::: {.wfrc-block}
### Dashboard
Description.

[Open](#){.btn .btn-sm}
:::
::: {.wfrc-block .mid}
...
:::
::: {.wfrc-block .brick}
...
:::
:::
:::
```

| Class | Purpose |
|---|---|
| `.wfrc-hero` | Navy gradient hero with faint contour lines. `[text]{.accent}` makes a gold highlight. |
| `.wfrc-band`, `.wfrc-band-alt` | Full-width bright-blue band, and a quiet taupe band. |
| `.wfrc-blocks` + `.wfrc-block` (`.mid`, `.teal`, `.brick`) | A row of flat color blocks. |
| `.wfrc-keyfacts` | One bordered strip of key numbers. Each child div holds a bold number and a label. |
| `.wfrc-updates` + `[Oct 21]{.wfrc-date}` | A dated update list with brick date tiles. |
| `.wfrc-chip` | Small pill label. Add `.chip-live`, `.chip-internal` or `.chip-archived` for a status. |
| `.wfrc-stat-num` | A large number inside a `.wfrc-block`. |
| `.wfrc-cite` | A quiet aside with a bright-blue rule, for "How to cite". |
| `.wfrc-shot` | A screenshot with a hairline border and rounded corners. |

---

## Charts

The categorical chart palette has **five colors** in a fixed order (blue, orange, violet, gold, teal). It passes lightness, chroma and color-vision checks. Never cycle past five: facet, or group the rest as "Other". Gold is below 3:1 on white, so always label series directly instead of relying on a legend.

All three helpers read colors from `brand.yml` or the theme's CSS variables, so nothing is duplicated.

**R** (ggplot2):

```r
source("_extensions/wfrc-brand/assets/charts/wfrc-charts.R")
ggplot(df, aes(date, value, color = mode)) +
  geom_line() + theme_wfrc() + scale_color_wfrc()      # mode = "dark" for dark pages
```

**Python** (matplotlib, plotly):

```python
import sys; sys.path.append("_extensions/wfrc-brand/assets/charts")
import wfrc_charts as wfrc
wfrc.use_style()                                         # matplotlib
fig.update_layout(template=wfrc.plotly_template())       # plotly
```

**Observable JS** (follows light and dark automatically):

```js
// inside an OJS code cell
import {wfrcPlot} from "./_extensions/wfrc-brand/assets/charts/wfrc-charts.js"
wfrcPlot({Plot, marks: [Plot.lineY(data, {x: "date", y: "value", stroke: "mode"})]})
```

The CSS variables `--wfrc-chart-1` to `--wfrc-chart-5` are available to any custom JavaScript.

---

## How it is built

```
_extensions/wfrc-brand/
├── _extension.yml        wfrc-brand-html / -dashboard / -revealjs / -typst formats
├── brand.yml             the ONLY place hex codes are written (palette, type, logos, light/dark roles)
├── brand-offline.yml     generated from brand.yml, with bundled fonts
├── brand-flat.yml        generated from brand.yml, light values only, for Shiny, R and Python
├── wfrc-shared.yml       org defaults loaded with metadata-files: theme, layout, navbar, footer, freeze
└── assets/
    ├── theme/
    │   ├── wfrc.scss             shared structure: layout and sizing, no color
    │   ├── wfrc-light.scss       role map for light: each role points at a brand.yml palette name
    │   ├── wfrc-dark.scss        role map for dark
    │   ├── wfrc-overrides.scss   every Quarto component rule, written once for both modes
    │   ├── wfrc-revealjs.scss    slide shape
    │   └── wfrc-{light,dark}.theme   syntax highlighting palettes (Pandoc format)
    ├── fonts/                    Poppins, Inter, Fira Code (woff2 and ttf)
    ├── charts/                   R, Python and Observable JS helpers
    └── logo/
```

The repo root is the starter project (`_quarto.yml`, `index.qmd`, `contact/`, `terms/`). `_quarto-docs.yml` is the profile that adds the documentation pages for this repo's own site; `.quartoignore` keeps them out of new sites.

**Theme layers**, low to high priority: `wfrc.scss`, `wfrc-light|dark.scss`, `wfrc-overrides.scss`, then the `brand` keyword. Putting `brand` last is what makes `$brand-*` Sass variables (and `$primary`, `$background`) available in the files above it, so the SCSS never writes a hex code.

**One source for colors.** `brand.yml` defines the palette. Quarto turns every entry into `$brand-<name>` for Sass and `--brand-<name>` for CSS. The mode files map *roles* (surface, line, heading, link, action, callout colors) to those names. `wfrc-overrides.scss` uses only roles, which is why it has almost no light/dark branching.

The two exceptions are the Pandoc syntax themes (`.theme` JSON cannot reference `brand.yml`) and the helpers' small role lookups. When you change a palette color used there, update both.

### Design tokens

| Role | Light | Dark |
|---|---|---|
| Page | `#FFFFFF` | `#0A1F2E` |
| Alternate band / raised surface | `#F4F2EF` / `#EAF0F4` | `#0E2738` / `#17384F` |
| Card (`--wfrc-card-bg`) / card border (`--wfrc-card-line`) | `#E8F5FA` / `#A5CEDD` | `#17384F` / `#2F6286` |
| Text / secondary text | `#16232C` / `#4F5E69` | `#E8EEF2` / `#A3B8C6` |
| Hairline | `#D9E0E5` | `#264A63` |
| Heading 1 / headings 2–6 | `#00395B` / `#2C6788` | `#BFE6F5` / `#8FCBE6` |
| Link / hover | `#00395B` / `#00799F` | `#5CC4E8` / `#A6E0F3` |
| Action (buttons) | `#00799F` | `#5CC4E8` |
| Bright blue (rules, focus rings, large fills) | `#0093C5` | `#0093C5` |
| Brick accent / brick that holds white text | `#C85327` / `#B4461F` | `#E06A3A` / `#8F3A1C` |
| Gold | `#FEBC46` | `#FEBC46` |

**Contrast rules the system follows.** The live site's bright blue `#0093C5` is 3.51:1 against white, below AA for text. It is used only for rules, focus rings and large fills. Buttons and interactive fills use `#00799F` (4.96:1). Brick `#C85327` is 4.45:1, so any brick fill that carries small white text uses `#B4461F` (5.47:1).

---

## Migrating an existing site

The [migration guide](https://wfrcanalytics.github.io/wfrc-brand/migrate.html) covers moving from 0.x (what 1.0 removed) and from a site with its own theme. In short: `quarto add WFRCAnalytics/wfrc-brand` (or start from the template), add the `project.brand` and `metadata-files` lines from **Install**, delete your own theme, CSS and font links, remove config that `wfrc-shared.yml` already supplies (Quarto lists append), keep your title, navbar and sidebars, add `contact/index.qmd` and `terms/index.qmd`, then render and check light and dark.

### Accessibility checklist

The extension keeps `axe: true` on. In a pass over the preview pages and real site pages, everything the theme controls passes WCAG 2 AA contrast in both modes. These items depend on your content and config:

- **Logo alt text** is set in `brand.yml`. If you override the navbar logo, give it an `alt`.
- **Icon-only tools menus** need `text:` (it becomes the `aria-label`), as in `wfrc-shared.yml`.
- **Images** on about pages and elsewhere need `alt` text.
- Observable Plot's `<g aria-label>`, Quarto's collapsed-callout `aria-expanded` and scrollable regions are reported by axe but come from those libraries; `assets/js/a11y-fixes.html` repairs them at load, so axe runs clean on the preview pages.

---

## Known limits

- **Hero and band sections cover the TOC.** Use them on `toc: false` pages.
- **Dashboards** need `format: wfrc-brand-dashboard`; setting `format: dashboard` gives Quarto's default look.
- **Slides are light only** (Reveal.js has no color-scheme toggle) and use Google Fonts even with `brand-offline.yml`. **Word** picks up brand colors and fonts through `brand.yml` only. The bundled fonts are checked in Typst with system fonts ignored.
- **R helpers.** The palette lookup is tested; the ggplot2 theme was written but not run in the environment used to build this release (ggplot2 was not installed).
- **No numbered sections by default** in websites. Set `number-sections: true` per site, or use `wfrc-brand-html`.

---

## Maintaining this repo

| To change | Edit |
|---|---|
| A color, logo or font | `brand.yml` (and the `.theme` files if it is a syntax color), then `python scripts/build-brand-variants.py` |
| Which palette name a role uses | `wfrc-light.scss`, `wfrc-dark.scss` |
| How a Quarto component looks | `wfrc-overrides.scss` (sections are numbered at the top) |
| How slides look | `wfrc-revealjs.scss` |
| Layout or sizing that is the same in both modes | `wfrc.scss` |
| Org-wide site defaults | `wfrc-shared.yml` (and keep `_extension.yml`'s theme list in step) |
| What a new site starts with | `_quarto.yml`, `index.qmd`, `contact/`, `terms/` |
| Documentation pages | `brand-guide.qmd`, `migrate.qmd`, `example*.qmd`, `_quarto-docs.yml` (add new docs-only files to `.quartoignore`) |

Run the checks with `pytest tests` (needs `pyyaml`, `matplotlib`, and optionally `plotly`, `brand-yml` and `shiny[theme]`) and `Rscript tests/test-charts.R`; CI also renders the starter. Preview the documentation site with `quarto preview --profile docs`. GitHub Actions builds it with `quarto render --profile docs` and publishes it to GitHub Pages on every push to `main` (`docs/` is build output and is not committed); a pull request builds it without deploying. Check each page in light and dark, and at phone width. Without `--profile docs`, Quarto renders the starter.

**Clearing the Sass cache.** Quarto caches compiled SCSS in `.quarto/`. If a style change does not show, delete that folder and render again (`rmdir /s /q .quarto` on Windows, `rm -rf .quarto` elsewhere).

**Versioning.** Bump `version` in `_extension.yml` and add an entry to [`CHANGELOG.md`](CHANGELOG.md) on every meaningful change. Downstream sites update with `quarto update WFRCAnalytics/wfrc-brand`.

---

## References

- [Quarto brand extensions](https://quarto.org/docs/extensions/brand.html) · [`brand.yml` spec](https://posit-dev.github.io/brand-yml/) · [HTML themes and Sass variables](https://quarto.org/docs/output-formats/html-themes.html) · [Dashboards](https://quarto.org/docs/dashboards/)
