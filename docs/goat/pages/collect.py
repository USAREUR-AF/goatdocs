#!/usr/bin/env python3
"""Collect every live goat landing page into catalog.json and shots/. Run by hand.

  python3 -I docs/goat/pages/collect.py            fetch the pages, write catalog.json
  python3 -I docs/goat/pages/collect.py --shots    also capture the first screens (needs Chrome; macOS sips)

The list of pages is .claude/skills/splash-page/examples.md, the same list the
splash-page skill keeps. For each page it records, from the live page itself:
the title, the tagline, the lede, and the numbers strip (value, label, how it is
measured).
Standard library only. build.py renders the catalogue from catalog.json without
the network.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EXAMPLES = os.path.join(ROOT, ".claude", "skills", "splash-page", "examples.md")
SHOTS = os.path.join(HERE, "shots")
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def pages():
    """(name, url, shows, kind) for every row of examples.md that links a live page."""
    out = []
    for line in open(EXAMPLES).read().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[1].startswith("https://"):
            out.append({"name": cells[0], "url": cells[1], "shows": cells[2], "kind": "site",
                        "repo": f"https://github.com/USAREUR-AF/{cells[0]}"})
        elif cells[0].startswith("https://"):
            name = cells[0].rstrip("/").split("/")[-1]
            out.append({"name": name, "url": cells[0], "shows": cells[1], "kind": "subpage",
                        "repo": "https://github.com/USAREUR-AF/goatdocs"})
    return out


def slug(url):
    path = urllib.parse.urlparse(url).path.strip("/").split("/")
    path = path[1:] if path[0] == "goatdocs" else path
    path = path[1:] if path[:1] == ["goat"] and len(path) > 1 else path
    return "-".join(path)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "goatdocs-collect"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 - fixed https URLs from examples.md
        return r.read().decode("utf-8", "replace")


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def first(pattern, page):
    m = re.search(pattern, page, re.S)
    return text(m.group(1)) if m else ""


def numbers(page):
    """Each cell of the numbers strip: value, label, and the measurement line under it.
    Pages write the strip as <ul class="numbers"> or <div class="numbers|strip"> with one
    <li> or <div> per number: the value in <b> (or class="n"), then a label <span>, then
    a <code> or a class="d" line saying how it is measured."""
    m = re.search(r'<(ul|div)[^>]*class="(?:numbers|strip)[^"]*"[^>]*>', page)
    if not m:
        return []
    rest = page[m.end():]
    cells = []
    for c in re.finditer(r"<(li|div)\b[^>]*>(.*?)</\1>", rest, re.S):
        if c.start() > 0 and re.match(r"\s*</(ul|div)>", rest[:c.start()].split(">")[-1] or ""):
            break
        cell = c.group(2)
        v = re.search(r"<b\b[^>]*>(.*?)</b>", cell, re.S) or re.search(r'class="n"[^>]*>(.*?)</span>', cell, re.S)
        if not v:
            continue
        after = cell[v.end():]
        lab = None
        for sp in re.finditer(r'<span(?![^>]*class="d")[^>]*>(.*?)</span>', after, re.S):
            lab = sp
            break
        how = re.search(r"<code>(.*?)</code>\s*$", after.strip(), re.S) or re.search(r'class="d"[^>]*>(.*?)</span>', after, re.S)
        label = text(re.sub(r"<sup>.*?</sup>", "", lab.group(1), flags=re.S)) if lab else ""
        cells.append({"n": text(v.group(1)), "l": label, "how": text(how.group(1)) if how else ""})
        if len(cells) == 4:
            break
    return cells


def shoot(url, out, scheme):
    with tempfile.TemporaryDirectory() as d:
        png = os.path.join(d, "s.png")
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",  # noqa: S603
                        f"--blink-settings=preferredColorScheme={0 if scheme == 'dark' else 1}",
                        "--virtual-time-budget=4000", "--window-size=1440,900", f"--screenshot={png}", url],
                       capture_output=True, timeout=120, check=False)
        subprocess.run(["sips", "-Z", "1080", "-s", "format", "jpeg", "-s", "formatOptions", "72", png, "--out", out],  # noqa: S603,S607
                       capture_output=True, check=True)


def main():
    rows = []
    for p in pages():
        page = get(p["url"])
        p.update({
            "slug": slug(p["url"]),
            "title": first(r"<title>(.*?)</title>", page),
            "tagline": first(r'<p class="(?:tagline|tag)"[^>]*>(.*?)</p>', page),
            "lede": first(r'<p class="(?:lede|sentence)"[^>]*>(.*?)</p>', page),
            "numbers": numbers(page),
            "measured": len(re.findall(r"data-measure=", page)),
        })
        rows.append(p)
        print(f"{p['slug']}: " + " | ".join(f"{c['n']} {c['l'][:28]}" for c in p["numbers"]))
        if "--shots" in sys.argv[1:]:
            os.makedirs(SHOTS, exist_ok=True)
            for scheme in ("light", "dark"):
                shoot(p["url"], os.path.join(SHOTS, f"{p['slug']}-{scheme}.jpg"), scheme)
    with open(os.path.join(HERE, "catalog.json"), "w") as f:
        json.dump({"source": ".claude/skills/splash-page/examples.md", "pages": rows}, f, indent=1, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
