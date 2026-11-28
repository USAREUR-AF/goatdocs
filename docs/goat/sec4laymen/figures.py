"""The drawings of docs/goat/sec4laymen. Fixed-layout SVG, composed by hand on a 360-unit-wide sheet
so that every mark and word is readable on a phone. One idea per drawing. Colours are the page's
tokens only: ink for the world, one teal for what belongs to the private network."""

INK, QUIET, LINE, RULE = "var(--ink)", "var(--quiet)", "var(--line)", "var(--rule)"
ACC, SOFT, PANEL, PAPER, WARM = "var(--accent)", "var(--accent-soft)", "var(--panel)", "var(--paper)", "var(--soft)"


def svg(h, alt, body):
    return (f'<svg viewBox="0 0 360 {h}" role="img" aria-label="{alt}" fill="none" stroke-linecap="round" '
            f'stroke-linejoin="round">\n' + "\n".join(body) + "\n</svg>")


def text(x, y, s, size=13.5, cls="svg-q", anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}" stroke="none"{w}>{s}</text>'


def house(x, y, w=46, h=30, ours=False, door=True, lit=False, dotted=False):
    """(x, y) is the middle of the ground line under the house."""
    col = ACC if ours else INK
    fill = SOFT if ours else PANEL
    dash = ' stroke-dasharray="3 5"' if dotted else ""
    if dotted:
        fill = "none"
    l, r, top = x - w / 2, x + w / 2, y - h
    o = [f'<path d="M{l} {y} V{top} L{x} {top - h * 0.62:.1f} L{r} {top} V{y} Z" fill="{fill}" stroke="{col}" stroke-width="2.4"{dash}/>']
    if door and not dotted:
        o.append(f'<path d="M{x - 5} {y} v-13 h10 v13" stroke="{col}" stroke-width="2"/>')
    if lit:
        o.append(f'<rect x="{x + 7}" y="{top + 5}" width="9" height="9" rx="1.5" fill="{ACC}" stroke="none"/>')
    return "\n".join(o)


def lock(x, y, s=1.0, col=None, bg=None, opened=False):
    """A padlock centred on (x, y)."""
    col = col or ACC
    w, h = 15 * s, 11.5 * s
    sh = f'M{x - 4.5 * s} {y - h / 2 + 1} v{-4 * s} a{4.5 * s} {4.5 * s} 0 0 1 {9 * s} 0 v{4 * s}'
    if opened:
        sh = f'M{x - 4.5 * s} {y - h / 2 + 1} v{-4 * s} a{4.5 * s} {4.5 * s} 0 0 1 {9 * s} 0'
    o = []
    if bg:
        o.append(f'<circle cx="{x}" cy="{y - 2 * s}" r="{13 * s}" fill="{bg}" stroke="none"/>')
    o.append(f'<path d="{sh}" stroke="{col}" stroke-width="{2.2 * s:.1f}"/>')
    o.append(f'<rect x="{x - w / 2}" y="{y - h / 2 + 1}" width="{w}" height="{h}" rx="{2.4 * s:.1f}" fill="{col}" stroke="none"/>')
    return "\n".join(o)


def envelope(x, y, w=32, h=22, col=None, fill=None, locked=False):
    """An envelope centred on (x, y)."""
    col = col or INK
    fill = fill or PANEL
    l, t = x - w / 2, y - h / 2
    o = [f'<rect x="{l}" y="{t}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{col}" stroke-width="2"/>',
         f'<path d="M{l + 1.5} {t + 2} L{x} {y + 2} L{l + w - 1.5} {t + 2}" stroke="{col}" stroke-width="2"/>']
    if locked:
        o.append(lock(x + w / 2 - 2, y + h / 2 - 2, 0.72, ACC, PANEL))
    return "\n".join(o)


def key(x, y, s=1.0, col=None):
    col = col or ACC
    return (f'<circle cx="{x}" cy="{y}" r="{6 * s}" stroke="{col}" stroke-width="{2.4 * s:.1f}"/>'
            f'<path d="M{x + 6 * s} {y} h{17 * s} M{x + 17 * s} {y} v{5.5 * s} M{x + 22 * s} {y} v{4 * s}" stroke="{col}" stroke-width="{2.4 * s:.1f}"/>')


