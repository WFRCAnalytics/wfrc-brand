"""Compare two built Quarto sites page by page and report any CONTENT difference.

    python compare_builds.py OLD_DIR NEW_DIR [--show N]

For every .html page in OLD (outside site_libs) it finds the same path in NEW and compares, for the
main content area only (not the navbar, footer, sidebar or table of contents, which are expected to change):
  - the visible text (whitespace normalised, section numbers removed),
  - the list of headings,
  - counts of tables, figures/images, code blocks, callouts and tabsets,
  - the links inside the content (href multiset, query/anchor-only differences ignored).
Exit code 0 means no content difference. It is deliberately strict.
"""
import re
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

SKIP_DIRS = {"site_libs", "_extensions"}
VOLATILE = re.compile(r"\b(Modified|Last updated|Published)\b.*$", re.M)


def pages(root):
    out = {}
    for p in root.rglob("*.html"):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS or part.endswith("_files") for part in rel.parts):
            continue
        out[rel.as_posix()] = p
    return out


def main_of(soup):
    return soup.select_one("main#quarto-document-content") or soup.select_one("main") or soup.body


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def summarize(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    m = main_of(soup)
    if m is None:
        return None
    # #quarto-back-to-top is the new "Back to top" pill: a new control, not page content
    for t in m.select(".header-section-number, script, style, noscript, #quarto-back-to-top"):
        t.decompose()
    # tabbable/scroll attributes added by the a11y script are not content
    # Quarto puts the title block (title, subtitle, author, published/modified dates, abstract) in a
    # header that sits just OUTSIDE main#quarto-document-content: include it, plus the page <title>.
    tb = soup.select_one("#title-block-header, header.quarto-title-block")
    head = norm(tb.get_text(" ")) if tb is not None else ""
    ttl = norm(soup.title.get_text(" ")) if soup.title else ""
    text = norm(f"[title] {ttl} [header] {head} [main] " + m.get_text(" "))
    heads = [norm(h.get_text(" ")) for h in m.select("h1,h2,h3,h4,h5,h6")]
    links = Counter(re.sub(r"[?#].*$", "", a.get("href", "")) for a in m.select("a[href]"))
    counts = {
        "tables": len(m.select("table")),
        "images": len(m.select("img")),
        "figures": len(m.select("figure, .quarto-figure")),
        "code blocks": len(m.select("pre")),
        "callouts": len(m.select(".callout")),
        "tabsets": len(m.select(".panel-tabset")),
        "iframes": len(m.select("iframe")),
        "svg": len(m.select("svg")),
    }
    return {"text": text, "heads": heads, "links": links, "counts": counts}


def first_diff(a, b, ctx=60):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"at char {i}: old …{a[max(0, i - ctx):i + ctx]}…  |  new …{b[max(0, i - ctx):i + ctx]}…"
    return f"one text is longer (old {len(a)} chars, new {len(b)} chars)"


def main():
    old, new = Path(sys.argv[1]), Path(sys.argv[2])
    show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 8
    po, pn = pages(old), pages(new)
    only_old = sorted(set(po) - set(pn))
    only_new = sorted(set(pn) - set(po))
    problems = []
    same = 0
    for rel in sorted(set(po) & set(pn)):
        a, b = summarize(po[rel]), summarize(pn[rel])
        if a is None and b is None and po[rel].read_bytes() == pn[rel].read_bytes():
            same += 1  # an empty page in both builds, byte for byte (pre-existing)
            continue
        if a is None or b is None:
            problems.append((rel, ["could not find the main content area"]))
            continue
        issues = []
        if a["text"] != b["text"]:
            issues.append("text differs: " + first_diff(a["text"], b["text"]))
        if a["heads"] != b["heads"]:
            issues.append(f"headings differ: old {a['heads'][:6]} new {b['heads'][:6]}")
        for k in a["counts"]:
            if a["counts"][k] != b["counts"][k]:
                issues.append(f"{k}: old {a['counts'][k]}, new {b['counts'][k]}")
        if a["links"] != b["links"]:
            lost = a["links"] - b["links"]
            gained = b["links"] - a["links"]
            issues.append(f"links differ: lost {dict(list(lost.items())[:3])} gained {dict(list(gained.items())[:3])}")
        if issues:
            problems.append((rel, issues))
        else:
            same += 1
    print(f"pages in old: {len(po)}   in new: {len(pn)}   compared: {same + len(problems)}")
    print(f"identical content: {same}   with differences: {len(problems)}")
    if only_old:
        print(f"only in OLD ({len(only_old)}): {only_old[:show]}")
    if only_new:
        print(f"only in NEW ({len(only_new)}): {only_new[:show]}")
    for rel, issues in problems[:show]:
        print(f"\n  {rel}")
        for i in issues:
            print("    -", i[:400])
    if len(problems) > show:
        print(f"\n  ... and {len(problems) - show} more pages with differences")
    return 1 if (problems or only_old or only_new) else 0


if __name__ == "__main__":
    sys.exit(main())
