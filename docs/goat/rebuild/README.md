# The rebuild page

`index.html` in this directory is the landing page for rebuild time as a security control,
served at `goat/rebuild/`. It is written by `build.py`; do not edit it by hand.

| File | What it is |
|---|---|
| `run.json` | the record of one timed run of a first site on real machines: every step with its seconds, every stop with its reason, the acceptance result, and the teardown. It names no goatnet, machine, address or person |
| `page.html` | the text and layout |
| `extra.css` | this page's tokens and metaphor (a timing sheet), placed before the skill's own `templates/site/assets/site.css` |
| `extra-tail.css` | styles this page adds: the clock, the three bars, the status tiles |
| `replay.js` | copy buttons and the first screen's replay of the run |
| `icon.svg` | the page icon, inlined as a data URL |
| `build.py` | writes `index.html`; `--check` fails when it is not current |

```sh
python3 -I docs/goat/rebuild/build.py           # write index.html
python3 -I docs/goat/rebuild/build.py --check   # what CI runs
```

## Showing a later run

Replace `run.json` with the record of the new run and run `build.py`. Every number on the
page, the three bars of the first screen, the table of stops, the verdict words ("met",
"not met") and the replay are computed from it. Nothing else changes unless the status of
a property changed, in which case edit its tile in `page.html`.

## How each number is measured

| Number | From |
|---|---|
| time to take a site down | `teardown.seconds`: the wall time of `goatbuilder teardown --services`, which ends with `teardown: ok (N checks)` |
| time to the first sign-in | `person.done_at_s`: seconds from the first phase to the end of phase 11 |
| time to a passing acceptance suite | `acceptance.at_s`: seconds from the first phase to the first run of phase 13 with no failed check |
| the same steps with no stop | `unattended_total_s` (the total the tool prints for phases 1 to 10), plus the sign-in without its stopped time, plus every `late_steps` entry. Each step's seconds is its `phase N took Ns` line in the run that passed it |
| stops | one entry of `stops` for each time a person had to act before the run could continue |

The status word on each tile is the status of that part in the public goatcore tree. A tile
names the least-built part of what its title claims. The page describes each property by
what it does and names no product; it links to the requirements list, where row C1 records
the same times.

`acceptance.approximate` marks an instant known to the minute; the page then prints "about".