def person(x, y, col=None, s=1.0):
    """A standing person; (x, y) is the middle of the ground line under them."""
    col = col or INK
    return (f'<circle cx="{x}" cy="{y - 27 * s}" r="{6 * s}" fill="{PANEL}" stroke="{col}" stroke-width="2.2"/>'
            f'<path d="M{x - 9 * s} {y} v{-8 * s} a{9 * s} {9 * s} 0 0 1 {18 * s} 0 v{8 * s}" fill="{PANEL}" stroke="{col}" stroke-width="2.2"/>')


def computer(x, y, col=None, fill=None, s=1.0):
    """A small computer; (x, y) is the middle of its base."""
    col = col or INK
    fill = fill or PANEL
    return (f'<rect x="{x - 12 * s}" y="{y - 21 * s}" width="{24 * s}" height="{16 * s}" rx="2.5" fill="{fill}" stroke="{col}" stroke-width="2"/>'
            f'<path d="M{x - 7 * s} {y} h{14 * s} M{x} {y} v{-5 * s}" stroke="{col}" stroke-width="2"/>')


def page(x, y, w=26, h=32, col=None, lines=3, squiggle=False):
    col = col or INK
    l, t = x - w / 2, y - h / 2
    o = [f'<rect x="{l}" y="{t}" width="{w}" height="{h}" rx="3" fill="{PANEL}" stroke="{col}" stroke-width="2"/>']
    for i in range(lines):
        yy = t + 9 + i * 7
        if squiggle:
            o.append(f'<path d="M{l + 5} {yy} q3 -4 5 0 t5 0 t5 0" stroke="{QUIET}" stroke-width="1.8"/>')
        else:
            o.append(f'<path d="M{l + 5} {yy} h{w - 10 - (5 if i == lines - 1 else 0)}" stroke="{QUIET}" stroke-width="1.8"/>')
    return "\n".join(o)


def arrow(x1, y1, x2, y2, col=None, w=2.2, dash=None):
    import math
    col = col or QUIET
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 8 * math.cos(a), y2 - 8 * math.sin(a)
    p1 = (hx + 4.5 * math.sin(a), hy - 4.5 * math.cos(a))
    p2 = (hx - 4.5 * math.sin(a), hy + 4.5 * math.cos(a))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{x1} {y1} L{hx:.1f} {hy:.1f}" stroke="{col}" stroke-width="{w}"{d}/>'
            f'<path d="M{x2} {y2} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z" fill="{col}" stroke="{col}" stroke-width="1"/>')


def tick(x, y, r=11):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ACC}" stroke="none"/>'
            f'<path d="M{x - r * 0.45:.1f} {y} l{r * 0.33:.1f} {r * 0.36:.1f} l{r * 0.6:.1f} -{r * 0.7:.1f}" stroke="var(--on-accent)" stroke-width="2.4"/>')


def ground(y, x1=18, x2=342):
    return f'<path d="M{x1} {y} H{x2}" stroke="{RULE}" stroke-width="2.4"/>'


# ---- the first screen: three places kept in touch by a private, locked route ----------------------------
def hero():
    o = [f'<path d="M24 150 H336 M92 150 V186 M228 150 V186 M24 186 H336" stroke="{RULE}" stroke-width="7"/>',
         f'<path d="M64 116 C64 40 180 26 180 70 M180 70 C180 26 296 40 296 116 M64 124 C120 168 240 168 296 124" stroke="{ACC}" stroke-width="3" stroke-dasharray="1 7"/>',
         house(64, 150, ours=True, lit=True), house(180, 104, ours=True, lit=True), house(296, 150, ours=True, lit=True),
         envelope(118, 52, locked=True), envelope(244, 160, locked=True)]
    return svg(206, "Three houses joined by a dotted private route that runs above the public streets. A locked envelope travels along the route.", o)


def why():
    o = [f'<path d="M180 16 V176" stroke="{RULE}" stroke-width="2" stroke-dasharray="2 6"/>',
         # left: a stranger reads the letter
         house(48, 112), house(132, 112),
         f'<path d="M71 96 H109" stroke="{LINE}" stroke-width="2.4"/>',
         envelope(90, 70, 30, 20),
         person(90, 164, QUIET),
         f'<path d="M90 126 V84" stroke="{QUIET}" stroke-width="2" stroke-dasharray="2 5"/>',
         text(90, 190, "read by a stranger", 13.5),
         # right: the line is cut
         house(228, 112), house(312, 112),
         f'<path d="M251 96 H262 M278 96 H289" stroke="{LINE}" stroke-width="2.4"/>',
         f'<path d="M264 88 l6 16 M270 88 l6 16" stroke="{INK}" stroke-width="2.4"/>',
         text(270, 190, "cut off", 13.5)]
    return svg(204, "Two things that go wrong. On the left, a stranger reads a letter that passes between two houses. On the right, the line between two houses is cut.", o)


