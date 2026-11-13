# Changelog, 10 to 13 November 2026: federation is one goatbuilder command, and a stable line follows releases

Federating two goatnets is now one command, `goatbuilder federate <partner>`, released in goatbuilder 0.5.1 and 0.5.3. All work still lands on `main`, and a branch named `stable` is set up to follow whole-tree releases, so people who build on goat have a fixed line while `main` keeps moving. goatbuilder also has a written gate for version 1.0, with compatibility checked on every pull request.

This entry covers all 26 public [USAREUR-AF](https://github.com/USAREUR-AF) repositories, because a change in one usually lands with matching changes in others. It follows [the entry for 8 to 10 November](2026-11-10-signed-commits-one-build.md).

## In short

- **Contribute to `main`; build on a release.** A signed tag `goatcore/vX.Y.Z` marks a release of the whole repository, and the branch `stable` will point at the newest one. The workflow is built and first runs when the next such tag is cut ([section 1](#1-contributing-one-development-branch-and-a-stable-line)).
- **Outside pull requests are labeled `community`,** and `CONTRIBUTING.md` says what a contributor can expect from the maintainers ([section 1](#1-contributing-one-development-branch-and-a-stable-line)).
- **Federate with `goatbuilder federate <partner>`.** One run does all fourteen phases and stops only where a person must look. Use goatbuilder 0.5.3 ([section 2](#2-federation-is-one-goatbuilder-command)).
- **Two peerings on one edge and core are kept apart.** goat 0.5.19 grants each partner only the release sets agreed with it ([section 2](#2-federation-is-one-goatbuilder-command)).
- **A run shows what it does.** On `main`, every command is named before it runs and every run leaves a record. This ships in goatbuilder 0.6.0, which is in review ([section 3](#3-a-run-shows-what-it-does)).
- **goatbuilder 1.0 has a gate and a deprecation rule.** A deprecated command, flag or field keeps working for at least two minor releases and 90 days, and only a major release removes it ([section 4](#4-what-goatbuilder-10-will-promise)).
- **Browser interfaces are plain JavaScript with no build step,** and a new build or package manifest needs an owner and a reason ([section 6](#6-browser-interfaces-without-a-build-step)).

## What to do

| If you | Do this | Why |
|---|---|---|
| contribute to any repository | Open your pull request against `main`, as before. Never against `stable`: a pull request there is closed with a pointer to `main` | [ADR 1231](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1231-one-development-branch-and-a-stable-line-that-follows-releases.md) (goatcore [#581](https://github.com/USAREUR-AF/goatcore/pull/581)) |
| build on goat and want a fixed reference | Pin a release tag. When the first `goatcore/v` tag of the new line is cut, `stable` names the newest one | the same ADR; today the newest released tool versions are goatbuilder 0.5.3 and goat 0.5.19 |
| federate, or plan to | Install goatbuilder 0.5.3 and run `goatbuilder federate <partner>`. `goat federate <verb>` still runs and prints the goatbuilder command | [ADR 1225](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1225-federation-belongs-to-goatbuilder-one-command-one-decision.md) (goatcore [#343](https://github.com/USAREUR-AF/goatcore/pull/343), [#395](https://github.com/USAREUR-AF/goatcore/pull/395)) |
| run, or plan, a second peering on the same edge and core hosts | Use goat 0.5.19 and render the edge and core again. Move your peering directory to saltlick v0.5.0 before the second peering | Outward grants were the whole wire name `from/<us>/**`, so one partner's edge could read a set agreed only with another (goatcore [#267](https://github.com/USAREUR-AF/goatcore/pull/267), [#272](https://github.com/USAREUR-AF/goatcore/pull/272)); an older directory holds one package for every partner |
| script around federation acceptance | Treat exit status 3 as incomplete: acceptance exits 3 when any check was skipped | A skip is no longer a pass (goatcore [#343](https://github.com/USAREUR-AF/goatcore/pull/343)) |
| add a build or package manifest, such as a `package.json` | List it in `ops/ci/manifest-allowlist.txt` with an owner and a one-line reason, and pin every `package.json` dependency to an exact version | The check `manifest-allowlist` refuses it otherwise (goatcore [#326](https://github.com/USAREUR-AF/goatcore/pull/326), goatstuff [#49](https://github.com/USAREUR-AF/goatstuff/pull/49)) |
| run Alertmanager from the observability stack | Deploy the stack again to get the scrape and the two alerts on failing notifications | Alertmanager was the one service Prometheus did not scrape (goatcore [#421](https://github.com/USAREUR-AF/goatcore/pull/421)) |

## Who should read what

| If you | Read | Because |
|---|---|---|
| contribute code or documents | [1](#1-contributing-one-development-branch-and-a-stable-line), [6](#6-browser-interfaces-without-a-build-step) | where work lands, what the maintainers aim to do for you, and the rule for new manifests |
| build on goat, or pin it in your own environment | [1](#1-contributing-one-development-branch-and-a-stable-line), [4](#4-what-goatbuilder-10-will-promise) | which names stay fixed, and what will not change under you from 1.0 |
| federate with another goatnet, or plan to | [2](#2-federation-is-one-goatbuilder-command), [5](#5-hardening-fixes) | the procedure is one command, and several peerings on one host are kept apart |
| run a goatnet | [3](#3-a-run-shows-what-it-does), [7](#7-running-a-goatnet-and-the-smaller-repositories) | what a run prints and records, and fixes to alerting, roles and images |
| run a moon pod | [7](#7-running-a-goatnet-and-the-smaller-repositories) | a pod's router now forwards partner data to fabric-wide subscribers |

Each pull request's page names its author and any co-authors.

---

## 1. Contributing: one development branch and a stable line

Every change still lands on `main`, many times a day. What is new is a fixed line beside it: a signed tag for a release of the whole repository, and a branch that always points at the newest such tag.

![A pull request from anyone passes checks and review and merges to main; a minor release is tagged from main, a signed whole-tree tag is cut at the same commit, and the stable branch moves to that tag](figures/2026-11-13/stable-line.svg)

| Name | What it is | Use it when |
|---|---|---|
| `main` | the one development branch | you are contributing |
| `goatcore/vX.Y.Z` | a signed tag for the whole repository, at the commit of the goatbuilder release with the same version, cut at a minor release after that commit has run in the maintainers' environments | you want a fixed reference |
| `stable` | a branch that points at the newest `goatcore/v` tag and takes no pull requests | you want the newest release by a name that does not change |

| Change | What you see | PR |
|---|---|---|
| The stable line ([ADR 1231](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1231-one-development-branch-and-a-stable-line-that-follows-releases.md), accepted) | `.github/workflows/stable.yml` moves `stable` when a `goatcore/v` tag is pushed, and only after `ops/release/stable.py check` confirms the tag is on `main` and shares its commit with `goatbuilder/v` of the same version. The release page lists the tool versions that go together. **Built; it first runs when the next `goatcore/v` tag is cut** | goatcore [#581](https://github.com/USAREUR-AF/goatcore/pull/581) |
| `stable` takes no direct work | A pull request against `stable` is closed with a comment that points to `main`. A push to it that is not a tagged release fails `stable-guard`, and a ruleset refuses deleting it or moving it backward | goatcore [#581](https://github.com/USAREUR-AF/goatcore/pull/581) |
| Outside pull requests are labeled | `contributor-trust` adds the label `community` to a pull request whose author is not a member of the organization, so the maintainers can list them | goatcore [#582](https://github.com/USAREUR-AF/goatcore/pull/582) |
| What a contributor can expect | `CONTRIBUTING.md` has a section for it. Once you are validated, the maintainers aim to reply within one working day. It is an aim, not a guarantee. You are validated when you are registered in a goat community environment with a linked GitHub account, or have an earlier merged pull request | goatcore [#581](https://github.com/USAREUR-AF/goatcore/pull/581), [#582](https://github.com/USAREUR-AF/goatcore/pull/582) |
| No approvals required, and no bypass | The rulesets on the public repositories require zero approving reviews and have no bypass actors. An owner merges on green checks; a required check that fails or never starts blocks everyone, owners included | [ADR 1221](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1221-outside-contributions-need-a-known-author-or-a-recorded-security-review.md) (goatcore [#340](https://github.com/USAREUR-AF/goatcore/pull/340), [#346](https://github.com/USAREUR-AF/goatcore/pull/346)) |
| The NetBird fork runs `contributor-trust` | The same check as every other repository | netbird [#1](https://github.com/USAREUR-AF/netbird/pull/1) |

The design is in [`community-and-stable-line.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/community-and-stable-line.md).

## 2. Federation is one goatbuilder command

`goatbuilder federate <partner>` runs the whole procedure between two sovereign goatnets. You decide the partner and the release sets it receives; the command derives everything else from what the deployment already declares, records each phase, and resumes where it stopped.

![You name the partner and the release sets it receives; goatbuilder federate then runs all fourteen phases and stops three times for a person: the partner's key and CA fingerprint read aloud, approval of the plan's hash, and approval of what our core will admit; it then deploys the transport, the edge and SPIRE and runs acceptance last](figures/2026-11-13/federate-one-command.svg)

The previous entry reported this work as in review on the branch `integration/federation-turnkey`. It reached `main` in two promotions, and the pull requests that entry listed are part of them.

| Change | What you see | PR |
|---|---|---|
| One command | `goatbuilder federate xab` at a terminal does every phase. It asks for the partner's verifying key and CA fingerprint, shows the plan and asks you to approve its hash, shows what your core will admit and asks you to approve that. The core router restarts only after that approval. Acceptance runs last | goatcore [#343](https://github.com/USAREUR-AF/goatcore/pull/343), [#395](https://github.com/USAREUR-AF/goatcore/pull/395) |
| Each part by itself | `goatbuilder federate plan`, `deploy`, `test`, `status` and `backout` | goatcore [#395](https://github.com/USAREUR-AF/goatcore/pull/395) |
| Peerings are declared | `goatbuilder federate allocate` writes each peering's interface, port and addresses from the `peerings:` declaration. Nothing is numbered by hand | goatcore [#343](https://github.com/USAREUR-AF/goatcore/pull/343), [#395](https://github.com/USAREUR-AF/goatcore/pull/395) |
| Acceptance is evidence | It generates its checks from the agreement, writes a versioned evidence bundle per run, and exits 3 when any check was skipped | goatcore [#343](https://github.com/USAREUR-AF/goatcore/pull/343) |
| Several peerings on one edge and core | Each outward grant names one offered release set. A second peering is refused when it would reuse another's inventory name, interface, port, address or metrics port. A three-party test covers it | goatcore [#267](https://github.com/USAREUR-AF/goatcore/pull/267), [#272](https://github.com/USAREUR-AF/goatcore/pull/272), [#271](https://github.com/USAREUR-AF/goatcore/pull/271) |
| The edge role finds the core router | the way `goat federate init` does | goatcore [#243](https://github.com/USAREUR-AF/goatcore/pull/243) |
| The documents match the command | Ten statements in the federation documents were corrected against the released code, and the fourteen phases are described in one catalog, `ops/phases/catalog.yaml`, from which the runbook's table is rendered | goatcore [#427](https://github.com/USAREUR-AF/goatcore/pull/427), [#494](https://github.com/USAREUR-AF/goatcore/pull/494) |

### Releases

| Release | Carries |
|---|---|
| [goat-cli-v0.5.19](https://github.com/USAREUR-AF/goatcore/releases/tag/goat-cli-v0.5.19) | outward grants per offered set, the second-peering refusals, and the WireGuard key passed to `wg` through a pipe (goatcore [#335](https://github.com/USAREUR-AF/goatcore/pull/335), [#273](https://github.com/USAREUR-AF/goatcore/pull/273)) |
| [goatbuilder/v0.5.1](https://github.com/USAREUR-AF/goatcore/releases/tag/goatbuilder/v0.5.1) | `goatbuilder federate` (goatcore [#424](https://github.com/USAREUR-AF/goatcore/pull/424)) |
| [goatbuilder/v0.5.3](https://github.com/USAREUR-AF/goatcore/releases/tag/goatbuilder/v0.5.3) | the corrected federation documents, declared values passed to each phase as one word, `verify` reading a failed ledger read as unknown, private keys removed after an interrupted phase 8 (goatcore [#450](https://github.com/USAREUR-AF/goatcore/pull/450), [#509](https://github.com/USAREUR-AF/goatcore/pull/509)) |

The tags `goatbuilder/v0.5.0` and `goatbuilder/v0.5.2` exist and have no published release. Install 0.5.3.

### On main, for goatbuilder 0.6.0

| Change | What you see | PR |
|---|---|---|
| One directory package per partner by default | Phase 5 publishes a package for each counterparty, so a second peering does not replace the first one's package. **Behavior change:** with a directory older than saltlick v0.5.0 the command says so, keeps the single package, and stops for a confirmation before it places the partner's package. `FED_DIRECTORY_PER_COUNTERPARTY=0` keeps the earlier behavior | goatcore [#552](https://github.com/USAREUR-AF/goatcore/pull/552), [#549](https://github.com/USAREUR-AF/goatcore/pull/549), [#522](https://github.com/USAREUR-AF/goatcore/pull/522) |
| A back-out reads the core the way admission wrote it | `goatbuilder federate backout <partner>` surveys through the admission's inventories, refuses a survey no host answers, and leaves the core's org fragment byte for byte as it was | goatcore [#459](https://github.com/USAREUR-AF/goatcore/pull/459), [#526](https://github.com/USAREUR-AF/goatcore/pull/526), [#531](https://github.com/USAREUR-AF/goatcore/pull/531) |
| Admission keeps the rest of the core's peerings file | It replaces only the list it owns and refuses a file it cannot read as literal entries (GB-237) | goatcore [#516](https://github.com/USAREUR-AF/goatcore/pull/516), [#476](https://github.com/USAREUR-AF/goatcore/pull/476) |
| One side at a time | Phase 1 and phase 3 take `--side edge` or `--side core`, for a site where no single machine reaches both hosts. The full run does not yet hand over between two machines; the contract for that is designed in [`federation-two-drivers.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/federation-two-drivers.md) | goatcore [#482](https://github.com/USAREUR-AF/goatcore/pull/482), [#558](https://github.com/USAREUR-AF/goatcore/pull/558), [#462](https://github.com/USAREUR-AF/goatcore/pull/462), [#491](https://github.com/USAREUR-AF/goatcore/pull/491) |
| Key rotation for a peering | Designed in [`federation-key-rotation.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/federation-key-rotation.md). Rotating a peering's leaves is built as a library and tested on a running peering with data flowing; no command reaches it yet. A recorded rotation makes phase 3 measure the package again | goatcore [#490](https://github.com/USAREUR-AF/goatcore/pull/490), [#493](https://github.com/USAREUR-AF/goatcore/pull/493), [#514](https://github.com/USAREUR-AF/goatcore/pull/514), [#481](https://github.com/USAREUR-AF/goatcore/pull/481) |
| A journal from a later goatbuilder is read | An outcome word or field this build does not know is kept and shown as written; only a later schema is refused (GB-182) | goatcore [#485](https://github.com/USAREUR-AF/goatcore/pull/485) |

## 3. A run shows what it does

On `main`, goatbuilder names every command before it runs it and keeps a record of every run. These changes ship in goatbuilder 0.6.0, whose version pull request is open (goatcore [#589](https://github.com/USAREUR-AF/goatcore/pull/589)); no released binary has them yet.

![A dry run prints every command the real run will execute; during the run each command is named in a frame before it prints and its output is kept in a log; when the run ends a record is written, and the commands runs, show and runs diff read it later](figures/2026-11-13/run-record.svg)

| Change | What you see | PR |
|---|---|---|
| Every process is named first | Each child process starts through one runner. Before it prints anything, a frame on stderr gives the phase, its purpose, the exact command, the host and the log path | goatcore [#507](https://github.com/USAREUR-AF/goatcore/pull/507), [#553](https://github.com/USAREUR-AF/goatcore/pull/553), [#555](https://github.com/USAREUR-AF/goatcore/pull/555), [#556](https://github.com/USAREUR-AF/goatcore/pull/556) |
| A record of every run | A verb that drives hosts writes `<state>/runs/<id>/run.json` (mode 0600; no secret value is written). `goatbuilder runs` lists the records, `show <run>` prints one, and `runs diff <a> <b>` compares two | goatcore [#550](https://github.com/USAREUR-AF/goatcore/pull/550) |
| A dry run prints the real commands | `--dry-run` at a terminal shows each phase's command on one line, as the real run executes it | goatcore [#536](https://github.com/USAREUR-AF/goatcore/pull/536) |
| `explain` answers for a phase | `goatbuilder explain federate 8` says what the phase does, why, what it changes, how to tell it worked, and its command by hand | goatcore [#551](https://github.com/USAREUR-AF/goatcore/pull/551) |
| A failed federate phase is interpreted | Its output is matched against the error catalog, and the failure carries the matching code with its likely cause and fix, the log, and the command to retry that phase alone | goatcore [#585](https://github.com/USAREUR-AF/goatcore/pull/585) |
| `update` verifies the release signature itself | `goatbuilder update` checks the signature with no `cosign` installed, and refuses a release whose signature does not verify or is not served (GB-261). **Behavior change:** an install without `cosign` used to proceed with the signature not checked | goatcore [#524](https://github.com/USAREUR-AF/goatcore/pull/524) |
| `status` reads real hosts | It reads them the way `diff` does and grades them by `verify`'s rule | goatcore [#474](https://github.com/USAREUR-AF/goatcore/pull/474) |

Built as libraries, with no command yet: listing every value a run uses with its source, and tracing a value back through its sources (goatcore [#515](https://github.com/USAREUR-AF/goatcore/pull/515), [#529](https://github.com/USAREUR-AF/goatcore/pull/529)). The design is [`goatbuilder-legibility.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatbuilder-legibility.md).

## 4. What goatbuilder 1.0 will promise

Version 1.0 will be the first goatbuilder release that carries a promise: a deployment that works on 1.0 keeps working on every later 1.x release with no change to its files or to the programs that call the binary. The gate that decides 1.0 is written, is not yet met, and several of its rows are already tests that run on every pull request.

![A flag deprecated in release 1.2 keeps working with a warning through 1.3 and 1.4 and until 90 days have passed, and is removed only in major release 2.0](figures/2026-11-13/deprecation.svg)

| Change | What you see | PR |
|---|---|---|
| The gate | [`goatbuilder-v1-gate.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatbuilder-v1-gate.md) names four surfaces other people build on (the configuration, the commands with their flags and exit codes, the `-o json` and `-o yaml` documents, the `GB-nnn` error codes) and one test per requirement | goatcore [#406](https://github.com/USAREUR-AF/goatcore/pull/406), [#527](https://github.com/USAREUR-AF/goatcore/pull/527) |
| The deprecation rule ([ADR 1228](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1228-goatbuilder-keeps-its-four-surfaces-and-removes-only-in-a-major-release.md), accepted) | From 1.0 the four surfaces change only by additions. A deprecated command, flag or field warns for at least two minor releases and 90 days, and only a major release removes it. The library that prints the warning is built; nothing is deprecated with it yet | goatcore [#457](https://github.com/USAREUR-AF/goatcore/pull/457), [#579](https://github.com/USAREUR-AF/goatcore/pull/579), [#567](https://github.com/USAREUR-AF/goatcore/pull/567) |
| Compatibility is checked on every pull request | Configuration files from each published release since 0.4.1 are kept and validated. Commands, flags, documents and error codes are compared with a baseline recorded from the published 0.5.1 binary | goatcore [#571](https://github.com/USAREUR-AF/goatcore/pull/571), [#464](https://github.com/USAREUR-AF/goatcore/pull/464) |
| An error code is never lost | A code a release printed cannot be dropped or retitled, so `explain` keeps answering for it | goatcore [#559](https://github.com/USAREUR-AF/goatcore/pull/559) |
| Upgrades are tested | A deployment made with 0.4.3 or 0.5.1 continues on the current build, a peering 0.5.1 took to phase 10 is finished by it, and `update` moves a 0.5.1 install to it and back | goatcore [#454](https://github.com/USAREUR-AF/goatcore/pull/454), [#461](https://github.com/USAREUR-AF/goatcore/pull/461), [#510](https://github.com/USAREUR-AF/goatcore/pull/510) |
| Two groups joined the gate | A node on a phone (group H) and a joined site that keeps running when cut off (group I). Both are designed | goatcore [#576](https://github.com/USAREUR-AF/goatcore/pull/576), [#587](https://github.com/USAREUR-AF/goatcore/pull/587) |
| A goatlite can grow | Growth from a goatlite into a full environment without a tear-down is designed in [`goatlite-growth.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatlite-growth.md) | goatcore [#468](https://github.com/USAREUR-AF/goatcore/pull/468) |

## 5. Hardening fixes

Values and keys now reach the commands goatbuilder runs as data, never as shell text, and the edge refuses more configurations it cannot verify. None of these changes needs action unless a row says the behavior changed.

| Change | What you see | PR |
|---|---|---|
| Declared values are one word each | A value from group_vars, the inventory or a declaration that contains `$(…)`, a backtick or `;` is passed to a phase as data and is not run by the shell. Plain values are written as before | goatcore [#477](https://github.com/USAREUR-AF/goatcore/pull/477), [#478](https://github.com/USAREUR-AF/goatcore/pull/478), [#496](https://github.com/USAREUR-AF/goatcore/pull/496), [#499](https://github.com/USAREUR-AF/goatcore/pull/499), [#570](https://github.com/USAREUR-AF/goatcore/pull/570) |
| Keys stay out of argv and the environment | The WireGuard key goes to `wg` through a pipe; a federate run keeps its derived values out of the process environment; an interrupted leaf mint leaves no key material behind | goatcore [#273](https://github.com/USAREUR-AF/goatcore/pull/273), [#498](https://github.com/USAREUR-AF/goatcore/pull/498), [#458](https://github.com/USAREUR-AF/goatcore/pull/458) |
| The edge reads the core where it runs | The edge role's ingress check reads the core's configuration on the core's own host, at the path the router's arguments name. **Behavior change:** a core whose arguments the check cannot read stops phase 12 | goatcore [#475](https://github.com/USAREUR-AF/goatcore/pull/475), [#520](https://github.com/USAREUR-AF/goatcore/pull/520), [#537](https://github.com/USAREUR-AF/goatcore/pull/537) |
| The edge refuses a key storage wider than its grant | Every storage under `keys/` that `goat_zenoh_edge_key_bundle_key_exprs` does not include is refused, and the comparison fails closed. **Behavior change:** such a core fails the edge role | goatcore [#538](https://github.com/USAREUR-AF/goatcore/pull/538), [#539](https://github.com/USAREUR-AF/goatcore/pull/539) |
| Dependency advisories | Go builds and scans on 1.26.11 for GO-2026-6859. quinn-udp 0.5.16 and quinn-proto 0.11.19 answer RUSTSEC-2026-0523, -0524 and -0538; a host runs them once its image pin moves to a build after the change | goatcore [#405](https://github.com/USAREUR-AF/goatcore/pull/405), [#590](https://github.com/USAREUR-AF/goatcore/pull/590) |
| Rust toolchain pinned | Every workflow builds with Rust 1.100.0, and a floating toolchain is refused | goatcore [#488](https://github.com/USAREUR-AF/goatcore/pull/488) |

## 6. Browser interfaces without a build step

The default for a goat browser interface is hand-written HTML, CSS and JavaScript modules served as files, with no bundler, transpiler or framework. TypeScript stays allowed for a frontend too complex for that default, for a library other teams consume from TypeScript, and for Playwright tests.

| Change | What you see | PR |
|---|---|---|
| The rule | `engineering-baseline.md` entry 12.4: a new language, framework or package manager needs a written reason and a named owner before it lands. A third-party browser library is one vendored file with its version and license noted | goatdocs [#17](https://github.com/USAREUR-AF/goatdocs/pull/17), [#20](https://github.com/USAREUR-AF/goatdocs/pull/20); goatcore [#439](https://github.com/USAREUR-AF/goatcore/pull/439) |
| The check | `manifest-allowlist` refuses a build or package manifest that is not in `ops/ci/manifest-allowlist.txt`, and a `package.json` dependency that is not an exact version | goatcore [#326](https://github.com/USAREUR-AF/goatcore/pull/326), goatstuff [#49](https://github.com/USAREUR-AF/goatstuff/pull/49) |
| Four interfaces converted | panoscope (d3 vendored as one file), the trust sandbox, the zenoh sandbox (zenoh-ts vendored as one checked file) and the smoketest dashboard are plain JavaScript with no npm install and no build | goatstuff [#51](https://github.com/USAREUR-AF/goatstuff/pull/51), [#50](https://github.com/USAREUR-AF/goatstuff/pull/50), [#57](https://github.com/USAREUR-AF/goatstuff/pull/57); goatcore [#327](https://github.com/USAREUR-AF/goatcore/pull/327) |

## 7. Running a goatnet, and the smaller repositories

Alerting now reports its own delivery failures, several roles run on more hosts, and CI no longer depends on one package mirror.

| Change | What you see | PR |
|---|---|---|
| Alertmanager is scraped | Prometheus scrapes Alertmanager and alerts when notifications fail. A large alert group reaches ntfy as one bounded notification, and `webhook-noop` is a true null receiver | goatcore [#421](https://github.com/USAREUR-AF/goatcore/pull/421), [#419](https://github.com/USAREUR-AF/goatcore/pull/419), [#420](https://github.com/USAREUR-AF/goatcore/pull/420) (`joshkor1982`) |
| A rotated CA does not fail the deploy | The `goat-zenoh` trust-anchor check ignores an issuer that has already expired. A valid issuer that disappears still fails | goatcore [#413](https://github.com/USAREUR-AF/goatcore/pull/413) (`joshkor1982`) |
| Audit eviction fails loudly | `audit-fifo-evict` reports an error when storage is over its high-water mark and eviction is disabled | goatcore [#414](https://github.com/USAREUR-AF/goatcore/pull/414) (`joshkor1982`) |
| Audit readers use bounded memory | `audit-tail`, stethoscope and microscope fold events as they arrive | goatcore [#319](https://github.com/USAREUR-AF/goatcore/pull/319), goatstuff [#45](https://github.com/USAREUR-AF/goatstuff/pull/45) |
| Debian 13 hosts | The `docker-engine` role takes Docker's apt repository from the host's distribution, and the `pgbackrest` role installs `cron` before it writes the backup schedule | goatcore [#519](https://github.com/USAREUR-AF/goatcore/pull/519), [#578](https://github.com/USAREUR-AF/goatcore/pull/578) |
| The status page's list refreshes alone | `ops/ansible/isitup-rows.yml` renders the probe list and recreates only its container; `ops/scripts/isitup-list.py check` fails when a host's list is behind its declaration | goatcore [#586](https://github.com/USAREUR-AF/goatcore/pull/586) |
| Health roll-ups on a paired site | A site's roll-up skips the pair's passive node | goatcore [#440](https://github.com/USAREUR-AF/goatcore/pull/440) |
| A runtime-health gate on the release ladder | A component moves up only when it ran on the lower rung with no restarts over the soak | goatcore [#320](https://github.com/USAREUR-AF/goatcore/pull/320) |
| Runtime pins and Terraform | Refreshed pins for the federation proxy and the Blackbox Exporter, described egress rules in the host modules, Vite 6.4.6 in two dashboards, a warning for malformed numeric configuration in microscope | goatcore [#376](https://github.com/USAREUR-AF/goatcore/pull/376), [#379](https://github.com/USAREUR-AF/goatcore/pull/379), [#334](https://github.com/USAREUR-AF/goatcore/pull/334), [#325](https://github.com/USAREUR-AF/goatcore/pull/325); goatstuff [#48](https://github.com/USAREUR-AF/goatstuff/pull/48), [#58](https://github.com/USAREUR-AF/goatstuff/pull/58) (`HaterAndrew`) |
| A moon pod forwards partner data | Data a partner publishes through the pod's local router now reaches fabric-wide subscribers such as the audit and catalog services. Before, it left the pod only when a consumer subscribed under the pod's own slot, and the publisher saw no error | zagros-moon-pod [#12](https://github.com/USAREUR-AF/zagros-moon-pod/pull/12) (`volandmag`) |
| CI does not depend on one mirror | When a runner cannot reach Ubuntu's package mirror, jobs fail over to the project's own package cache image. A workflow that calls another without granting the permissions it asks for fails a check | goatcore [#426](https://github.com/USAREUR-AF/goatcore/pull/426), [#453](https://github.com/USAREUR-AF/goatcore/pull/453), [#505](https://github.com/USAREUR-AF/goatcore/pull/505) |
| The weekly changelog run | Where a workflow may not open a pull request, the weekly run commits the page to a branch and opens an issue with the link | goatdocs [#18](https://github.com/USAREUR-AF/goatdocs/pull/18) |

## 8. Still in progress

These areas are moving now. Status words are the ones the repositories use.

| Area | State | Watch |
|---|---|---|
| goatbuilder 0.6.0 | **In review**: the version pull request. It releases sections 2 and 3's "on main" changes | goatcore [#589](https://github.com/USAREUR-AF/goatcore/pull/589) |
| The stable line | **Built, not yet run**: `stable` appears when the next `goatcore/v` tag is cut at a goatbuilder minor release | [`community-and-stable-line.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/community-and-stable-line.md) |
| Back-out of a peering | **Open**: probes that cannot tell report unknown, never absent; the driver backs out a core admission it placed. Back-out measured on running hosts is not in 0.6.0 | goatcore [#543](https://github.com/USAREUR-AF/goatcore/pull/543), [#530](https://github.com/USAREUR-AF/goatcore/pull/530) |
| Compatibility baseline | **Open**: the baseline moves to the published 0.5.3; every refusal names its catalog code | goatcore [#561](https://github.com/USAREUR-AF/goatcore/pull/561), [#560](https://github.com/USAREUR-AF/goatcore/pull/560) |
| Proposed decisions | [ADR 1229](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1229-a-partners-new-package-is-confirmed-within-confirmation-1.md) **proposed**: a partner's new package under the same key is confirmed within the first confirmation. ADR 1225 stays **proposed** | goatcore [#512](https://github.com/USAREUR-AF/goatcore/pull/512) |
| Federation package, listener and ingress | **Open**: an ADR that separates the listener target from the ingress policy in package version 2 | goatcore [#577](https://github.com/USAREUR-AF/goatcore/pull/577) |
| CLI, federation and image fixes from a contributor | **Open**: context completion, federation declarations kept during regeneration, the Raspberry Pi image checksum, warrant membership versions explained | goatcore [#444](https://github.com/USAREUR-AF/goatcore/pull/444), [#447](https://github.com/USAREUR-AF/goatcore/pull/447), [#449](https://github.com/USAREUR-AF/goatcore/pull/449), [#408](https://github.com/USAREUR-AF/goatcore/pull/408) |
| Dependency and image pins | **Open** (`HaterAndrew`): Go modules, service runtime pins, SPIRE staged upgrades, the health publishers' dependencies | goatcore [#308](https://github.com/USAREUR-AF/goatcore/pull/308), [#359](https://github.com/USAREUR-AF/goatcore/pull/359), [#592](https://github.com/USAREUR-AF/goatcore/pull/592); goatstuff [#60](https://github.com/USAREUR-AF/goatstuff/pull/60) and siblings |
| The edge's peering port | **Open** (`joshkor1982`): default 51823, clear of NetBird's 51820 | goatcore [#353](https://github.com/USAREUR-AF/goatcore/pull/353) |
| Azure | **Open**: relays and certificates on Azure, with the standup fixes split into drafts | goatcore [#12](https://github.com/USAREUR-AF/goatcore/pull/12), [#111](https://github.com/USAREUR-AF/goatcore/pull/111) to [#122](https://github.com/USAREUR-AF/goatcore/pull/122) |
| Portal resilience | **Open** (`0mlml`): panicking requests access-logged. The roster parsed once per change merged in this window (goatcore [#76](https://github.com/USAREUR-AF/goatcore/pull/76)) | goatcore [#75](https://github.com/USAREUR-AF/goatcore/pull/75) |
| Topology view | **Open**: every router in the fabric drawn, with labels that tell routers apart | goatstuff [#73](https://github.com/USAREUR-AF/goatstuff/pull/73), [#74](https://github.com/USAREUR-AF/goatstuff/pull/74) |
| goatlite | **WIP**; the two-person drill is its gate | [`goatlite.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatlite.md) |

The maintainers' public roadmap, [github.com/orgs/USAREUR-AF/projects/8](https://github.com/orgs/USAREUR-AF/projects/8), lists open issues and pull requests by status.

## About this entry

- **Window.** Pull requests merged from 10 November 2026 05:00 UTC to 13 November 2026 16:10 UTC, in every public USAREUR-AF repository.
- **What "merged" means here.** A change is described as part of goat only when it merged into a repository's default branch. A pull request merged into any other branch is reported as in review.
- **The weekly listing.** [`weekly/`](weekly/INDEX.md) lists every merged pull request by kind, one page per ISO week, generated with no person or model in the loop. Written entries explain; the weekly listing is the complete record.
