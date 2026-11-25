#!/usr/bin/env python3
"""Write docs/goat/splash-page/index.html and check it. Standard library only.

  python3 -I docs/goat/splash-page/build.py           write index.html
  python3 -I docs/goat/splash-page/build.py --check   fail when index.html is not what this writes,
                                                      or a number or a picture does not hold

The page is page.html with the skill's own stylesheet and script inlined
(.claude/skills/splash-page/templates/site/assets/), extra.css and replay.js,
the icon as a data URL, and one gallery card per live page in
.claude/skills/splash-page/examples.md. Each number marked data-measure is
measured here from the tree. Each card's pictures must be in shots/.
"""
import ast
import glob
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SKILL = os.path.join(ROOT, ".claude", "skills", "splash-page")
ASSETS = os.path.join(SKILL, "templates", "site", "assets")
OUT = os.path.join(HERE, "index.html")
HEAD = "<!-- Written by docs/goat/splash-page/build.py from page.html; edit that, then run the script. -->\n"


def read(*p):
    with open(os.path.join(*p)) as f:
        return f.read()


def live_pages():
    """(name, url, shows) for every row of examples.md that links a live page."""
    rows = []
    for line in read(SKILL, "examples.md").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[1].startswith("https://"):            # own site: repository | page | shows | ...
            rows.append((cells[0], cells[1], cells[2]))
        elif cells[0].startswith("https://"):          # sub-page: page | for | ...
            name = cells[0].rstrip("/").split("/")[-1]
            rows.append((name, cells[0], cells[1]))
    return rows


def slug(url):
    path = urllib.parse.urlparse(url).path.strip("/").split("/")
    path = path[1:] if path[0] == "goatdocs" else path
    path = path[1:] if path[:1] == ["goat"] and len(path) > 1 else path
    return "-".join(path)


def third_party():
    files = [os.path.join(SKILL, "scaffold.py"), os.path.join(HERE, "build.py")]
    files += glob.glob(os.path.join(SKILL, "templates", "site", "*.py"))
    found = set()
    for f in files:
        for node in ast.walk(ast.parse(read(f))):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.module and not node.level else []
            found.update(n.split(".")[0] for n in names if n.split(".")[0] not in sys.stdlib_module_names)
    return found


def measure():
    widths = re.search(r"^WIDTHS = \(([^)]*)\)", read(SKILL, "templates", "site", "fitcheck.py"), re.M).group(1)
    return {
        "live-pages": str(len(live_pages())),
        "template-files": str(sum(len(f) for _, _, f in os.walk(os.path.join(SKILL, "templates")))),
        "widths": str(len([w for w in widths.split(",") if w.strip()])),
        "third-party": str(len(third_party())),
    }


def gallery():
    cards = []
    for name, url, shows in live_pages():
        s = slug(url)
        cards.append(
            f'      <a class="shot" href="{url}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="shots/{s}-dark.jpg">'
            f'<img src="shots/{s}-light.jpg" width="720" height="450" loading="lazy" alt="The first screen of the {name} landing page."></picture>'
            f'<span class="nm">{name}</span><span class="sh">{shows}</span></a>')
    return "\n".join(cards)


def render():
    icon = "data:image/svg+xml," + urllib.parse.quote(read(HERE, "icon.svg").strip(), safe="=:/ '")
    css = read(ASSETS, "site.css")
    css = css[css.index("* { box-sizing"):]   # the template's tokens and metaphor are replaced by extra.css
    page = read(HERE, "page.html")
    for key, value in {"ICON": icon, "CSS": read(HERE, "extra.css") + css + read(HERE, "extra-tail.css"),
                       "JS": read(HERE, "replay.js"), "GALLERY": gallery()}.items():
        page = page.replace("{{" + key + "}}", value)
    return HEAD + page


def main():
    check = "--check" in sys.argv[1:]
    page = render()
    bad = 0
    if check:
        if not os.path.exists(OUT) or read(OUT) != page:
            print("docs/goat/splash-page/index.html is not current: run python3 -I docs/goat/splash-page/build.py")
            bad += 1
    else:
        with open(OUT, "w") as f:
            f.write(page)
    stated = dict(re.findall(r'data-measure="([a-z0-9-]+)">([^<]*)<', page))
    for key, value in measure().items():
        if stated.get(key) != value:
            print(f"docs/goat/splash-page: {key} says {stated.get(key)}, the tree gives {value}")
            bad += 1
    for key in stated.keys() - measure().keys():
        print(f"docs/goat/splash-page: data-measure=\"{key}\" is not measured by build.py")
        bad += 1
    for pic in re.findall(r'(?:src|srcset)="(shots/[^"]+)"', page):
        if not os.path.exists(os.path.join(HERE, pic)):
            print(f"docs/goat/splash-page: {pic} is missing")
            bad += 1
    if "{{" in page:
        print("docs/goat/splash-page: a {{...}} marker was not filled")
        bad += 1
    if bad:
        return 1
    print("docs/goat/splash-page: current; numbers match the tree:", ", ".join(f"{k}={v}" for k, v in measure().items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
