#!/usr/bin/env python3
"""Draw the repository's figures from the tree.

    python3 -I docs/figures/make-figures.py           # write docs/figures/*.svg
    python3 -I docs/figures/make-figures.py --check   # exit 1 if a committed figure is out of date

Each figure is written twice, `<name>-light.svg` and `<name>-dark.svg`, for a
`<picture>` element. Each is a redraw of a diagram from the design system's
library (docs/design-system/assets/diagrams/): its labels, its systems and
where they sit are read from that SVG, and it is drawn self-contained, in the
system's green, so GitHub can show it through an <img>. The output is
deterministic. Standard library only.
"""

import os
import re
import xml.etree.ElementTree as ET
import sys
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

THEMES = {
    "light": {
        "paper": "#ffffff", "panel": "#f6f8fa", "ink": "#1f2328", "quiet": "#59636e", "rule": "#d1d9e0",
        "line": "#818b98", "accent": "#0969da", "accent_soft": "#ddf4ff", "on_accent": "#ffffff",
        "good": "#1a7f37", "good_bg": "#dafbe1", "crit": "#cf222e", "crit_bg": "#ffebe9", "mute": "#6e7781",
        "s0": "#0969da", "s1": "#bc4c00", "s2": "#1a7f37", "s3": "#8250df",
    },
    "dark": {
        "paper": "#0d1117", "panel": "#161b22", "ink": "#e6edf3", "quiet": "#9198a1", "rule": "#3d444d",
        "line": "#7d8590", "accent": "#4493f8", "accent_soft": "#132c4c", "on_accent": "#0d1117",
        "good": "#3fb950", "good_bg": "#12261e", "crit": "#f85149", "crit_bg": "#2f1517", "mute": "#8b949e",
        "s0": "#4493f8", "s1": "#f0883e", "s2": "#3fb950", "s3": "#bc8cff",
    },
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def n(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def tw(s, size, mono=False, bold=False):
    """Text width estimate; the browser check in the README confirms it."""
    if mono:
        return len(s) * size * 0.62
    w = 0.0
    for c in s:
        if c in "il.,:;|!'`·1 ":
            w += 0.30
        elif c in "ft()[]/-":
            w += 0.36
        elif c in "mwMW@%":
            w += 0.86
        elif c.isupper() or c in "0123456789≤≥²→":
            w += 0.64
        else:
            w += 0.55
    return w * size * (1.06 if bold else 1.0)


def wrap(s, width, size, mono=False, bold=False):
    out, line = [], ""
    for word in s.split(" "):
        t = word if not line else line + " " + word
        if tw(t, size, mono, bold) <= width or not line:
            line = t
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


class SVG:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.items = []

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="panel", stroke="rule", rx=8, sw=1, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="{%s}" stroke="{%s}" stroke-width="%s"%s/>'
                 % (n(x), n(y), n(w), n(h), n(rx), fill, stroke, n(sw), d))

    def text(self, x, y, s, size=14, fill="ink", anchor="start", bold=False, mono=False, italic=False):
        self.add('<text x="%s" y="%s" font-size="%s" fill="{%s}" text-anchor="%s"%s%s%s>%s</text>'
                 % (n(x), n(y), n(size), fill, anchor, ' font-weight="600"' if bold else "",
                    ' font-family="%s"' % MONO if mono else "", ' font-style="italic"' if italic else "", escape(s)))

    def lines(self, x, y, rows, size=14, lead=1.4, **kw):
        for i, r in enumerate(rows):
            self.text(x, y + i * size * lead, r, size, **kw)
        return y + len(rows) * size * lead

    def line(self, x1, y1, x2, y2, stroke="line", sw=1.5, dash=None, arrow=False):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="{%s}" stroke-width="%s"%s%s/>'
                 % (n(x1), n(y1), n(x2), n(y2), stroke, n(sw), d, m))

    def path(self, d, stroke="line", fill="none", sw=1.5, dash=None, arrow=False):
        dd = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if arrow else ""
        f = "none" if fill == "none" else "{%s}" % fill
        self.add('<path d="%s" fill="%s" stroke="{%s}" stroke-width="%s"%s%s/>' % (d, f, stroke, n(sw), dd, m))

    def circle(self, x, y, r, fill="ink", stroke=None, sw=1.5):
        s = ' stroke="{%s}" stroke-width="%s"' % (stroke, n(sw)) if stroke else ""
        f = "none" if fill == "none" else "{%s}" % fill
        self.add('<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (n(x), n(y), n(r), f, s))

    def ellipse(self, x, y, rx, ry, fill="none", stroke="line", sw=1.5, dash=None, opacity=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        f = "none" if fill == "none" else "{%s}" % fill
        o = ' fill-opacity="%s"' % opacity if opacity is not None else ""
        self.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s stroke="{%s}" stroke-width="%s"%s/>'
                 % (n(x), n(y), n(rx), n(ry), f, o, stroke, n(sw), d))

    def render(self, theme):
        t = THEMES[theme]
        body = "\n".join(self.items)
        for k, v in t.items():
            body = body.replace("{%s}" % k, v)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
                'aria-labelledby="t d" font-family="%s">\n<title id="t">%s</title>\n<desc id="d">%s</desc>\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                'orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="%s"/></marker></defs>\n'
                '<rect width="100%%" height="100%%" rx="12" fill="%s"/>\n%s\n</svg>\n'
                % (self.w, self.h, self.w, self.h, SANS.replace("'", "&apos;"), escape(self.title), escape(self.desc),
                   t["line"], t["paper"], body))


