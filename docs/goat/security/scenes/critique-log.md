# Critique log: scene modules

Rendered with `preview.py` at 1120 and 464 wide, light and dark, and read at real size.

## Round 1
| Figure | Defect | Fix |
|---|---|---|
| layers, wide | The last status line left one word alone on its second line | Wider wrap for the text beside a badge |
| layers | Grant encryption graded "built" | "in use, where an owner turns it on for a data set" (operator, 28 Nov) |
| path, wide | The title sat on the open-lock marks of the top stops | Title moved up, stops moved down |
| path, narrow | The "Here" heading was cut after its first line | Two lines above the direct line |
| custody, wide | The heading "YOUR HARDWARE..." was crossed by the sealed connection | Heading moved under the two sites, centered |
| boundary, federation | The tunnel arrived at check 2, not check 1 | Checks placed in reading order after the tunnel |
| boundary, simple | A label crossed the edge of the environment plate; the node's name touched its box | Label moved outside the plate; box widened |
| self-documenting, wide | "reads the same files" ran over the declaration's edge; "an audit trail" broke badly | Label set on two lines above its arrow; short names kept on one line |
| preview | Light and dark renders were identical on a machine set to dark | The preview rewrites the theme media query, so each theme renders whatever the machine is set to |

## Round 2
| Figure | Defect | Fix |
|---|---|---|
| estimate | The fourth label ran into its bar; rows 3 and 4 were crowded; the stop marks were too small; a value sat on a grid line | Wider rows, a three-line label, larger stop marks, the long bar's value set inside its right end |
| throughput | The small bar was a dashed sliver | Solid; both bars on the same origin as the estimate |
| layers, narrow | The record was clipped by its card; three orphan words | Wider card, smaller record type, wider wrap |
| custody, narrow | The lists sat on the connection; the tiles overflowed the sites | Lists moved under the sites; tiles in one column |
| boundary, federation, narrow | "does not cross" was hidden by the node; the line from the receiving node ended in nothing | Node moved down; the line now runs to check 1 |
| boundary, simple, wide | A label crossed the plate edge | Moved outside the plate |
| air gap | A label was clipped at the left; the boats were too small; the right side read as a known symbol | Shorter label, island moved, larger boats, a different arrangement of links |
| boundary mark | Four strokes of three kinds, unreadable at tile size | A wall with a wide opening (two lines) and a narrow one (one arrow) |

## Round 3
| Figure | Defect | Fix |
|---|---|---|
| boundary, federation, narrow | The tunnel's label was hidden under the second environment | The gap between the two environments widened, label set in the gap |

Not checked by a script: contrast of each tone against the page background (the figures use only the page's
tokens, which the page's own checks cover), and the scene sections at 1440 and 390 px inside the page
(`SCENE_SHOTS=1 python3 scenes/preview.py` renders them; the first lane's fitcheck should run after wiring).

## Round 4: less prose
The operator's rule of 28 Nov: a scene is a heading, the "Known as" line, three short blocks, the figure and the
status rows; about 70 words of prose at most; everything else goes to an appendix. Every scene was cut to that
(40 to 65 words each) and its leftover material moved to `notes()`. The path scene keeps its bars and loses its
five paragraphs; the timing scene keeps one line per case and moves the sources to the appendix.

| Figure | Defect | Fix |
|---|---|---|
| timing, wide | "416 days, 2011" was clipped at the right edge; the last value touched the band | Label anchored to its marker's left near the edge; taller band |
| timing | Case marks on the axis would crowd the figure | Kept off the figure; the cases are one line each under it |
