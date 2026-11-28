#!/usr/bin/env python3
"""Figures for goatdocs goat/security/: fixed-layout SVG, page CSS classes only.

Every figure is 480 units wide, so its text stays readable in a 390 px window, and is
drawn from fixed coordinates: no automatic layout. Colors come from the page's classes,
so each figure follows the light and the dark scheme. State is shown by line pattern
(solid: in use; dashed: designed, or closed to an intruder), never by a warning color.

    join_svg()       joining, once, through the only public name
    after_svg()      after joining: direct connections, and nothing public
    identity_svg()   zero trust: one request and the four checks it must pass
    readers_svg()    who can read a secret and a shared message
    chain_svg()      from a commit to a running machine, and what a deploy checks
    quantum_svg()    traffic recorded today and opened later: one key exchange against two
    decoy_svg()      a decoy, and what its first use starts
    rebuild_svg()    the cycle from a declaration to a running site and back
    silent_svg()     a packet from a stranger gets no answer
    island_svg()     a site with its link cut, everything running inside it
    hub_svg()        the hub severs a site; the site works alone and rejoins by being built again
    site_svg()       the first screen: a whole site, one part for each stage of the build
"""
import html

W = 480


def esc(s):
    return html.escape(s, quote=True)


class Fig:
    def __init__(self):
        self.out = []

    def rect(self, x, y, w, h, cls="bx", rx=8):
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')

    def text(self, x, y, s, cls="t", size=15, bold=False, anchor=None, halo=False):
        a = f' text-anchor="{anchor}"' if anchor else ""
        b = ' font-weight="700"' if bold else ""
        c = cls + (" halo" if halo else "")
        d = ' data-lint="halo"' if halo else ""
        self.out.append(f'<text x="{x}" y="{y}"{a} class="{c}" font-size="{size}"{b}{d}>{esc(s)}</text>')

    def lines(self, x, y, rows, cls="tq", size=14, gap=18, anchor=None):
        for i, s in enumerate(rows):
            self.text(x, y + i * gap, s, cls, size, False, anchor)

    def path(self, d, cls="ln", extra=""):
        self.out.append(f'<path d="{d}" class="{cls}"{extra}/>')

    def line(self, pts, cls="ln", extra=""):
        self.path("M" + "L".join(f"{x} {y}" for x, y in pts), cls, extra)

    def arrow(self, pts, cls="ln", head="fl"):
        """A line with a filled head at its last point."""
        self.line(pts, cls)
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        dx, dy = x1 - x0, y1 - y0
        n = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / n, dy / n
        px, py = -uy, ux
        a = (x1 - ux * 10 + px * 5, y1 - uy * 10 + py * 5)
        b = (x1 - ux * 10 - px * 5, y1 - uy * 10 - py * 5)
        self.out.append(f'<path d="M{x1} {y1}L{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}Z" class="{head}"/>')

    def box(self, x, y, w, h, title, sub=(), cls="bx", size=15, center=False):
        self.rect(x, y, w, h, cls)
        rows = [sub] if isinstance(sub, str) else list(sub)
        block = 18 + 18 * len(rows)
        ty = y + (h - block) / 2 + 15
        if center:
            self.text(x + w / 2, ty, title, "t", size, True, "middle")
            self.lines(x + w / 2, ty + 20, rows, "tq", 14, 18, "middle")
        else:
            self.text(x + 14, ty, title, "t", size, True)
            self.lines(x + 14, ty + 20, rows, "tq", 14, 18)

    def intruder(self, x, y, label=True):
        """The intruder: an open diamond. A shape, not a warning color."""
        self.out.append(f'<path d="M{x} {y - 13}L{x + 13} {y}L{x} {y + 13}L{x - 13} {y}Z" class="intr"/>')
        if label:
            self.text(x, y + 32, "intruder", "t", 14, True, "middle")

    def lock(self, x, y):
        """A small closed padlock, about 16 by 20, its top left corner at x, y."""
        self.out.append(f'<path d="M{x + 3.5} {y + 9}V{y + 6}a4.5 4.5 0 0 1 9 0V{y + 9}" class="lka" data-lint="nohead"/>')
        self.out.append(f'<rect x="{x}" y="{y + 9}" width="16" height="11" rx="2" class="fa"/>')

    def bell(self, x, y):
        self.out.append(f'<path d="M{x} {y + 14}h20l-3 -4v-5a7 7 0 0 0 -14 0v5z" class="fa"/>'
                        f'<circle cx="{x + 10}" cy="{y + 17.5}" r="2.4" class="fa"/>')

    def tick(self, x, y):
        self.out.append(f'<path d="M{x} {y + 6}l4.5 4.5l8 -9.5" class="lna" data-lint="nohead"/>')

    def bar(self, x, y, vertical=True, half=7):
        """A stop bar: where a line ends because the way is closed."""
        if vertical:
            self.line([(x, y - half), (x, y + half)], "stopbar", ' data-lint="nohead"')
        else:
            self.line([(x - half, y), (x + half, y)], "stopbar", ' data-lint="nohead"')

    def svg(self, id_, h, label):
        return (f'<svg id="{id_}" class="viz" viewBox="8 0 {W - 16} {h}" role="img" aria-label="{esc(label)}">\n'
                + "\n".join(self.out) + "\n</svg>")


