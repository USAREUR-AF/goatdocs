# Staged delivery — the shape every major build-out takes here

**One driver, numbered idempotent phases, a fail-closed gate at each end, and acceptance criteria
that include the refusals.** This is the canonical shape for **any** major engineering build-out in
this repository — a goatnet, a federation, a tactical site, a new hosted service, a new plane. It is
not a pattern one effort may adopt; it is the one every dimension converges on, so that a reader who
has run one has effectively run all of them.

Principles live in [goatnet-deployment-doctrine](https://github.com/usareur-af/goatcore/blob/main/docs/design/goatnet-deployment-doctrine.md) (P1–P10) and are not
restated here. This is the **structure** those principles imply.

## The rule

**A new dimension adopts this shape. It does not invent its own.**

What inventing looks like, measured 2026-09-07: `docs/operations/` holds **17 bringup and standup
runbooks, and exactly one of them names a driver script.** The other sixteen are prose procedures a
human follows, each re-deciding its own ordering, its own resume story, and its own idea of done.
That is P1 ("never a second THE procedure") violated sixteen times, and it is the cost this document
exists to stop paying.

## Who this is for

Anyone standing up a substantial new capability. If the work has more than about five ordered steps,
at least one irreversible action, and someone other than the author will run it, it wants this
shape.

## The ten elements

Each names where it already exists, so none of it has to be built from nothing.

| # | Element | Already exists in | Contract |
|---|---|---|---|
| 1 | **One driver, one entrypoint** | `ops/scripts/goat-standup.sh` | Never a second "THE procedure" (P1). A runbook a human reads is not a driver |
| 2 | **Phase 1 is a fail-closed preflight** | `standup-config-preflight.py` | Refuses before anything is touched. Missing inputs are named, not defaulted |
| 3 | **Numbered phases, each with a kind** | `step <n> <kind> <label>` — `GATE`/`A`/`T`/`MANUAL` | The kind tells the reader who acts. `MANUAL` stops and says how to resume |
| 4 | **Every phase idempotent, resumable** | `--from N` | Re-running a phase is always safe, so a failure is recoverable without reverse-engineering |
| 5 | **Plan mode** | `--plan` | Prints the whole path and executes nothing. This is how a reviewer sees the shape |
| 6 | **Inputs derived, never typed** | `goatbuilder federate init` (`goat federate init` during the transition) | Measure the running system. A value that cannot be derived **fails and names itself** rather than being defaulted |
| 7 | **One artifact, exactly one writer** | the agreement digest; `apply --confirm` | Every other verb is read-only. Two consumers of one artifact cannot drift by being typed twice |
| 8 | **Per-phase "worked when"** | the "The run" table in [goatnet-standup](https://github.com/usareur-af/goatcore/blob/main/docs/operations/goatnet-standup.md) | The end state, not "the command exited 0" |
| 9 | **A terminal acceptance gate that runs** | `step 14 GATE "acceptance suite"` | Values derived from config; all applicable rows green. A gate nobody executes is a document |
| 10 | **Negative acceptance — the refusals** | Step 7 of the [federation runbook](https://github.com/usareur-af/goatcore/blob/main/docs/operations/sovereign-federation-runbook.md); the conformance bundle's `refuse-*` fixtures | A check that cannot fail is not a check. Assert what must be refused, and assert it *alongside* a positive that proves the path was live |

## Acceptance criteria have four tiers, and most work ships with one

Naming them separately is the point: "it works" usually means only the first.

1. **Per-phase end state.** What is true when this phase is done — a file present, a session
   established, a rule loaded. Written per phase, before the phase is built.
2. **Positive terminal gate.** The capability does its job, measured end to end, with values derived
   from configuration rather than typed into the test.
3. **Negative gate.** The refusals fire. Run these *only* alongside a passing positive — a refusal
   asserted against a dead path passes vacuously and proves nothing.
4. **A one-sided proof.** Something the party who will actually operate this can run alone, without
   privileged access to the other side. This is the tier almost always missing, and it is the one
   that survives after the two engineers who built the thing have moved on.

Tier 4 is why [`ops/federation/roundtrip/`](https://github.com/usareur-af/goatcore/tree/main/ops/federation/roundtrip) exists: every other
federation assertion needed shell on both sovereigns, which no real publisher has.

## Why elements 6 and 10 keep being the ones that catch things

**Derived inputs (6)** catch the class where an operator's claim and the machine's reality differ.
A typed capability stays wrong until the link fails in front of a counterparty.

**Negative acceptance (10)** catches the class where the mechanism was never live. Four defects found
on 2026-09-07 — F-491, F-492, F-493, F-494 — all shared one shape: the artifact under test had always
been *hand-written to match expectations*, so it was accidentally correct wherever the generated one
was wrong. Deploying the generated artifact is itself a negative test: it asks whether the tool, not
the author, produces something that works.

## The dimensions, and where each one stands

No dimension has the whole shape yet. Each row is concrete work, not aspiration, and every gap has a
working reference implementation in one of the other rows.

| Dimension | Driver today | Has | Missing |
|---|---|---|---|
| **Goatnet standup** | `ops/scripts/goat-standup.sh` | 1–6, 8–10 | 7 — the config surface has several writers, so two of its consumers can still disagree |
| **Cross-sovereign federation** | `goatbuilder federate <partner>`; the script avenue `ops/scripts/peering-standup.sh` | all ten | — |
| **Site node addition** (a node into a live goatnet) | none — `node-addition.md` is prose | a clear founder/joiner fork | 1, 3, 4, 5, 9, 10 |
| **Tactical site standup** (four-node host site, ADR 1141) | none, and not built | — | all ten; design it into the build rather than after |
| **New hosted service** | `ops/serve/services.yaml` → `generate.py` | 7 (one registry, one generator), part of 2 | 1, 3, 4, 5, 9, 10 |
| **New service carrying new infrastructure** | the above plus a terraform tree | 7 | 1, 3, 4, 5, 6, 9, 10 — and the infra half has no acceptance gate at all |

**A new hosted service is the most common case and the least covered.** It already has the hardest
element to retrofit — a single registry with a single generator (element 7) — and none of the
cheapest ones. A service that ships with a driver, a plan mode and a terminal gate would be the
second reference implementation, and it is a smaller build than either of the two that exist.

### The two originals, element by element

Both got a different half right, which is why the union is worth stating explicitly.

| Element | goatnet standup | cross-sovereign federation |
|---|---|---|
| 1 driver | `goat-standup.sh` | **missing** — a six-step runbook a human follows |
| 2 fail-closed preflight | `standup-config-preflight.py` | partial — `init` refuses, but only for its own inputs |
| 3 phases with kinds | yes | **missing** |
| 4 idempotent + resumable | `--from N` | untested — no driver to resume |
| 5 plan mode | `--plan` | **missing** |
| 6 derived inputs | partial — reads config, does not measure the host | `init`, fully |
| 7 one artifact, one writer | config surface is the artifact; several writers | the agreement; `apply` alone |
| 8 per-phase "worked when" | yes | prose, not per-step |
| 9 terminal gate that runs | `step 14 GATE` | **missing** — Step 5 is a table a human works through |
| 10 negative acceptance | **missing** | Step 5 and the `refuse-*` fixtures |

**The convergence is done, bar one element.** Federation gained a driver with plan mode, resume and a
terminal gate (`ops/scripts/peering-standup.sh`); standup gained negative acceptance rows
(`must_refuse` + `paired_positive`, CI-guarded) and host measurement at phase 1
(`standup-host-preflight.py`). Neither needed anything invented — each carried across what the
other already had working, which is the argument for doing the same with the rows below. What
remains is standup's element 7: its config surface has several writers, so two consumers of it
can still drift — the failure federation's single agreement is built to make impossible.

Federation is now also the reference for how few stops a driver needs. `goatbuilder federate
<partner>` is becoming four stages of one command, each also runnable alone: `plan` validates and
explains the bounded change, `deploy` carries out the approved plan, `test` runs a bilateral
acceptance session, and `status` reports health and the age of the last evidence. A person makes
one decision: the partner, and the release sets it receives, which the deployment's
`federation.toml` owns and a peering entry may only narrow. Two confirmations stay human: the
verifying keys and CA fingerprints read aloud with the counterparty and the agreement digest
compared, and approval of what the core admits, including the reviewed configuration change, bound
to the plan's hash. Live prerequisites are checked again just before any change. Acceptance checks
read PASS, FAIL, BLOCKED, SKIP or NOT APPLICABLE, and a required check never passes on a skip; each
side keeps its evidence in `<work>/evidence/acceptance/` and the two exchange result bundles by
file. Publishing `exchanging` afterwards is a third deliberate act by both operators, through a
reviewable change. A re-run resumes by inspecting actual state, guided by the run journal in the
working directory, so a `MANUAL` stop no longer needs a `--from` number. Each stage arrives beside
today's run, which stays the default and reachable until that stage's default switch lands.

Status: WIP — gate: the federation end-to-end test drives both sides with goatbuilder federate alone.

## Applying it to something new

1. Write the phase list with its kinds first, and the per-phase "worked when" beside each. If a
   phase's end state cannot be stated, it is not one phase.
2. Write phase 1 — what must be true before anything is touched — and make it refuse.
3. Decide the one artifact and the one command that writes it.
4. Build the driver with `--plan` and `--from` from the start; retrofitting resume is expensive.
5. Write all four acceptance tiers before building the phases. Tier 3 and tier 4 are the ones that
   will be skipped under time pressure, which is precisely why they are written first.
6. Every gap found while running it feeds the mechanism, not just the fix (P10).

## Related

- [goatnet-deployment-doctrine](https://github.com/usareur-af/goatcore/blob/main/docs/design/goatnet-deployment-doctrine.md) — the principles this shape serves
- [goatnet-standup](https://github.com/usareur-af/goatcore/blob/main/docs/operations/goatnet-standup.md) — the reference driver
- [sovereign-federation-runbook](https://github.com/usareur-af/goatcore/blob/main/docs/operations/sovereign-federation-runbook.md) — the reference for
  derived inputs and negative acceptance
- [release-graduation](https://github.com/usareur-af/goatcore/blob/main/docs/design/release-graduation.md) — how a built thing moves between environments; this
  doc is about getting it built in the first place
