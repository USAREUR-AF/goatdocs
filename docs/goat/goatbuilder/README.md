# The goatbuilder page

`index.html` in this directory is the landing page for goatbuilder, the tool in goatcore (`crates/goatbuilder`) that builds the machines of a goatnet. It is a single static file with inline CSS, SVG and script, in the design of `docs/goat/index.html`, and makes no request to another host. The site build copies it as it is; this README is served at `goat/goatbuilder/readme/` and excluded in `mkdocs.yml`.

The first screen draws the machine roles of a goatnet: solid where `goatbuilder join-node` builds one today, dashed where it is designed as a target type ([goatcore #1091](https://github.com/usareur-af/goatcore/pull/1091)). The same drawing for READMEs is made by `docs/assets/goatbuilder-roles.py` in goatcore. When a role is built, change its status in both.

The terminal blocks are real output of release 0.7.3, and the type file is the sketch from the design. Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.
