"""Scene: the system documents itself. Grades (goatcore main): built. The log collector is the role
ops/ansible/roles/goat-logship (decision record 1078): it normalizes host and fabric security records to
OCSF, ships them off the host to write-once storage, and carries a sink that forwards the same stream to an
organization's own collector when one address is set. Services emit events over OpenTelemetry
(docs/design/observability-wide-events.md; some producers landed, some pending).
This is the only scene that names RMF, ACAS, STIG and Burp, at the operator's instruction."""
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, LINE, mark as _mark, scene

ALT = ("At the center, one declaration: a document listing the machines, the exact versions by content hash, the "
       "allowed connections, who may do what, and the signed, reviewed changes. An arrow from it to the left builds "
       "the running system. An arrow from it to the right goes to the assessor, who reads the same files. The "
       "running system leaves records: deploy and check records, an audit trail, security events in OCSF, and "
       "service events over OpenTelemetry. Those records flow to your monitoring platform, connected by setting "
       "one address. Outside the system, drawn with dashed lines, are three checks that an organization still "
       "runs from outside: vulnerability scans, configuration baselines and web application testing.")

DECL = ["the machines", "exact versions, by content hash", "the allowed connections", "who may do what", "signed, reviewed changes"]
RECORDS = ["deploy and check records", "an audit trail", "security events, in OCSF", "service events, over OpenTelemetry"]
OUTSIDE = [("vulnerability scans", "ACAS"), ("configuration baselines", "STIG"), ("web application testing", "Burp")]


