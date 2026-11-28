"""Scene: the race of clocks. One figure on one logarithmic time axis: an attacker's clocks, a defender's
usual clocks, and the two clocks measured here. It sits directly before the rebuild scene.

Every attacker and usual-defender value is from a named published source, listed in SOURCES and printed
under the figure (read 28 Nov 2026). The two values for "here" are the page's own measured numbers
(run.json): a site taken down in 5 min 54 s, a whole site built in 38 min 12 s of machine time.
Left out, because no defensible published number was found: the time to lock down data and access after
an incident."""
import math
from _kit import Fig, INK, QUIET, PAPER, PANEL, ACC, SOFT, LINE, RULE, ONACC, mark as _mark, scene

MIN, HOUR, DAY = 60, 3600, 86400
TICKS = [(MIN, "1 minute", "1 min"), (HOUR, "1 hour", "1 h"), (DAY, "1 day", "1 d"), (7 * DAY, "1 week", "1 wk"),
         (30 * DAY, "1 month", "1 mo"), (182 * DAY, "6 months", "6 mo")]
LO, HI = math.log10(20), math.log10(600 * DAY)

# (label lines, then (seconds, text) or None, now (seconds, text), extra)
ATTACK = [(["Average time to exploit a flaw,", "counted from its fix"], (63 * DAY, "63 days, 2018 to 2019"), (5 * DAY, "5 days, 2023"), None),
          (["Average time from a first foothold", "to moving through the network"], (118 * MIN, "1 h 58 min, 2017"), (29 * MIN, "29 min, 2025"), (27, "fastest seen: 27 s")),
          (["Median time inside", "before being noticed"], (416 * DAY, "416 days, 2011"), (14 * DAY, "14 days, 2025"), None)]
DEFEND = [(["To fix half of the critical flaws,", "once a fix exists"], None, (55 * DAY, "55 days"), None),
          (["Mean time to identify and", "contain a data breach"], None, (241 * DAY, "241 days"), None),
          (["To recover after", "ransomware"], None, (30 * DAY, "more than a month, for 34 in 100"), "open")]
HERE = [(["A site taken down"], None, (354, "5 min 54 s"), None),
        (["A whole site built again"], None, (38 * MIN + 12, "38 min 12 s"), None)]

SOURCES = [
    ("Average time to exploit a flaw", "Mandiant, \"How Low Can You Go? An Analysis of 2023 Time-to-Exploit Trends\", 15 October 2024: an average of 63 days in 2018 to 2019 and of five days in 2023, with outliers left out",
     "https://cloud.google.com/blog/topics/threat-intelligence/time-to-exploit-trends-2023"),
    ("Average time from a first foothold to moving through the network, 2017", "CrowdStrike, press release on its 2018 Global Threat Report, 26 February 2018: one hour and 58 minutes",
     "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-global-threat-report-reveals-the-biggest-cyber-crime-and-targeted-intrusion-trends/"),
    ("The same, 2025", "CrowdStrike, press release on its 2026 Global Threat Report, 24 February 2026: an average of 29 minutes for criminal intrusions, the fastest in 27 seconds",
     "https://www.crowdstrike.com/en-us/press-releases/2026-crowdstrike-global-threat-report/"),
    ("Median time inside before being noticed, 2011", "Mandiant, \"M-Trends 2021\", 13 April 2021: a global median of 416 days reported in 2011",
     "https://cloud.google.com/blog/topics/threat-intelligence/m-trends-2021-a-view-from-the-front-lines"),
    ("The same, 2025", "Mandiant, \"M-Trends 2026\", 23 March 2026: a global median of 14 days, up from 11",
     "https://cloud.google.com/blog/topics/threat-intelligence/m-trends-2026"),
    ("Time to fix half of the critical flaws", "Verizon, release on its 2024 Data Breach Investigations Report, 1 May 2024: 55 days to remediate 50 percent of critical vulnerabilities after patches are available",
     "https://www.verizon.com/about/news/2024-data-breach-investigations-report-vulnerability-exploitation-boom"),
    ("Mean time to identify and contain a data breach", "IBM, \"2025 Cost of a Data Breach Report\": a mean of 241 days",
     "https://www.ibm.com/think/x-force/2025-cost-of-a-data-breach-navigating-ai"),
    ("Time to recover after ransomware", "Sophos, The State of Ransomware 2024 (survey of 5,000 organizations, January to February 2024): 34 percent took more than a month",
     "https://assets.sophos.com/X24WTUEQ/at/sbqqvwxz3jksrbmfgnbj9pkp/sophos-ransomware-experience-infographic.pdf"),
]

