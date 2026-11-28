"""Scene (second part of the layers idea): protection is applied once, at the ends, and stays on for the
whole path. One idea: the path. Grades: direct connections between machines with a relay only as a
fallback that cannot read what it carries: in use (goatcore decision record 0201, and the mesh documents).
No latency figure is printed: the public tree holds no measured direct-against-relayed number."""
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, RULE, ONACC, mark as _mark, scene

ALT = ("Two paths between the same two sites. The usual path is long: it leaves the first site, passes a gateway, "
       "an aggregation point, a distant hub and another gateway, and at each of those stops the traffic is "
       "opened and wrapped again. The path here is one direct line between the two sites with its locks closed "
       "the whole way. A relay is drawn as a second carrier for when no direct line exists, and it stays closed too.")


def _site(f, x, y, label, r=30):
    f.circle(x, y, r, fill=SOFT, stroke=INK, sw=3)
    f.party(x - 9, y - 6, 5, ring=False); f.party(x + 9, y - 4, 5, ring=False); f.party(x, y + 10, 5, ring=False)
    f.t(x, y + r + 22, label, 15, 700, anchor="middle")


def _stop(f, x, y, label, w=128):
    f.rect(x - w / 2, y - 22, w, 44, 6, PANEL, INK, 1.8, dash="5 4")
    f.t(x, y + 5, label, 14, 400, anchor="middle")
    f.openlock(x, y - 34, 0.95)


def figure_wide():
    return [_path_wide(), estimate_wide(), loss_wide()]


def figure_narrow():
    return [_path_narrow(), estimate_narrow(), loss_narrow()]


def _path_wide():
    f = Fig(1120, 500, ALT, uid="pt")
    ax, bx, y0 = 96, 1024, 318
    # the usual path: a detour through four stops
    stops = [(240, 206, "gateway"), (430, 112, "aggregation point"), (690, 112, "distant hub"), (880, 206, "gateway")]
    pts = [(ax, y0 - 30)] + [(x, y) for x, y, _ in stops] + [(bx, y0 - 30)]
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    f.path(d, stroke=QUIET, sw=2.4, dash="7 6")
    for x, y, lab in stops:
        _stop(f, x, y, lab)
    f.t(560, 28, "Usually: a long way round, opened at every stop", 17, 700, anchor="middle")
    f.t(560, 172, "opened and wrapped again at each stop", 14, 400, QUIET, anchor="middle", italic=True)
    # here: one direct line, closed the whole way
    f.path(f"M{ax + 30} {y0} L{bx - 30} {y0}", stroke=ACC, sw=5)
    for x in (300, 560, 820):
        f.lock(x, y0, 1.0, ACC)
    f.t(560, y0 - 28, "Here: one direct line, closed the whole way", 17, 700, anchor="middle")
    # the relay: a second carrier, which stays closed
    f.path(f"M{ax + 22} {y0 + 22} Q560 {y0 + 150} {bx - 22} {y0 + 22}", stroke=ACC, sw=2.4, dash="3 7")
    f.circle(560, y0 + 86, 20, fill=PAPER, stroke=INK, sw=2.2)
    f.lock(560, y0 + 86, 0.8, ACC)
    f.t(560, y0 + 130, "a relay, when there is no direct line: it carries the traffic closed", 14, 400, QUIET, anchor="middle")
    _site(f, ax, y0, "one site"); _site(f, bx, y0, "another site")
    f.openlock(60, 474, 0.8); f.t(82, 479, "opened here", 13.5, 400, QUIET)
    f.lock(196, 474, 0.8, ACC); f.t(218, 479, "stays closed", 13.5, 400, QUIET)
    return f.svg()


