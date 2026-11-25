#!/usr/bin/env python3
"""Write docs/goat/pages/index.html from catalog.json, and check it. Standard library only.

  python3 -I docs/goat/pages/build.py           write index.html
  python3 -I docs/goat/pages/build.py --check   fail when index.html is not what this writes,
                                                when catalog.json and the splash-page skill's
                                                examples.md list different pages, when a page
                                                lacks its tagline or four numbers, or when a
                                                capture is missing

catalog.json is written by collect.py from the live pages; groups.json sets the order
and the group headings, and every page must be in exactly one group. The styles are the
splash-page skill's own (.claude/skills/splash-page/templates/site/assets/site.css)
with this page's tokens (extra.css) and additions (extra-tail.css).
"""
import html
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SKILL = os.path.join(ROOT, ".claude", "skills", "splash-page")
OUT = os.path.join(HERE, "index.html")
HEAD = "<!-- Written by docs/goat/pages/build.py from page.html and catalog.json; edit those, then run the script. -->\n"
sys.path.insert(0, HERE)
from collect import pages as listed  # noqa: E402  the same reading of examples.md collect.py uses


def read(*p):
    with open(os.path.join(*p)) as f:
        return f.read()


def esc(s):
    return html.escape(s, quote=True)


def md(s):
    """Escape, then turn `code` spans from examples.md into <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(s))


def plate(i, p, status=None):
    cells = "".join(
        f'<div><span class="n">{esc(c["n"])}</span><span class="l">{esc(c["l"])}</span>'
        + (f'<code>{esc(c["how"])}</code>' if c["how"] else "") + "</div>" for c in p["numbers"])
    addr = re.sub(r"^https?://", "", p["url"])
    return f'''    <article class="plate" id="{esc(p["slug"])}" data-kind="{p["kind"]}">
      <a class="print" href="{esc(p["url"])}"><picture><source media="(prefers-color-scheme: dark)" srcset="shots/{p["slug"]}-dark.jpg"><img src="shots/{p["slug"]}-light.jpg" width="1080" height="675" loading="lazy" alt="The first screen of the {esc(p["name"])} landing page."></picture></a>
      <div>
        <span class="no">{esc(addr)}</span>
        <h3><a href="{esc(p["url"])}">{esc(p["name"])}</a>{f' <span class="st">{esc(status)}</span>' if status else ""}</h3>
        <p class="tg">{esc(p["tagline"])}</p>
        <p class="ld">{esc(p["lede"])}</p>
        <div class="mini">{cells}</div>
        <p class="fs"><b>First screen:</b> {md(p["shows"])}</p>
        <p class="go"><a href="{esc(p["url"])}">Open the page</a><a href="{esc(p["repo"])}">Repository</a></p>
      </div>
    </article>'''


def plates(groups):
    status = json.loads(read(HERE, "groups.json")).get("status", {})
    out, i = [], 0
    for g, members in groups:
        out.append(f'    <div class="group" id="g-{g["id"]}"><h3 class="gh">{esc(g["title"])}</h3><p class="gs">{esc(g["says"])}</p></div>')
        for p in members:
            i += 1
            out.append(plate(i, p, status.get(p["slug"])))
    return "\n".join(out)


def measure(cat):
    ps = cat["pages"]
    return {"pages": str(len(ps)), "groups": str(len(json.loads(read(HERE, "groups.json"))["groups"])),
            "repos": str(len({p["repo"] for p in ps})),
            "numbers": str(sum(len(p["numbers"]) for p in ps))}


def grouped(cat):
    """[(group, [page, ...]), ...] in the order of groups.json."""
    by = {p["slug"]: p for p in cat["pages"]}
    return [(g, [by[s] for s in g["pages"] if s in by]) for g in json.loads(read(HERE, "groups.json"))["groups"]]


def render(cat):
    groups = grouped(cat)
    ps = [p for _, members in groups for p in members]
    icon = "data:image/svg+xml," + urllib.parse.quote(read(HERE, "icon.svg").strip(), safe="=:/ '")
    css = read(SKILL, "templates", "site", "assets", "site.css")
    css = read(HERE, "extra.css") + css[css.index("* { box-sizing"):] + read(HERE, "extra-tail.css")
    m = measure(cat)
    bg = "\n".join(f"{p['slug']:<22}{p['url']}" for p in ps)
    page = read(HERE, "page.html")
    for k, v in {
        "ICON": icon, "CSS": css, "JS": read(HERE, "catalogue.js"), "BGCODE": esc(bg),
        "FIRST_NAME": esc(ps[0]["name"]), "FIRST_URL": esc(ps[0]["url"]), "FIRST_SLUG": ps[0]["slug"],
        "COUNT": m["pages"],
        "PLATES": plates(groups),
        "GROUPNAV": "".join(f'<a href="#g-{g["id"]}">{esc(g["title"])} <span>{len(m)}</span></a>' for g, m in groups),
        "PAGES_JSON": json.dumps([{"name": p["name"], "url": p["url"], "slug": p["slug"]} for p in ps]),
    }.items():
        page = page.replace("{{" + k + "}}", v)
    for k, v in m.items():
        page = page.replace(f'data-measure="{k}">0<', f'data-measure="{k}">{v}<')
    return HEAD + page


def main():
    cat = json.loads(read(HERE, "catalog.json"))
    page = render(cat)
    bad = []
    if "--check" in sys.argv[1:]:
        if not os.path.exists(OUT) or read(OUT) != page:
            bad.append("index.html is not current: run python3 -I docs/goat/pages/build.py")
    else:
        with open(OUT, "w") as f:
            f.write(page)
    want = [p["url"] for p in listed()]
    have = [p["url"] for p in cat["pages"]]
    if want != have:
        bad.append(f"catalog.json lists {have}, examples.md lists {want}: run collect.py --shots")
    for p in cat["pages"]:
        if not p["tagline"] or len(p["numbers"]) != 4:
            bad.append(f"{p['slug']}: no tagline or not four numbers in catalog.json")
        for scheme in ("light", "dark"):
            if not os.path.exists(os.path.join(HERE, "shots", f"{p['slug']}-{scheme}.jpg")):
                bad.append(f"shots/{p['slug']}-{scheme}.jpg is missing")
    placed = [s for g in json.loads(read(HERE, "groups.json"))["groups"] for s in g["pages"]]
    slugs = [p["slug"] for p in cat["pages"]]
    for s in sorted(set(slugs) - set(placed)):
        bad.append(f"{s} is in catalog.json but in no group of groups.json")
    for s in sorted(set(placed) - set(slugs)):
        bad.append(f"groups.json names {s}, which catalog.json does not have")
    for s in sorted(set(json.loads(read(HERE, "groups.json")).get("status", {})) - set(slugs)):
        bad.append(f"groups.json status names {s}, which catalog.json does not have")
    for s in sorted({s for s in placed if placed.count(s) > 1}):
        bad.append(f"groups.json puts {s} in more than one group")
    if "{{" in page:
        bad.append("a {{...}} marker was not filled")
    stated = dict(re.findall(r'data-measure="([a-z]+)">([^<]*)<', page))
    for k, v in measure(cat).items():
        if stated.get(k) != v:
            bad.append(f"{k} says {stated.get(k)}, catalog.json gives {v}")
    for b in bad:
        print("docs/goat/pages:", b)
    if bad:
        return 1
    print("docs/goat/pages: current;", ", ".join(f"{k}={v}" for k, v in measure(cat).items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
