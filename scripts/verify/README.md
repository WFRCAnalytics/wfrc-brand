# Verify a site migration or update

Use these to prove a site's content did not change when its styling did. Build the old and the new
site (the old one is usually the committed `docs/`), then:

```sh
pip install beautifulsoup4 lxml
python scripts/verify/compare_builds.py OLD_DIR NEW_DIR   # visible text, headings, tables, figures, links per page
python scripts/verify/files_parity.py   OLD_DIR NEW_DIR   # files added, removed or changed outside HTML

cd scripts/verify && npm install
CHROME=/path/to/chrome node visual.js OLD_DIR NEW_DIR OUT_DIR index.html other.html
```

`visual.js` loads each page from both builds in light and dark at 1300px and 390px and flags new failed
requests, console errors, horizontal overflow and a logo that overlaps the title. It also saves screenshots.

Tips learned while migrating:

- Render in a git worktree, not your working copy, and reuse the cached results (`_freeze`) so notebooks do not re-run.
- `date: last-modified` uses file mtimes; restore them (`touch -r`) in the worktree or every date changes.
- Copy git-ignored data files the pages read at render time, or charts 404.
- Compare the title block as well as the main content; `compare_builds.py` does.
