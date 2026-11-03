# goat-sre-agent — Scout-class peer for incident triage + action

| Field | Value |
|---|---|
| Status | Draft (Phase 3 commitment; gated on Block 23 + Block 17A.5) |
| Role | First agent that issues outbound `cmd/` |
| ADR anchor | [`../adr/0515-sre-agent-scout-class-peer.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0515-sre-agent-scout-class-peer.md) |
| Bones doc | [`ai-rapid-adaptation.md`](ai-rapid-adaptation.md) |
| Sibling proof case | Tipper (preplanned specialist) — [`tipper.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md) |
| Sibling proof case | Scout (ad-hoc human-defined, read-only) — [`scout.md`](scout.md) |
| Implementation tracker | `../project/implementation-plan.md` Block 69 |

## What `goat-sre-agent` is

`goat-sre-agent` is a **Scout-class peer** that takes a per-incident scope, plans a remediation against the fabric's queryable + tool-peer surface, and (within its lifecycle authority) executes typed actions. Reads are unguarded queryable invocations; writes route through the [Block 17A.5 policy engine](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md). Externally, it looks like Scout with one additional capability: it can issue `cmd/` to mutate operational state. Internally, that one extra capability is what this design earns its keep on.

The agent does **not** replace operators. It collapses the median-incident triage loop from "ssh in, run six commands, decide, run two more, document" to "agent proposes a diff, operator clicks Approve in Matrix, audit is complete." The high-blast-radius surface stays human-in-the-loop indefinitely.

## Why a Scout-class peer (vs new shape)

Scout already establishes the right contract: ephemeral, request-scoped, planner at a swappable boundary, citation discipline, audit-by-construction, refusal modes. The SRE agent extends that contract with one delta — outbound `cmd/` — gated through the existing policy engine. That delta is the right place to land an ADR; everything else inherits.

A standalone "long-running auto-remediation peer" was considered and rejected at v1 (see [ADR 0515 §"Alternatives considered"](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0515-sre-agent-scout-class-peer.md)). The request-scoped shape bounds blast radius better and fits the audit pattern Scout already established. If a class of work earns the long-running case (e.g. continuous TLS rotation across a 600-peer mesh), that returns through its own ADR.

## Operational walkthrough

A typical incident:

