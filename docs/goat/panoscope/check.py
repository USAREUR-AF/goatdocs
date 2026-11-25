#!/usr/bin/env python3
"""Check the panoscope page against goatstuff. Standard library only.

  python3 -I docs/goat/panoscope/check.py <goatstuff-checkout>

Measures each number marked data-measure="<key>" in index.html from
<goatstuff-checkout>/ops/panoscope, the same way as the command printed under
it, and fails when the page states anything else, when the page names a key
this file does not measure, or when a measured key is missing from the page.
It also fails when an image the page names is not beside it, or when a
scaffold placeholder survives.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def measures(tree):
    """key -> the exact text the page must show."""

    def pages():  # ls frontend/web/*.html | wc -l
        return str(len(glob.glob(os.path.join(tree, "frontend", "web", "*.html"))))

    def max_elements():  # grep -o 'MAX_ELEMENTS: usize = [0-9_]*' src/view/assemble.rs
        m = re.search(r"MAX_ELEMENTS: usize = ([0-9_]+)", read(os.path.join(tree, "src", "view", "assemble.rs")))
        return f"{int(m.group(1).replace('_', '')):,}" if m else "missing"

    def vendored():  # ls frontend/web/vendor/*/*.js | wc -l
        return str(len(glob.glob(os.path.join(tree, "frontend", "web", "vendor", "*", "*.js"))))

    def rust_tests():  # grep -rE '#\[(tokio::)?test' src | wc -l
        n = 0
        for d, _, files in os.walk(os.path.join(tree, "src")):
            for name in files:
                with open(os.path.join(d, name), encoding="utf-8", errors="replace") as f:
                    n += sum(1 for line in f if re.search(r"#\[(tokio::)?test", line))
        return str(n)

    return {"pages": pages(), "max-elements": max_elements(), "vendored": vendored(), "rust-tests": rust_tests()}


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2].strip())
        return 2
    tree = os.path.join(sys.argv[1], "ops", "panoscope")
    if not os.path.isdir(tree):
        print(f"docs/goat/panoscope: {tree} is not a directory")
        return 2
    page = read(os.path.join(HERE, "index.html"))
    measured = measures(tree)
    stated = dict(re.findall(r'data-measure="([a-z0-9-]+)">([^<]*)<', page))
    bad = 0
    for key, value in measured.items():
        if stated.get(key) != value:
            print(f"docs/goat/panoscope: {key} says {stated.get(key)}, goatstuff gives {value}")
            bad += 1
    for key in stated.keys() - measured.keys():
        print(f'docs/goat/panoscope: data-measure="{key}" is not measured by check.py')
        bad += 1
    for pic in sorted(set(re.findall(r'(?:src|srcset)="([^":/]+\.png)"', page))):
        if not os.path.exists(os.path.join(HERE, pic)):
            print(f"docs/goat/panoscope: {pic} is missing")
            bad += 1
    if re.search(r"REPLACE|\{\{[A-Z_]+\}\}", page):
        print("docs/goat/panoscope: a scaffold placeholder survives in index.html")
        bad += 1
    if bad:
        return 1
    print("docs/goat/panoscope: numbers match goatstuff:", ", ".join(f"{k}={v}" for k, v in measured.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
