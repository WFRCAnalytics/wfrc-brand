# `wfrc-brand` Quarto Brand Extension for Wasatch Front Regional Council

A [Quarto brand extension](https://quarto.org/docs/extensions/brand.html) that applies the Wasatch Front Regional Council (WFRC) visual identity — colors, typography, logos, light/dark theming, and org-wide site defaults — to any WFRC Quarto website with a single command.

---

## Why This Extension Exists

Every WFRC analytics website needs the same foundation: brand colors, fonts, logos, footer, social links, and dark/light mode support. Without a shared extension, each project manually duplicates all of this — and any brand update has to be applied to every repo individually.

This extension solves that by centralizing the brand layer in one place. Benefits:

- **Install once, stay consistent.** One `quarto add` command applies the full WFRC identity to any project — no copying SCSS files or pasting footer YAML between repos.
- **Light and dark mode out of the box.** The theme automatically switches between modes based on the visitor's system preference using [`respect-user-color-scheme`](https://quarto.org/docs/output-formats/html-themes.html#dark-mode). Light mode uses the GitHub syntax highlighting theme; dark mode uses Dracula.
- **Brand-managed logos.** The [`brand.yml` logo spec](https://posit-dev.github.io/brand-yml/brand/logo.html) serves the correct logo variant (horizontal color, horizontal white, stacked, abbreviated) for each context and color mode automatically — no manual `logo:` path in each project.
- **Centralized updates.** Fix a color, update a font, or add a new social link in this repo and every downstream project picks it up on the next `quarto update`.
- **Quarto-native approach.** Built on the official [Quarto extensions system](https://quarto.org/docs/extensions/) and [brand.yml spec](https://posit-dev.github.io/brand-yml/) — not a workaround. Fully supported and forward-compatible.

---

## What Gets Applied Automatically

When a project installs this extension, the following are contributed automatically via [`_extension.yml`](https://quarto.org/docs/extensions/creating.html) — no configuration needed in the project's `_quarto.yml`:

| Category | What's applied |
|---|---|
| **Theme** | Cosmo base + WFRC SCSS (light and dark) |
| **Syntax highlighting** | GitHub (light) / Dracula (dark) |
| **Color scheme** | Respects system dark/light preference |
| **Brand colors** | `wfrc-blue`, `wfrc-secondary-blue`, `wfrc-yellow`, `wfrc-gray`, RTP colors, Wasatch Choice colors |
| **Typography** | Poppins (body), Inter (headings/navbar), Fira Code (monospace) — loaded from Google Fonts |
| **Logos** | Light/dark variants auto-selected per context |
| **Favicon** | WFRC abbreviated logo |
| **Footer left** | © WFRC copyright with link to wfrc.utah.gov |
| **Footer center** | Social icons: GitHub, Facebook, X, Instagram, LinkedIn, YouTube |
| **Footer right** | Contact and License links → `wfrcanalytics.github.io` (absolute URLs, no local pages required) |
| **Navbar** | Follow Us social dropdown menu |
| **Twitter/OG card** | `@wasatchcouncil` metadata for social sharing |
| **Output directory** | `docs/` (GitHub Pages standard) |
| **Project type** | `website` |
| **Freeze** | `auto` (only re-execute if file changed) |
| **Layout** | `page-layout: full`, `toc: true`, `grid.sidebar-width: 350px` |
| **Accessibility** | `axe: true` (automated accessibility checking) |

---

## Installation

Requires [Quarto](https://quarto.org/docs/get-started/) ≥ 1.8.0.

In the terminal, from the root of your Quarto project:

```bash
quarto add WFRCAnalytics/wfrc-brand
```

This installs the extension into `_extensions/wfrc-brand/`. The full brand is immediately active — no further configuration required for a basic site.

---

## Minimal Project Setup

After installation, your project's `_quarto.yml` only needs the things that differ per site:

```yaml
project:
  type: website
  output-dir: docs
  brand: _extensions/wfrc-brand/brand.yml  # explicit path for dev correctness

website:
  title: "Your Site Title"
  site-url: "https://wfrcanalytics.github.io/your-site"

  # Optional: per-deployment announcement banner
  announcement:
    icon: info-circle
    dismissable: true
    content: "Site under development."
    type: primary
    position: below-navbar

  # The full footer (left, center, right) is contributed by the extension.
  # Contact → wfrcanalytics.github.io/contact
  # License → wfrcanalytics.github.io/license
  # Only define page-footer here if this site needs different right-column links.
  # IMPORTANT: defining any page-footer key replaces the entire block —
  # you must repeat left and center alongside any custom right entries.
  # page-footer:
  #   left: "© 2025 [Wasatch Front Regional Council](https://wfrc.utah.gov/)"
  #   center: [ ...social icons... ]
  #   right:
  #     - text: Custom Page
  #       href: custom.qmd
  # Navbar tools: per-site GitHub repo links
  # IMPORTANT: defining navbar.tools here means you must also repeat
  # logo-alt and navbar.right (Follow Us) — Quarto replaces the entire
  # navbar block, not individual keys.
  navbar:
    logo-alt: "Wasatch Front Regional Council"
    right:
      - text: Follow Us
        menu:
          - icon: facebook
            text: Facebook
            href: https://www.facebook.com/WasatchFrontRegionalCouncil
            target: _blank
          - icon: twitter-x
            text: X (Twitter)
            href: https://twitter.com/wasatchcouncil
            target: _blank
          - icon: instagram
            text: Instagram
            href: https://www.instagram.com/wasatchfrontregionalcouncil/
            target: _blank
          - icon: linkedin
            text: LinkedIn
            href: https://www.linkedin.com/company/wasatch-front-regional-council
            target: _blank
          - icon: youtube
            text: YouTube
            href: https://www.youtube.com/user/wfrcvideo
            target: _blank
    tools:
      - icon: github
        menu:
          - text: Source Code
            href: https://github.com/WFRCAnalytics/your-repo
            target: _blank
          - text: Report a Bug
            href: https://github.com/WFRCAnalytics/your-repo/issues/new
            target: _blank

format:
  html:
    # Repeat theme here with full paths so the dev project resolves correctly.
    # Downstream installs get this from the extension automatically.
    axe: true
    page-layout: full
    grid:
      sidebar-width: 350px
    toc: true
    respect-user-color-scheme: true
    highlight-style:
      light: github
      dark: dracula
    theme:
      light:
        - cosmo
        - _extensions/wfrc-brand/assets/theme/wfrc.scss
        - _extensions/wfrc-brand/assets/theme/wfrc-light.scss
      dark:
        - _extensions/wfrc-brand/assets/theme/wfrc.scss
        - _extensions/wfrc-brand/assets/theme/wfrc-dark.scss
```

> **Note on `brand.yml`:** The `project.brand` line is needed in the dev project (`_quarto.yml`) because Quarto's `contributes.metadata` mechanism resolves paths relative to the project root, not the extension folder. Downstream installs resolve this correctly without it — but it doesn't hurt to include it.

---

## Important: YAML Merge Behavior

Quarto merges extension metadata into your project config, but **lists and maps replace rather than append**. This has two practical consequences:

**`navbar`** — If you define `navbar.tools` in your project, Quarto replaces the entire `navbar` block from the extension. You must also repeat `logo-alt` and `navbar.right` (the Follow Us menu) in your project's `_quarto.yml`.

**`page-footer`** — If you define any key under `page-footer` (e.g. `right`), Quarto replaces the entire `page-footer` block. You must repeat `left` and `center` alongside your `right` entries.

Projects that define **neither** `navbar` nor `page-footer` in their `_quarto.yml` get the full extension contribution automatically with no repetition needed.

---

## Repository Structure

```
wfrc-brand/
├── _quarto.yml                          # Dev project config (not shipped with extension)
├── example.qmd                          # Preview page for testing the theme
│
└── _extensions/
    └── wfrc-brand/
        ├── _extension.yml               # Extension metadata and contributions
        ├── brand.yml                    # Brand spec: colors, typography, logos
        └── assets/
            ├── logo/
            │   ├── horizontal/          # WFRC_logo_horizontal_color/white_transparent.png
            │   ├── stacked/             # WFRC_logo_stacked_color/white_transparent.png
            │   └── abbreviated/         # WFRC_logo_abbreviated_color/white_transparent.png
            └── theme/
                ├── _wfrc-colors.scss    # Brand color variables
                ├── _wfrc-fonts.scss     # Typography variables
                ├── wfrc.scss            # Shared structural SCSS (both modes)
                ├── wfrc-light.scss      # Light mode overrides
                └── wfrc-dark.scss       # Dark mode overrides
```

---

## Updating the Extension in Downstream Projects

When this repo is updated (new colors, font changes, logo updates, etc.), downstream projects pull the latest version by running:

```bash
quarto update WFRCAnalytics/wfrc-brand
```

---

## Maintaining This Repo

### Color changes

Edit `_extensions/wfrc-brand/assets/theme/_wfrc-colors.scss` for SCSS variables and `_extensions/wfrc-brand/brand.yml` under `color.palette` for brand-level tokens. Both must stay in sync — the SCSS variables are used in the theme files, and the `brand.yml` palette generates `$brand-*` Sass variables automatically in downstream projects.

### Typography changes

Edit `_extensions/wfrc-brand/assets/theme/_wfrc-fonts.scss` for SCSS font variables and `_extensions/wfrc-brand/brand.yml` under `typography` for brand-level font declarations. Both must be kept consistent — `brand.yml` declares what fonts to load (Google Fonts), `_wfrc-fonts.scss` declares the SCSS variables used throughout the theme.

### Light / dark mode styles

- **Structural rules** (layout, spacing, border-radius, font properties) → `wfrc.scss`
- **Light mode colors and overrides** → `wfrc-light.scss`
- **Dark mode colors and overrides** → `wfrc-dark.scss`

### Logo updates

Replace files in `_extensions/wfrc-brand/assets/logo/`. The `brand.yml` logo block references them by filename — as long as filenames stay the same, no YAML changes are needed.

### Adding a new org-wide default

Add it under `contributes.metadata` in `_extension.yml` if it's a project/website config property, or under `contributes.formats.html` if it's an HTML format property. Then mirror it in the dev project's `_quarto.yml` with full `_extensions/wfrc-brand/` paths.

### Clearing the Sass cache

Quarto caches compiled SCSS in `.quarto/`. After any SCSS change that doesn't seem to render, delete this folder before re-rendering:

```bash
# Windows
rmdir /s /q .quarto

# macOS / Linux
rm -rf .quarto
```

### Versioning

Bump the `version` field in `_extension.yml` on every meaningful change so downstream projects can track what they have installed.

---

## Reference Documentation

- [Quarto Extensions](https://quarto.org/docs/extensions/) — overview of the extension system
- [Creating Extensions](https://quarto.org/docs/extensions/creating.html) — `_extension.yml` spec and `contributes` keys
- [Brand Extensions](https://quarto.org/docs/extensions/brand.html) — how brand extensions work in Quarto
- [brand.yml spec](https://posit-dev.github.io/brand-yml/) — full reference for `brand.yml` color, typography, and logo fields
- [HTML Theming](https://quarto.org/docs/output-formats/html-themes.html) — Quarto SCSS theming, dark mode, Bootstrap variables
- [Sass Variables](https://quarto.org/docs/output-formats/html-themes.html#sass-variables) — Quarto's exposed Bootstrap/Quarto SCSS variables
