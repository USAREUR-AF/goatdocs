# Changelog, 13 to 16 November 2026: one command builds a joining site, and a fault on someone else's peer is measured

`goatbuilder join-node` now builds a joining site with no manual step after the node is reached: it enrolls the node, issues its certificates, and deploys its data router, health publishers and front door. A goatnet can also measure a fault on a peer it does not own, such as a clock that runs ahead or a client that refuses the router's certificate, and show it per peer. The first release tag of the whole repository, `goatcore/v0.6.1`, is cut, and the branch `stable` points at it.

This entry covers all 27 public [USAREUR-AF](https://github.com/USAREUR-AF) repositories, because a change in one usually lands with matching changes in others. It follows [the entry for 10 to 13 November](2026-11-13-one-command-federation-stable-line.md).

## In short

- **Install goatbuilder 0.6.1, and build on `goatcore/v0.6.1` or `stable`.** 0.6.1 fixes the one known issue in 0.6.0. The release change for 0.7.0 is merged; its tag is not published ([section 1](#1-a-release-of-the-whole-repository)).
- **`goatbuilder join-node` builds a joining site.** Only reaching the node stops the run. The portal, the id console and the onboarding engine still run only at a goatnet's first site ([section 2](#2-one-command-builds-a-joining-site)).
- **Backing a peering out removes the partner's data whole.** A partner's data lives in its own store, and the store is dropped when the peering ends ([section 3](#3-federation-back-out-two-drivers-and-rotation)).
- **Every goatbuilder verb shows its work.** `standup`, `join-node`, `deploy` and `federate` list every value with its source, and a failed phase carries its error code and fix ([section 4](#4-every-verb-shows-its-work)).
- **A fault on a peer you do not own is measured, not guessed.** `goat health --domain peer` shows which peer's clock is ahead ([section 5](#5-faults-on-peers-you-do-not-own)).
- **Every site of a goatnet will write, and the first site is its hub.** ADR 1165 and ADR 1205 are accepted. Most of the design is not built ([section 6](#6-sites-that-run-cut-off)).
- **A moon pod is a learning tool,** and the documents no longer describe it as a guarantee of sovereignty ([section 7](#7-learning-and-documents)).

## What to do

| If you | Do this | Why |
|---|---|---|
| run goatbuilder 0.6.0 or older | Install [goatbuilder/v0.6.1](https://github.com/USAREUR-AF/goatcore/releases/tag/goatbuilder/v0.6.1) | A `federate` run killed in phase 11 did not resume (goatcore [#597](https://github.com/USAREUR-AF/goatcore/pull/597)) |
| build on goat and want a fixed reference | Pin `goatcore/v0.6.1`, or follow the branch `stable` | The first whole-tree tag exists and `stable` points at it; goatenv builds with it (goatenv [#11](https://github.com/USAREUR-AF/goatenv/pull/11)) |
| want to check a downloaded release before installing it | `goatbuilder update verify-release <dir> --signer <owner>/<repo> --version <x.y.z>` | It makes the checks `goatbuilder update` makes, and installs nothing (goatcore [#655](https://github.com/USAREUR-AF/goatcore/pull/655)) |
| script around `goatbuilder status` | Run it without `--mock`. It reads the hosts, changes nothing, and exits 3 while any machine is pending or unknown | Error GB-026 is retired (goatcore [#648](https://github.com/USAREUR-AF/goatcore/pull/648)) |
| federate | Keep the edge and core hosts' clocks synchronized. Phase 1 refuses a host that is unsynchronized or over the offset budget, with GB-268 | The router rejects data stamped more than 500 ms ahead (goatcore [#731](https://github.com/USAREUR-AF/goatcore/pull/731)) |
| run the audit subscriber on MinIO | Expect a deploy to fail when nothing cleans up stalled multipart uploads. Set MinIO's `stale_uploads_expiry`, or use a release that keeps the lifecycle clause | The deploy used to warn and continue (goatcore [#739](https://github.com/USAREUR-AF/goatcore/pull/739)) |
| open a pull request with an unsigned commit | Read the comment the check leaves on your pull request; it names the commit and the repair | `verified-commits` now tells the author (.github [#4](https://github.com/USAREUR-AF/.github/pull/4), goatcore [#660](https://github.com/USAREUR-AF/goatcore/pull/660)) |

## Who should read what

| If you | Read | Because |
|---|---|---|
| build on goat, or pin it | [1](#1-a-release-of-the-whole-repository) | the fixed line exists, and what the next release carries |
| add a site or a node to a goatnet | [2](#2-one-command-builds-a-joining-site), [6](#6-sites-that-run-cut-off) | what the command builds for you, and what a second site does not run yet |
| federate with another goatnet | [3](#3-federation-back-out-two-drivers-and-rotation) | what a back-out removes, and how a peering is driven from two machines |
| run a goatnet | [4](#4-every-verb-shows-its-work), [5](#5-faults-on-peers-you-do-not-own), [9](#9-fixes-for-a-running-goatnet) | what a run prints and records, a new health domain, and deploy fixes |
| are learning goat, or teach it | [7](#7-learning-and-documents) | the learning program, and what a moon pod is for |
| contribute code or documents | [8](#8-contributing-and-ci) | what a fix must show, and what CI runs for your pull request |

Each pull request's page names its author and any co-authors.

---

## 1. A release of the whole repository

`goatcore/v0.6.1` is the first signed tag for the whole repository, and the branch `stable` points at it. goatbuilder 0.6.1 was published the same day and is the release to install.

![The release plan to goatbuilder 1.0 has six steps: 0.5.3 made federation one command and 0.6.1 made runs show their work, and both are published; 0.7.0 completes federation and tests upgrades and its release change is merged but not tagged; 0.7.x lets a joined site run cut off; a 1.0.0 release candidate is proven on hardware and by people outside the team; 1.0.0 freezes the surfaces](figures/2026-11-16/road-to-1-0.svg)

| Change | What you see | PR |
|---|---|---|
| [goatbuilder/v0.6.1](https://github.com/USAREUR-AF/goatcore/releases/tag/goatbuilder/v0.6.1) | The peering link restarts when its interface does not hold the agreed peer, so a `federate` run killed in phase 11 resumes. An interface that lacks the agreed peer is named as GB-271 | goatcore [#597](https://github.com/USAREUR-AF/goatcore/pull/597), [#610](https://github.com/USAREUR-AF/goatcore/pull/610), [#646](https://github.com/USAREUR-AF/goatcore/pull/646) |
| [goatcore/v0.6.1](https://github.com/USAREUR-AF/goatcore/releases/tag/goatcore/v0.6.1) | The whole-tree tag at the commit of goatbuilder 0.6.1. `stable` moved to it. goatenv, the example environment, builds with it | goatenv [#11](https://github.com/USAREUR-AF/goatenv/pull/11) |
| goatbuilder 0.7.0, release change merged | **Not published:** the tag `goatbuilder/v0.7.0` does not exist yet. It carries sections 2 to 4 of this entry | goatcore [#746](https://github.com/USAREUR-AF/goatcore/pull/746) |
| Verify a release without installing it | `goatbuilder update verify-release` checks the keyless signature over `SHA256SUMS` and every file against it | goatcore [#655](https://github.com/USAREUR-AF/goatcore/pull/655) |
| The changelog of goatbuilder is rendered | One file per entry; the release renders `CHANGELOG.md` from them, so two pull requests never edit the same lines | goatcore [#623](https://github.com/USAREUR-AF/goatcore/pull/623), [#639](https://github.com/USAREUR-AF/goatcore/pull/639) |
| Compatibility follows each release | The configuration files and the command baseline of 0.6.0 and 0.6.1 are kept, and every pull request is compared with the newest | goatcore [#631](https://github.com/USAREUR-AF/goatcore/pull/631), [#634](https://github.com/USAREUR-AF/goatcore/pull/634), [#675](https://github.com/USAREUR-AF/goatcore/pull/675), [#676](https://github.com/USAREUR-AF/goatcore/pull/676), [#562](https://github.com/USAREUR-AF/goatcore/pull/562), [#563](https://github.com/USAREUR-AF/goatcore/pull/563) |
| A release run again on a later day gives the same result | The release drivers and the soak tests no longer depend on the date | goatcore [#621](https://github.com/USAREUR-AF/goatcore/pull/621), [#622](https://github.com/USAREUR-AF/goatcore/pull/622), [#628](https://github.com/USAREUR-AF/goatcore/pull/628) |

The gate that decides 1.0 is [`goatbuilder-v1-gate.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatbuilder-v1-gate.md). It sets no dates: a release is cut when its rows pass.

## 2. One command builds a joining site

`goatbuilder join-node` used to stop twice for a person, and left the site's data router, certificates and health publishers as steps done by hand. It now runs phases 1 to 15 in order and stops only at phase 1, where a person reaches the node.

![goatbuilder join-node builds a joining site's setup key, enrollment, certificates, data router, health publishers and front door with no manual phase; a site's own mesh DNS, the rule that only the hub makes a platform admin and a phone node are in review; the portal, the id console, the onboarding engine and the mail queue at every site are designed and not built](figures/2026-11-16/joining-site.svg)

| Change | What you see | PR |
|---|---|---|
| No manual phase after reaching the node | Phase 10 enrolls the node with a single-use setup key minted where it is used; nobody types `netbird up`. Every secret reference passed to a node is resolved first | goatcore [#661](https://github.com/USAREUR-AF/goatcore/pull/661) |
| The site's certificates | The joining site's leaves are minted and staged before its router starts, the audit subscriber's with the others | goatcore [#715](https://github.com/USAREUR-AF/goatcore/pull/715), [#737](https://github.com/USAREUR-AF/goatcore/pull/737) |
| The data router | Deployed at the joining site by the command | goatcore [#699](https://github.com/USAREUR-AF/goatcore/pull/699) |
| Health publishers | The ones the site declares are deployed | goatcore [#718](https://github.com/USAREUR-AF/goatcore/pull/718) |
| The front door | Set up when the site declares signal federation off | goatcore [#721](https://github.com/USAREUR-AF/goatcore/pull/721) |
| A third site | Phases 1 to 15 run for a third site that declares federation off | goatcore [#613](https://github.com/USAREUR-AF/goatcore/pull/613) |
| What the site does not run is stated | `join-node` names each service the site does not run, with the reason from the end-state model | goatcore [#612](https://github.com/USAREUR-AF/goatcore/pull/612), [#637](https://github.com/USAREUR-AF/goatcore/pull/637) |
| Smaller machines | Every container memory limit and the Postgres memory settings are variables whose defaults are the earlier values | goatcore [#615](https://github.com/USAREUR-AF/goatcore/pull/615) |

The design is "join-node builds the whole declared site" (goatcore [#604](https://github.com/USAREUR-AF/goatcore/pull/604)). In review: a joining site that runs its own mesh DNS (goatcore [#678](https://github.com/USAREUR-AF/goatcore/pull/678)), a refusal before any change when the node's clock is off (goatcore [#766](https://github.com/USAREUR-AF/goatcore/pull/766)), and a phone as a node with `--class phone --via usb` (goatcore [#747](https://github.com/USAREUR-AF/goatcore/pull/747)). An Android app that starts the node's virtual machine when the phone boots is merged (goatcore [#743](https://github.com/USAREUR-AF/goatcore/pull/743)).

## 3. Federation: back-out, two drivers and rotation

Backing a peering out now removes the partner's stored data whole and leaves every other line of the core's configuration as it was. A peering can be declared as driven from two machines, for a site where no single machine reaches both the edge host and the core host.

| Change | What you see | PR |
|---|---|---|
| A partner's data is dropped whole ([ADR 1234](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1234-a-partners-data-lives-in-its-own-store-dropped-whole-when-the-peering-ends.md), accepted) | `goatbuilder federate backout <partner>` takes the partner's entry out of the core's peerings file, restarts the router without the partner's store, and removes the store. Deletion by record, key or person is not built and is not planned | goatcore [#614](https://github.com/USAREUR-AF/goatcore/pull/614), [#629](https://github.com/USAREUR-AF/goatcore/pull/629) |
| Back-out is measured | The back-out scenario passes every one of its checks in the federation test environment, on both shapes of core | goatcore [#554](https://github.com/USAREUR-AF/goatcore/pull/554), [#547](https://github.com/USAREUR-AF/goatcore/pull/547), [#640](https://github.com/USAREUR-AF/goatcore/pull/640) |
| Two drivers, first parts | A peering opts in with `drivers: two`. The run stops at the first phase that needs the edge, and the controller imports phase 1's edge result and runs its core half. The hand-over of phase 3 is in review | goatcore [#601](https://github.com/USAREUR-AF/goatcore/pull/601), [#690](https://github.com/USAREUR-AF/goatcore/pull/690), [#608](https://github.com/USAREUR-AF/goatcore/pull/608) |
| Both sides' acceptance, as a library | A side signs its acceptance result and verifies the partner's under the key bound at phase 5, and both sides derive one session from the agreement. No command reaches it yet | goatcore [#654](https://github.com/USAREUR-AF/goatcore/pull/654), [#659](https://github.com/USAREUR-AF/goatcore/pull/659) |
| Key rotation, as libraries and in the roles | The forwarder carrier keys and the WireGuard peering key can be rotated. The command `federate rotate` is in review. Rotation of an IPsec peering's credentials is designed | goatcore [#667](https://github.com/USAREUR-AF/goatcore/pull/667), [#680](https://github.com/USAREUR-AF/goatcore/pull/680), [#701](https://github.com/USAREUR-AF/goatcore/pull/701), [#734](https://github.com/USAREUR-AF/goatcore/pull/734) |
| A clock check before a peering | Phase 1 refuses a peering host whose clock is unsynchronized or over the budget (GB-268) | goatcore [#731](https://github.com/USAREUR-AF/goatcore/pull/731) |
| Running a phase again changes nothing | Phase 10 places nothing and restarts nothing when the admission is in place; phase 13 keeps a newer partner bundle; `federate status` resumes from the first phase it cannot show passed | goatcore [#692](https://github.com/USAREUR-AF/goatcore/pull/692), [#698](https://github.com/USAREUR-AF/goatcore/pull/698), [#632](https://github.com/USAREUR-AF/goatcore/pull/632), [#712](https://github.com/USAREUR-AF/goatcore/pull/712) |
| The link's read-back reads the peer | The WireGuard and carrier read-backs compare each peer's public key and allowed address. An edge driven from a workspace gets the certificates it mounts, or GB-275 says why | goatcore [#662](https://github.com/USAREUR-AF/goatcore/pull/662), [#663](https://github.com/USAREUR-AF/goatcore/pull/663), [#658](https://github.com/USAREUR-AF/goatcore/pull/658) |

## 4. Every verb shows its work

The previous entry described runs that name each command and leave a record. That now holds for `standup`, `join-node`, `deploy` and `federate`, and each run also lists every value it uses with where the value came from.

| Change | What you see | PR |
|---|---|---|
| Every value with its source | `run.json` and the dry run list each value with its source: a file and line, a derivation, an environment override, a default or an allocation. A secret shows its source and never its value | goatcore [#649](https://github.com/USAREUR-AF/goatcore/pull/649) |
| `status` reads real hosts | One row per machine and component: converged, pending or unknown. It runs no play and writes nothing | goatcore [#648](https://github.com/USAREUR-AF/goatcore/pull/648) |
| Phases of every verb are in one catalog | `standup`, `join-node` and `deploy` have phase catalogs, held to the plan each verb prints, so `goatbuilder explain` answers for their phases | goatcore [#651](https://github.com/USAREUR-AF/goatcore/pull/651), [#703](https://github.com/USAREUR-AF/goatcore/pull/703) |
| A failed phase is interpreted | A failed `standup`, `join-node` or `deploy` phase carries the matching error code, its likely cause and its fix | goatcore [#652](https://github.com/USAREUR-AF/goatcore/pull/652), [#669](https://github.com/USAREUR-AF/goatcore/pull/669), [#703](https://github.com/USAREUR-AF/goatcore/pull/703) |
| Every refusal has a code | Each refusal of goatbuilder names its catalog code, and a stop after a printed view says why | goatcore [#560](https://github.com/USAREUR-AF/goatcore/pull/560), [#656](https://github.com/USAREUR-AF/goatcore/pull/656), [#668](https://github.com/USAREUR-AF/goatcore/pull/668) |
| One page per error code | Generated from the catalog and served on the documentation site, one URL per code | goatcore [#666](https://github.com/USAREUR-AF/goatcore/pull/666), goatdocs [#26](https://github.com/USAREUR-AF/goatdocs/pull/26) |
| The contract says so | Clause C11, legibility, is in the deploy contract beside C1 to C10, with its conformance test | goatcore [#647](https://github.com/USAREUR-AF/goatcore/pull/647) |

## 5. Faults on peers you do not own

A goatnet has peers its operators do not own: a partner's router, a contributor's laptop. When such a peer misbehaves, the goatnet now measures the fault at its own router, names the peer, and shows the reading; it never disconnects a peer automatically.

| Change | What you see | PR |
|---|---|---|
| The decision ([ADR 1232](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1232-faults-on-peers-we-do-not-own-follow-one-five-stage-path.md), accepted) | One five-stage path: measure at the router we own, attribute to an owner, tell the admins, the owner and the peer, track, and close when the reading is clean. The first notice to an owner is approved by an operator. Stage 1 and the displays are built; the rest is designed | goatcore [#594](https://github.com/USAREUR-AF/goatcore/pull/594), [#735](https://github.com/USAREUR-AF/goatcore/pull/735) |
| A clock that runs ahead | The reader `goat-peer-health` counts the router's timestamp rejections per peer and publishes a reading on `ops/peer/health/<site>`. When the local clock is suspect, no peer is blamed | goatstuff [#82](https://github.com/USAREUR-AF/goatstuff/pull/82), [#89](https://github.com/USAREUR-AF/goatstuff/pull/89) |
| A client that refuses the router's certificate | A second detector counts ended TLS handshakes per alert name and lists absent peers as candidates | goatstuff [#91](https://github.com/USAREUR-AF/goatstuff/pull/91) |
| Deploying the reader | Role `peer-health`, play `ops/ansible/peer-health-deploy.yml -e target=<group>`, a router access rule and a pin row | goatcore [#730](https://github.com/USAREUR-AF/goatcore/pull/730) |
| Reading it | `goat health` reads the peer domain and this machine's own router verdict. `goat health --domain time` lists clocks a neighbor observed, apart from the site's own. panoscope and the map show the domain, and panoscope's `/top` shows trust refusals | goatcore [#728](https://github.com/USAREUR-AF/goatcore/pull/728), [#733](https://github.com/USAREUR-AF/goatcore/pull/733); goatstuff [#84](https://github.com/USAREUR-AF/goatstuff/pull/84), [#90](https://github.com/USAREUR-AF/goatstuff/pull/90), [#92](https://github.com/USAREUR-AF/goatstuff/pull/92) |

## 6. Sites that run cut off

The design in which every site of a goatnet can admit people and machines while cut off from the others is accepted, together with the rule that makes one site the hub. Most of it is not built: today the portal and the id console run only at a goatnet's first site.

| Change | What you see | PR |
|---|---|---|
| ADR 1165 and ADR 1205 are accepted | Every site writes. The hub is the first site by default, and only the hub makes a platform admin. A cut-off site joining 1.0's gate is group I of the gate | goatcore [#682](https://github.com/USAREUR-AF/goatcore/pull/682) |
| The hub-directive applier is installed | `site-bootstrap.yml` applies the role at each replicating site that names a hub. **Written; not yet run against a host** | goatcore [#596](https://github.com/USAREUR-AF/goatcore/pull/596) |
| Proposed: a joiner runs the replication core | [ADR 1233](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1233-a-joiner-runs-the-replication-core.md), **proposed** | goatcore [#607](https://github.com/USAREUR-AF/goatcore/pull/607) |
| Proposed: two independent SPIRE servers at a site | [ADR 1236](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1236-a-sites-spire-server-is-made-redundant-by-two-independent-servers-after-a-gated-trial.md), **proposed**; nothing in a running goatnet changes | goatcore [#665](https://github.com/USAREUR-AF/goatcore/pull/665) |
| Proposed: rebuild a site from nothing | [ADR 1237](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1237-a-site-is-rebuilt-from-nothing-and-a-combed-extract-of-its-identities.md), **proposed**: a site or an environment is rebuilt from nothing and a checked extract of its identities, rolling or all down | goatcore [#672](https://github.com/USAREUR-AF/goatcore/pull/672), [#684](https://github.com/USAREUR-AF/goatcore/pull/684) |
| Designed | The audit of a cut-off site and a capped spool for a phone; a batch of certificates minted ahead; the console's outbound mail queue | goatcore [#611](https://github.com/USAREUR-AF/goatcore/pull/611), [#605](https://github.com/USAREUR-AF/goatcore/pull/605), [#697](https://github.com/USAREUR-AF/goatcore/pull/697), [#714](https://github.com/USAREUR-AF/goatcore/pull/714) |

**Not in `main`:** how each write class is turned on, checked and rolled back is merged into the branch `island/integration` (goatcore [#624](https://github.com/USAREUR-AF/goatcore/pull/624)), and reaches `main` when that branch is promoted.

## 7. Learning and documents

The learning program is written down as a ladder of ten rungs and a lane beyond it, and the documents state once what a moon pod is for.

| Change | What you see | PR |
|---|---|---|
| The learning program ([ADR 1238](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1238-the-learning-program-is-a-ten-rung-ladder-and-a-lane-beyond-it-in-use-while-proposed.md), proposed and in use) | The learner ladder stays at ten rungs. A lane named "Beyond the ladder" holds operating, proof-of-value and advanced modules; a module whose tooling is not built is marked `frontier: true` | goatcore [#681](https://github.com/USAREUR-AF/goatcore/pull/681), [#688](https://github.com/USAREUR-AF/goatcore/pull/688), [#679](https://github.com/USAREUR-AF/goatcore/pull/679); goatstuff [#85](https://github.com/USAREUR-AF/goatstuff/pull/85), [#86](https://github.com/USAREUR-AF/goatstuff/pull/86) |
| A moon pod is a learning tool ([ADR 1239](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1239-a-moon-pod-is-a-learning-tool-and-not-a-sovereignty-guarantee.md), proposed) | The documents no longer offer a moon pod for real data flow or call bare metal sovereign | goatcore [#687](https://github.com/USAREUR-AF/goatcore/pull/687); goatdocs [#28](https://github.com/USAREUR-AF/goatdocs/pull/28); goatstuff [#87](https://github.com/USAREUR-AF/goatstuff/pull/87); zagros-moon-pod [#19](https://github.com/USAREUR-AF/zagros-moon-pod/pull/19); hello-galaxy-zagros-pod [#8](https://github.com/USAREUR-AF/hello-galaxy-zagros-pod/pull/8) |
| A goatlite skill for a coding agent | The README has one line that hands the goatlite tutorial to an agent | goatcore [#670](https://github.com/USAREUR-AF/goatcore/pull/670) |
| `AGENTS.md` in every repository | Each repository tells a coding agent how to build, test and contribute there | .github [#5](https://github.com/USAREUR-AF/.github/pull/5), goat-client [#3](https://github.com/USAREUR-AF/goat-client/pull/3), saltlick [#13](https://github.com/USAREUR-AF/saltlick/pull/13), open-billie [#25](https://github.com/USAREUR-AF/open-billie/pull/25) and the hello-galaxy repositories |
| The documentation site for machines and for questions | `llms.txt` and `llms-full.txt`, a `context7.json`, and eight pages titled with the question they answer | goatdocs [#23](https://github.com/USAREUR-AF/goatdocs/pull/23), [#24](https://github.com/USAREUR-AF/goatdocs/pull/24), [#25](https://github.com/USAREUR-AF/goatdocs/pull/25), [#27](https://github.com/USAREUR-AF/goatdocs/pull/27) |
| The relay | The documents state that the relay built from the written wire-protocol specification is released and in service | goatcore [#702](https://github.com/USAREUR-AF/goatcore/pull/702), [#713](https://github.com/USAREUR-AF/goatcore/pull/713); goatdocs [#29](https://github.com/USAREUR-AF/goatdocs/pull/29) |
| Work others build on goat | The README points to the list `awesome-goat` | goatcore [#732](https://github.com/USAREUR-AF/goatcore/pull/732), awesome-goat [#1](https://github.com/USAREUR-AF/awesome-goat/pull/1) |

## 8. Contributing and CI

A fix now shows its failure on `main` before its pull request opens, and CI runs less for a pull request that changes only documents.

| Change | What you see | PR |
|---|---|---|
| A fix shows its failure first | `CONTRIBUTING.md`: a pull request that fixes a defect links the failing run or test on `main` | goatcore [#588](https://github.com/USAREUR-AF/goatcore/pull/588) |
| The check tells the author | `verified-commits` comments on the pull request when a commit is not verified | .github [#4](https://github.com/USAREUR-AF/.github/pull/4), goatcore [#660](https://github.com/USAREUR-AF/goatcore/pull/660) |
| Documents-only pull requests | `goatbuilder-pr` runs only the documents' configuration examples for a pull request of documents only | goatcore [#685](https://github.com/USAREUR-AF/goatcore/pull/685), [#704](https://github.com/USAREUR-AF/goatcore/pull/704), [#568](https://github.com/USAREUR-AF/goatcore/pull/568) |
| ADR index rows are rendered | The index rows of new ADRs come from the ADR files | goatcore [#636](https://github.com/USAREUR-AF/goatcore/pull/636) |
| A run on `main` is never cancelled | The next push to `main` no longer cancels the run before it | goatcore [#618](https://github.com/USAREUR-AF/goatcore/pull/618) |
| Generated files are held to their source | `.envrc.example` and the goat command reference are regenerated and compared in CI | goatcore [#627](https://github.com/USAREUR-AF/goatcore/pull/627), [#635](https://github.com/USAREUR-AF/goatcore/pull/635), [#633](https://github.com/USAREUR-AF/goatcore/pull/633) |
| The two-sovereign test runs in stages | One build stage and four scenario stages, each with its own cache key | goatcore [#602](https://github.com/USAREUR-AF/goatcore/pull/602), [#603](https://github.com/USAREUR-AF/goatcore/pull/603), [#638](https://github.com/USAREUR-AF/goatcore/pull/638), [#643](https://github.com/USAREUR-AF/goatcore/pull/643) |
| The weekly changelog merges itself | The weekly run merges its own pull request when every check passed | goatdocs [#22](https://github.com/USAREUR-AF/goatdocs/pull/22) |

## 9. Fixes for a running goatnet

These fixes change what a deploy does on a host. None needs action unless the "What to do" table lists it.

| Change | What you see | PR |
|---|---|---|
| A sign-in deploy never recreates the database | `ory-deploy.yml` reads the Postgres password itself and starts services with `--no-deps` | goatcore [#593](https://github.com/USAREUR-AF/goatcore/pull/593) |
| containerd's root is checked where it runs | The `docker-engine` role reads the running containerd's root before writing its configuration, and fails with containers running on a mismatch | goatcore [#664](https://github.com/USAREUR-AF/goatcore/pull/664) |
| The audit subscriber | Its lifecycle steps run `mc` with a writable `HOME`; a deploy fails when nothing cleans up stalled multipart uploads | goatcore [#595](https://github.com/USAREUR-AF/goatcore/pull/595), [#739](https://github.com/USAREUR-AF/goatcore/pull/739) |
| Rollback reaches a goatnet as deploy does | The rollback driver uses the goatnet's declared door and passes `--site` from the canary | goatcore [#644](https://github.com/USAREUR-AF/goatcore/pull/644), [#723](https://github.com/USAREUR-AF/goatcore/pull/723) |
| Values reach phases as values | An in-process init and `standup`'s phases get their values as run state, not through the process environment | goatcore [#641](https://github.com/USAREUR-AF/goatcore/pull/641), [#642](https://github.com/USAREUR-AF/goatcore/pull/642), [#740](https://github.com/USAREUR-AF/goatcore/pull/740) |
| Pre-disclosure patches per repository | The source check judges each pre-disclosure patch against its own repository | goatcore [#368](https://github.com/USAREUR-AF/goatcore/pull/368) |
| Dependency advisories | The feeds shim takes the fixed quinn-proto and quinn-udp | goatstuff [#83](https://github.com/USAREUR-AF/goatstuff/pull/83) |

## 10. Still in progress

These areas were moving when the window closed. Status words are the ones the repositories use.

| Area | State | Watch |
|---|---|---|
| goatbuilder 0.7.0 | **Release change merged; tag not published** | goatcore [#746](https://github.com/USAREUR-AF/goatcore/pull/746) |
| Both sides' acceptance in the command | **Open**: each side's signed result crosses the fabric, and `federate test --bilateral` runs phase 14 on a derived session | goatcore [#719](https://github.com/USAREUR-AF/goatcore/pull/719), [#720](https://github.com/USAREUR-AF/goatcore/pull/720), [#752](https://github.com/USAREUR-AF/goatcore/pull/752) |
| Key rotation as a command | **Open**: `federate rotate <partner>` for leaves and carrier; an IPsec leaf rotated from staged material; a new signing key handed to the directory, signed by the key it replaces | goatcore [#689](https://github.com/USAREUR-AF/goatcore/pull/689), [#763](https://github.com/USAREUR-AF/goatcore/pull/763), [#683](https://github.com/USAREUR-AF/goatcore/pull/683) |
| Two drivers | **Open**: the edge driver runs phase 1's edge checks; phase 3 hands the edge half over | goatcore [#717](https://github.com/USAREUR-AF/goatcore/pull/717), [#736](https://github.com/USAREUR-AF/goatcore/pull/736) |
| Back-out with two peerings | **Open**: backing out one of two peerings keeps the core leaf both use, or stops with GB-293 | goatcore [#716](https://github.com/USAREUR-AF/goatcore/pull/716) |
| The hub alone makes a platform admin | **Open**: a guard on identities, an alert when a guard refuses, access-rule cutover while cut off | goatcore [#722](https://github.com/USAREUR-AF/goatcore/pull/722), [#727](https://github.com/USAREUR-AF/goatcore/pull/727), [#708](https://github.com/USAREUR-AF/goatcore/pull/708) |
| Replication after a heal | **Open**: report and alert on rows a heal replaced by last-write-wins; count conflicts in every replicated database; migrate each site's database in turn | goatcore [#691](https://github.com/USAREUR-AF/goatcore/pull/691), [#710](https://github.com/USAREUR-AF/goatcore/pull/710), [#749](https://github.com/USAREUR-AF/goatcore/pull/749) |
| A joining site | **Open**: its own mesh DNS; every site's end state runs every service; a phone node; a clock check before changes | goatcore [#678](https://github.com/USAREUR-AF/goatcore/pull/678), [#671](https://github.com/USAREUR-AF/goatcore/pull/671), [#747](https://github.com/USAREUR-AF/goatcore/pull/747), [#766](https://github.com/USAREUR-AF/goatcore/pull/766) |
| A goatlite grows | **Open**: a goatlite configuration rewritten into the full preset, as a library | goatcore [#765](https://github.com/USAREUR-AF/goatcore/pull/765) |
| Trust refusals in the CLI | **Open**: `goat health --domain peer` and `goat top` show the trust-refusal reading | goatcore [#744](https://github.com/USAREUR-AF/goatcore/pull/744), [#745](https://github.com/USAREUR-AF/goatcore/pull/745) |
| The host firewall on an edge | **Draft**: the peering plays require the host firewall baseline on an edge (GB-279) | goatcore [#696](https://github.com/USAREUR-AF/goatcore/pull/696), [#707](https://github.com/USAREUR-AF/goatcore/pull/707) |
| The gym | **Open**: modules for an outside service, quality of service, events from a model at the edge, and coordination | goatstuff [#88](https://github.com/USAREUR-AF/goatstuff/pull/88), [#94](https://github.com/USAREUR-AF/goatstuff/pull/94), [#95](https://github.com/USAREUR-AF/goatstuff/pull/95) |
| Catalogs and scorecard | **Draft**: `publiccode.yml` and `code.json` for government code catalogs; a weekly OpenSSF Scorecard run | goatcore [#694](https://github.com/USAREUR-AF/goatcore/pull/694), [#695](https://github.com/USAREUR-AF/goatcore/pull/695) |
| Contributors' open work | **Open**: context completion, federation declarations kept during regeneration, the Raspberry Pi image checksum, the listener and ingress ADR; dependency and image pins (`HaterAndrew`); the edge's peering port, pytest in parallel (`joshkor1982`); Azure relays and certificates | goatcore [#444](https://github.com/USAREUR-AF/goatcore/pull/444), [#447](https://github.com/USAREUR-AF/goatcore/pull/447), [#449](https://github.com/USAREUR-AF/goatcore/pull/449), [#577](https://github.com/USAREUR-AF/goatcore/pull/577), [#592](https://github.com/USAREUR-AF/goatcore/pull/592), [#353](https://github.com/USAREUR-AF/goatcore/pull/353), [#437](https://github.com/USAREUR-AF/goatcore/pull/437), [#12](https://github.com/USAREUR-AF/goatcore/pull/12) |
| goatlite | **WIP**; the two-person drill is its gate | [`goatlite.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatlite.md) |

The maintainers' public roadmap, [github.com/orgs/USAREUR-AF/projects/8](https://github.com/orgs/USAREUR-AF/projects/8), lists open issues and pull requests by status.

## About this entry

- **Window.** Pull requests merged from 13 November 2026 16:10 UTC to 14 November 2026 19:22 UTC, in every public USAREUR-AF repository.
- **What "merged" means here.** A change is described as part of goat only when it merged into a repository's default branch. A pull request merged into any other branch is reported as in review.
- **The weekly listing.** [`weekly/`](weekly/INDEX.md) lists every merged pull request by kind, one page per ISO week, generated with no person or model in the loop. Written entries explain; the weekly listing is the complete record.
