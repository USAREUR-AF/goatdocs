"""Scene: an air gap is one more boundary. One idea: the gap is a single line with trust inside it, and it is
crossed by hand; against no single line, with every connection sealed on its own.
Grades (goatcore main): a site running with no link: designed (decision record 1165; the tests for mesh control
and sign-in under a cut link are built); nothing reachable from the public internet: in use (record 1192);
signed, verified releases: in use; carrying releases to a cut-off site as one signed bundle: designed
(decision record 1277, accepted, not built). No public case is cited."""
import itertools, math
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, LINE, mark as _mark, scene

ALT = ("Two drawings. First, an island with water all round it. Inside the island every party is joined freely to "
       "every other. Three small boats cross the water toward it: a drive, a maintenance laptop and an update. "
       "Second, an open field with no water and no shore: each party has its own identity and each connection "
       "between two parties has its own lock.")


def _boat(f, x, y, ang):
    f.raw(f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang})" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
          f'<path d="M-18 3H18L11 14H-11Z" fill="{PAPER}"/><path d="M0 3V-18L12 -2H0"/></g>')


def _island(f, cx, cy, r, labels=True, small=False):
    for k, rr in enumerate((r + 58, r + 38, r + 18)):
        f.circle(cx, cy, rr, fill="none", stroke=LINE, sw=1.8, dash="10 7" if k % 2 == 0 else "4 9")
    f.circle(cx, cy, r, fill=SOFT, stroke=INK, sw=3)
    pts = [(cx + r * .55 * math.cos(math.radians(a)), cy + r * .55 * math.sin(math.radians(a))) for a in (-90, -18, 54, 126, 198)]
    for a, b in itertools.combinations(range(5), 2):
        f.path(f"M{pts[a][0]:.1f} {pts[a][1]:.1f} L{pts[b][0]:.1f} {pts[b][1]:.1f}", stroke=QUIET, sw=1.6)
    for x, y in pts:
        f.party(x, y, 7, ring=False)
    boats = [(205, "a drive"), (150, "a laptop"), (20, "an update")] if not small else [(215, "a drive"), (150, "a laptop"), (25, "an update")]
    for ang, lab in boats:
        a = math.radians(ang)
        bx, by = cx + (r + 38) * math.cos(a), cy + (r + 38) * math.sin(a)
        ox, oy = cx + (r + 96) * math.cos(a), cy + (r + 96) * math.sin(a)
        ix, iy = cx + (r + 6) * math.cos(a), cy + (r + 6) * math.sin(a)
        f.path(f"M{ox:.1f} {oy:.1f} L{bx:.1f} {by:.1f}", stroke=INK, sw=2, dash="2 6")
        f.path(f"M{bx:.1f} {by:.1f} L{ix:.1f} {iy:.1f}", stroke=INK, sw=2, dash="2 6", arrow=True)
        _boat(f, bx, by, 0)
        if labels:
            anchor = "end" if math.cos(a) < -0.3 else ("start" if math.cos(a) > 0.3 else "middle")
            f.t(ox + (-8 if anchor == "end" else 8 if anchor == "start" else 0), oy + (5 if anchor != "middle" else 18), lab, 14.5, 600, anchor=anchor)


def _field(f, pts, links):
    for a, b in links:
        f.path(f"M{pts[a][0]} {pts[a][1]} L{pts[b][0]} {pts[b][1]}", stroke=ACC, sw=3.2)
    for a, b in links:
        f.lock((pts[a][0] + pts[b][0]) / 2, (pts[a][1] + pts[b][1]) / 2, 0.86, ACC)
    for x, y in pts:
        f.party(x, y, 8)


def figure_wide():
    f = Fig(1120, 500, ALT, uid="ag")
    f.t(24, 32, "An air gap", 20, 700)
    _island(f, 300, 250, 112)
    f.t(300, 250 + 112 + 86, "the gap is crossed by hand, where no one is watching", 15, 400, QUIET, anchor="middle")
    f.t(300, 250 + 112 + 108, "inside, everything is trusted", 15, 400, QUIET, anchor="middle")
    f.path("M590 30 V470", stroke=LINE, sw=1.4, dash="6 6")
    f.t(624, 32, "No single line to defend", 20, 700)
    pts = [(680, 170), (800, 104), (950, 130), (1050, 240), (960, 356), (800, 360), (690, 300), (880, 240)]
    links = [(0, 1), (1, 2), (2, 7), (7, 3), (3, 4), (7, 5), (5, 6), (6, 0)]
    _field(f, pts, links)
    f.t(862, 448, "every connection is checked and sealed on its own", 15, 400, QUIET, anchor="middle")
    f.t(862, 470, "what crosses one of them meets the next", 15, 400, QUIET, anchor="middle")
    return f.svg()


def figure_narrow():
    f = Fig(464, 900, ALT, narrow=True, uid="agn")
    f.t(14, 28, "An air gap", 18, 700)
    _island(f, 232, 214, 96, small=True)
    f.lines(14, 404, ["The gap is crossed by hand, where no one is", "watching. Inside, everything is trusted."], 15, fill=QUIET)
    f.path("M8 462 H456", stroke=LINE, sw=1.4, dash="6 6")
    f.t(14, 500, "No single line to defend", 18, 700)
    pts = [(60, 590), (190, 540), (340, 560), (410, 670), (330, 780), (170, 776), (64, 700), (250, 664)]
    links = [(0, 1), (1, 2), (2, 7), (7, 3), (3, 4), (7, 5), (5, 6), (6, 0)]
    _field(f, pts, links)
    f.lines(14, 836, ["Every connection is checked and sealed on its own.", "What crosses one of them meets the next."], 15, fill=QUIET)
    return f.svg()


def mark():
    """A gap between two banks, and one small plank across it."""
    return _mark("air-gap", "Two banks with a gap between them, and one small plank laid across the gap.",
                 '<path d="M6 40H34V86" class="mk"/>'
                 '<path d="M90 40H62V86" class="mk"/>'
                 '<path d="M38 60H58M38 74H58" class="mk mkd mkt"/>'
                 '<path d="M26 30H70" class="mka"/>')


def html():
    return scene(
        "air-gap", "The idea, taken to its limit", "An air gap is one more boundary",
        "air gap, network isolation, perimeter security, removable-media transfer",
        "A system is cut off from every other network and called safe. The air gap is treated as the strongest protection there is.",
        "An air gap is the boundary idea taken to its limit: one line round everything, and full trust inside. A working system is rarely cut off for long. Data, updates and people have to get in and out, so the gap is crossed by hand, with a drive, a maintenance laptop or a vendor's update, and those crossings are the least watched doors. Isolation slows updates, so the inside falls behind on fixes. It gives no help once something is inside. It suits a thing that changes rarely and talks to no one, such as a key kept offline. It does not suit a system of many connected parts that exchange data all the time. goat has no single line to defend: every connection is checked and sealed on its own, a site can run with no link when it needs to, and every change arrives as a signed, verified release.",
        "Isolation when you need it, without betting everything on it.",
        [("in use", "nothing of a site is reachable from the public internet; every release is signed and verified before it runs"),
         ("designed", "a site that keeps working with no link at all; the tests for mesh control and sign-in under a cut link are built"),
         ("designed", "one signed bundle that carries a release to a site that is cut off")],
        figure_wide() + "\n" + figure_narrow(), mark())
