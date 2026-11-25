# Live landing pages

Every page below follows this skill. https://usareur-af.github.io/goatdocs/goat/pages/ is the
catalogue of them, built from this list by goatdocs `docs/goat/pages/`. Read the source of two before writing a new one:
`git show origin/main:site/index.html` in a clone, or the page itself.

## Own sites (`site/` in the repository)

| Repository | Page | First screen shows | Worth copying |
|---|---|---|---|
| goat-processors | https://usareur-af.github.io/goat-processors/ | a test vector replayed step by step on a plan view, with its trace records | `build.py` measures four numbers and a benchmark row and checks status tiles; `contribute.html` second page |
| goat-transformers | https://usareur-af.github.io/goat-transformers/ | a conversion played byte by byte by the engine built to WebAssembly | `build.sh` builds the engine for the page; a radial catalog figure |
| open-billie | https://usareur-af.github.io/open-billie/ | a real frame decoded in the first screen | hero data written by a small Rust program in `site/hero-data/` |
| first-bite | https://usareur-af.github.io/first-bite/ | a test vector decoded live | a full decoder as a sub-page, `site/decoder/` |
| saltlick | https://usareur-af.github.io/saltlick/ | a directory session recorded against a real instance | `build.py` builds the program and records the session |
| goat-client | https://usareur-af.github.io/goat-client/ | the real daemon, CLI and handshake, replayed | daemon, CLI and handshake in one stage |
| goatrodeo | https://usareur-af.github.io/goatrodeo/ | the real game | the product itself as the stage |
| open-entity-gateway | https://usareur-af.github.io/open-entity-gateway/ | what the gateway prints for one record | one record, end to end, as the stage |
| zagros-moon-pod | https://usareur-af.github.io/zagros-moon-pod/ | what crosses the pod router | a boundary as the stage |
| goat-cloud | https://usareur-af.github.io/goat-cloud/ | an ownership register: every cloud resource has an owner | smallest site: one `index.html` with styles inline, `fitcheck.py`, `README.md`; serif for statements, mono for what a machine reads |
| goatrope | https://usareur-af.github.io/goatrope/ | a rope figure drawn by `build.py`, state drawn rather than colored | `page.html` → `index.html` with `build.py --check`; SPDX headers |
| scapegoat | https://usareur-af.github.io/scapegoat/ | a real session against the toy simulator: the link established, lost and established again | `site/record.py` records the session; `build.py` checks the recording and the quoted event log against the tree |
| goatstuff | https://usareur-af.github.io/goatstuff/ | real recordings of the surfaces, one after another: panoscope, flashlight, goat-map, the playground, goat-topology, dataflows | a gallery card per surface whose status `build.py` checks against `docs/RELEASE-CONTENTS.md` |

## Sub-pages in goatdocs (`docs/goat/<slug>/index.html`)

| Page | For | Worth copying |
|---|---|---|
| https://usareur-af.github.io/goatdocs/goat/ | goat as one system | the parent every component sub-page links back to |
| https://usareur-af.github.io/goatdocs/goat/goatbuilder/ | goatbuilder, the tool in goatcore that builds, releases and deploys every machine | a site plan of machine roles, each selectable, built or designed |
| https://usareur-af.github.io/goatdocs/goat/goat-cli/ | goat, the command-line tool in goatcore that operates a goatnet | real output of the release binary: the sandbox, why a connection is blocked, an error explained |
| https://usareur-af.github.io/goatdocs/goat/panoscope/ | panoscope, the live view of a goat fabric, in goatstuff | a replay of a real recording against the synthetic fleet: peers, topics and sampled messages moving |
| https://usareur-af.github.io/goatdocs/goat/fieldkit-feeds/ | Fieldkit Feeds, a service inside goatstuff | captures in light and dark chosen by color scheme; event lines replay a real audit log; numbers each name their command |
| https://usareur-af.github.io/goatdocs/hello-galaxy/ | the hello-galaxy worked examples | one page for a family of small repositories |

The style these pages share was taken from https://ziggity.dev/: a terminal prompt over a
one-word wordmark, a short tagline, Star first among the buttons, a copyable install command,
a strip of big measured numbers, declarative section headlines, real captures instead of
mockups. What the house adds: every number is checked against the tree in CI, the first
screen replays a real artifact, and nothing is fetched from another host.
