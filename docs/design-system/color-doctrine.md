# Color and emphasis doctrine

**Status: proposed.** Every rule on this page is a proposal under review. Nothing here is adopted, and no surface has been changed to follow it. Two decisions are open and are listed first.

Each color in a goat interface carries one meaning, and the meaning matches what an operator already expects: green is good, amber is degraded, red is bad or dangerous, blue is waiting. A status is always shown as a shape and a word as well as a color, opacity marks only things that are not relevant in the current state, and the status of the thing being watched is the strongest element on the screen.

The request this answers, in the operator's words:

> "the color schemes are not intuitive here. it should be more thoughtful. opacity should be rare and indicate relevance in current context. and colors should match functionality and status typical expectations. ... we need some doctrine on this in the design system for all goat work. I'm surprised that it is so haphazard"

The page that prompted it was a field link-status page. One blue was used for the selected tab, for the link-state badge (`HANDSHAKING`) and for every action button. Every label was dim grey. A section of actions that change the remote device was marked only by a dashed border.

## Open decisions

### Decision 1: does a live operator interface use red and amber for status?

An existing house rule for diagrams, figures, slides and briefs rests on the operator's words "red has a very specific meaning in mil data flow and networking diagrams it means either secret or enemy". It also excludes orange, yellow and purple, which read as classification colors, and shows status by grey tone, line pattern and weight. The operator's words above ask for colors that "match functionality and status typical expectations". The two cannot both govern a live status screen.

