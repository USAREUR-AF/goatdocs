# Complexity budget and substrate encapsulation

A framework for managing layered-substrate complexity so that consumers of an open-source infrastructure project can clone, run, and use it without acquiring expertise in every layer the maintainers had to build. Sized for projects that have accumulated many individually-justified substrates (auth, identity, replication, mesh, observability, supply chain, key custody) and now need to ensure those substrates do not become a barrier to adoption.

---

## Why this matters

Every well-architected infrastructure project eventually accumulates layers. Each layer was added for a specific real reason. Each layer composes correctly with the others. Each layer is documented somewhere. **And yet new operators bounce off, vendors decline to integrate, and partner deployments stall — because the cumulative weight of the layers exceeds what a reasonable adopter is willing to internalize before getting value.**

The failure mode is not "we added the wrong layers." The failure mode is **letting the user-facing surface grow in lockstep with the internal complexity**. A project that does this asks every adopter to become an expert in every layer before they can run the thing.

The fix is not removal. Removing well-justified substrate gives up real value (defense in depth, sovereignty, resilience). The fix is **encapsulation** — making the substrate invisible to consumers who don't need to peek inside, while keeping it visible and debuggable for the small number of people maintaining it.

This document defines the bar, the strategy, and the measurement cadence for holding to it.

---

## The bar (definition of success)

**A new contributor / operator / partner should need no more expertise in the underlying substrates than they would need to adopt any well-run single open-source repository.** Single clone, single bringup command, working system. Substrate complexity becomes visible only when the operator needs to debug or customize.

Concretely, four onboarding paths. Each path is completable using **one** primary document, with **one** rollback procedure, and produces a working outcome. If any path requires reading more than one doc to succeed, the abstraction is leaking. That leak is the engineering target.

| Path | Outcome | Bar |
|---|---|---|
| **5-min** | Substrate runs on operator laptop; one peer enrolled to a local instance | `git clone && make bringup` produces a working substrate. No expertise required. |
| **30-min** | First real peer enrolled against a real mgmt-stack; one service reachable end-to-end | One operator runs one playbook against one host. No substrate decisions surfaced. |
| **1-day** | Second site provisioned; federation working; replication visible | Two playbook runs + one configuration value. No knowledge of replication topology, CA custody, or trust-anchor distribution required. |
| **1-week** | Operator troubleshoots a real failure from logs to root cause | Single troubleshooting decision tree. No requirement to read 15 design docs. Decision tree points the operator at the right substrate doc only when the layer is implicated. |

These are paths a *consumer* takes. The 1-week troubleshooting path is the most important — it is the test of whether the encapsulation holds under stress. When the system breaks, the operator must have somewhere coherent to start. If the only path forward is "ask the maintainer," the substrate is not yet a product.

---

## Strategy — three encapsulation layers

The substrate inventory does not shrink. The user-facing surface does. This is achieved through three layers of encapsulation, each independently valuable.

### 1. Make-it-work — defaults so good that no one configures

The 5-min and 30-min paths exist by virtue of this layer.

- **Single bringup command.** `make bringup` (or equivalent) produces a working substrate. Every substrate decision has a default that works for the dominant case.
- **One configuration surface.** A single `.envrc.local.example` (or equivalent) covers every variable a new operator needs to set. Each variable has a comment naming the substrate it belongs to and what the default does.
- **No required reading.** The README's first section produces a running system. Substrate-specific documentation lives one level deeper, only consulted when the default is being overridden.

The test of this layer: a first-time operator can produce a working system in the 5-min path without opening any document beyond the README.

### 2. Make-it-true — one place to start when defaults fail

The 1-week troubleshooting path exists by virtue of this layer. It is the layer that says, *honestly*, what is running.