def silent_svg():
    """A packet from a stranger gets no answer; a packet from a known machine does."""
    f = Fig()
    rows = [("a stranger", "a packet it cannot authenticate", "no answer", False),
            ("a known machine", "a packet it can authenticate", "the tunnel opens", True)]
    y = 16
    for who, what, result, ok in rows:
        f.box(16, y, 150, 62, who, cls="bx" if ok else "bxd", center=True)
        f.box(314, y, 150, 62, "a goat machine", cls="bxk", center=True)
        if ok:
            f.arrow([(166, y + 22), (312, y + 22)], "lna", "fa")
            f.arrow([(314, y + 42), (168, y + 42)], "lna", "fa")
        else:
            f.arrow([(166, y + 31), (312, y + 31)], "lnd", "fl")
        f.text(240, y + 86, what, "tq", 14, False, "middle")
        f.text(240, y + 106, result, "t", 15, True, "middle")
        y += 138
    return f.svg("fig-silent", y - 14,
                 "Two exchanges. A stranger sends a packet that the goat machine cannot authenticate, and gets no answer. "
                 "A known machine sends a packet that the goat machine can authenticate, and the tunnel opens.")


def _party(f, x, y, ring=True, cls="dot"):
    """A party: a filled center, and a ring for its own identity once it has one."""
    if ring:
        f.out.append(f'<circle cx="{x}" cy="{y}" r="15" class="idring"/>')
    f.out.append(f'<circle cx="{x}" cy="{y}" r="8.5" class="{cls}"/>')


def _lockat(f, x, y):
    f.out.append(f'<g transform="translate({x} {y})"><circle r="13" class="lockring"/>'
                 '<rect x="-5.5" y="-2" width="11" height="8.5" rx="2" class="fa"/>'
                 '<path d="M-3.4 -2v-2.8a3.4 3.4 0 0 1 6.8 0v2.8" class="lka" data-lint="nohead"/></g>')


def _num(f, x, y, n):
    f.out.append(f'<circle cx="{x}" cy="{y}" r="11" class="fa"/>')
    f.text(x, y + 5, str(n), "ton", 14, True, "middle")


def join_svg():
    """Joining, once: a new device, the one public name, a relay that passes it through, the service that admits it."""
    f = Fig()
    # the site: the admitting service has no address of its own
    f.rect(338, 30, 126, 124, "bxd", 14)
    f.text(401, 52, "a site", "tq", 14, False, "middle")
    _party(f, 401, 92)
    f.lines(401, 126, ["admits it;", "no address"], "tq", 14, 17, "middle")
    # the public name
    f.rect(96, 72, 96, 40, "bxa", 20)
    f.text(144, 97, "public name", "t", 14, True, "middle")
    # the relay: a pass-through, not an end point
    f.line([(222, 78), (300, 78)], "ln", ' data-lint="nohead"')
    f.line([(222, 106), (300, 106)], "ln", ' data-lint="nohead"')
    f.text(261, 130, "relay", "t", 14, True, "middle")
    # the device and the one connection, through everything
    _party(f, 40, 92, ring=False, cls="arrival")
    f.text(40, 130, "new device", "t", 14, True, "middle")
    f.line([(52, 92), (96, 92)], "link", ' data-lint="nohead"')
    f.arrow([(192, 92), (384, 92)], "link", "fa")
    _lockat(f, 261, 92)
    _num(f, 74, 66, 1)
    _num(f, 261, 54, 2)
    _num(f, 320, 66, 3)
    # what comes back
    f.path("M388 100Q220 196 56 106", "lna", ' data-lint="nohead"')
    f.arrow([(64, 112), (52, 104)], "lna", "fa")
    _num(f, 220, 166, 4)
    steps = ["A new device contacts the goatnet's one public name.",
             "A relay passes the encrypted connection through, unread.",
             "The device presents a key that works once.",
             "It gets its identity, and the list of parties it may reach."]
    y = 216
    for i, t in enumerate(steps):
        _num(f, 28, y + i * 30, i + 1)
        f.text(48, y + 5 + i * 30, t, "t", 14)
    return f.svg("fig-join", y + 4 * 30 - 4,
                 "Joining, in four steps. One: a new device contacts the goatnet's one public name. Two: a relay behind "
                 "that name passes the encrypted connection through, and cannot read it. Three: the device presents a key "
                 "that works once to the service that admits it, which is inside a site and has no address of its own. "
                 "Four: the device gets its identity on the mesh, and the list of parties it may reach.")


