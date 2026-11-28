#!/usr/bin/env python3
"""Write docs/goat/rebuild/index.html from page.html and run.json, and check it. Standard library only.

  python3 -I docs/goat/rebuild/build.py           write index.html
  python3 -I docs/goat/rebuild/build.py --check   fail when index.html is not what this writes

run.json is the record of one timed run: every step with its seconds, every stop with its
reason, the acceptance result and the teardown. Every number on the page, the three bars
of the first screen, the table of stops and the replay are computed from it here. To show
a later run, replace run.json and run this script; nothing on the page is typed by hand.
"""
import html
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(ROOT, ".claude", "skills", "splash-page", "templates", "site", "assets")
OUT = os.path.join(HERE, "index.html")
HEAD = "<!-- Written by docs/goat/rebuild/build.py from page.html and run.json; edit those, then run the script. -->\n"
SCALE = 5400  # the bars' full width, in seconds (90 minutes)


def read(*p):
    with open(os.path.join(*p)) as f:
        return f.read()


def dur(s):
    """354 -> '5 min 54 s'; 4860 -> '81 min'."""
    m, sec = divmod(int(s), 60)
    return f"{m} min {sec} s" if sec else f"{m} min"


def clock(s):
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


def pct(s):
    return f"{100 * s / SCALE:.2f}%"


def facts(d):
    """Everything derived from run.json, once."""
    person = d["person"]["done_at_s"] - d["unattended_end_s"] - d["person"]["stopped_s"]
    late = sum(s["seconds"] for s in d["late_steps"])
    clean = d["unattended_total_s"] + person + late
    acc = d["acceptance"]
    if clean >= acc["at_s"]:
        sys.exit("run.json: the steps alone take longer than the elapsed time")
    return {"person_s": person, "late_s": late, "clean_s": clean,
            "met": acc["at_s"] <= d["target_s"] and acc["fail"] == 0,
            "down_met": d["teardown"]["seconds"] <= d["teardown"]["target_s"]}


def measures(d, f):
    acc, td = d["acceptance"], d["teardown"]
    over = acc["at_s"] - d["target_s"]
    return {
        "teardown": dur(td["seconds"]),
        "teardown-checks": str(td["checks"]),
        "teardown-target": dur(td["target_s"]),
        "teardown-verdict": "met" if f["down_met"] else "not met",
        "signin": dur(d["person"]["done_at_s"]),
        "accept": dur(acc["at_s"]),
        "accept-target": dur(d["target_s"]),
        "accept-verdict": "met" if f["met"] else "not met",
        "accept-over": dur(abs(over)) + (" over the target" if over > 0 else " under the target"),
        "clean": dur(f["clean_s"]),
        "lost": dur(acc["at_s"] - f["clean_s"]),
        "unattended-steps": str(len(d["steps"])),
        "unattended": dur(d["unattended_total_s"]),
        "pass": str(acc["pass"]), "fail": str(acc["fail"]), "unknown": str(acc["unknown"]),
        "stops": str(len(d["stops"])),
        "stops-tool": str(sum(1 for s in d["stops"] if s["cause"] == "tool")),
        "stops-other": str(sum(1 for s in d["stops"] if s["cause"] != "tool")),
        "run": d["run"], "run-date": d["date"], "node-target": dur(d["node"]["target_s"]),
        "slowest": max(d["steps"], key=lambda s: s["seconds"])["name"],
        "slowest-s": dur(max(s["seconds"] for s in d["steps"])),
    }


