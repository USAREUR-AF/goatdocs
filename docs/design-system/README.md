# GOAT-Net Design System

> An opinionated open-source data substrate for sovereign edge deployments.
> This is the design system that dresses it.

GOAT-Net — Geo-distributed Open Architecture Transformation Network — is the
software-defined tactical data fabric assembled from Netbird (identity-based
WireGuard mesh), Eclipse Zenoh (partition-tolerant pub/sub), an offline-CA
enrollment chain, and phoenix-native peer discipline.

This design system describes the **visual + verbal language** the project uses
when it shows up as an artifact — a brief, a runbook, a status console, a
landing page, a slide. It is **not** the product UI itself; the product surface
is an operator's dashboard, a CLI, and a catalog. This system makes design
artifacts for the project read as one thing.

## Sources

Everything here was derived from material the user attached. If you have access,
read these directly — they're the ground truth and we're downstream of them.

- **The project source repository.**
  Source of the project's voice (root `README.md`, `docs/manifesto/`, `docs/briefs/`),
  the green brand mark (`docs/assets/goat-logo.svg` → `assets/goat-logo.svg`), and
  the diagram library (`docs/briefs/assets/zenoh-in-goat-net/` → `assets/diagrams/`).
- **`raw/zenoh-brief.md`** — the prose tour of how GOAT-Net uses Zenoh. The
  best single sample of the voice.
- **`raw/zenoh-brief.html`** — a 12-slide presentation built around that brief.
  Original is paper-warm + serif; this design system **does not** carry that
  treatment forward. The dark/tactical aesthetic in this kit was specified by
  the operator and overrides the brief's softer print look.
- **`raw/manifesto.md`** — short summary of the manifesto series. Position
  papers in the source repo at `docs/manifesto/`.

The repo has a lot more — ADRs (`docs/adr/`), runbooks (`docs/operations/`),
findings (`docs/findings/`), and a research backlog (`docs/research/`). If you
need to design something that touches a specific subsystem, go read the
corresponding ADR before designing. The decisions are dense and the language is
specific; the design will be better for matching them.

## Manifest

| File | Role |
|---|---|
| `README.md` | This file. Read first. |
| `SKILL.md` | Cross-compatible skill entry point for Agent Skills / Claude Code. |
| `colors_and_type.css` | All design tokens — primitives + semantic vars + base typography. Import this. |
| `components.css` | Reusable component classes — buttons, chips, inputs, tables, banners, etc. |
| `assets/goat-logo.svg` | The original goat-head mark from the repo (single-path, `#20964f`). |
| `assets/goat-mark.svg` | **Working default mark** — geometric horns + wedge, uses `currentColor`. |
| `assets/goat-mark-curve.svg` | Alternative mark — spiral horns, monoline. |
| `assets/goat-mark-solid.svg` | Alternative mark — filled tactical badge. |
| `assets/diagrams/*.svg` | Stock illustrative diagrams from the Zenoh brief. |
| `preview/*.html` | Design-system tab cards: type, color, spacing, components, brand. |
| `ui_kits/console/` | Operator console UI kit — catalog, peer drawer, command palette. |
| `ui_kits/brief/` | Brief / deck UI kit — 6 slide-type patterns, deck-stage shell. |
| `raw/` | Source documents this system was extracted from. |

---

## CONTENT FUNDAMENTALS

The voice is the single most distinctive thing about this project. Match it
before you match a color.

### Posture

- **Matter-of-fact, technical, specific about failures.**
- **No marketing warmth.** No "we're excited to," no "delighted," no
  "world-class," no "seamless." When something is good, the writing lets
  the reader notice — it doesn't announce.
- **No exclamation points.** Not in headlines, not in CTAs, not in error
  messages. None.
- **No emoji.** Two exceptions in the source: a `⚠` in a migration banner and
  a section pin in the manifesto. If you reach for an emoji, write a sentence
  instead.
- **Acronyms before flourish.** STUN, NAT, PACE, ACME, CGNAT, ML-KEM. Define
  them once in a glossary, then use them straight. The audience knows them
  or will learn.
- **First-person plural for the project, second-person for the reader.**
  *"We keep the old names in these docs so the history still reads."* / *"If you already have a local clone and active work in flight,
  hold your changes locally."*

