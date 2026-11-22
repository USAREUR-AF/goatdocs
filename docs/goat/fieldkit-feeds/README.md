# The Fieldkit Feeds page

`index.html` in this directory is the landing page for Fieldkit Feeds: goat-feeds in goatstuff (`ops/serve/goat-feeds`), the page operators use to send a fabric topic to a system on the mesh and to receive a system's own data onto the fabric. It is a single static file with inline CSS, SVG and script, in the design of `docs/goat/index.html`, and makes no request to another host.

The site build copies it as it is; this README is served at `goat/fieldkit-feeds/readme/` and excluded in `mkdocs.yml`.

The first screen animates a drawing of the mechanism; the two lines under it replay, in order, the audit log of the run the captures were taken from. With reduced motion it shows one still frame.

The images are captures of goat-feeds built from goatstuff `main` at commit `804dd77`, run on a laptop against a scratch Postgres, signed in as a tactical admin, with example names and documentation addresses (198.51.100.0/24). The converter behind it was a stand-in that counts messages; the service, its pages and the commands it shows are the real ones. Each capture is 1240 CSS px wide at 1.5x, in a light and a dark version (`<name>-light.png`, `<name>-dark.png`), chosen by the reader's color scheme.

Every number on the page has the command that reproduces it in its Numbers section. The terminal blocks are real output of the commands shown above them. Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.