def header(f, title, sub):
    """Title and subtitle at the top left."""
    f.text(24, 38, title, 20, bold=True)
    f.text(24, 62, sub, 14, fill="quiet")



# The design system's own tokens (docs/design-system/colors_and_type.css): the light theme's paper,
# ink and green, and the dark theme's ink scale and green.
THEMES["light"].update({"paper": "#fbf8f3", "panel": "#f0eade", "ink": "#1f1d1a", "quiet": "#4a4744",
                        "rule": "#d4cab2", "line": "#807c76", "accent": "#20964f", "accent_soft": "#d6efde",
                        "good": "#176e3a", "crit": "#a83b2a", "crit_bg": "#f5d8d2"})
THEMES["dark"].update({"paper": "#0b0f0e", "panel": "#11171a", "ink": "#e8ece9", "quiet": "#8a958f",
                       "rule": "#28333a", "line": "#5d6661", "accent": "#34d97e", "accent_soft": "#0c2e1c",
                       "good": "#34d97e", "crit": "#ff7c69", "crit_bg": "#2a1410"})

SOURCE = os.path.join("docs", "design-system", "assets", "diagrams", "06-fits-into-goat-net.svg")
NS = "{http://www.w3.org/2000/svg}"


def source_facts():
    """Title, labels and systems of the source diagram.

    systems: [(kind, side)] for each identity-checked system, kind one of circle/square/diamond/triangle,
    side "above" or "below" the bus, in left-to-right order on each side.
    """
    root = ET.parse(os.path.join(ROOT, SOURCE)).getroot()
    title = root.find(NS + "title").text.strip()
    bus_y = None
    for el in root.iter(NS + "line"):
        if el.get("class") is None and float(el.get("y1")) == float(el.get("y2")) and el.get("stroke-dasharray") is None:
            bus_y = float(el.get("y1"))
            break
    boundary = None
    for el in root.iter(NS + "text"):
        if el.get("class") == "annot" and boundary is None:
            boundary = el.text.strip()
    systems, outsider = [], None
    for el in root.iter():
        if el.get("class") != "node-fill":
            continue
        tag = el.tag[len(NS):]
        if tag == "circle":
            kind, x, y = "circle", float(el.get("cx")), float(el.get("cy"))
        elif tag == "rect":
            kind = "square"
            x, y = float(el.get("x")) + float(el.get("width")) / 2, float(el.get("y")) + float(el.get("height")) / 2
        else:
            pts = [tuple(map(float, p.split(","))) for p in el.get("points").split()]
            kind = "diamond" if len(pts) == 4 else "triangle"
            x, y = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        if el.get("stroke"):
            outsider = kind
            continue
        systems.append((kind, "above" if y < bus_y else "below", x))
    labels = [el.text.strip() for el in root.iter(NS + "text") if el.get("fill") and el.text and el.text.strip() != boundary]
    ident = [el.text.strip() for el in root.iter(NS + "text") if el.get("fill") is None and el.text]
    if not (bus_y and boundary and systems and outsider and len(labels) == 2 and ident):
        sys.exit("make-figures: %s no longer has the bus, boundary, systems and refused outsider this redraw reads" % SOURCE)
    above = [k for k, s, x in sorted(systems, key=lambda t: t[2]) if s == "above"]
    below = [k for k, s, x in sorted(systems, key=lambda t: t[2]) if s == "below"]
    return {"title": title, "boundary": boundary, "above": above, "below": below, "outsider": outsider,
            "no_identity": labels[0], "refused": labels[1], "identity": ident[0]}


W = 880


