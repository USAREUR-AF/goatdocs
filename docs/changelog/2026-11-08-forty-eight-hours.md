# Changelog, 6 to 8 November 2026: the first two days of public development

On 6 November goat moved from one private monorepo to public development in the USAREUR-AF repositories. From now on a merged public pull request is the change, and a deployment is built from the public repositories plus a private overlay that holds only that deployment's own configuration. In the two days since, four things changed that affect how you run, join or contribute to a goatnet. Federation partners now meet through a directory on the internet, with one phone call as the only human step. A migration moves a goatnet's Postgres to UTF8, which decides whether a new site can join it. Base images are named by role, so you build on your own catalogue without forking a Dockerfile. Outside contributions get a trust check, and registered operators receive vulnerability fixes before the public advisory.

This page lists what changed, why it matters to someone who runs or contributes to a goatnet, and where to read the code. It also explains the processes that are not visible from the public repositories alone, and closes with the work that is still changing fast.

## At a glance

| Theme | What changed | Read first |
|---|---|---|
| [Public development and the assembled tree](#1-public-development-and-the-assembled-tree) | Development happens in the public repositories; a deployment is built from them plus a private overlay. 38 CI workflows that stopped running at the split run again; deployment names come from configuration | goatcore [#83](https://github.com/USAREUR-AF/goatcore/pull/83), [#92](https://github.com/USAREUR-AF/goatcore/pull/92), [#123](https://github.com/USAREUR-AF/goatcore/pull/123) |
| [Federation through the peering directory](#2-federation-through-the-peering-directory) | Phase 5 of the 14-phase peering driver exchanges packages and CAs through saltlick. Adds the peering forwarder and the `PEERING-EDGE` class, and fixes the joiner path | goatcore [#156](https://github.com/USAREUR-AF/goatcore/pull/156), saltlick [#5](https://github.com/USAREUR-AF/saltlick/pull/5) |
| [Postgres SQL_ASCII to UTF8](#3-postgres-sql_ascii-to-utf8) | A nine-phase migration play. Every phase fails closed, and the old data is kept for rollback | [`postgres-utf8-migration.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/operations/postgres-utf8-migration.md) |
| [Base images by role](#4-base-images-by-role) | Every Dockerfile takes its base image as a role. Public defaults are Chainguard's free catalogue pinned by digest, and an overlay may supply its own (ADR 1220) | [ADR 1220](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1220-public-base-images-by-role-overlay-supplies-its-own.md) |
| [Contributor trust, leak gate, releases](#5-contributor-trust-leak-gate-and-releases) | Outside pull requests need a known author or a recorded security review (ADR 1221). The leak gate also scans branch pushes. Releases add two platforms and carry their books | [ADR 1221](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1221-outside-contributions-need-a-known-author-or-a-recorded-security-review.md) |
| [Vulnerability disclosure and advance notice](#6-vulnerability-disclosure-and-advance-notice) | Registered operators receive fixes before the public advisory. An assembled tree may carry recorded pre-disclosure patches | [`SECURITY.md`](https://github.com/USAREUR-AF/goatcore/blob/main/SECURITY.md), goatcore [#19](https://github.com/USAREUR-AF/goatcore/pull/19) |
| [Portal and relay hardening](#7-portal-and-relay-hardening) | Fixes CBPF shard steering, bounds relay subscriptions, and caps live streams per key | goatcore [#73](https://github.com/USAREUR-AF/goatcore/pull/73), [#74](https://github.com/USAREUR-AF/goatcore/pull/74), [#77](https://github.com/USAREUR-AF/goatcore/pull/77) |
| [Operating a goatnet](#8-operating-a-goatnet) | Adds a 24-hour secrets session, a doctrine that every site runs every surface, rollback through the env door, portal guards, and fixes ported from the frozen repository | goatcore [#68](https://github.com/USAREUR-AF/goatcore/pull/68), [#100](https://github.com/USAREUR-AF/goatcore/pull/100) |
| [goatrodeo and licensing](#9-goatrodeo-and-licensing) | New public repository for games on a goat fabric, starting with airdefenders. Licensing follows Code.mil | [goatrodeo](https://github.com/USAREUR-AF/goatrodeo) |
| [Still in progress](#10-still-in-progress-expect-rapid-change) | What will keep changing, and where to watch it | |

The maintainers' private overlay changed in the same window. It holds their goatnets' configuration and pin moves, and is described below only as process.

### If you

| If you | Read | Because |
|---|---|---|
| run a goatnet from the public repositories | [1](#1-public-development-and-the-assembled-tree), [3](#3-postgres-sql_ascii-to-utf8), [8](#8-operating-a-goatnet) | your deployment is now an assembled tree with an overlay; the UTF8 migration decides whether a new site can join you; several operator commands changed |
| federate with another goatnet, or plan to | [2](#2-federation-through-the-peering-directory) | packages and CAs now travel through a directory, and the forwarder covers two edges behind NAT |
| build your own images | [4](#4-base-images-by-role) | Dockerfiles take their base images as roles; you override them from your overlay, not by forking |
| contribute code | [5](#5-contributor-trust-leak-gate-and-releases), [10](#10-still-in-progress-expect-rapid-change) | what the trust check asks of you, what the leak gate refuses, and which areas will keep changing under you |
| operate a deployment and want to hear about vulnerabilities first | [6](#6-vulnerability-disclosure-and-advance-notice) | how to become a registered recipient, and how a pre-disclosure fix reaches your tree |
| run the portal or relay under load | [7](#7-portal-and-relay-hardening) | three defects fixed, one new cap to tune |

Each pull request's page names its author and any co-authors.

---

## 1. Public development and the assembled tree

goatcore, goatstuff, goatdocs, goatenv and goatrodeo are where goat is developed: a merged pull request is the change. The private monorepo they were exported from has been frozen since 6 November and takes no commits. A real deployment runs a tree assembled from the public repositories at pinned commits, with that deployment's private configuration copied over them.

### How a deployment's tree is built

The assembled tree is not visible from any public repository. It decides which public commit a deployment actually runs.

| Layer | Source | Pinned by |
|---|---|---|
| 1 | `USAREUR-AF/goatcore` | `goatcore.ref` in the overlay (a 40-hex commit) |
| 2 | `USAREUR-AF/goatstuff`, copied in | `goatstuff.ref` |
| 3 | `USAREUR-AF/goatrodeo`, copied in | `goatrodeo.ref` |
| (between 3 and 4) | pre-disclosure patches, if any ([section 6](#6-vulnerability-disclosure-and-advance-notice)) | `embargo/<id>/patches.sha256` |
| 4 | the deployment's overlay repository | the overlay commit itself |

- A path that two public layers both carry must be byte-identical, or the assembly stops. This is why shared files such as `ops/base-images/base-images.py` and the rollback-ledger tasks are kept identical across repositories (goatstuff [#5](https://github.com/USAREUR-AF/goatstuff/pull/5)).
- The assembly writes a `.goat-assembled` marker: `goatcore_ref`, `goatstuff_ref`, `goatrodeo_ref`, `overlay_commit`, the layer checkout paths and any `embargo=` line. The deploy's source-of-record check, [`ops/scripts/lib/source_of_record.py`](https://github.com/USAREUR-AF/goatcore/blob/main/ops/scripts/lib/source_of_record.py), refuses a tree whose files differ from the commits the marker names. goatrodeo became an accepted public layer in goatcore [#42](https://github.com/USAREUR-AF/goatcore/pull/42).
- Every deploy ledger row records this once, under `source_tree` (goatcore [#51](https://github.com/USAREUR-AF/goatcore/pull/51), goatstuff [#7](https://github.com/USAREUR-AF/goatstuff/pull/7)).
- Nothing can be pushed from an assembled tree. Changes go to the public repository by pull request, and the overlay then moves its `.ref` file. In this window the maintainers moved their `goatcore.ref` 21 times, each time by a reviewed overlay pull request.

goatcore checks that walk files now read the layers of an assembled tree, because the goatstuff and overlay files sit untracked over goatcore's HEAD. This affects the image-ref guard ([#141](https://github.com/USAREUR-AF/goatcore/pull/141)), the `.envrc.example` generator ([#143](https://github.com/USAREUR-AF/goatcore/pull/143), which reads 1,436 variables instead of 803 on such a tree) and the three goatbuilder-versus-shell parity gates ([#124](https://github.com/USAREUR-AF/goatcore/pull/124)).

### The release ladder from an assembled tree

A component reaches production by climbing a ladder of goatnets written as data in `ops/release/ladder.yaml`. In the maintainers' overlay the rungs are development, then preprod, then prod. A release candidate is a declared deviation on a lower rung. Graduation folds it into the `fleet:` value in `ops/pins/fleet-pins.yaml`. Each step writes a record under `ops/release/records/`. `ops/release/graduate.py check` refuses undeclared skew, and graduation is always a person's act ([ADR 1177](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1177-graduation-is-never-automated-the-daily-review-is.md)). Design: [`release-graduation.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/release-graduation.md).

`rc.sh` and `goatbuilder release` now run from an assembled tree (goatcore [#34](https://github.com/USAREUR-AF/goatcore/pull/34)). Each step's edits land as a pull request on the overlay. The tree is assembled again from the merged overlay, and the deploy runs from the new tree. The workflow is in [`release-candidate-validation.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/release-candidate-validation.md). The overlay's image build opens the development-rung record for every pin it moves, so a new image is on the ladder as soon as it exists.

### Checks that run again

At the split, 38 workflows that guarded the monorepo stopped running anywhere. They run again, each in the repository that holds what it reads. Each restore also fixed the tree defects the workflow found.

| PR | Workflows |
|---|---|
| goatcore [#83](https://github.com/USAREUR-AF/goatcore/pull/83) | 11 guard workflows: acceptance pairings, ACL assertions, admit-audit, agent references and others |
| goatcore [#84](https://github.com/USAREUR-AF/goatcore/pull/84) | 11 checks: goat-obs rules and dashboards, and others |
| goatcore [#80](https://github.com/USAREUR-AF/goatcore/pull/80) | 11 end-to-end and harness workflows: deploy-e2e (hermetic tier), goat-cli UI parity and others |
| goatcore [#81](https://github.com/USAREUR-AF/goatcore/pull/81) | 3 goat-cli book checks. Translation drift is reported and never fails the build |
| goatstuff [#12](https://github.com/USAREUR-AF/goatstuff/pull/12), [#19](https://github.com/USAREUR-AF/goatstuff/pull/19) | netvis client checks; goat-map scope guards |

Also: four checks the export left unable to run now run ([#86](https://github.com/USAREUR-AF/goatcore/pull/86)). A docs-only pull request now finishes CI in about a minute instead of about six, and still reports every required check ([#24](https://github.com/USAREUR-AF/goatcore/pull/24)).

### Nothing of one deployment in the public tree

Values the export had rewritten now come from the caller's configuration, with the example goatnet `zagros` as the default.

| PR | Scope |
|---|---|
| goatcore [#92](https://github.com/USAREUR-AF/goatcore/pull/92) | Names, descriptions and ids a deploy writes onto hosts or cloud resources. Terraform modules take `goatnet` and description variables, so a root whose live resources carry other values is not replaced |
| goatcore [#123](https://github.com/USAREUR-AF/goatcore/pull/123) | Checks and operator scripts. A deployment adds its values in `ops/ci/<check>.d/*` and `ops/pins/parity-capabilities.d/*.yaml` |
| goatcore [#53](https://github.com/USAREUR-AF/goatcore/pull/53) | Ten operator scripts are now either generic (they take `<goatnet>`) or removed |
| goatcore [#45](https://github.com/USAREUR-AF/goatcore/pull/45) | `gen-config.py` reads `repo:` and `deploy:` from `ops/goatbuilder/project.yml` |
| goatstuff [#18](https://github.com/USAREUR-AF/goatstuff/pull/18) | TAK scripts and the trust-sandbox edge |

Every public repository now has an `AGENTS.md` (goatcore [#96](https://github.com/USAREUR-AF/goatcore/pull/96) and its siblings). It covers the layout, the rules CI enforces, and the local checks for contributors and their coding agents. goatcore [#154](https://github.com/USAREUR-AF/goatcore/pull/154) adds `.claude/skills/goat-cli` and `.claude/skills/adr`. Design documents the code cites are now public: [`consistency-foundation.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/consistency-foundation.md) and [`zenoh-data-fabric.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-data-fabric.md) ([#27](https://github.com/USAREUR-AF/goatcore/pull/27)), and ADRs 1114 and 1141 ([#23](https://github.com/USAREUR-AF/goatcore/pull/23)).

---

## 2. Federation through the peering directory

Two goatnets federate by exchanging signed packages and CA certificates, then making one call in which each side reads its key and CA fingerprint aloud. The packages now travel through saltlick, the peering directory. saltlick runs on the internet outside every goatnet and holds pointers, not permissions. A party behind NAT with no public host can therefore federate without sending files by hand.

### The bootstrap: two packages through the directory, one call

| Step | Party A | Directory | Party B |
|---|---|---|---|
| 1 | `PUT /v1/parties/A`: signed pointer `saltlick-pointer/v1` | stores the entry and binds A's key on first use | (same for B) |
| 2 | `PUT /v1/parties/A/package` and `/ca` | each request must be signed by A's bound key; 64 KiB cap | (same for B) |
| 3 | fetches B's pointer, package and CA | serves them byte for byte | fetches A's |
| 4 | checks the package digest, both signatures and the CA against `identity.ca_fingerprint` | | checks A's |
| 5 | **the call**: both sides read their Ed25519 verifying key and CA fingerprint aloud, in groups of four | | |
| 6 | keyring, then phases 6 to 14 (`--from 6`) | | same |

- **Driver.** `peering-standup.sh` and `goatbuilder federate` are kept identical by a parity gate. Preflight requires `FED_DIRECTORY_URL` (https), `FED_COUNTERPARTY_ID` and `FED_SIGNING_KEY`. `FED_NO_DIRECTORY=1` is the one exception, for a counterparty that can reach no directory, and the driver then names the files to hand over. goatcore [#156](https://github.com/USAREUR-AF/goatcore/pull/156), [#57](https://github.com/USAREUR-AF/goatcore/pull/57), [#31](https://github.com/USAREUR-AF/goatcore/pull/31).
- **Directory.** saltlick v0.2.0 added the pointer record ([#3](https://github.com/USAREUR-AF/saltlick/pull/3)) and per-source rate limits: reads 10/s with a burst of 30, writes 6/min with a burst of 6, IPv6 keyed by /64 ([#2](https://github.com/USAREUR-AF/saltlick/pull/2)). v0.2.1 added a page at `/` that lists the parties ([#4](https://github.com/USAREUR-AF/saltlick/pull/4)). v0.3.0 hosts each party's package and CA ([#5](https://github.com/USAREUR-AF/saltlick/pull/5)). v0.4.0 hosts a party's SPIFFE trust bundle and serves each file's upload signature ([#9](https://github.com/USAREUR-AF/saltlick/pull/9)). The directory is not an input to the trust decision: every check in step 4 holds without it.
- **Where it runs.** saltlick is never a mesh service: goatcore [#65](https://github.com/USAREUR-AF/goatcore/pull/65) removed the mesh-internal role. [`peering-directory-service.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/peering-directory-service.md) marks it **built**, deployed on the internet from the deploying team's overlay.
- **Parties share a spec version, not a tool.** Two parties need the same `federation-package` spec version, and each implementation must pass the conformance vectors. A different tool, release or commit is allowed. The driver grades a spec mismatch FAIL and a `tool_version` mismatch WARN ([#33](https://github.com/USAREUR-AF/goatcore/pull/33)).
- **Teaching material follows.** Tutorial 3 checkpoints (hello-galaxy-goatenv [#10](https://github.com/USAREUR-AF/hello-galaxy-goatenv/pull/10)), the gym module (goatstuff [#25](https://github.com/USAREUR-AF/goatstuff/pull/25)) and stages 05 and 05b of hello-galaxy-cross-env-federation ([#4](https://github.com/USAREUR-AF/hello-galaxy-cross-env-federation/pull/4)) teach this model.

### The edge and the forwarder

| Piece | What it is | Status | Read |
|---|---|---|---|
| Peering forwarder (ADR 1218) | A host with a fixed public address, for when neither edge accepts inbound UDP. The listening edge keeps an outbound carrier tunnel (`wg-carry0`) to it. The forwarder relays ciphertext, holds no key, CA or certificate of the peering, and joins no mesh | ADR **proposed**; role **built, not yet run between two goatnets** | [ADR 1218](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1218-peering-forwarder-when-neither-edge-accepts-inbound.md), [`peering-forwarder.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/peering-forwarder.md), [#22](https://github.com/USAREUR-AF/goatcore/pull/22), [#30](https://github.com/USAREUR-AF/goatcore/pull/30) |
| `PEERING-EDGE` node class (ADR 1219) | The edge trusts a foreign root, so it reaches only the core router's fabric port (tcp 7447 on `FABRIC-CORE`) and mesh DNS (udp 5353 on `INFRA`). Only platform admins reach it, on tcp 22 | **accepted**; no live effect until a scope declares it | [ADR 1219](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1219-peering-edge-on-the-mesh-reaches-only-the-core-router.md), [#32](https://github.com/USAREUR-AF/goatcore/pull/32), [#66](https://github.com/USAREUR-AF/goatcore/pull/66) |
| Outbound republisher | Runs on our core host. It reads `release/<set>/**` and writes `from/<us>/<set>/**`, and is the only writer of `from/<us>/**`. The driver now deploys it, and phase 14 acceptance proves each offered set crosses | **built**; image pinned per peering | [#70](https://github.com/USAREUR-AF/goatcore/pull/70), [#87](https://github.com/USAREUR-AF/goatcore/pull/87) |
| Two-sovereign e2e | Both sides of a peering in containers, nightly and on driver changes | runs in CI | [#69](https://github.com/USAREUR-AF/goatcore/pull/69) |

The edge is a peer of its own mesh. Only the peering tunnel joins neither network ([#55](https://github.com/USAREUR-AF/goatcore/pull/55)).

### Adding a site to a running goatnet

Several fixes make the joiner path work from public goatcore alone. A joiner can stand up with the generic `site-seed-from-peer.yml` play ([#44](https://github.com/USAREUR-AF/goatcore/pull/44)). It wires its Spock peers or fails by name, and it matches its founder's encoding ([#71](https://github.com/USAREUR-AF/goatcore/pull/71)). Its pgBackRest passphrase seed survives a host rename, and it can be reached through `join-node --via door` ([#78](https://github.com/USAREUR-AF/goatcore/pull/78)). Each node class targets its own group ([#67](https://github.com/USAREUR-AF/goatcore/pull/67)). Signal federation between a goatnet's two management nodes is now a standard, gated step of adding a joiner ([#79](https://github.com/USAREUR-AF/goatcore/pull/79), [#89](https://github.com/USAREUR-AF/goatcore/pull/89); design [`signal-federation-pair.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/signal-federation-pair.md)).

---

## 3. Postgres SQL_ASCII to UTF8

A goatnet whose Postgres clusters were created before UTF8 became the compose default is SQL_ASCII. It stores bytes unvalidated, and a UTF8 joiner cannot replicate with it. `ops/ansible/postgres-encoding-migrate.yml` moves every Spock member and its streaming standby to UTF8 in one outage. It keeps the old PGDATA, so the goatnet can be put back exactly as it was. The enrolled mesh keeps working throughout. Management, sign-in and the consoles stop from phase 2 to phase 9.

| # | Phase | Refuses when (examples) |
|---|---|---|
| 1 | preflight: reads everything, changes nothing | non-UTF8 group_vars; a non-replicating subscription; divergent replicated rows or FK orphans ([#91](https://github.com/USAREUR-AF/goatcore/pull/91)); compose lacking `POSTGRES_INITDB_ARGS` ([#131](https://github.com/USAREUR-AF/goatcore/pull/131)); Ory containers that do not exist ([#134](https://github.com/USAREUR-AF/goatcore/pull/134)); declared Spock wiring different from live ([#137](https://github.com/USAREUR-AF/goatcore/pull/137)); not enough disk (3 × PGDATA + 1 GiB) |
| 2 | quiesce | a client session remains |
| 3 | capture: hashes, counts, full backup, dumps | slots do not catch up; key sets differ |
| 4 | snapshot: old PGDATA kept as a volume | the copy does not fit or match |
| 5 | reinit as UTF8; restore validates every byte | archiving stays off until phase 7 ([#97](https://github.com/USAREUR-AF/goatcore/pull/97)) |
| 6 | rebuild every physical standby ([#125](https://github.com/USAREUR-AF/goatcore/pull/125)) | a standby does not stream |
| 7 | new pgBackRest stanza and full backup | check or backup fails |
| 8 | re-wire Spock and Ory in join order | a subscription phase 1 did not record |
| 9 | probe: each node writes non-ASCII text that every node must receive intact | a probe row does not arrive |

Each phase leaves a marker per host, so a re-run resumes where it stopped. `action=status`, `rollback`, `reconcile` and `cleanup` are separate actions. Runbook: [`postgres-utf8-migration.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/operations/postgres-utf8-migration.md). Code: `ops/ansible/roles/postgres-encoding-migrate/`. First PR: [#85](https://github.com/USAREUR-AF/goatcore/pull/85).

**Status.** The runbook and role are tagged **WIP, not for production use**. The tag's gate is one live migration of a goatnet run end to end. On 7 November the maintainers ran the play on their three environments in the order the runbook prescribes: development, then preprod, then prod. Those environments' Postgres is now UTF8, and the fixes those runs needed are #91 to #137 above.

---

## 4. Base images by role

Every goat image is built from a few base images: one for compiling Rust, one for Go, one the program runs in. Dockerfiles now name these by role, not by vendor. The public defaults are Chainguard's free catalogue, which anyone can pull without an account, pinned by digest. A deployment that wants other bases, such as a paid catalogue or its own mirror, puts one file per role in its overlay. No Dockerfile is forked.

| Role | Build argument | Public default (digest-pinned) |
|---|---|---|
| `rust-build` | `BASE_RUST_BUILD` | `cgr.dev/chainguard/rust:latest-dev` |
| `go-build` | `BASE_GO_BUILD` | `cgr.dev/chainguard/go:latest` |
| `node-build` (goatstuff) | `BASE_NODE_BUILD` | `cgr.dev/chainguard/node:latest-dev` |
| `runtime-cc` | `BASE_RUNTIME_CC` | `cgr.dev/chainguard/glibc-dynamic:latest` |
| `runtime-static` | `BASE_RUNTIME_STATIC` | `cgr.dev/chainguard/static:latest` |
| `runtime-shell` | `BASE_RUNTIME_SHELL` | `cgr.dev/chainguard/wolfi-base:latest` |

### How an overlay supplies its own catalogue

1. The overlay carries `ops/base-images/<role>/Dockerfile`, one digest-pinned `FROM` line, for each role it changes. Roles that link glibc are overridden together.
2. Assembly copies the file over the public one. Every image build calls `ops/base-images/base-images.py args`, so the overlay's bases are used.
3. The maintainers' overlay carries a file for every role, and its build refuses when the public tree has a role it lacks.
4. A private catalogue (`cgr.dev/<org>/*`) appears only in an overlay. The public gate `base-images.py check` fails on a subscription registry in any public role, default or compose template.
5. Dependabot refreshes each role digest. `base-images.py sync` rewrites the Dockerfile defaults, which rebuilds exactly the images whose base moved (goatstuff [#23](https://github.com/USAREUR-AF/goatstuff/pull/23)).

goatcore [#54](https://github.com/USAREUR-AF/goatcore/pull/54) introduced the roles and [#94](https://github.com/USAREUR-AF/goatcore/pull/94) set the free-catalogue defaults, with matching PRs in goatstuff and goatrodeo. A worked example lives in goatenv `base-images-private-catalogue/` ([#6](https://github.com/USAREUR-AF/goatenv/pull/6)), and a rehearsal in hello-galaxy-goatenv ([#3](https://github.com/USAREUR-AF/hello-galaxy-goatenv/pull/3), [#6](https://github.com/USAREUR-AF/hello-galaxy-goatenv/pull/6)). The how-to is [`build-on-your-own-base-images.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/operations/build-on-your-own-base-images.md), and the supply-chain rows in goatdocs [`architecture-spine.md`](../design/architecture-spine.md) and [`deliberate-deltas.md`](../design/deliberate-deltas.md) say the same ([#4](https://github.com/USAREUR-AF/goatdocs/pull/4)). Related image fixes: `mc-init` runs on the non-root minio-client image ([#93](https://github.com/USAREUR-AF/goatcore/pull/93)), and the audit evictor pins the Chainguard minio-client ([#60](https://github.com/USAREUR-AF/goatcore/pull/60)).

---

## 5. Contributor trust, leak gate and releases

### Contributor trust (ADR 1221): what an outside contributor does

A check named `contributor-trust` places each pull request's author in a tier. An unknown author's change needs a recorded security review before it can merge.

| Tier | Who | Security review needed |
|---|---|---|
| maintainer | GitHub reports `OWNER`, `MEMBER` or `COLLABORATOR` | no |
| automation | Dependabot | no |
| known | registered in a goat community environment, or the author of at least one merged pull request in the organisation | only when a path in `.github/contributor-trust/sensitive-paths.txt` changes (CI and build files, pins and lockfiles, identity, access, crypto, relay, fabric) |
| unknown | neither | yes |

To be **known**, either have a pull request merged, or register in a community environment and add your GitHub username to your registration in that environment's identity service. Otherwise an owner reviews your change against the checklist in `CONTRIBUTING.md` and applies the `security-reviewed` label, and a second owner approves. A new push removes the label. The check runs from the base branch under `pull_request_target`. It never checks out or runs your code, and never prints who is on the roster.

The check is in every public repository: goatcore [#146](https://github.com/USAREUR-AF/goatcore/pull/146) and [#155](https://github.com/USAREUR-AF/goatcore/pull/155), goatstuff [#24](https://github.com/USAREUR-AF/goatstuff/pull/24), goatdocs [#7](https://github.com/USAREUR-AF/goatdocs/pull/7), goatenv [#9](https://github.com/USAREUR-AF/goatenv/pull/9), goatrodeo [#8](https://github.com/USAREUR-AF/goatrodeo/pull/8) and hello-galaxy-goatenv [#9](https://github.com/USAREUR-AF/hello-galaxy-goatenv/pull/9). It is not yet a required check. It becomes required once it has run green on open pull requests.

### The leak gate

No hostname, domain, address, account id, key, person, place or organisation of a real goatnet may enter a public file or commit message. The leak gate checks every added line against a private list of deployment names, and prints only `<file>:<line>: <class>`, never the matched value. It now also scans every branch push, not only pull requests ([#98](https://github.com/USAREUR-AF/goatcore/pull/98)). A push scan blocks nothing, but it notifies the pusher. A red leak gate means: rename the identifier. Use the example goatnet `zagros`, RFC 5737 addresses (`100.127.0.0/16` for the mesh) and `example.org` mail.

### Releases and dependencies

| Change | PR |
|---|---|
| goat and goatbuilder binaries for darwin-amd64 and windows-amd64, as well as linux-amd64, linux-arm64 and darwin-arm64 | goatcore [#16](https://github.com/USAREUR-AF/goatcore/pull/16) |
| Releases carry their books (`goat-docs.tar.gz`, `goatbuilder-docs.tar.gz`) in the signed `SHA256SUMS`. The grant-crypto SDK is now released here | [#56](https://github.com/USAREUR-AF/goatcore/pull/56), [#52](https://github.com/USAREUR-AF/goatcore/pull/52) (goat-cli-v0.5.16, goatbuilder/v0.4.2) |
| `goat-get` reads public releases without a token | [#26](https://github.com/USAREUR-AF/goatcore/pull/26) |
| `goatbuilder update` verifies the signature of the repository that published the binary, so a fork verifies against itself | [#63](https://github.com/USAREUR-AF/goatcore/pull/63) |
| Release downloads in CI retry on transient 5xx | [#157](https://github.com/USAREUR-AF/goatcore/pull/157) |
| Dependabot no longer proposes Postgres majors (the pgedge tags are not semver). A major upgrade stays a reviewed plan | [#158](https://github.com/USAREUR-AF/goatcore/pull/158) |
| rustls-webpki 0.103.16 in three zenoh peers (RUSTSEC-2026-0382) | goatstuff [#10](https://github.com/USAREUR-AF/goatstuff/pull/10) |

---

## 6. Vulnerability disclosure and advance notice

Report a vulnerability privately through the repository's *Security* tab, never in a public issue. When a fix exists for an undisclosed vulnerability in goat's own code, registered members of the goat user community receive the fix privately, before the public advisory. Their deployments are then patched by the time the advisory is published.

| Rule | Value |
|---|---|
| Used for | undisclosed vulnerabilities in goat's own code, once a fix exists. A dependency with a public advisory is handled in the open |
| Window | 7 days from the notice, extendable once to 14, always ending at or before the disclosure date agreed with the reporter (30-day target). Ends at once if the vulnerability is exploited, public, or leaked by a recipient |
| Recipients | people who have completed onboarding to a community environment the maintainers operate, whose registration is current, and who have linked a GitHub account to it |
| What they receive | read access to a private repository holding the advisory text, the fix as a patch and fixed images and binaries, plus an e-mail per notice |
| What they may do | deploy the fix to the deployments they operate and tell those deployments' operators. They may not discuss it publicly or share the patch or artifacts beyond those deployments |

Source: [`SECURITY.md`](https://github.com/USAREUR-AF/goatcore/blob/main/SECURITY.md) (goatcore [#20](https://github.com/USAREUR-AF/goatcore/pull/20)). The `SECURITY.md` of goatdocs, goatstuff and hello-galaxy-goatenv now points to the private reporting form (goatdocs [#2](https://github.com/USAREUR-AF/goatdocs/pull/2)). The maintainers' decision record for this process is ADR 1217. It lives with their overlay, which is why 1217 is absent from the public register.

### Pre-disclosure patches in an assembled tree

During the window, a fix must reach registered deployments without appearing in a public repository. An overlay therefore declares the fix as a patch: `embargo/<id>/core.patch` (goatcore files) or `embargo/<id>/stuff.patch` (goatstuff files), with each patch's sha256 in `embargo/<id>/patches.sha256`. The assembly fetches each patch from the source the overlay names, and refuses it unless the digest matches. It applies the patches between the goatrodeo and overlay layers, and records them in `.goat-assembled` as `embargo=<id>/<kind>.patch:<sha256>,…`. The deploy's source-of-record check accepts a tree that differs from the public commits only by recorded patches. The deploy ledger names them in `source_tree.embargo`. goatcore [#19](https://github.com/USAREUR-AF/goatcore/pull/19).

---

## 7. Portal and relay hardening

Three fixes from `0mlml` close load and correctness gaps in the relay and the portal's live stream.

| PR | Defect | Change |
|---|---|---|
| [#73](https://github.com/USAREUR-AF/goatcore/pull/73) | The `SO_REUSEPORT_CBPF` steering program (`--cbpf-affinity`) read the source address at `ld [12]`, past the TCP header, so every connection went to shard 0 | It loads at `SKF_NET_OFF + 12`. The end-to-end test, previously skipped, now passes 4/4 in CI |
| [#74](https://github.com/USAREUR-AF/goatcore/pull/74) | A peer could grow the relay's subscription registry without bound, and each disconnect walked every subject under the global lock | `SubscriptionIndex` indexes both ways. A peer may watch at most 16,384 subjects, and refusals are counted in `subscriptions_refused` |
| [#77](https://github.com/USAREUR-AF/goatcore/pull/77) | Each `/api/topics/stream` connection polls the router once a second, with no limit per key | At most `PORTAL_MAX_STREAMS_PER_PRINCIPAL` (default 8) streams per org or slot key. Past the cap the portal answers `409 stream_limit`. Operators are exempt |

[#174](https://github.com/USAREUR-AF/goatcore/pull/174) adds the role variable `portal_max_streams_per_principal`. Left empty, the image default applies. Set a number to raise the cap where many people share one org key, or `0` to turn the cap off.

---

## 8. Operating a goatnet

| Change | What an operator does differently | PR |
|---|---|---|
| Secrets session | `ops/scripts/secrets-session start [--store S] [--hours N]`: one approval lets `with-secrets` resolve references unattended for up to 24 h, on 1Password, OpenBao or Vaultwarden | [#68](https://github.com/USAREUR-AF/goatcore/pull/68) |
| Every site runs every surface (doctrine P13) | Read-only and per-site surfaces run at every site. Single-homing is allowed only for an admin writer declared `single_homed_role`. `generate-pins.py --check` refuses other claims | [#100](https://github.com/USAREUR-AF/goatcore/pull/100) |
| Rollback through the env door | `rollback.sh <c> --list` names the goatnet whose history it shows | [#90](https://github.com/USAREUR-AF/goatcore/pull/90) |
| Portal flag guard | A command-line flag the pinned image does not define is refused before the container is replaced. `portal_ca_root_cert_flag` may be a list of candidates | [#88](https://github.com/USAREUR-AF/goatcore/pull/88), [#99](https://github.com/USAREUR-AF/goatcore/pull/99) |
| Release sets in group_vars | A goatnet declares `portal_release_sets` | [#72](https://github.com/USAREUR-AF/goatcore/pull/72) |
| Portal-minted certificates carry the goatnet's Subject O | `portal_cert_sign_org` | [#50](https://github.com/USAREUR-AF/goatcore/pull/50) |
| id-console session cookie lifetime | `oauth2_proxy_id_console_cookie_expire` (default `8h`) | [#139](https://github.com/USAREUR-AF/goatcore/pull/139) |
| Admin guide link | `ADMIN_GUIDE_URL` / `id_admin_console_admin_guide_url` | [#64](https://github.com/USAREUR-AF/goatcore/pull/64) |
| `goat acl test` with no assertions | exits 1 (or 0 with `--none-expected`). goatlite renders assertions | [#61](https://github.com/USAREUR-AF/goatcore/pull/61) |
| Warrant membership on a laptop | `goatnet.toml` carries `warrant_membership_converge` | [#140](https://github.com/USAREUR-AF/goatcore/pull/140) |
| Secrets check | names the portal and console database passwords before the play | [#102](https://github.com/USAREUR-AF/goatcore/pull/102) |
| Store gates | read older names of the store label (`*_store_label_aliases`) | [#95](https://github.com/USAREUR-AF/goatcore/pull/95) |
| Public-CA NetBird API | `-e netbird_api_ca=public` | [#36](https://github.com/USAREUR-AF/goatcore/pull/36) |
| flashlight on a passive node | runs with no local router or portal | goatstuff [#17](https://github.com/USAREUR-AF/goatstuff/pull/17) |
| Raspberry Pi image scripts | run on Linux as well as macOS | [#43](https://github.com/USAREUR-AF/goatcore/pull/43) |

**Ported from the frozen repository.** Six pull requests that were open when the monorepo froze were re-landed in goatcore with their authors as co-authors, named on each pull request:

| PR | Change |
|---|---|
| [#40](https://github.com/USAREUR-AF/goatcore/pull/40) | FIFO-eviction service for the audit bucket |
| [#38](https://github.com/USAREUR-AF/goatcore/pull/38) | restore audit scrape inputs and remote producer checks |
| [#41](https://github.com/USAREUR-AF/goatcore/pull/41) | validate an optional GitHub username at intake |
| [#39](https://github.com/USAREUR-AF/goatcore/pull/39) | Onboarded and Enrolled tabs stay responsive |
| [#37](https://github.com/USAREUR-AF/goatcore/pull/37) | external-service refuses withdrawn proposals |
| [#35](https://github.com/USAREUR-AF/goatcore/pull/35) | machine-provenance reads warrant's declared hosts and holds |

---

## 9. goatrodeo and licensing

[goatrodeo](https://github.com/USAREUR-AF/goatrodeo) is a new public repository for games that run on a goat fabric. It starts with airdefenders: the game server, its Zenoh event schemas, an Ansible role and an image at `ghcr.io/usareur-af/airdefenders` ([9900c5e](https://github.com/USAREUR-AF/goatrodeo/commit/9900c5e)). It is the third public layer of an assembled tree. Fixes: a host is refused before its ledger row is written ([#1](https://github.com/USAREUR-AF/goatrodeo/pull/1)), and a deployment keeps its game directory and owner ([#2](https://github.com/USAREUR-AF/goatrodeo/pull/2)). goatcore and goatstuff call the game by its name again ([#29](https://github.com/USAREUR-AF/goatcore/pull/29), goatstuff [#13](https://github.com/USAREUR-AF/goatstuff/pull/13)).

Licensing follows the Code.mil guidance: public domain in the U.S., Apache-2.0 where copyright is recognized, and a DCO sign-off on every commit. LICENSE, NOTICE, INTENT.md, CONTRIBUTING.md and GOVERNANCE.md were aligned in saltlick [#6](https://github.com/USAREUR-AF/saltlick/pull/6), hello-galaxy-cross-env-federation [#2](https://github.com/USAREUR-AF/hello-galaxy-cross-env-federation/pull/2), hello-galaxy-partner-data-sharing [#2](https://github.com/USAREUR-AF/hello-galaxy-partner-data-sharing/pull/2) and goatrodeo [#4](https://github.com/USAREUR-AF/goatrodeo/pull/4).

---

## 10. Still in progress: expect rapid change

These areas are moving now. Build against them knowing their interfaces and docs may change from one pull request to the next. Status words are those the repositories use.

| Area | State as the repository states it | Watch |
|---|---|---|
| Postgres UTF8 migration | **WIP, not for production use**; run on the maintainers' three environments | goatcore `docs/operations/postgres-utf8-migration.md`, `roles/postgres-encoding-migrate/` |
| Secrets session | **Built; WIP**. The gate is one live 24-hour run on each of 1Password, OpenBao and Vaultwarden | [`secrets-session.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/secrets-session.md) |
| Peering forwarder | ADR 1218 **proposed**; role **built, not yet run between two goatnets**. `transport_offer.via` is designed, not built | [ADR 1218](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1218-peering-forwarder-when-neither-edge-accepts-inbound.md) |
| Peering directory and federation package | saltlick **built**, at v0.4.0. The goatcore design doc still names v0.1.0 and calls the pointer entry designed. The package spec is written, with conformance vectors | saltlick releases, [`peering-directory-service.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/peering-directory-service.md) |
| Contributor-trust check | runs on every pull request; **not yet required** | ADR 1221, each repository's `main` ruleset |
| Contribution standards | draft PRs that pin action revisions, restrict workflow defaults and add DCO and supply-chain checks, open in all nine repositories | goatcore [#127](https://github.com/USAREUR-AF/goatcore/pull/127), [#128](https://github.com/USAREUR-AF/goatcore/pull/128); goatdocs [#6](https://github.com/USAREUR-AF/goatdocs/pull/6) and siblings |
| Deployment values out of the binaries | open: `goat acl`, `goatbuilder update` and id-console take the deployment's values; "one build serves every deployment" in AGENTS.md | goatcore [#178](https://github.com/USAREUR-AF/goatcore/pull/178), [#180](https://github.com/USAREUR-AF/goatcore/pull/180) |
| Release ladder on door goatnets; ledger rows | open | goatcore [#173](https://github.com/USAREUR-AF/goatcore/pull/173), [#145](https://github.com/USAREUR-AF/goatcore/pull/145) |
| oauth2-proxy cookie secrets | open: every fence asserts a 16, 24 or 32 character secret | goatcore [#176](https://github.com/USAREUR-AF/goatcore/pull/176), goatstuff [#28](https://github.com/USAREUR-AF/goatstuff/pull/28) |
| Azure | open: relays and certificates on Azure, with the standup fixes split into drafts | goatcore [#12](https://github.com/USAREUR-AF/goatcore/pull/12), [#111](https://github.com/USAREUR-AF/goatcore/pull/111)–[#122](https://github.com/USAREUR-AF/goatcore/pull/122) |
| Portal performance and resilience | open (`0mlml`): roster parsed once per change; panicking requests access-logged | goatcore [#76](https://github.com/USAREUR-AF/goatcore/pull/76), [#75](https://github.com/USAREUR-AF/goatcore/pull/75) |
| Code-scanning and session hardening | drafts | goatcore [#7](https://github.com/USAREUR-AF/goatcore/pull/7), [#130](https://github.com/USAREUR-AF/goatcore/pull/130); trivy reporting [#9](https://github.com/USAREUR-AF/goatcore/pull/9) |
| Object store | ADR 1222 **proposed**: move the S3 store from MinIO to RustFS | goatcore [#48](https://github.com/USAREUR-AF/goatcore/pull/48) |
| Public roadmap | draft: public standards without delivery commitments | goatcore [#129](https://github.com/USAREUR-AF/goatcore/pull/129) |
| Base-image refresh | Dependabot group update open | goatcore [#59](https://github.com/USAREUR-AF/goatcore/pull/59) |
| goatlite (one box from one file) | **WIP**; run once on hardware. ADR 1213 **proposed** | [`goatlite.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatlite.md), [ADR 1213](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1213-goatlite-preset-one-box-one-file.md) |
| goatbuilder speed | **built; the hour not yet measured on hardware** | [`goatbuilder-speed.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatbuilder-speed.md) |
| Public core, private overlay | ADR 1197 **proposed**. The assembled tree of section 1 is how it runs today | [ADR 1197](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1197-public-core-versioned-dependency-private-overlay-repo.md) |

The maintainers' public roadmap, [github.com/orgs/USAREUR-AF/projects/8](https://github.com/orgs/USAREUR-AF/projects/8), lists these and the other open issues and pull requests by status. The full list of open pull requests is on each repository's *Pull requests* tab. [`RELEASE-CONTENTS.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/RELEASE-CONTENTS.md) grades every goatcore component Tested in CI, Built, Not run or WIP.