- **One architecture overview.** A single diagram + narrative names every layer that the substrate is built from, in language an operator can follow. Each layer is described in one sentence + one pointer to the deep doc.
- **One "what's actually running" doc.** When the operator runs the substrate, what processes are alive, what ports are listening, what files exist on disk, what trust roots are in play. Refreshed whenever the substrate changes.
- **One troubleshooting decision tree.** When the system breaks, the operator starts here. The tree's branches point at the substrate-specific doc only when the layer is implicated by the symptom.
- **Honest defaults documentation.** Every default in the make-it-work layer is documented in this layer with the trade-off it embodies and the substrate decision it pre-makes. An operator who wants to peek behind the curtain can do so in one place.

The test of this layer: an operator who hits an error message they have never seen before can find the right substrate doc in under five minutes.

### 3. Make-it-yours — clean swap-points for advanced operators

Defaults work, but consumers eventually want to swap substrates (bring-your-own-IdP, bring-your-own-CA, bring-your-own-relay tier). This layer is the engineering discipline that keeps swap-points clean.

- **Every substrate has an isolated swap-point.** The substrate is decoupled from its callers via a stable interface (a config schema, a network protocol, an API contract). Replacing the default with a different implementation is a configuration change, not a code rewrite.
- **The default is one implementation among several.** Documentation does not equate "default substrate" with "only substrate." Reference implementations exist for at least one alternative, even if the alternative is `bring-your-own`.
- **Sovereignty escape valves.** For substrates where the project's value proposition rests on sovereignty (CA, identity, key custody), the swap-point is the explicit answer to "how do I bring my own?" Adopters with their own infrastructure must be able to integrate without forking.

The test of this layer: a partner with their own CA / IdP / relay tier can adopt the substrate without forking the codebase.

---

## Layer inventory

A complexity budget cannot be managed without an inventory. The inventory is a living document that names every substrate, classifies it as **consumer-facing** or **maintainer-only**, and links to the make-it-work / make-it-true / make-it-yours position of each.

The classification follows from the four onboarding paths. A substrate is **consumer-facing** if any of the four paths surface the substrate to the operator (asks them to configure it, name it, distinguish it, troubleshoot it). It is **maintainer-only** if the four paths can complete without the operator knowing it exists.

The goal is to push as many substrates as possible from consumer-facing to maintainer-only over time, without removing any.

