#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build one self-contained HTML page from a written changelog entry.

    pip install markdown        # already present where the docs site is built
    page.py docs/changelog/2026-11-10-example.md --out /tmp/changelog.html

The page is for sharing an entry outside the repository. It is made from the
same Markdown and the same figure files as the entry, so the two cannot
disagree: figures are placed inline, links to files in this repository point
at GitHub, and the colors are the figure roles in figure.css (the goat design
system, light and dark). The output has no <html>, <head> or <body> element,
so it can be published as a fragment or opened in a browser as it is.
"""
from __future__ import annotations

import argparse
import html
import os
import re

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_URL = "https://github.com/USAREUR-AF/goatdocs/blob/main/"

PAGE_CSS = """
/* One reading column; tables and figures may scroll sideways inside their own frame. */
body { margin:0; background:var(--paper); color:var(--ink);
  font:16px/1.6 "Geist", system-ui, -apple-system, "Segoe UI", sans-serif;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px));
  padding-block:40px 72px; }
main { max-width:860px; margin:0 auto; display:flex; flex-direction:column; gap:18px; min-width:0; }
main > * { margin:0; min-width:0; }
h1 { font-size:clamp(1.6rem, 4.2vw, 2.25rem); line-height:1.15; letter-spacing:-.015em; text-wrap:balance; }
h1 .when { display:block; font:600 .8rem/1.4 "Geist Mono", ui-monospace, Menlo, monospace; letter-spacing:.08em;
  text-transform:uppercase; color:var(--accent); margin-bottom:10px; }
h2 { font-size:1.4rem; line-height:1.25; letter-spacing:-.01em; text-wrap:balance; margin-top:26px;
  padding-top:22px; border-top:1px solid var(--rule); }
h3 { font-size:1.08rem; line-height:1.3; margin-top:10px; text-wrap:balance; }
p, li { max-width:70ch; text-wrap:pretty; }
ul { padding-left:1.15rem; display:flex; flex-direction:column; gap:6px; }
a { color:var(--accent); text-underline-offset:2px; }
a:focus-visible { outline:2px solid var(--accent); outline-offset:2px; border-radius:3px; }
code { font:.86em "Geist Mono", ui-monospace, Menlo, monospace; background:var(--panel); border:1px solid var(--rule);
  border-radius:4px; padding:0 4px; overflow-wrap:anywhere; }
hr { display:none; }
.lead { font-size:1.12rem; color:var(--ink); }
.short { background:var(--accent-soft); border:1px solid var(--accent); border-radius:10px; padding:16px 18px;
  display:flex; flex-direction:column; gap:10px; }
.short h2 { margin:0; padding:0; border:0; font-size:1.05rem; letter-spacing:.02em; }
.short li { max-width:none; }
.tw { overflow-x:auto; border:1px solid var(--rule); border-radius:8px; background:var(--paper); }
table { border-collapse:collapse; width:100%; font-size:.92rem; line-height:1.5; }
th, td { text-align:left; vertical-align:top; padding:9px 12px; border-bottom:1px solid var(--rule); }
th { background:var(--panel); font-weight:600; font-size:.8rem; letter-spacing:.04em; text-transform:uppercase;
  color:var(--quiet); white-space:nowrap; }
tr:last-child td { border-bottom:0; }
td:first-child { min-width:9rem; }
figure { margin:0; overflow-x:auto; }
figure svg { display:block; width:100%; min-width:560px; height:auto; }
footer { color:var(--quiet); font-size:.86rem; border-top:1px solid var(--rule); padding-top:14px; margin-top:20px; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior:smooth; } }
@page { size: letter; margin: 16mm 15mm; }
@media print {
  /* System faces in print: a variable web font is embedded as Type 3, whose text copies out unreadable. */
  body { padding:0; font-size:10.5pt; font-family:"Helvetica Neue", Helvetica, Arial, sans-serif; }
  code, h1 .when { font-family:Menlo, Consolas, "Courier New", monospace; }
  main { max-width:none; gap:11pt; }
  h2 { break-after:avoid; margin-top:10pt; padding-top:10pt; }
  h3 { break-after:avoid; }
  .tw { overflow:visible; }
  table { font-size:8.6pt; }
  th { white-space:normal; }
  tr, figure, .short li { break-inside:avoid; }
  figure { overflow:visible; }
  figure svg { min-width:0; }
  a { text-decoration:none; }
}
"""


def inline_figure(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        svg = handle.read()
    svg = re.sub(r"<style>.*?</style>\s*", "", svg, count=1, flags=re.S)  # the page carries figure.css once
    return f"<figure>{svg}</figure>"


def build(entry: str) -> str:
    with open(entry, encoding="utf-8") as handle:
        text = handle.read()
    with open(os.path.join(HERE, "figure.css"), encoding="utf-8") as handle:
        figure_css = handle.read()
    base = os.path.dirname(entry)
    figures: list[str] = []

    def stash(found: re.Match) -> str:
        figures.append(inline_figure(os.path.normpath(os.path.join(base, found["path"]))))
        return f"\n\nFIGURE-{len(figures) - 1}-HERE\n\n"

    text = re.sub(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)\s]+\.svg)\)", stash, text)
    body = markdown.markdown(text, extensions=["tables", "toc", "attr_list"], output_format="html5")
    for index, figure in enumerate(figures):
        body = body.replace(f"<p>FIGURE-{index}-HERE</p>", figure)

    def repo_link(found: re.Match) -> str:
        target = found.group(1)
        if re.match(r"^(https?:|#|mailto:)", target):
            return found.group(0)
        path = os.path.normpath(os.path.join(base, target.split("#")[0]))
        anchor = ("#" + target.split("#", 1)[1]) if "#" in target else ""
        return f'href="{REPO_URL}{path}{anchor}"'

    body = re.sub(r'href="([^"]+)"', repo_link, body)
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    title = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    plain = re.sub(r"<[^>]+>", "", title.group(1)) if title else "Changelog"
    when, _, what = plain.partition(": ")
    if title and what:
        body = body.replace(title.group(0), f'<h1><span class="when">{html.escape(when)}</span>'
                                            f"{html.escape(what[:1].upper() + what[1:])}</h1>", 1)
    body = re.sub(r"(</h1>\s*)<p>", r'\1<p class="lead">', body, count=1)
    body = re.sub(r'(<h2 id="in-short">.*?</ul>)', r'<section class="short">\1</section>', body, count=1, flags=re.S)
    name = "goat changelog " + re.sub(r"^Changelog, ", "", when)
    return (
        f"<title>{html.escape(name)}</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700'
        '&family=Geist+Mono:wght@400;600&display=swap">\n'
        f"<style>\n{figure_css}\n{PAGE_CSS}</style>\n"
        f"<main>\n{body}\n<footer>Source: <a href=\"{REPO_URL}{entry}\">{html.escape(entry)}</a> "
        "in USAREUR-AF/goatdocs.</footer>\n</main>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("entry")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(build(args.entry))
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
