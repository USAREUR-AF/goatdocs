# Design system — GOAT-Net visual + verbal language

**Status:** Proposed 2026-05-25. Phase A install-as-canon in PR (this change-set); Phases B-G gate per-surface.
**Source-of-truth:** [`docs/design-system/`](../design-system/) — bundle exported from the design tool; provenance in `_origin/`.
**Track:** `docs/project/active-work/tracks/design-system-install-as-canon.yaml`.
**Composes with:** [ADR 0859 easy rollback](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0859-easy-rollback-engineering-principle.md) (per-surface image-SHA rollback ledger covers each migration PR independently).

## What this is

A documented visual + verbal language for every artifact the project renders as a UI — operator dashboards, briefing decks, status pages, vendor portals, game-of-the-week. Dark-tactical default, light paper-warm as opt-in via `data-theme="light"`, sharp corners, monospace for anything the machine considers a value, a single phosphor-green accent used sparingly. Voice is matter-of-fact and technical — no exclamation points, no emoji, no marketing warmth.

The bundle at [`docs/design-system/`](../design-system/) carries everything needed to land it: tokens (`colors_and_type.css`), components (`components.css`), the original brand mark and the diagram library, two UI kits (operator console catalog + brief slide deck), a full preview-card library covering type / colors / spacing / components / brand, and a [`SKILL.md`](../design-system/SKILL.md) so a Claude Code session can invoke the design system as a skill when authoring new artifacts. The bundle's own [`README.md`](../design-system/README.md) is the canonical reference — this doc is the *project's* explainer for how the bundle lands inside the repo and how consumers adopt it.

## Why this is one thing, not many

Today every consumer surface in the repo carries its own bespoke CSS. brief and dataflows have parallel-but-divergent stylesheets that started identical and drifted. goat-zenoh-portal carries the most pages and has its own design language (theme picker, three-segment selector, hljs swap). panoscope has a tactical-dark aesthetic that visually rhymes with the design system but was authored independently. isitup and demogame are each their own world.

The cost of N bespoke surfaces is paid in two places: (1) every new surface (flashlight, stethoscope, nova-lan, future partner dashboards) re-authors the same visual decisions and either rhymes by accident or drifts by accident; (2) every visual change to one surface has to be hand-replicated to the rest if we want them to stay coherent. The design system collapses that — one set of tokens, one component vocabulary, one voice, one mark.

## Where it lives

Source-of-truth at [`docs/design-system/`](../design-system/). Treated as documentation canon, sibling to `docs/design/` and `docs/adr/`. The `_origin/` subdirectory preserves the handoff README + chat transcript from the design tool so future readers can trace provenance.

Top-level layout:

```
docs/design-system/
├── README.md                  # canonical reference — read first
├── SKILL.md                   # invoke from Claude Code as a skill
├── colors_and_type.css        # tokens — import this
├── components.css             # reusable component classes
├── assets/                    # goat-logo.svg + alternates + diagram library
├── preview/                   # design-system preview cards (type / color / spacing / components / brand)
├── ui_kits/
│   ├── console/               # operator catalog kit (peer drawer, side nav, command palette)
│   └── brief/                 # slide-deck kit (6 slide patterns + deck-stage shell)
├── raw/                       # source documents the system was extracted from
└── _origin/                   # handoff provenance (design-tool README + chat)
```

## How consumers receive the CSS bytes

**Dockerfile COPY from repo-root build context.** Each consumer's image build copies the relevant design-system CSS files into the served static directory at image-build time. Concretely:

- Build context = repo root (each surface's `docker-compose.yml` / build invocation passes `context: ../..` or equivalent so the Dockerfile can reach `docs/design-system/`).
- Dockerfile carries `COPY docs/design-system/colors_and_type.css /usr/share/<service>/static/design-system/` plus any other files the consumer pulls in.
- Each consumer's HTML `<link rel="stylesheet" href="/design-system/colors_and_type.css">` (path under the served root).

This keeps the design system as a single source of truth — every consumer pulls the same bytes at build time — and fits the existing image-SHA pin model. A design-system change rebuilds every consumer's image on the next CI run; the per-surface image-SHA rollback ledger ([ADR 0859](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0859-easy-rollback-engineering-principle.md)) lets any surface roll back independently if a design-system change breaks it visually.

Alternatives considered and rejected: Ansible role rendering the CSS at deploy time (decouples build context but adds a deploy-time step and breaks the image-is-immutable invariant); vendor a copy into each surface's static dir (simplest immediate diff but drifts over time, defeats the purpose).

## Per-surface adoption plan

Phase A (this PR) lands the bundle as canon with **zero consumer changes** — risk floor. Subsequent PRs migrate one surface at a time, additively. Each surface PR:

1. **Imports tokens first** — adds the design-system CSS `<link>` alongside the existing stylesheet, no class swaps yet. Visual delta is the rendered token differences (background, text colors, accent).
2. **Migrates components in batches** — replaces bespoke classes with design-system component classes (`.t-h1`, `.t-mono`, `.t-label`, semantic `--bg-card` / `--fg-accent` / `--border`). One batch per commit; PR can carry multiple commits.
3. **Captures visual baseline at the start** — a `before.png` (and one per page for multi-page consumers) checked into the PR. Review = "do these screenshots match the design intent?" instead of "do you trust this diff?"
4. **Deletes legacy CSS only when visually verified** — last commit of the migration PR. Until then both stylesheets coexist; rollback is one image-SHA revert.

Fit-ordered sequence (highest confidence first):

| Phase | Surface | Notes |
|---|---|---|
| **B** | `ops/serve/brief/` | Direct match to the bundle's [`ui_kits/brief/`](../design-system/ui_kits/brief/). Closest surface — more "swap stylesheet" than redesign. Brief's deck-stage color scheme override (paper-dark with `--accent #93c0e0`) lifts verbatim. |
| **C** | [`ops/serve/dataflows/`](https://github.com/usareur-af/goatstuff/tree/main/ops/serve/dataflows) | Sibling of brief. Lift-and-shift the Phase B migration. |
| **D** | [`ops/goat-zenoh-portal/web/static/`](https://github.com/usareur-af/goatcore/tree/main/ops/goat-zenoh-portal/web/static) | 10+ static HTML pages. Biggest reach. First portal PR is **tokens-only** (semantic CSS vars, no component class swaps); per-page component migration follows as separate PRs. Theme picker behavior preserved — design system ships a parallel `data-theme` mechanism. |
| **E** | [`ops/panoscope/frontend/`](https://github.com/usareur-af/goatstuff/tree/main/ops/panoscope/frontend) | Already dark-tactical, mostly token-alignment. Custom D3/HUD components (search overlay, lasso-select, side panel) stay untouched. |
| **F** | `ops/status/` and [`ops/ansible/roles/isitup/`](https://github.com/usareur-af/goatcore/tree/main/ops/ansible/roles/isitup) | Thin status page. Low risk. |
| **G** | `ops/serve/demogame/` | Canvas game with almost no chrome. Lowest priority; what little exists (title screen, leaderboard) gets the token import. |

Born-in-the-design-system: [flashlight (Block 89)](https://github.com/usareur-af/goatstuff/blob/main/docs/design/flashlight.md) and [stethoscope (Block 90)](https://github.com/usareur-af/goatstuff/blob/main/docs/design/stethoscope.md) adopt the design system as part of their own bring-up. No retroactive migration needed.

## Voice + casing — non-visual canon

The design system carries content fundamentals as load-bearing as the tokens — the project's voice is the most distinctive thing about it and survives even when the CSS doesn't. Verbatim from the bundle's README:

- **Matter-of-fact, technical, specific about failures.** Where another project would say "robust," this one says "Block 22 is designed, not yet shipped."
- **No marketing warmth.** No "we're excited to," no "delighted," no "world-class," no "seamless."
- **No exclamation points.** Not in headlines, not in CTAs, not in error messages.
- **No emoji.** Two exceptions repo-wide: a `⚠` in a migration banner and a section pin in the manifesto. If you reach for an emoji, write a sentence instead.
- **Sentence case** for headlines. Not Title Case, not ALL CAPS.
- **UPPERCASE MONO** for system labels rendered in monospace (`STATUS`, `PEER`, `BLOCK 22`).
- **First-person plural for the project, second-person for the reader.**

A draft that reads like marketing is rewritten as a fact. This applies to docs prose, runbook headlines, ADR titles, brief-deck copy, and every consumer surface's UI text — not just the CSS-bearing artifacts.

## Caveats from the handoff

Three flagged substitutions or limitations the bundle's authors recorded that carry forward into this install:

1. **Geist + Geist Mono are CDN-loaded** from Google Fonts at runtime. No `.ttf` files are checked in. If a surface needs offline rendering (likely for nova-lan or any air-gapped install), the fonts need to be self-hosted. Tracking as a Phase D follow-on against the portal (first surface big enough to feel the CDN dependency).
2. **Lucide icons are a flagged substitution** for UI icons (status dots, menu, copy, link, terminal, lock, server, network). Stroke width 1.5, served from `https://unpkg.com/lucide@latest`. The source repo did not specify an icon library; if the project standardizes on a different one later, swap the CDN reference.
3. **The Zenoh brief's paper-warm aesthetic is intentionally not adopted** as a sibling mode. The light-mode that ships in the design system is its own simplified paper palette; the brief deck carries a dedicated paper-dark scheme as a `<deck-stage>` override (see [`ui_kits/brief/`](../design-system/ui_kits/brief/)) and that is the only place the original brief aesthetic survives.

## What this doc does not do

Does not specify per-surface migration details — those live in each Phase B-G track yaml + PR description. Does not pick winners between bespoke per-surface motifs and the design system — that's a per-surface judgment made at migration time, with the design system as the default and any deliberate deviation called out in the migration PR. Does not address mobile + offline + bandwidth-constrained delivery — those are inherited by the [minimalism-under-network-constraints doctrine (ADR 0861)](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0861-minimalism-under-network-constraints.md) at the time a surface adopts both.
