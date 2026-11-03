# Minimalism under network constraints

| Field | Value |
|---|---|
| Status | Design (authored 2026-05-24; first instance is [`flashlight.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/flashlight.md)). Project-wide doctrine; future bandwidth-constrained surfaces inherit from this. Anchored by [ADR 0861](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0861-minimalism-under-network-constraints.md). |
| Scope | The principles that govern any goat web surface designed to remain useful under degraded network AND degraded client compute. Not a framework — a discipline. |
| Related | [ADR 0861](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0861-minimalism-under-network-constraints.md) (doctrine adoption — the anchor decision record), [ADR 0862](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0862-two-tier-web-architecture-canonical-coprocessor.md) (the Tier-1-canonical / Tier-2-coprocessor architectural decision recorded separably), [`flashlight.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/flashlight.md) (first instance), `panoscope.md` (the richer companion this doctrine deliberately is NOT), [ADR 0112](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0112-tech-strategy-workload-shape-language-boundary.md) (workload-shape language boundary). |

## What this is

A doctrine for building modern web surfaces — including ones that need real-time data, client-side compute, in-line analytics — without abandoning the operator on a degraded link or a degraded device. The doctrine grew out of designing flashlight (a focus-oriented Zenoh inspection tool sibling to panoscope), but applies to any present-or-future goat surface where the operator might be on satellite-over-VPN, in nova-lan island mode, on a trickle of bandwidth during rapid-bringup, or on a low-memory mobile browser the bad guys can suspend at any moment.

The core observation: most modern web design assumes the network and the client are both good. When either degrades, the experience falls off a cliff — because the dominant patterns (single-page apps, framework-mediated reactivity, hydration) put a large up-front cost on the user before anything works. That cost is invisible on good networks and disqualifying on bad ones.

Minimalism under network constraints is the discipline of structuring web surfaces so that **a trickle of network produces a maximum of useful work**, while **layered enhancements deliver modern capability when conditions allow** — and gracefully step out of the way when they don't.

We borrow the **DIL** vocabulary from tactical communications research: *Disconnected, Intermittent, Low-bandwidth*. A DIL-aware surface is one where each of those three states has a defined experience, not an accident. We are building DIL-aware surfaces.

## Operating regime

Every surface that adopts this doctrine declares which DIL regimes it serves and how:

| Regime | What works | What degrades | What's hidden |
|---|---|---|---|
| **Connected, good link** | Everything. Tier 1 + Tier 2 + all analytics. | Nothing. | Nothing. |
| **Connected, low-bandwidth** | Tier 1 fully functional; Tier 2 loads if operator opts in. | Tier 2 features that depend on bandwidth (live decode at line rate). | Auto-load of Tier 2 (operator must opt in). |
| **Intermittent** | Tier 1 fully functional with auto-reconnect; SSE resumes from `Last-Event-ID`; Service Worker bridges tab-lifecycle events. | Tier 2 may evict during outages and reload on reconnect. | Nothing structural — gaps are visible as staleness indicators, not silent. |
| **Disconnected** | Last-known state remains visible; UI says "disconnected" honestly. | All live functions. | Nothing — the UI is candid about what it cannot do. |

This is not a hierarchy where higher tiers replace lower tiers. It's a layering where each tier *augments* the one below it without making it dependent.

## The two-tier pattern

The architectural shape that delivers the operating regime above is a two-tier surface:

- **Tier 1 — the canonical workhorse.** Server-rendered HTML over a long-lived streaming connection (SSE today; HTTP/3 server push or its successor when middlebox support catches up). Vanilla JavaScript, no framework. Owns the DOM, owns the in-memory data buffer, owns rendering. Always loads first. Always works alone.
- **Tier 2 — the optional coprocessor.** A Rust→WASM module that reads Tier 1's data structures and produces *additional* views (decoded payloads, statistical overlays, analytics widgets). Treats Tier 1 as a workhorse it cooperates with — never as a substrate it replaces or shadows. Lazy-loaded; opt-in or auto-loaded under good conditions; gracefully evicts under bad ones.

The asymmetry is structural. Tier 1 has zero knowledge of Tier 2. Tier 2 reads from Tier 1's stable interface (a small ring buffer + the focused-subscription URL + a `BroadcastChannel` for events). If Tier 2 crashes, fails to load, or never gets requested, Tier 1 was already running and keeps running. Nothing has to be torn down or re-mounted.

This is **single-island upgrade against a no-hydration substrate** — distinct from Astro/Marko-style *per-component* islands (which hydrate many small components on the client) and from Qwik-style *resumability* (which serializes framework state into HTML to skip hydration cost). Both are clever solutions to problems we don't have: we don't have a framework whose state we need to rehydrate or resume in the first place.

## Principles

Fourteen principles. None are aspirations; each is a verifiable design property. New surfaces adopting this doctrine should be reviewable against the list.

### Tier-1 / Tier-2 architecture

1. **Tier 1 is canonical; Tier 2 is a coprocessor.** Tier 1 owns the data path, the DOM, and the rendering. Tier 2 reads from Tier 1's state and produces derived views. Tier 2 never replaces a Tier 1 surface — it augments alongside.
2. **Usable on first byte.** First paint happens before any Tier 2 load decision. If Tier 2 never loads, the surface is still a useful tool — not a stub, not a placeholder, not a "feature requires JavaScript" wall.
3. **Single-island upgrade, no hydration.** Tier 2 is one explicit upgrade boundary, not a graph of dynamically-hydrated components. Tier 1 has no framework state to hydrate.
4. **Tier 2 is a single download, not a graph.** No dynamic-import waterfalls inside Tier 2; either the whole analytics module loads or none of it. Predictable for browser caching and for the operator's load-or-not decision.

### Network discipline

5. **Server filters at the edge of subscription.** The URL declares what the operator is focused on; the server narrows its upstream subscription accordingly; the stream over the wire is *already* the focused slice. Even 10 kbps carries meaningful events because there is no waste in the pipe.
6. **Bookmark = subscription = share.** The URL IS the focus. Pasting a URL into chat gives another operator the same focused view, regardless of their Tier 2 availability.
7. **Wire compression is mandatory, not optional.** Long-lived event streams use Brotli (better ratio over time via forward/back references; designed for streaming text). Short request-response endpoints use ZSTD (lower time-to-first-byte). Both are supported by browser `CompressionStream` and Rust crates.
8. **Connection continuity survives tab lifecycle.** A Service Worker owns the streaming connection; browser tabs subscribe via `BroadcastChannel`. A tab reload, bfcache restore, or brief offline window doesn't drop the stream — the SW reconnects with `Last-Event-ID` and continuity is preserved.
9. **Focus-transition speed is a feature.** Speculation Rules `prerender` on declared sibling-focus links exploits the MPA architecture the URL-as-focus discipline already produces. Tier-1-only feature, zero Tier-2 cost.

### Graceful degradation

10. **Graceful degradation in both directions.** Bad network → Tier 2 stays unloaded; Tier 1 carries on. Bad client (low memory, suspended tab, WASM crash) → Tier 2 evicts; Tier 1 carries on. The degradation surface is symmetric, never one-sided.
11. **Honest naming, not silent dead-ends.** When a feature requires Tier 2 and Tier 2 is unavailable, the UI says so explicitly (e.g., "decode requires analytics module — load now?"). Hidden features that silently do nothing are forbidden.
12. **Equivalence-by-construction where features overlap.** Features that have both a Tier 1 and Tier 2 implementation have CI-asserted identical output on canned input streams. Drift between tiers is caught at build time, not in production.

### Compute placement

13. **Compute placement is operator-controllable.** Same Rust analytics code compiles to two targets: `wasm32-unknown-unknown` (Tier 2 in the browser) and native (a `/api/compute` server endpoint). The operator decides where compute lands without code changes: pull it into the browser on a strong device; push it to the server on a degraded one.

### Surface discipline

14. **No framework in Tier 1.** Vanilla JavaScript + platform primitives only — `EventSource`, `Canvas`, `MutationObserver`, `BroadcastChannel`, `CompressionStream`, Speculation Rules. The escape hatch when Tier 1 grows complex enough to warrant fine-grained reactivity is `@preact/signals-core` (~1.5 KB) as a *library*, not a framework. Adopting a framework in Tier 1 is a doctrine violation.

## Conscious rejections

Each of these is a path the wider community has taken or is taking. They are not oversights — they are choices we made, with reasoning a future reviewer can interrogate.

- **WebTransport over HTTP/3** for the streaming path. WebTransport has lower latency than SSE in the best case but loses middlebox traversal, the `Last-Event-ID` resume primitive, and the "indistinguishable from a slow HTTP response" property that lets SSE traverse degraded networks gracefully. Re-evaluate when HTTP/3 middlebox support matures and `Last-Event-ID`-equivalent resumability is wire-level.
- **Per-component partial hydration** (Astro islands, Marko 6 auto-islands). Cleaner for content-heavy sites with isolated interactive widgets; wrong shape for a real-time-data surface where the "interactive widget" is the whole page. We use single-island upgrade instead.
- **Hydration as a model.** Tier 1 has no framework state to rehydrate. Hydration's elegance is a solution to a problem we don't have. This rejection drives the no-framework choice in Tier 1.
- **Resumability frameworks** (Qwik). Resumability is brilliant for large interactive SPAs that need framework reactivity without paying hydration cost. The framework floor cost (~30-50 KB minimum) exceeds the entire Tier 1 budget for surfaces this doctrine governs. Solves a problem we don't have, at a cost we can't afford.
- **WebGPU for tiny visualizations.** Pipeline-creation cost dominates below ~256×256 matrices; for sparklines and event-rate ribbons, WebGL/Canvas 2D wins. Re-evaluate if a surface ever genuinely renders large numerical workloads in the browser.
- **Generic Service Worker caching.** Service Workers are notorious for lifecycle bugs (`workbox` issues are legion). We use them *only* for the `EventSource`-ownership pattern that delivers tab-lifecycle continuity — not for asset caching, not for offline app shells, not for general caching strategies.
- **Frameworks in Tier 1** (React/Vue/Svelte/Qwik/Solid/etc.). Any framework's hello-world floor exceeds our Tier 1 budget. The escape hatch when vanilla JS gets unwieldy is `@preact/signals-core` as a library, not adopting a framework.

## Locked-in decisions

Three decisions where smart experts disagree, where we picked a side consciously.

### Decision 1: Brotli on streaming, ZSTD on request-response

**Choice.** Long-lived event streams (Server-Sent Events, future HTTP/3 streams) compress with Brotli at moderate level (quality 4-6). Short request-response endpoints (analytics queries, compute results) compress with ZSTD.

**Rationale.** Brotli's forward/back references compound over the lifetime of a long stream, beating gzip by ~2x and ZSTD on ratio. ZSTD's compress-and-emit-bytes-immediately profile wins on time-to-first-byte for endpoints where the operator is waiting for the answer rather than passively receiving events. Both are first-class in browser `CompressionStream`. The complexity cost of running two algorithms is small; the bandwidth/latency win on the wrong stream type is large.

**Reference.** Anders Murphy, *Why you should consider using brotli compression with SSE* (2025).

### Decision 2: SVG for semantic elements, Canvas 2D for streaming visualization

**Choice.** SVG for icons, status pills, semantic elements, anything that needs accessibility / CSS styling / per-element interaction. Canvas 2D for sparklines, event-rate ribbons, anything that animates or redraws on every tick.

**Rationale.** The crossover threshold between SVG and Canvas (quoted at 1k-10k elements) is not the load-bearing axis for our surfaces. The load-bearing axis is *redraw frequency* and *per-element-interactivity*. Streaming viz is high-frequency / no-per-element-interaction (Canvas wins decisively). Icons + pills are low-frequency / per-element-interactive (SVG wins decisively). The hybrid rule is unambiguous and each path is independently simple.

**Excluded:** WebGPU and WebGL for tiny visualizations — pipeline-creation cost dominates below ~256×256 matrices.

### Decision 3: Progressive Enhancement, with signals as the escape hatch

**Choice.** Tier 1 is built as Progressive Enhancement: server-rendered HTML + a small standalone JavaScript file that opens an `EventSource` and pokes the DOM. The escape hatch if vanilla JS ever grows unwieldy is `@preact/signals-core` (~1.5 KB) as a library — adding reactivity without adopting a framework.

**Rationale.** Progressive Enhancement is how the web worked for its first ~15 years. It got rebranded as a "movement" only because the React/Vue/Svelte ecosystem made adopting a framework feel like the default. Strip that bias and the choice is unambiguous when the dynamic surface is small: Tier 1 has at most ~5 interactive elements (focus URL input, filter toggles, pause/resume, tier toggle, share button). A framework's floor cost solves no problem we have. Resumability frameworks (Qwik) elegantly solve hydration cost — for surfaces that have framework state to hydrate, which we don't.

If a future Tier 1 grows complex enough to genuinely warrant fine-grained reactivity (8+ interactive elements with cross-dependencies), `@preact/signals-core` adds signals as a library, preserving the DOM-is-the-state model. Adopting a framework remains a doctrine violation.

## Validation against state of the art

Where the doctrine matches expert consensus, the alignment is recorded so it is read as a *choice consistent with the field* rather than a parochial invention:

- **SSE over WebSocket/WebTransport** for server→client streams — 2025-2026 consensus matches.
- **URL as state / bookmark = share** — matches hypermedia (HTMX / Hotwire / Carson Gross) and Speculation Rules' MPA-first design.
- **Tier 1 canonical, Tier 2 coprocessor** — matches the local-first-software framing: *"availability of another computer should never prevent you from working"* (Martin Kleppmann, Ink & Switch, 2019).
- **First-paint / 14 KB initcwnd budget** — still authoritative in 2026 under HTTP/3.
- **Server filters at the edge of subscription** — matches Honeycomb's high-cardinality streaming-filter discipline.
- **WASM streaming compile + single download** — matches `web.dev/loading-wasm` guidance and V8 TurboFan code-cache behavior.

## How to adopt this doctrine

When a new bandwidth-constrained surface enters design:

1. Read this doc + [`flashlight.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/flashlight.md) as the worked first instance.
2. Declare which DIL regimes the surface targets and what each looks like.
3. Identify the Tier 1 surface set (what works without Tier 2) and the Tier 2 surface set (what augments).
4. Check the 14 principles. Any deviation must be a *named* deviation with rationale recorded in the surface's own design doc — not silent drift.
5. Check the conscious-rejections list. If a rejected pattern is being considered, the rationale section must explicitly argue why this surface is the exception.
6. Reuse `panoscope-core` (or its successor shared crate) for substrate-layer concerns; reuse `flashlight-analytics` (or its successor dual-target crate) for compute that should be relocatable between Tier 2 and a server endpoint.

A surface that adopts this doctrine should land its design doc with a one-sentence statement: *"This surface adopts [`minimalism-under-network-constraints.md`](minimalism-under-network-constraints.md); deviations are noted below."*

## Why this is a doctrine, not a one-off

The first instance is flashlight. The shape applies cleanly to at least four other surfaces already in our plan:

- **goat-client GUI** (Block 76) — desktop + mobile clients onboarding peers on degraded networks.
- **snitch-app** (Block 77) — fleet visibility surface running on mobile under battery / bandwidth constraints.
- **partner-facing dashboards** (Block 84 partner peering portal; future Block 60 moon-pod observer) — partners we don't get to specify the network for.
- **nova-lan** (Block 87) — LAN-only instance with no WAN at all; DIL = always "Disconnected from the outside world."
- **rapid-bringup surfaces** (Block 68) — bringup operator on a trickle of bandwidth bootstrapping a new site.

Each of these benefits from the same 14 principles. Writing the doctrine once and applying it five times is the cost-effective shape.

## What this doctrine deliberately does NOT cover

This doctrine handles **real-time inspection of small structured events** under DIL conditions. Other domains have *different* engineering concerns that would be hidden if we let readers force-fit them into the same frame. The boundary is load-bearing — naming it explicitly prevents a future contributor from applying this doctrine to a problem it doesn't fit.

| Out-of-scope domain | Why this doctrine doesn't fit | Where to look instead |
|---|---|---|
| **Bulk container image distribution** | Content-addressing, cache tiers, cosign verification — different shape. | `docs/design/oci-goat-substrate.md` + ADR 0838 (Block 75). |
| **Streaming media (video, audio)** | HLS/DASH adaptive streaming, codec-aware bitrate ladders, SFU patterns. Video bytes do not ride on the same fabric as structured events. | `docs/design/video-fabric.md` (Block 35). |
| **Mission-data blob exchange** | Trust-domain crossing, data-conditioning checkpoint, partner-namespace governance. | [`docs/design/mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md) + [ADR 0821](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md) (Block 21). |
| **Server-internal protocols** (Zenoh fabric, Spock replication, wg-cp0) | Throughput / consistency / partition tolerance concerns; no human in the loop watching directly. | The respective fabric design docs. Governed by [ADR 0863](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0863-resilient-end-node-design-philosophy.md)'s Out of scope. |
| **Bulk historical sensor-data retrieval** | Query / range / paging patterns over archived NDJSON; backend-style concerns. | ⚠️ **GAP** — see backlog → bulk-historical-sensor-data-retrieval-doctrine. |
| **Static document / briefing / image delivery under DIL** | Progressive rendering, chunked transfer, content-addressing for arbitrary documents (PDFs, briefing decks, images) — not pre-baked container images. | ⚠️ **GAP** — `brief.nova.*` and `dataflows.nova.*` operate without doctrine today. See backlog → progressive-bulk-asset-delivery-under-dil. |

The two ⚠️ rows are real gaps. The other rows are companion doctrines that already exist for adjacent concerns; this doctrine and those compose.

A surface that *needs* one of the out-of-scope behaviors should NOT extend this doctrine to cover it. The right move is either (a) apply the companion doctrine listed above, or (b) for the two gaps, surface the need for a new doctrine via the backlog entry — don't invent local discipline that future maintainers can't find.

## Parent philosophy

This doctrine is the *web instantiation* of the broader [ADR 0863 — Resilient end-node design philosophy](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0863-resilient-end-node-design-philosophy.md). Roughly half the principles above (the seven that generalize beyond web — canonical workhorse + coprocessor, usable-on-first-byte, declarative state in invocation artifact, graceful degradation in both directions, operator-controllable compute placement, honest naming, DIL operating regime framing) inherit from the parent philosophy. The other half (compression algorithms, SVG vs Canvas, Progressive Enhancement, web platform primitives, the 14 KB initcwnd budget, Speculation Rules) are web-tactical specializations that don't generalize.

Future non-web surfaces (goat-client GUI Block 76; snitch-app Block 77) will write *sibling* doctrines that share the parent and add their own platform-tactical specializations.

## Living document

This doctrine evolves as we learn what works. Changes that materially alter a principle, a conscious rejection, or a locked-in decision land via PR with a rationale; tightening / clarifying language can land without ceremony. The first material revision target is when flashlight ships and we learn what we got wrong.