ALT = ("A race of clocks on one logarithmic time axis, from seconds to more than a year. An attacker's clocks, each "
       "with an earlier value and a current value: the average time to exploit a flaw, 63 days then and 5 days now; "
       "the average time from a first foothold to moving through the network, 1 hour 58 minutes then and 29 "
       "minutes now, with the fastest seen at 27 seconds; the median time inside before being noticed, 416 days "
       "then and 14 days now. A defender's usual clocks: 55 days to fix half of the critical flaws once a fix "
       "exists; a mean of 241 days to identify and contain a data breach; more than a month to recover after "
       "ransomware for 34 organizations in 100. The clocks measured here: a site taken down in 5 minutes 54 "
       "seconds, which is faster than the average time to start moving; and a whole site built again in 38 "
       "minutes 12 seconds, which is of the same order as that time and far faster than every usual defender "
       "clock and than the time intruders usually stay.")


def _x(sec, x0, x1):
    return x0 + (math.log10(sec) - LO) / (HI - LO) * (x1 - x0)


def _band(f, y, h, title, x_left, x_right, tone):
    f.rect(x_left, y, x_right - x_left, h, 10, SOFT if tone == "here" else "none", ACC if tone == "here" else (INK if tone == "attack" else LINE),
           2.6 if tone != "defend" else 2, dash="7 5" if tone == "defend" else None)
    f.t(x_left + 16, y + 24, title, 13.5, 700, ACC if tone == "here" else (INK if tone == "attack" else QUIET), ls="1.5")


def _marker(f, x, y, tone, then=False):
    if tone == "attack":
        if then: f.circle(x, y, 8, fill=PAPER, stroke=INK, sw=2, dash="3 3")
        else: f.circle(x, y, 10, fill=INK, stroke="none", sw=0)
    elif tone == "defend":
        f.rect(x - 9, y - 9, 18, 18, 3, PANEL, QUIET, 2.4)
        f.path(f"M{x - 6} {y + 6}L{x + 6} {y - 6}M{x - 6} {y}L{x} {y - 6}M{x} {y + 6}L{x + 6} {y}", stroke=QUIET, sw=1.6)
    else:
        f.circle(x, y, 13, fill=ACC, stroke=INK, sw=2.4)


def _rows(f, rows, y, x0, x1, tone, row_h, label_x, narrow):
    for lines, then, now, extra in rows:
        ry = y + (46 if narrow else row_h / 2)
        if narrow:
            lab = " ".join(lines).replace("from a first foothold", "from foothold")   # the full label does not fit 464 units
            f.t(label_x, y + 8, lab, 14 if len(lab) > 52 else 14.5, 700 if tone == "here" else 600)
        else:
            for k, ln in enumerate(lines):
                f.t(label_x, ry + 5 - (len(lines) - 1) * 9 + k * 18, ln, 15, 700 if tone == "here" else 600)
        f.path(f"M{x0} {ry} H{x1}", stroke=RULE, sw=1.4)
        xn = _x(now[0], x0, x1)
        if then:
            xt = _x(then[0], x0, x1)
            f.path(f"M{xt - 12:.1f} {ry} H{xn + 16:.1f}", stroke=INK, sw=2.2, arrow=True)
            _marker(f, xt, ry, tone, then=True)
            near_end = xt > x1 - 70
            f.t(xt + (12 if near_end else 0), ry - 16, then[1], 12.5, 400, QUIET, "end" if near_end else "middle")
        if extra == "open":
            f.path(f"M{xn + 12:.1f} {ry} H{min(xn + 150, x1 - 6):.1f}", stroke=QUIET, sw=2.2, dash="2 6", arrow=True)
        _marker(f, xn, ry, tone)
        anchor = "start" if (xn < x0 + 40 or (narrow and isinstance(extra, tuple))) else ("end" if xn > x1 - 60 else "middle")
        tx = xn + (-12 if anchor == "end" else 0) if anchor != "start" else xn - 12
        if narrow and anchor == "middle" and tx + len(now[1]) * 3.9 > f.w - 12:   # a long value near the right edge ends at the edge
            tx, anchor = f.w - 14, "end"
        f.t(tx, ry + 30, now[1], 14 if tone != "here" else 16, 700, INK, anchor)
        if isinstance(extra, tuple):
            xe = _x(extra[0], x0, x1)
            f.path(f"M{xe:.1f} {ry - 9} L{xe + 8:.1f} {ry} L{xe:.1f} {ry + 9} L{xe - 8:.1f} {ry} Z", stroke=INK, sw=2, fill=PAPER)
            if narrow: f.t(xe - 10, ry + 29, extra[1].replace("fastest seen", "fastest"), 12.5, 400, QUIET)
            else: f.t(xe - 10, ry - 16, extra[1], 12.5, 400, QUIET)
        y += row_h
    return y


