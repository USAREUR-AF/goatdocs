# Entity vocabulary — living glossary for cross-cutting fabric entities

| Field | Value |
|---|---|
| Status | Living document |
| ADR anchor | [`../adr/0512-rapid-adaptation-with-ai.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) §"Anti-platform posture" |
| Companion | [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) (referenced via `entity_ref`) |

## Why this exists

Without a shared vocabulary, "sensor," "source," and "emitter" become near-synonyms that mean different things in different schemas, and Scout's planner cannot join them confidently. This is the **entity-confusion** failure mode named in [`ai-rapid-adaptation.md`](ai-rapid-adaptation.md). The fix is the thinnest possible discipline: a **living glossary** that names the small set of cross-cutting entities the fabric talks about, with one canonical term per concept and a plain-language description.

This is **not** a controlled ontology. There is no "object types must be registered before use" gate. Schemas reference entries via the `entity_ref` field in [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md); when a publisher needs an entity not yet listed, they publish under their schema and the glossary catches up — append a row, link from the schema. Add via PR; remove with care.

## How to use

- Schemas reference entries here via `entity_ref: <slug>`. Example: a `source_id` field with `entity_ref: sensor` declares "this string identifies a sensor."
- Scout's planner consults the glossary when joining or correlating across topics.
- Operators read the glossary to disambiguate terms when writing questions or interpreting answers.
- Lineage labels graph nodes with their `entity_ref` (where the schema declares one).

The glossary is **per-project**, not global. Other deployments in this codebase family maintain their own. A future cross-project meta-glossary may emerge but is not in scope today.

## Conventions

- **Slug**: lowercase, hyphenated, singular (`sensor`, not `Sensors`).
- **Canonical term**: the one preferred name; alternates appear in "also called."
- **Description**: plain-language, two-to-four sentences. What it *is*, not what schemas *do with* it.
- **Identity shape**: how instances of the entity are identified on the fabric (typical `id` field shape).
- **Where it appears**: example fabric topics where the entity is the subject or the object.

## Entries

### `track`

- **Canonical term**: track
- **Description**: A persistent identification of a moving object across multiple sensor samples. A track has a unique identifier, an emitter (the sensor that sees it), a position history, and zero or more derived attributes (classification, kinematic state, behaviour score).
- **Identity shape**: `track_id: string` — unique within a sensor source. Cross-sensor track-fusion produces a separate fused-track entity (out of scope for v1).
- **Where it appears**: `data/track/<source-id>/<track-id>`, `agents/tipper/anomaly/<track-id>`, `agents/tipper/queue/<track-id>`.

### `sensor`

- **Canonical term**: sensor
- **Also called**: source, emitter (when emphasizing the data-emission role)
- **Description**: A physical or virtual device that observes the world and emits data on the fabric. Radars, cameras, acoustic arrays, ELINT receivers, software detectors are all sensors. A sensor has an identity, a location (or virtual location), a declared data domain, and a freshness target.
- **Identity shape**: `sensor_id: string` — typically `<class>-<site>-<index>` (e.g., `radar-site-a-01`).
- **Where it appears**: `data/track/<sensor-id>/...`, `data/video/<sensor-id>/...`, `attest/schema/data/<class>/<sensor-id>/...`, `health/sensors/<sensor-id>/...`.
- **Note**: "source" is acceptable as a field name when context makes it unambiguous (e.g., `source_id` in a track schema clearly means the emitting sensor). Cross-cutting prose should use "sensor."

### `anomaly`

- **Canonical term**: anomaly
- **Also called**: detection, flag (in some contexts)
- **Description**: An emission from an agent-class peer indicating that one or more samples deviate from a baseline — statistically (Tipper), behaviourally (TTP-drift agent), or against a declared rule. An anomaly cites the sample(s) that triggered it, names the dimensions on which the deviation occurred, and carries the agent's confidence representation.
- **Identity shape**: `track_id` or `entity_id` of the subject + emission `timestamp` (anomalies are not separately identified — they're emissions about other entities).
- **Where it appears**: `agents/<name>/anomaly/<subject-id>` (e.g., `agents/tipper/anomaly/T1234`).

### `queue`

- **Canonical term**: queue
- **Description**: A ranked or unranked set of items awaiting further processing — typically by humans or downstream agents. Tipper's anomaly queue is the canonical example. A queue entry has a status (`pending` / `inspected` / `dismissed`), a TTL, and a citation back to what put it in the queue.
- **Identity shape**: queue entries are identified by the subject they reference (e.g., `track_id`).
- **Where it appears**: `agents/<name>/queue/<entry-id>`.

### `request`

- **Canonical term**: request
- **Also called**: query, inquiry (deprecated — "request" preferred to avoid overloading "query")
- **Description**: A bounded unit of ad-hoc work spawned by a human or upstream agent. Each Scout invocation is a request. A request has a unique id, a parent identity (who asked), a question or trigger, a scoped lifetime, and emits its output under a `<request-id>`-namespaced subtree.
- **Identity shape**: `request_id: string` — UUID v4 typically, `req-<short>` form in human-readable contexts.
- **Where it appears**: `agents/scout/<request-id>/answer`, `agents/scout/<request-id>/transcript`, `agents/scout/<request-id>/viz`.

### `partner`

- **Canonical term**: partner
- **Description**: A named external organization with whom data is exchanged under the partner-sharing pattern (ADR [`../adr/0821-mission-partner-sharing-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md)). A partner has a slug, a federated OIDC IdP, and a signed Partner Data Sharing Charter.
- **Identity shape**: `partner_slug: string` — short, lowercase, hyphenated (e.g., `partner-a`).
- **Where it appears**: `release/<partner>/...`, partner-side reciprocity uses the same shape; `health/partner/<partner>/...`.

