# Zenoh as an API substrate

**Status:** Planning / notional. Not Accepted. Not yet implemented. This page sketches a direction we may or may not invest in. Date: 2026-05-18.

## Thesis

A Zenoh fabric, a topic-and-asset registry, and per-vendor adapters together can mediate every interaction pattern a typical multi-system ecosystem ships — without a separate API protocol on top.

The transport stops being the integration story. The integration story becomes: **describe your data, optionally describe your capabilities, optionally adapt commands back to your native interface.** The portal owns the registry; Zenoh owns the wire; the vendor owns the adapter.

## The three primitives

| Primitive | What it is | Where it lives today |
|---|---|---|
| **Transport** | Topic-keyed pub/sub with capability-based ACL | Zenoh router on nova-a (Block 82A); will be mgmt-host pairs at every goat-net site under ADR 0844 |
| **Registry** | Per-vendor identity + topic + format + schema body + (future) capability/state | `ops/goat-zenoh-portal/` — Block 85 PR-A through PR-D |
| **Adapter (shim)** | Per-vendor process that subscribes/publishes on the fabric and translates to/from the vendor's native interface | Block 20 / ADR 0217 shim-repo-containment; per-vendor private repos |

Nothing in the thesis requires new substrate. The "graceful extension" path is small and additive — described later in this doc.

## What an API typically does, and how pub/sub + registry + adapter covers it

| Typical API pattern | Pub/sub + registry equivalent |
|---|---|
| `POST /radar/123/task` | Publish to `vendor/radar/123/task`. The radar's adapter subscribes to that key and translates the message into the radar's native command interface (vendor-side). The Zenoh ACL gates who is allowed to publish there. |
| `GET /radar/123/state` (poll) | Subscribe to `vendor/radar/123/state` — the adapter publishes state continuously (or on-change). Steady-state subscribers see updates as they happen; bursty consumers can use a Zenoh query against the same key to get the latest value. |
| `GET /assets?capability=area-scan` | Query the portal registry: `GET /api/assets?capability=area-scan`. Returns a list of key-expressions to subscribe to. The transport doesn't need a discovery primitive — the registry IS the discovery service. |
| API key / OAuth scope | Per-vendor offline-CA URI-SAN cert (`urn:goat-nova:vendor=<v>`) + per-key ACL allowlist enforced at the Zenoh router. Same machinery we already ship. |
| Webhook (server-pushes-to-client) | Subscribe. Pub/sub is just webhooks turned inside out — instead of the producer remembering every consumer's URL, every consumer subscribes to the producer's key. |
| Version negotiation (`/v2/radar`) | Already convention in the goat-net key shape: `vendor/system/.../v1`, `.../v2` per ADR 0506. Two versions on the wire simultaneously; consumers pick which to subscribe to. |
| Rate limiting / backpressure | Zenoh congestion control + per-vendor publish-rate quota at the router (forward-compat hook in ADR 0844). |
| Schema / OpenAPI doc | `.proto` data dictionary uploaded to the portal (Block 85 PR-A); rendered in `/schema.html` for humans, served via `GET /api/schemas/{key...}` for machines. |
| Idempotency tokens | Producer puts a UUID in the payload; the adapter dedupes. Same as REST. |
| Pagination | Query the registry returns a list, subscribe to each. Or use Zenoh query with key-expression wildcards. |
| Long-polling | Subscribe. |
| Streaming (gRPC / WebSocket) | Subscribe. This is what Zenoh is for. |

Two patterns where the equivalence isn't clean — listed honestly:

- **Synchronous request/response with tight latency budget.** Zenoh has a query primitive but for genuine RPC at sub-millisecond response budgets, you're better off with a direct unary call. We deliberately punted on query/response at the trial layer per ADR 0844. If a use case really needs RPC, the adapter can expose a localhost-only gRPC port and the caller hits that — the adapter is the integration boundary, not the fabric.
- **External partners who require REST.** Bridge VPSes terminate REST at the boundary and republish to Zenoh inside (Block 35 / ADR 0821 mission-partner-sharing-pattern). The pattern doesn't replace REST at the external surface; it eliminates it from the internal surface.

## Worked example: radar sequencing parity

The whiteboard sketch shows a typical radar-to-gateway integration:

```
1. Radar powers on; edge router up
2. Radar registers: capabilities + identity + initial state
3. Gateway queries the registry for matching radars
4. Gateway tasks a radar: "scan sector X"
5. Radar publishes detections
```

On pub/sub + registry + adapter:

```
1. Radar powers on; adapter (Block 20 shim, on the same Orin / co-located with radar)
   establishes Zenoh session with offline-CA leaf cert (urn:goat-nova:asset=<vendor>/radar/<id>).
2. Adapter posts to portal: POST /api/vendors/<v>/assets with capabilities + initial state.
   Adapter starts publishing heartbeat on system/health/<asset-id> every 30s.
3. Gateway queries portal: GET /api/assets?capability=area-scan → list of (asset-id, key) pairs.
4. Gateway publishes SensorTask on vendor/radar/<id>/task. Per-asset ACL allows the gateway's
   cert to publish here. Adapter subscribes, translates to the radar's native protocol
   (whatever that is — proprietary serial, SNMP, vendor REST, doesn't matter).
5. Radar produces detections; adapter publishes Detection on vendor/radar/<id>/detection.
   Subscribers (fusion, dashboards, audit-subscriber for compliance) receive them.
```