def _path_narrow():
    f = Fig(464, 640, ALT, narrow=True, uid="ptn")
    ax, bx, y0 = 58, 406, 420
    f.t(232, 26, "Usually: a long way round,", 16, 700, anchor="middle")
    f.t(232, 47, "opened at every stop", 16, 700, anchor="middle")
    stops = [(92, 262, "gateway", 104), (232, 132, "distant hub", 124), (372, 262, "gateway", 104)]
    pts = [(ax, y0 - 30)] + [(x, y) for x, y, _, _ in stops] + [(bx, y0 - 30)]
    f.path("M" + " L".join(f"{x} {y}" for x, y in pts), stroke=QUIET, sw=2.4, dash="7 6")
    for x, y, lab, w in stops:
        _stop(f, x, y, lab, w)
    f.t(232, y0 - 52, "Here: one direct line,", 16, 700, anchor="middle")
    f.t(232, y0 - 31, "closed the whole way", 16, 700, anchor="middle")
    f.path(f"M{ax + 30} {y0} L{bx - 30} {y0}", stroke=ACC, sw=5)
    for x in (160, 304):
        f.lock(x, y0, 1.0, ACC)
    f.path(f"M{ax + 22} {y0 + 22} Q232 {y0 + 140} {bx - 22} {y0 + 22}", stroke=ACC, sw=2.4, dash="3 7")
    f.circle(232, y0 + 81, 20, fill=PAPER, stroke=INK, sw=2.2)
    f.lock(232, y0 + 81, 0.8, ACC)
    _site(f, ax, y0, "one site", 26); _site(f, bx, y0, "another", 26)
    f.t(232, y0 + 126, "a relay, when there is no direct line:", 14, 400, QUIET, anchor="middle")
    f.t(232, y0 + 145, "it carries the traffic closed", 14, 400, QUIET, anchor="middle")
    f.openlock(60, 612, 0.8); f.t(82, 617, "opened here", 13.5, 400, QUIET)
    f.lock(196, 612, 0.8, ACC); f.t(218, 617, "stays closed", 13.5, 400, QUIET)
    return f.svg()


EST_ALT = ("Three bars on one time scale, each the round trip between two machines that are ten kilometres apart. "
           "Direct, machine to machine: about one to two milliseconds. Through a regional relay, the fallback, with "
           "nothing opened on the way: about fifteen milliseconds. A typical government or military network, as a "
           "worked example, through a gateway on another continent and back: about two hundred and ten to two "
           "hundred and thirty milliseconds. The same network reached over a satellite service whose ground entry point "
           "is on the far side of another continent: about three hundred and ninety to four hundred and sixty milliseconds. These are estimates from the listed assumptions, not measurements.")

# round trip, milliseconds: (label lines, note, low, high, tone, closed)
EST = [(["Direct, machine to machine"], "the normal case here", 1, 2, "acc", "about 1 to 2 ms"),
       (["Through a regional relay"], "the fallback here; nothing is opened on the way", 15, 15, "acc", "about 15 ms"),
       (["A typical government or military", "network (worked example)"], "through a gateway on another continent, and back", 210, 230, "ink", "about 210 to 230 ms"),
       (["The same, reached over a satellite", "service whose ground entry point is", "on the far side of another continent"], "to the entry point, through more stops there, and back out the same way", 390, 460, "ink", "about 390 to 460 ms")]


def _estimate(f, x0, scale, top, row_h, label_above):
    """Bars on one scale. x0: where 0 ms is; scale: px per ms. Each row is as tall as its own label
    needs, so no label reaches the bar of its row or the row below. Returns the bottom of the axis."""
    import textwrap
    rows, y = [], top
    for lines, note, lo, hi, tone, val in EST:
        if label_above:
            ll, nl = textwrap.wrap(" ".join(lines), 50), textwrap.wrap(note, 58)
            by = y + 4 + (len(ll) - 1) * 19 + len(nl) * 17 + 12
            h = by - y + 30 + 26
        else:
            ll, nl = lines, textwrap.wrap(note, 52)
            by = y + 10
            h = max(row_h, 16 + len(ll) * 20 + (len(nl) - 1) * 17 + 24)
        rows.append((y, by, ll, nl, hi, tone, val))
        y += h
    axis_bottom = y - (8 if label_above else 4)
    for ms in (0, 100, 200, 300, 400):
        x = x0 + ms * scale
        f.path(f"M{x:.1f} {top - 14} V{axis_bottom:.1f}", stroke=RULE, sw=1.4)
        f.t(x, axis_bottom + 20, f"{ms} ms", 13.5, 400, QUIET, "middle")
    for y, by, ll, nl, hi, tone, val in rows:
        if label_above:
            for k, ln in enumerate(ll):
                f.t(14, y + 4 + k * 19, ln, 15, 700)
            for k, ln in enumerate(nl):
                f.t(14, y + 4 + len(ll) * 19 + k * 17, ln, 13.5, 400, QUIET, italic=True)
        else:
            for k, ln in enumerate(ll):
                f.t(24, y + 16 + k * 20, ln, 15.5, 700)
            for k, ln in enumerate(nl):
                f.t(24, y + 16 + len(ll) * 20 + k * 17, ln, 13.5, 400, QUIET, italic=True)
        w = max(hi * scale, 7)
        col = ACC if tone == "acc" else INK
        f.rect(x0, by, w, 30, 3, col if tone == "acc" else PANEL, col, 2, dash=None if tone == "acc" else "6 4")
        inside = x0 + w + 170 >= f.w          # no room after the bar: the value goes inside its right end
        if tone == "ink":   # the stops, where the traffic is opened and sealed again
            n = 6 if f.w > 600 else 4
            span = w - (176 if inside else 0)
            for k in range(1, n):
                f.openlock(x0 + span * k / n, by + 15, 0.74)
        if inside: f.t(x0 + w - 12, by + 20.5, val, 15, 700, anchor="end")
        else: f.t(x0 + w + 12, by + 20.5, val, 15, 700)
    return axis_bottom


