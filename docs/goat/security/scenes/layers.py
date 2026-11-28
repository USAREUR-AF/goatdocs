"""Scene: three layers of encryption around every message, drawn as an onion with the readable
message at the center. Grades, from the public tree (goatcore main, 28 Nov 2026):
  mesh tunnel        in use   (WireGuard; a post-quantum key exchange for the tunnel: designed)
  data fabric link   in use   (docs/design/zenoh-pqc-tls.md: the hybrid exchange is the router default)
  grant encryption   in use   (ADR 1208, Accepted, makes it part of the sharing model, and the key service is a
                              pinned fleet component; ADRs 1094 and 1106 still read Proposed and are being
                              corrected. docs/design/grant-crypto-sdk.md: "The platform holds no keys.")"""
import math, textwrap
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, ONACC, RULE, mark as _mark, scene

ALT = ("An onion of three layers around one message. The outer layer is the mesh tunnel between two machines, "
       "a WireGuard tunnel whose keys only those two machines hold. Inside it is the data fabric link between a "
       "program and a router, which prefers a hybrid post-quantum key exchange and applies access rules by "
       "identity. Inside that is grant encryption, which the owner can turn on to seal a data set for named "
       "readers, so that routers and the platform hold no key. At the center is the message itself, a small "
       "readable record. Opening it takes all three keys, and each is held by a different party.")

LAYERS = [
    ("3", "Mesh tunnel", "between two machines",
     "Every packet between two machines travels in a WireGuard tunnel, encrypted with ChaCha20-Poly1305.",
     "Keys held by the two machines, and no one else.",
     [("in use", ""), ("designed", "a standardized post-quantum key exchange for the tunnel")]),
    ("2", "Data fabric link", "between a program and a router",
     "Each link to a router is TLS 1.3 and prefers a hybrid post-quantum key exchange. Access rules, by identity, decide who may publish or read each topic.",
     "Keys held by the two ends of the link.",
     [("in use", "")]),
    ("1", "Grant encryption", "from the owner to named readers",
     "The owner can seal a data set for named readers with hybrid encryption. It is turned on per data set.",
     "Keys held by the named readers. Routers and the platform hold none.",
     [("in use", "for the data sets an owner seals")]),
]


def _onion(f, cx, cy, R, small=False):
    fills = [PANEL, SOFT, PANEL]
    for i, r in enumerate(R[:3]):
        f.circle(cx, cy, r, fill=fills[i], stroke=INK, sw=3 if i == 0 else 2.4)
    # the name of each layer, set on its own band along the top
    names = ["MESH TUNNEL", "DATA FABRIC LINK", "GRANT ENCRYPTION"]
    for i, name in enumerate(names):
        rm = (R[i] + R[i + 1]) / 2 - (5 if small else 6)
        a1, a2 = math.radians(205), math.radians(335)
        x1, y1, x2, y2 = cx + rm * math.cos(a1), cy + rm * math.sin(a1), cx + rm * math.cos(a2), cy + rm * math.sin(a2)
        pid = f"{f.uid}-arc{i}"
        f.raw(f'<path id="{pid}" d="M{x1:.1f} {y1:.1f} A{rm:.1f} {rm:.1f} 0 0 1 {x2:.1f} {y2:.1f}" fill="none"/>')
        f.raw(f'<text font-size="{11.5 if small else 13}" font-weight="700" fill="{QUIET}" letter-spacing="{2.2 if small else 3}">'
              f'<textPath href="#{pid}" startOffset="50%" text-anchor="middle">{name}</textPath></text>')
    # the message: a small record that can be read
    r0 = R[3]
    f.circle(cx, cy, r0, fill=ACC, stroke=INK, sw=2.4)
    cw, ch = (r0 * (1.62 if small else 1.36), r0 * 0.84)
    f.t(cx, cy - ch / 2 - 9, "the message", 13 if small else 14, 700, ONACC, "middle")
    f.rect(cx - cw / 2, cy - ch / 2, cw, ch, 4, PAPER, INK, 1.6)
    fs = 10 if small else 12
    for k, s in enumerate(("station  07", "temp   21.4 C", "time 14:02:11")):
        f.t(cx - cw / 2 + 9, cy - ch / 2 + fs + 7 + k * (fs + 4.5), s, fs, 400, INK, mono=True)


