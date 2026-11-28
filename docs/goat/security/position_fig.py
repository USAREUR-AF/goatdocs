"""The position figure: one boundary with everything alike inside it, against a network that is hidden
from the internet and in which every connection is separately protected. Drawn to the operator's
specification of 28 Nov 2026. Fixed layout; colours are the page's tokens plus eight link tones."""
import itertools, math

STYLE = """<style>
.pf{--l0:#1f8a55;--l1:#11868c;--l2:#2a6fc0;--l3:#6b8f1a;--l4:#5c7183;--l5:#0f7460;--l6:#2f8fb8;--l7:#7f8f2a;--pf-net:#e4e6da;--pf-zone:#e6ecdf;--pf-one:#4d564f}
@media (prefers-color-scheme: dark){.pf{--l0:#6fd39a;--l1:#4fc3c8;--l2:#6aa9ee;--l3:#a7d15a;--l4:#9fb4c6;--l5:#3fae86;--l6:#8fd0f0;--l7:#c5d98a;--pf-net:#232a20;--pf-zone:#1c2619;--pf-one:#b9c0b8}}
.pf text{font-family:var(--sans)}
</style>"""
DASH = ["2 7", "9 6", "1 6", "12 5 2 5", "5 5", "14 6", "3 4", "8 4 2 4"]
ALT = ("Two drawings, one above the other. Above, a few fixed boundaries: one closed boundary with a door "
       "facing the public internet; inside it one network in which every party is joined to every other by "
       "the same kind of line, and three of those lines carry an extra lock added by an application. Below, "
       "no inside and no outside: there is no boundary and no door, and nothing answers from the public "
       "internet; the parties stand in small groups, most groups are joined into one network and one pair "
       "stands apart; every connection is drawn in its own colour and pattern, because each one is "
       "separately encrypted, authenticated and authorized.")