def stage(d, f, m):
    acc, td = d["acceptance"], d["teardown"]
    ticks = "".join(f'<i class="tick" data-at="{s["at_s"]}" style="left:{pct(s["at_s"])}"></i>' for s in d["stops"])
    target = f'<i class="target" style="left:{pct(d["target_s"])}"></i>'
    lines = [
        ("", f'{d["steps"][-1]["phase"]:02d}  {d["steps"][-1]["name"]}  {clock(d["steps"][-1]["seconds"])}'),
        ("", f'{d["person"]["phase"]}  {d["person"]["name"]}, done at {clock(d["person"]["done_at_s"])}'),
        ("st", f'{len(d["stops"])} stops; the last phase did not finish'),
        ("ev", f'acceptance: {acc["pass"]} passed, {acc["fail"]} failed, {acc["unknown"]} undecided, at {clock(acc["at_s"])}'),
        ("st" if not f["met"] else "ok", f'first site: {m["accept"]}; target {m["accept-target"]}: {m["accept-verdict"]}'),
        ("", f'the same steps with no stop: {m["clean"]}'),
        ("ok" if f["down_met"] else "st", f'site taken down: {m["teardown"]}; target {m["teardown-target"]}: {m["teardown-verdict"]}'),
    ]
    pre = "".join(f'<span class="{c}">{html.escape(t)}</span>' if c else f"<span>{html.escape(t)}</span>" for c, t in lines)
    label = (
        f'A replay of run {d["run"]}, a first site built on real machines against a clock. The steps of phases 1 to 10 run '
        f'with no stop in {m["unattended"]}. The administrator signs in at {m["signin"]}. Then {m["stops"]} stops follow. '
        f'The acceptance suite passes {m["accept"]} after the start, with {acc["pass"]} checks passed, {acc["fail"]} failed '
        f'and {acc["unknown"]} undecided. The target is {m["accept-target"]}, so the target is {m["accept-verdict"]}. '
        f'A second bar shows the same steps with no stop: {m["clean"]}. A third bar shows a site taken down in '
        f'{m["teardown"]}, against a target of {m["teardown-target"]}.')
    marks = "".join(f'<span style="left:{pct(t * 60)}">{t}</span>' for t in (0, 15, 30, 45, 75, 90))
    return f'''<div class="stage" role="img" aria-label="{html.escape(label)}">
      <div class="stage-head"><span><b>run {d["run"]}</b> &middot; a first site</span><span id="step">acceptance</span></div>
      <div class="clock" aria-hidden="true"><span class="t" id="clk">{clock(acc["at_s"])}</span><span class="of">minutes:seconds &middot; target {clock(d["target_s"])}</span></div>
      <div class="bars" aria-hidden="true">
        <div class="brow"><div class="bl"><span>this run, start to passing acceptance</span><b id="v1">{m["accept"]}</b></div>
          <div class="trk"><i class="run" id="b1" style="width:{pct(d["person"]["done_at_s"])}"></i><i class="lost" id="b1l" style="left:{pct(d["person"]["done_at_s"])};width:{pct(acc["at_s"] - d["person"]["done_at_s"])}"></i>{ticks}{target}</div></div>
        <div class="brow"><div class="bl"><span>the same steps with no stop</span><b id="v2">{m["clean"]}</b></div>
          <div class="trk"><i class="run" id="b2" style="width:{pct(f["clean_s"])}"></i>{target}</div></div>
        <div class="brow"><div class="bl"><span>a site taken down (target {m["teardown-target"]})</span><b id="v3">{m["teardown"]}</b></div>
          <div class="trk"><i class="run" id="b3" style="width:{pct(td["seconds"])}"></i><i class="target" style="left:{pct(td["target_s"])}"></i></div></div>
        <div class="scale">{marks}<span class="tg" style="left:{pct(d["target_s"])}">target 60</span></div>
      </div>
      <div class="key" aria-hidden="true"><span><i class="k-run"></i>steps running</span><span><i class="k-lost"></i>stopped, or repeating after a stop</span><span><i class="k-tg"></i>target</span></div>
      <pre class="stage-lines" id="stage-lines" aria-hidden="true">{pre}</pre>
      <div class="stage-foot">The run's own step times and stops, from <code>run.json</code> beside this page, replayed in order.</div>
    </div>'''


def stops_rows(d):
    return "\n".join(
        f'          <tr><td class="c num">{s["n"]}</td><td class="c">{s["phase"]}</td><td>{html.escape(s["reason"])}</td><td class="c">{s["cause"]}</td></tr>'
        for s in d["stops"])


def render():
    d = json.loads(read(HERE, "run.json"))
    f = facts(d)
    m = measures(d, f)
    icon = "data:image/svg+xml," + urllib.parse.quote(read(HERE, "icon.svg").strip(), safe="=:/ '")
    css = read(ASSETS, "site.css")
    css = css[css.index("* { box-sizing"):]   # the template's tokens and metaphor are replaced by extra.css
    replay = {"scale": SCALE, "target": d["target_s"], "steps": d["steps"], "unattended_end": d["unattended_end_s"],
              "person": d["person"], "stops": d["stops"], "acceptance": d["acceptance"], "clean": f["clean_s"],
              "teardown": d["teardown"], "met": f["met"], "down_met": f["down_met"]}
    page = read(HERE, "page.html")
    for key, value in {"ICON": icon, "CSS": read(HERE, "extra.css") + css + read(HERE, "extra-tail.css"),
                       "JS": read(HERE, "replay.js"), "STAGE": stage(d, f, m), "STOPS": stops_rows(d),
                       "RUN": json.dumps(replay, separators=(",", ":")).replace("</", "<\\/")}.items():
        page = page.replace("{{" + key + "}}", value)

    def fill(match):
        key = match.group(2)
        if key not in m:
            sys.exit(f"page.html: data-measure=\"{key}\" has no measure in build.py")
        return match.group(1) + html.escape(m[key]) + match.group(3)
    page = re.sub(r'(<[a-z]+[^>]*\bdata-measure="([^"]+)"[^>]*>)[^<]*(<)', fill, page)
    return HEAD + page, d


def main():
    check = "--check" in sys.argv[1:]
    page, d = render()
    bad = 0
    if check:
        if not os.path.exists(OUT) or read(OUT) != page:
            print("docs/goat/rebuild/index.html is not current: run python3 -I docs/goat/rebuild/build.py")
            bad += 1
    else:
        with open(OUT, "w") as f:
            f.write(page)
    if "{{" in page:
        print("docs/goat/rebuild: a {{...}} marker was not filled")
        bad += 1
    # run.json is public: it holds step names, seconds and plain reasons, and nothing that names a deployment
    raw = read(HERE, "run.json")
    if re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b|[A-Za-z0-9-]+\.(net|com|mil|org)\b|@", raw):
        print("docs/goat/rebuild/run.json: an address, a domain name or a mail address; the record names no deployment")
        bad += 1
    for s in d["stops"]:
        if s["cause"] not in ("tool", "process", "test harness"):
            print(f'docs/goat/rebuild/run.json: stop {s["n"]}: cause must be tool, process or test harness')
            bad += 1
    if bad:
        return 1
    print("docs/goat/rebuild: current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
