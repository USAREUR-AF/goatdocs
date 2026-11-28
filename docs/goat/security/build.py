#!/usr/bin/env python3
"""Write docs/goat/security/index.html from page.html, figures.py and run.json, and check it.
Standard library only.

  python3 -I docs/goat/security/build.py           write index.html
  python3 -I docs/goat/security/build.py --check   fail when index.html is not what this writes

run.json is one measured build of a whole site on real machines: every stage with the time
of each of its steps, and one measured teardown. Every time on the page, the build drawn in
the first screen and in the rebuild section, and the replay are computed from it here. To
show a later measurement, replace run.json and run this script.
"""
import html
import importlib.util
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(ROOT, ".claude", "skills", "splash-page", "templates", "site", "assets")
OUT = os.path.join(HERE, "index.html")
HEAD = "<!-- Written by docs/goat/security/build.py from page.html, figures.py and run.json; edit those, then run the script. -->\n"

# Where each part stands: (what it is, status). Measured: a named run on real machines. In use: built and
# running by default. Built: in the tree, and not switched on by default. Designed: decided, not built.
STATUS = [
    ("A whole site built by one command", "measured"),
    ("A site taken down by one command", "measured"),
    ("Every site runs on hardware its owner holds", "in use"),
    ("A cloud holds relays only, and a relay reads nothing", "in use"),
    ("A private mesh overlay that rides on any link", "in use"),
    ("Mesh tunnels on a common open protocol", "in use"),
    ("No answer to a packet that cannot be authenticated", "in use"),
    ("No site has a public address", "in use"),
    ("Service names are known inside only", "in use"),
    ("An identity for each person, machine and workload", "in use"),
    ("No connection without a declared rule", "in use"),
    ("Access rules generated from a reviewed declaration", "in use"),
    ("The secret store cannot read what it holds", "in use"),
    ("Shared data sealed for named readers; the platform holds no key", "in use"),
    ("No central broker on the data fabric", "in use"),
    ("Three layers of encryption, each with its own keys", "in use"),
    ("Machines connect directly; a relay is a fallback", "in use"),
    ("A deploy refuses what it cannot verify", "in use"),
    ("Post-quantum key exchange preferred on the data fabric", "in use"),
    ("Machines that have joined keep talking with no link to any other site", "in use"),
    ("A declared table of roles, enforced", "built"),
    ("Each site runs its own sign-in and mesh control, tested with the link cut", "built"),
    ("The hub's sever directive: nothing a severed site writes reaches another site", "built"),
    ("Federation between two environments, set up and backed out by one command", "built"),
    ("A simple boundary node: one stream, one way, to one destination", "built"),
    ("Security records normalized to OCSF, and forwarded to your collector as CEF over syslog", "built"),
    ("A partner is verified without being granted anything", "built"),
    ("An identity can be revoked, a machine held for review", "built"),
    ("A post-quantum key exchange for mesh tunnels, not enabled", "built"),
    ("Decoy names and web paths", "built"),
    ("Post-quantum key exchange between organizations", "designed"),
    ("Decoys on the data fabric, decoy credentials", "designed"),
    ("Secrets replaced as part of a rebuild", "designed"),
    ("Administration changes at a site that is cut off, merged when the link returns", "designed"),
    ("A severed site rejoins after it is built again and loaded from the hub", "designed"),
    ("A site built again from a checked export", "designed"),
    ("One signed bundle that carries a release to a site that is cut off", "designed"),
    ("A standardized post-quantum key exchange for mesh tunnels; options are being evaluated", "planned"),
]
ORDER = ["measured", "in use", "built", "designed", "planned"]

# Scenes written as one module each in scenes/: the module returns its whole section and its mark.
SCENES = ["layers", "path", "custody", "self_documenting", "boundary", "air_gap", "grade", "timing"]


def read(*p):
    with open(os.path.join(*p)) as f:
        return f.read()