### Casing

- **Sentence case** for headlines and titles. Not Title Case, not ALL CAPS.
  *"Why splitting things up matters"* — not *"Why Splitting Things Up
  Matters."*
- **UPPERCASE** is reserved for system labels rendered in monospace (e.g.
  `STATUS`, `PEER`, `BLOCK 22`). It signals "this is a tag the machine
  knows," not emphasis.
- **Block-N** convention for in-flight work. Block 22, Block 30, Wave 33.
  When you reference one, it usually links to the implementation plan.

### Sentence shapes

- **Lead with the position, not the context.** From the manifesto authoring
  rules verbatim — and it generalizes. State the claim, then defend it.
- **Allow the long sentence.** The brief writing is dense, with clauses that
  carry conditions: *"Mesh-internal services live at `*.mesh.example`.
  The records resolve only inside the mesh — Cloudflare's public zone holds
  no `A`/`AAAA` records for service hostnames."* Don't shorten by removing
  the qualifying clause.
- **Em-dash is fine; semicolons are common.** Both connect related thoughts
  without ceremony.
- **Numbers stay numerals when they are technical.** "10 systems → 45
  conversations." Spell out only in fully prose passages.

### A few canonical examples

> "If the internet goes down, peers keep talking."

> "A vendor-owned bus is a gilded cage — not the pattern."

> "Status: pre-1.0, pre-tagged-release, in rapid single-contributor
> development."

> "Phoenix-native: peers should rebuild themselves from declarative
> supply-chain artifacts; persistent identity belongs to the operator,
> not the peer."

If your draft reads like marketing, rewrite the sentence as a fact.

---

## VISUAL FOUNDATIONS

The aesthetic is **tactical-console**: near-black backgrounds, a single
phosphor-green accent used sparingly, monospace for anything the machine
considers a value, and sharp corners throughout. The reference frame is a
night-watch terminal, not a SaaS dashboard.

### Two modes

The system ships **dark** (default) and **light** (paper-warm) modes,
matching the two-mode aesthetic of the Zenoh brief
(`raw/zenoh-brief.html`). Toggle via the `data-theme` attribute:

```html
<html data-theme="light">   <!-- paper-warm -->
<html data-theme="dark">    <!-- tactical default -->
<html>                       <!-- follows OS preference, defaults to dark -->
```

The console UI kit ships a `☾ DARK / ☀ LIGHT` toggle in the top bar.
Pages without a toggle default to dark and follow `prefers-color-scheme`
when `data-theme` is unset.

**Only backgrounds, foregrounds, borders, and status-tints shift between
modes.** The brand-green palette (`--c-green-mid` `#20964f` and its hi/flare
derivatives) stays constant; the spacing scale, shape tokens, and timing
tokens do not change.

### Color

- **Two palettes, one accent.**
  - **Dark mode** (default): primary surface `#06090a` (`--bg-page`),
    stepping up through three cooler-than-black greys to `#1e272c` for
    raised cards. No pure black; no white.
  - **Light mode**: primary surface `#fbf8f3` (paper from the Zenoh brief),
    stepping down through `#f0eade` (paper-soft) to `#ddd0b1` for wells.
    Borders use `#c8bfb0` (brief rule). Text is `#1f1d1a` (brief ink).
- **One accent — green.** Brand mark `#20964f` (matches
  `assets/goat-logo.svg`). Two derivatives carry weight in dark mode:
  `#34d97e` (active) and `#6cf5a8` (peak / links). In light mode the
  accent collapses to the brand `#20964f` for contrast and the glow
  effects dim by ~30%. The accent **glows** via a soft drop-shadow
  approximation (`--glow-accent`) on focus rings, live counters, the
  cursor in a terminal. Do not flood with green — it should feel precious.
- **Status colors are desaturated.** Amber for warn, red for fail, blue
  for info, violet for "experimental / pre-1.0". Each pairs a deep tint
  (dark) or a wash (light) with a deeper foreground for contrast.

### Typography

- **Geist + Geist Mono.** Sans for everything human-reading, mono for
  anything the machine knows (IDs, IPs, peer names, durations, command
  output, ADR numbers).
