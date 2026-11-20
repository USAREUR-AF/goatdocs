# The Hello Galaxy page

`index.html` in this directory is one page for the Hello Galaxy series: the public `USAREUR-AF/hello-galaxy-*` repositories, each a small runnable example that answers one question about goat. It is a single static file with inline CSS and script, and it makes no request to another host.

The site build copies it as it is. MkDocs serves a hand-written `index.html` beside a `README.md` unchanged, and serves this file at `hello-galaxy/readme/` (`.github/pages/hooks.py`; `mkdocs.yml` excludes it under `exclude_docs`).

Each card uses the figure at the top of that repository's README, copied from its `docs/figures/` as `<repository>-light.svg` and `<repository>-dark.svg`. The figures sit beside the page so the site build does not generate a listing page for an image directory. The question on each card is taken from that README, and the command and what it needs are from its run section.

The terminal on the first screen replays lines that three runs printed, with `...` where lines are left out: `bin/hello-time offline` in hello-galaxy-time-hygiene at `39027df`, `./run` in hello-galaxy-cross-env-federation at `717007d`, and `python3 bin/demo` in hello-galaxy-universal-id at `33bc6e7`. The page's Numbers section gives the command behind each number. When a repository is added to the series, or its figure changes, copy the figure and add a card.