1. **Trigger.** Either an alertmanager page emitting to `agents/sre/inbox`, an operator-issued natural-language request via `cmd/agents/sre/ask`, or an upstream-agent escalation (Tipper sees something Tipper alone can't act on).
2. **Spawn.** `goat-sre-agent` instantiates with a request-scoped workload identity derived from the triggering parent (alertmanager service-account, operator OIDC, or upstream agent identity). Lifetime budget: 60 min default, 4 h ceiling, configurable per request class.
3. **Plan.** The planner peer (per [ADR 0512](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) §"The planner — swappable at the boundary") translates the trigger into a **structured remediation plan**: a sequence of read queryables to confirm the diagnosis, followed by zero or more typed `cmd/<peer>/<verb>` invocations to remediate.
4. **Diagnose.** Agent invokes read queryables — `cmd/log-tools/grep`, `cmd/pg-tools/query`, `cmd/svc-tools/status`, `cmd/lineage/backward/<topic>`, etc. Pre-flight density / staleness / consistency checks run before each diagnostic claim is admitted to the proposed plan (per [`scout.md` §"Pre-flight checks"](scout.md)).
5. **Propose.** Agent emits a **proposed action diff** under `agents/sre/<incident-id>/proposed/...` — the candidate remediation plan with citations for every diagnostic claim and the action-class declarations for every proposed write.
6. **Authorize.** Per the lifecycle mode for each proposed `(peer, verb)`:
   - **Shadow** — emit-only; no write authority. Operator reviews proposals in daily sweep.
   - **Assisted** — submit each write to the policy engine; await dual-path approval (normal 24 h SLA or fast-path two-of-N).
   - **Autonomous** — apply the write directly under the action-class's standing allow-list; emit the same audit + wide-event envelope as Assisted.
7. **Execute.** For approved writes, agent invokes `cmd/<peer>/<verb>` against the typed tool peer. Tool peers are responsible for atomicity, idempotency, and per-action audit emissions of their own.
8. **Verify.** Agent re-runs a verification queryable (the same diagnostic that surfaced the issue, expecting a different result) and emits the verification under `agents/sre/<incident-id>/verified/...` with citations.
9. **Close + tear down.** Agent emits `agents/sre/<incident-id>/closed` with the full transcript ID, outcome (`resolved` / `partial` / `escalated` / `failed`), and incident-class tag for future eval-harness replay. Audit-logger holds the full transcript under one incident-id-scoped key.

A **partial / escalated** outcome is a first-class result — the agent didn't have authority for a write, the diagnostic was inconclusive, or pre-flight checks refused. Escalation routes through the same Matrix + ntfy fanout and notes the specific gap.

## Tool-peer surface (v1 charter)

Tool peers are normal phoenix-native peers under [ADR 0208](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0208-phoenix-native-peer-discipline.md). They live at `ops/sre-tools/<peer-name>/`, share a helper crate at `ops/sre-tools/lib/`, and follow [ADR 0112](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0112-tech-strategy-workload-shape-language-boundary.md) workload-shape rules — request-shaped → Go.

| Tool peer | Verbs | Action class | Default lifecycle (v1) |
|---|---|---|---|
| `pg-tools` | `query` (read), `role-create`, `role-revoke`, `slot-status` (read), `replication-restart` | `db.read`, `db.role.create`, `db.role.revoke`, `db.slot.read`, `db.replication.restart` | Read-only Autonomous; all writes Assisted |
| `wg-tools` | `peer-list` (read), `peer-add`, `peer-revoke`, `route-show` (read) | `mesh.read`, `mesh.peer.add`, `mesh.peer.revoke`, `mesh.route.read` | Read-only Autonomous; writes Assisted |
| `svc-tools` | `status` (read), `journal-tail` (read), `restart`, `stop`, `start` | `svc.read`, `svc.restart.<role-tag>`, `svc.stop.<role-tag>`, `svc.start.<role-tag>` | Read Autonomous; `restart` Autonomous on `load-bearing: false` only; others Assisted |
| `ansible-tools` | `play` (signed playbook ref + dry-run + lint pre-flight) | `ansible.play.<role-tag>` | Assisted always at v1 |
| `cert-tools` | `expiry-check` (read), `renew` | `cert.read`, `cert.renew.<service>` | `expiry-check` Autonomous; `renew` Assisted |
| `log-tools` | `tail`, `grep`, `correlate-by-id` | `log.read` | Autonomous |
| `metrics-tools` | `query`, `range-query`, `alert-history` | `metrics.read` | Autonomous |

**A generic SSH peer is explicitly out of scope.** Free-form remote shell breaks the typed-action discipline — there is no audit shape that captures "agent typed `kubectl edit deploy ...`" cleanly enough to attribute outcome to action class. If an operation can't be expressed as a tool-peer verb, the right outcome is "operator handles this once; if it recurs, we add a tool peer." Recurrence is the trigger to expand the surface, not convenience.

### Action-class declaration

Every `(peer, verb)` pair declares its action class at boot under `attest/action-class/<peer>/<verb>`:

```yaml
peer: pg-tools
verb: role-create
class: db.role.create
description: |
  Create a new postgres role with named permissions on a named database.
  Idempotent on (role-name, database) — re-create on existing role is a no-op.
blast_radius: site                  # site | service | mesh | fleet
idempotent: true
load_bearing: true                  # true → never Autonomous in v1
sla_tier: assisted                  # shadow | assisted | autonomous
audit_class: db-mutation            # threads to Block 27 + 17D taxonomy
schema_in: cmd/pg-tools/role-create/schema-in
schema_out: cmd/pg-tools/role-create/schema-out
```

The schema-enforcer interceptor rejects `cmd/<peer>/<verb>` invocations whose action-class declaration is absent or whose lifecycle mode contradicts the policy engine's standing allow-list.

## Lifecycle gating in detail

Three modes per `(peer, verb)`. Promotion is per-action-class, drill-gated, and reversible.

### Shadow mode

- Agent emits proposed diffs to `agents/sre/<incident-id>/proposed/`. Tool peer is **never invoked** for the class.
- Operator reviews every Shadow proposal. Two outcomes per proposal:
  - **Confirmed** — operator marks "I would have approved this." Counter increments toward promotion.
  - **Unsafe** — operator marks "this would have broken something." F-NNN finding draft auto-generated; counter resets to zero; class stays Shadow until root cause is documented and a re-attempt is authorized.
- Promotion gate: 10 consecutive Confirmed + 0 Unsafe.

### Assisted mode

- Agent submits each write to the policy engine via the existing `cmd/policy-engine/request` interface; awaits approval via Matrix room `#agent-approvals:<site>.netbird.legacy.example` or ntfy push.
- Approval flow inherits [Block 17A.5 design](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md): normal path (single role-holder + 24 h SLA, auto-escalates to fast-path on breach) and fast path (two-of-N peer ≠ requestor, immediate).
- Promotion gate: 30 consecutive approved-and-applied with 0 production-impact regressions.

### Autonomous mode

- Agent applies the write directly. Audit + wide-event + citation envelope unchanged.
- **Reversion is automatic.** First production-impact regression in 90 d → class reverts to Assisted. Second → Shadow. Third → permanent revert (requires explicit ADR to re-promote).
- Production-impact regression is defined per-class in the action-class declaration's `regression_signals` field; default signals are alertmanager pages within 15 min of action and policy-engine post-hoc challenges.

### Class-line invariant

`load_bearing: true` action classes — `db.role.create`, `db.role.revoke`, `mesh.peer.add`, `mesh.peer.revoke`, `cert.renew.<load-bearing-service>`, `ansible.play.<role-tag>` for any `load-bearing: true` role — **never reach Autonomous in v1**. Promotion past the line requires its own ADR with named operator + lead-engineer consent. Default-deny is structural, not policy-toggle.

## Approval surface — Matrix + ntfy + isitup

Reuses the existing notification adapters from [ADR 0805 policy engine](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0805-policy-engine-active-passive.md):

- **Matrix** — per-site tuwunel homeserver per [ADR 0835](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0835-secure-messaging-substrate-tuwunel.md), room `#agent-approvals:<site>.netbird.legacy.example`. Bot posts a message per request with: incident-id, proposed action, action-class, blast-radius, citations, dual-path approval buttons (✅ Approve / ❌ Deny / ⏫ Escalate-to-fast-path).
- **ntfy** — per-site sovereign push tier from [ADR 0010](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0010-boundary-classification-escalation-and-medium.md). Topic `<site>-agent-approvals`; clickable inline action buttons on supported clients.
- **isitup widget** — per-site dashboard at `isitup.<site>.netbird.legacy.example/agent-approvals` showing held actions + SLA countdown.

Approval action posts to `cmd/policy-engine/approve` with the request ID; engine releases the held action; agent receives confirmation and proceeds.

**Off-hours / SLA breach.** Normal-path 24 h SLA auto-escalates to fast-path. If no two-of-N answers within an additional 1 h, the agent emits `agents/sre/<incident-id>/escalated/no-approval` and routes the incident to operator pickup via the same fan-out — the incident becomes a human ticket.

## Inference — local on a utility host, eval-first

Per [ADR 0515 §D6](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0515-sre-agent-scout-class-peer.md):

- **Inference host:** a per-site utility host runs Ollama. v2 may swap to vLLM if measured throughput pressure justifies the migration cost.
- **Planner peer boundary** unchanged from Scout — input: incident-trigger + catalog snapshot + tool-class manifest + action-class registry; output: structured plan.
- **Eval harness** at `ops/sre-agent/eval/`:
  - Replays past F-NNN findings and recorded incidents as synthetic incident triggers.
  - Pass criterion: ≥ 70 % "would-have-proposed-the-correct-fix" rate (operator-judged from the proposed diff against the actual historical fix), with **zero unsafe proposals**. The unsafe-proposal floor is hard — not an averaged property.
  - Run on every model bump; deployed model is the cheapest passing model.

**Candidate models** (not commitments): Qwen-Coder-32B (Q4 ~20 GB), Kimi-Dev-72B (Q4 ~40 GB), Llama-3.3-70B-Instruct, GLM-4.5-Air. The eval picks; the design doesn't.

**Two-model action+reviewer stack** is allowed but not assumed. The eval harness measures with-and-without; if the reviewer pass measurably lifts the pass-rate at acceptable latency cost, it ships. If not, single-model is the v1 shape.

**Externally-authored model code** (vendor planner adapter, partner-supplied diagnostic plugin) lands as `.wasm` only — see [ADR 0515 §D7](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0515-sre-agent-scout-class-peer.md) and [ADR 0513](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0513-wasm-conditioning-sandbox.md).

## Pre-flight checks (inherited from Scout)

Three checks gate every proposed action, not just every claim — extending [`scout.md` §"Pre-flight checks"](scout.md) to the write path:

1. **Density** — every diagnostic claim that motivates a write must rest on `sample_count ≥ 30` for statistical claims (`5` for "any" claims). Below floor → refuse the write; surface the data gap in the proposed-diff emission.
2. **Staleness** — every diagnostic claim's `latest_sample_timestamp` is checked against the topic's `freshness_target` and the incident's implicit time window. Stale → refuse the write or escalate the incident.
3. **Consistency** — when multiple sources should corroborate a diagnosis, disagreement beyond tolerance is surfaced in the proposed-diff and *blocks the write* in Assisted mode (the human reviewer adjudicates) and *defers to Shadow* in Autonomous mode.

Pre-flight refusals are themselves emissions with citations of what was attempted and why it refused. They land in the audit log under the incident-id and count toward eval-harness scoring as "agent correctly refused."

## Refusal modes

The agent refuses, rather than guesses, in these cases — superset of Scout's refusal modes plus the write-specific cases:

- **No tool peer matches the proposed remediation.** Surface what tool peers were considered and what verb was missing. Operator handles this incident; if the gap recurs, a new tool-peer ADR.
- **Authorization scope insufficient.** Parent identity does not authorize the proposed `(peer, verb)` per the policy engine. Surface the missing authorization; do not retry under a different identity.
- **Pre-flight checks refuse the write.** Density / staleness / consistency floor breached. Surface the gap; do not attempt the write under reduced confidence.
- **Action-class declaration missing.** Schema-enforcer rejects at the publish path; agent treats as a configuration error and escalates.
- **Hard timeout reached.** Partial action (whatever has been completed) + `incomplete: true` flag + escalation to operator.
- **Verification fails.** The post-action verification queryable does not show the expected new state. Agent emits `verified: false` and escalates rather than retrying. Re-attempts require human confirmation.

## Topic schema

**Inbound — `cmd/agents/sre/ask`** (operator question):

```yaml
question: string                      # natural language
incident_class: string                # optional; e.g. "tls-expiry", "spock-replication-lag"
budget_minutes: int                   # default 60, ceiling 240
parent_identity: string               # operator OIDC sub
```

**Inbound — `agents/sre/inbox`** (alertmanager / upstream-agent trigger):

```yaml
trigger_class: string                 # alert | upstream-agent | scheduled-check
trigger_id: string                    # alert ID or upstream incident-id
payload: object                       # original trigger payload
parent_identity: string               # service-account or upstream-agent identity
```

**Outbound — `agents/sre/<incident-id>/proposed`**:

```yaml
incident_id: string
plan:
  - step: int
    type: read | write
    peer: string
    verb: string
    action_class: string              # required for type=write
    args: object
    citations: [{topic, ts, digest}]  # standard sources array
sources: [{topic, ts, digest}]        # plan-level citations (mandatory)
time_quality: object                  # ADR 0514 envelope
correlation_id: string                # ADR 0822
```

**Outbound — `agents/sre/<incident-id>/closed`**:

```yaml
incident_id: string
outcome: resolved | partial | escalated | failed
verified: bool
transcript_audit_key: string          # pointer into audit-integrity tier
incident_class: string                # for eval-harness replay
duration_seconds: int
sources: [...]
time_quality: object
correlation_id: string
```

## Sequencing dependencies

`goat-sre-agent` cannot land before its dependencies. Ordered:

1. **Block 23** — Tipper + Scout MVP. The bones (queryable-by-default, citation discipline, schema-enforcer interceptor, ephemeral-agent lifecycle, mandatory data-dictionary, materialized lineage) are the safety architecture.
2. **Block 17A.5** — per-site policy engine implemented. Today the engine is design-landed only (the Go service `db-policy-engine` is not yet in the tree per `CLAUDE.md` §"Policy Engine"); the agent depends on the engine being live for write-action gating.
3. **Block 27** — wide-event observability operational. `correlation_id` cross-plane joins are the substrate that makes "did the agent's restart cause the alert spike" answerable.
4. **Block 28** — WASM sandbox available, in case any tool-peer plugin lands externally-authored.
5. **Block 36 / [ADR 0514](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0514-time-quality-attestation.md)** — time-quality attestation propagated through the fabric. Agent emissions carry the quality envelope; consumers filter / weight by quality.

Block 69 (implementation tracker) sequences after these. Authoring can start in parallel with their implementation; deployment cannot.

## Out of scope (explicit)

- Cross-site SRE-agent coordination. v1 is per-site; cross-site escalation is via the existing operator surface.
- Multi-agent SRE composition (multiple SRE agents on one incident). v1 is one-agent-per-incident.
- Long-running auto-remediation pattern (continuous TLS rotation, continuous credential hygiene). Returns through its own ADR if it earns the case.
- Adversarial-prompt robustness on the planner LLM. Shared concern with Scout.
- Specific model + serving stack pick — deferred to the eval harness output.
- Generic SSH / SQL / Ansible god-shell — explicitly rejected per [ADR 0515 §"Alternatives considered"](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0515-sre-agent-scout-class-peer.md).

## What it is not

- It is **not** an autonomous SRE replacement. Operator-in-the-loop is the v1 default for every consequential class, indefinitely for `load_bearing: true` classes.
- It is **not** a chatbot front-end to the fabric. It plans, diagnoses, proposes, and (under authority) executes typed actions. Conversational debugging is operator-territory.
- It is **not** a separate "control plane" parallel to the existing fabric. It is one peer + a small fleet of typed tool peers, all riding the substrate already in place.
- It is **not** a guardrail-by-regex stack. The regex blacklist pattern is structurally rejected (D2). Safety is typed-action + lifecycle gating + policy engine, by construction.

## Operator skepticism culture (inherited from Scout)

Trust = "I can verify the agent's work in seconds." The same UI contract from [`scout.md` §"Citation-alongside-prose UI contract"](scout.md) holds:

- Prose alongside, never replacing, the citation table.
- No collapsing of the citation column by default.
- Lineage-link affordance — every closed incident carries a "show provenance" action that invokes `cmd/lineage/backward/agents/sre/<incident-id>/closed`.
- Audit-key affordance — every closed incident carries the audit-key pointer for full transcript replay.

The agent serves the operator. The operator never serves the agent.