def _fig(w, top_n, clusters, bridges, cap_top, cap_bot, ts, cs, band_h, top_h, bot_h, r):
    INK, QUIET, PAPER = "var(--ink)", "var(--quiet)", "var(--paper)"
    o = []
    pad = 16 if w < 600 else 24

    def band(y):
        o.append(f'<rect x="0" y="{y}" width="{w}" height="{band_h}" fill="var(--pf-net)"/>')
        o.append(f'<text x="{pad}" y="{y + band_h * 0.66:.0f}" font-size="{cs * 0.86:.1f}" fill="{QUIET}" letter-spacing="1.4">THE PUBLIC INTERNET</text>')

    def probe(x, y1, y2, through=False):
        o.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{INK}" stroke-width="2.2" stroke-dasharray="2 6" stroke-linecap="round"/>')
        if through:
            o.append(f'<path d="M{x - 6} {y2 - 9} L{x} {y2} L{x + 6} {y2 - 9}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            o.append(f'<line x1="{x - 9}" y1="{y2}" x2="{x + 9}" y2="{y2}" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>')

    def caption(y, lines):
        for i, ln in enumerate(lines):
            o.append(f'<text x="{pad}" y="{y + i * cs * 1.35:.0f}" font-size="{cs}" fill="{QUIET}">{ln}</text>')

    # ---- above: one boundary -------------------------------------------------------------------------
    y = ts + 8
    o.append(f'<text x="{pad}" y="{y}" font-size="{ts}" font-weight="700" fill="{INK}">A few fixed boundaries</text>')
    y += 16
    band(y)
    by = y + band_h + 44
    bx, bw, bh = (w * 0.2, w * 0.6, top_h) if w > 600 else (pad, w - 2 * pad, top_h)
    o.append(f'<rect x="{bx:.0f}" y="{by}" width="{bw:.0f}" height="{bh}" rx="30" fill="var(--pf-zone)" stroke="{INK}" stroke-width="5"/>')
    gx = bx + bw / 2
    o.append(f'<rect x="{gx - 26:.0f}" y="{by - 6}" width="52" height="12" fill="var(--pf-zone)"/>')
    o.append(f'<path d="M{gx - 26:.0f} {by - 10} v20 M{gx + 26:.0f} {by - 10} v20" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
    for dx in (-bw * 0.3, -13, 13, bw * 0.3):
        probe(round(gx + dx), y + band_h + 6, by - 4 if abs(dx) < 20 else by - 14, through=abs(dx) < 20)
    cx, cy, rx, ry = gx, by + bh / 2 + 6, bw * 0.39, bh * 0.34
    T = [(cx + rx * math.cos(math.radians(k * 360 / top_n - 90)), cy + ry * math.sin(math.radians(k * 360 / top_n - 90))) for k in range(top_n)]
    for a, b in itertools.combinations(range(top_n), 2):
        o.append(f'<line x1="{T[a][0]:.1f}" y1="{T[a][1]:.1f}" x2="{T[b][0]:.1f}" y2="{T[b][1]:.1f}" stroke="var(--pf-one)" stroke-width="1.5"/>')
    for a, b in ((1, 2), (top_n // 2, top_n // 2 + 1), (top_n - 2, top_n - 1)):
        mx, my = (T[a][0] + T[b][0]) / 2, (T[a][1] + T[b][1]) / 2
        o.append(f'<g transform="translate({mx:.1f} {my:.1f})"><circle r="12" fill="var(--pf-zone)" stroke="var(--pf-one)" stroke-width="2"/>'
                 f'<rect x="-5" y="-1.5" width="10" height="8" rx="2" fill="var(--pf-one)"/>'
                 f'<path d="M-3.1 -1.5 v-2.6 a3.1 3.1 0 0 1 6.2 0 v2.6" fill="none" stroke="var(--pf-one)" stroke-width="1.9"/></g>')
    for x, yy in T:
        o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r}" fill="{INK}"/>')
    y = by + bh + 16 + cs
    caption(y, cap_top)
    y += len(cap_top) * cs * 1.35 + 22
    o.append(f'<line x1="0" y1="{y:.0f}" x2="{w}" y2="{y:.0f}" stroke="var(--rule)" stroke-width="1.5"/>')
    # ---- below: hidden, every connection its own -----------------------------------------------------
    y += ts + 18
    o.append(f'<text x="{pad}" y="{y:.0f}" font-size="{ts}" font-weight="700" fill="{INK}">No inside, no outside</text>')
    y += 16
    band(y)
    xs = [w * f for f in ((0.27, 0.42, 0.57, 0.73) if w > 600 else (0.3, 0.5, 0.7))]
    for x in xs:
        probe(round(x), y + band_h + 6, y + band_h + 30)
    g = y + band_h + 58
    P, idx, k = [], [], 0
    for cxn, cyn, offs in clusters:
        idx.append(list(range(k, k + len(offs)))); k += len(offs)
        P += [(cxn + ox, g + cyn + oy) for ox, oy in offs]
    L = []
    for grp in idx:
        L += list(zip(grp, grp[1:]))
        if len(grp) > 3: L.append((grp[0], grp[-1]))
    for ca, cb in bridges:  # the closest pair of parties between two groups
        a, b = min(((i, j) for i in idx[ca] for j in idx[cb]), key=lambda p: math.dist(P[p[0]], P[p[1]]))
        L.append((a, b))
    for n, (a, b) in enumerate(L):
        o.append(f'<line x1="{P[a][0]:.1f}" y1="{P[a][1]:.1f}" x2="{P[b][0]:.1f}" y2="{P[b][1]:.1f}" stroke="var(--l{n % 8})" stroke-width="3.2" stroke-dasharray="{DASH[(n * 3) % 8]}" stroke-linecap="round"/>')
    for n, (x, yy) in enumerate(P):
        o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r + 5.5}" fill="{PAPER}" stroke="var(--l{(n * 5) % 8})" stroke-width="2"/><circle cx="{x:.1f}" cy="{yy:.1f}" r="{r - 1}" fill="{INK}"/>')
    y = g + bot_h + cs + 6
    caption(y, cap_bot)
    h = y + len(cap_bot) * cs * 1.35
    return w, round(h), "\n".join(o)


def _tri(s=34): return [(-s, -s * 0.5), (s * 0.9, -s * 0.75), (s * 0.2, s * 0.85)]
def _quad(s=36): return [(-s, -s * 0.6), (s * 0.7, -s * 0.9), (s, s * 0.5), (-s * 0.5, s * 0.8)]
def _pair(s=30): return [(-s, s * 0.4), (s, -s * 0.4)]


def position_svg(wide=True):
    if wide:
        clusters = [(150, 60, _tri()), (420, 50, _quad()), (700, 62, _tri()), (960, 54, _quad()),
                    (285, 205, _pair()), (560, 212, _tri()), (835, 206, _pair()), (1048, 220, _pair())]
        bridges = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (4, 5), (2, 5), (5, 6), (3, 6)]
        w, h, body = _fig(1120, 9, clusters, bridges,
                          ["One boundary, with a door on the internet. Inside, every connection is alike and trusted. A few applications add a lock."],
                          ["Hidden from the internet. Every connection is separately encrypted, authenticated and authorized."],
                          ts=22, cs=16.5, band_h=44, top_h=236, bot_h=262, r=9)
        cls = "viz wide pf"
    else:
        clusters = [(110, 50, _tri(30)), (345, 48, _quad(30)), (112, 190, _quad(30)), (348, 196, _tri(30)),
                    (118, 330, _pair(28)), (330, 334, _tri(30)), (232, 440, _pair(26))]
        bridges = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
        w, h, body = _fig(464, 7, clusters, bridges,
                          ["One boundary, with a door on the internet.", "Inside, every connection is alike and trusted.", "A few applications add a lock."],
                          ["Hidden from the internet. Every connection is", "separately encrypted, authenticated and authorized."],
                          ts=17, cs=14, band_h=38, top_h=250, bot_h=478, r=8)
        cls = "viz narrow pf"
    alt = ALT.replace('"', "&quot;")
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" role="img" aria-label="{alt}">\n{body}\n</svg>'


def position_figure():
    return STYLE + "\n" + position_svg(True) + "\n" + position_svg(False)
