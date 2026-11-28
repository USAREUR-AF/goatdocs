"""Shared drawing and markup helpers for the scene modules in this directory.

Every figure is fixed-layout SVG placed by hand; colours come only from the page's tokens
(--ink, --quiet, --paper, --panel, --accent, --accent-soft, --on-accent, --rule, --line).
State is shown by line pattern and weight, never by a warning colour."""
import html as _html

INK, QUIET, PAPER, PANEL = "var(--ink)", "var(--quiet)", "var(--paper)", "var(--panel)"
ACC, SOFT, ONACC, RULE, LINE = "var(--accent)", "var(--accent-soft)", "var(--on-accent)", "var(--rule)", "var(--line)"
SANS, MONO = "var(--sans)", "var(--mono)"


def esc(s):
    return _html.escape(str(s), quote=True)


class Fig:
    def __init__(self, w, h, alt, narrow=False, uid="f"):
        self.w, self.h, self.alt, self.narrow, self.uid = w, h, alt, narrow, uid
        self.o = []

    # ---- text ------------------------------------------------------------------------------------
    def t(self, x, y, s, size=15, weight=400, fill=INK, anchor="start", italic=False, mono=False, ls=None):
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        i = ' font-style="italic"' if italic else ""
        f = f' font-family="{MONO}"' if mono else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        wt = f' font-weight="{weight}"' if weight != 400 else ""
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{wt} fill="{fill}"{a}{i}{f}{l}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=15, lead=1.38, **kw):
        for k, s in enumerate(rows):
            self.t(x, y + k * size * lead, s, size, **kw)
        return y + len(rows) * size * lead

    # ---- shapes ----------------------------------------------------------------------------------
    def raw(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, rx=8, fill=PANEL, stroke=INK, sw=2, dash=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{extra}/>')

    def circle(self, x, y, r, fill=PANEL, stroke=INK, sw=2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def path(self, d, stroke=INK, sw=2, fill="none", dash=None, cap="round", arrow=False):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        ar = f' marker-end="url(#{self.uid}-ah)"' if arrow else ""
        self.o.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}" stroke-linejoin="round"{da}{ar}/>')

    def party(self, x, y, r=9, ring=True, tone=ACC):
        if ring:
            self.circle(x, y, r + 6, fill=PAPER, stroke=tone, sw=2)
        self.circle(x, y, r, fill=INK, stroke="none", sw=0)

    def lock(self, x, y, s=1.0, tone=INK, bg=PAPER):
        self.o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({s})"><circle r="14" fill="{bg}" stroke="{tone}" stroke-width="2.2"/>'
                      f'<rect x="-5.5" y="-1.5" width="11" height="9" rx="2" fill="{tone}"/>'
                      f'<path d="M-3.4 -1.5 v-3 a3.4 3.4 0 0 1 6.8 0 v3" fill="none" stroke="{tone}" stroke-width="2"/></g>')

    def key(self, x, y, s=1.0, tone=INK):
        """A small key, bow at the left, bit at the right."""
        self.o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({s})" fill="none" stroke="{tone}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
                      f'<circle cx="-9" cy="0" r="5.5"/><path d="M-3.5 0H13M8 0v5M12.5 0v4"/></g>')

    def num(self, x, y, n, r=15):
        self.circle(x, y, r, fill=INK, stroke="none", sw=0)
        self.t(x, y + r * 0.37, n, round(r * 1.02), 700, PAPER, "middle")

    def badge(self, x, y, word):
        """A status word. in use: solid; built: soft fill; designed: dashed outline. Returns its width."""
        w = len(word) * 7.6 + 16
        if word == "in use":
            self.rect(x, y - 13, w, 19, 3, INK, INK, 1.4)
            fill = PAPER
        elif word == "designed":
            self.rect(x, y - 13, w, 19, 3, "none", INK, 1.4, dash="3 3")
            fill = INK
        else:
            self.rect(x, y - 13, w, 19, 3, SOFT, ACC, 1.4)
            fill = INK
        self.t(x + w / 2, y + 1, word.upper(), 11.5, 700, fill, "middle", mono=True, ls="0.6")
        return w

    def svg(self):
        cls = "viz narrow" if self.narrow else "viz wide"
        defs = (f'<defs><marker id="{self.uid}-ah" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="12" refX="11" refY="6" orient="auto">'
                f'<path d="M1 1 L12 6 L1 11 z" fill="{INK}"/></marker></defs>')
        return (f'<svg class="{cls}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.alt)}" font-family="{SANS}">\n'
                + defs + "\n" + "\n".join(self.o) + "\n</svg>")


def mark(name, label, body):
    return f'<svg class="mark mark-{name}" viewBox="0 0 96 96" role="img" aria-label="{esc(label)}">{body}</svg>'


def scene(sid, eyebrow, title, known, usually, here, you, status, figure_html, mark_html, full=True):
    """One scene's section, in the page's own classes. status: [(word, text)]."""
    cls = {"in use": "s-inuse", "built": "s-built", "designed": "s-designed", "measured": "s-measured"}
    rows = "\n".join(f'        <li><span class="status {cls[w]}">{w}</span><span>{t}</span></li>' for w, t in status)
    say = f'''      <div class="mk-anchor" aria-hidden="true">{mark_html}</div>
      <p class="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p class="known"><i>Known as: {known}</i></p>'''
    if full:
        return f'''<section class="scene center" id="{sid}">
  <div class="wrap">
    <div class="say wide">
{say}
      <dl class="cols">
        <div><dt>Usually</dt><dd class="usual">{usually}</dd></div>
        <div><dt>Here</dt><dd class="here">{here}</dd></div>
        <div><dt>For you</dt><dd class="you">{you}</dd></div>
      </dl>
      <ul class="ev">
{rows}
      </ul>
    </div>
    <figure class="full"><div class="frame">{figure_html}</div></figure>
  </div>
</section>'''
    return f'''<section class="scene" id="{sid}">
  <div class="wrap">
    <div class="say">
{say}
      <dl>
        <dt>Usually</dt><dd class="usual">{usually}</dd>
        <dt>Here</dt><dd class="here">{here}</dd>
        <dt>For you</dt><dd class="you">{you}</dd>
      </dl>
      <ul class="ev">
{rows}
      </ul>
    </div>
    <figure><div class="frame">{figure_html}</div></figure>
  </div>
</section>'''


def _openlock(self, x, y, s=1.0, tone=INK, bg=PAPER):
    """A lock with its shackle lifted: the traffic is opened here."""
    self.o.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({s})"><circle r="14" fill="{bg}" stroke="{tone}" stroke-width="2.2" stroke-dasharray="3 3"/>'
                  f'<rect x="-5.5" y="-0.5" width="11" height="9" rx="2" fill="none" stroke="{tone}" stroke-width="2"/>'
                  f'<path d="M-3.4 -0.5 v-4 a3.4 3.4 0 0 1 6.8 0" fill="none" stroke="{tone}" stroke-width="2"/></g>')


Fig.openlock = _openlock
