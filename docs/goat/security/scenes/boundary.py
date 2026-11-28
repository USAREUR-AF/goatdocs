"""Scene: two ways data crosses the edge of an owner's environment, each its own figure.
Grades (goatcore main, 28 Nov 2026):
  federation boundary node  built   (goatbuilder federate; gate group B: 7 of 10 rows measured)
  sealing for named readers across a federated boundary: designed (decision record 1208, Accepted, says it is
                            not in use between two separate goatnets; goatcore #1501)
  simple boundary node      built   (decision records 1253 and 1263; docs/design/simple-boundary-node.md is marked WIP;
                                     the machine type is built in part and its acceptance has not run on a goatnet)"""
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, LINE, mark as _mark, scene

ALT_FED = ("Two owners' environments, drawn as two plates with a gap between them. A federation boundary node stands at "
           "the edge of each. From the first owner, two sets of data that the owner released travel to the node and "
           "cross to the other side through one sealed tunnel between the two nodes. A third set, not released, "
           "stops before the node and does not cross. On the other side the receiving node makes two separate "
           "checks, first whether it recognizes the sender and then whether the sender is authorized, before the "
           "released data arrives.")
ALT_SIMPLE = ("One owner's environment as a plate. At its edge stands a dedicated machine, the simple boundary node. "
              "From it one plain stream runs one way, inside an encrypted tunnel, to one known destination with a "
              "known owner. An arrow from the destination back toward the environment ends at a bar: nothing else "
              "is reachable through the node. If the tunnel is down, nothing is sent.")


def _card(f, x, y, w, label, released=True):
    f.rect(x, y, w, 40, 6, PAPER if released else "none", INK if released else LINE, 2, dash=None if released else "5 4")
    f.raw(f'<path d="M{x + 12} {y + 14}h20M{x + 12} {y + 22}h14M{x + 12} {y + 30}h18" stroke="{INK if released else LINE}" stroke-width="2" stroke-linecap="round" fill="none"/>')
    f.t(x + 44, y + 25.5, label, 15, 600 if released else 400, INK if released else QUIET)