def _axis(f, x0, x1, y_top, y_bot, narrow):
    for sec, long_, short in TICKS:
        x = _x(sec, x0, x1)
        f.path(f"M{x:.1f} {y_top} V{y_bot}", stroke=RULE, sw=1.4, dash="2 5")
        f.t(x, y_top - 8, short if narrow else long_, 13 if narrow else 13.5, 600, QUIET, "middle")
        f.t(x, y_bot + 18, short if narrow else long_, 13 if narrow else 13.5, 600, QUIET, "middle")


# Real cases, each showing one clock. Only what the linked source states; nothing about cause beyond it.
# (when, who as the source names it, what the source states, the clock, [(source label, url)])
CASES = [
    ("2017", "Equifax",
     "A flaw was publicly disclosed on 7 March 2017. Attackers began an attack on 13 May 2017, and it lasted for 76 days, according to the staff report of the U.S. House Committee on Oversight and Government Reform.",
     "undetected for 76 days",
     [("U.S. House Committee on Oversight and Government Reform, December 2018", "https://oversight.house.gov/wp-content/uploads/2018/12/Equifax-Report.pdf")]),
    ("2020", "SolarWinds",
     "Hidden code was put into a file in the company's software updates from February 2020, and a security firm stated that it detected an intrusion in November 2020, according to the U.S. Government Accountability Office.",
     "about nine months from the hidden code to detection",
     [("U.S. Government Accountability Office", "https://www.gao.gov/blog/solarwinds-cyberattack-demands-significant-federal-and-private-sector-response-infographic")]),
    ("2021", "The Log4j flaw",
     "The flaw was disclosed on 9 December 2021. Five days later one network operator observed 400 attempts to use it every second, as the Cyber Safety Review Board reported.",
     "400 attempts a second, five days after disclosure",
     [("Cyber Safety Review Board, 11 July 2022", "https://www.cisa.gov/sites/default/files/publications/CSRB-Report-on-Log4-July-11-2022_508.pdf")]),
    ("2023", "The British Library",
     "A ransomware attack became clear on 28 October 2023. The Library's own review, published on 8 March 2024, says that staff were still working on full restoration.",
     "restoration still under way after four months",
     [("British Library, cyber incident review, 8 March 2024", "https://www.bl.uk/home/british-library-cyber-incident-review-8-march-2024.pdf")]),
    ("September to November 2026", "Maileva, a subsidiary of La Poste",
     "La Poste announced on 14 November 2026 that a cyberattack on Maileva in mid-September led to the theft of the contact details of 22 million people, as franceinfo reported on 15 November.",
     "about two months from the attack to the announcement",
     [("franceinfo, 15 November 2026", "https://www.franceinfo.fr/internet/securite-sur-internet/cyberattaques/maileva-une-filiale-du-groupe-la-poste-victime-d-un-vol-de-donnees-touchant-22-millions-de-personnes_8283335.html")]),
    ("November 2026", "SAP",
     "The company said that it had identified suspicious activity, and that it had found no evidence of unauthorized access to customer business data, as quoted on 27 November 2026. Nothing else is confirmed by the company.",
     "no time has been published",
     [("BleepingComputer, quoting the company, 27 November 2026", "https://www.bleepingcomputer.com/news/security/sap-confirms-security-incident-after-suspicious-github-activity/")]),
]


def cases_html():
    """One line per case under the figure; the sources are in notes()."""
    rows = "\n".join(f'        <li><span class="when">{when}</span><span><b>{who}:</b> {clock}.</span></li>' for when, who, _, clock, _ in CASES)
    return ('    <div class="cases">\n      <h3>The clocks in real cases</h3>\n      <ul>\n' + rows +
            '\n      </ul>\n      <p class="note"><a href="notes/#cases">What each source states</a></p>\n    </div>\n')