def basics():
    o = [f'<path d="M20 76 H340 M20 150 H340 M96 30 V182 M240 30 V182" stroke="{RULE}" stroke-width="8"/>',
         house(48, 70), house(170, 70), house(300, 144), house(48, 144),
         # the post office
         f'<path d="M146 150 V112 H206 V150 Z" fill="{PANEL}" stroke="{INK}" stroke-width="2.4"/>',
         f'<path d="M140 112 H212 M158 150 v-16 h12 v16 M184 124 h12 v10 h-12 z" stroke="{INK}" stroke-width="2"/>',
         f'<path d="M206 112 V92 h13 l-4 5 l4 5 h-13" fill="{SOFT}" stroke="{ACC}" stroke-width="2"/>',
         envelope(240, 46, 28, 19, ACC, SOFT),
         text(48, 172, "computer", 13.5), text(176, 172, "server", 13.5), text(284, 51, "message", 13.5)]
    return svg(196, "A small town of streets. The houses are computers, the post office is a server, and a letter on the street is a message.", o)


def locks():
    o = [text(22, 30, "Decode: translate. No secret is needed.", 13.5, "svg-t", "start", True),
         page(74, 78, squiggle=True), arrow(110, 78, 232, 78), page(270, 78),
         f'<path d="M150 66 h10 m-5 -5 v10 M176 66 h10 M176 72 h10" stroke="{QUIET}" stroke-width="0"/>',
         text(171, 68, "same words,", 13.5), text(171, 98, "another alphabet", 13.5),
         f'<path d="M20 124 H340" stroke="{RULE}" stroke-width="2" stroke-dasharray="2 6"/>',
         text(22, 152, "Decrypt: unlock. Only the key opens it.", 13.5, "svg-t", "start", True),
         # locked box
         f'<rect x="52" y="178" width="46" height="32" rx="4" fill="{SOFT}" stroke="{ACC}" stroke-width="2.4"/>',
         lock(75, 196, 1.0, ACC),
         key(128, 194), arrow(170, 194, 232, 194),
         # opened box with the page
         f'<rect x="247" y="186" width="46" height="24" rx="4" fill="{SOFT}" stroke="{ACC}" stroke-width="2.4"/>',
         f'<path d="M247 186 l8 -14 h46 l-8 14" fill="{PANEL}" stroke="{ACC}" stroke-width="2.4"/>',
         page(270, 176, 22, 26, INK, 2)]
    return svg(228, "Two rows. Decode: a page in one alphabet becomes a page in another, with no key. Decrypt: a locked box and a key become an open box with the page inside.", o)


def route():
    o = [f'<path d="M20 60 H340 M20 122 H340 M20 184 H340 M70 26 V200 M180 26 V200 M290 26 V200" stroke="{RULE}" stroke-width="8"/>',
         house(125, 54, 40, 26), house(235, 116, 40, 26), house(125, 178, 40, 26), house(320, 54, 34, 24),
         # the private route follows the public roads
         f'<path d="M70 108 V60 H180 V122 H290 V170" stroke="{ACC}" stroke-width="8"/>',
         f'<path d="M70 108 V60 H180 V122 H290 V170" stroke="{PANEL}" stroke-width="2.4" stroke-dasharray="1 7"/>',
         house(40, 116, 40, 26, ours=True, lit=True), house(318, 178, 40, 26, ours=True, lit=True),
         envelope(180, 92, 26, 18, ACC, PANEL, locked=True)]
    return svg(212, "A grid of public streets with houses. A teal route runs along the same streets between two teal houses, and a locked envelope travels inside it.", o)


def hidden():
    o = [ground(150),
         house(48, 150, 50, 38), house(112, 150, 50, 38),
         house(226, 150, 62, 46, ours=True, door=False, lit=True),
         house(310, 150, 50, 38),
         person(170, 150, QUIET),
         f'<path d="M184 128 l8 -3 M184 134 h9 M184 140 l8 3" stroke="{QUIET}" stroke-width="2"/>',
         text(226, 178, "no door, and no answer", 13.5)]
    return svg(194, "A street of houses. Three have a door on the street. The teal house has no door, and a stranger knocking at its wall gets no answer.", o)


