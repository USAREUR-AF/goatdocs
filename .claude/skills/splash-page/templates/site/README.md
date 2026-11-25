# site

The landing page published to GitHub Pages by `.github/workflows/pages.yml`.
One static page: no framework, no external requests, no web fonts, light and dark.

## Files

| File | What it is |
|---|---|
| `index.html` | the page |
| `assets/site.css` | its styles, light and dark (`prefers-color-scheme`) |
| `assets/site.js` | the copy buttons and the first screen's replay |
| `assets/icon.svg` | the page icon |
| `assets/from-tree/` | git-ignored; written by `build.py` from the tree |
| `build.py` | copies `assets/from-tree/`, checks every number and placeholder, runs `fitcheck.py` |
| `fitcheck.py` | loads the page in headless Chrome at 1440 and 390 px; fails when a command box is cut off or the page scrolls sideways |

## Preview

```sh
python3 -I site/build.py
python3 -m http.server 8000 --directory site    # then open http://127.0.0.1:8000/
```

## Where each number comes from

Every number is in an element with `data-measure="<key>"`; `build.py` measures the key
from the tree and fails if the page says something else.

| Key | On the page | Measured as |
|---|---|---|
| REPLACE | | |

## The first screen

REPLACE: which file from the tree the replay shows, in what order, and which frame it
stops on with reduced motion or without JavaScript.
