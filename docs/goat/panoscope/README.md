# The panoscope page

`index.html` in this directory is the landing page for panoscope, the inspection tool in goatstuff (`ops/panoscope`) that draws a goat data fabric live in the browser. It is one self-contained file, served at `goat/panoscope/` by goatdocs Pages, with styles and script inline and no request to another host. It was laid down with `.claude/skills/splash-page/scaffold.py subpage`. This README is served at `goat/panoscope/readme/` and excluded in `mkdocs.yml`, with `check.py`.

## The first screen

The stage replays one recorded run of the real program. Its four images are captures of panoscope's COP page, taken in this order:

| File | Frame |
|---|---|
| `cop-fabric.png` | the whole notional fabric: 23 peers, 19 topics |
| `cop-topic.png` | the topic `notional/octopus/alpha-fob/tracks/v1` opened, with its samples in the stream pane |
| `cop-family.png` | after 120 keys under `notional/viewproof/stream/` were put on the router: one family group |
| `cop-collapsed.png` | after COLLAPSE ALL: the notional organization as one node |

The lines under each frame are `publish_sampled` events that panoscope sent to its WebSocket (`/ws?snapshot=0`) during the same run, nine per frame in the order they arrived, copied into the script with their clock times. For frames 1, 2 and 4 they are the last nine before the capture; for frame 3 they are the first five and the last of the 120 keys and the three publishes that followed. Without JavaScript or with reduced motion the stage shows frame 2.

The run: goatstuff `main` at commit `69e8165`, `./demo.sh up` in `ops/panoscope` on a laptop (a Zenoh router, the notional fleet of `ops/zenoh-trial-peers/synth-vendor/demo-roster.json`, and panoscope, all on the loopback), captured with headless Chrome at 1280 by 800 CSS px at 1.5x. The 120 extra keys were put through the router's REST plugin, the same keys and bodies as the loop in the page's Quick start, in the shape of the proof in goatstuff `docs/design/panoscope-view-model.md`. All data is notional; peer ids are the random Zenoh ids of that run.

panoscope has one dark theme, so each capture is a single image shown in both color schemes. The page itself follows the reader's light or dark setting.

The `/api/view` blocks are real output from that run. The `cargo test view::group` block is real output on the same commit. The `/api/samples` and `/api/snapshot` blocks are real output from a fresh `./demo.sh up` about 40 seconds after start.

`docs/goat/panoscope.png` (used on `docs/goat/index.html`) is a frame of the older recording in goatstuff `docs/figures/panoscope.gif`. This page does not use it.

## Where each number comes from

Every number on the first screen is in an element with `data-measure="<key>"`. `check.py` measures each key from a goatstuff checkout and fails if the page says something else. Run it before you change the page and when panoscope changes in goatstuff. The pages workflow does not run it, so a change in goatstuff never fails a goatdocs build:

```sh
python3 -I docs/goat/panoscope/check.py <goatstuff-checkout>
```

| Key | On the page | Measured as, in `ops/panoscope` |
|---|---|---|
| `pages` | 4 | `ls frontend/web/*.html \| wc -l` |
| `max-elements` | 5,000 | `grep -o 'MAX_ELEMENTS: usize = [0-9_]*' src/view/assemble.rs` |
| `vendored` | 1 | `ls frontend/web/vendor/*/*.js \| wc -l` |
| `rust-tests` | 256 | `grep -rE '#\[(tokio::)?test' src \| wc -l` |

Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.

## Recapture

Start the demo, wait about 40 seconds, then drive the COP in a browser at 1280 by 800: take frame 1, click the `tracks` pin of `notional/octopus/alpha-fob/tracks/v1` for frame 2, press Escape, run the Quick start loop and wait about 9 seconds for frame 3, then click COLLAPSE ALL for frame 4. Record `/ws?snapshot=0` alongside, and update the events in the script and the numbers in the outputs to match the new run.
