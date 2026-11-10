# Changelog, 8 to 10 November 2026: signed commits everywhere, and one build for every deployment

Two rules now hold in every public goat repository: each commit in a pull request must carry a signature GitHub verifies, and an outside contribution needs a known author or a recorded security review. In the same two days the tools stopped carrying any one deployment's values inside the build, federation gained fixes found by people running it, and work began to make federation one `goatbuilder` command.

This entry covers all 26 public [USAREUR-AF](https://github.com/USAREUR-AF) repositories, because a change in one usually lands with matching changes in others. It follows [the entry for 6 to 8 November](2026-11-08-forty-eight-hours.md).

## In short

- **Sign your commits.** A pull request with any unverified commit cannot merge, in any repository ([section 1](#1-contributing-two-required-checks-in-every-repository)).
- **Upgrade to goat 0.5.18 and goatbuilder 0.4.3.** They read your deployment's ACL declaration and release source from configuration. Nothing of any deployment is compiled in ([section 2](#2-one-build-for-every-deployment)).
- **A deploy now stops on an unresolved secret reference.** A value that still reads `op://`, `bao://` or `bw://` is refused before the play starts, where it used to reach a container as a literal string ([section 4](#4-secrets-and-deploy-safety)).
- **Federation works with the standard core router role,** keeps received data per partner, and reuses its certificates when a phase is run again ([section 3](#3-federation)).
- **Every image is public.** A first goatnet needs no registry token, and the README's first run uses a released `goatbuilder` binary with no build ([section 5](#5-a-first-goatnet-goatlite)).
- **Two decisions about sharing between nations are proposed,** and the documents now say plainly that each nation runs its own environment ([section 3](#decisions-about-sharing-between-nations)).
- **Not in `main` yet:** federation as one `goatbuilder federate <partner>` command is in review on an integration branch ([section 3](#in-review-federation-as-one-goatbuilder-command)).

## What to do

| If you | Do this | Why |
|---|---|---|
| contribute to any repository | Set up commit signing once, and sign every commit. To repair a branch: `git rebase --exec 'git commit --amend --no-edit -S' origin/main`, then `git push --force-with-lease` | The check `verified-commits` is required by an organization ruleset ([ADR 1226](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1226-every-commit-in-a-pull-request-is-signed-and-verified.md)) |
| run `goat acl` or `goat warrant` against your own ACL declaration | Point the command at it: `--declaration <dir>`, or `GOAT_ACL_DECLARATION_DIR`, or `acl_declaration_dir` in the context's `profile.toml` | goat 0.5.17 and later compile in no ACL table (goatcore [#178](https://github.com/USAREUR-AF/goatcore/pull/178)) |
| publish your own goatbuilder releases from a fork | Declare `repo.release_source` in `ops/goatbuilder/project.yml`, after you serve goatbuilder 0.4.3 | `goatbuilder update` takes its release signer from configuration; 0.4.2 rejects the key (goatcore [#220](https://github.com/USAREUR-AF/goatcore/pull/220), [#227](https://github.com/USAREUR-AF/goatcore/pull/227)) |
| deploy netvis, panoscope, trust-sandbox or snitch | Re-run the role when you take the new image. It now mounts your declaration and sets the values the image used to carry | These images read every deployment value at start (goatstuff [#29](https://github.com/USAREUR-AF/goatstuff/pull/29), goatcore [#181](https://github.com/USAREUR-AF/goatcore/pull/181)) |
| federate from a goatnet deployed with the standard `goat-zenoh` role | Use goat 0.5.18 for `goat federate init` | 0.5.17 looks only for a container named `goat-zenoh` and stops at phase 3 (goatcore [#239](https://github.com/USAREUR-AF/goatcore/pull/239)) |
| already federate | Re-render the core router so it has one store per partner, and pass `--rotate` only when you mean to replace peering certificates | A store on `from/**` kept nothing behind an edge that grants `from/<peer>/**`; a rerun of phase 8 used to mint new keys (goatcore [#235](https://github.com/USAREUR-AF/goatcore/pull/235), [#236](https://github.com/USAREUR-AF/goatcore/pull/236)) |
| run service health checks against a private CA | Give the check its `ca_file` | HTTPS service checks now verify the certificate chain and hostname (goatcore [#7](https://github.com/USAREUR-AF/goatcore/pull/7)) |
| pull images with `GHCR_READ_TOKEN` | Remove the token | All 27 pinned images and `goat-relay` pull without credentials (goatcore [#222](https://github.com/USAREUR-AF/goatcore/pull/222)) |

## Who should read what

| If you | Read | Because |
|---|---|---|
| contribute code or documents | [1](#1-contributing-two-required-checks-in-every-repository), [7](#7-still-in-progress) | two checks decide whether your pull request can merge, and several areas are changing under you |
| run a goatnet | [2](#2-one-build-for-every-deployment), [4](#4-secrets-and-deploy-safety) | the tools read your values from configuration, and the deploy preflight refuses more mistakes before it touches a host |
| federate with another goatnet, or plan to | [3](#3-federation) | fixes to the path on `main`, two proposed decisions, and the one-command procedure in review |
| are standing up your first goatnet | [5](#5-a-first-goatnet-goatlite) | the tutorial was followed as written on clean machines and corrected where it failed |
| operate the portal, snitch or a pod | [6](#6-security-fixes-and-the-smaller-repositories) | browser sessions, TLS checks and dependency advisories |

Each pull request's page names its author and any co-authors.

---

## 1. Contributing: two required checks in every repository

A pull request now passes two checks before an owner's review counts. Every commit in it must be signed with a signature GitHub verifies, and its author must be known to the project or the change must carry a recorded security review. Both are required on the default branch of all 26 public repositories.

![A pull request is opened, every commit in it must carry a signature GitHub verifies, its author must be known or the change must have a recorded security review, an owner reviews it, and only then is it squash-merged to main; the two middle checks are required in all 26 public repositories](figures/2026-11-10/pull-request-checks.svg)

| Check | What it refuses | Where it is defined |
|---|---|---|
| `verified-commits` | a pull request that holds any commit GitHub does not verify. Branch protection's own "require signed commits" sees only the squash commit, which GitHub signs whatever the pull request held | [ADR 1226](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1226-every-commit-in-a-pull-request-is-signed-and-verified.md) (goatcore [#283](https://github.com/USAREUR-AF/goatcore/pull/283)); the workflow lives in the organization's `.github` repository ([#2](https://github.com/USAREUR-AF/.github/pull/2)) and one organization ruleset requires it everywhere |
| `contributor-trust` | a change from an unknown author with no `security-reviewed` label, and a change from a known author to a path listed in `.github/contributor-trust/sensitive-paths.txt` without one | [ADR 1221](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1221-outside-contributions-need-a-known-author-or-a-recorded-security-review.md). It was in six repositories and is now required in all of them (goatcore [#318](https://github.com/USAREUR-AF/goatcore/pull/318), `.github` [#3](https://github.com/USAREUR-AF/.github/pull/3) and one pull request in each remaining repository) |

- **A pull request opened before a new required check exists does not run it.** Push a commit, or close and reopen the pull request, and the check runs.
- **Automation commits through the GitHub API,** which signs the commit. goatdocs' own weekly changelog does this ([below](#about-this-entry)).
- **`AGENTS.md` in goatcore names each component's build and test commands,** their prerequisites, and the rule that a skipped check is not a pass (goatcore [#195](https://github.com/USAREUR-AF/goatcore/pull/195), from `rsivilli`).
- **`INTENT.md` opens with what to do:** treat the project as Apache 2.0, which covers you everywhere. The Code.mil statement follows word for word. The same change landed in every repository (goatcore [#264](https://github.com/USAREUR-AF/goatcore/pull/264) and its siblings). No licensing changed.

## 2. One build for every deployment

`goat`, `goatbuilder` and the images no longer carry any deployment's values. Each reads them from configuration when it runs, and stops with a named error when one is missing. One released binary and one image therefore serve every goatnet, including yours.

![Before, three tools carried one deployment's values inside the build: the ACL tables in goat, a repository name in goatbuilder, and one deployment's rules in the netvis image. Now each reads those values from configuration when it runs, and stops with a named error when they are missing](figures/2026-11-10/one-build.svg)

| Tool | Before | Now | PR |
|---|---|---|---|
| `goat acl`, `goat warrant` | the ACL taxonomy and matrix were compiled in with `include_str!` | read from the first of: `--declaration <dir>`, `GOAT_ACL_DECLARATION_DIR`, the context's `acl_declaration_dir` or `acl/` directory, the checkout's `ops/ansible/` | goatcore [#178](https://github.com/USAREUR-AF/goatcore/pull/178) |
| `goatbuilder update` | a repository name was compiled in | the release signer comes from `repo.release_source`, else `repo.source`; `gen-config.py` carries the key from `project.yml` | goatcore [#178](https://github.com/USAREUR-AF/goatcore/pull/178), [#227](https://github.com/USAREUR-AF/goatcore/pull/227) |
| netvis | the image compiled in one deployment's ACL files and rule intents | read at start from `NETVIS_ACL_DECLARATION_DIR` and `NETVIS_RULE_INTENTS_FILE`; the role mounts the goatnet's files read-only | goatstuff [#29](https://github.com/USAREUR-AF/goatstuff/pull/29) |
| snitch, netbird-mgmt, panoscope, trust-sandbox | deployment values as defaults | every such value from configuration; public defaults unchanged. `SNITCH_SATLINK_NAME` lets a collector keep reading history written under another table name | goatcore [#181](https://github.com/USAREUR-AF/goatcore/pull/181), goatstuff [#29](https://github.com/USAREUR-AF/goatstuff/pull/29) |
| onboarding acceptance check | searched the `goat` binary for the goatnet's name | reads the default profile inside the running onboard-runner, so a new goatnet needs nothing compiled into goat-cli | goatcore [#135](https://github.com/USAREUR-AF/goatcore/pull/135) (`joshkor1982`), [#175](https://github.com/USAREUR-AF/goatcore/pull/175); hello-galaxy-goatenv [#12](https://github.com/USAREUR-AF/hello-galaxy-goatenv/pull/12) |

### Releases

| Release | Carries |
|---|---|
| [goat-cli-v0.5.17](https://github.com/USAREUR-AF/goatcore/releases/tag/goat-cli-v0.5.17) and [goatbuilder/v0.4.3](https://github.com/USAREUR-AF/goatcore/releases/tag/goatbuilder/v0.4.3) | the configuration-read ACL declaration and release source (goatcore [#220](https://github.com/USAREUR-AF/goatcore/pull/220)) |
| [goat-cli-v0.5.18](https://github.com/USAREUR-AF/goatcore/releases/tag/goat-cli-v0.5.18) | `goat federate init` finds the core router the standard role deploys (goatcore [#241](https://github.com/USAREUR-AF/goatcore/pull/241)) |
| [snitch-v0.1.1](https://github.com/USAREUR-AF/goatcore/releases/tag/snitch-v0.1.1) | snitch with every deployment value from configuration |
| goat-relay and goat-relay-protocol 0.1.0 | the crates leave their placeholder version; the relay is still released by image digest (goatcore [#281](https://github.com/USAREUR-AF/goatcore/pull/281)) |

Base images: goatcore refreshes the roles it defines, goatstuff refreshes only `node-build`, and goatstuff and goatrodeo copy goatcore's files, checked on every pull request and daily (goatcore [#201](https://github.com/USAREUR-AF/goatcore/pull/201), goatstuff [#30](https://github.com/USAREUR-AF/goatstuff/pull/30), goatrodeo [#9](https://github.com/USAREUR-AF/goatrodeo/pull/9)). The shared files must be byte-identical for a deployment's tree to assemble, which is why they are copied and not edited in place.

## 3. Federation

Three things happened to federation. The procedure on `main` received fixes from people running it between real environments. Two decisions about how nations share were written down as proposals. And the procedure itself is being rebuilt as one `goatbuilder` command, which is in review and not in `main`.

### On main: the directory carries more, and reruns are safe

| Change | What it means when you federate | PR |
|---|---|---|
| The directory carries the SPIFFE trust bundle | Phase 5 uploads your bundle and fetches your partner's, and places it only when the upload's signature checks against the key your partner read aloud. Nobody hands a bundle over by file | goatcore [#172](https://github.com/USAREUR-AF/goatcore/pull/172) |
| https only | `directory.py` refuses a directory that is not https. A private CA is trusted through `SSL_CERT_FILE` | goatcore [#172](https://github.com/USAREUR-AF/goatcore/pull/172) |
| The end-to-end test uses a real directory | `ops/federation-e2e/run.sh` runs saltlick v0.4.0, pinned by digest, behind a TLS front, and exchanges each side's package, CA and bundle through it | goatcore [#172](https://github.com/USAREUR-AF/goatcore/pull/172), [#142](https://github.com/USAREUR-AF/goatcore/pull/142) |
| One receive store per partner | The core router keeps a persistent store scoped to each configured peer. A single store on `from/**` could be connected and still retain nothing | goatcore [#235](https://github.com/USAREUR-AF/goatcore/pull/235) (`joshkor1982`) |
| The edge checks those stores | Before it admits a partner, the edge checks the core for a receive store matching every admitted scope, and accepts older history beside the scoped stores | goatcore [#237](https://github.com/USAREUR-AF/goatcore/pull/237) (`pbolduc-rhc`) |
| Certificates are reused on a rerun | Phase 8 validates the peering certificates it finds and reuses them. It mints only a missing pair, and replaces one only with `--rotate`. An ordinary rerun does not need the offline CA key | goatcore [#236](https://github.com/USAREUR-AF/goatcore/pull/236) (`joshkor1982`) |
| `goat federate init` finds the core router | It discovers one running core by role label or by the standard and older names, accepts `FED_ROUTER_CONTAINER`, and refuses a missing, stopped or ambiguous target | goatcore [#239](https://github.com/USAREUR-AF/goatcore/pull/239) (`joshkor1982`, reported by `philosoma`) |

### Decisions about sharing between nations

Each nation runs its own environment, manages its own pods, and shares only by federating across boundary nodes. Several documents read as if one nation's site could sit inside another's environment, or as if a moon pod were the operational path. They now say what the model is, and two proposed decisions fill gaps in it.

![Nation A releases data to nation B across their peering. It goes no further by itself. It reaches nation C only if B re-releases it under B's own name, or if A publishes it as a general release, which every federated edge forwards and which keeps A's code in the key](figures/2026-11-10/one-hop.svg)

| Decision | Status | What it says |
|---|---|---|
| [ADR 1224](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1224-transit-is-one-hop-unless-the-owner-marks-a-general-release.md): transit is one hop | proposed | A release goes one hop. It moves further only by a deliberate re-release attributed to the re-releasing nation, or when its owner publishes to `release/general/**`. Origin beyond the first hop is proven by the owner's signature. It replaces two earlier rules that disagreed (goatcore [#225](https://github.com/USAREUR-AF/goatcore/pull/225)) |
| [ADR 1223](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1223-federated-recipient-key-crosses-the-boundary-signed-and-long-lived.md): a reader's key crosses the boundary | proposed | The reading nation keeps a long-lived recipient key in its own environment and publishes the public half under its own landing prefix, signed with its SPIFFE identity. The sealing side checks it against the trust bundle it already holds. Sealing for another nation is designed this way and is not yet usable between two real environments (goatcore [#210](https://github.com/USAREUR-AF/goatcore/pull/210)) |

Status lines corrected to match what exists:

- **No nation's site sits inside another sovereign's environment.** ADR 1157, 1208 and 1158 say so directly (goatcore [#205](https://github.com/USAREUR-AF/goatcore/pull/205)).
- **A moon pod is a learning tool for an exercise environment,** not the way nations share operational data. Its seven conformance requirements moved to goatstuff beside the moon-pod design (goatcore [#207](https://github.com/USAREUR-AF/goatcore/pull/207), [#209](https://github.com/USAREUR-AF/goatcore/pull/209); goatstuff [#31](https://github.com/USAREUR-AF/goatstuff/pull/31), [#33](https://github.com/USAREUR-AF/goatstuff/pull/33); goatdocs [#9](https://github.com/USAREUR-AF/goatdocs/pull/9)).
- **Grant-keyed payload encryption is built,** so a machine reads under the same grants a person does (ADR 1094, goatcore [#204](https://github.com/USAREUR-AF/goatcore/pull/204)).
- **The peering forwarder is built** and not yet run between two real environments (ADR 1218, goatcore [#208](https://github.com/USAREUR-AF/goatcore/pull/208)).
- **ADR 1025's deferred features** are restated against the current model (goatcore [#206](https://github.com/USAREUR-AF/goatcore/pull/206)).

### In review: federation as one goatbuilder command

Today a federation needs two tools on two machines and several files copied by hand. The work in review makes `goatbuilder federate <partner>` the whole procedure: one decision (the partner and the release sets offered), two human confirmations kept on purpose (the key and CA fingerprint read aloud, and approval of what the core admits), and everything else done, checked, recorded and resumable.

![On main, federation code lives inside goat-cli, goat and goatbuilder each run part of the procedure, five certificate files are copied to the edge by hand, and the edge and core hosts have no host firewall. On the integration branch, one goat-federation library holds the code, ADR 1225 makes goatbuilder federate the one command, the edge role installs the certificates, and an opt-in host firewall covers the edge and core hosts](figures/2026-11-10/federation-move.svg)

**None of this is in `main`.** The pieces below merged into the branch `integration/federation-turnkey`. That branch reaches `main` when the federation end-to-end test drives both sides with `goatbuilder federate` alone.

| Piece | On the integration branch | PR |
|---|---|---|
| ADR 1225 (proposed) | All federation code moves into the `goat-federation` library and `goatbuilder federate`. `goat federate <verb>` runs the same library and names the goatbuilder command until partner environments have a goatbuilder that carries the verbs | goatcore [#245](https://github.com/USAREUR-AF/goatcore/pull/245) |
| The library | `crates/goat-cli/src/fed/` becomes `crates/goat-federation`, and the six verbs (init, lint, compose, diff, verify, apply) move into it with no change in behavior | goatcore [#242](https://github.com/USAREUR-AF/goatcore/pull/242), [#298](https://github.com/USAREUR-AF/goatcore/pull/298) |
| Certificates | With `goat_zenoh_edge_install_certs: true` the edge role installs the peering leaves and the partner's CA from the run's working directory | goatcore [#246](https://github.com/USAREUR-AF/goatcore/pull/246) |
| Host firewall | `roles/goat-host-firewall`: an opt-in baseline (inbound default deny, accept rules derived from the peering's own variables) on the edge and core router hosts. A deployment may tighten it freely and loosen only a named rule with a recorded reason | goatcore [#285](https://github.com/USAREUR-AF/goatcore/pull/285) |

The stages still open are listed in [section 7](#7-still-in-progress).

## 4. Secrets and deploy safety

The deploy preflight refuses more mistakes before it changes a host, and a host's ledger shows which tree last converged it.

| Change | What you see | PR |
|---|---|---|
| Unresolved secret references are refused | `ansible-preflight.sh` exits 2 when any environment value still begins `op://`, `bao://` or `bw://`. It names each variable and prints no value. The check runs before the `GOAT_SKIP_ANSIBLE_PREFLIGHT` bypass | goatcore [#183](https://github.com/USAREUR-AF/goatcore/pull/183) |
| The secrets check reads the tasks a play reaches | A secret a role resolves inside a task, including one reached through `include_tasks`, is named before the deploy starts | goatcore [#233](https://github.com/USAREUR-AF/goatcore/pull/233) |
| A secrets session on Linux with no desktop | `secrets-session` keeps its token in the kernel user keyring: written and read through a pipe, never in argv or a file, with a kernel timeout at the session's expiry. `GOAT_SECRETS_KEYSTORE=keychain\|keyring` chooses where both exist | goatcore [#218](https://github.com/USAREUR-AF/goatcore/pull/218) |
| The ledger records a new tree | A deploy that changes only configuration (a new overlay commit, or a pre-disclosure patch) writes a ledger row with the same image ref | goatcore [#145](https://github.com/USAREUR-AF/goatcore/pull/145), goatstuff [#37](https://github.com/USAREUR-AF/goatstuff/pull/37) |
| The two release drivers agree | `rc.sh` and `goatbuilder release` write the same development-rung evidence into a preprod record | goatcore [#196](https://github.com/USAREUR-AF/goatcore/pull/196), [#202](https://github.com/USAREUR-AF/goatcore/pull/202) |
| A standby is left alone | No audit-role write on a PostgreSQL standby, and management health is checked only where management runs. An unknown recovery state refuses the write | goatcore [#116](https://github.com/USAREUR-AF/goatcore/pull/116) |
| Seed retries keep ledger protections | The retry saves the seed tables' trigger modes, reloads inside one transaction per database, and restores the exact modes | goatcore [#230](https://github.com/USAREUR-AF/goatcore/pull/230) |
| Backup acceptance follows what a site declares | pgBackRest is in the endstate catalog; a site that disables independent backups marks the check absent | goatcore [#121](https://github.com/USAREUR-AF/goatcore/pull/121) |
| Onboarding honors the configured transport | The delegate's SSH settings and the resolved management URL are passed through | goatcore [#115](https://github.com/USAREUR-AF/goatcore/pull/115) |
| Controller-side API calls do not use sudo | Remote host operations keep their privilege requirements | goatcore [#120](https://github.com/USAREUR-AF/goatcore/pull/120) |

Pull requests #115 to #121 and #230 are from `joshkor1982`; #115 to #121 were extracted from `kananmuna26`'s Azure pull request (goatcore [#12](https://github.com/USAREUR-AF/goatcore/pull/12)) so each could be reviewed alone.

## 5. A first goatnet (goatlite)

The goatlite tutorial was followed as written on two fresh Ubuntu 24.04 machines and on a clean Mac, and every step that failed was fixed in the tutorial or the tool. The Linux run reached `doctor` 21 of 21, `assay` 23 PASS with 0 FAIL and 0 UNKNOWN, and a round-trip publish. goatlite stays **WIP**: its gate is the drill by two people who did not write it.

| Change | PR |
|---|---|
| The README's first run downloads the released `goatbuilder` and needs no build. A cold source build took about 36 minutes on a laptop; the rehearsal itself runs in about a second | goatcore [#259](https://github.com/USAREUR-AF/goatcore/pull/259), [#222](https://github.com/USAREUR-AF/goatcore/pull/222) |
| The macOS setup works on a clean Mac, and a macOS CI job runs the tutorial's commands as written: Python 3.14 for Ansible, the rustup installer, Homebrew on `PATH`, an SSH key | goatcore [#229](https://github.com/USAREUR-AF/goatcore/pull/229) |
| `goat pub --confirm` lands on a goatlite: the founder namespace has a store, so the read-back that proves the router accepted the write finds it | goatcore [#223](https://github.com/USAREUR-AF/goatcore/pull/223) |
| `goat status` reports a healthy goatlite healthy: with no portal key it probes the portal's unauthenticated health endpoint | goatcore [#232](https://github.com/USAREUR-AF/goatcore/pull/232) |
| `doctor`, `assay` and the host preflight grade one box on a LAN on the rows that apply to it | goatcore [#186](https://github.com/USAREUR-AF/goatcore/pull/186), [#191](https://github.com/USAREUR-AF/goatcore/pull/191), [#192](https://github.com/USAREUR-AF/goatcore/pull/192), [#234](https://github.com/USAREUR-AF/goatcore/pull/234) |
| Tutorial text matches what a clean run shows; Rust installs unattended; `goat` is installed before the probe context | goatcore [#185](https://github.com/USAREUR-AF/goatcore/pull/185), [#187](https://github.com/USAREUR-AF/goatcore/pull/187), [#190](https://github.com/USAREUR-AF/goatcore/pull/190), [#193](https://github.com/USAREUR-AF/goatcore/pull/193), [#221](https://github.com/USAREUR-AF/goatcore/pull/221) |
| The portal's CA-root flag defaults to both names the portal has used | goatcore [#189](https://github.com/USAREUR-AF/goatcore/pull/189), [#203](https://github.com/USAREUR-AF/goatcore/pull/203) |
| The hello-galaxy examples run against a goatlite you stand up, or another goatnet you have access to | [hello-galaxy-access-mgmt #4](https://github.com/USAREUR-AF/hello-galaxy-access-mgmt/pull/4) and five sibling repositories |

Newly readable in public:

- **goatdocs is a website:** [usareur-af.github.io/goatdocs](https://usareur-af.github.io/goatdocs/), built with MkDocs from `main` (goatdocs [#12](https://github.com/USAREUR-AF/goatdocs/pull/12)).
- **Built with:** [`built-with.md`](../reference/built-with.md) lists the open-source projects goat uses, their licences and where each is used (goatdocs [#13](https://github.com/USAREUR-AF/goatdocs/pull/13)).
- **goat-client's source** is public at [USAREUR-AF/goat-client](https://github.com/USAREUR-AF/goat-client). The public tree ships no certificate and pins no signing key; a deployment adds its own CA root (goatcore [#244](https://github.com/USAREUR-AF/goatcore/pull/244)).
- **The NetBird fork** is [USAREUR-AF/netbird](https://github.com/USAREUR-AF/netbird). It embeds no certificate (goatcore [#228](https://github.com/USAREUR-AF/goatcore/pull/228)).
- **panoscope** is shown at the top of the goatcore README, on 22 synthetic peers (goatcore [#231](https://github.com/USAREUR-AF/goatcore/pull/231)).

## 6. Security fixes and the smaller repositories

| Repository | Change | PR |
|---|---|---|
| goatcore | The portal and snitch web pages no longer keep an API key in browser storage. A key is exchanged for an opaque eight-hour server session, the underlying credential and role are checked on every request, and cookie-authenticated writes need an exact Origin. Bearer API clients are unchanged | [#7](https://github.com/USAREUR-AF/goatcore/pull/7) (`joshkor1982`) |
| goatcore | HTTPS service checks verify certificate chains and hostnames, with optional `ca_file` trust roots; Python TLS contexts have a TLS 1.2 floor | [#7](https://github.com/USAREUR-AF/goatcore/pull/7) |
| goatcore | Ten Python code-scanning findings resolved with no change in behavior | [#130](https://github.com/USAREUR-AF/goatcore/pull/130) (`joshkor1982`) |
| open-billie | 18 dependency advisories resolved: Vitest, Vite and esbuild upgraded, and CI's Ansible Core pinned | [#21](https://github.com/USAREUR-AF/open-billie/pull/21) (`joshkor1982`) |
| octo-pod | Uninstall keeps identity, keys, retained data and the running mesh agent unless `--purge-data` is given, and no longer reports success after a failed cleanup | [#17](https://github.com/USAREUR-AF/octo-pod/pull/17), [#16](https://github.com/USAREUR-AF/octo-pod/pull/16), [#18](https://github.com/USAREUR-AF/octo-pod/pull/18) (`joshkor1982`) |
| goat-client | The trust-root loader returns walk and read errors where it returned none | [#1](https://github.com/USAREUR-AF/goat-client/pull/1) |
| goatrodeo | Air Defenders runs its game step on a fixed 60 Hz clock, so its speed no longer follows the display's refresh rate | [#13](https://github.com/USAREUR-AF/goatrodeo/pull/13) (`philosoma`), [#14](https://github.com/USAREUR-AF/goatrodeo/pull/14) |

## 7. Still in progress

These areas are moving now. Status words are the ones the repositories use.

| Area | State | Watch |
|---|---|---|
| Federation as one goatbuilder command | **In review** on `integration/federation-turnkey`, in stages: the verbs in goatbuilder, phase 3 measured over SSH, a plan with a stable hash, per-peering allocation, a journal with resume, acceptance that writes an evidence bundle, back-out of one peering | goatcore [#297](https://github.com/USAREUR-AF/goatcore/pull/297), [#252](https://github.com/USAREUR-AF/goatcore/pull/252), [#280](https://github.com/USAREUR-AF/goatcore/pull/280), [#289](https://github.com/USAREUR-AF/goatcore/pull/289), [#302](https://github.com/USAREUR-AF/goatcore/pull/302), [#276](https://github.com/USAREUR-AF/goatcore/pull/276), [#287](https://github.com/USAREUR-AF/goatcore/pull/287) |
| Several peerings on one edge and core | **Open**: each peering refuses another's interface, port, address, metrics port or inventory name; a three-party test | goatcore [#268](https://github.com/USAREUR-AF/goatcore/pull/268), [#269](https://github.com/USAREUR-AF/goatcore/pull/269), [#270](https://github.com/USAREUR-AF/goatcore/pull/270), [#275](https://github.com/USAREUR-AF/goatcore/pull/275); saltlick [#10](https://github.com/USAREUR-AF/saltlick/pull/10) |
| Federation test environment | **Open**: named runs that share one machine, a versioned result schema, a scenario catalog | goatcore [#256](https://github.com/USAREUR-AF/goatcore/pull/256), [#257](https://github.com/USAREUR-AF/goatcore/pull/257), [#258](https://github.com/USAREUR-AF/goatcore/pull/258), [#260](https://github.com/USAREUR-AF/goatcore/pull/260), [#316](https://github.com/USAREUR-AF/goatcore/pull/316), [#317](https://github.com/USAREUR-AF/goatcore/pull/317) |
| Proposed decisions | ADR 1223 (a reader's key crosses the boundary) and ADR 1224 (one hop) **proposed**; ADR 1225 proposed on the integration branch. [ADR 1222](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1222-object-store-moves-from-minio-to-rustfs.md) **proposed**: move the S3 object store from MinIO to RustFS | [section 3](#decisions-about-sharing-between-nations), goatcore [#48](https://github.com/USAREUR-AF/goatcore/pull/48) |
| goatlite | **WIP**; followed as written on clean machines; the two-person drill is its gate | [`goatlite.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/goatlite.md) |
| Secrets session | **Built; WIP**. The gate is one live 24-hour run on each of 1Password, OpenBao and Vaultwarden | [`secrets-session.md`](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/secrets-session.md) |
| Azure | **Open**: relays and certificates on Azure, with the standup fixes split into drafts | goatcore [#12](https://github.com/USAREUR-AF/goatcore/pull/12), [#111](https://github.com/USAREUR-AF/goatcore/pull/111) to [#122](https://github.com/USAREUR-AF/goatcore/pull/122) |
| Contribution standards | **Drafts** in most repositories: pinned action revisions, restricted workflow defaults, DCO and supply-chain checks | goatcore [#127](https://github.com/USAREUR-AF/goatcore/pull/127), [#128](https://github.com/USAREUR-AF/goatcore/pull/128) and siblings |
| Portal performance and resilience | **Open** (`0mlml`): the roster parsed once per change; panicking requests access-logged | goatcore [#76](https://github.com/USAREUR-AF/goatcore/pull/76), [#75](https://github.com/USAREUR-AF/goatcore/pull/75) |
| Dependency and image pins | **Open** (`HaterAndrew`, Dependabot): Go and Rust dependency updates, pinned base images | goatcore [#308](https://github.com/USAREUR-AF/goatcore/pull/308), [#312](https://github.com/USAREUR-AF/goatcore/pull/312), [#294](https://github.com/USAREUR-AF/goatcore/pull/294); goatstuff [#42](https://github.com/USAREUR-AF/goatstuff/pull/42), [#44](https://github.com/USAREUR-AF/goatstuff/pull/44); zagros-moon-pod [#9](https://github.com/USAREUR-AF/zagros-moon-pod/pull/9) |
| open-billie setup wizard and networking | **Open** (`GoldCoin1987`) | open-billie [#19](https://github.com/USAREUR-AF/open-billie/pull/19) |

The maintainers' public roadmap, [github.com/orgs/USAREUR-AF/projects/8](https://github.com/orgs/USAREUR-AF/projects/8), lists open issues and pull requests by status.

## About this entry

- **Window.** Pull requests merged from 8 November 2026, after the previous entry was written, to 10 November 2026 05:00 UTC, in every public USAREUR-AF repository.
- **What "merged" means here.** A change is described as part of goat only when it merged into a repository's default branch. A pull request merged into any other branch is reported as in review.
- **The weekly listing.** From this week, [`weekly/`](weekly/INDEX.md) holds a page per ISO week that lists every merged pull request by kind. A scheduled workflow generates it from pull request titles with no person or model in the loop (`.github/workflows/changelog-weekly.yml`). Written entries like this one explain; the weekly listing is the complete record.
- **How entries are written.** `.claude/skills/changelog/` holds the method, the template and the checks this entry was made with.