def own():
    o = [# the rented computer in the middle sky
         f'<path d="M142 66 a17 17 0 0 1 14 -27 a23 23 0 0 1 44 3 a16 16 0 0 1 14 24 Z" fill="{PANEL}" stroke="{LINE}" stroke-width="2.2" stroke-dasharray="4 5"/>',
         envelope(180, 54, 26, 18, ACC, PANEL, locked=True),

         # two sites
         f'<path d="M22 196 V128 L78 96 L134 128 V196 Z" fill="{SOFT}" stroke="{ACC}" stroke-width="2.4"/>',
         f'<path d="M226 196 V128 L282 96 L338 128 V196 Z" fill="{SOFT}" stroke="{ACC}" stroke-width="2.4"/>',
         computer(50, 186, ACC, PANEL), computer(106, 186, ACC, PANEL), key(64, 142, 0.9),
         computer(254, 186, ACC, PANEL), computer(310, 186, ACC, PANEL), key(268, 142, 0.9),
         arrow(104, 104, 150, 70, ACC, 2.4, "1 6"), arrow(212, 70, 256, 104, ACC, 2.4, "1 6"),
         text(180, 20, "a rented computer carries it, with no key", 13.5),
         text(78, 216, "one site, its own key", 13.5), text(282, 216, "another, its own key", 13.5)]
    return svg(228, "Two sites, each a house that holds its own computers and its own key. Between them a rented computer in the sky carries a locked envelope and holds no key.", o)


def trust():
    def building(x, locked):
        col = ACC if locked else INK
        b = [f'<rect x="{x}" y="46" width="140" height="112" rx="5" fill="{SOFT if locked else PANEL}" stroke="{col}" stroke-width="2.4"/>',
             f'<path d="M{x} 102 H{x + 140} M{x + 70} 46 V158" stroke="{col}" stroke-width="2.2"/>']
        for dx, dy in ((35, 102), (105, 102)):
            if locked:
                b.append(lock(x + dx, 102, 0.85, ACC, SOFT))
            else:
                b.append(f'<path d="M{x + dx - 9} 102 H{x + dx + 9}" stroke="{PANEL}" stroke-width="5"/>')
        for dy in (74, 130):
            if locked:
                b.append(lock(x + 70, dy, 0.85, ACC, SOFT))
            else:
                b.append(f'<path d="M{x + 70} {dy - 9} V{dy + 9}" stroke="{PANEL}" stroke-width="5"/>')
        # the front door
        b.append(f'<path d="M{x + 28} 158 H{x + 44}" stroke="{PANEL if not locked else SOFT}" stroke-width="5"/>')
        if locked:
            b.append(lock(x + 36, 158, 0.85, ACC, SOFT))
        return "\n".join(b)
    o = [text(90, 28, "One guard at the door", 13.5, "svg-t", "middle", True),
         building(20, False), person(56, 198, INK, 0.9),
         text(90, 214, "every room is open", 13.5),
         text(270, 28, "Every door checks", 13.5, "svg-t", "middle", True),
         building(200, True),
         text(270, 214, "every door is locked", 13.5)]
    return svg(226, "Two buildings. In the first, one guard stands at the front door and every room inside is open. In the second, every door has its own lock.", o)


def layers():
    o = [f'<rect x="22" y="26" width="196" height="150" rx="16" fill="{PANEL}" stroke="{INK}" stroke-width="2.6"/>',
         f'<rect x="50" y="52" width="140" height="98" rx="12" fill="{SOFT}" stroke="{ACC}" stroke-width="2.6"/>',
         page(120, 101, 54, 46, INK, 4),
         lock(218, 52, 1.05, INK, PANEL), lock(190, 132, 1.05, ACC, SOFT),
         f'<path d="M234 52 H250 M206 132 H250 M148 101 H236 q14 0 14 0" stroke="{LINE}" stroke-width="1.8"/>',
         text(256, 49, "a lock for the", 13.5, "svg-t", "start"), text(256, 65, "journey", 13.5, "svg-t", "start"),
         text(256, 97, "the message", 13.5, "svg-t", "start"),
         text(256, 129, "a lock for its", 13.5, "svg-t", "start"), text(256, 145, "named readers", 13.5, "svg-t", "start")]
    return svg(200, "A message inside two envelopes, one inside the other. The outer one is locked for the journey between two computers. The inner one is locked for the named readers.", o)


