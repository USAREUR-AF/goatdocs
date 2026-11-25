# The goat page

`index.html` in this directory is the landing page for `goat`, the operator command-line tool in goatcore (`crates/goat-cli`). It is a single static file with inline CSS, SVG and script, in the design of the goatbuilder page beside it, and makes no request to another host. The site build copies it as it is; this README is served at `goat/goat-cli/readme/` and excluded in `mkdocs.yml`.

The first screen replays three sessions of the release binary `goat-cli-v0.5.20`, run on a laptop with no profile and no network: `goat hello` in the built-in sandbox, `goat warrant why-blocked` against the example goatnet `zagros` from a goatcore checkout, and `goat explain E_OFF_MESH`. Without JavaScript, or with reduced motion, it shows the first session whole.

Every other terminal block is real output of the same release, except the `goat top --once` frame: `top` needs a live goatnet, so that frame is what goat's own plain renderer (`render_plain` in `crates/goat-cli/src/tui/top.rs`) prints for the synthetic state of its unit test `plain_snapshot_renders_panes_with_honesty`. The `goat acl test` block reads the test declaration in `crates/goat-cli/tests/fixtures/acl`. When a new release changes any of this output, run the same commands again and replace the blocks.

The page has no number strip. Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.