A worked example for the goat substrate appears at [§ Goat as worked example](#goat-as-worked-example) below.

---

## Leak register

A complexity leak occurs when an operator following one of the four onboarding paths is forced to drop down a layer — to learn about a substrate that should have been encapsulated, to read a substrate-specific doc that should have been hidden, to make a substrate decision that should have had a default.

Leaks are captured in the same register pattern as findings ([ADR 1011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1011-findings-register.md)) — durable, append-only, cross-linked. They are the engineering targets that drive complexity-budget work. Each leak entry names:

- The path that surfaced the leak (5-min / 30-min / 1-day / 1-week)
- The substrate that leaked through encapsulation
- The minimum fix (a default, a doc consolidation, a swap-point) that closes the leak
- The status (open / in-flight / closed)

A leak closes when the path runs end-to-end without the operator dropping a layer. Closed leaks stay in the register for trend analysis.

**The register exists as of 2026-08-04: `docs/leaks/`** (`L-NNN`, `INDEX.md` + `TEMPLATE.md`, the ADR 1011 shape). It was created by CF-6's change-set — the first consumer-facing increment whose ADR made the D7 entry a landing condition ([ADR 1110](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1110-typed-consistency-foundation-and-console.md); entry L-001) — not by Block 81, whose seeding pass over the F-090..F-111 cluster remains owed and is named as debt in the register itself.

---

## Quarterly review cadence

The complexity budget is a measurable trend, not a one-time decision. Quarterly:

1. **Inventory refresh.** Walk the layer inventory. Reclassify substrates that have moved consumer-facing ↔ maintainer-only. Add new substrates landed since the last review.
2. **Path verification.** Run each of the four onboarding paths end-to-end. Time each path. Record every doc consulted. Every doc consulted beyond the primary one is a leak.
3. **Leak register triage.** Score open leaks by frequency (how often does this path get walked) and severity (does the leak block the path or merely slow it). Schedule the top three for the coming quarter.
4. **Trend reporting.** One number: count of consumer-facing substrates. Should be flat or shrinking; never growing without an explicit decision recorded in an ADR.
5. **No new substrate without budget.** New substrates land only when they are landed in the maintainer-only column. Substrates that land consumer-facing carry an entry in the leak register and a fix plan in the same change-set that introduced them.

This cadence runs parallel to (does not replace) the engineering-health scorecard at [`engineering-health-assessment.md`](engineering-health-assessment.md). Engineering health asks "is the foundation sound?"; complexity budget asks "is the foundation *adoptable*?"

---

## Anti-patterns

Practices that look like complexity management but actually grow the user-facing surface.

- **"Read the design doc before contributing."** Design docs are reference material for maintainers, not onboarding for operators. If an operator needs the design doc to run the system, the make-it-work layer is incomplete.
- **"It's all in CLAUDE.md."** An index is not encapsulation. CLAUDE.md (or analogous index docs) point at the substrate; they do not absolve the substrate of needing a working default.
- **"We documented every option."** Documentation of every configuration option is the *failure mode* of make-it-work. The 5-min path requires zero options.
- **"Substrate X has a runbook."** A runbook is the make-it-true layer for *operators already debugging substrate X*. It does not encapsulate substrate X for everyone else.
- **"The complexity is necessary."** All complexity is necessary at the layer that justifies it. The question is whether the *user-facing* surface needs to grow alongside.
- **"Once you understand the model, it's simple."** This is the diagnostic that something is consumer-facing that should not be. A consumer should not have to internalize the model to run the substrate.

---

## Severability

This framework is severable. It can be lifted out of the goat repo and applied to any infrastructure project that has accumulated substrates faster than it has accumulated adopters. The body above is written that way on purpose. Goat-specific application appears below as a worked example, and as inline pointers to existing artifacts.

Most of the framework lands as a small set of artifacts:

- A **layer inventory** document, refreshed quarterly
- A **leak register** alongside the findings register
- A **bringup command** that runs the 5-min path
- An **architecture overview** document that powers the 1-week troubleshooting path
- A **quarterly review** ritual, output committed to the repo

The framework does not require new tooling, new infrastructure, or new staff. It requires a written bar and the discipline to hold to it.

---

## Goat as worked example

The substrate that prompted this framework is goat — a layered tactical-data-fabric project that, by 2026-05-12, had accumulated roughly fifteen substrates each individually justified:

- wg-cp0 silent control plane (ADR 0313)
- Offline X.509 CA on YubiKey PIV (ADR 0406 + 0407)
- Bundle-rooted enrollment (Block 22K)
- Spock multi-master replication (`ha-multi-site.md`)
- Postgres streaming replication intra-site
- Ory Kratos + Hydra cluster-shared (ADR 1009 + 1010)
- Mesh-internal CoreDNS (`dns-service-discovery.md`)
- Per-site topology with profile-aware bootstrap (ADR 0826 + Block 22L)
- Two AWS account trees with strict blast-radius separation (`cloud-environments.md`)
- netbird fork (mobile-load-bearing; desktop decoupling queued)
- signal-server fork (federation patches)
- snitch fleet-health probe (Block 61)
- Rapid-bringup substrate (Block 68)
- LUKS multi-modal continuity (passphrase + TPM2 + Tang/NBDE + FIDO2 + dropbear) (Block 65)
- Image-distribution substrate (ADR 0838, Block 75)

Each was the correct decision at the time it was made. The cumulative weight — surfaced concretely by ~15 findings in the F-090-to-F-111 range, all of which are interaction bugs between layers rather than bugs in any single substrate — is the proximate driver of this framework.

**Goat's bones for the encapsulation layers are partly already there:**

- **Make-it-work foundation** exists in pieces. Block 29 (OSS go-open) names a `git clone && docker compose up` 5-min demo as the deliverable. Block 22L ships a turnkey profile-aware [`site-bootstrap.yml`](https://github.com/usareur-af/goatcore/blob/main/ops/ansible/site-bootstrap.yml). Block 68 commits to a 1-hour rapid-bringup shot clock with an automated harness. Block 76 ships goat-client as the non-engineer-facing surface.
- **Make-it-true foundation** exists in pieces. [`docs/design/architecture-spine.md`](architecture-spine.md) is a one-page orientation pointing at fifteen architectural themes. The integration matrix is the runtime-dependency view. The findings register ([ADR 1011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1011-findings-register.md)) catalogs interaction bugs. The deltas + baseline pair ([`deliberate-deltas.md`](deliberate-deltas.md) + [`engineering-baseline.md`](engineering-baseline.md)) explains why each substrate is the way it is.
- **Make-it-yours foundation** exists in pieces. Block 60 goat-moon-pod specifies a 7-requirement conformance contract that any partner can implement instead of adopting the reference. The [Vendor Data Services Provider Charter](../vendor-templates/data-services-provider-charter.md) defines partner-provided-substrate expectations.

**What goat is missing is the spine** — a single program that ties these bones into a coherent complexity-budget posture, with a written bar, a layer inventory, a leak register, and a quarterly review. That spine is Block 81 in the implementation plan, with this design doc as its anchor.

Goat-specific first deliverables:

1. **Layer inventory** authored from the list above; each substrate classified consumer-facing vs maintainer-only against the four paths
2. **Leak register** seeded with the leaks already implicit in the F-090-to-F-111 finding cluster (e.g., trust-anchor distribution surfacing through operator-laptop onboarding; cert-chain rotation requiring multi-doc reading). *The register itself exists since 2026-08-04 (`docs/leaks/`, created by CF-6); this deliverable is now the seeding pass only*
3. **5-min path stand-up** consolidating Block 29 deliverables into a single `make bringup` target that runs against a laptop
4. **Architecture overview consolidation** — the existing spine + integration matrix + deltas docs are excellent reference material, but they are three docs; the 1-week troubleshooting path needs one entry point
5. **Quarterly cadence kickoff** — first review scheduled to land alongside the first OSS publication (Block 29M) so the publication itself becomes a measurement event

---

## Composes with — does not replace

- [`engineering-health-assessment.md`](engineering-health-assessment.md) — engineering health asks "is the foundation sound?"; complexity budget asks "is the foundation adoptable?" Both feed the OSS publication readiness criteria.
- Block 29 — OSS go-open execution; the 5-min demo is no longer just a marketing artifact but the load-bearing measurement of whether the budget is being held.
- Block 32 — engineering-health scorecard; quarterly cadence runs alongside, sharing scope and reporting surface.
- Block 60 — goat-moon-pod 7-requirement conformance contract; the contract is one instance of the make-it-yours layer for partners.
- Block 68 — rapid-bringup shot clock; the shot clock IS the 30-min / 1-day path measurement.
- Block 76 — goat-client; the non-engineer-facing surface that the 5-min path produces for desktop operators.
- [ADR 1011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1011-findings-register.md) — findings register pattern; the leak register reuses the discipline.
- [ADR 1015](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md) — block-completion review checklist; gains a complexity-leak audit row when this framework lands.

---

## What this framework does not do

- It does not assess strategic fit, requirements alignment, or whether the substrate solves the right problem. Those questions are real and belong in a different mechanism.
- It does not measure whether the substrate is *good* in absolute terms — that is the engineering-health scorecard's job.
- It does not prescribe substrate removal. Substrates that are individually justified stay; the work is on their visibility.
- It does not replace per-substrate design docs, runbooks, or ADRs. Those are reference material; this framework governs how much of that reference material a new adopter is required to read.