def estimate_wide():
    f = Fig(1120, 480, EST_ALT, uid="es")
    f.t(24, 30, "Round trip between two machines 10 km apart", 17, 700)
    _estimate(f, 380, 1.56, 66, 88, False)
    return f.svg()


def estimate_narrow():
    f = Fig(464, 560, EST_ALT, narrow=True, uid="esn")
    f.t(14, 26, "Round trip between two machines 10 km apart", 15.5, 700)
    _estimate(f, 14, 0.94, 60, 106, True)
    return f.svg()


LOSS_ALT = ("Two bars: the sustained throughput of one connection when one packet in a hundred is lost. At a round trip "
            "of 2 milliseconds, about 70 megabits per second. At a round trip of 450 milliseconds, about 0.3 megabits "
            "per second. The loss rate is the same in both. These are estimates from a standard formula.")


def _loss(f, x0, scale, y, label_above):
    rows = [("Direct: a round trip of about 2 ms", 71, "about 70 megabits per second", True),
            ("The long way: a round trip of about 450 ms", 0.32, "about 0.3 megabits per second", False)]
    for lab, mbit, val, acc in rows:
        if label_above:
            f.t(14, y + 4, lab, 15, 700); by = y + 14
        else:
            f.t(24, y + 28, lab, 15.5, 700); by = y + 10
        w = max(mbit * scale, 5)
        f.rect(x0, by, w, 26, 3, ACC if acc else INK, ACC if acc else INK, 2)
        f.t(x0 + w + 12, by + 18.5, val, 15, 700) if x0 + w + 250 < f.w else f.t(x0 + w - 10, by + 18.5, val, 15, 700, ONACC, "end")
        y += 62 if label_above else 48


def loss_wide():
    f = Fig(1120, 150, LOSS_ALT, uid="lo")
    f.t(24, 28, "Throughput of one connection when 1 packet in 100 is lost", 17, 700)
    _loss(f, 380, 9.4, 40, False)
    return f.svg()


def loss_narrow():
    f = Fig(464, 176, LOSS_ALT, narrow=True, uid="lon")
    f.t(14, 24, "One connection, 1 packet in 100 lost", 15.5, 700)
    _loss(f, 14, 6.0, 48, True)
    return f.svg()


