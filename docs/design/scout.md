# Scout — ad-hoc human-defined agent, proof case 2 of 2

| Field | Value |
|---|---|
| Status | Draft (Phase 2D-late / Phase 3 commitment) |
| Role | Proof case 2 of 2 for the rapid-adaptation-with-AI bones |
| ADR anchor | [`../adr/0512-rapid-adaptation-with-ai.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) |
| Companion proof case | Tipper — see [`tipper.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md) |
| Bones doc | [`ai-rapid-adaptation.md`](ai-rapid-adaptation.md) |
| Implementation tracker | `../project/implementation-plan.md` Block 23 |

## What Scout is

Scout is the **ad-hoc human-defined agent** — proof case 2 of 2 for the rapid-adaptation-with-AI substrate. An operator asks a natural-language tactical question. Scout spawns request-scoped, plans against the fabric's queryable catalog (per the queryable-by-default bone), executes, assembles a **cited live answer**, and tears down. No standing peer accumulates between requests.

Scout proves the bones hold under the **ephemeral lifecycle** shape, complementing Tipper's proof at the **long-running specialist** shape. Both share the agent-class peer pattern; only lifetime, identity scope, and emission addressing differ.

## What Scout does (operational walkthrough)

A typical request:

1. **Operator asks a question** in natural language. Example: "Show me anomalous tracks from radar-* in the last 2 hours, with a live map and citations."
2. **Scout spawns** with a request-scoped workload identity derived from the operator's parent identity.
3. **Scout's planner** translates the question into a structured query plan — a sequence of fabric queryable invocations against `attest/queryable/**` (the catalog). The planner is LLM-backed in production but **swappable at the planner-peer boundary** (see "LLM swappability" below).
4. **Scout executes the plan** — invokes `cmd/<peer>/query` queryables in order, accumulates `matches`, `unit` tags, `confidence` annotations, and source citations.
5. **Scout runs pre-flight checks** — refuses or warns if source data falls below density / staleness / consistency floors. Concrete checks: `sample_count` minimums on aggregates, `staleness` thresholds against per-topic data-dictionary `freshness_target`, cross-source-consistency where multiple sources should agree.
6. **Scout assembles the answer** under `agents/scout/<request-id>/...`:
   - `agents/scout/<request-id>/answer` — the prose / table / structured response.
   - `agents/scout/<request-id>/viz` — the live visualization (map, chart, time-series) when the request implies one.
   - `agents/scout/<request-id>/transcript` — the full plan + execution trace.
   - Each emission carries the standard `sources` citation array.
7. **The operator's UI** subscribes to the `<request-id>` namespace and renders prose **alongside citations**. The citation table — fabric topic + timestamp + payload digest per claim — is non-collapsible. Prose is advisory; citations are the contract.
8. **Scout tears down** on completion or timeout. The audit-logger has the full transcript under one request-id-scoped key for replay.

## The ephemeral lifecycle in detail

Distinct from long-running peer lifetime:

- **Spawn trigger.** Either a human request via the Scout entry-point (`cmd/agents/scout/ask`) or an upstream triggered event (a long-running specialist that wants a deeper investigation — bounded by the parent agent's policy authorization).
- **Request-scoped identity.** Derived from the requesting human or upstream agent's identity. No privilege escalation through ad-hoc spawn — Scout cannot query topics the parent identity could not. The identity carries the request-id as a claim so the audit-logger can correlate.
- **Lifetime budget.** Default: 5 minutes wall-clock or until completion, whichever first. Configurable per request up to a hard ceiling (default 30 minutes). Long-running tactical questions that exceed this convert into preplanned-specialist work, not extended Scout runs.
- **Storage.** None. Scout's working memory is in-process; the substrate carries the audit trail.
- **Teardown.** On completion: emit the answer + transcript, tear down the worker. On timeout: emit a partial answer with explicit `incomplete: true` flag + the work-so-far citations. Either way, the audit-log entry under `<request-id>` is closed by an explicit terminal record.

## The planner — swappable at the boundary

Scout's planner is the LLM-backed component (in production). The **convention is the contract** — what the planner outputs is a structured query plan, not free-form text. Implementations swap behind this boundary without changing Scout's substrate behaviour.

Phase 2D bones — **deterministic / rule-based planner** against a fixture corpus:

- Pattern-match the question against a set of known query templates ("show me anomalous X from Y in last Z" → `cmd/agents/<X>/query` with parameters).
- No LLM. Useful even when LLM serving is unavailable — island-mode-correct.
- Proves the substrate convention without proving model fidelity.

Phase 3 — **local quantized model** (e.g., on AGX Orin or x86 mgmt-host):

- Llama / Mistral / similar, quantized to fit available memory.
- No outbound network for inference. Sovereign.
- Higher fidelity on under-specified questions; better natural-language coverage.

Phase 3+ — **vendor LLM endpoint via egress proxy** for unclassified inquiries:

- Routed through the data-conditioning checkpoint (ADR [`../adr/0806-egress-proxy-cascade.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0806-egress-proxy-cascade.md)).
- Sovereignty preserved by egress + policy gating, not by the model itself.
- Suitable when bandwidth + classification permit.

The planner-peer boundary lives at `cmd/agents/scout/plan` — Scout invokes it with the question + catalog snapshot, gets back a structured plan. Planner instances run as separate peers; multiple planners may coexist (a deterministic + a local-LLM, with Scout choosing per request based on policy + availability).

## Pre-flight checks (the agent-design discipline)

The substrate gives Scout the means to detect bad-input situations; Scout uses them. Three checks gate every answer:

### Density check

Every aggregate in the answer carries a `sample_count`. If `sample_count` falls below a configurable floor (default: 30 for statistical claims, 5 for "any" claims), Scout **warns** in the answer:

> ⚠ This claim is based on only 4 samples; treat as advisory.

If `sample_count` is zero on a claim that requires data, Scout **refuses** that claim and returns the question with the data gap labelled.

### Staleness check

Every queryable response carries a `latest_sample_timestamp`. Scout compares against the topic's `freshness_target` from `attest/schema/<topic>` and the question's implicit time window. If samples are older than expected, Scout warns or refuses depending on severity.

### Consistency check

When the answer draws on multiple sources that should corroborate (e.g., two radars covering the same airspace), Scout compares overlapping samples for consistency. If sources disagree beyond a configurable tolerance, Scout flags the inconsistency in the answer rather than picking a winner silently.

These checks are **not optional** — Scout's emission validator rejects answers that don't include the check results.

## Citation-alongside-prose UI contract

The contract for any human-facing rendering of a Scout answer:

- **Prose** appears alongside, never replacing, the citation table.
- **Citation table** lists `(fabric topic, timestamp, payload digest, sample count, staleness)` for every claim.
- **No collapsing** of the citation column by default. An operator can hide it explicitly per session, but the audit log records that.
- **Verifiability** — clicking any citation row opens the source topic at the cited timestamp via `cmd/<peer>/query` with the digest as a constraint. The operator can confirm the cited datum exists and matches the digest.
- **Lineage link** — every answer carries a "show provenance" action that invokes `cmd/lineage/backward/agents/scout/<request-id>/answer` (per [`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md)) and renders the upstream graph.

This is the operator-skepticism culture made enforceable in software. Trust = "I can verify the work in seconds."

## Refusal modes

Scout refuses, rather than guesses, in these cases:

- **No queryable matches the question.** "I cannot answer — no fabric peer exposes a queryable for this domain." Scout surfaces what queryables it found and what was missing.
- **Authorization scope insufficient.** The parent identity cannot reach a topic the answer would require. Scout names the missing authorization, does not attempt the query.
- **Pre-flight checks fail catastrophically.** Density / staleness / consistency floors all breached → refusal rather than misleading answer.
- **Policy-gated `cmd/` would be needed.** Scout does not issue outbound `cmd/` in v1; if a question can only be answered by issuing one, Scout names that and refuses.
- **Hard timeout reached.** Partial answer + `incomplete: true` flag.

A refusal is itself an emission with citations (what was attempted, what failed) and lands in the audit log.

## Topic schema

**Inbound — `cmd/agents/scout/ask`**:

```yaml
question: string                      # natural language
operator_identity: string             # the requesting human's parent identity
context:                              # optional, freeform
  mission_phase: string?
  recent_request_id: string?          # for follow-up questions
constraints:
  max_lifetime_seconds: int?          # default 300, cap 1800
  max_topics_queried: int?            # default 50
  policy_scope: string?               # explicit policy scope override (subject to authorization)
output_form:                          # optional preference
  prose: bool                         # default true
  table: bool                         # default true
  visualization: enum?                # map | timeseries | chart | none
```

**Outbound — `agents/scout/<request-id>/answer`**:

```yaml
request_id: string
question: string
answered_at: rfc3339
prose: string
table:
  columns: [...]
  rows: [...]
visualization_ref: string?            # zenoh keyexpr of the live viz, when one was produced
preflight:
  density: pass | warn | fail
  staleness: pass | warn | fail
  consistency: pass | warn | fail
warnings: [string]                    # per-claim warnings
incomplete: bool                      # true if timed out
sources: [...]                        # citation array — one entry per fabric topic consumed
```

**Outbound — `agents/scout/<request-id>/transcript`**: full plan + per-step execution log + planner output. Audit-grade, replay-capable.

## Identity, audit, observability, schema

- **Identity:** request-scoped derivation from operator parent. Phase 2 — Ory sub-identity; Phase 3+ — SPIFFE SVID with request-id claim.
- **Audit:** every emission keyed by request-id under the operator's parent identity. Full transcript replayable.
- **Observability:** Prometheus on the Scout container — request rate, planner latency, queryable-call count per request, refusal rate, pre-flight failure rates by check.
- **Schema declaration (mandatory):** Scout publishes schemas for `agents/scout/**` topics at `attest/schema/agents/scout/**`. Per [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md).
- **Lineage:** Scout's emissions feed the lineage materializer through the audit-logger. Backward lineage on a Scout answer walks back to source `data/...` topics through any intermediate `agents/...` (e.g., a Tipper anomaly cited as a source).
- **Policy:** Scout v1 issues no outbound `cmd/` other than queryables. The first version that needs to issue an actuating `cmd/` triggers a separate decision-review per ADR 0512's trigger conditions.

## Implementation surface

| Path | Purpose |
|---|---|
| `ops/agents/scout/` | Rust crate — orchestrator (lifecycle, planner-call, queryable execution, emission assembly, pre-flight checks) |
| `ops/agents/scout/planners/deterministic/` | Phase 2D rule-based planner (template matcher) |
| `ops/agents/scout/planners/llm/` | Phase 3 LLM-backed planner (model client + tool-call shape) |
| `ops/agents/scout/schema/` | `attest/schema/...` source-of-truth |
| `ops/ansible/roles/scout/` | Deploy role |
| `docs/operations/scout-runbook.md` | Operator runbook (created when Scout deploys) |

## Out of scope for Scout v1

- LLM-backed planner — Phase 3 follow-on, swappable behind the planner-peer boundary.
- Outbound `cmd/` issuance (Scout that *acts*, not just *answers*).
- Multi-turn conversational interface — v1 is single-shot question → answer + teardown.
- Voice / speech interface.
- Cross-site federated planning (a Scout instance at site A invokes queryables across multiple sites under partition).
- Adversarial-prompt robustness — defers to publisher-trust-model and prompt-injection design work.
- Vector-store-backed semantic search (planner finds queryables by name matching in v1; semantic similarity comes when a vector store lands).
- Long-running mission-tracking sessions (those become preplanned specialists).

## How we know Scout works (test plan)

- **Unit tests.** Plan generation against known question templates; queryable invocation correctness; pre-flight check correctness; emission schema validation; refusal-mode triggering.
- **Smoke test (CI).** Synthetic question → planner → queryable mock → answer with citations + pre-flight pass. Audit-logger receives transcript; lineage materializer indexes.
- **Integration test (integdev).** With Tipper running and emitting anomalies, ask "show me anomalies from source X in the last hour" — Scout plans, calls `cmd/agents/tipper/query`, assembles answer with citations, emits viz reference. Operator UI renders prose + citation table.
- **Substrate-proof criterion.** A second ad-hoc agent (e.g., a `briefing` agent that produces a daily situation summary) ships by reusing the agent-class convention without changing it. Until that ships, the substrate proof for the ad-hoc shape is *provisional*.
- **Soak test.** 24h soak with synthetic operator question stream (mix of well-formed, malformed, refusal-triggering). Pass: refusal rate within expected band, pre-flight checks fire correctly, no lifecycle leaks (every request id has a terminal record).

## References

- ADR [`0512`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) — bones + Scout as proof case 2
- [`ai-rapid-adaptation.md`](ai-rapid-adaptation.md) — bones / strategic frame
- [`tipper.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md) — proof case 1 (preplanned)
- [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) — schema declaration discipline
- [`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md) — provenance Scout calls into
- [`entity-vocabulary.md`](entity-vocabulary.md) — entity glossary planner uses
- ADR [`0508`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0508-audit-logger-interceptor.md) — audit-logger interceptor
- ADR [`0805`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0805-policy-engine-active-passive.md) — policy engine
- ADR [`0806`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0806-egress-proxy-cascade.md) — egress proxy (Phase 3+ vendor LLM routing)
- `tech-strategy.md` — Rust default for data-services
- `../project/implementation-plan.md` Block 23
