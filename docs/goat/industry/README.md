# The industry page

`index.html` in this directory is the page for companies that want their product on a goat fabric: where each kind of product fits, five steps from nothing to a listed integration with what each takes and gives, the open standards goat is built from, the license, and how to contact the project once an integration runs. It is a single static file with inline CSS and script, in the design of the goat CLI page beside it, and makes no request to another host. The site build copies it as it is; this README is served at `goat/industry/readme/` and excluded in `mkdocs.yml`.

The first screen's command is the goat CLI page's own download command for release `goat-cli-v0.5.20`; change both together. The step 2 build command and the host requirements are quoted from goatcore `docs/tutorials/00-goatlite.md`, and the awesome-goat entry line from awesome-goat `README.md`. The times on the route are typical for an engineer who knows Linux, containers and Git; the goatlite tutorial's own words are used for step 2.

The page has no number strip. Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.
