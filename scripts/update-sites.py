"""Update every WFRC site that already uses wfrc-brand to a new release, in one pass.

    python scripts/update-sites.py --tag v1.0.6                  # every site found under D:/GitHub
    python scripts/update-sites.py --tag v1.0.6 APP-Benefit-Cost-Analysis GIS-adhoc-analyses
    python scripts/update-sites.py --tag v1.0.6 --dry-run        # show what would happen, change nothing
    python scripts/update-sites.py --tag v1.0.6 --no-render WF-TDM-Calibration   # no data here: skip the render

For each site (a folder with _extensions/WFRCAnalytics/wfrc-brand) it
  1. skips the site if its working tree has uncommitted changes (submodules are ignored),
  2. stays on the current branch, or creates wfrc-brand-<tag> when on main or master,
  3. deletes the old extension folder and runs `quarto add WFRCAnalytics/wfrc-brand@<tag>`,
  4. commits that,
  5. runs `quarto render`, then commits the rebuilt output folders (docs/, _freeze/) separately.
It never pushes and never opens a pull request. It only updates sites already on the 1.0 layout: a site
with an older extension (or none) needs the full migration, see the migration instructions.

The extension's own changes between two releases are in CHANGELOG.md; a patch release (1.0.x) changes
no configuration, so an update is a reinstall plus a re-render.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXT_REL = Path("_extensions/WFRCAnalytics/wfrc-brand")
OUTPUT_DIRS = ["docs", "_freeze"]


def run(cmd, cwd, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=(sys.platform == "win32" and cmd[0] == "quarto"))
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{(r.stdout + r.stderr).strip()[-1200:]}")
    return r


def git(cwd, *args, check=True):
    return run(["git", *args], cwd, check)


def version_of(site):
    f = site / EXT_REL / "_extension.yml"
    if not f.exists():
        return None
    m = re.search(r"^version:\s*(\S+)", f.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "?"


def find_sites(root, names):
    if names:
        return [root / n for n in names]
    return sorted(p.parent.parent.parent.parent for p in root.glob("*/_extensions/WFRCAnalytics/wfrc-brand/_extension.yml"))


def update(site, tag, dry, render):
    want = tag.lstrip("v")
    have = version_of(site)
    if not (site / ".git").exists():
        return "skip", "not a git repository"
    if have is None:
        return "skip", "no _extensions/WFRCAnalytics/wfrc-brand: needs the full migration (see _migration/)"
    if have == want:
        return "skip", f"already on {want}"
    dirty = git(site, "status", "--porcelain", "--ignore-submodules=all").stdout.strip()
    if dirty:
        return "skip", "uncommitted changes (commit or stash them first):\n      " + dirty.replace("\n", "\n      ")[:400]
    branch = git(site, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    new_branch = f"wfrc-brand-{want}" if branch in ("main", "master") else None
    plan = f"{have} -> {want} on {new_branch or branch}" + ("" if render else " (no render)")
    if dry:
        return "would update", plan
    if new_branch:
        git(site, "checkout", "-b", new_branch)
    shutil.rmtree(site / EXT_REL, ignore_errors=False)
    run(["quarto", "add", f"WFRCAnalytics/wfrc-brand@{tag}", "--no-prompt"], site)
    got = version_of(site)
    if got != want:
        raise RuntimeError(f"installed version is {got}, expected {want}")
    git(site, "add", "-A", "--", "_extensions")
    git(site, "commit", "-q", "-m", f"update wfrc-brand to {want}")
    note = plan
    if render:
        r = run(["quarto", "render"], site, check=False)
        errs = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR")]
        if r.returncode != 0 or errs:
            return "RENDER FAILED", plan + "\n      " + "\n      ".join(errs[:3] or ["see `quarto render` in the site"])
        # Only folders the site tracks: a folder in .gitignore (docs/ when CI builds the site, _freeze when
        # it is local cache) cannot be added, and trying to makes the whole update fail.
        outs = [d for d in OUTPUT_DIRS
                if (site / d).exists() and git(site, "check-ignore", "-q", d, check=False).returncode != 0]
        if outs:
            git(site, "add", "-A", "--", *outs)
            if git(site, "diff", "--cached", "--quiet", check=False).returncode != 0:
                git(site, "commit", "-q", "-m", f"rebuild output for wfrc-brand {want}")
                note += f"; rebuilt {', '.join(outs)}"
    return "updated", note


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sites", nargs="*", help="site folder names under --root (default: every site found)")
    ap.add_argument("--tag", required=True, help="release tag to install, e.g. v1.0.6")
    ap.add_argument("--root", default="D:/GitHub", help="folder that holds the site repositories")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-render", action="store_true", help="skip `quarto render` (a site whose data is not on this machine)")
    a = ap.parse_args()
    root = Path(a.root)
    sites = find_sites(root, a.sites)
    if not sites:
        print(f"no sites with {EXT_REL} under {root}")
        return 1
    print(f"wfrc-brand {a.tag}{' (dry run)' if a.dry_run else ''}: {len(sites)} site(s) under {root}\n")
    results = []
    for s in sites:
        try:
            status, msg = update(s, a.tag, a.dry_run, not a.no_render)
        except Exception as e:  # keep going: one broken site must not stop the rest
            status, msg = "ERROR", str(e)
        results.append((s.name, status, msg))
        print(f"{status:<14} {s.name}\n      {msg}\n")
    bad = [r for r in results if r[1] in ("ERROR", "RENDER FAILED")]
    print(f"done: {sum(r[1] == 'updated' for r in results)} updated, "
          f"{sum(r[1] == 'skip' for r in results)} skipped, {len(bad)} failed. Nothing was pushed.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