def after_svg():
    """After joining: direct encrypted connections, a relay only as a fallback, and nothing public."""
    f = Fig()
    pts = {"you": (70, 96), "b": (214, 50), "c": (392, 84), "d": (150, 206), "e": (330, 212)}
    for a, b in (("you", "b"), ("you", "d"), ("b", "c"), ("d", "e")):
        (x1, y1), (x2, y2) = pts[a], pts[b]
        f.line([(x1, y1), (x2, y2)], "link", ' data-lint="nohead"')
        _lockat(f, (x1 + x2) / 2, (y1 + y2) / 2)
    # two devices that cannot reach each other directly: through a relay, unread
    f.line([pts["c"], (372, 132)], "linkd", ' data-lint="nohead"')
    f.line([(350, 164), pts["e"]], "linkd", ' data-lint="nohead"')
    f.out.append('<g transform="rotate(-66 361 148)"><path d="M341 138h40M341 158h40" class="ln" data-lint="nohead"/></g>')
    f.text(398, 152, "relay,", "t", 14, True)
    f.text(398, 170, "if needed", "tq", 14)
    for k, (x, y) in pts.items():
        _party(f, x, y)
    f.text(70, 66, "your device", "t", 14, True, "middle")
    # services, by names that exist only inside
    f.box(16, 250, 250, 56, "services", ["names known only inside"], cls="bx")
    f.line([(150, 222), (150, 250)], "link", ' data-lint="nohead"')
    # the service that admitted the device is not in the path
    f.rect(290, 250, 174, 56, "bxd", 8)
    f.text(377, 274, "admitting service", "tq", 14, False, "middle")
    f.text(377, 293, "not in the path", "tq", 14, False, "middle")
    # the view from the internet
    f.rect(16, 332, 448, 66, "bxp", 8)
    f.out.append('<circle cx="46" cy="365" r="16" class="bx"/><path d="M35 365q11 -10 22 0q-11 10 -22 0z" class="ln" data-lint="nohead"/><circle cx="46" cy="365" r="3.2" class="fl"/>')
    f.text(74, 359, "From the internet: encrypted packets", "t", 14, True)
    f.text(74, 379, "between addresses. Nothing answers a probe.", "tq", 14)
    return f.svg("fig-after", 414,
                 "After joining. Your device has direct encrypted connections to other devices, each connection with its "
                 "own lock. Two devices that cannot reach each other directly are joined through a relay, which carries "
                 "encrypted traffic it cannot read. Services are reached by names known only inside the mesh. The service "
                 "that admitted the device is not in the path. From the internet, an observer sees encrypted packets "
                 "between addresses, and nothing answers a probe.")


