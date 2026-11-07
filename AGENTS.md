# AGENTS.md

Instructions for AI coding agents, and a short version for anyone working here. [CONTRIBUTING.md](CONTRIBUTING.md) is the full process.

## What this repository is

goatdocs holds the explanatory corpus for goat: architecture overviews, strategy, the design system every goat surface renders with, procedures, reference tables, and the templates handed to partners and vendors. A component's own design document lives beside its code in goatcore or goatstuff, not here.

It sits beside [goatcore](https://github.com/usareur-af/goatcore), which builds and runs a goatnet. A real deployment is goatcore at a pinned commit plus a private overlay repository with that deployment's configuration; no deployment's configuration is ever in this repository.

## Layout

| Path | What |
|---|---|
| `docs/INDEX.md` | start here |
| `docs/design/` | designs that are not one component's: architecture, strategy, engineering baselines, patterns |
| `docs/design-system/` | the CSS and rules every goat surface renders with |
| `docs/operations/`, `docs/reference/` | procedures and reference material |
| `docs/partner-templates/`, `docs/vendor-templates/` | documents handed to a partner or vendor |

## Rules CI enforces

1. **No identifier of a real deployment.** Hostnames, domains, addresses, account ids, keys, people, places and organisations of any real goatnet never enter a file or a commit message. Use the example goatnet `zagros`, documentation addresses (RFC 5737, and `100.127.0.0/16` for mesh), and `example.org` mail. The leak gate (`.github/workflows/leak-gate.yml`) checks every added line against a private list of deployment names. It never prints what matched, so a red leak gate means: rename the identifier. The name list is not available outside CI.
2. **Commits.** Conventional Commits subject of 100 characters or fewer, with a scope (`fix(<component>): …`). Every commit is signed off (`git commit -s`, the DCO) and signed. One logical change per pull request.
3. **Design documents move with the code.** A change to behaviour, data flow, topology or an integration point updates its design document in the same pull request, using the status words built, measured, designed and not built exactly. Decisions are ADRs in [goatcore](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md).

## Before you push

The documentation checks live in goatcore. With a goatcore checkout beside this one:

```bash
python3 ../goatcore/ops/ci/check-doc-links.py
bash ../goatcore/ops/ci/check-no-identity-spillage.sh
```

## Writing here

Each document opens with what a reader who stops after two sentences needs, then the detail. Name the real thing (a file with its path, a command, a number with its unit). State the design as it is, not the order it was arrived at.