| | Option A: status palette in live interfaces | Option B: grey patterns everywhere |
|---|---|---|
| Live operator interfaces (consoles, status pages, dashboards) | Use green / amber / red / blue for status, each paired with a distinct shape and a word | Status by grey tone, line pattern and weight, as in diagrams; green only for good |
| Diagrams, figures, slides, briefs | Keep the no-red rule unchanged | Keep the no-red rule unchanged |
| What an operator reads at a glance | The conventional reading: red means bad, amber means degraded | Must read the shape or word; color does not separate degraded from bad |
| Risk | Red in a live interface could be read as a classification or hostile marking. Mitigated by never using red as an area fill, a banner or a full-width bar: red appears only inside a status badge with its cross shape and word, or on a dangerous-action button with its verb | A degraded link and a lost link look alike from across a room. This is the condition the operator called "not intuitive" |
| Token values | The table in [Color roles and tokens](#color-roles-and-tokens) as written | `--status-degraded` and `--status-bad` become grey patterns (hatched and solid inverse); all other tokens unchanged |

Purple (violet) is retired under both options: it reads as a classification color and it is not a status (see rule 7).

### Decision 2: does green stay the color of the primary action?

The current design system ([README.md](README.md), section Color) names green as the one accent and uses it for the brand mark, the primary button, links, the focus ring, eyebrow labels and the "ok" status. One meaning per color (rule 1) cannot hold while green means both "press this" and "this is good".

| | Option 1: actions are neutral | Option 2: green stays the action color |
|---|---|---|
| Primary action | Filled with the strongest text color (near-white on dark, near-black on light) | Filled green, as today |
| Good status | Green, and nothing else on the screen is green except the brand mark | Moves to a shape-and-word-only treatment, or shares green with buttons |
| Links, focus ring, eyebrow labels | Strongest text color, with underline (links) or a 2px outline (focus) as the shape | Green, as today |
| Consequence | The brand green becomes rare: the mark, plus the good state | A green button beside a green `ESTABLISHED` badge reads as one family, which is the defect in the triggering example with blue swapped for green |

The token table below is written for Option 1. Option 2 changes only the `--action-primary-*`, `--link` and `--focus-ring` rows.

## Rules (proposed)

### 1. One meaning per color

Each hue has exactly one job on a screen. A hue that marks a status is never also the color of a button, a selected tab, a link or a heading.

| Hue family | Its one meaning |
|---|---|
| Green | Good: established, healthy, verified |
| Amber | Degraded: working, but a person should look |
| Red | Bad or dangerous: lost, failed, or an action that harms if pressed in error (Decision 1) |
| Blue | Waiting or in progress: handshaking, enrolling, syncing |
| Grey | Unknown, no data, inactive, and every neutral surface and text |
| Brand green | The goat mark only (Decision 2) |

Selection, focus and actions use neutral tones and shape (a bar, an outline, a fill) rather than a hue.

### 2. A status is a shape and a word, never a color alone

Every status is shown as a filled badge holding an icon and an uppercase word. The color is the third, redundant channel. Red and green measure 3.9 apart under simulated deuteranopia (see [Validation](#validation)), so for a colorblind operator the shape and the word carry the whole meaning.

| Status | Word examples | Shape | Lucide icon |
|---|---|---|---|
| Good | `ESTABLISHED`, `HEALTHY`, `OK` | filled circle with a check | `circle-check` |
| Degraded | `DEGRADED`, `SLOW`, `STALE` | triangle with an exclamation mark | `triangle-alert` |
| Bad | `LOST`, `FAILED`, `DOWN` | octagon with a cross | `octagon-x` |
| Waiting / in progress | `HANDSHAKING`, `ENROLLING` | dashed circle | `circle-dashed` |
| Unknown / no data | `UNKNOWN`, `NO DATA` | hollow circle with a question mark, outline only, no fill | `circle-help` |
| Inactive / disabled | `DISABLED`, `OFF` | hollow circle with a bar, outline only | `circle-minus` |

The word inside the badge is ink (`--status-on`) on the status fill. Values, labels and sentences around the badge stay in the text tokens; they never take the status color.

### 3. Status is the strongest element; actions are quieter

Hierarchy comes from size, weight, position and fill, in this order of strength:

1. The status badge of the thing being watched: largest, filled, first in reading order of its card.
2. The values a person acts on (addresses, counters, seconds since last receive): `--fg-primary`, monospace.
3. Labels: `--fg-muted`, uppercase monospace, 12px. Labels are quieter by color and size, not by opacity.
4. One primary action per area: filled neutral button.
5. Secondary actions: outlined buttons.
6. Dangerous actions: last, in their own section (rule 5).

No action button is as visually heavy as the status badge.

### 4. Opacity means "not relevant in the current state" and nothing else

Opacity below 1 is allowed for one purpose: an element that exists but does not apply right now, such as a control that cannot be used in the current state or a card for a check that does not apply to this host. A dimmed control always has a visible sentence saying why (for example "Remote control is off in this node's configuration").

Opacity is never used for hierarchy, decoration, labels or a status. A peer that has stopped reporting is a status (`STALE` or `UNKNOWN`, rule 2), not a dimmed row. The one opacity value is `--opacity-irrelevant: 0.55`; scrims behind a dialog keep the existing `rgba(0,0,0,0.6)`.

### 5. Dangerous actions are isolated and distinct by more than a border

An action that changes a remote device, deletes data or affects other people sits in its own section at the end of its area, under a heading that names the consequence ("Changes the remote device"). Each button names its verb and object ("Restart remote device"), uses the danger treatment (red outline and text under Decision 1 Option A; a 2px strongest-text outline and hatched section header under Option B), carries the `lock` icon while it is not allowed, and asks for confirmation. A dashed border alone does not mark danger.

### 6. Selected and current are neutral and shaped

The selected tab or row uses `--selected-bg`, a 3px `--selected-bar` on its leading or bottom edge, and weight 600. It never uses a status hue and never the primary-action fill. Keyboard focus is a 2px `--focus-ring` outline with a 2px offset, visible at all times.

### 7. Labels that are not statuses are neutral tags

"Experimental", "pre-1.0", "simulated" and similar are tags, not statuses. They render as an outlined neutral tag with the word, no fill and no hue. This retires `--status-exp-*` (violet).

### 8. Contrast meets WCAG 2.1 AA in both themes

Text meets 4.5:1 against the surface it sits on (3:1 for text 18px and larger, or 14px bold). Non-text marks that carry meaning (badge edges, control borders, focus rings) meet 3:1. Each theme's values are chosen and measured separately; a dark-theme value is never reused in light without measuring it. `--fg-faint` (`#5d6661`, 3.37:1 on the dark page) is for rules and dividers only, never text.

## Color roles and tokens

Dark is measured against `--bg-page` `#06090a` and `--bg-card` `#161e22`; light against `--bg-page` `#fbf8f3` and `--bg-panel` `#f0eade`. Status fills are the same in both themes; text on a status fill is always `--status-on`.

| Token | Role | Dark | Light | Measured contrast |
|---|---|---|---|---|
| `--status-good` | good fill | `#2c9e5a` | `#2c9e5a` | 5.85 dark page, 4.94 dark card, 3.23 light page; ink on fill 5.64 |
| `--status-degraded` | degraded fill | `#e8a91f` | `#e8a91f` | 9.63 dark page, 8.15 dark card, 1.96 light page; ink on fill 9.30 |
| `--status-degraded-edge` | 1px badge border in light theme | none | `#8a5a00` | 5.59 light page (supplies the 3:1 edge the fill lacks on paper) |
| `--status-bad` | bad fill (Decision 1, Option A) | `#e5484d` | `#e5484d` | 5.10 dark page, 4.32 dark card, 3.69 light page; ink on fill 4.93 |
| `--status-progress` | waiting / in-progress fill | `#4d8fe0` | `#4d8fe0` | 6.01 dark page, 5.09 dark card, 3.14 light page; ink on fill 5.80 |
| `--status-unknown` | unknown outline and icon | `#8a958f` | `#6e6a63` | 6.45 / 5.45 dark; 5.08 / 4.49 light |
| `--status-inactive` | inactive outline and icon | `#8a958f` | `#6e6a63` | as unknown; shape (bar vs question mark) and word separate them |
| `--status-on` | text and icon on any status fill | `#0b0f0e` | `#0b0f0e` | see each fill |
| `--action-primary-bg` / `-fg` | primary button (Decision 2, Option 1) | `#e8ece9` / `#06090a` | `#1f1d1a` / `#fbf8f3` | 16.75 dark, 15.87 light |
| `--action-secondary-border` | outlined button edge; text is `--fg-primary` | `#6b7a83` | `#857f72` | 4.51 / 3.81 dark; 3.76 / 3.32 light |
| `--action-danger-fg` / `-bg` / `-border` | dangerous button (Option A) | `#ff7c69` / `#2a1410` / `#e5484d` | `#9b2f22` / `#fbe9e5` / `#a83b2a` | text 6.91 dark, 6.34 light; border 5.10 dark page |
| `--selected-bg` | selected tab or row | `#222d33` | `#e1d6b8` | text on it 11.81 dark, 11.62 light |
| `--selected-bar` | 3px edge bar on the selected item | `#e8ece9` | `#1f1d1a` | 11.81 dark, 11.62 light |
| `--focus-ring` | 2px keyboard focus outline | `#e8ece9` | `#1f1d1a` | 16.75 dark, 15.87 light page |
| `--link` | link text, always underlined | `#e8ece9` | `#1f1d1a` | as `--fg-primary` |
| `--fg-primary` | values, status words outside badges, headings | `#e8ece9` | `#1f1d1a` | unchanged from today |
| `--fg-body` | prose | `#b9c2bd` | `#2e2b27` | unchanged |
| `--fg-muted` | labels | `#8a958f` | `#4a4744` | 6.45 / 5.45 dark; 6.89 on light card |
| `--opacity-irrelevant` | rule 4 only | `0.55` | `0.55` | n/a |

Surfaces (`--bg-*`) and borders (`--c-line*`) keep their current values in [colors_and_type.css](colors_and_type.css).

## What exists now

The design system lives in this directory: tokens in [colors_and_type.css](colors_and_type.css), components in [components.css](components.css), rules in [README.md](README.md). It defines status tokens (`--status-ok/warn/err/info/exp`, each `-fg` and `-bg`), says status colors are desaturated, names green as the one accent and the primary action, and allows "inline transparency for ambient state (e.g. dim a peer that hasn't reported in 5s to 50% opacity)". It has no rule against one hue carrying two meanings, no rule pairing status with a shape, and no opacity rule beyond that example.

Several surfaces carry their own status colors instead of these tokens:

| Surface | File | Status colors today |
|---|---|---|
| Design system | `docs/design-system/colors_and_type.css` (this repo; copied into goatstuff) | ok green `#34d97e`, warn amber `#f4c860`, err red `#ff7c69`, info blue `#7ed1f0`, experimental violet `#9d7fe0`; green also primary button, link, focus |
| Portal | goatcore `ops/goat-zenoh-portal/web/static/styles.css` | own palette: success `#065f46`, warn `#5e4400`, err `#b00020`, link blue `#1d4ed8`, accent green `#246b46` |
| panoscope | goatstuff `ops/panoscope/frontend/web/src/styles.css` | `--state-working #46c86e`, `--state-failing #dc5a5a`; schema and role colors include red `#f85149` and purple `#a371f7` as categories |
| goat-map | goatstuff `ops/serve/goat-map/` | `--live #34d399`, `--dead #f43f5e`, `--rd-break #fb923c`, `--rd-attest #f0b429`; affiliation colors (hostile `#fb7185`) |
| stethoscope | goatstuff `crates/stethoscope/src/assets/stethoscope.css` | design-system tokens; opacity 0.5 on not-applicable cards, 0.75 on skipped cards |
| flashlight | goatstuff `ops/flashlight/src/assets/flashlight.css` | `--warn` amber and `--fail` red from the design system |
| netvis | goatstuff `crates/netvis` | `--nv-scoped` teal `#5FBBC8` / `#1F6F7A` |
| Relay health, snitch, smoke-test dashboards | goatcore `ops/relay/health/*.html`, `ops/snitch/internal/server/*.html`, `ops/smoketest/dashboard/style.css` | inline palettes of their own |

Map affiliation symbology (friend, hostile, neutral, unknown) follows its own military standard and is outside this doctrine.

## Do and don't

The triggering link-status page, rule by rule:

| Don't (as built) | Do (proposed) | Rule |
|---|---|---|
| The selected tab, the `HANDSHAKING` badge and every action button are the same blue | `HANDSHAKING` is a blue dashed-circle badge; the selected tab is a neutral bar and bold text; buttons are neutral (filled primary, outlined secondary) | 1, 6 |
| The link state is a colored pill with no icon | Badge with icon and word: `circle-dashed HANDSHAKING`, `circle-check ESTABLISHED`, `triangle-alert DEGRADED`, `octagon-x LOST` | 2 |
| Every label is dim grey at the same weight as the badge's neighbors | Labels in `--fg-muted` at 12px uppercase mono; values in `--fg-primary`; the badge is the largest element on the card | 3 |
| Disabled buttons are faded with no explanation | Faded to 0.55 with the `lock` icon and a sentence naming why they are off | 4 |
| The dangerous section is marked only by a dashed border | Its own section at the end, headed "Changes the remote device", buttons named by verb with the danger treatment and a confirmation step | 5 |
| A wrong-subnet warning is a dashed grey box | A `DEGRADED` or `FAILED` badge with the plain sentence and the fix beside it | 2 |

## Checklist for a UI brief

A brief for a person or an agent building a goat interface includes:

1. The list of states the interface shows, each mapped to one of the six statuses in rule 2, with its word.
2. Which element is the status of the thing being watched (it gets the strongest treatment).
3. The one primary action per area, and which actions are secondary.
4. Every dangerous action, the consequence heading for its section, and the condition that enables it.
5. What is ever not relevant in a state (the only things that may be dimmed), and the sentence shown with each.
6. "Use the tokens in `docs/design-system/color-doctrine.md`; no hex values in component code."
7. Both themes, checked at 4.5:1 for text and 3:1 for marks.
8. Which answer applies for Decision 1 and Decision 2 once they are decided.

## Validation

**Measured** with the dataviz palette validator (`validate_palette.js`, all pairs) on the four status fills `#2c9e5a, #e8a91f, #e5484d, #4d8fe0`:

| Check | Dark (`#06090a`) | Light (`#fbf8f3`) |
|---|---|---|
| Normal-vision separation, worst pair | 22.1 (blue vs green), pass (floor 15) | 22.1, pass |
| Simulated colorblind separation, worst pair | 3.9 (red vs green, deuteranopia), below 8 | 3.9, below 8 |
| Contrast vs page, 3:1 for marks | all four pass | amber 1.96, below 3:1; supplied by `--status-degraded-edge` |

The colorblind result is expected for any red and green pair and is why rule 2 makes the shape and the word mandatory. The validator's lightness-band and chroma checks target chart fills and do not apply to badge fills. Text contrast figures in the token table were computed with the WCAG 2.1 relative-luminance formula.

## Changes if adopted

| File | Proposed change |
|---|---|
| `docs/design-system/colors_and_type.css` | add the tokens above; retire `--status-exp-*`; keep `--status-ok/warn/err/info-*` as aliases during migration |
| `docs/design-system/components.css` | `.chip--*` become status badges with icon and word; `.btn--primary` and `.btn--danger` follow the token table; add a `.tag` for rule 7 |
| `docs/design-system/README.md` | Color, Transparency and Hover/focus sections point here; the 50%-opacity stale-peer example is replaced by the `STALE` status |
| Surfaces in [What exists now](#what-exists-now) | move from their own palettes to these tokens, one pull request per surface |
