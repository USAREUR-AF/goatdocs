# Rapid adaptation with AI — the bones

| Field | Value |
|---|---|
| Status | Draft (Phase 2D-late / Phase 3 commitment) |
| ADR anchor | [`../adr/0512-rapid-adaptation-with-ai.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) |
| Proof cases | [`tipper.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md) (preplanned), [`scout.md`](scout.md) (ad-hoc) |
| Companion conventions | [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md), [`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md), [`entity-vocabulary.md`](entity-vocabulary.md) |
| Implementation tracker | `../project/implementation-plan.md` Block 23 |

## Why this doc exists

The bones design doc for rapid-adaptation-with-AI. The strategic frame ("rapid adaptation, not an AI playground"), the four substrate primitives ("the bones"), the named posture (minimal semantic layer; refusal to own ontology / transformation / governance shape), and the five-failure-mode discipline all live in ADR [`0512`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md). This document is the design-level companion that future contributors read alongside the ADR.

## The thesis in one paragraph

Missions, threats, and partnerships change faster than any team can build bespoke software for each new shape. AI lets a small team produce trustable, mission-relevant work at the speed of those changes. **Rapid adaptation with AI** is the project capability commitment: the team operates at the tempo of changing missions, with AI doing the heavy lifting of "go from question / threat / need to trustable output," held to a sovereign + auditable + island-mode-correct discipline. This is mission-shape work — not an AI feature gallery.

The substrate primitives (Zenoh + identity + audit + policy + observability) already exist in this repo for other reasons. The bones below are the deliberate convention that turns those primitives into an environment where preplanned specialists *and* human-defined ad-hoc agents both compose cleanly. The honest framing of the posture: **a minimal semantic layer with a deliberate refusal to own ontology, transformation logic, or governance UI shape.** Mandatory schema declaration plus a publish-time enforcer is, by construction, a platform-shaped commitment at the data-description layer; we name it as such rather than calling the whole project "anti-platform." What we commit, in writing, to **not** build is the big-platform shape — central ontology registries, transformation engines as products, governance-UI-as-product.

This is also the substrate the project brands externally as **GOAT-Net (Geo-Distributed Open Architecture Transformation Network)** — the data backbone that vendors integrate with and that partners federate with. goat is the engineering project; GOAT-Net is what those audiences interact with.

**Maturity caveat.** GOAT-Net is at proof-of-concept stage. We are in uncharted territory — sovereign tactical-edge data backbones at this shape and scope do not have established operational precedent at theater scale. The direction is sound and anchored in mainstream distributed-systems patterns; specific scaling, performance, and operational characteristics will be discovered, not asserted. A viable scaling plan exists (ADR [`../adr/0216-goat-net-federation-and-site-planes.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0216-goat-net-federation-and-site-planes.md), design at `goat-net-scaling.md`) and becomes operative *if* GOAT-Net earns it through the early phases. The project commits to the direction, not to specific numbers.

## The four bones (durable substrate primitives)

### 1. Agent-class peers

