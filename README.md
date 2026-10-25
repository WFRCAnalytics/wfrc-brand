# `wfrc-brand` — Quarto brand extension for WFRC Analytics

One design system for every WFRC Analytics Quarto site: colors, type, logos, light and dark mode, and styling for every Quarto component (navbar, callouts, code, tabsets, cards, tables, dashboards, footer). It is built on Posit's [`brand.yml`](https://posit-dev.github.io/brand-yml/) and Quarto's own theming, so it only uses what Quarto can render. There is no JavaScript.

The look is WFRC's marketing site brought to analytics density: Inter headings with Poppins body text, flat navy, blue and brick color blocks, pill buttons, 10px cards, and a ridge line above the footer. Hex codes come from the live wfrc.utah.gov site.

Requires [Quarto](https://quarto.org/docs/get-started/) 1.8 or later (tested on 1.10).

---

## Install

From the root of a Quarto project:

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

For a standalone document outside a website, `format: wfrc-brand-html` (adds numbered sections, KaTeX, code links) and `format: wfrc-brand-typst` are also available.

> **Why dashboards use their own format name.** Quarto only applies an extension's `contributes.formats.*` to the extension's own named formats, never to plain `html`. That is why HTML defaults live in `wfrc-shared.yml` (loaded with `metadata-files`) and dashboards use `wfrc-brand-dashboard`. Do not add a `dashboard:` key to `wfrc-shared.yml` or a project-level metadata file: in Quarto 1.10 it breaks the announcement banner render on every HTML page.

---

## What you get automatically

| Area | Result |
|---|---|
| **Theme** | One Bootstrap base for both modes. Light and dark are separate designs, not an inversion. Follows the visitor's OS setting, with a toggle in the navbar. |
| **Type** | Poppins body 16px/1.6, Inter headings and navbar, Fira Code for code. All from Google Fonts. |
| **Logos** | The brand logo set switches by mode (color on light, white on dark) and carries alt text. |
| **Navbar** | Page-colored with a hairline, Inter 600 links, uppercase site title, bright-blue underline on hover and for the current page. |
| **Buttons** | Pill shaped. `.btn-primary` is the AA-safe action blue. |
| **Cards** | Listings, dashboards and bslib cards: 10px radius, hairline border, soft shadow, Inter header row. |
| **Callouts** | Five types with a 4px colored edge and a tinted title strip. Text stays in the ink color. |
| **Code** | Cool-tinted blocks, no ligatures, custom syntax palette (`wfrc-light.theme`, `wfrc-dark.theme`) that holds AA contrast. |
| **Tabsets** | The active tab and its pane share one surface. |
| **Tables** | No vertical rules, bright-blue header rule, tabular numerals, scroll inside their own box on phones. |
| **TOC and sidebar** | Active item marked with a bright-blue edge. |
| **Footer** | Navy with a ridge line. The ridge is a CSS mask, so it follows each mode's color. |
| **Dashboards** | Flat navy, mid-blue, teal and brick value boxes in both modes; transparent Observable Plot charts. |
| **Org defaults** | Social menu, footer, `axe` accessibility checking, `page-layout: full`, TOC, smooth scroll, freeze `auto`, knitr and jupyter engines. |

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
| `.wfrc-chip` | Small pill label. |

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
├── _extension.yml        wfrc-brand-html / -dashboard / -typst formats (same theme list as wfrc-shared.yml)
├── brand.yml             the ONLY place hex codes are written (palette, type, logos, light/dark roles)
├── wfrc-shared.yml       org defaults loaded with metadata-files: theme, layout, navbar, footer, freeze
└── assets/
    ├── theme/
    │   ├── wfrc.scss             shared structure: layout and sizing, no color
    │   ├── wfrc-light.scss       role map for light: each role points at a brand.yml palette name
    │   ├── wfrc-dark.scss        role map for dark
    │   ├── wfrc-overrides.scss   every Quarto component rule, written once for both modes
    │   └── wfrc-{light,dark}.theme   syntax highlighting palettes (Pandoc format)
    ├── charts/                   R, Python and Observable JS helpers
    └── logo/
```

**Theme layers**, low to high priority: `wfrc.scss`, `wfrc-light|dark.scss`, `wfrc-overrides.scss`, then the `brand` keyword. Putting `brand` last is what makes `$brand-*` Sass variables (and `$primary`, `$background`) available in the files above it, so the SCSS never writes a hex code.

**One source for colors.** `brand.yml` defines the palette. Quarto turns every entry into `$brand-<name>` for Sass and `--brand-<name>` for CSS. The mode files map *roles* (surface, line, heading, link, action, callout colors) to those names. `wfrc-overrides.scss` uses only roles, which is why it has almost no light/dark branching.

The two exceptions are the Pandoc syntax themes (`.theme` JSON cannot reference `brand.yml`) and the helpers' small role lookups. When you change a palette color used there, update both.

### Design tokens

| Role | Light | Dark |
|---|---|---|
| Page | `#FFFFFF` | `#0A1F2E` |
| Alternate band / raised surface | `#F4F2EF` / `#EAF0F4` | `#0E2738` / `#17384F` |
| Card | `#FFFFFF` | `#122E46` |
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

Use the [wfrcanalytics.github.io](https://github.com/WFRCAnalytics/wfrcanalytics.github.io) site as the model.

1. `quarto add WFRCAnalytics/wfrc-brand`, then add the `brand` and `metadata-files` lines from **Install**.
2. Delete the site's own `_brand.yml`, custom theme SCSS, `format.html.theme`, `css:` and `include-in-header` font preloads.
3. **Remove anything `wfrc-shared.yml` already supplies.** Quarto lists *append* across config levels, so a site that also defines its own "Follow Us" menu, GitHub tools menu or footer links shows them twice.
4. Keep what is yours: `website.title`, `site-url`, `navbar.left`, the sidebars, announcements, and per-site GitHub links.
5. Pages that used the old `index.scss` classes (`#bio`, `#landing-icons`, `.name-highlight`) still work. New pages can use the `.wfrc-*` components above.
6. Render, then clear the cache if styles look stale (see below).

### Accessibility checklist

The extension keeps `axe: true` on. In a pass over the preview pages and real site pages, everything the theme controls passes WCAG 2 AA contrast in both modes. These items depend on your content and config:

- **Logo alt text** is set in `brand.yml`. If you override the navbar logo, give it an `alt`.
- **Icon-only tools menus** need `text:` (it becomes the `aria-label`), as in `wfrc-shared.yml`.
- **Images** on about pages and elsewhere need `alt` text.
- Observable Plot's `<g aria-label>` and Quarto's collapsed-callout `aria-expanded` are reported by axe but come from those libraries.

---

## Known limits

- **Hero and band sections cover the TOC.** Use them on `toc: false` pages.
- **Dashboards** need `format: wfrc-brand-dashboard`; setting `format: dashboard` gives Quarto's default look.
- **RevealJS** is not themed by this extension. **Typst and Word** pick up brand colors and fonts through `brand.yml` only. The Typst render was checked for errors, not for appearance.
- **R helpers.** The palette lookup is tested; the ggplot2 theme was written but not run in the environment used to build this release (ggplot2 was not installed).
- **No numbered sections by default** in websites. Set `number-sections: true` per site, or use `wfrc-brand-html`.

---

## Maintaining this repo

| To change | Edit |
|---|---|
| A color, logo or font | `brand.yml` (and the `.theme` files if it is a syntax color) |
| Which palette name a role uses | `wfrc-light.scss`, `wfrc-dark.scss` |
| How a Quarto component looks | `wfrc-overrides.scss` (sections are numbered at the top) |
| Layout or sizing that is the same in both modes | `wfrc.scss` |
| Org-wide site defaults | `wfrc-shared.yml` (and keep `_extension.yml`'s theme list in step) |

Preview: `quarto preview` renders [`example.qmd`](example.qmd) (every component), [`example-landing.qmd`](example-landing.qmd) and [`example-dashboard.qmd`](example-dashboard.qmd). Check each in light and dark, and at phone width.

**Clearing the Sass cache.** Quarto caches compiled SCSS in `.quarto/`. If a style change does not show, delete that folder and render again (`rmdir /s /q .quarto` on Windows, `rm -rf .quarto` elsewhere).

**Versioning.** Bump `version` in `_extension.yml` on every meaningful change. Downstream sites update with `quarto update WFRCAnalytics/wfrc-brand`.

### Changelog

**0.1.0** — Redesign.
- New palette from the live wfrc.utah.gov tokens: navy `#00395B`, bright blue `#0093C5`, brick `#C85327`, gold `#FEBC46`. Legacy names (`wfrc-blue`, `wfrc-secondary-blue`, `wfrc-yellow`) are kept as aliases. **`wfrc-secondary-blue` changed from `#52b6d5` to `#0093C5`.**
- Dark mode is now a designed palette, not a lightened copy.
- `brand.yml` is the single source for hex codes; the SCSS no longer repeats them (`_wfrc-colors.scss` and `_wfrc-fonts.scss` removed).
- Light and dark SCSS shrank to role maps; all component rules moved to one file, `wfrc-overrides.scss`.
- Cosmo is no longer the light-mode base, so both modes share one Bootstrap base.
- Fixed: org defaults now apply to plain `format: html` through `wfrc-shared.yml`.
- Added: `wfrc-brand-dashboard` format, dashboard value-box and card styling, custom syntax themes, landing-page components, chart helpers, logo alt text, and phone-width fixes for tables and plots.

---

## References

- [Quarto brand extensions](https://quarto.org/docs/extensions/brand.html) · [`brand.yml` spec](https://posit-dev.github.io/brand-yml/) · [HTML themes and Sass variables](https://quarto.org/docs/output-formats/html-themes.html) · [Dashboards](https://quarto.org/docs/dashboards/)