def _doc(f, x, y, w, h, title, rows, size=15):
    f.rect(x, y, w, h, 8, PAPER, INK, 3)
    f.raw(f'<path d="M{x + w - 30} {y} v30 h30" fill="none" stroke="{INK}" stroke-width="2"/>')
    f.t(x + 20, y + 34, title, size + 3, 700)
    for k, r in enumerate(rows):
        yy = y + 68 + k * (size + 13)
        f.raw(f'<path d="M{x + 22} {yy - 5} l5 5 l9 -10" fill="none" stroke="{ACC}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
        f.t(x + 46, yy, r, size)


def _system(f, x, y, w, h):
    f.rect(x, y, w, h, 12, SOFT, INK, 3)
    pts = [(x + w * .22, y + h * .36), (x + w * .5, y + h * .24), (x + w * .78, y + h * .4), (x + w * .34, y + h * .7), (x + w * .66, y + h * .72)]
    for a, b in ((0, 1), (1, 2), (0, 3), (3, 4), (2, 4), (1, 4)):
        f.path(f"M{pts[a][0]:.0f} {pts[a][1]:.0f} L{pts[b][0]:.0f} {pts[b][1]:.0f}", stroke=ACC, sw=2.6)
    for px, py in pts:
        f.party(px, py, 7)


def figure_wide():
    f = Fig(1120, 640, ALT, uid="sd")
    # the declaration, at the center
    _doc(f, 400, 24, 320, 222, "the declaration", DECL)
    # the running system, built from it
    _system(f, 40, 54, 250, 160)
    f.t(165, 240, "the running system", 16, 700, anchor="middle")
    f.path("M400 134 H300", stroke=INK, sw=2.4, arrow=True)
    f.t(350, 122, "builds", 14, 400, QUIET, anchor="middle", italic=True)
    # the assessor, reading the same files
    f.rect(830, 54, 250, 160, 12, PANEL, INK, 3)
    f.raw(f'<g fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M905 134q50 -46 100 0q-50 46 -100 0z"/></g><circle cx="955" cy="134" r="11" fill="{ACC}"/>')
    f.t(955, 240, "an assessor, or a security engineer", 16, 700, anchor="middle")
    f.path("M720 134 H820", stroke=INK, sw=2.4, arrow=True)
    f.t(772, 104, "reads the", 14, 400, QUIET, anchor="middle", italic=True)
    f.t(772, 122, "same files", 14, 400, QUIET, anchor="middle", italic=True)
    # the records the system leaves
    f.path("M165 252 V318", stroke=INK, sw=2.4, arrow=True)
    f.t(180, 292, "leaves records", 14, 400, QUIET, italic=True)
    for k, r in enumerate(RECORDS):
        x = 40 + k * 196
        f.rect(x, 330, 184, 62, 6, PAPER, INK, 2)
        f.raw(f'<path d="M{x + 14} {352}h16M{x + 14} {361}h10M{x + 14} {370}h14" stroke="{INK}" stroke-width="2" stroke-linecap="round" fill="none"/>')
        words = r.split(", ")
        if len(r) < 16:
            f.t(x + 40, 366, r, 14, 600)
        elif len(words) == 2:
            f.t(x + 40, 356, words[0] + ",", 14, 600); f.t(x + 40, 375, words[1], 14, 600)
        else:
            w2 = r.split(" ", 2)
            f.t(x + 40, 356, " ".join(w2[:2]), 14, 600); f.t(x + 40, 375, w2[2] if len(w2) > 2 else "", 14, 600)
    f.path("M812 361 H862", stroke=INK, sw=2.4, arrow=True)
    f.rect(872, 318, 208, 86, 10, PANEL, INK, 3)
    f.t(976, 352, "your monitoring", 16, 700, anchor="middle"); f.t(976, 373, "platform", 16, 700, anchor="middle")
    f.t(976, 426, "connected by setting one address", 14, 400, QUIET, anchor="middle", italic=True)
    # run from outside
    f.path("M20 462 H1100", stroke=LINE, sw=1.6, dash="6 6")
    f.t(40, 494, "RUN FROM OUTSIDE BY YOUR ORGANIZATION, AND STILL REQUIRED", 14, 700, QUIET, ls="1.4")
    for k, (name, tool) in enumerate(OUTSIDE):
        x = 40 + k * 352
        f.rect(x, 512, 336, 64, 8, "none", INK, 2, dash="6 5")
        f.t(x + 20, 540, name, 16, 600); f.t(x + 20, 561, tool, 14, 400, QUIET)
    f.t(40, 612, "The documentation is the set of files the system runs from, so it cannot drift from the system.", 16, 400, QUIET)
    return f.svg()


def figure_narrow():
    f = Fig(464, 1196, ALT, narrow=True, uid="sdn")
    _doc(f, 52, 12, 360, 222, "the declaration", DECL)
    f.path("M150 234 V282", stroke=INK, sw=2.4, arrow=True); f.t(134, 264, "builds", 14, 400, QUIET, anchor="end", italic=True)
    f.path("M314 234 V282", stroke=INK, sw=2.4, arrow=True); f.t(330, 258, "reads the", 14, 400, QUIET, italic=True); f.t(330, 276, "same files", 14, 400, QUIET, italic=True)
    _system(f, 14, 294, 210, 140)
    f.t(119, 458, "the running system", 15, 700, anchor="middle")
    f.rect(240, 294, 210, 140, 12, PANEL, INK, 3)
    f.raw(f'<g fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M295 364q50 -46 100 0q-50 46 -100 0z"/></g><circle cx="345" cy="364" r="11" fill="{ACC}"/>')
    f.t(345, 458, "an assessor, or a", 15, 700, anchor="middle"); f.t(345, 478, "security engineer", 15, 700, anchor="middle")
    f.path("M119 470 V520", stroke=INK, sw=2.4, arrow=True); f.t(134, 502, "leaves records", 14, 400, QUIET, italic=True)
    for k, r in enumerate(RECORDS):
        y = 532 + k * 56
        f.rect(14, y, 300, 46, 6, PAPER, INK, 2)
        f.raw(f'<path d="M28 {y + 15}h16M28 {y + 23}h10M28 {y + 31}h14" stroke="{INK}" stroke-width="2" stroke-linecap="round" fill="none"/>')
        f.t(56, y + 28.5, r, 14.5, 600)
    f.path("M164 756 V796", stroke=INK, sw=2.4, arrow=True)
    f.rect(14, 808, 300, 60, 10, PANEL, INK, 3)
    f.t(164, 844, "your monitoring platform", 16, 700, anchor="middle")
    f.t(14, 894, "connected by setting one address", 14, 400, QUIET, italic=True)
    f.path("M8 924 H456", stroke=LINE, sw=1.6, dash="6 6")
    f.t(14, 952, "RUN FROM OUTSIDE BY YOUR", 13, 700, QUIET, ls="1.3"); f.t(14, 971, "ORGANIZATION, AND STILL REQUIRED", 13, 700, QUIET, ls="1.3")
    for k, (name, tool) in enumerate(OUTSIDE):
        y = 988 + k * 52
        f.rect(14, y, 436, 42, 8, "none", INK, 2, dash="6 5")
        f.t(30, y + 27, name, 15, 600); f.t(436, y + 27, tool, 14, 400, QUIET, anchor="end")
    f.lines(14, 1164, ["The documentation is the set of files the system", "runs from, so it cannot drift from the system."], 15, fill=QUIET)
    return f.svg()


def mark():
    """A page whose lines are ticked off by the system itself, with a ledger ring."""
    return _mark("self-documenting", "A page with three ticked lines.",
                 '<path d="M22 8H62L78 24V88H22Z" class="mkf"/>'
                 '<path d="M62 8V24H78" class="mk mkt"/>'
                 '<path d="M32 42l5 5l9 -10M32 60l5 5l9 -10M32 78l5 5l9 -10" class="mka mkt"/>'
                 '<path d="M54 44H68M54 62H68M54 80H68" class="mk mkt"/>')


def html():
    return scene(
        "self-documenting", "Evidence", "The system documents itself",
        "compliance as code, continuous monitoring, audit trail, security information and event management (SIEM)",
        "A system's description is written by hand for an assessment, and it is out of date as soon as the system changes.",
        "The system is built from a declaration, so the declaration is the description. Its logs are already in open formats, ready for your monitoring platform.",
        "Your evidence is current because it is the system.",
        [("built", "the declaration, the generated rules, the records and the audit trail, for assessors working under the Risk Management Framework and for security engineers"),
         ("built", "security records in OCSF, sent off each machine, with a forwarder to your own collector")],
        figure_wide() + "\n" + figure_narrow(), mark())


def notes():
    return """<section id="evidence"><h2>What an assessor can read</h2>
<p>The declaration states the machines, the exact version of everything by content hash, the connections that are allowed, and who may do what. Every change is a signed, reviewed commit. Deploys and checks leave their own records.</p>
<p>A collector on every machine gathers the system journal, the audit log, the data fabric's audit records and the access logs. It normalizes them to OCSF and sends them off the machine. A forwarder to an organization's own collector is switched on by setting one address. Services also emit events over OpenTelemetry.</p>
<p>Vulnerability scans (ACAS), configuration baselines (STIG) and web application testing (Burp) are outside tools that an organization still runs.</p>
</section>"""