def jar(x, y, broken=False):
    """A sealed parcel: a box, a band around it and the maker's seal on the band."""
    col = QUIET if broken else ACC
    o = [f'<rect x="{x - 19}" y="{y - 34}" width="38" height="34" rx="4" fill="{PANEL if broken else SOFT}" stroke="{col}" stroke-width="2.4"/>']
    if broken:
        o.append(f'<path d="M{x - 19} {y - 17} H{x - 6} M{x + 7} {y - 17} H{x + 19}" stroke="{col}" stroke-width="2.4"/>')
        o.append(f'<path d="M{x - 6} {y - 22} l5 4 l-4 4 l6 4" stroke="{INK}" stroke-width="2.2"/>')
    else:
        o.append(f'<path d="M{x - 19} {y - 17} H{x + 19}" stroke="{col}" stroke-width="2.4"/>')
        o.append(f'<circle cx="{x}" cy="{y - 17}" r="7.5" fill="{ACC}" stroke="none"/>')
    return "\n".join(o)


def verified():
    o = [jar(52, 76), arrow(82, 60, 146, 60, ACC),
         f'<circle cx="180" cy="60" r="20" fill="{PANEL}" stroke="{ACC}" stroke-width="2.2"/>',
         f'<circle cx="176" cy="56" r="7" stroke="{ACC}" stroke-width="2.2"/><path d="M181 61 l7 7" stroke="{ACC}" stroke-width="2.6"/>',
         arrow(206, 60, 268, 60, ACC), computer(300, 74, ACC, SOFT, 1.25), tick(326, 42, 10),
         text(180, 100, "seal and contents match: it runs", 13.5),
         f'<path d="M20 116 H340" stroke="{RULE}" stroke-width="2" stroke-dasharray="2 6"/>',
         jar(52, 180, True), arrow(82, 164, 146, 164, QUIET),
         f'<circle cx="180" cy="164" r="20" fill="{PANEL}" stroke="{INK}" stroke-width="2.2"/>',
         f'<circle cx="176" cy="160" r="7" stroke="{INK}" stroke-width="2.2"/><path d="M181 165 l7 7" stroke="{INK}" stroke-width="2.6"/>',
         f'<path d="M222 146 V182" stroke="{INK}" stroke-width="4"/>',
         computer(300, 178, LINE, PANEL, 1.25),
         text(180, 206, "seal broken or contents changed: refused", 13.5)]
    return svg(220, "Two rows. A jar with its seal intact is checked and goes onto a computer. A jar with a broken seal is checked and stopped before it reaches the computer.", o)


def box(x, y, col=None, fill=None, dotted=False):
    col = col or ACC
    fill = fill or SOFT
    d = ' stroke-dasharray="3 5"' if dotted else ""
    return f'<rect x="{x - 21}" y="{y - 15}" width="42" height="30" rx="4" fill="{"none" if dotted else fill}" stroke="{col}" stroke-width="2.4"{d}/>'


def quantum():
    o = [f'<path d="M24 152 H322" stroke="{RULE}" stroke-width="2.4"/>', arrow(300, 152, 338, 152, LINE),
         f'<circle cx="62" cy="152" r="5" fill="{INK}" stroke="none"/><circle cx="262" cy="152" r="5" fill="{INK}" stroke="none"/>',
         text(62, 176, "today", 13, "svg-t", "middle", True), text(262, 176, "years later", 13, "svg-t", "middle", True),
         # today: the locked box, and a copy taken
         box(62, 84), lock(62, 86, 0.95, ACC),
         box(62, 40, QUIET, None, True),
         text(96, 28, "a copy is taken and kept", 13.5, "svg-q", "start"),
         f'<path d="M90 44 C160 46 196 62 234 84" stroke="{QUIET}" stroke-width="2" stroke-dasharray="2 6"/>',
         # later: two locks, the old one opened, the new one holding
         box(262, 96, ACC, SOFT),
         lock(250, 98, 0.85, QUIET, None, True), lock(274, 98, 0.85, ACC),
         text(262, 132, "one lock still holds", 13.5),
         text(180, 204, "Two locks together: an old kind and a new kind.", 13.5)]
    return svg(218, "A line from today to years later. Today a locked box is copied and the copy is kept. Years later one of its two locks has been opened and the second lock still holds.", o)


