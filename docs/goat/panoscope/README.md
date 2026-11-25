# The panoscope page

`index.html` in this directory is the landing page for panoscope: the web surface in goatstuff (`ops/panoscope`) that draws a goat Zenoh data fabric as it runs, built on the crate `panoscope-core` in goatcore. It is a single static file with inline CSS, SVG and script, and makes no request to another host. Its parent is `docs/goat/index.html`, which links to it from the goatstuff card and the footer.

The site build copies it as it is; this README is served at `goat/panoscope/readme/`. `README.md`, `build.py` and `record.mjs` are excluded in `mkdocs.yml`.

## The first screen

The scope in the first screen replays a session recorded from a running panoscope:

1. `record.mjs` (Node 22 or later, no packages) asks a panoscope on `127.0.0.1:8080` for `POST /api/view`, `/api/legend` and `/api/stats`, keeps every WebSocket `delta` for 90 seconds, and then the last three samples of each topic from `/api/samples`.
2. `build.py <session.json>` lays the view out on fixed rings (publishers outside, ordered by role class; topics in the middle; subscribers at the center), writes it as static SVG between the `BEGIN scope` / `END scope` markers, and writes the compact session (peers, topics, `[ms, topic, ema_eps]` per `publish_sampled` event, the first 16 bytes of each topic's last sample) as JSON beside it.
3. The page's script replays the events at the times the WebSocket sent them: one dot from the publisher to its topic and on to each subscriber, as panoscope animates one dot per sampled publish. The HUD rate counts the replayed events of the last five seconds. With reduced motion, or without JavaScript, the static frame stays.

The recording in the page was made on a laptop from panoscope built from goatstuff `main` at commit `69e8165` with `cargo build --release`, a Zenoh 1.9.0 router (`zenohd`), and `synth-vendor` from `ops/zenoh-trial-peers/synth-vendor` in fleet mode with `demo-roster.json` (endpoint set to `tcp/127.0.0.1:7447`). Every peer and topic is synthetic. To record again, run that stack (or `./demo.sh up` in `ops/panoscope`), then:

```
node docs/goat/panoscope/record.mjs /tmp/session.json 90
python3 -I docs/goat/panoscope/build.py /tmp/session.json
```

The scope's colors are this page's, chosen by role class (cyan, blue, teal, green); the shapes follow panoscope's (circle publishes, hexagon publishes and subscribes, inverted triangle subscribes, diamond topic, dashed square the router).

## The captures

`cop.png` and `selected.png` are panoscope itself, captured during the same run with headless Chrome at 1600 by 1000 CSS pixels: the COP page after the layout settled, and the peer `octopus-alpha` selected with its side panel and stream. panoscope has one dark theme, so each capture serves both color schemes.

## Sources

Every statement on the page comes from goatstuff `ops/panoscope` (source, `README.md`, `README-local-demo.md`, `frontend/README.md`) and `docs/design/panoscope-view-model.md`, and from ADR 1123 in goatcore. The thresholds it names (7, 16, 40, 5,000, 4, 50, 200 and the frame times) are constants in that source. The page has no number strip.

Every `<pre>` is marked `data-box="command"` or `data-box="output"`, and the pages workflow checks the page at 1440 and 390 px with `.github/pages/fitcheck.py`.
