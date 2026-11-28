# The security page

`index.html` in this directory is the landing page for goat's security design, served at
`goat/security/`. It is written by `build.py`; do not edit it by hand.

The page states one position, "no inside, no outside", and then gives one section to each
idea that follows from it. A section has one figure, a heading that states the idea, three
short answers (what is usual, what goat does, what that changes for the reader), one line of
evidence and one status word.

| File | What it is |
|---|---|
| `page.html` | the text and layout |
| `figures.py` | every drawing: the figure of each section, the site that builds itself in the first screen, and the ten small marks. Fixed-layout SVG, colored by the page's classes only |
| `run.json` | one measured build of a whole site on real machines: every stage with the time of each step, and one measured teardown. It names no goatnet, machine, address or person |
| `extra.css` | this page's tokens (the goat pages' field-map sheet), placed before the skill's own `templates/site/assets/site.css` |
| `figs.css` | the classes the figures and marks are colored by |
| `extra-tail.css` | styles this page adds: the sections, the build on one clock, the status grid |
| `replay.js` | copy buttons and the first screen's replay of the build |
| `icon.svg` | the page icon, inlined as a data URL |
| `build.py` | writes `index.html`; `--check` fails when it is not current |
| `critique-log.md` | the rounds of looking at the rendered page, and what each changed |

```sh
python3 -I docs/goat/security/build.py           # write index.html
python3 -I docs/goat/security/build.py --check   # what CI runs
```

## Showing a later measurement

Replace `run.json` and run `build.py`. Every time on the page, the stages in the first screen
and in the rebuild section, and the replay are computed from it.

| Number | From |
|---|---|
| machine time to build a whole site | the seconds of every step of every stage, plus `between_steps_s`. A step's seconds is the `phase N took Ns` line that `goatbuilder standup` prints for it |
| time to take a site down | `teardown.seconds`: the elapsed time of `goatbuilder teardown --services`, which ends with `teardown: ok (N checks)` |
| checks passed on the built site | `checks_passed`: the acceptance suite, the last stage of the build |

## Rules this page keeps

- One idea in each section and in each figure.
- A property is described by what it does. No product or vendor is named, except the mesh
  protocol, which the project already names.
- A status is one of four words. Measured: a named run on real machines. In use: built and
  running by default. Built: in the tree, and not switched on by default. Designed: decided, and
  not built. The words are in `STATUS` in `build.py`.
- The position figure is drawn by `position_fig.py`; every other figure by `figures.py`.
- State is drawn by line pattern and weight (solid: in use; dashed: designed, or closed), never
  by a warning color.
- No text in a figure is smaller than 14 units of its 464-unit width, so it stays readable in
  a 390 px window.