def decoys():
    def door(x, dotted=False):
        d = ' stroke-dasharray="3 5"' if dotted else ""
        col = ACC if dotted else INK
        return (f'<rect x="{x - 19}" y="76" width="38" height="74" rx="3" fill="{SOFT if dotted else PANEL}" stroke="{col}" stroke-width="2.4"{d}/>'
                f'<circle cx="{x + 10}" cy="116" r="2.6" fill="{col}" stroke="none"/>')
    o = [f'<path d="M18 150 H342 M18 58 H342" stroke="{RULE}" stroke-width="2.4"/>',
         door(66), door(160), door(262, True),
         # the bell over the decoy
         f'<path d="M250 44 a12 12 0 0 1 24 0 v8 l5 6 h-34 l5 -6 z" fill="{ACC}" stroke="{ACC}" stroke-width="2"/>',
         f'<circle cx="262" cy="62" r="2.6" fill="{ACC}" stroke="none"/>',
         f'<path d="M240 34 q-7 10 0 22 M284 34 q7 10 0 22 M232 28 q-11 16 0 34 M292 28 q11 16 0 34" stroke="{ACC}" stroke-width="2"/>',
         person(304, 150, QUIET, 0.95),
         text(113, 176, "real doors", 13.5), text(262, 176, "a door to nowhere", 13.5)]
    return svg(192, "A wall with three doors. Two are real. The third is a decoy that leads nowhere, and a bell rings above it when a stranger tries it.", o)


def rebuild():
    o = [ground(126),
         house(60, 126, 62, 44, door=False),
         f'<path d="M52 98 q2 -10 10 -8 q9 3 0 12 v4 M62 114 v1" stroke="{INK}" stroke-width="2.6"/>',
         arrow(102, 96, 138, 96),
         house(180, 126, 62, 44, dotted=True),
         arrow(222, 96, 258, 96, ACC),
         house(300, 126, 62, 44, ours=True, lit=True), tick(328, 62, 11),
         text(60, 150, "in doubt", 13.5), text(180, 150, "taken down", 13.5), text(300, 150, "built again", 13.5),
         text(180, 180, "The same written plan builds it each time.", 13.5)]
    return svg(194, "Three steps. A house that is in doubt. The same house taken down, shown as a dotted outline. The house built again from its plan, with a check mark.", o)


def alone():
    o = [f'<path d="M87 140 C110 128 132 120 153 114" stroke="{LINE}" stroke-width="2.6"/>',
         f'<path d="M207 114 L228 122 M252 131 L275 140" stroke="{LINE}" stroke-width="2.6"/>',
         f'<path d="M232 114 l4 20 M244 118 l4 20" stroke="{INK}" stroke-width="2.6"/>',
         house(60, 158, 54, 40, ours=True, lit=True), house(180, 124, 54, 40, ours=True, lit=True),
         house(302, 158, 54, 40, ours=True, lit=True),
         f'<path d="M318 96 l4 -9 M302 92 v-10 M286 96 l-4 -9" stroke="{ACC}" stroke-width="2.2"/>',
         text(120, 190, "still connected", 13.5), text(296, 190, "cut off, lights on", 13.5)]
    return svg(206, "Three houses. Two are still connected. The line to the third is cut, and its lights are still on.", o)


def open_():
    o = [page(98, 92, 96, 118, INK, 0),
         f'<path d="M66 60 h64 M66 76 h64 M66 92 h44 M66 108 h64 M66 124 h52" stroke="{QUIET}" stroke-width="2"/>',
         f'<circle cx="150" cy="118" r="26" fill="{PANEL}" fill-opacity="0.55" stroke="{ACC}" stroke-width="3"/>',
         f'<path d="M169 137 l20 20" stroke="{ACC}" stroke-width="5"/>',
         text(98, 176, "the design: public", 13.5, "svg-t", "middle", True),
         f'<rect x="232" y="62" width="86" height="60" rx="8" fill="{SOFT}" stroke="{ACC}" stroke-width="2.4"/>',
         key(256, 92, 1.1), lock(318, 62, 1.0, ACC, PANEL),
         text(275, 176, "the keys: secret", 13.5, "svg-t", "middle", True)]
    return svg(194, "On the left, a document under a magnifying glass: the design is public. On the right, a key kept in a locked box: the keys are secret.", o)
