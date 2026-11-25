#!/usr/bin/env python3
"""Write the first screen of docs/goat/panoscope/index.html from a recorded panoscope session.

  python3 -I docs/goat/panoscope/build.py <session.json>

<session.json> is what record.mjs (beside this file) writes against a running panoscope:
the /api/view answer, the WebSocket `publish_sampled` events and the last samples per topic.
This script lays the view out on fixed rings (publishers outside, topics in the middle,
subscribers at the center), writes it as static SVG (the no-JavaScript and reduced-motion
frame) and writes the compact session the page replays. It changes only the text between
the BEGIN/END markers in index.html. Standard library only.
"""
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "index.html"
W, H = 740, 540
CX, CY = 370, 270
R_PUB, R_TOPIC, R_CORE = 214, 146, 42
ORDER = ["sensor", "data-service", "c2", "effector"]


def short(key):
    # notional/<system>/<site>/<kind>/v1 -> <system>/<kind>
    p = key.split("/")
    return f"{p[1]}/{p[3]}" if len(p) >= 4 else key


def hexline(sample):
    entries = (sample or {}).get("entries") or []
    if not entries:
        return None
    e = entries[0]
    first = e.get("preview", "").split("\n")[0]
    # "00000000  0a 0d 64 ...|... | ascii" -> the 16 bytes
    body = first[10:58].replace("|", " ")
    return {"fmt": e.get("format"), "size": e.get("size_bytes"), "hex": " ".join(body.split())}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(path):
    rec = json.loads(pathlib.Path(path).read_text())
    view = rec["view"]
    peers = {p["peer_id"]: p for p in view["peers"]}
    topics = view["topics"]
    subs_of = {}
    for e in view["edges"]:
        if e["kind"] == "subscribe":
            subs_of.setdefault(e["from"][len("topic:"):], []).append(e["to"])

    # the center: peers that subscribe (sinks and the observer), and the router
    core = [p for p in view["peers"] if p["subscribes"]]
    core.sort(key=lambda p: (p["role"] != "deriver", p.get("display_name") or ""))
    router = [p for p in view["peers"] if p.get("node_kind") == "router"]

    # the ring: one slot per topic, ordered by the publisher's role class
    def tkey(t):
        pub = peers.get(t["publishers"][0], {}) if t["publishers"] else {}
        rc = pub.get("role_class") or "zz"
        return (ORDER.index(rc) if rc in ORDER else len(ORDER), t["key"])

    topics = sorted(topics, key=tkey)
    n = len(topics)
    nodes, tops = [], []
    index = {}

    def add(peer, x, y, ring):
        index[peer["peer_id"]] = len(nodes)
        name = peer.get("display_name") or ("zenoh-router" if peer.get("node_kind") == "router" else peer["peer_id"][:8])
        nodes.append({"n": name, "rc": peer.get("role_class") or ("router" if peer.get("node_kind") == "router" else "unknown"),
                      "r": peer["role"], "x": round(x, 1), "y": round(y, 1), "ring": ring})

    for i, p in enumerate(core):
        a = -math.pi / 2 + 2 * math.pi * i / len(core)
        add(p, CX + R_CORE * math.cos(a), CY + R_CORE * math.sin(a), "core")
    for p in router:
        add(p, CX, CY, "core")
    for i, t in enumerate(topics):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pub = t["publishers"][0]
        if pub not in index:
            add(peers[pub], CX + R_PUB * math.cos(a), CY + R_PUB * math.sin(a), "outer")
        node = nodes[index[pub]]
        tops.append({"k": t["key"], "s": short(t["key"]), "p": index[pub],
                     "x": round(CX + R_TOPIC * math.cos(a), 1), "y": round(CY + R_TOPIC * math.sin(a), 1),
                     "a": round(a, 4), "subs": [index[s] for s in subs_of.get(t["key"], []) if s in index],
                     "b": hexline(rec["samples"].get(t["key"]))})
        node.setdefault("a", round(a, 4))
    tix = {t["k"]: i for i, t in enumerate(tops)}
    t0 = rec["events"][0]["ts_ms"]
    events = [[e["ts_ms"] - t0, tix[e["topic"]], round(e["ema_eps"], 2)]
              for e in rec["events"] if e.get("kind") == "publish_sampled" and e["topic"] in tix]
    duration = events[-1][0] + 1500
    data = {"w": W, "h": H, "cx": CX, "cy": CY, "nodes": nodes, "topics": tops, "events": events, "duration": duration,
            "totals": {"peers": view["totals"]["peers"], "topics": view["totals"]["topics"]}}

    # static frame: edges sized by the rate panoscope projected in the view
    eps = {t["key"]: t.get("projected_eps") or 0 for t in view["topics"]}
    svg = [f'<svg id="scope" viewBox="0 0 {W} {H}" role="img" aria-labelledby="scope-t">',
           '<title id="scope-t">A replay of 90 seconds recorded from panoscope: 18 synthetic peers on the outer ring each publish one topic; '
           'the topics sit on the middle ring; four subscribers at the center take every topic. A dot travels from a publisher to its topic '
           'and on to the subscribers for each message panoscope sampled.</title>',
           f'<circle class="ring" cx="{CX}" cy="{CY}" r="{R_PUB}"/><circle class="ring" cx="{CX}" cy="{CY}" r="{R_TOPIC}"/>',
           '<g id="sub-edges">']
    for i, t in enumerate(tops):
        for s in t["subs"]:
            nd = nodes[s]
            svg.append(f'<line class="se" data-t="{i}" x1="{t["x"]}" y1="{t["y"]}" x2="{nd["x"]}" y2="{nd["y"]}"/>')
    svg.append('</g><g id="pub-edges">')
    for i, t in enumerate(tops):
        nd = nodes[t["p"]]
        w = 1 + min(3, eps.get(t["k"], 0) * 1.6)
        svg.append(f'<line class="pe rc-{nd["rc"]}" data-t="{i}" x1="{nd["x"]}" y1="{nd["y"]}" x2="{t["x"]}" y2="{t["y"]}" style="stroke-width:{w:.1f}"/>')
    svg.append('</g><g id="pins">')
    for i, t in enumerate(tops):
        x, y = t["x"], t["y"]
        svg.append(f'<path class="pin" data-t="{i}" d="M{x} {y - 6}L{x + 6} {y}L{x} {y + 6}L{x - 6} {y}Z"><title>{esc(t["k"])}</title></path>')
    svg.append('</g><g id="dots"></g><g id="nodes">')
    for i, nd in enumerate(nodes):
        x, y, c = nd["x"], nd["y"], f'nd rc-{nd["rc"]}'
        if nd["rc"] == "router":
            shape = f'<rect class="{c}" data-n="{i}" x="{x - 7}" y="{y - 7}" width="14" height="14" rx="2"/>'
        elif nd["r"] == "sink":
            shape = f'<path class="{c}" data-n="{i}" d="M{x - 10} {y - 7}H{x + 10}L{x} {y + 10}Z"/>'
        elif nd["r"] == "deriver":
            pts = " ".join(f"{x + 11 * math.cos(math.pi / 3 * k):.1f},{y + 11 * math.sin(math.pi / 3 * k):.1f}" for k in range(6))
            shape = f'<polygon class="{c}" data-n="{i}" points="{pts}"/>'
        else:
            shape = f'<circle class="{c}" data-n="{i}" cx="{x}" cy="{y}" r="9"/>'
        svg.append(f'<g>{shape}<title>{esc(nd["n"])} · {esc(nd["rc"])} · {esc(nd["r"])}</title></g>')
        if nd["ring"] == "outer":
            a = nd["a"]
            lx, ly = CX + (R_PUB + 16) * math.cos(a), CY + (R_PUB + 16) * math.sin(a)
            anchor = "start" if math.cos(a) > 0.06 else "end" if math.cos(a) < -0.06 else "middle"
            dy = 4 if abs(math.sin(a)) < 0.9 else (12 if math.sin(a) > 0 else -4)
            svg.append(f'<text class="pl" x="{lx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}">{esc(nd["n"])}</text>')
    svg.append('</g></svg>')

    out = "\n".join(svg) + "\n" + '<script id="session" type="application/json">' + json.dumps(data, separators=(",", ":")) + "</script>"
    html = PAGE.read_text()
    a, b = "<!-- BEGIN scope (build.py) -->", "<!-- END scope (build.py) -->"
    i, j = html.index(a) + len(a), html.index(b)
    PAGE.write_text(html[:i] + "\n" + out + "\n" + html[j:])
    print(f"wrote {PAGE.name}: {len(nodes)} peers, {len(tops)} topics, {len(events)} events over {duration / 1000:.1f} s")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
