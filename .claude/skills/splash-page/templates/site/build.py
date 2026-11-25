#!/usr/bin/env python3
"""Prepare site/ for publishing and check it against the tree. Standard library only.

    python3 -I site/build.py

1. Copies the files the page shows from the tree into site/assets/from-tree/
   (git-ignored). The page never carries its own copy of a figure or capture.
2. Measures every number marked data-measure="<key>" on every page and fails
   when the page states anything else, when a page names a key this file does
   not measure, or when the home page leaves a measured key out.
3. Fails when the page or a file under assets/ still holds a placeholder
   (the word in capitals the templates use, or a double-braced NAME).
4. Runs site/fitcheck.py: in headless Chrome at 1440 and 390 px, no command box
   is cut off, no output box at 1440 px, and the page never scrolls sideways.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(SITE, "assets", "from-tree")

# Every page of the site. Each number on any of them is checked.
PAGES = ["index.html"]

# Files copied from the tree into assets/from-tree/, by path relative to the repo root.
FROM_TREE = [
    # "docs/figures/overview-light.svg", "docs/figures/overview-dark.svg",
]


def count(pattern):
    return len(glob.glob(os.path.join(ROOT, pattern)))


# key -> function returning the exact text the page must show. One line per number,
# and site/README.md says how each is measured.
MEASURES = {
    "example-count": lambda: f"{count('site/*.html')}",  # REPLACE with the repo's own facts
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for rel in FROM_TREE:
        shutil.copyfile(os.path.join(ROOT, rel), os.path.join(OUT, os.path.basename(rel)))
    measured = {k: f() for k, f in MEASURES.items()}
    bad = 0
    served = PAGES + [os.path.relpath(p, SITE) for p in glob.glob(os.path.join(SITE, "assets", "*.*"))]
    for name in served:
        with open(os.path.join(SITE, name), errors="replace") as f:
            text = f.read()
        lines = sorted({text.count("\n", 0, m.start()) + 1 for m in re.finditer(r"REPLACE|\{\{[A-Z_]+\}\}", text)})
        if lines:
            more = f" (and {len(lines) - 5} more)" if len(lines) > 5 else ""
            print(f"site/{name}: placeholders on line{'s' if len(lines) > 1 else ''} {', '.join(map(str, lines[:5]))}{more}")
            bad += 1
    for name in PAGES:
        with open(os.path.join(SITE, name)) as f:
            page = f.read()
        stated = dict(re.findall(r'data-measure="([a-z0-9-]+)">([^<]*)<', page))
        for key, value in measured.items():
            if key not in stated:
                if name == "index.html":
                    print(f"site/{name}: no data-measure=\"{key}\"")
                    bad += 1
            elif stated[key] != value:
                print(f"site/{name}: {key} says {stated[key]}, the tree gives {value}")
                bad += 1
        for key in stated.keys() - measured.keys():
            print(f"site/{name}: data-measure=\"{key}\" is not measured by site/build.py")
            bad += 1
    if bad:
        return 1
    print("site: numbers match the tree:", ", ".join(f"{k}={v}" for k, v in measured.items()))
    return subprocess.run([sys.executable, "-I", os.path.join(SITE, "fitcheck.py"), SITE] + PAGES).returncode


if __name__ == "__main__":
    sys.exit(main())
