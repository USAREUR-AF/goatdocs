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
    ("A deploy refuses what it cannot verify", "in use"),
    ("Two key exchanges offered first on the data fabric", "in use"),
    ("A declared table of roles, enforced", "built"),
    ("A partner is verified without being granted anything", "built"),
    ("An identity can be revoked, a machine held for review", "built"),
    ("Two key exchanges on mesh tunnels", "built"),
    ("Decoy names and web paths", "built"),
    ("Two key exchanges between organizations", "designed"),
    ("Decoys on the data fabric, decoy credentials", "designed"),
    ("Secrets replaced as part of a rebuild", "designed"),
    ("A site keeps working when it is cut off", "designed"),
    ("The hub severs a site; the site works alone", "designed"),
    ("A site built again from a checked export", "designed"),
]
ORDER = ["measured", "in use", "built", "designed"]


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
        out.append(f'<li class="wsum"><span class="wn"><b>Whole site</b><small>The stages, and {dur(d["between_steps_s"])} between steps.</small></span>'
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
    fill = {"ICON": icon, "CSS": read(HERE, "extra.css") + css + read(HERE, "figs.css") + read(HERE, "extra-tail.css"),
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
    page = read(HERE, "page.html")
    for key, value in fill.items():
        page = page.replace("{{" + key + "}}", value)

    def put(match):
        key = match.group(2)
        if key not in m:
            sys.exit(f"page.html: data-measure=\"{key}\" has no measure in build.py")
        return match.group(1) + html.escape(m[key]) + match.group(3)
    page = re.sub(r'(<[a-z]+[^>]*\bdata-measure="([^"]+)"[^>]*>)[^<]*(<)', put, page)
    return HEAD + page


def main():
    check = "--check" in sys.argv[1:]
    page = render()
    bad = 0
    if check:
        if not os.path.exists(OUT) or read(OUT) != page:
            print("docs/goat/security/index.html is not current: run python3 -I docs/goat/security/build.py")
            bad += 1
    else:
        with open(OUT, "w") as f:
            f.write(page)
    if "{{" in page:
        print("docs/goat/security: a {{...}} marker was not filled")
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
