#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Make a changelog figure stand alone, and check the ones an entry uses.

    figure.py wrap drawing.svg docs/changelog/figures/2026-11-10/one-hop.svg
    figure.py check docs/changelog/2026-11-10-example.md

A changelog figure is an SVG that reads the same on GitHub, on the docs site
and inside a page: it carries its own styles (figure.css, light and dark), its
own background, a <title> that states the finding and a <desc> that says the
whole message in a sentence. `wrap` adds those to a drawing whose shapes use
the classes in figure.css. `check` refuses an entry whose figures lack them.
"""
from __future__ import annotations

import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN_TAG = re.compile(r"<svg\b[^>]*>", re.S)
IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)\s]+\.svg)\)")


def wrap(source: str, target: str) -> None:
    with open(source, encoding="utf-8") as handle:
        drawing = handle.read()
    with open(os.path.join(HERE, "figure.css"), encoding="utf-8") as handle:
        css = handle.read()
    tag = OPEN_TAG.search(drawing)
    if not tag:
        raise SystemExit(f"figure: {source} has no <svg> element")
    opening = tag.group(0)
    box = re.search(r'viewBox="([\d.\s-]+)"', opening)
    label = re.search(r'aria-label="([^"]*)"', opening)
    first_text = re.search(r"<text\b[^>]*>(.*?)</text>", drawing, re.S)
    if not box or not label or not first_text:
        raise SystemExit(f"figure: {source} needs a viewBox, an aria-label (the whole message) and a title line")
    _, _, width, height = (float(value) for value in box.group(1).split())
    title = re.sub(r"<[^>]+>", "", first_text.group(1)).strip()
    if "xmlns=" not in opening:
        opening = opening.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    head = (
        f"{opening}\n<title>{html.escape(html.unescape(title))}</title>\n"
        f"<desc>{html.escape(html.unescape(label.group(1)))}</desc>\n"
        f"<style>\n{css}</style>\n"
        f'<rect x="0.5" y="0.5" width="{width - 1:g}" height="{height - 1:g}" rx="10" '
        'style="fill:var(--paper);stroke:var(--rule)"/>\n'
    )
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(drawing.replace(tag.group(0), head, 1))
    print(target)


def check(entry: str) -> int:
    with open(entry, encoding="utf-8") as handle:
        text = handle.read()
    problems = []
    for found in IMAGE.finditer(text):
        path = os.path.normpath(os.path.join(os.path.dirname(entry), found["path"]))
        if len(found["alt"].split()) < 8:
            problems.append(f"{found['path']}: the alt text must say the whole message in a sentence")
        if not os.path.exists(path):
            problems.append(f"{found['path']}: file not found")
            continue
        with open(path, encoding="utf-8") as handle:
            svg = handle.read()
        for needed, why in (("<title>", "a <title> that states the finding"),
                            ("<desc>", "a <desc> that says the whole message"),
                            ("prefers-color-scheme: dark", "its own dark colors"),
                            ("var(--paper)", "its own background")):
            if needed not in svg:
                problems.append(f"{found['path']}: needs {why} (run figure.py wrap)")
        if re.search(r'(fill|stroke)="#[0-9a-fA-F]{3,8}"', svg):
            problems.append(f"{found['path']}: a literal color; use the classes in figure.css")
    for problem in problems:
        print(f"figure: {problem}", file=sys.stderr)
    return 1 if problems else 0


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "wrap":
        wrap(sys.argv[2], sys.argv[3])
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        return check(sys.argv[2])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