A peer class that extends [`phoenix-architecture.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/phoenix-architecture.md) §2A with explicit declarations:

- `services/agents/<name>/<instance>/announce` carries `{consumes, emits, commands_issued, identity_subject, agent_version}`.
- Emits **only** to `agents/<name>/...` (long-running) or `agents/<name>/<request-id>/...` (ad-hoc). Cross-namespace publishing is forbidden by convention; the audit-logger / schema-enforcer interceptor enforces this against the announce manifest.
- Workload identity is offline-CA-issued (Ory Phase 2; SPIFFE Phase 3+).
- Health under `health/agents/<name>/<instance>`; standard Prometheus.

Long-running specialists (Tipper) and ad-hoc agents (Scout) share this pattern — only the lifecycle differs (per bone #4).

### 2. Queryable-by-default fabric — our MCP analog

The convention that makes LLM-backed agents work without bespoke per-peer integration code.

**Every state-holding peer exposes `cmd/<peer>/query`**, a structured queryable whose input + output schemas are published under `attest/queryable/<peer>`. A planner agent — LLM-backed or rule-based — discovers what the fabric carries by walking `attest/queryable/**`. No central registry, no schema-as-a-service.

What a queryable response carries:

- `matches` — the data that satisfies the query, each entry with full citation `(topic, timestamp, digest)`.
- `unit` tags on every numeric field (per [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md)).
- `confidence` / `sample_count` on aggregates so a planner can detect sparse-input situations.
- `entity_ref` cross-references to [`entity-vocabulary.md`](entity-vocabulary.md) for the entities involved.

Convention is opt-in by peer class — state-holders expose; transient passthrough peers don't have to. The catalog is the fabric.

This is the project's analog of Anthropic's Model Context Protocol — a uniform shape for exposing data + tools to AI-backed agents — built on the substrate primitives we already have.

### 3. Citation discipline

**Every emission under `agents/...` carries a `sources` array** — one entry per fabric input that contributed, with `(topic, timestamp, digest)`. Zero-citation emissions are structurally invalid; the audit-logger / schema-enforcer rejects.

Why this is the trust model: trust = "I can verify the work in seconds," not prose persuasion. An operator reading a Scout answer sees the table of source topics + timestamps + digests next to every claim. The agent's prose is advisory; the citations are the contract.

The audit-logger ([`../adr/0508-audit-logger-interceptor.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0508-audit-logger-interceptor.md)) carries citations into the integrity tier ([`../adr/0811-audit-log-integrity.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0811-audit-log-integrity.md)) automatically — provenance is a fabric property, not a per-agent concern.

### 4. Ephemeral-agent lifecycle

Distinct from long-running peer lifetime. An ad-hoc agent (Scout-shape):

- Spawns from a request — typically a human question, sometimes an upstream triggered event.
- Receives a **request-scoped workload identity** (sub-identity of the requesting human, scoped to the request lifetime).
- Subscribes / queries within the bounds of the parent identity's authorization (no privilege escalation through ad-hoc spawn).
- Emits under `agents/<name>/<request-id>/...` with full citations.
- **Tears down on completion or timeout.** No state outside the audit trail. Phoenix-native at request scope.

The full transcript (request → plan → sources consumed → output) lives in the audit log under one request-id-scoped key for replay. An assessor can reconstruct any rapid-adaptation session.

## The five-failure-mode discipline

Live data + LLM-driven planners is dangerous without discipline. Five tactical-grade failure modes, mapped to mitigations:

| # | Failure mode | Substrate mitigation | Agent-design mitigation |
|---|---|---|---|
| 1 | Unit confusion (m/s vs knots) | Mandatory `unit` field in queryable I/O schemas | Planner reads units from `attest/schema/**` before composing |
| 2 | Entity confusion (sensor vs source vs emitter) | Cross-cutting entity vocabulary; `entity_ref` field in schemas | Planner resolves references via the glossary before joining |
| 3 | Confidence laundering (sparse data → confident prose) | `confidence` / `sample_count` fields on aggregates; citation density requirement | Pre-flight checks: refuse / warn on sparse, stale, or contradictory inputs |
| 4 | Cross-namespace leakage (agent publishes to `data/` or `release/`) | Strict output namespace gating; audit-logger enforces against announce manifest | — |
| 5 | Audit opacity (can't reconstruct why the agent said that) | Citation discipline + lineage queryable | Citation always shown alongside prose in human-facing output |

The substrate side is **bones**; the agent-design side is **discipline in Scout** (see [`scout.md`](scout.md)). Both are required.

## The posture: minimal semantic layer; refusal to own ontology / transformation / governance shape

The bones above (queryable-by-default, citation discipline, ephemeral-agent lifecycle, mandatory data-dictionary declaration, schema-enforcer interceptor at the publish path, materialized lineage) constitute a thin **semantic layer**. Calling this "anti-platform" would overstate the case: a layer that mandates schema declaration and rejects undeclared publishes is, by construction, a platform-shaped commitment at the data-description layer. Adopters who climb onto these conventions take on a real portability cost if they later swap fabrics — declarations, citation envelopes, and queryable I/O shapes are portable in spirit but not byte-for-byte portable.

What the project explicitly refuses is the broader platform shape of the large commercial data-platform offerings — central ontology registries, transformation engines as products, governance-UI-as-product, controlled-vocabulary-as-platform-feature. Each layer below the substrate is provided by the thinnest discipline that gets the value:

| Layer | What we own (and adopters inherit) | What we explicitly refuse |
|---|---|---|
| **Semantic** | Mandatory two-state schema declaration ([`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md)); `unit` / `confidence` / `description` / `entity_ref` fields; schema-enforcer interceptor as a publish-time gate. **A narrow platform-shaped commitment, named here so adopters are not surprised by the lock-in cost.** | Central data dictionary as a service; controlled-vocabulary registration; field-meaning-as-platform-property |
| **Ontological** | Living entity-vocabulary glossary ([`entity-vocabulary.md`](entity-vocabulary.md)); 9-prefix top-level keyexpr ontology; `entity_ref` fields point into the glossary. Documents the ontology; doesn't enforce a controlled one. | Controlled ontology; mandatory entity-resolution pipeline; "object types must be registered before use" platform |
| **Transformation** | "A transformation is just a peer" — interceptors per [`../adr/0501-rust-interceptors.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0501-rust-interceptors.md), agent-class peers per ADR 0512, stateful consumers per [`../adr/0505-stateful-consumer-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0505-stateful-consumer-pattern.md). Substrate provides pub/sub + storage shape; transformations are written in normal code in normal repos. | Transformation engine as a product; pipeline-as-a-service; visual workflow editor; opaque "platform manages your transforms" |
| **Governance** | Identity ([`../adr/0411`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0411-ory-idp-mvp.md), `../adr/0412`) + policy engine ([`../adr/0805`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0805-policy-engine-active-passive.md)) + audit-logger ([`../adr/0508`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0508-audit-logger-interceptor.md)) + citation discipline + lineage ([`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md)). All composable, individually replaceable. | Governance UI as a product; lineage-as-a-service; central RBAC console as the only interface |

**The honest commitment.** The semantic layer is a deliberate, narrow platform commitment. The ontology / transformation / governance layers are not platforms; they are conventions over individually replaceable components. Adopters get the leverage of the semantic layer; they pay a portability cost if they later swap fabrics. The tradeoff is documented explicitly so downstream adopters are not surprised.

**Revisability.** Each piece is recoverable individually — if the queryable-by-default convention is wrong, revise it without rebuilding the substrate. The platform shape we refuse (where the vendor owns *all* layers and exit is structurally impossible) is what would be unrecoverable; the four-layer table above is the test.

## What this enables in operation

Concrete behaviours the bones make possible:

- **A new always-on watcher peer ships in days.** A team writes the agent-domain logic; the convention provides identity, audit, queryable surface, schema declaration, citation, observability, deployment shape. Marginal cost of agent N+1 is dominated by domain logic.
- **An operator gets a cited live answer to an ad-hoc tactical question in minutes.** Scout spawns request-scoped, plans against the queryable catalog, executes, assembles, cites, tears down. The operator sees prose alongside source citations and can verify in seconds.
- **A new partner joins the fabric without bespoke integration code.** `release/<partner>/...` namespace + bring-your-own-OIDC + `attest/schema/**` declarations all compose with the agent platform — partner-released topics are discoverable by Scout with the same citation discipline (cross-references [`mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md)).
- **An incident reviewer reconstructs why the agent said what it said.** Lineage queryable backward-walks from the output to source topics; audit log carries the full request transcript; data-dictionary tells the reviewer what each field meant at the time.
- **A new vendor's data lands in GOAT-Net cleanly.** Vendor charter (see [`../vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md)) enforces schema declaration; data-dictionary makes it browsable; lineage tracks downstream uses; agents query it without per-vendor integration.

## Out of scope (explicitly named)

- Specific LLM model + serving stack choice — separate Phase 3 ADR.
- Vector store for semantic search (Qdrant / LanceDB) — deferred until Scout's planner needs it.
- Multi-agent orchestration as a primary flow.
- Federated agent state across sites.
- Agent-platform UI / "console" beyond per-agent dashboards already in observability.
- Adversarial-prompt robustness for the LLM-backed planner.

These are tracked as trigger conditions in ADR [`0512`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md).

## References

- ADR [`0512`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) — anchor decision
- [`tipper.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md) — preplanned proof case
- [`scout.md`](scout.md) — ad-hoc proof case
- [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) — mandatory schema declaration + Swagger-like rendering
- [`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md) — RocksDB materializer + KuzuDB upgrade path
- [`entity-vocabulary.md`](entity-vocabulary.md) — living glossary
- [`mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md) — partner federation
- [`../vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md) — vendor obligations
- `zenoh-data-fabric.md` — substrate
- [`phoenix-architecture.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/phoenix-architecture.md) — phoenix-native peer pattern
- `identity-architecture.md` — four-domain identity model
- `../project/implementation-plan.md` Block 23
