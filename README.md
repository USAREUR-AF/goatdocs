<h1 align="center">goatdocs</h1>

<p align="center">
  Architecture, strategy, design system and integration guides for goat.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

> [!NOTE]
> goat is pre-1.0. Until goatcore's first tag, `goatcore/v0.1.0`, this repository is regenerated from its source tree and `main` may be replaced; clone again rather than pull.

The explanatory corpus for goat — the design documents, reference material, design system, positions and templates that explain the system and the thinking behind it, as distinct from the component documentation that lives beside the code in [`goatcore`](https://github.com/usareur-af/goatcore).

| Directory | What |
|---|---|
| `docs/design/` | architecture overviews, strategy, technology evaluations, engineering baselines, patterns — the designs that are not one component's |
| `docs/reference/` | reference material: glossaries, lexicons, comparative tables |
| `docs/design-system/` | the design system every goat surface renders with |
| `docs/manifesto/` | positions: phoenix-native peers, queryable by default, the licence-tier posture, substrate not platform |
| `docs/partner-templates/`, `docs/vendor-templates/` | the documents a partner or vendor is handed |

Where a document here cites code, it cites `goatcore` by path; where it describes a component, the component's own design document in `goatcore/docs/design/` is canonical and this corpus links to it.

Start at [docs/INDEX.md](docs/INDEX.md).

## Contributing and licence

Docs follow the same pull-request process as code: [CONTRIBUTING.md](CONTRIBUTING.md). Every document states what is *built*, *designed* or *not built*; a document that does not is a defect. Apache License 2.0 ([LICENSE](LICENSE)).