def figure_wide():
    f = Fig(1120, 756, ALT, uid="tm")
    lx, x0, x1 = 44, 330, 1076
    _axis(f, x0, x1, 40, 704, False)
    _band(f, 52, 232, "AN ATTACKER'S CLOCKS", 24, 1096, "attack")
    _rows(f, ATTACK, 84, x0, x1, "attack", 64, lx, False)
    _band(f, 296, 232, "A DEFENDER'S CLOCKS, USUALLY", 24, 1096, "defend")
    _rows(f, DEFEND, 328, x0, x1, "defend", 64, lx, False)
    _band(f, 540, 156, "THE CLOCKS MEASURED HERE", 24, 1096, "here")
    _rows(f, HERE, 566, x0, x1, "here", 56, lx, False)
    # legend
    f.circle(44, 742, 7, fill=PAPER, stroke=INK, sw=2, dash="3 3"); f.t(60, 747, "earlier", 13.5, 400, QUIET)
    f.circle(134, 742, 8, fill=INK, stroke="none", sw=0); f.t(150, 747, "now", 13.5, 400, QUIET)
    f.t(1096, 747, "each step on this axis is many times the one before it", 13.5, 400, QUIET, "end", italic=True)
    return f.svg()


def figure_narrow():
    f = Fig(464, 1090, ALT, narrow=True, uid="tmn")
    x0, x1 = 30, 436
    _axis(f, x0, x1, 30, 1040, True)
    _band(f, 42, 350, "AN ATTACKER'S CLOCKS", 6, 458, "attack")
    _rows(f, ATTACK, 82, x0, x1, "attack", 104, 20, True)
    _band(f, 406, 350, "A DEFENDER'S CLOCKS, USUALLY", 6, 458, "defend")
    _rows(f, DEFEND, 446, x0, x1, "defend", 104, 20, True)
    _band(f, 770, 260, "THE CLOCKS MEASURED HERE", 6, 458, "here")
    _rows(f, HERE, 810, x0, x1, "here", 108, 20, True)
    f.circle(20, 1076, 7, fill=PAPER, stroke=INK, sw=2, dash="3 3"); f.t(36, 1081, "earlier", 13.5, 400, QUIET)
    f.circle(110, 1076, 8, fill=INK, stroke="none", sw=0); f.t(126, 1081, "now", 13.5, 400, QUIET)
    return f.svg()


def mark():
    """Two clock hands on one dial: one far ahead of the other."""
    return _mark("timing", "A clock face with a short hand and a long hand, and a mark at the start.",
                 '<circle cx="48" cy="50" r="36" class="mk"/>'
                 '<path d="M48 50V26" class="mk"/>'
                 '<path d="M48 50L66 60" class="mka"/>'
                 '<path d="M40 6H56" class="mk"/>'
                 '<circle cx="48" cy="50" r="5" class="mkfa"/>')


def html():
    s = scene(
        "timing", "The race", "Security is a race of clocks, and a fast rebuild resets it",
        "time to exploit, breakout time, dwell time, mean time to detect, mean time to recover, defender's dilemma",
        "Defense is a race, and the attacker's clocks have moved much further than the defender's.",
        "A site is taken down in about 6 minutes, faster than an intruder's average time to start moving, and built again in under an hour. Other defenses slow the attacker or speed up detection; a fast rebuild resets the race.",
        "You are back on a known clean system sooner than intruders usually stay.",
        [("measured", "a site taken down in 5 min 54 s; a whole site built in 38 min 12 s of machine time")],
        figure_wide() + "\n" + figure_narrow(), mark())
    src = '    <p class="known"><a href="notes/#clocks">Where the numbers come from</a></p>\n'
    return s.replace("  </div>\n</section>", src + cases_html() + "  </div>\n</section>")


def notes():
    src = "\n".join(f'<li><b>{k}:</b> {v} (<a href="{u}">source</a>).</li>' for k, v, u in SOURCES)
    cases = "\n".join(f'<tr><td>{when}</td><td>{who}</td><td>{what}</td><td>' + "; ".join(f'<a href="{u}">{n}</a>' for n, u in srcs) + '</td></tr>'
                      for when, who, what, _, srcs in CASES)
    return f"""<section id="clocks"><h2>The race of clocks: sources</h2>
<p>The clocks measured here are this project's own measurements. Every other value is from a published report, with its year. They measure different populations in different ways, so compare their size, not their last digit.</p>
<p>Why the attacker's clocks moved: systems used to be disconnected, knowledge of a flaw spread slowly, and the tools needed a career expert or a state. Now systems are connected, a flaw is published and automated within days, and capable tools are widely available.</p>
<ul>
{src}
</ul>
<p>Not shown: the time to lock down data and access after an incident. No defensible published number was found.</p>
</section>
<section id="cases"><h2>The clocks in real cases</h2>
<p>Each case is stated as its source states it, with the date of the source. The recent ones are days old, and what is known about them will change.</p>
<table>
<tr><th>When</th><th>Who</th><th>What the source states</th><th>Source</th></tr>
{cases}
</table>
</section>"""