def identity_svg():
    """Zero trust: one request, and the four checks it must pass."""
    f = Fig()
    kinds = [("a person", "signs in"), ("a machine", "its own key"), ("a workload", "a certificate")]
    for i, (t, sub) in enumerate(kinds):
        x = 16 + i * 152
        f.box(x, 16, 144, 58, t, [sub], center=True)
        f.line([(x + 72, 74), (x + 72, 92)], "ln", ' data-lint="nohead"')
    f.line([(88, 92), (392, 92)], "ln", ' data-lint="nohead"')
    f.arrow([(240, 92), (240, 112)], "ln")
    gates = [("1", "Who is asking?", "the identity is proven, each kind its own way"),
             ("2", "Is there a declared rule?", "no rule, no connection; position grants nothing"),
             ("3", "May this role do this?", "a declared table of roles, enforced"),
             ("4", "Still in good standing?", "not revoked, not held for review")]
    y = 114
    for n, q, sub in gates:
        f.rect(16, y, 448, 62, "bxa", 8)
        f.out.append(f'<circle cx="44" cy="{y + 31}" r="14" class="fa"/>')
        f.text(44, y + 36, n, "ton", 15, True, "middle")
        f.text(70, y + 27, q, "t", 15, True)
        f.text(70, y + 46, sub, "tq", 14)
        if n != "4":
            f.arrow([(240, y + 62), (240, y + 76)], "lna", "fa")
        y += 78
    f.arrow([(240, y - 16), (240, y + 2)], "lna", "fa")
    f.box(16, y + 4, 448, 46, "the service", cls="bxk", center=True)
    f.lines(240, y + 80, ["A request that fails one check stops there.",
                          "Rules 2 and 3 are generated from a reviewed declaration."], "tq", 14, 19, "middle")
    return f.svg("fig-identity", y + 112,
                 "A request from a person, a machine or a workload passes four checks before it reaches a service. One: who "
                 "is asking; the identity is proven, each kind in its own way. Two: is there a declared rule; with no rule "
                 "there is no connection, and a position on the network grants nothing. Three: may this role do this; a "
                 "declared table of roles is enforced. Four: is the identity still in good standing, meaning not revoked "
                 "and not held for review. A request that fails one check stops there.")


def readers_svg():
    f = Fig()
    f.text(16, 24, "A secret", "t", 16, True)
    f.box(16, 36, 186, 70, "your device", ["encrypts it first"])
    f.box(278, 36, 186, 70, "the secret store", ["holds it, cannot read it"], cls="bxp")
    f.arrow([(202, 80), (276, 80)], "lna", "fa")
    f.lock(231, 50)
    f.text(16, 162, "A shared message", "t", 16, True)
    f.box(16, 174, 132, 70, "the sender", ["seals it"])
    f.box(174, 174, 132, 70, "the fabric", ["carries it"], cls="bxp")
    f.box(332, 174, 132, 70, "the reader", ["named, opens it"])
    f.arrow([(148, 222), (172, 222)], "lna", "fa")
    f.arrow([(306, 222), (330, 222)], "lna", "fa")
    f.lock(153, 190)
    f.lock(311, 190)
    f.lines(240, 276, ["The fabric holds no key and has no central broker:", "machines pass the sealed message on."], "tq", 14, 19, "middle")
    return f.svg("fig-readers", 312,
                 "A secret is encrypted on your device before it reaches the secret store, which holds it and cannot read "
                 "it. A shared message is sealed by the sender, carried by the data fabric, and opened only by a named "
                 "reader. The fabric holds no key and has no central broker: machines pass the sealed message on.")


def chain_svg():
    f = Fig()
    steps = [("a commit", "signed by its author"), ("the release list", "signed: which release runs where"),
             ("an image", "named by its content hash")]
    y = 16
    for t, s in steps:
        f.box(16, y, 448, 58, t, [s])
        f.arrow([(240, y + 58), (240, y + 78)], "ln")
        y += 80
    f.rect(16, y, 448, 150, "bxa", 8)
    f.text(30, y + 26, "a deploy checks, before it changes a machine", "t", 15, True)
    checks = ["the signature on the release list", "the content hash of every image",
              "the source matches the repository", "the earlier stage runs this release"]
    for i, c in enumerate(checks):
        f.tick(32, y + 42 + i * 26)
        f.text(56, y + 54 + i * 26, c, "t", 14.5)
    f.arrow([(240, y + 150), (240, y + 170)], "lna", "fa")
    f.box(16, y + 172, 448, 46, "the machine", cls="bxk", center=True)
    f.text(240, y + 246, "One check fails: the deploy refuses, and nothing changes.", "tq", 14, False, "middle")
    return f.svg("fig-chain", y + 262,
                 "The chain from a commit to a running machine. A commit is signed by its author. The release list, which "
                 "says which release runs where, is signed. An image is named by its content hash. Before a deploy changes "
                 "a machine it checks the signature on the release list, the content hash of every image, that the source "
                 "matches the repository, and that the earlier stage runs this release. If one check fails, the deploy "
                 "refuses and nothing changes.")


