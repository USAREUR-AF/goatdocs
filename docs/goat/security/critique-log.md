# Critique log: goat/security

Each round: render the page, look at it at 1440 and 390 px in light and dark, list defects,
fix, render again. Gates: `build.py --check`, `.github/pages/fitcheck.py`, and the
visualization skill's `figlint.mjs` at 1440 and 390 px in both schemes.

## Round 1: the first version (a page about rebuild time only)

| Item | Defect | Fix |
|---|---|---|
| whole page | one property, shown as tiles and tables of small text with one figure | rebuilt as a page about the whole design, one section an idea |
| the run section | a record of one test run | removed; the page shows the stages of a build and two measured times |
| first screen | three bars | a drawing of a site that builds itself stage by stage, then is taken down and built again |

## Round 2: the figures alone, 400 px wide, light and dark

| Item | Defect | Fix |
|---|---|---|
| intruder figure | lines from one point to a 3 by 2 grid crossed boxes and labels | redrawn, then removed in round 5 |
| identity | three arrows met at one point on the gate | one bar collects them, one arrow enters |
| readers | a lock sat on the arrow line; "a named reader" touched its box | locks above the arrows; label shortened |
| decoy | the bell floated above the alert box | bell inside the box |
| three sites | the cut link was not readable | later split into two figures (round 5) |

## Round 3: the marks, at 176, 96, 64 and 40 px

| Item | Defect | Fix |
|---|---|---|
| hidden overlay | the tunnel arc left the grid at the bottom | ground line raised, arc kept inside |
| all | none of the others at 64 px | kept: one line weight (5), one corner radius (6), ink, map green, dashes for what is absent |

## Round 4: the page, 1440 px, light

| Item | Defect | Fix |
|---|---|---|
| rebuild section | text, numbers and figure drawn over each other: a class name, `top`, was the template's header class | renamed `lead` |
| four habits | "A common open protocol" and "Ordinary small computers" ran out of their boxes | right column widened; titles at 15 |
| first screen | a chip label touched its box | label shortened |

## Round 5: one idea a figure (operator's review)

| Item | Defect | Fix |
|---|---|---|
| position figure | both sides were the same list of boxes; it also carried decoys and rebuild | redrawn as areas against links: shaded enclosures with free lines inside, against open space where each link carries its own mark |
| hidden overlay section | carried the protocol point as a second idea | split: "A scan finds nothing listening" with its own figure |
| sites section | cut off, removed and rebuilt in one figure | split: a site by itself; the hub removes a site and it returns by being built again |
| wording | boundary drawn as a single barrier | replaced by "No inside, no outside" |

## Round 6: figlint, 1440 and 390 px, light and dark

First run: 7 errors, 210 warnings. Last run: 0 errors.

| Finding | Fix |
|---|---|
| figure-no-alt (the first screen's drawing) | given its own label |
| html-overflow at 390 px (the stage header) | header shortened; the right-hand label does not shrink |
| low-contrast (status words hidden in the grid's marks) | marks drawn by CSS; the word is shown on a narrow screen |
| small-text, 157 at 390 px | every figure text at 14 units or more; side margins of each drawing cropped; frames full width on a narrow screen |
| text-clearance | boxes made taller; two labels reworded |
| empty-space (decoy) | the real names in one row, the decoy under them |

Accepted warnings:

| Warning | Why it stays |
|---|---|
| `var-fallback --hang` | from the skill's own stylesheet, where the fallback is the design |
| prose-in-box (the deploy checks) | the box is a list of four checks; the list is the figure |

## Compared with the best existing pages

Looked at beside goat-processors and the goat page, first screens, light.

| They do better | What changed here |
|---|---|
| goat-processors: the first screen is a drawing of the thing moving, with its own records beside it | the first screen draws the site and builds it stage by stage |
| goat: the mechanism is drawn, and the caption says what moves | the stage caption says what one command does and that the times are measured |
| goat: four large numbers, each with one plain sentence | the strip keeps four numbers, each with what it is and how it is measured |
| both: one accent color used sparingly | map green only for the idea in each figure; everything else ink and grey |

Still better there: goat-processors replays real records line by line, so a reader can check
each one. This page replays stage times only.


## Later rounds

| Part | Defect seen | Change |
|---|---|---|
| status lines | two statuses in one line read as a broken table | one status a row: a badge column of fixed width, then the text |
| statuses | three words did not separate running by default from built | four words: measured, in use, built, designed |
| position figure | two sides too alike | one boundary with a door, against no boundary and every connection its own tone and dash (`position_fig.py`) |
| the outside view | two moments in one drawing | two figures: joining, and after joining |
| the idea index | a vertical list | a grid of ten tiles, each a mark, a name and one line |
