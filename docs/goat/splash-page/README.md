# splash-page landing page

The page for the `splash-page` Claude Code skill (`.claude/skills/splash-page/`), served at
`goat/splash-page/`. `index.html` is written by `build.py`; do not edit it by hand.

| File | What it is |
|---|---|
| `page.html` | the text and layout |
| `extra.css` | this page's tokens and metaphor (a proof sheet), placed before the skill's own `templates/site/assets/site.css` |
| `extra-tail.css` | styles this page adds: the gallery, the file tree, the replay |
| `replay.js` | copy buttons and the first screen's replay: the output of `scaffold.py` and `site/build.py` run in a new repository, copied from the run |
| `icon.svg` | the page icon, inlined as a data URL |
| `shots/` | the first screen of each live page in `examples.md`, light and dark, 720 px wide, captured with headless Chrome at 1440 x 900 |
| `build.py` | writes `index.html`; `--check` fails when it is not current, when a number differs from the tree, or when a picture is missing |

```sh
python3 -I docs/goat/splash-page/build.py           # write index.html
python3 -I docs/goat/splash-page/build.py --check   # what CI runs
```

When a page is added to `examples.md`, add its two pictures to `shots/` (`<slug>-light.jpg`,
`<slug>-dark.jpg`, the slug being the URL path without `goatdocs/goat/`) and run `build.py`.