def _block(f, lx, y, layer, chars):
    num, name, sub, body, keys, stat = layer
    f.num(lx, y + 8, num)
    f.t(lx + 28, y + 7, name, 19, 700)
    f.t(lx + 28, y + 28, sub, 14, 400, QUIET, italic=True)
    yy = f.lines(lx + 28, y + 55, textwrap.wrap(body, chars), 15)
    yy += 2
    f.key(lx + 40, yy - 5, 0.9, ACC)
    kl = textwrap.wrap(keys, chars - 3)
    yy = f.lines(lx + 62, yy, kl, 14, fill=QUIET) + 8
    for word, txt in stat:
        w = f.badge(lx + 28, yy, word)
        if txt:
            tl = textwrap.wrap(txt, chars - 9)
            f.lines(lx + 28 + w + 10, yy + 1.5, tl, 13.5, fill=QUIET)
            yy += (len(tl) - 1) * 18
        yy += 26
    return yy


def figure_wide():
    f = Fig(1120, 652, ALT, uid="ly")
    cx, cy, R = 296, 312, [270, 206, 142, 80]
    _onion(f, cx, cy, R)
    lx, ys, angs = 644, [34, 232, 434], [-56, -16, 22]
    for layer, y, r, a in zip(LAYERS, ys, R[:3], angs):
        ex, ey = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        f.path(f"M{ex:.1f} {ey:.1f} L{lx - 74} {y + 8} L{lx - 18} {y + 8}", sw=1.6)
        f.lock(ex, ey)
        _block(f, lx, y, layer, 54)
    f.t(24, 634, "Opening a message takes all three keys, and each is held by a different party.", 16, 400, QUIET)
    return f.svg()


def figure_narrow():
    f = Fig(464, 1096, ALT, narrow=True, uid="lyn")
    cx, cy, R = 232, 222, [212, 162, 112, 64]
    _onion(f, cx, cy, R, small=True)
    for r, a in zip(R[:3], [58, 90, 122]):
        f.lock(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), 0.92)
    y = 474
    for layer in LAYERS:
        y = _block(f, 30, y, layer, 54) + 14
    f.lines(14, y + 6, ["Opening a message takes all three keys,", "and each is held by a different party."], 15, fill=QUIET)
    f.h = round(y + 44)
    return f.svg()


def mark():
    """Three rings around a filled center: layers around one message."""
    return _mark("layers", "Three rings around one filled center.",
                 '<circle cx="48" cy="48" r="40" class="mk"/>'
                 '<circle cx="48" cy="48" r="27" class="mka"/>'
                 '<circle cx="48" cy="48" r="14" class="mk mkt"/>'
                 '<circle cx="48" cy="48" r="6" class="mkfa"/>')


def html():
    return scene(
        "layers", "Three layers", "Three layers around every message",
        "defense in depth, end-to-end encryption, hybrid key exchange",
        "Traffic is encrypted once, by the network or by the application. Whoever breaks or holds that one key reads everything.",
        "A message can be wrapped three times: sealed for its named readers, then carried over a data fabric link, then carried in a mesh tunnel between two machines. Each layer has its own keys, held by different parties.",
        "Breaking one layer shows the next layer, not your data.",
        [("in use", "the mesh tunnel, and the data fabric link with its hybrid post-quantum key exchange"),
         ("in use", "sealing for named readers, for the data sets an owner seals inside a goatnet"),
         ("designed", "a standardized post-quantum key exchange for the mesh tunnel")],
        figure_wide() + "\n" + figure_narrow(), mark())
