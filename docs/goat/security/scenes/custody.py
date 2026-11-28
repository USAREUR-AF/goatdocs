"""Scene: the whole environment runs on hardware its owner controls and keeps custody of; a cloud holds
relays only. Grades: in use (goatcore decision record 1192: "No host site has a public address"; the
relays pass encrypted connections and are not peers of the mesh)."""
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, ONACC, RULE, LINE, mark as _mark, scene

ALT = ("Two sites drawn as solid plates, each holding four things: services, identity, keys and data. This is the "
       "owner's hardware, and everything lives there. Above them a thin band is a cloud, and it holds one thing: "
       "a relay. A sealed connection between the two sites passes through the relay without being opened. Beside "
       "the relay two short lists say what it can see, which is sealed traffic, two addresses, and how much and "
       "when, and what it cannot see, which is contents, keys, identities and data. A second relay is drawn "
       "faintly: any relay can be replaced with no loss.")


def _glyph(f, kind, x, y):
    s = f'fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "services":
        f.raw(f'<g {s}><rect x="{x - 14}" y="{y - 13}" width="28" height="10" rx="2"/><rect x="{x - 14}" y="{y + 3}" width="28" height="10" rx="2"/></g>'
              f'<circle cx="{x - 8}" cy="{y - 8}" r="1.8" fill="{INK}"/><circle cx="{x - 8}" cy="{y + 8}" r="1.8" fill="{INK}"/>')
    elif kind == "identity":
        f.raw(f'<g {s}><circle cx="{x}" cy="{y - 7}" r="6.5"/><path d="M{x - 13} {y + 14} a13 11 0 0 1 26 0"/></g>')
    elif kind == "keys":
        f.raw(f'<g {s}><circle cx="{x - 9}" cy="{y}" r="6.5"/><path d="M{x - 2.5} {y}H{x + 15}M{x + 9} {y}v6M{x + 14} {y}v5"/></g>')
    else:
        f.raw(f'<g {s}><ellipse cx="{x}" cy="{y - 10}" rx="13" ry="5"/><path d="M{x - 13} {y - 10}v20a13 5 0 0 0 26 0v-20"/><path d="M{x - 13} {y}a13 5 0 0 0 26 0"/></g>')


