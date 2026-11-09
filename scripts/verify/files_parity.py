"""Compare the file sets of two built sites (outside site_libs/_extensions) and report files added, removed or
changed in bytes (HTML is left to compare_builds.py).

    python files_parity.py OLD_DIR NEW_DIR
"""
import sys
from pathlib import Path
old, new = Path(sys.argv[1]), Path(sys.argv[2])
def files(root):
    return {p.relative_to(root).as_posix(): p for p in root.rglob('*') if p.is_file() and 'site_libs' not in p.parts and '_extensions' not in p.parts}
fo, fn = files(old), files(new)
only_o, only_n = sorted(set(fo) - set(fn)), sorted(set(fn) - set(fo))
changed = [r for r in sorted(set(fo) & set(fn)) if not r.endswith('.html') and fo[r].read_bytes() != fn[r].read_bytes()]
print(f"files (outside site_libs/_extensions): old {len(fo)}, new {len(fn)}")
print(f"only in OLD: {only_o[:12]}"); print(f"only in NEW: {only_n[:12]}"); print(f"non-html files whose bytes differ: {changed[:12]}")
sys.exit(1 if (only_o or only_n or changed) else 0)
