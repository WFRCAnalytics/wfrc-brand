"""Download the WFRC brand fonts into _extensions/wfrc-brand/assets/fonts/.

Fonts are SIL OFL 1.1 licensed (Poppins, Inter, Fira Code), so they can be redistributed.
Google Fonts serves a different file type depending on the User-Agent:
  - a modern browser gets WOFF2 split by unicode-range; we keep the `latin` subset (web)
  - a legacy client gets one TTF per weight and style (Typst, which cannot read WOFF2). Google's
    Inter and Fira Code TTFs are variable fonts that Typst reads at the default weight only, so
    those two come from the static builds in the @expo-google-fonts npm packages instead.

    python scripts/fetch-fonts.py

Edit FAMILIES to change the set, then update `typography.fonts` in brand.yml to match.
"""
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_extensions/wfrc-brand/assets/fonts"

# family -> (weights, styles)
FAMILIES = {
    "Poppins": ([400, 500, 600], ["normal", "italic"]),
    "Inter": ([400, 500, 600, 700], ["normal"]),
    "Fira Code": ([400, 500], ["normal"]),
}

# family -> (npm package, file prefix); static TTFs at <pkg>/<wght><Name>/<prefix>_<wght><Name>.ttf
STATIC_TTF = {"Inter": ("inter", "Inter"), "Fira Code": ("fira-code", "FiraCode")}
WEIGHT_NAME = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}

MODERN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
LEGACY = "curl/8.0"  # no browser UA: Google serves static TTFs, one per weight and style


def css_url(family, weights, styles):
    ital = "ital," if "italic" in styles else ""
    tuples = []
    for s in styles:
        for w in weights:
            tuples.append(f"{1 if s == 'italic' else 0},{w}" if ital else str(w))
    q = family.replace(" ", "+")
    axis = f"{ital}wght@" + ";".join(sorted(tuples))
    return f"https://fonts.googleapis.com/css2?family={q}:{axis}&display=swap"


def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    return urllib.request.urlopen(req, timeout=60).read()


def blocks(css):
    for m in re.finditer(r"(?:/\*\s*([\w-]+)\s*\*/\s*)?@font-face\s*\{(.*?)\}", css, re.S):
        subset, body = m.group(1), m.group(2)
        weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
        style = re.search(r"font-style:\s*(\w+)", body).group(1)
        url = re.search(r"url\(([^)]+)\)", body).group(1).strip("'\"")
        yield subset, int(weight), style, url


def slug(family):
    return family.replace(" ", "")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for family, (weights, styles) in FAMILIES.items():
        url = css_url(family, weights, styles)
        for subset, w, s, u in blocks(get(url, MODERN).decode()):
            if subset != "latin":
                continue
            dest = OUT / f"{slug(family)}-{w}-{s}.woff2"
            dest.write_bytes(get(u, MODERN))
            print("web ", dest.name, dest.stat().st_size)
        if family in STATIC_TTF:
            pkg, prefix = STATIC_TTF[family]
            for w in weights:
                n = WEIGHT_NAME[w]
                u = f"https://cdn.jsdelivr.net/npm/@expo-google-fonts/{pkg}@latest/{w}{n}/{prefix}_{w}{n}.ttf"
                dest = OUT / f"{slug(family)}-{w}-normal.ttf"
                dest.write_bytes(get(u, LEGACY))
                print("ttf ", dest.name, dest.stat().st_size)
            continue
        for _, w, s, u in blocks(get(url, LEGACY).decode()):
            dest = OUT / f"{slug(family)}-{w}-{s}.ttf"
            dest.write_bytes(get(u, LEGACY))
            print("ttf ", dest.name, dest.stat().st_size)


if __name__ == "__main__":
    sys.exit(main())