def _site(f, x, y, w, h, label, tw, th, small=False):
    f.rect(x, y, w, h, 14, SOFT, INK, 3)
    f.t(x + 18, y + 28, label, 13 if small else 14, 700, INK, ls="1.5")
    cols = 1 if small else 2
    rows = 4 // cols
    gx = (w - cols * tw) / (cols + 1)
    gy = (h - 44 - rows * th) / (rows + 1)
    for k, name in enumerate(("services", "identity", "keys", "data")):
        tx = x + gx + (k % cols) * (tw + gx)
        ty = y + 44 + gy + (k // cols) * (th + gy) - gy / 2
        f.rect(tx, ty, tw, th, 8, PAPER, INK, 1.8)
        _glyph(f, name, tx + (26 if not small else 22), ty + th / 2)
        f.t(tx + (52 if not small else 44), ty + th / 2 + 5.5, name, 16 if not small else 14, 600)


def _relay(f, x, y, r=26, faint=False):
    f.circle(x, y, r, fill=PAPER, stroke=INK, sw=2.6, dash="4 4" if faint else None)
    if not faint:
        f.raw(f'<path d="M{x - r + 7} {y} H{x + r - 7}" stroke="{ACC}" stroke-width="5" stroke-linecap="round"/>')


def _lists(f, x1, x2, y, size=15):
    f.t(x1, y, "A relay can see", size, 700)
    f.lines(x1, y + size * 1.6, ["sealed traffic", "two addresses", "how much, and when"], size, fill=QUIET)
    f.t(x2, y, "A relay cannot see", size, 700)
    f.lines(x2, y + size * 1.6, ["contents", "keys", "identities", "data"], size, fill=QUIET)


def figure_wide():
    f = Fig(1120, 610, ALT, uid="cu")
    # the cloud: a thin band, relays only
    f.rect(20, 18, 1080, 176, 12, "none", LINE, 1.8, dash="6 6")
    f.t(40, 46, "A CLOUD: RELAYS ONLY", 14, 700, QUIET, ls="1.5")
    _lists(f, 96, 800, 84)
    rx, ry = 560, 104
    # the sealed connection: up from one site, through the relay, down to the other
    f.path(f"M300 262 C300 150 430 {ry} {rx - 26} {ry}", stroke=ACC, sw=5)
    f.path(f"M{rx + 26} {ry} C690 {ry} 820 150 820 262", stroke=ACC, sw=5)
    _relay(f, rx, ry)
    f.lock(rx, ry, 0.82, ACC)
    f.t(rx, ry + 50, "passes it through, closed", 14, 400, QUIET, anchor="middle", italic=True)
    _relay(f, rx + 104, ry - 34, 17, faint=True)
    f.t(rx + 128, ry - 60, "a spare: any relay can be replaced", 13.5, 400, QUIET)
    # the owner's hardware
    _site(f, 40, 262, 460, 250, "A SITE", 196, 74)
    _site(f, 620, 262, 460, 250, "ANOTHER SITE", 196, 74)
    f.t(560, 540, "YOUR HARDWARE, IN YOUR CUSTODY: EVERYTHING LIVES HERE", 14, 700, INK, anchor="middle", ls="1.5")
    f.lock(300, 262, 1.0, ACC); f.lock(820, 262, 1.0, ACC)
    # the direct line between the two sites
    f.path("M500 400 H620", stroke=ACC, sw=5)
    f.lock(560, 400, 0.9, ACC)
    f.t(560, 368, "directly,", 13.5, 400, QUIET, anchor="middle")
    f.t(560, 446, "when they can", 13.5, 400, QUIET, anchor="middle")
    f.t(560, 464, "reach each other", 13.5, 400, QUIET, anchor="middle")
    f.t(40, 576, "The two ends hold the keys. A relay holds no key, stores nothing, and cannot read or change what it carries.", 16, 400, QUIET)
    f.t(40, 600, "Losing a relay loses no data and no identity.", 16, 400, QUIET)
    return f.svg()


def figure_narrow():
    f = Fig(464, 800, ALT, narrow=True, uid="cun")
    f.rect(8, 10, 448, 176, 12, "none", LINE, 1.8, dash="6 6")
    f.t(24, 38, "A CLOUD: RELAYS ONLY", 13, 700, QUIET, ls="1.4")
    rx, ry = 232, 96
    f.path(f"M118 252 C118 150 150 {ry} {rx - 26} {ry}", stroke=ACC, sw=5)
    f.path(f"M{rx + 26} {ry} C314 {ry} 346 150 346 252", stroke=ACC, sw=5)
    _relay(f, rx, ry); f.lock(rx, ry, 0.82, ACC)
    f.t(rx, ry + 52, "passes it through, closed", 14, 400, QUIET, anchor="middle", italic=True)
    _site(f, 8, 252, 220, 286, "A SITE", 184, 50, small=True)
    _site(f, 236, 252, 220, 286, "ANOTHER SITE", 184, 50, small=True)
    f.lock(118, 252, 1.0, ACC); f.lock(346, 252, 1.0, ACC)
    f.t(232, 566, "YOUR HARDWARE, IN YOUR CUSTODY", 13, 700, INK, anchor="middle", ls="1.4")
    f.t(232, 585, "EVERYTHING LIVES HERE", 13, 700, INK, anchor="middle", ls="1.4")
    _lists(f, 24, 250, 624, 15)
    f.lines(14, 744, ["The two ends hold the keys. A relay holds no key,", "stores nothing, and cannot read or change what it", "carries. Losing a relay loses no data and no identity."], 15, fill=QUIET)
    return f.svg()


def mark():
    """A box held in a cradle: the thing itself, in its owner's hands."""
    return _mark("custody", "A box resting in a cradle, held from below.",
                 '<path d="M10 40V64Q10 86 32 86H64Q86 86 86 64V40" class="mk"/>'
                 '<rect x="28" y="22" width="40" height="40" rx="6" class="mkf"/>'
                 '<circle cx="48" cy="42" r="6" class="mkfa"/>')


def html():
    return scene(
        "custody", "Custody", "Your hardware, in your custody",
        "data sovereignty, on-premises, positive control",
        "Services, identity, keys and data are placed in a provider's cloud.",
        "Everything runs on hardware you control and keep. A cloud holds only relays, which carry sealed traffic they cannot read.",
        "Nothing you need to protect is ever in someone else's building.",
        [("in use", "every site on its owner's hardware; relays as the only thing in a cloud")],
        figure_wide() + "\n" + figure_narrow(), mark())


def notes():
    return """<section id="custody"><h2>Why a relay in a cloud is safe</h2>
<p>A relay passes connections that are encrypted from end to end by the two parties that hold the keys. It holds no key, it cannot read or change what it carries, and it stores nothing.</p>
<p>A relay can be replaced or moved at any time. Losing one loses no data and no identity.</p>
</section>"""
