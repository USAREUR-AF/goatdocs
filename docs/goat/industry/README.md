# The industry page

`index.html` in this directory is the page to send a company that wants its product on goat. It addresses the company as "you" throughout. The first half is for whoever receives the link: where a product fits, why one integration reaches every goatnet, the standards goat is built from, and the license. A single band then asks the reader to forward the page to the engineer who owns the product's interfaces, and the second half is that engineer's path, with what each step takes, needs and gives. It is a single static file with inline CSS, SVG and script, on the goat pages' field-map sheet, and makes no request to another host. The site build copies it as it is; this README is served at `goat/industry/readme/` and excluded in `mkdocs.yml`.

The two figures, the fit map in the first screen and the three nations, are drawn by `figures.py` in this directory (`fit_svg()`, `nations_svg()`); paste its output over the `<svg id="fig-fit">` and `<svg id="fig-nations">` elements when a figure changes. The fit map's groups carry `data-k`, and the page script lights the path of the selected product type.

The first screen's command is the goat CLI page's own download command for release `goat-cli-v0.5.20`; change both together. The step 2 build command, the host requirements and "an hour or more" are from goatcore `docs/tutorials/00-goatlite.md`, and the awesome-goat entry line from awesome-goat `README.md`. The other step times are typical for an engineer who knows Linux, containers and Git.

The page has no number strip. Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.
