# The catalogue of goat landing pages

Every goat landing page in one page, served at `goat/pages/`. `index.html` is written by
`build.py`; do not edit it by hand.

| File | What it is |
|---|---|
| `collect.py` | reads the page list from `.claude/skills/splash-page/examples.md`, fetches each live page and records its title, tagline, lede and numbers strip in `catalog.json`; with `--shots` captures each first screen at 1440 x 900, light and dark, into `shots/` (needs Chrome; resizes with macOS `sips`) |
| `catalog.json` | what `collect.py` recorded |
| `build.py` | writes `index.html` from `page.html` and `catalog.json`; `--check` (run in CI) fails when it is not current, when `catalog.json` and `examples.md` list different pages, or a page lacks its captures, tagline or four numbers |
| `page.html` | the text and layout |
| `extra.css`, `extra-tail.css` | this page's tokens and additions, around the splash-page skill's own `site.css` |
| `catalogue.js` | copy button, the first screen's slideshow, the filter |

When a page is added to `examples.md` or a live page changes its words or numbers:

```sh
python3 -I docs/goat/pages/collect.py --shots
python3 -I docs/goat/pages/build.py
```
