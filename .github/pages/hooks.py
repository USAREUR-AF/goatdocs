"""MkDocs hook: map the corpus's own conventions onto site URLs.

The corpus is written to read on GitHub: it names its top-level index
``INDEX.md``, links to directories (``design/``), and links to repository files
outside ``docs/``. This hook makes the same files read as a website. It runs at
build time only and changes no source file.

1. ``docs/INDEX.md`` is the home page.
2. A directory with no ``README.md`` or ``index.md`` gets a generated page that
   lists its documents by title (and its HTML pages by file name).
3. A ``README.md`` beside a hand-written ``index.html`` (the design-system UI
   kits) is served at ``<dir>/readme/``; ``mkdocs.yml`` excludes it so MkDocs
   does not drop it with a warning first.
4. A link to a directory points at that directory's landing page, and a link
   to a repository file outside ``docs/`` points at the file on GitHub.
5. ``llms-full.txt`` at the site root holds every page's Markdown in one file,
   for language models and the indexes that feed them (https://llmstxt.org/).
   It is written by the build and is never committed.
"""

from __future__ import annotations

import os
import posixpath
import re
from collections import defaultdict

from mkdocs.structure.files import File, Files, InclusionLevel

REPO_URL = "https://github.com/USAREUR-AF/goatdocs/blob/main/"
LANDING = ("README.md", "index.md", "INDEX.md")
_H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# A Markdown inline link target: ](target) or ](target "title").
_LINK = re.compile(r"\]\((?P<target>[^)\s]+)(?P<rest>(?:\s+\"[^\"]*\")?)\)")

# Directory (relative to docs_dir) -> the src_uri of its landing page.
_landing: dict[str, str] = {}
# src_uri -> (page URL, page Markdown with absolute links), for llms-full.txt.
_full: dict[str, tuple[str, str]] = {}


def _title(file: File) -> str:
    try:
        match = _H1.search(file.content_string)
    except (OSError, UnicodeDecodeError):
        match = None
    if match:
        return match.group(1)
    return posixpath.splitext(posixpath.basename(file.src_uri))[0]


def _file(config, src_uri: str, dest_uri: str) -> File:
    f = File(
        src_uri,
        config["docs_dir"],
        config["site_dir"],
        config["use_directory_urls"],
        dest_uri=dest_uri,
    )
    f.inclusion = InclusionLevel.INCLUDED
    return f


def on_files(files: Files, config) -> Files:
    docs_dir = os.path.abspath(config["docs_dir"])
    by_dir: dict[str, list[str]] = defaultdict(list)
    for root, _dirs, names in os.walk(docs_dir):
        rel = os.path.relpath(root, docs_dir).replace(os.sep, "/")
        rel = "" if rel == "." else rel
        by_dir[rel].extend(sorted(names))
        for parent in [rel]:
            while parent:
                parent = posixpath.dirname(parent)
                by_dir.setdefault(parent, [])

    _landing.clear()
    _full.clear()

    # 1. Home page.
    home = files.get_file_from_path("INDEX.md")
    if home is not None and files.get_file_from_path("index.md") is None:
        files.remove(home)
        files.append(_file(config, "INDEX.md", "index.html"))
    _landing[""] = "INDEX.md"

    for directory in sorted(by_dir):
        names = set(by_dir[directory])
        if not directory:
            continue
        readme_uri = posixpath.join(directory, "README.md")

        # 3. README.md beside a hand-written index.html.
        if "index.html" in names and "README.md" in names:
            if files.get_file_from_path(readme_uri) is None:
                files.append(
                    _file(config, readme_uri, posixpath.join(directory, "readme", "index.html"))
                )
            _landing[directory] = readme_uri
            continue

        landing = next((n for n in LANDING if n in names), None)
        if landing:
            _landing[directory] = posixpath.join(directory, landing)
            continue

        # 2. Generated listing.
        subdirs = sorted(d for d in by_dir if d and posixpath.dirname(d) == directory)
        pages = [
            files.get_file_from_path(posixpath.join(directory, n))
            for n in sorted(names)
            if n.endswith(".md")
        ]
        lines = [f"# {posixpath.basename(directory)}", ""]
        for s in subdirs:
            name = posixpath.basename(s)
            lines.append(f"- [{name}/]({name}/)")
        for page in pages:
            if page is not None:
                lines.append(f"- [{_title(page)}]({posixpath.basename(page.src_uri)})")
        for name in sorted(n for n in names if n.endswith(".html")):
            lines.append(f"- [{name}]({name})")
        index_uri = posixpath.join(directory, "index.md")
        files.append(File.generated(config, index_uri, content="\n".join(lines) + "\n"))
        _landing[directory] = index_uri
    return files


def on_page_markdown(markdown: str, page, config, files: Files) -> str:
    here = posixpath.dirname(page.file.src_uri)

    def rewrite(match: re.Match) -> str:
        target = match.group("target")
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target, re.IGNORECASE):
            return match.group(0)
        path, sep, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(here, path)) if path else here
        if resolved == ".":
            resolved = ""
        if resolved == ".." or resolved.startswith("../"):
            # Outside docs/: the repository file on GitHub, when it is inside the repo.
            repo_path = posixpath.normpath(posixpath.join("docs", resolved))
            if repo_path.startswith("../"):
                return match.group(0)
            new = REPO_URL + repo_path
        elif resolved in _landing and (path.endswith("/") or path in ("", ".") or
                                       files.get_file_from_path(resolved) is None):
            if not path and not sep:
                return match.group(0)
            new = posixpath.relpath(_landing[resolved], here or ".")
        else:
            return match.group(0)
        return f"]({new}{sep}{anchor}{match.group('rest')})"

    markdown = _LINK.sub(rewrite, markdown)
    _full[page.file.src_uri] = (_absolute(page.file.url, config), _LINK.sub(
        lambda m: _absolute_link(m, here, files, config), markdown))
    return markdown


def _absolute(url: str, config) -> str:
    site = (config.get("site_url") or "").rstrip("/") + "/"
    return site + ("" if url in (".", "./") else url)


def _absolute_link(match: re.Match, here: str, files: Files, config) -> str:
    """A relative link to another page or file of the site, as its full URL.

    In llms-full.txt every page sits in one file, so a relative link has
    nothing to be relative to.
    """
    target = match.group("target")
    if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target, re.IGNORECASE):
        return match.group(0)
    path, sep, anchor = target.partition("#")
    linked = files.get_file_from_path(posixpath.normpath(posixpath.join(here, path)))
    if linked is None:
        return match.group(0)
    return f"]({_absolute(linked.url, config)}{sep}{anchor}{match.group('rest')})"


def on_post_build(config) -> None:
    """Write llms-full.txt: the home page first, then every page by path."""
    home = _landing.get("", "")
    parts = [f"# {config['site_name']}", ""]
    if config.get("site_description"):
        parts += [f"> {config['site_description']}", ""]
    for src_uri in sorted(_full, key=lambda uri: (uri != home, uri)):
        url, markdown = _full[src_uri]
        parts += ["---", "", f"Source: {url}", "", markdown.strip(), ""]
    with open(os.path.join(config["site_dir"], "llms-full.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(parts))