def quantum_svg():
    """Recorded today, opened later: one key exchange against two."""
    f = Fig()
    f.text(16, 24, "Today", "t", 16, True)
    f.box(16, 36, 160, 62, "two machines", ["agree on a key"], center=True)
    f.box(304, 36, 160, 62, "a recorder", ["keeps the traffic"], cls="bxd", center=True)
    f.arrow([(176, 67), (302, 67)], "ln")
    f.text(16, 150, "Years later, with a quantum computer", "t", 16, True)
    rows = [("one key exchange", ["of the usual kind"], "the recording opens", "bx", False),
            ("two key exchanges", ["the usual kind, and one built", "to resist that computer"],
             "the recording stays closed", "bxa", True)]
    y = 162
    for t, sub, result, cls, closed in rows:
        f.box(16, y, 250, 76, t, sub, cls=cls)
        f.arrow([(266, y + 38), (296, y + 38)], "lna" if closed else "ln", "fa" if closed else "fl")
        if closed:
            f.lock(306, y + 28)
        else:
            f.out.append(f'<path d="M309.5 {y + 37}V{y + 33}a4.5 4.5 0 0 1 9 0" class="ln" data-lint="nohead"/>'
                         f'<rect x="306" y="{y + 37}" width="16" height="11" rx="2" class="fl"/>')
        words = result.split(" ", 2)
        f.lines(332, y + 34, [" ".join(words[:2]), words[2]], "t", 14, 18)
        y += 92
    f.text(240, y + 18, "Both must be broken to read the traffic.", "tq", 14, False, "middle")
    return f.svg("fig-quantum", y + 36,
                 "Today two machines agree on a key, and a recorder keeps the encrypted traffic. Years later, with a quantum "
                 "computer, a recording protected by one key exchange of the usual kind opens. A recording protected by two "
                 "key exchanges, the usual kind and one built to resist that computer, stays closed, because both must be "
                 "broken to read the traffic.")


def decoy_svg():
    f = Fig()
    f.text(16, 24, "What a site offers", "t", 16, True)
    for i, n in enumerate(["a real name", "a real web path", "a real service"]):
        f.rect(16 + i * 152, 36, 144, 40, "bx", 6)
        f.text(88 + i * 152, 61, n, "tq", 14, False, "middle")
    f.rect(16, 104, 200, 62, "bxd", 6)
    f.text(116, 130, "a decoy", "t", 15, True, "middle")
    f.text(116, 150, "nothing uses it", "tq", 14, False, "middle")
    f.intruder(116, 222)
    f.arrow([(116, 208), (116, 168)], "lna", "fa")
    f.arrow([(216, 135), (286, 135)], "lna", "fa")
    f.rect(288, 100, 176, 70, "bxa")
    f.bell(304, 124)
    f.text(338, 130, "an alert", "t", 15, True)
    f.text(338, 150, "on the first use", "tq", 14)
    f.arrow([(376, 170), (376, 206)], "lna", "fa")
    f.box(288, 208, 176, 52, "the operator on call", cls="bxk", center=True)
    return f.svg("fig-decoy", 276,
                 "A site offers real names, real web paths and real services, and also a decoy that nothing has a reason "
                 "to use. When an intruder uses the decoy, the first use raises an alert, and the alert reaches the "
                 "operator on call.")


def rebuild_svg(build="38 min 12 s", down="5 min 54 s"):
    """The cycle: a declaration becomes a running site, and the site is taken down again."""
    f = Fig()
    f.box(16, 118, 150, 76, "a declaration", ["in a repository"], cls="bxa", center=True)
    f.box(314, 118, 150, 76, "a running site", ["checked, in use"], cls="bxk", center=True)
    f.path("M91 116Q240 6 383 110", "lna", ' data-lint="nohead"')
    f.arrow([(377, 104), (389, 116)], "lna", "fa")
    f.path("M389 196Q240 306 97 202", "lna", ' data-lint="nohead"')
    f.arrow([(103, 208), (91, 196)], "lna", "fa")
    f.text(240, 40, "build", "t", 15, True, "middle", True)
    f.text(240, 60, build, "ta", 17, True, "middle", True)
    f.text(240, 254, "take down", "t", 15, True, "middle", True)
    f.text(240, 274, down, "ta", 17, True, "middle", True)
    f.text(240, 152, "one command", "tq", 14, False, "middle")
    f.text(240, 170, "each way", "tq", 14, False, "middle")
    f.lines(240, 316, ["Every rebuild returns every machine to a known clean state."], "tq", 14, 19, "middle")
    return f.svg("fig-rebuild", 334,
                 f"A cycle. A declaration in a repository is built into a running site by one command; the build is {build} of "
                 f"machine time. One command takes the site down again in {down}. Every rebuild returns every machine to a "
                 "known clean state.")


