"""Bring goatcore's generated error-code pages into the site.

goatcore generates one page per error code from its catalog
(``ops/errors/catalog.yaml`` -> ``docs/reference/errors/<CODE>.md``, by
``ops/ci/check-error-catalog.py --write``, held current by its CI gate). This
script copies those pages into ``docs/reference/errors/`` of this checkout so
the site serves each at ``reference/errors/<CODE>/``, and the table of every
code (``docs/reference/errors.md``) as that directory's landing page.

It writes nothing by hand: the text is goatcore's. It changes two things only.
A relative link that leaves the copied pages becomes the file's address in
goatcore on GitHub, and each page gets a ``description`` (the entry's "What it
means" paragraph) for the page's meta description.

The copies are build output: ``docs/reference/errors/`` is ignored by git.
A goatcore checkout that has no code pages yet copies nothing and exits 0.

usage: import-error-pages.py <goatcore checkout> [--docs DIR] [--self-test]
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import shutil
import sys
import tempfile

GOATCORE_URL = "https://github.com/USAREUR-AF/goatcore/blob/main/"
SRC_PAGES = "docs/reference/errors"
SRC_TABLE = "docs/reference/errors.md"
DEST = "reference/errors"
_LINK = re.compile(r"\]\((?P<target>[^)\s]+)\)")
_WHAT = re.compile(r"^## What it means\n\n(.+?)\n", re.MULTILINE)
_TAG = re.compile(r"`|\\(?=\*)")


def relink(text: str, src: str) -> str:
    """Rewrite the relative links of a goatcore file at repository path `src`."""
    here = posixpath.dirname(src)

    def one(match: re.Match) -> str:
        target = match.group("target")
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#", target, re.IGNORECASE):
            return match.group(0)
        path, sep, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(here, path))
        if resolved == SRC_TABLE:
            new = "README.md"
        elif posixpath.dirname(resolved) == SRC_PAGES and resolved.endswith(".md"):
            new = posixpath.basename(resolved)
        else:
            new = GOATCORE_URL + resolved
        return f"]({new}{sep}{anchor})"

    return _LINK.sub(one, text)


def describe(text: str) -> str:
    """Front matter carrying the page's meta description, from "What it means"."""
    match = _WHAT.search(text)
    if not match:
        return text
    what = _TAG.sub("", match.group(1)).replace("&lt;", "<").replace("&amp;", "&")
    return f"---\ndescription: {json.dumps(what)}\n---\n{text}"


def run(goatcore: str, docs: str) -> int:
    pages = os.path.join(goatcore, SRC_PAGES)
    dest = os.path.join(docs, DEST)
    shutil.rmtree(dest, ignore_errors=True)
    names = sorted(n for n in os.listdir(pages) if n.endswith(".md")) if os.path.isdir(pages) else []
    if not names:
        print(f"import-error-pages: {SRC_PAGES}/ has no pages in {goatcore}; nothing copied")
        return 0
    os.makedirs(dest)
    for name in names:
        with open(os.path.join(pages, name), encoding="utf-8") as f:
            text = f.read()
        with open(os.path.join(dest, name), "w", encoding="utf-8") as f:
            f.write(describe(relink(text, posixpath.join(SRC_PAGES, name))))
    with open(os.path.join(goatcore, SRC_TABLE), encoding="utf-8") as f:
        table = f.read()
    with open(os.path.join(dest, "README.md"), "w", encoding="utf-8") as f:
        f.write(relink(table, SRC_TABLE))
    print(f"import-error-pages: copied {len(names)} code pages and the table to {DEST}/")
    return 0


def self_test() -> int:
    page = ("# GB-001: t\n\nintro\n\n## What it means\n\nno `x` in &lt;site>, 2 \\* 3\n\n## Read more\n\n"
            "- [`docs/design/x.md`](../../../docs/design/x.md)\n- [Every error code](../errors.md)\n"
            "- [other](GB-002.md) [web](https://example.org/a)\n")
    with tempfile.TemporaryDirectory() as t:
        core, docs = os.path.join(t, "core"), os.path.join(t, "docs")
        assert run(core, docs) == 0 and not os.path.exists(os.path.join(docs, DEST)), "no pages copies nothing"
        os.makedirs(os.path.join(core, SRC_PAGES))
        with open(os.path.join(core, SRC_PAGES, "GB-001.md"), "w") as f:
            f.write(page)
        with open(os.path.join(core, SRC_TABLE), "w") as f:
            f.write("# t\n\n[d](../design/e.md)\n\n| [`GB-001`](errors/GB-001.md) |\n")
        assert run(core, docs) == 0
        with open(os.path.join(docs, DEST, "GB-001.md")) as f:
            got = f.read()
        assert got.startswith('---\ndescription: "no x in <site>, 2 * 3"\n---\n# GB-001: t\n'), got
        assert f"]({GOATCORE_URL}docs/design/x.md)" in got and "](README.md)" in got
        assert "](GB-002.md)" in got and "](https://example.org/a)" in got
        with open(os.path.join(docs, DEST, "README.md")) as f:
            got = f.read()
        assert "](GB-001.md)" in got and f"]({GOATCORE_URL}docs/design/e.md)" in got, got
    print("import-error-pages: self-test ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("goatcore", nargs="?", help="a goatcore checkout")
    ap.add_argument("--docs", default=os.path.join(os.path.dirname(__file__), "..", "..", "docs"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.goatcore:
        ap.error("name a goatcore checkout")
    return run(a.goatcore, os.path.abspath(a.docs))


if __name__ == "__main__":
    sys.exit(main())