def load_figures():
    spec = importlib.util.spec_from_file_location("figures", os.path.join(HERE, "figures.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dur(s):
    """354 -> '5 min 54 s'; 3600 -> '60 min'."""
    m, sec = divmod(int(s), 60)
    return f"{m} min {sec} s" if sec else f"{m} min"


def clock(s):
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


def stages(d):
    """[(name, what it does, seconds)], the handover time between steps as the last row."""
    rows = [(s["name"], s["does"], sum(x["seconds"] for x in s["steps"])) for s in d["stages"]]
    return rows, sum(r[2] for r in rows) + d["between_steps_s"]


def measures(d, rows, total):
    td, req = d["teardown"], d["requirement"]
    slow = max(rows, key=lambda r: r[2])
    return {
        "build": dur(total), "build-min": dur(total - total % 60), "build-clock": clock(total), "down": dur(td["seconds"]),
        "down-checks": str(td["checks"]), "checks": str(d["checks_passed"]), "stages": str(len(rows)),
        "commands": "1",
        "req-site": dur(req["first_site_s"]), "req-node": dur(req["machine_added_s"]), "req-down": dur(req["site_down_s"]),
        "slowest": slow[0][0].lower() + slow[0][1:], "slowest-s": dur(slow[2]),
    }


def waterfall(rows, total, d, full):
    """The build as rows on one clock: each stage starts where the one before it ended."""
    out, t = [], 0
    for i, (name, does, sec) in enumerate(rows):
        left, width = 100 * t / total, max(100 * sec / total, 0.9)
        text = f'<span class="wn"><b>{html.escape(name)}</b>' + (f'<small>{html.escape(does)}</small>' if full else "") + "</span>"
        out.append(f'<li data-end="{t + sec}">{text}<span class="wt"><i style="left:{left:.2f}%;width:{width:.2f}%"></i></span>'
                   f'<span class="wd">{clock(sec)}</span></li>')
        t += sec
    if full:
        out.append(f'<li class="wsum"><span class="wn"><b>Whole site</b><small>all stages, plus {dur(d["between_steps_s"])} between them.</small></span>'
                   f'<span class="wt"><i style="left:0;width:100%"></i></span><span class="wd">{clock(total)}</span></li>')
    return "\n          ".join(out)


def stage(rows, total, d, m, figs):
    label = (f'A drawing of a whole site that builds itself in {m["stages"]} stages: '
             + "; ".join(f"{n.lower()}, {dur(s)}" for n, _, s in rows)
             + f'. The whole build is {m["build"]} of machine time, measured on real machines. '
             f'The site is then taken down again in {m["down"]}, and built again.')
    marks = "".join(f'<i style="left:{100 * sum(r[2] for r in rows[:k + 1]) / total:.2f}%"></i>' for k in range(len(rows) - 1))
    return f'''<div class="stage" role="img" aria-label="{html.escape(label)}">
      <div class="stage-head"><span><b>standup</b> &middot; one command</span><span id="phase">built</span></div>
      <div class="site" aria-hidden="true">{figs.site_svg("")}</div>
      <div class="clock" aria-hidden="true"><span class="t" id="clk">{clock(total)}</span><span class="of"><b id="step">The whole site is built and checked</b><span id="clk-of">minutes:seconds of machine time</span></span></div>
      <div class="prog" aria-hidden="true"><span class="bar"><i id="pbar" style="width:100%"></i>{marks}</span></div>
      <div class="stage-foot">One command builds the site; one command takes it down in {m["down"]}; the same command builds it again. Times measured on real machines.</div>
    </div>'''


def status_grid():
    head = "".join(f'<span class="sh">{o}</span>' for o in ORDER)
    rows = []
    for what, st in sorted(STATUS, key=lambda r: ORDER.index(r[1])):
        kind = "s-" + st.replace(" ", "")
        cells = "".join(f'<span class="sc on {kind}" data-s="{o}" role="img" aria-label="{o}"></span>' if st == o
                        else '<span class="sc"></span>' for o in ORDER)
        rows.append(f'<div class="sr" role="listitem"><span class="sw">{html.escape(what)}</span>{cells}</div>')
    return (f'<div class="sgrid" role="list" aria-label="The status of each part of the design">'
            f'<div class="sr shead" aria-hidden="true"><span class="sw"></span>{head}</div>\n      ' + "\n      ".join(rows) + "</div>")


# Each scene links to the row of the code table that shows its claim: scene id -> the claim, in STATUS's words.
IN_THE_CODE = {
    "position": "No connection without a declared rule",
    "air-gap": "Machines that have joined keep talking with no link to any other site",
    "custody": "Every site runs on hardware its owner holds",
    "join": "No site has a public address",
    "after": "Machines connect directly; a relay is a fallback",
    "silent": "No answer to a packet that cannot be authenticated",
    "zero-trust": "No connection without a declared rule",
    "readers": "Shared data sealed for named readers; the platform holds no key",
    "layers": "Three layers of encryption, each with its own keys",
    "path": "Machines connect directly; a relay is a fallback",
    "chain": "A deploy refuses what it cannot verify",
    "self-documenting": "Security records normalized to OCSF, and forwarded to your collector as CEF over syslog",
    "quantum": "Post-quantum key exchange preferred on the data fabric",
    "decoy": "Decoy names and web paths",
    "timing": "A site taken down by one command",
    "rebuild": "A whole site built by one command",
    "island": "Machines that have joined keep talking with no link to any other site",
    "hub": "The hub's sever directive: nothing a severed site writes reaches another site",
    "boundary": "Federation between two environments, set up and backed out by one command",
}


def code_table():
    """The section "Where each claim is shown in the code": one row for each row of the status figure."""
    d = json.loads(read(HERE, "code-links.json"))
    by = {c["claim"]: c for c in d["claims"]}
    missing = [w for w, _ in STATUS if w not in by] + [c for c in by if c not in dict(STATUS)]
    if missing:
        sys.exit("code-links.json and STATUS in build.py do not list the same claims: " + "; ".join(missing))
    base = f'{d["repository"]}/blob/{d["commit"]}/'

    def links(items):
        def one(label, p, a, b_):
            if p.startswith("https://"):
                return f'<a href="{p}">{html.escape(label)}</a>'
            return f'<a href="{base}{p}#L{a}' + (f'-L{b_}' if a != b_ else "") + f'">{html.escape(label)}</a>'
        return "<br>".join(one(*i) for i in items)
    rows = []
    for n, (what, st) in enumerate(sorted(STATUS, key=lambda r: ORDER.index(r[1])), 1):
        c = by[what]
        note = f'<span class="cn">{html.escape(c["note"])}</span>' if c["note"] else ""
        code = links(c["code"]) + ("<br>" if c["code"] and note else "") + note
        rows.append(f'<tr id="{code_id(what)}"><td>{html.escape(what)}</td><td>{st}</td><td>{code}</td><td>{links(c["test"]) or ("none" if c["code"] else "")}</td></tr>')
    return (f'<section id="code"><h2>Where each claim is shown in the code</h2>\n'
            f'<p>One row for each row of the status figure on the security page. Every link goes to the public repository at commit '
            f'<a href="{d["repository"]}/commit/{d["commit"]}"><code>{d["commit"][:8]}</code></a> of {d["date"]}, so the line numbers stay true.</p>\n'
            f'<p>A claim that is designed links to its decision record or design document.</p>\n'
            f'<div class="tw"><table>\n<tr><th>Claim</th><th>Status</th><th>Where it is shown</th><th>Test</th></tr>\n'
            + "\n".join(rows) + "\n</table></div>\n</section>")


def code_id(what):
    return "code-" + re.sub(r"[^a-z0-9]+", "-", what.lower()).strip("-")[:48].strip("-")


def render():
    d = json.loads(read(HERE, "run.json"))
    rows, total = stages(d)
    m = measures(d, rows, total)
    figs = load_figures()
    icon = "data:image/svg+xml," + urllib.parse.quote(read(HERE, "icon.svg").strip(), safe="=:/ '")
    css = read(ASSETS, "site.css")
    css = css[css.index("* { box-sizing"):]   # the template's tokens and metaphor are replaced by extra.css
    replay = {"total": total, "down": d["teardown"]["seconds"], "ends": [], "names": [r[0] for r in rows]}
    t = 0
    for _, _, sec in rows:
        t += sec
        replay["ends"].append(t)
    fill = {"ICON": icon, "CSS": read(HERE, "extra.css") + css + read(HERE, "figs.css") + read(HERE, "extra-tail.css") + read(HERE, "scenes", "scenes.css"),
            "JS": read(HERE, "replay.js"), "STAGE": stage(rows, total, d, m, figs),
            "WATERFALL": waterfall(rows, total, d, True), "STATUS": status_grid(),
            "RUN": json.dumps(replay, separators=(",", ":")).replace("</", "<\\/")}
    for key, fn in figs.FIGURES.items():
        fill[key] = fn(m["build"], m["down"]) if key == "FIG_REBUILD" else fn()
    _ps = importlib.util.spec_from_file_location("position_fig", os.path.join(HERE, "position_fig.py"))
    position_fig = importlib.util.module_from_spec(_ps); _ps.loader.exec_module(position_fig)  # operator-specified position figure (28 Nov)
    fill["FIG_BOUNDARIES"] = position_fig.position_figure()
    for key, fn in figs.MARKS.items():
        fill[key] = fn()
    notes = []
    sys.path.insert(0, os.path.join(HERE, "scenes"))   # the scene modules import their shared kit by name
    for name in SCENES:
        spec = importlib.util.spec_from_file_location("scene_" + name, os.path.join(HERE, "scenes", name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fill["SCENE_" + name.upper()] = mod.html()
        fill["SCENE_MARK_" + name.upper()] = mod.mark()
        if hasattr(mod, "notes"):
            notes.append(mod.notes())
    page = read(HERE, "page.html")
    for key, value in fill.items():
        page = page.replace("{{" + key + "}}", value)

    def put(match):
        key = match.group(2)
        if key not in m:
            sys.exit(f"page.html: data-measure=\"{key}\" has no measure in build.py")
        return match.group(1) + html.escape(m[key]) + match.group(3)
    measure = r'(<[a-z]+[^>]*\bdata-measure="([^"]+)"[^>]*>)[^<]*(<)'
    page = re.sub(measure, put, page)
    # the notes page: the scenes' own notes in page order, then the notes kept beside this script
    body = "\n".join(notes) + "\n" + read(HERE, "notes-own.html") + "\n" + code_table()
    for sid, what in IN_THE_CODE.items():        # ONE small link in each scene: after its status rows, or after its three blocks
        sec = re.search(r'<section class="scene[^"]*" id="%s">.*?</section>' % re.escape(sid), page, flags=re.S)
        if not sec:
            sys.exit(f"build.py: no scene {sid} for its code link")
        inner = re.search(r'<ul class="ev">.*?</ul>', sec.group(0), flags=re.S) or re.search(r'</dl>', sec.group(0))
        at = sec.start() + inner.end()
        page = page[:at] + f'\n      <p class="incode"><a href="notes/#{code_id(what)}">in the code</a></p>' + page[at:]
    for sec in re.finditer(r'<section class="scene[^"]*" id="([^"]+)">.*?</section>', page, flags=re.S):
        if sec.group(0).count('class="incode"') != 1:
            sys.exit(f"build.py: scene {sec.group(1)} has {sec.group(0).count('class=\"incode\"')} code links; each scene has one")
    body = re.sub(r'(?<!<div class="tw">)<table>(.*?)</table>', r'<div class="tw"><table>\1</table></div>', body, flags=re.S)   # a wide table scrolls by itself
    toc = "".join(f'<a href="#{i}">{html.escape(t)}</a>' for i, t in re.findall(r'<section id="([^"]+)"><h2>([^<]+)</h2>', body))
    note = read(HERE, "notes-page.html")
    for key, value in {"ICON": icon, "CSS": fill["CSS"], "TOC": toc, "NOTES": body}.items():
        note = note.replace("{{" + key + "}}", value)
    note = re.sub(measure, put, note)
    return HEAD + page, HEAD.replace("page.html, figures.py and run.json", "notes-page.html, notes-own.html and the scenes") + note


def main():
    check = "--check" in sys.argv[1:]
    page, note = render()
    bad = 0
    for out, text in ((OUT, page), (os.path.join(HERE, "notes", "index.html"), note)):
        if check:
            if not os.path.exists(out) or read(out) != text:
                print(f"{os.path.relpath(out, ROOT)} is not current: run python3 -I docs/goat/security/build.py")
                bad += 1
        else:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w") as f:
                f.write(text)
        if "{{" in text:
            print(f"{os.path.relpath(out, ROOT)}: a {{{{...}}}} marker was not filled")
            bad += 1
    # run.json is public: stage names, seconds and plain descriptions, and nothing that names a deployment
    if re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b|[A-Za-z0-9-]+\.(net|com|mil|org)\b|@", read(HERE, "run.json")):
        print("docs/goat/security/run.json: an address, a domain name or a mail address; the record names no deployment")
        bad += 1
    if bad:
        return 1
    print("docs/goat/security: current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
