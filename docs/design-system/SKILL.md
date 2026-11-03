---
name: goat-net-design
description: Use this skill to generate well-branded interfaces and assets for GOAT-Net (Geo-distributed Open Architecture Transformation Network), the software-defined tactical data fabric. The system covers dark tactical UI, console screens, briefs, and operator dashboards. Tone is matter-of-fact and technical — specific about failure, no marketing warmth, no exclamation points.
user-invocable: true
---

# GOAT-Net Design Skill

You are designing for **GOAT-Net** — an opinionated open-source data substrate
for sovereign edge deployments. The product is a software-defined tactical
data fabric assembled from Netbird (identity-based WireGuard mesh), Eclipse
Zenoh (partition-tolerant pub/sub), and an offline-CA enrollment chain. It
runs at the edge, on commodity hardware, with the management plane silent on
the public internet by design.

## How to use this skill

1. **Read `README.md`** in this skill folder first. It contains everything:
   product context, content fundamentals, visual foundations, iconography.
2. **Look at `colors_and_type.css` and `components.css`** for tokens and
   component classes. Reach for the semantic tokens (`--bg-card`,
   `--fg-accent`, `--accent`, `--border`) not the primitives.
3. **Browse `preview/*.html`** to see how each token is meant to look in
   isolation.
4. **Look at the `ui_kits/`** for full reference surfaces:
   - `ui_kits/console/` — operator console (catalog + peer drawer)
   - `ui_kits/brief/` — slide-deck shell with 6 slide-type patterns
5. **Look at `assets/`** for the goat marks and the in-house diagram
   library extracted from the source repo.

## When creating visual artifacts

- For **slides/decks/briefs**, copy `ui_kits/brief/` as the starting point.
  Its slide-type patterns (`slide--title`, `slide--section`, `slide--two-col`,
  `slide--stat`, `slide--quote`, `slide--code`) cover most of what briefs
  in this voice need. Use `deck-stage.js` for the shell.
- For **operator surfaces**, copy `ui_kits/console/` as the starting
  point. The components there are small, modular, and reusable.
- For **standalone pages**, import `colors_and_type.css` and
  `components.css` at the top, then build from `.t-*` typography classes
  and `.btn` / `.chip` / `.card` component classes.
- **Copy assets out** when authoring an artifact — don't link across
  projects. Put copied marks under `assets/` in the output project.

## Voice — the most distinctive part

- **Matter-of-fact, technical, specific about failures.**
- **No marketing warmth.** No "we're excited to," "seamless," or
  "world-class."
- **No exclamation points.** Anywhere.
- **No emoji** in product surfaces. Exception: `⚠` in markdown migration
  banners only.
- **Sentence case** for titles and headlines. UPPERCASE-MONO is reserved
  for system labels (`STATUS`, `PEER`, `BLOCK 22`).
- **Use technical specifics:** acronyms (STUN, CGNAT, ML-KEM), durations
  ("90d expiry"), version numbers ("Block 22").

## Visual one-liner

Near-black backgrounds. One glowing tactical-green accent
(`#34d97e`, derived from the brand `#20964f`). Sharp corners everywhere
except status chips. Monospace for any data the machine knows. No drop
shadows, no gradients-as-decoration, no photography, no rounded-corner
cards with a colored left strip.

## If the user invokes this skill without other guidance

Ask them:
1. What are they making — slide, dashboard, landing page, runbook?
2. What surface size — 1280×720, 1920×1080, fluid?
3. Production code or a throwaway HTML mock?

Then act as an expert designer in the GOAT-Net language and output an HTML
artifact (or production code, if asked) that matches this system.

## Production vs prototype

- For **prototypes/mocks**, copy assets and inline the CSS as needed.
  Single-file HTML is fine.
- For **production**, this skill folder is a design reference — pull
  tokens, type, and component patterns into the actual codebase rather
  than copying these files verbatim.

## Sources you can read further

If you have access (the repo is private and these are pinned URLs):

- <https://github.com/usareur-af/goatcore>
- `raw/zenoh-brief.md` in this skill — the best single sample of the
  voice
- `raw/manifesto.md` in this skill — manifesto framing