def island_svg():
    """One site with its link cut: everything it needs is running inside it, and nothing leaves it."""
    f = Fig()
    f.box(16, 16, 150, 56, "the other sites", cls="bx", center=True)
    f.line([(166, 44), (214, 44)], "ln", ' data-lint="nohead"')
    f.bar(214, 44, half=10)
    f.bar(246, 44, half=10)
    f.line([(246, 44), (300, 44), (300, 104)], "ln", ' data-lint="nohead"')
    f.text(230, 26, "cut", "t", 14, True, "middle")
    f.rect(16, 106, 448, 164, "area", 16)
    f.text(32, 132, "a site, by itself", "t", 16, True)
    for i, name in enumerate(["sign-in", "the mesh", "data", "access changes"]):
        x = 32 + (i % 2) * 212
        y = 148 + (i // 2) * 54
        f.rect(x, y, 204, 42, "bx", 6)
        f.tick(x + 14, y + 13)
        f.text(x + 44, y + 27, name, "t", 14.5)
    f.text(240, 296, "Nothing has to leave the site for it to keep working.", "tq", 14, False, "middle")
    return f.svg("fig-island", 312,
                 "A site whose link to the other sites is cut. Inside the site, sign-in, the mesh, data and access "
                 "changes all keep running. Nothing has to leave the site for it to keep working.")


def hub_svg():
    """The hub severs a site. The site keeps working alone, and rejoins only after it is built again."""
    f = Fig()
    f.box(152, 16, 176, 56, "the hub", ["the site with authority"], cls="bxa", center=True)
    f.line([(240, 72), (240, 104)], "ln", ' data-lint="nohead"')
    f.line([(96, 104), (384, 104)], "ln", ' data-lint="nohead"')
    f.line([(96, 104), (96, 150)], "ln", ' data-lint="nohead"')
    f.box(16, 152, 160, 76, "a site", ["in the goatnet"], center=True)
    f.line([(384, 104), (384, 122)], "ln", ' data-lint="nohead"')
    f.bar(384, 122, vertical=False, half=11)
    f.text(398, 127, "ended", "t", 14, True)
    f.rect(304, 152, 160, 76, "bxk", 8)
    f.tick(318, 166)
    f.text(342, 180, "a severed site", "t", 15, True)
    f.text(384, 204, "still works, alone", "tq", 14, False, "middle")
    f.path("M384 230Q384 286 250 286", "lna", ' data-lint="nohead"')
    f.arrow([(262, 286), (198, 286)], "lna", "fa")
    f.text(330, 312, "to rejoin", "t", 14, True, "middle")
    f.box(16, 258, 180, 56, "built again", ["and loaded from the hub"], cls="bxa", center=True)
    f.arrow([(96, 258), (96, 230)], "lna", "fa")
    return f.svg("fig-hub", 330,
                 "The hub, the site with authority, severs a site. The link between the severed site and the others is "
                 "ended, and nothing the severed site writes afterward reaches another site. The severed site still works, "
                 "alone, for the people there. To rejoin, it is built again and loaded from the hub.")


def site_svg(label):
    """A whole site, drawn so that each stage of the build adds its part (groups carry data-stage)."""
    f = Fig()

    def stage(n, draw):
        f.out.append(f'<g class="st" data-stage="{n}">')
        draw()
        f.out.append("</g>")

    def chip(x, y, name):
        f.rect(x, y, 112, 30, "bxa", 5)
        f.text(x + 56, y + 20, name, "t", 14, False, "middle")

    def machines():
        f.rect(30, 108, 252, 170, "bx", 8)
        f.text(44, 128, "core machine", "t", 14, True)
        f.lock(256, 112)
        for y in (108, 162):
            f.rect(298, y, 152, 46, "bx", 8)
            f.text(312, y + 28, "monitoring", "t", 14, True)
            f.lock(424, y + 13)

    def site():
        f.rect(16, 74, 448, 216, "edge2", 14)
        f.text(30, 96, "the site", "tq", 14)

    def relays():
        f.rect(150, 8, 180, 40, "bxa", 8)
        f.text(240, 33, "relays in a cloud", "t", 14, True, "middle")
        f.line([(240, 48), (240, 74)], "lna", ' data-lint="nohead"')

    def mesh():
        f.line([(282, 131), (298, 131)], "lna", ' data-lint="nohead"')
        f.line([(282, 185), (298, 185)], "lna", ' data-lint="nohead"')
        f.line([(374, 154), (374, 162)], "lna", ' data-lint="nohead"')

    def admin():
        f.rect(298, 222, 152, 56, "bxk", 8)
        f.out.append('<circle cx="318" cy="242" r="5" class="fa"/><path d="M308 260a10 9 0 0 1 20 0z" class="fa"/>')
        f.text(336, 246, "administrator", "t", 14, True)
        f.text(336, 264, "signed in", "tq", 14)

    def late():
        chip(42, 238, "access rules")
        chip(160, 238, "portal")
        f.rect(350, 8, 114, 40, "bx", 8)
        f.text(407, 33, "alarm, off-site", "t", 14, False, "middle")

    def checked():
        f.out.append('<circle cx="440" cy="92" r="13" class="fa"/><path d="M433.5 92l4.5 4.5l8 -9" class="lnon" data-lint="nohead"/>')
        f.text(420, 97, "checked", "t", 14, True, "end")

    stage(1, site)
    stage(2, machines)
    stage(3, lambda: chip(160, 136, "certificates"))
    stage(4, lambda: chip(42, 136, "management"))
    stage(5, lambda: chip(42, 170, "sign-in"))
    stage(6, relays)
    stage(7, mesh)
    stage(8, lambda: (chip(160, 170, "data router"), chip(42, 204, "workloads")))
    stage(9, lambda: chip(160, 204, "dashboard"))
    stage(10, admin)
    stage(11, late)
    stage(12, checked)
    return f.svg("fig-site", 302, label or "A whole site: its machines, its services, its relays and its checks.")


# ---- the marks: one small drawing an idea, all on one 96-unit grid -----------------------------------
# Line weight 5, round ends, corners of radius 6; ink for what is there, map green for the idea,
# dashes for what is absent or hidden. Each reads at 64 px.

def _mark(name, label, body):
    return (f'<svg class="mark mark-{name}" viewBox="0 0 96 96" role="img" aria-label="{esc(label)}">'
            f'{body}</svg>')


def mark_outside():
    """A building with no door on the street; the way in runs under the ground."""
    return _mark("outside", "A building with no door on the street. The way in runs under the ground.",
                 '<path d="M8 58H88" class="mk"/>'
                 '<path d="M30 58V28L50 14L70 28V58" class="mk"/>'
                 '<path d="M8 80Q50 92 50 58" class="mka mkd"/>'
                 '<circle cx="50" cy="42" r="5" class="mkfa"/>')


def mark_zero_trust():
    """Two points and the line between them, stopped at a gate and asked."""
    return _mark("zero-trust", "A line between two points, stopped at a gate in the middle.",
                 '<circle cx="14" cy="48" r="7" class="mkf"/><circle cx="82" cy="48" r="7" class="mkf"/>'
                 '<path d="M23 48H36M60 48H73" class="mk"/>'
                 '<circle cx="48" cy="48" r="17" class="mka"/>'
                 '<path d="M48 39V57" class="mka"/>')


def mark_sealed():
    """A keeper holds a closed box. The key is somewhere else."""
    return _mark("sealed", "A closed box held on a tray. Its key is somewhere else.",
                 '<path d="M10 78H66M10 78V68M66 78V68" class="mk"/>'
                 '<rect x="18" y="36" width="40" height="34" rx="6" class="mkf"/>'
                 '<circle cx="38" cy="50" r="4.5" class="mkfi"/><path d="M38 54V61" class="mk"/>'
                 '<circle cx="76" cy="20" r="7" class="mka"/><path d="M76 27V46M76 38H84M76 46H82" class="mka"/>')


def mark_verified():
    """A stamp: checked before it runs."""
    return _mark("verified", "A stamp with a check mark.",
                 '<path d="M48 10L80 28V66L48 86L16 66V28Z" class="mkf"/>'
                 '<path d="M33 49L44 60L64 36" class="mka"/>')


def mark_quantum():
    """A padlock with two shackles: two key exchanges, and both must be broken."""
    return _mark("quantum", "A padlock with two shackles, one inside the other.",
                 '<path d="M24 46V34a24 24 0 0 1 48 0V46" class="mk"/>'
                 '<path d="M36 46V36a12 12 0 0 1 24 0V46" class="mka"/>'
                 '<rect x="16" y="46" width="64" height="40" rx="6" class="mkf"/>'
                 '<circle cx="48" cy="64" r="5" class="mkfi"/>')


def mark_decoy():
    """A door that stands alone, leads nowhere, and rings."""
    return _mark("decoy", "A door standing by itself, with nothing around it, and a bell that rings.",
                 '<path d="M6 84H90" class="mk mkd"/>'
                 '<rect x="26" y="20" width="34" height="64" rx="4" class="mkf"/>'
                 '<circle cx="51" cy="54" r="3.5" class="mkfi"/>'
                 '<path d="M72 34h16l-2.5 -3.5v-5a5.5 5.5 0 0 0 -11 0v5z" class="mkfa"/>'
                 '<path d="M68 16q-4 6 -1 12M92 16q4 6 1 12" class="mka mkt"/>')


def mark_rebuild():
    """What ended is drawn again, whole: a faint outline, the same shape solid, and the turn between them."""
    return _mark("rebuild", "A dashed outline of a shape, the same shape drawn solid again, and a turning arrow between them.",
                 '<rect x="10" y="50" width="30" height="30" rx="6" class="mk mkd"/>'
                 '<rect x="54" y="50" width="30" height="30" rx="6" class="mkf"/>'
                 '<path d="M25 40A24 24 0 0 1 66 30" class="mka"/>'
                 '<path d="M70 44L71 27L57 34Z" class="mkfa"/>')


def mark_island():
    """A site that stands by itself: the link out is cut, and the site is whole."""
    return _mark("island", "A site inside its own ring. The link that leaves it is cut.",
                 '<circle cx="40" cy="52" r="28" class="mka"/>'
                 '<rect x="27" y="39" width="26" height="26" rx="6" class="mkf"/>'
                 '<path d="M62 30L70 22M78 14L88 4" class="mk"/>')


def mark_silent():
    """A call that gets no answer."""
    return _mark("silent", "A signal sent toward a point, and no answer coming back.",
                 '<circle cx="74" cy="48" r="9" class="mkf"/>'
                 '<path d="M12 48H24" class="mk"/>'
                 '<path d="M34 30Q46 48 34 66" class="mk"/>'
                 '<path d="M48 22Q64 48 48 74" class="mk mkd"/>')


def mark_hub():
    """A hub and its links, one of them ended; the site at its end is still there."""
    return _mark("hub", "A hub with three links. One link is ended, and the site at its end is still there.",
                 '<circle cx="48" cy="26" r="12" class="mkf"/>'
                 '<path d="M38 36L20 62M48 38V62" class="mk"/>'
                 '<path d="M58 36L66 48" class="mk"/><path d="M58 54L74 44" class="mka"/>'
                 '<circle cx="18" cy="72" r="8" class="mkf"/><circle cx="48" cy="72" r="8" class="mkf"/>'
                 '<circle cx="78" cy="72" r="8" class="mkf"/>')


def mark_ordinary():
    """Three parts that are the same: any one can replace another."""
    return _mark("ordinary", "Three identical parts in a row. Any one can take the place of another.",
                 '<rect x="8" y="34" width="22" height="28" rx="6" class="mkf"/>'
                 '<rect x="37" y="34" width="22" height="28" rx="6" class="mkf"/>'
                 '<rect x="66" y="34" width="22" height="28" rx="6" class="mkf"/>'
                 '<path d="M20 20Q48 4 76 20" class="mka"/><path d="M80 24L80 12L68 16Z" class="mkfa"/>')


MARKS = {"MARK_OUTSIDE": mark_outside, "MARK_ZERO_TRUST": mark_zero_trust, "MARK_SEALED": mark_sealed,
         "MARK_VERIFIED": mark_verified, "MARK_QUANTUM": mark_quantum, "MARK_DECOY": mark_decoy,
         "MARK_REBUILD": mark_rebuild, "MARK_ISLAND": mark_island, "MARK_SILENT": mark_silent, "MARK_HUB": mark_hub, "MARK_ORDINARY": mark_ordinary}

FIGURES = {"FIG_SILENT": silent_svg, "FIG_JOIN": join_svg, "FIG_AFTER": after_svg, "FIG_IDENTITY": identity_svg,
           "FIG_READERS": readers_svg, "FIG_CHAIN": chain_svg, "FIG_QUANTUM": quantum_svg, "FIG_DECOY": decoy_svg, "FIG_REBUILD": rebuild_svg, "FIG_ISLAND": island_svg, "FIG_HUB": hub_svg}

if __name__ == "__main__":
    for name, fn in list(FIGURES.items()) + list(MARKS.items()):
        print(name, len(fn()))
