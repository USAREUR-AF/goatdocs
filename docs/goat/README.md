# The goat landing page

`index.html` in this directory is the landing page for goat as one system: goatcore, goatstuff, open-billie, octo-pod and goatdocs. It is a single static file with inline CSS, SVG and script. The first screen animates a drawing of two sites whose direct tunnel keeps carrying messages while their cloud link is cut; with reduced motion it shows one still frame. It loads the images beside it and makes no request to another host.

The site build copies it as it is. MkDocs serves a hand-written `index.html` beside a `README.md` unchanged, and serves this file at `goat/readme/` (`.github/pages/hooks.py`, rule 3; `mkdocs.yml` excludes it under `exclude_docs`).

Every number on the page has the command that reproduces it in the page's Numbers section. The terminal blocks are real output of the commands shown above them. The images are captures, kept beside the page so the site build does not generate a listing page for an image directory: `panoscope.png` is one frame of `docs/assets/panoscope.gif` in goatcore, and `goatdocs-error-page-light.png` / `goatdocs-error-page-dark.png` are the error-code page `reference/errors/GB-001/` of this site in its two color schemes, 900 px wide, from the top of the page to the end of its "What to do" section.

Every `<pre>` on the page is marked `data-box="command"` or `data-box="output"`. A command box shows the whole command at any width: it wraps at spaces, each line of it a `<span class="ln">` with a hanging indent, and Copy copies the exact text. An output box wraps on a wide screen and scrolls inside its box on a narrow one, and its caption says so. The pages workflow checks both at 1440 and 390 px wide with `.github/pages/fitcheck.py`.
