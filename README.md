<h1 align="center">goatdocs</h1>

<p align="center">
  Architecture, strategy, design system and integration guides for goat.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

> [!NOTE]
> goat is pre-1.0: interfaces can still change between releases.

The explanatory corpus for goat — the design documents, reference material, design system, positions and templates that explain the system and the thinking behind it, as distinct from the component documentation that lives beside the code in [`goatcore`](https://github.com/usareur-af/goatcore).

| Directory | What |
|---|---|
| `docs/design/` | architecture overviews, strategy, technology evaluations, engineering baselines, patterns — the designs that are not one component's |
| `docs/reference/` | reference material: glossaries, lexicons, comparative tables, and [the open-source projects goat is built with](docs/reference/built-with.md) |
| `docs/design-system/` | the design system every goat surface renders with |
| `docs/manifesto/` | positions: phoenix-native peers, queryable by default, the licence-tier posture, substrate not platform |
| `docs/partner-templates/`, `docs/vendor-templates/` | the documents a partner or vendor is handed |

Where a document here cites code, it cites `goatcore` by path; where it describes a component, the component's own design document in `goatcore/docs/design/` is canonical and this corpus links to it.

Start at [docs/INDEX.md](docs/INDEX.md). The same documents are published as a website at <https://usareur-af.github.io/goatdocs/>, built from `main` by [`.github/workflows/pages.yml`](.github/workflows/pages.yml) with MkDocs ([`mkdocs.yml`](mkdocs.yml)). Preview it locally with `pip install -r .github/pages/requirements.txt && mkdocs serve`.

## Built with

goat runs on and builds with open-source projects including Eclipse Zenoh, NetBird, WireGuard, Ory, SPIFFE/SPIRE, PostgreSQL with pgEdge Spock, and Prometheus. The full list, with licences and what each is used for: [docs/reference/built-with.md](docs/reference/built-with.md).

## Contributing and licence

Docs follow the same pull-request process as code: [CONTRIBUTING.md](CONTRIBUTING.md). Every document states what is *built*, *designed* or *not built*; a document that does not is a defect. Apache License 2.0 ([LICENSE](LICENSE)).

## Licence

`goatdocs` was written by U.S. Federal government employees. In the U.S. it is not subject to copyright and is in the public domain; in countries where copyright is recognized, it is released under the [Apache License 2.0](LICENSE). See [INTENT.md](INTENT.md).
