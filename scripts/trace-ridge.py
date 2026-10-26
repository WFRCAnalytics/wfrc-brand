"""Traces the footer skyline from a screenshot of the wfrc.utah.gov footer and
abstracts it into a smooth, geometric ridge line.

  python scripts/trace-ridge.py <screenshot.png> [--write]

Takes the top edge of the navy mass for every pixel column (snow patches are
filled in with a round closing), smooths it, then reduces it to a few straight
facets. Prints $wfrc-ridge-mask, or with --write replaces it between the
ridge:begin / ridge:end markers in wfrc-overrides.scss.
Needs Pillow, numpy and scipy. The screenshot must have white page background
above the footer and the full-width navy footer below the ridge.

Tune: SMOOTH (px) rounds off crags; EPS (viewBox units) sets how few, how
large the straight facets are. Higher EPS = more geometric.
"""
import re, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

W, H = 1200, 120         # viewBox; the ::before height in the SCSS must match
TOP, BOTTOM_PAD = 1, 8   # tallest peak sits TOP units from the top; deepest valley BOTTOM_PAD above the bottom
CLOSE = 16               # px radius: white inlets narrower than 2*CLOSE are filled (snow patches)
SMOOTH = 7               # px sigma of the gaussian that rounds off crags before simplifying
EPS = 1.6                # simplification tolerance in viewBox units

src = Path(sys.argv[1])
im = Image.open(src).convert("RGB")
px = im.load()
navy = lambda p: sum(p) < 330 and p[2] > p[0]   # dark and bluish: not text, not the scrollbar

# usable width (stops at the scrollbar) and the first row of the ridge
base_y = im.height - 120
x1 = max(x for x in range(im.width) if navy(px[x, base_y])) + 1
y0 = next(y for y in range(171, im.height) if any(navy(px[x, y]) for x in range(0, x1, 3)))

ys = range(y0 - 5, base_y)
mask = np.array([[navy(px[x, y]) for x in range(x1)] for y in ys])
r = np.arange(-CLOSE, CLOSE + 1)
disc = (r[:, None] ** 2 + r[None, :] ** 2) <= CLOSE ** 2
pad = CLOSE + 2
m = np.pad(mask, ((0, 0), (pad, pad)), mode="edge")
m = np.pad(m, ((pad, 0), (0, 0)), constant_values=False)   # sky above the screenshot crop
m = ndimage.binary_closing(m, structure=disc)[pad:, pad:-pad]
cols = np.array([y0 - 5 + int(np.argmax(m[:, x])) for x in range(x1)], dtype=float)
cols = ndimage.gaussian_filter1d(cols, SMOOTH, mode="nearest")

lo, hi = cols.min(), cols.max()
pts = [(x / (x1 - 1) * W, TOP + (y - lo) / (hi - lo) * (H - BOTTOM_PAD - TOP)) for x, y in enumerate(cols)]


def dp(p, eps):  # Douglas-Peucker
    if len(p) < 3:
        return p
    (ax, ay), (bx, by) = p[0], p[-1]
    n = ((by - ay) ** 2 + (bx - ax) ** 2) ** 0.5 or 1
    d, i = max((abs((by - ay) * (x - ax) - (bx - ax) * (y - ay)) / n, i) for i, (x, y) in enumerate(p[1:-1], 1))
    return dp(p[:i + 1], eps)[:-1] + dp(p[i:], eps) if d > eps else [p[0], p[-1]]


pts = dp(pts, EPS)
f = lambda n: f"{n:.1f}".rstrip("0").rstrip(".")
d = f"M0 {H}V{f(pts[0][1])}" + "".join(f"L{f(x)} {f(y)}" for x, y in pts[1:]) + f"V{H}z"
svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' preserveAspectRatio='none'><path d='{d}'/></svg>"
line = '$wfrc-ridge-mask: url("data:image/svg+xml,' + svg.replace("<", "%3C").replace(">", "%3E") + '");'

if "--write" in sys.argv:
    scss = Path(__file__).resolve().parent.parent / "_extensions/wfrc-brand/assets/theme/wfrc-overrides.scss"
    s = scss.read_text(encoding="utf8", newline="")
    s, n = re.subn(r"(// ridge:begin[^\n]*\n)[^\n]*\n(// ridge:end)", lambda m: f"{m[1]}{line}\n{m[2]}", s)
    assert n == 1, "ridge markers not found"
    scss.write_text(s, encoding="utf8", newline="")
    print(f"wrote {len(pts)} points ({len(d)} path chars) from {x1}px wide trace")
else:
    print(line)