Parity preserved. The vendor's existing process for establishing functionality is unchanged from their side of the adapter — they still command the radar in whatever native way they always did. The fabric just routes the messages.

## Where the value is, beyond pub/sub-by-itself

The basic pub/sub usage we ship in PR-D is "register a topic, declare a schema, publish bytes, subscribe somewhere." That's enough to deliver data. What this thesis adds:

1. **Discoverability without coupling.** A new subscriber doesn't need to know which assets exist — it queries the registry by capability and gets a list. Adding a new asset doesn't require updating any subscriber's config. This is the eliminated-N×N integration cost that makes the fabric pay back its complexity.
2. **Bidirectional control without inventing a control plane.** Commands are publishes; adapters do the translation. No new protocol, no separate gRPC service, no extra firewall hole. The ACL grammar already handles "who can publish to which key" — we just extend it to per-asset task topics.
3. **Health and state visibility for free.** Once an asset publishes a heartbeat, the operator's dashboard sees it. No per-vendor monitoring integration. No SNMP polling. No vendor cooperation needed beyond running the adapter.
4. **Audit + compliance.** The audit-subscriber (Block 82S) sees every publish on `**`, including commands. Every "who tasked what when" is durable in MinIO with COMPLIANCE retention. No application-layer audit hook required.
5. **AI orchestration substrate.** The goat-sre-agent (Block 69, ADR 0515) needs ground-truth answers to "what can I task" and "what's healthy" before it can issue `cmd/`. The capability + state registry IS that ground-truth.

## Graceful-extension path (planning, not committed)

If we decide to invest, the substrate adds:

- **One field on the `topics` table** — `capabilities[]` (TEXT, comma-separated tags), or one new sibling table `topic_capabilities(topic_id, capability)`.
- **One optional new entity** — `assets(id, vendor_prefix, asset_type, instance_id, capabilities[], state, state_updated_at, live_or_sim)`. Heartbeat updates `state` + `state_updated_at` via a portal subscriber to `system/health/<asset-id>`.
- **One reserved Zenoh prefix** — `system/health/**` for heartbeats. (Already a candidate for the 12 reserved prefixes named in ADR 0844; this picks one slot.)
- **No new wire protocol.** Discovery is an HTTP query against the portal; tasks are publishes; state is a publish stream. The router doesn't grow new behavior.
- **Per-vendor adapter remains vendor-owned** in the per-vendor private repos pattern (ADR 0217). The portal doesn't ship adapters; the portal serves the registry that adapters consume.

Each step is one PR, each is operator-visible immediately on the existing `/vendor.html` summary view (we'd add an "assets" sub-section), and none of them moves Zenoh's protocol surface.

## Non-goals

- **Not replacing all APIs everywhere.** External partners who require REST keep REST at the bridge boundary (ADR 0821). Some internal services that genuinely need RPC keep that. This is "default to publish + subscribe + registry" inside the fabric, not "ban REST."
- **Not a new protocol.** Everything here is the existing Zenoh transport + existing portal HTTP + existing per-vendor identity. The thesis is a stance, not new substrate.
- **Not a commitment to build all of this.** This page sketches the direction. Investment decisions land per-phase, each with its own PR + design ADR.

## Where this fits in the existing block taxonomy

| Block | Relationship |
|---|---|
| Block 20 (Phoenix peer discipline) | Adapter pattern is literally the shim from Block 20 |
| Block 23 (schema-enforcer) | Consumes the registry as the source of truth for "what to validate" |
| Block 17A.5 (Policy Engine) | Owns the long-term ACL surface for who-can-publish-where |
| Block 69 (goat-sre-agent) | First non-human consumer of the asset/capability registry |
| Block 85 (portal-driven schema publishing) | Where this would land additively — same portal, new entity types |
| ADR 0844 (Zenoh deployment topology) | Names the 12 reserved prefixes; `system/health/**` slots into that table |
| ADR 0506 (fabric schema evolution) | The versioning convention (`.../v1`, `.../v2`) is already what this design assumes |
| ADR 0512 (rapid adaptation with AI) | Capability declarations are how AI agents pick what to act on |
| ADR 0856 (partner peering capability mint) | The cert-encoded-capability pattern this would extend to per-asset granularity |

## Open questions (deliberately not answered yet)

- Is `assets` a sibling to `topics`, a subtype of `topics`, or just metadata on `topics`?
- Heartbeat cadence — 5s, 30s, 60s? Adaptive on liveness budget?
- Do capabilities form a hierarchy (sensing → area-scan → radar) or a flat tag set?
- Does the portal subscribe to `system/health/**` directly, or do we add a thin "registry-updater" sidecar like audit-subscriber?
- How does this interact with the partner-peering portal (Block 84)? Same shape, different trust boundary, presumably.
- For the live/sim distinction: payload header, key suffix, or registry flag?

These don't need answers now. They get answered when we decide a phase is worth shipping.

## See also

- `docs/design/portal-schema-publishing.md` — the data-dictionary substrate this builds on
- `docs/design/zenoh-trial-fabric.md` — what's running on nova-a today
- `docs/design/nova-goatnet.md` — the trial-scope deployment envelope
- `docs/design/phoenix-architecture.md` §2A — the shim pattern
- `ADR 0844` — Zenoh deployment topology + reserved prefixes
- `ADR 0517` (proposed, not yet drafted) — Zenoh queryables for system discovery
- The portal page at `/patterns.html` (vendor-facing version of this doc)