ESTIMATE_HTML = """    <figure class="full estimate"><div class="frame">
      <p class="est-h"><b>A rough estimate; the assumptions are listed.</b> None of these numbers is a measurement.</p>
{FIG}
      <ul class="est">
        <li><b>About one hundred times the delay</b> for two machines that are next to each other, when their traffic is sent to another continent and back.</li>
        <li><b>A new secure connection</b> needs about three round trips before the first reply arrives: about 5 ms direct, about 650 ms the long way.</li>
        <li><b>A task that makes 50 exchanges in sequence</b> takes about 0.1 s direct, and about 11 s the long way. On a line with some loss, sustained throughput falls roughly in proportion to the round-trip time.</li>
        <li><b>Encryption is not the cost.</b> One modern processor core seals or opens on the order of 1 to 3 gigabytes per second. The costs of stacked overlays and middle stops are the delay above, the extra header bytes (each tunnel adds roughly 50 to 80 bytes to a 1,500-byte packet, so three stacked tunnels use more than a tenth of every packet and risk splitting it), and the number of machines that must all be working: eight stops that are each up 99.9 percent of the time give a path that is up about 99.2 percent, roughly 70 hours down in a year.</li>
        <li><b>Over a satellite service whose ground entry point is on the far side of another continent</b> the long way grows again: about 390 to 460 ms for the round trip, about 1.2 to 1.4 s for a new secure connection, and about 20 to 23 s for the 50 exchanges. That is several hundred times the delay. With one common substrate, two machines at the same site talk over the local network and never use the satellite link, which then carries only what has to leave the site. Such links commonly give a terminal no public address and accept no inbound connection; the mesh needs neither, because every machine connects outward.</li>
        <li><b>Here</b> the three layers are applied at the ends only: six seal-or-open operations in total, and none in the middle.</li>
      </ul>
      <p class="est-h" style="margin-top:26px"><b>With real links.</b> Delay, variation in delay and loss multiply each other, so the long way behaves several times worse in use than the bars above show, and some applications stop working.</p>
{LOSS}
      <ul class="est">
        <li><b>A lost packet costs at least one more round trip</b> to repair: about 2 ms direct, about 450 ms the long way. When a timer has to run out first, the wait is set from the round-trip time and how much it varies; on the long way that is on the order of one second, and it doubles with each repeated loss.</li>
        <li><b>Throughput falls with delay at the same loss rate.</b> One connection sustains roughly 1.22 &times; packet size &divide; (round-trip time &times; the square root of the loss rate). With 1 percent loss and 1,460-byte packets that is about 70 megabits per second at 2 ms, and about 0.3 megabits per second at 450 ms: more than two hundred times less.</li>
        <li><b>Some uses have a limit, and past it they fail.</b> Conversational voice is planned for about 150 ms one way; the estimate above is 195 to 230 ms before any buffering. Anything that expects an answer within a fixed short time, such as a heartbeat, a lock, a control exchange or a handshake with a time limit, fails once delay and retries pass that limit. The result is not a slower application. It is one that does not work.</li>
      </ul>
      <p class="assume"><i>Assumptions:</i> light in optical fibre covers about 200 km per millisecond; a real route is about 1.5 times the straight-line distance; the two machines are 10 km apart; a regional relay is 500 km away; the distant gateway is 6,700 km away, about the distance from central Europe to the eastern United States; a middle stop that opens, inspects and seals traffic again costs about 1 to 2 ms, and such a route has 4 to 8 of them; for the satellite case, a hop in low orbit adds about 10 to 20 ms, the ground entry point is about 9,000 km away, and from there the traffic passes 6 to 10 stops and about 30 ms of travel before it turns back. The throughput relation is that of Mathis and others (1997); the timer rules are those of RFC 6298; the voice figure is from ITU-T G.114.</p>
    </div></figure>
"""


def mark():
    """Two points and one straight line between them, with a faint detour above it."""
    return _mark("path", "Two points joined by one straight line, with a faint long detour drawn above it.",
                 '<path d="M14 62L30 22H66L82 62" class="mk mkd mkt"/>'
                 '<path d="M14 62H82" class="mka"/>'
                 '<circle cx="14" cy="62" r="7" class="mkfi"/><circle cx="82" cy="62" r="7" class="mkfi"/>')


def html():
    return scene(
        "path", "Three layers: the path", "Sealed once, and closed for the whole path",
        "end-to-end encryption, direct path, hairpin routing, encapsulation overhead",
        "On large enterprise and government networks, each organization brings its own overlay and rides shared lines. Overlays stack. At each boundary between environments the traffic is unwrapped and wrapped again, and traffic between two sites overseas can be routed through gateways on another continent. Every stop adds delay, a place where it can fail, and a place where it is exposed.",
        "Protection is applied at the ends and stays on. Machines connect directly to each other, so traffic takes the short path between them. No outside gateway or relay ever opens the traffic, and sealed data stays sealed from its owner to its readers. One common substrate means one set of layers, applied the same way everywhere, with no re-wrapping in the middle.",
        "The same design choice makes traffic safer and faster.",
        [("in use", "direct connections between machines; a relay only as a fallback, carrying what it cannot read")],
        _path_wide() + "\n" + _path_narrow(), mark()).replace(
        "  </div>\n</section>", ESTIMATE_HTML.replace("{FIG}", estimate_wide() + "\n" + estimate_narrow()).replace("{LOSS}", loss_wide() + "\n" + loss_narrow()) + "  </div>\n</section>")