- **No serif.** The original Zenoh brief uses Charter and that aesthetic
  is **not** part of this system going forward.
- **UPPERCASE MONO** is reserved for labels — small, tracked +6%, never
  larger than 13px. Decorative all-caps in sans is forbidden.
- **No display-italic.** The matter-of-fact voice does not lean into things.
- **Tabular numerals everywhere.** Numbers in tables and dashboards must
  align vertically; `font-variant-numeric: tabular-nums` is on every
  mono token.

### Backgrounds

- **No photography.** No stock imagery, no hero shots, no people. The
  product is a substrate; rendering its visuals as a sunset is a
  category error.
- **No gradients as decoration.** A `--glow-accent` is a focused emission,
  not a fill. The only large gradient we ship is a near-imperceptible
  vertical fade on page backgrounds to mark depth.
- **Scanlines and a 24px grid** are available as overlays
  (`--scanline`, `--grid-overlay`) for hero surfaces and live-data
  panels. Use one or the other, not both. Both should sit at low
  opacity — the moment they're noticeable, they're too strong.
- **Diagrams from the brief library** (`assets/diagrams/*.svg`) are
  acceptable as full-bleed illustration, recolored to system tokens.

### Borders, corners, shadows

- **Sharp corners are the default.** `border-radius: 0` for cards,
  panels, sections. `2px` (`--r-1`) is acceptable for inputs and
  buttons. **Pill (`999px`) is allowed only for status chips.**
- **Borders are 1px hairlines.** `--c-line` for ambient, `--c-line-2`
  for visible separation, `--c-line-3` for focus. No double borders;
  no inset borders.
- **No drop shadows in the casual sense.** Dark UI doesn't need them.
  The only `box-shadow` we use is the green focus/glow ring
  (`--glow-accent`, `--glow-soft`, `--glow-text`).

### Hover, press, focus

- **Hover** raises surface lightness by one step (e.g. `--bg-card` →
  `--bg-hover`). It does not change color hue. Links flip to
  `--accent-flare` and pick up `--glow-text`.
- **Press** uses `--bg-active` plus a 1px inset border in
  `--c-line-2`. No scale or shrink — that's a consumer-app gesture.
- **Focus** is always the green ring: `box-shadow: var(--glow-accent)`.
  Visible at all times for keyboard users; never removed.
- **Disabled** drops to `--fg-disabled` text on `--bg-card` with no
  hover response.

### Motion

- **Linear and short.** `--dur-fast` (90ms) for state changes,
  `--dur-base` (140ms) for surfaces, `--dur-slow` (240ms) for entry
  of new panels. Ease is a near-linear `cubic-bezier(0.2, 0, 0.2, 1)`.
- **No bounce, no spring, no overshoot.** This isn't a consumer app.
- **Cursor blink** at 1.0s is acceptable on terminal-like surfaces.
- **Data updates flash green for one beat** then settle to default.
  A "tick" on a live counter — barely noticeable, never strobing.
- **No entrance animations on page load** beyond a 90ms fade-in.

### Transparency + blur

- **Used only for modals and overlays.** Page-level transparency is a
  marketing aesthetic and doesn't belong here.
- **Backdrop blur** is fine on a focused dialog (8–12px), against a
  dimmed (`rgba(0,0,0,0.6)`) scrim.