def _node(f, x, y, label, sub=None, w=150, h=92):
    f.rect(x - w / 2, y - h / 2, w, h, 10, PANEL, INK, 3)
    # a gate: two posts and an opening
    f.raw(f'<path d="M{x - 16} {y - 26}v22M{x + 16} {y - 26}v22M{x - 16} {y - 26}h32" fill="none" stroke="{ACC}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    f.t(x, y + 16, label, 14, 700, anchor="middle")
    if sub: f.t(x, y + 34, sub, 13.5, 400, QUIET, anchor="middle")


def fed_wide():
    f = Fig(1120, 470, ALT_FED, uid="bf")
    f.rect(20, 40, 480, 350, 14, SOFT, INK, 3)
    f.t(40, 70, "YOUR ENVIRONMENT, YOUR AUTHORITY", 14, 700, ls="1.4")
    f.rect(620, 40, 480, 350, 14, SOFT, INK, 3)
    f.t(640, 70, "ANOTHER OWNER'S ENVIRONMENT", 14, 700, ls="1.4")
    nx1, nx2, ny = 425, 695, 216
    # the sets of data
    for y, lab, rel in ((112, "a released set", True), (196, "a released set", True), (300, "not released", False)):
        _card(f, 48, y, 200, lab, rel)
    f.path(f"M248 132 C300 132 300 {ny - 16} {nx1 - 75} {ny - 16}", stroke=ACC, sw=3.2, arrow=False)
    f.path(f"M248 216 H{nx1 - 75}", stroke=ACC, sw=3.2)
    f.path("M248 320 H300", stroke=LINE, sw=2.4, dash="3 6")
    f.path("M306 308 V332", stroke=INK, sw=3.2)
    f.t(316, 325, "does not cross", 13.5, 400, QUIET, italic=True)
    _node(f, nx1, ny, "federation", "boundary node")
    _node(f, nx2, ny, "federation", "boundary node")
    # the one tunnel between the two nodes
    f.path(f"M{nx1 + 75} {ny} H{nx2 - 75}", stroke=ACC, sw=6)
    f.lock((nx1 + nx2) / 2, ny, 1.05, ACC)
    f.t((nx1 + nx2) / 2, ny - 34, "one sealed tunnel", 13.5, 400, QUIET, anchor="middle")
    f.t((nx1 + nx2) / 2, ny + 44, "between the", 13.5, 400, QUIET, anchor="middle")
    f.t((nx1 + nx2) / 2, ny + 62, "two nodes", 13.5, 400, QUIET, anchor="middle")
    # on the other side: two separate checks, then the readers
    f.path(f"M{nx2 + 75} {ny} H810", stroke=ACC, sw=3.2)
    f.num(826, 216, "1", 14); f.t(848, 221, "recognized: who sent this?", 15, 600)
    f.num(826, 282, "2", 14); f.t(848, 287, "authorized: may it be read here?", 15, 600)
    f.path("M826 232 V264", stroke=INK, sw=2, arrow=True)
    f.path("M826 298 V326", stroke=INK, sw=2, arrow=True)
    _card(f, 786, 332, 250, "the released data arrives")
    f.t(848, 252, "two separate checks", 13.5, 400, QUIET, italic=True)
    f.t(20, 428, "Only the sets of data that the owner released cross. Each side keeps its own environment and its own authority.", 16, 400, QUIET)
    f.t(20, 452, "A peering can be removed cleanly: everything it created, and nothing else.", 16, 400, QUIET)
    return f.svg()


def fed_narrow():
    f = Fig(464, 948, ALT_FED, narrow=True, uid="bfn")
    f.rect(8, 10, 448, 356, 14, SOFT, INK, 3)
    f.t(24, 38, "YOUR ENVIRONMENT, YOUR AUTHORITY", 13, 700, ls="1.3")
    for y, lab, rel in ((58, "a released set", True), (112, "a released set", True), (176, "not released", False)):
        _card(f, 24, y, 196, lab, rel)
    nx, ny1, ny2 = 232, 310, 532
    f.path(f"M220 78 C340 78 340 200 {nx + 44} {ny1 - 46}", stroke=ACC, sw=3.2)
    f.path(f"M220 132 C296 132 296 200 {nx + 20} {ny1 - 46}", stroke=ACC, sw=3.2)
    f.path("M122 216 V236", stroke=LINE, sw=2.4, dash="3 6")
    f.path("M108 242 H136", stroke=INK, sw=3.2)
    f.t(24, 250, "does not", 13.5, 400, QUIET, italic=True)
    f.t(24, 267, "cross", 13.5, 400, QUIET, italic=True)
    _node(f, nx, ny1, "federation", "boundary node", 170, 92)
    f.path(f"M{nx} {ny1 + 46} V{ny2 - 46}", stroke=ACC, sw=6)
    f.lock(nx, 411, 1.05, ACC)
    f.t(nx + 28, 406, "one sealed tunnel", 13.5, 400, QUIET)
    f.t(nx + 28, 424, "between the two nodes", 13.5, 400, QUIET)
    f.rect(8, 456, 448, 392, 14, SOFT, INK, 3)
    f.t(24, 484, "ANOTHER OWNER'S", 13, 700, ls="1.3"); f.t(24, 502, "ENVIRONMENT", 13, 700, ls="1.3")
    _node(f, nx, ny2 + 20, "federation", "boundary node", 170, 92)
    f.path(f"M{nx} {ny2 + 66} V628 H60 V642", stroke=ACC, sw=3.2)
    f.num(60, 660, "1", 14); f.t(84, 665, "recognized: who sent this?", 15, 600)
    f.num(60, 716, "2", 14); f.t(84, 721, "authorized: may it be read here?", 15, 600)
    f.path("M60 676 V698", stroke=INK, sw=2, arrow=True)
    f.path("M60 732 V770", stroke=INK, sw=2, arrow=True)
    f.t(84, 693, "two separate checks", 13.5, 400, QUIET, italic=True)
    _card(f, 40, 778, 260, "the released data arrives")
    f.lines(14, 882, ["Only the sets of data that the owner released cross.", "Each side keeps its own environment and authority.", "A peering can be removed cleanly."], 15, fill=QUIET)
    return f.svg()


def simple_wide():
    f = Fig(1120, 372, ALT_SIMPLE, uid="bs")
    f.rect(20, 40, 400, 250, 14, SOFT, INK, 3)
    f.t(40, 70, "YOUR ENVIRONMENT", 14, 700, ls="1.4")
    _card(f, 48, 146, 190, "released data")
    nx, ny = 420, 166
    f.path(f"M238 166 H{nx - 98}", stroke=ACC, sw=3.2)
    f.rect(nx - 98, ny - 52, 196, 104, 10, PANEL, INK, 3)
    f.raw(f'<path d="M{nx - 8} {ny - 30}v22M{nx + 8} {ny - 30}v22" fill="none" stroke="{ACC}" stroke-width="3.2" stroke-linecap="round"/>')
    f.t(nx, ny + 12, "simple boundary node", 14, 700, anchor="middle")
    f.t(nx, ny + 31, "a dedicated machine", 13.5, 400, QUIET, anchor="middle")
    # one stream, one way, inside an encrypted tunnel
    tx1, tx2 = nx + 98, 840
    f.rect(tx1, ny - 20, tx2 - tx1, 40, 20, "none", INK, 2, dash="7 5")
    f.path(f"M{tx1 + 6} {ny} H{tx2 - 10}", stroke=ACC, sw=5, arrow=False)
    f.raw(f'<path d="M{tx2 - 24} {ny - 9} L{tx2 - 8} {ny} L{tx2 - 24} {ny + 9}" fill="none" stroke="{ACC}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    f.lock((tx1 + tx2) / 2, ny - 20, 0.9)
    f.t((tx1 + tx2) / 2, ny - 46, "an encrypted tunnel to that one destination", 13.5, 400, QUIET, anchor="middle")
    f.t((tx1 + tx2) / 2, ny + 46, "one plain UDP or TCP stream, one way", 15, 600, anchor="middle")
    # the one destination
    f.rect(840, ny - 62, 250, 124, 10, PAPER, INK, 3)
    f.raw(f'<g fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="864" y="{ny - 40}" width="44" height="32" rx="3"/><path d="M876 {ny + 2}h20M886 {ny - 8}v10"/></g>')
    f.t(922, ny - 26, "one known", 15, 700); f.t(922, ny - 7, "destination", 15, 700)
    f.t(864, ny + 28, "a known owner", 14, 400, QUIET)
    f.t(864, ny + 47, "the conventions it already uses", 13.5, 400, QUIET)
    # nothing comes back through it
    f.path(f"M900 {ny + 62} V262 H548", stroke=LINE, sw=2.4, dash="3 6")
    f.path("M542 250 V274", stroke=INK, sw=3.2)
    f.t(548, 290, "nothing else is reachable through it", 13.5, 400, QUIET, italic=True)
    f.t(20, 330, "One stream, one destination, one direction. If the tunnel is down, nothing is sent.", 16, 400, QUIET)
    f.t(20, 354, "For a system that cannot join a data fabric.", 16, 400, QUIET)
    return f.svg()


def simple_narrow():
    f = Fig(464, 660, ALT_SIMPLE, narrow=True, uid="bsn")
    f.rect(8, 10, 448, 232, 14, SOFT, INK, 3)
    f.t(24, 38, "YOUR ENVIRONMENT", 13, 700, ls="1.3")
    _card(f, 132, 58, 200, "released data")
    nx, ny = 232, 186
    f.path(f"M{nx} 98 V{ny - 52}", stroke=ACC, sw=3.2)
    f.rect(nx - 100, ny - 52, 200, 104, 10, PANEL, INK, 3)
    f.raw(f'<path d="M{nx - 8} {ny - 30}v22M{nx + 8} {ny - 30}v22" fill="none" stroke="{ACC}" stroke-width="3.2" stroke-linecap="round"/>')
    f.t(nx, ny + 12, "simple boundary node", 14, 700, anchor="middle")
    f.t(nx, ny + 31, "a dedicated machine", 13.5, 400, QUIET, anchor="middle")
    ty1, ty2 = ny + 52, 430
    f.rect(nx - 20, ty1, 40, ty2 - ty1, 20, "none", INK, 2, dash="7 5")
    f.path(f"M{nx} {ty1 + 6} V{ty2 - 10}", stroke=ACC, sw=5)
    f.raw(f'<path d="M{nx - 9} {ty2 - 24} L{nx} {ty2 - 8} L{nx + 9} {ty2 - 24}" fill="none" stroke="{ACC}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    f.lock(nx + 20, (ty1 + ty2) / 2, 0.9)
    f.lines(nx + 46, (ty1 + ty2) / 2 - 22, ["an encrypted tunnel", "to that one destination"], 13.5, fill=QUIET)
    f.lines(nx - 34, (ty1 + ty2) / 2 - 22, ["one plain UDP", "or TCP stream,", "one way"], 15, weight=600, anchor="end")
    f.rect(nx - 130, 430, 260, 96, 10, PAPER, INK, 3)
    f.t(nx, 462, "one known destination", 15, 700, anchor="middle")
    f.t(nx, 483, "a known owner", 14, 400, QUIET, anchor="middle")
    f.t(nx, 503, "the conventions it already uses", 13.5, 400, QUIET, anchor="middle")
    f.lines(14, 566, ["One stream, one destination, one direction.", "Nothing else is reachable through the node.", "If the tunnel is down, nothing is sent."], 15, fill=QUIET)
    return f.svg()


def figure_wide():
    return [fed_wide(), simple_wide()]


def figure_narrow():
    return [fed_narrow(), simple_narrow()]


def mark():
    """One edge with two openings of different kinds: a wide gate and a narrow one-way slot."""
    return _mark("boundary", "A wall with two openings: through the wide one run two lines, through the narrow one runs a single arrow.",
                 '<path d="M48 6V26M48 54V62M48 76V90" class="mk"/>'
                 '<path d="M24 35H72M24 45H72" class="mka"/>'
                 '<path d="M24 69H70M61 61L71 69L61 77" class="mka mkt"/>')


def html():
    s = scene(
        "boundary", "The edge", "Two ways data crosses the edge",
        "federation, gateway, controlled release",
        "Networks are joined to each other: a shared network, a firewall rule, a general gateway. What can cross is whatever the rule fails to stop.",
        "Data enters or leaves only through a boundary node, and there are two kinds. A federation boundary node carries the sets of data that the owner released, over the data fabric, to another owner's environment. A simple boundary node carries one plain stream, one way, to one known destination, for a system that cannot join a data fabric.",
        "You choose what leaves, to whom, and through which one machine.",
        [("built", "federation between two environments: <code>goatbuilder federate &lt;partner&gt;</code> sets it up in one run and can back it out"),
         ("designed", "sealing data for named readers across a boundary between two environments"),
         ("built", "the simple boundary node, as a machine type; it meets the other side's encrypted gateway and stops sending if the tunnel is down")],
        "{F1}", mark())
    two = (fed_wide() + "\n" + fed_narrow() + '</div></figure>\n    <figure class="full"><div class="frame">' + simple_wide() + "\n" + simple_narrow())
    return s.replace("{F1}", two)