### `agent-instance`

- **Canonical term**: agent-instance
- **Description**: A deployed instance of an agent-class peer. Long-running specialists (Tipper) typically have one or a few instances per site; ad-hoc agents (Scout) spawn instances per request. Each instance has a workload identity, a host, and a lifecycle.
- **Identity shape**: long-running — `<agent-name>/<instance-id>` (e.g., `tipper/instance-a`); ad-hoc — `<agent-name>/<request-id>` (e.g., `scout/req-7891`).
- **Where it appears**: `services/agents/<name>/<instance>/announce`, `health/agents/<name>/<instance>`, audit-log identity claims.

### `vendor`

- **Canonical term**: vendor
- **Description**: An external commercial entity providing data, data services, or data-emitting capabilities to the project under the Data Services Provider Charter ([`../vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md)). Distinct from a partner — vendors are commercial suppliers; partners are mission peers.
- **Identity shape**: `vendor_slug: string`.
- **Where it appears**: `data/...` topics emitted by vendor systems (with vendor-id in the source path), `attest/schema-declaration/...` for binary formats, vendor schema-compliance dashboard entries.

### `release-event`

- **Canonical term**: release-event
- **Description**: A single auditable instance of data crossing the partner boundary. Distinct from a `release/<partner>/<topic>` allowlist entry (which permits a *class* of releases) — a release-event is one specific data sample being released, identity-bound and audit-logged.
- **Identity shape**: not separately identified; reconstructed from audit-log entries.
- **Where it appears**: implicit in audit-log entries with `release_event` semantics; `lineage` queryable surfaces them.

## Adding entries

When a schema needs to reference an entity that isn't here yet:

1. Open a PR that adds the entry (slug, canonical term, description, identity shape, "where it appears").
2. Land the schema referencing it in the same PR.
3. The PR reviewer's job is to check for conflict with existing entries — does the new entity overlap "sensor" or "track" too closely? If so, reuse the existing entry or add an "also called" line rather than introducing a near-duplicate.

## Removing or renaming entries

- **Removing**: only after all referencing schemas have been migrated. The glossary entry is a contract; removal is a breaking change governed by ADR [`../adr/0506-fabric-schema-evolution.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0506-fabric-schema-evolution.md).
- **Renaming**: keep the old slug as an alias; add a "preferred" pointer; migrate schemas at their own pace.

## What this is NOT

- **Not a controlled vocabulary.** Field names + descriptions in schemas are owned by the publishing peer.
- **Not a registry-as-a-service.** This is a markdown file. The fabric-as-dictionary discipline carries the load; the glossary is a thin convention layered on top.
- **Not exhaustive.** Domain-specific entities (radar-cross-section, IFF-mode, COA-segment) live in their domain schemas; the glossary covers cross-cutting entities only.

## References

- ADR [`0512`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) — anchor decision
- [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) — schemas reference glossary entries via `entity_ref`
- [`scout.md`](scout.md) — Scout's planner consults the glossary when joining
- [`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md) — lineage labels graph nodes by `entity_ref`
- [`tipper.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md) — Tipper's schemas reference `track` and `sensor`
- [`mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md) — references `partner`
- [`../vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md) — references `vendor`