- **Inline transparency** for ambient state (e.g. dim a peer that
  hasn't reported in 5s to 50% opacity).

### Cards

- Flat — `--bg-card` (`#161e22`) on a `--bg-panel` (`#11171a`) page.
- 1px `--c-line` border. Sharp corners.
- Generous internal padding (`--s-6` / 24px minimum).
- Optional 1px top-edge `--accent` strip when the card represents
  a primary action surface or "live" data. Not on every card.
- **Never:** colored left border with everything else neutral. That's
  a SaaS card and it does not appear here.

### Layout rules

- **24-column grid at 1280px and above; 12 at 960; 4 at mobile.**
  Gutters at `--s-6` (24px), margins at `--s-7` (32px).
- **Top nav is fixed**, 56px tall, hairline `--c-line` underline.
  Background `--bg-surface` with no transparency.
- **Sticky section anchors** for long-form docs (the project's
  natural rhythm is the ADR/runbook page).
- **Footers are minimal:** repo link, license badge, build SHA.

### Imagery

- The diagrams in `assets/diagrams/` are the closest the system gets
  to imagery. They're line-drawings in `currentColor` so they tint to
  whatever surface they sit on.
- **No round avatars.** Peer identity is a fingerprint (mono), not a
  face.
- **No stock photography**, ever. If you find yourself wanting a
  photo, you have not done enough with type.

---

## ICONOGRAPHY

The brand mark is `assets/goat-logo.svg` — the original goat-head from the
source repo. Single path, filled `#20964f`. This is what every artifact in
this system uses, in the console top bar, on the brief deck cover, and on
any chrome that carries identity.

The wordmark is **GOAT-Net** — uppercase GOAT, hyphen, capitalized Net.
Never `goat·net`, `GOATnet`, `Goat-Net`, or `Goat Net`.

> Three minimalist alternates were drafted during system bring-up and live
> at `assets/goat-mark.svg`, `assets/goat-mark-curve.svg`, and
> `assets/goat-mark-solid.svg`. They are not part of the active mark set
> and should not be used in production artifacts.

Other iconography decisions:

1. **The mark.** `assets/goat-logo.svg` (option A) is the default
   mark. It is a single path filled `#20964f`. Use it at 24–96px in UI
   chrome and full-width on landing surfaces. **Do not recolor** outside
   `--c-green-mid`, `--c-green-hi`, or `--c-fog-0` (mono knockout).
   Alternates B/C/D in `assets/` are available for niche contexts.
2. **UI icons → Lucide.** For everything functional (status dots,
   menu, copy, link, terminal, lock, server, network) this system
   uses [Lucide](https://lucide.dev) at stroke width `1.5`, served
   from CDN: `https://unpkg.com/lucide@latest`. This is a **flagged
   substitution** — the source repo does not specify an icon library;
   Lucide was chosen for its thin tactical line weight and
   permissive license. If the project standardizes on a different
   library later, swap the CDN reference.
3. **Diagrams → in-house library.** The Zenoh brief assets in
   `assets/diagrams/` are the in-house illustration style: thin
   strokes, no fills, captions in mono. When designing a new
   diagram, match this style; do not introduce a new illustration
   system.
4. **Emoji and unicode glyphs.** Forbidden in product UI. Acceptable
   in a single banner-warning context (`⚠`) when there is no other
   way to mark danger inline in a markdown stream. Never elsewhere.
5. **Status dots, not icons.** For live state (`online`, `degraded`,
   `offline`, `enrolling`), prefer a 6–8px colored dot with a mono
   label beside it over a glyph. The dot uses the corresponding
   `--status-*-fg` color and `--glow-text` if the state is "live".

---

## Working with this system

1. Import `colors_and_type.css` at the top of any HTML file you author.
2. Reach for the semantic tokens (`--bg-card`, `--fg-accent`,
   `--border`) not the primitives.
3. Use the typography classes (`.t-h1`, `.t-mono`, `.t-label`, `.t-eyebrow`)
   directly, or copy their rules into component CSS.
4. Match the voice. If your draft has an exclamation point or the word
   "seamless," delete and rewrite.
5. When uncertain about a treatment, open the source repo and find the
   analogous surface (a runbook section, an ADR, a brief slide). Match
   it.

---

## Caveats

- **The codebase has no UI to copy from.** This is a backend project — Rust
  crates, Go agents, Ansible playbooks, Terraform. There is no React app,
  no Figma, no marketing site checked in. The UI kits in this system are
  therefore **opinionated reconstructions** of surfaces the project
  *would* have if it had them (operator catalog, brief layout). Treat
  them as proposals, not recoveries.
- **Fonts are CDN-loaded.** Geist + Geist Mono come from Google Fonts at
  runtime. No `.ttf` files are checked in. If you need offline rendering,
  download and self-host.
- **Lucide is a substitution.** See ICONOGRAPHY above.
- **The Zenoh brief uses a paper-warm aesthetic** that is intentionally
  not adopted here. If the operator wants a paper variant for print
  materials, that's a sibling system — not a fork of this one.