def shape(f, kind, x, y, r, fill="accent", stroke=None):
    s = ' stroke="{%s}" stroke-width="2"' % stroke if stroke else ""
    if kind == "circle":
        f.circle(x, y, r, fill=fill, stroke=stroke, sw=2)
    elif kind == "square":
        f.add('<rect x="%s" y="%s" width="%s" height="%s" fill="{%s}"%s/>' % (n(x - r), n(y - r), n(2 * r), n(2 * r), fill, s))
    elif kind == "diamond":
        r2 = r * 1.25
        f.add('<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="{%s}"%s/>'
              % (n(x), n(y - r2), n(x + r2), n(y), n(x), n(y + r2), n(x - r2), n(y), fill, s))
    else:
        r2 = r * 1.2
        f.add('<polygon points="%s,%s %s,%s %s,%s" fill="{%s}"%s/>'
              % (n(x), n(y - r2), n(x + r2), n(y + r2 * 0.8), n(x - r2), n(y + r2 * 0.8), fill, s))


def gate(f, x, y):
    """The identity check where a system's link meets the bus."""
    f.rect(x - 9, y - 7, 18, 14, fill="paper", stroke="accent", rx=2, sw=1.5)


def fig_fits():
    s = source_facts()
    title = s["title"]
    head, _, tail = title.partition(" at ")
    boundary = s["boundary"].replace(" — ", ": ").replace(" + ", " and ")
    f = SVG(W, 420, title,
            "%s %d systems attach to one shared bus inside the dashed boundary, each through an identity check; "
            "a system with no identity is refused at the boundary." % (title, len(s["above"]) + len(s["below"])))
    header(f, head, "at " + tail.rstrip(".") if tail else "")

    bx0, bx1, by0, by1 = 28, 680, 96, 392
    f.add('<rect x="%s" y="%s" width="%s" height="%s" rx="4" fill="none" stroke="{accent}" stroke-width="1.8" '
          'stroke-dasharray="8,6"/>' % (n(bx0), n(by0), n(bx1 - bx0), n(by1 - by0)))
    fit(boundary, 14, bx1 - bx0 - 32, bold=True)
    f.add('<rect x="%s" y="%s" width="%s" height="22" fill="{paper}"/>' % (n(bx0 + 14), n(by0 - 11), n(tw(boundary, 14, bold=True) + 16)))
    f.text(bx0 + 22, by0 + 5, boundary, 14, fill="good", bold=True)

    bus_y = 246
    f.line(bx0 + 40, bus_y, bx1 - 40, bus_y, stroke="accent", sw=5)
    f.text(bx0 + 40, bus_y + 28, "the bus", 14, fill="quiet")

    def place(kinds, y, label_dy):
        span = bx1 - bx0 - 170
        for i, k in enumerate(kinds):
            x = bx0 + 120 + (span * (i + 0.5) / len(kinds))
            f.line(x, y + (16 if y < bus_y else -16), x, bus_y, stroke="line", sw=1.8)
            gate(f, x, bus_y + (-11 if y < bus_y else 11))
            shape(f, k, x, y, 14)
            f.text(x, y + label_dy, s["identity"], 14, anchor="middle", fill="ink")

    place(s["above"], 166, -28)
    place(s["below"], 330, 42)

    # the outsider
    ox, oy = 790, bus_y
    f.line(ox - 22, oy, bx1 + 14, oy, stroke="crit", sw=1.8, dash="4,4")
    cx = bx1
    f.line(cx - 9, oy - 9, cx + 9, oy + 9, stroke="crit", sw=3)
    f.line(cx - 9, oy + 9, cx + 9, oy - 9, stroke="crit", sw=3)
    shape(f, s["outsider"], ox, oy, 15, fill="crit_bg", stroke="crit")
    f.text(ox, oy - 34, s["no_identity"], 14, anchor="middle", fill="crit", bold=True)
    f.text(ox, oy + 46, s["refused"], 14, anchor="middle", fill="crit", bold=True)
    return f


def fit(s, size, width, mono=False, bold=False):
    if tw(s, size, mono, bold) > width:
        sys.exit("make-figures: %r does not fit in %d units" % (s, width))


FIGURES = [("identity-at-the-boundary", fig_fits)]


def main(argv):
    check = "--check" in argv
    stale = []
    for name, fn in FIGURES:
        fig = fn()
        for theme in THEMES:
            p = os.path.join(HERE, "%s-%s.svg" % (name, theme))
            out = fig.render(theme)
            if check:
                if not os.path.isfile(p) or open(p, encoding="utf-8").read() != out:
                    stale.append(os.path.relpath(p, ROOT))
            else:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(out)
                print(os.path.relpath(p, ROOT))
    if stale:
        print("out of date: " + ", ".join(stale) + "; run python3 -I docs/figures/make-figures.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
