#!/usr/bin/env python3
"""Figures for goatdocs goat/industry/: fixed-layout SVG, page CSS classes only.

fit_svg()      the hero: where a product joins goat; groups carry data-k for the selector
nations_svg()  three national goatnets, data released between them, one product in each
"""
import html


def esc(s):
    return html.escape(s, quote=True)


class Fig:
    def __init__(self, sub=13):
        self.out = []
        self.sub = sub

    def rect(self, x, y, w, h, cls, rx=8, k=None):
        a = f' data-k="{k}"' if k else ""
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"{a}/>')

    def text(self, x, y, s, cls="t", size=15, bold=False, anchor=None, halo=False):
        a = f' text-anchor="{anchor}"' if anchor else ""
        b = ' font-weight="700"' if bold else ""
        c = cls + (" halo" if halo else "")
        self.out.append(f'<text x="{x}" y="{y}"{a} class="{c}" font-size="{size}"{b}>{esc(s)}</text>')

    def line(self, pts, cls="ln", k=None):
        d = "M" + "L".join(f"{x} {y}" for x, y in pts)
        a = f' data-k="{k}"' if k else ""
        self.out.append(f'<path d="{d}" class="{cls}"{a}/>')

    def box(self, x, y, w, h, title, sub=None, cls="bx", k=None, center=False):
        self.out.append('<g class="node"' + (' data-k="%s"' % k if k else "") + '>')
        self.rect(x, y, w, h, cls)
        if center:
            cx = x + w // 2
            self.text(cx, y + (24 if sub else h // 2 + 5), title, "t", 15, True, "middle")
            if sub:
                self.text(cx, y + 43, sub, "tq", 13, False, "middle")
        else:
            self.text(x + 14, y + (23 if sub else h // 2 + 5), title, "t", 15, True)
            if sub:
                self.text(x + 14, y + 43, sub, "tq", self.sub)
        self.out.append("</g>")

    def svg(self, id_, w, h, label, cls="viz"):
        return (f'<svg id="{id_}" class="{cls}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
                + "\n".join(self.out) + "\n</svg>")


def fit_svg():
    f = Fig(sub=14)
    W = 600
    # what uses the data
    tops = [("C2 systems", "plans and tasks"), ("Data platforms", "store and analyze"), ("AI agents", "read and act")]
    xs = [20, 216, 412]
    for x, (t, s) in zip(xs, tops):
        f.box(x, 16, 168, 56, t, s, "bx", "c2")
    for x in xs:
        f.line([(x + 84, 72), (x + 84, 134)], "flow", "c2")
    f.text(300, 108, "native client or open-entity-gateway", "tq", 14, False, "middle", halo=True)
    # the fabric
    f.rect(20, 134, 560, 214, "bxp", 12)
    f.text(36, 160, "goat", "t", 17, True)
    f.text(84, 160, "the same three layers on every site", "tq", 14)
    layers = [("Data", "Zenoh publish/subscribe, no central broker", "data"),
              ("Identity", "people, machines and workloads", "ident"),
              ("Mesh", "WireGuard tunnels, NetBird control", "mesh")]
    for i, (t, s, k) in enumerate(layers):
        y = 174 + i * 56
        f.out.append(f'<g class="node layer" data-k="{k}">')
        f.rect(36, y, 528, 46, "bx", 6)
        f.text(52, y + 29, t, "t", 15, True)
        f.text(148, y + 29, s, "tq", 14)
        f.out.append("</g>")
    # doors and sources
    f.box(20, 392, 270, 56, "goat-transformers, open-billie", "open formats", "bx", "sensor")
    f.box(310, 392, 270, 56, "first-bite, octo-pod", "private formats", "bx", "legacy")
    f.line([(155, 392), (155, 348)], "flow", "sensor")
    f.line([(445, 392), (445, 348)], "flow", "legacy")
    f.box(20, 484, 270, 56, "Systems with an open format", "CoT, SAPIENT, ASTERIX", "bx", "sensor")
    f.box(310, 484, 270, 56, "Systems with a private format", "or a link you cannot change", "bx", "legacy")
    f.line([(155, 484), (155, 448)], "flow", "sensor")
    f.line([(445, 484), (445, 448)], "flow", "legacy")
    # the network underneath
    f.line([(300, 348), (300, 576)], "flow", "network")
    f.out.append('<g class="node" data-k="network">')
    f.rect(20, 576, 560, 44, "bxp", 8)
    f.text(300, 603, "Any IP network: radio, MANET, 5G, satellite, fiber", "t", 15, True, "middle", halo=True)
    f.out.append("</g>")
    label = ("Where a product joins goat. C2 systems, data platforms and AI agents subscribe to the data layer, natively or "
             "through open-entity-gateway. Systems with an open format, whether sensors, effectors or other equipment, enter "
             "through goat-transformers and open-billie; systems with a private format enter through first-bite or octo-pod. goat itself is three "
             "layers on every site: data, identity and mesh. It runs over any IP network: radio, MANET, 5G, satellite or "
             "fiber. Security products replace the mesh or identity layer.")
    return f.svg("fig-fit", W, 636, label, "viz fitmap")


def nations_svg():
    f = Fig()
    W, H = 800, 322
    zones = [(10, "Nation A"), (302, "Nation B"), (594, "Nation C")]
    zw = 196
    for x0, name in zones:
        f.rect(x0, 30, zw, 280, "bxp", 12)
        f.text(x0 + 18, 60, name, "t", 16, True)
        f.text(x0 + 18, 80, "its own goatnet", "tq", 13)
        f.box(x0 + 18, 102, 160, 48, "goat fabric", None, "bxa", center=True)
        for px, lab in ((x0 + 18, "Sensors"), (x0 + 104, "C2")):
            f.line([(px + 37, 196), (px + 37, 150)])
            f.rect(px, 196, 74, 30, "bx", 15)
            f.text(px + 37, 216, lab, "t", 13, False, "middle")
        f.line([(x0 + 98, 252), (x0 + 98, 150)], "lna")
        f.rect(x0 + 18, 252, 160, 36, "prod", 18)
        f.text(x0 + 98, 275, "your product", "ton", 14, True, "middle")
    for (a, _), (b, _) in zip(zones, zones[1:]):
        x1, x2 = a + 178, b + 18
        f.line([(x1, 126), (x2, 126)], "lna")
        for bx in (a + zw, b):
            f.out.append(f'<path d="M{bx} 117L{bx + 9} 126L{bx} 135L{bx - 9} 126z" class="bn"/>')
        f.text((a + zw + b) // 2, 112, "release set", "ta", 13, True, "middle")
    label = ("Three notional nations, each running its own goatnet with its own sensors and C2. Each releases chosen data "
             "to the next through a pair of boundary nodes. The same product runs inside each nation's goatnet, because "
             "every goatnet has the same open interfaces.")
    return f.svg("fig-nations", W, H, label)


if __name__ == "__main__":
    print(fit_svg())
    print(nations_svg())


def glyph(kind):
    """A small picture of where one kind of product attaches: data, identity and mesh bars, as in the fit map."""
    o = []
    bars = [("data", 22), ("ident", 36), ("mesh", 50)]
    on = {"security": {"ident", "mesh"}}.get(kind, set())
    for k, y in bars:
        o.append(f'<rect x="28" y="{y}" width="64" height="10" rx="2" class="{"bxa" if k in on else "bx"}"/>')
    if kind in ("open", "private"):
        o.append('<path d="M60 66V32" class="lna"/>')
        o.append('<rect x="44" y="64" width="32" height="12" rx="6" class="prod"/>')
        if kind == "private":
            o.append('<rect x="50" y="60" width="20" height="4" rx="1" class="fa"/>')
    elif kind == "c2":
        o.append('<path d="M60 14V22" class="lna"/>')
        o.append('<rect x="44" y="2" width="32" height="12" rx="6" class="prod"/>')
    elif kind == "network":
        o.append('<path d="M60 60V68" class="lna"/>')
        o.append('<rect x="14" y="68" width="92" height="8" rx="4" class="prod"/>')
    elif kind == "integration":
        o.append('<rect x="20" y="15" width="80" height="52" rx="6" class="gdash"/>')
    return ('<svg class="glyph" viewBox="0 0 120 80" aria-hidden="true">' + "".join(o) + "</svg>")
