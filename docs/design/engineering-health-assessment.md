# Foundational Engineering Health Self-Assessment

A severable framework for measuring whether the underlying technical foundation of an organization is sound, independent of strategic fit. Designed for large organizations with mixed build / buy / contractor / vendor footprints.

---

## Why this lives in the goat repo

Goat itself is small and mostly-build, with some buy. The framework below is sized for a much larger and more mixed environment than goat alone. It is here anyway, deliberately, for two reasons:

1. **Goat is foundational to a larger ecosystem** — the orgs that depend on goat-class infrastructure operate inside large mixed footprints, integrating contractor builds, vendor data services, GOTS, and sustainment-mode legacy. Goat's value proposition (sovereign, queryable-by-default, anti-platform) is meaningful only if those orgs can measure whether their foundation is actually sound. This framework is how they do it.
2. **Adopters will need it on day one.** Anyone picking goat up — industrial / OT, disaster response, energy, autonomy fleets, tactical — is doing it inside a larger mixed footprint. Shipping the measurement framework alongside the substrate is part of what makes adoption serious.

The framework is severable. It can be lifted out of this repo and used by an organization that has nothing to do with goat. The body below is written that way on purpose. Goat-specific application appears as a worked example at the end ([§ Goat as worked example](#goat-as-worked-example)) and as inline pointers to existing artifacts where they help.

This framework deliberately does not assess strategic fit, requirements alignment, or whether the system is solving the right problem. Those questions are real and important, and they belong in a different mechanism. Loading them onto these five numbers corrupts all five. See [§ What this framework does not do](#what-this-framework-does-not-do).

---

## The Ownership Principle

Before any measurement, one rule.

**The accountable entity owns these metrics. Vendors and contractors do not.**

A vendor can provide telemetry. A contractor can run the on-call rotation. Neither absolves the entity of measuring, interpreting, and acting on these numbers. An entity that has outsourced its own self-knowledge is an entity in name only.

This applies regardless of posture:

- **Build** — you own the metric and the implementation.
- **Buy** — you own the metric; the vendor is a measured component.
- **Maintain** — you own the metric on inherited systems even if you didn't build them.
- **Move beyond** — you own the metric on the way out. Sunset is an engineering activity, not the absence of one.

Operationally: every service in scope has a named human inside the entity who owns each of the five numbers, distinct from whoever operates the service day to day.

This principle is the enforcement mechanism behind the [Data Services Provider Charter](../vendor-templates/data-services-provider-charter.md). A vendor that cannot expose the telemetry the entity needs to score these metrics is not a candidate for ingestion.

---

## Scope

A service is in scope if any of the following are true:

1. The entity depends on it for mission delivery.
2. The entity pays for it, directly or via contract.
3. The entity is the consumer of record for its outputs.

Hosting model, vendor identity, classification level, and contracting vehicle do not change scope. If you depend on it, you measure it.

---

## The Five Metrics — Operationalized

### 1. Latency

**Measure**

- p50, p95, p99, p99.9 for each user-facing operation.
- End-to-end (user action to user-visible result) and per-hop component latency.
- Cold-path and warm-path separately where applicable.
- Cross-domain transit (cross-enclave, cross-classification, cross-region) as its own dimension.

**Collect**

- Synthetic probes from a location representative of the user, running continuously.
- Real user monitoring where applicable.
- Component telemetry from each tier (load balancer, application, database, external dependency).
- For vendor-operated components: contractual requirement to expose latency telemetry. If unavailable, the entity instruments around the boundary.

**Bands** (starting points; tune per service)

- **Green:** p99 within design budget.
- **Yellow:** p99 within 1.5× design budget, or p50 trending up four weeks running.
- **Red:** p99 exceeding 1.5× design budget.

**Mixed-footprint rule:** "We can't measure it" is not an exit. If a vendor will not expose telemetry, the entity probes from outside.

**Motifs from industry**

- **Amazon's 100ms / 1% rule.** Internal studies linked 100ms of added latency to roughly 1% of revenue loss. Latency became a dollar number, not a vibe. Adopt the motif: convert the latency budget into a unit your leadership cares about — revenue, mission readiness, mean time to decision — and post it next to the SLO.
- **Google's "tail at scale."** Averages lie; tails kill. Engineers explicitly track p99 and p99.9, and use techniques like hedged requests (issue to two replicas, take the first reply) to bound tail latency. Adopt the motif: never report latency as a single number.
- **Discord's Go-to-Rust rewrite.** A hot-path service was rewritten when Go's garbage collector showed up as periodic p99 spikes. The trigger was tail latency, not throughput. Adopt the motif: tail-latency anomalies are a legitimate trigger for re-platforming.
- **Cloudflare's edge-side measurement.** Probes from the user's actual network path, not from inside the provider's datacenter. Adopt the motif: never let the vendor mark its own homework on where its edges sit.

---

### 2. Engineering Velocity Mix

**Measure**

- Total engineering hours per period — in-house + contractor + vendor-billed.
- Hours classified as new capability work.
- Hours classified as maintenance, sustainment, defect fix, or operational toil.
- Ratio: new-work hours / total hours.
- Trend across at least four quarters.

**Collect**

- Time tracking against a shared taxonomy: new / maintenance / toil / overhead.
- Contractor and vendor deliverables report against the same taxonomy as a contract requirement.
- Quarterly adjudication by the entity's owner. Vendor-reported allocations get spot-audited.

**Bands**

- **Green:** 40%+ on new work, stable or rising.
- **Yellow:** 25–40% on new work, or any direction of drift over two quarters.
- **Red:** under 25% on new work, or four-quarter declining trend.

**Mixed-footprint rule:** if a contract is structured so the entity cannot see the new/maintenance split, that is a contracting defect, not a measurement gap. Fix on the next option year.

**Motifs from industry**

- **Google SRE's 50% toil cap.** SRE teams are not allowed to spend more than 50% of their time on toil. When they do, work flows back to the development team that produced it. The cap is enforced organizationally, not aspirationally. Adopt the motif: a hard ceiling on maintenance, with a defined consequence when it is breached.
- **DORA's four metrics.** Deployment frequency, lead time for changes, change failure rate, MTTR. Originally Google research, now industry standard. They turn velocity from a feeling into four numbers any team can produce. Adopt the motif: a small, fixed set of velocity numbers reported the same way across every team.
- **Stripe's investment in deploy infrastructure.** Heavy internal tooling investment specifically so engineers ship more new work per hour. Adopt the motif: treat developer platform engineering as a velocity multiplier, and budget it explicitly against the new-work ratio.
- **Spotify squad health checks.** Lightweight self-assessments where teams flag whether they're drowning in maintenance. Adopt the motif: bottom-up signal complements top-down time-tracking — engineers know before the spreadsheet does.

---

### 3. Uptime and SLA Conformance

**Measure**

- Measured availability, independent of vendor self-report.
- SLA met / SLA missed events per period.
- **Functional conformance:** percentage of expected behaviors working as specified — not just "is the endpoint reachable."
- MTTD and MTTR for incidents.
- Incidents caught by the entity vs. caught by vendor self-report vs. caught by users.

**Collect**

- Independent synthetic monitoring from outside the vendor's environment. Non-negotiable.
- Functional probes that exercise representative end-to-end workflows, not just liveness.
- Incident log maintained by the entity. Vendor-reported incidents reconciled against entity-observed outages.
- Where vendor and entity numbers diverge, the entity's number is the number of record.

**Bands**

- **Green:** meets contractual / design SLA, functional conformance above 99% of probed behaviors.
- **Yellow:** meets availability SLA but functional conformance below 99%, or MTTD/MTTR trending up.
- **Red:** misses availability SLA, or users detect outages before the entity does.

**Mixed-footprint rule:** trust-but-verify is the floor. The entity always operates an independent measurement layer. Vendor-reported 99.9% means nothing without corroboration.

**Motifs from industry**

- **Google SRE's error budgets.** A service with a 99.9% SLO has 0.1% of "allowed" downtime per period. That budget is spendable — burn it on shipping risk, or save it. When it's gone, you stop shipping new features until you've earned it back. Adopt the motif: convert reliability into a tradeable currency between development and operations.
- **Netflix's Chaos Monkey and the Simian Army.** Inject failures into production continuously to verify the system survives them. The premise: an outage you haven't simulated is an outage you don't understand. Adopt the motif: scheduled, deliberate breakage as a verification mechanism.
- **Cloudflare and GitLab post-mortem transparency.** Public, detailed RCAs published shortly after incidents. The forcing function is reputational. Adopt the motif (internal version): mandatory post-mortems with named technical causes, distributed widely enough that hiding them is impossible.
- **AWS service-level status pages.** Independent status per service, not a single rolled-up indicator. Adopt the motif: granularity prevents a vendor from masking a partial outage behind aggregate green.

---

### 4. Carrying Cost

**Measure**

- FTE-equivalents required to keep each service running — in-house + contractor + vendor-allocated.
- On-call burden: pages per week, after-hours interrupts, weekend incidents.
- Toil hours: repetitive operational work that produces no durable improvement.
- Service count: number of distinct foundational services the entity is on the hook for.
- Complexity proxy: integrations, dependencies, and unique runtime environments.
- Per-capability denominator: cost normalized to a unit of mission output where definable.

**Collect**

- Staffing rolls that include vendor headcount equivalents and contractor allocations.
- Paging and incident management system data for on-call load.
- A toil log maintained per service team, reviewed quarterly.
- Service inventory maintained by the entity, not by any single vendor.

**Bands**

- **Green:** flat or declining FTE-per-service across four quarters; on-call under threshold; toil under 25% of ops hours.
- **Yellow:** FTE-per-service rising under 10% per year, or on-call/toil trending up.
- **Red:** FTE-per-service rising over 10% per year, on-call producing attrition, or toil over 50% of ops hours.

**Mixed-footprint rule:** a vendor's headcount on your problem is your headcount on your problem. Carrying cost includes everyone working on the system regardless of badge color.

**Motifs from industry**

- **Netflix's "paved road."** A small, opinionated internal stack — Spinnaker for deploys, a defined service template, a known runtime — that absorbs the operational burden so product teams don't carry it. Going off-road is allowed but expensive. Adopt the motif: a few well-paved paths beat infinite optionality, and runtime sprawl is the leading indicator of carrying-cost decay.
- **Google's platform teams.** Specialized teams that absorb toil from product teams. If a platform team's five hours saves fifty across the company, it's a win — and the math is tracked. Adopt the motif: leverage is the unit of platform value, and it should be measurable.
- **Shopify's pillars.** Each new service has to justify the carrying cost of its existence. The default is consolidation, not proliferation. Adopt the motif: a new service is a permanent staffing commitment, and the bar for creating one is set accordingly.
- **Stripe's ruthless internal tooling.** Heavy investment in tools that reduce the team-to-service ratio. The implicit metric: how many services can one engineer responsibly own? Adopt the motif: the team-to-service ratio is a first-class number worth optimizing.

---

### 5. Data Leverage

The ability to get value out of your own data. This is the highest-level metric of the five — it sits on top of access, format, tooling, and the loop from insight to action.

**What it captures**

- **Access:** can the entity actually retrieve its own data? (Vendor lock-in, proprietary formats, custody, classification gating.)
- **Utility:** is it in a form you can query and join across sources?
- **Insight:** can you derive useful things from it?
- **Action:** do insights flow back into operations or product?

A failure at any layer collapses the whole metric. A perfectly accessible data lake that nobody queries is the same outcome as a vendor system that won't export.

**Measure**

- Time-to-answer for a representative new operational question — measured in hours, days, or weeks.
- Extraction posture per data source: full / throttled / none. Percentage of operationally-relevant sources at "full."
- Cross-source joinability: percentage of relevant sources that can be combined in a single analytic environment.
- Insight-to-action cycle time: from "we noticed something" to "we changed something because of it."
- Decision support coverage: number of significant decisions in the period that were quantitatively backed by entity-controlled analysis, versus anecdote or vendor-supplied reports.

**Collect**

- A data source inventory maintained by the entity, with extraction posture per source.
- A standing "data drill" — every quarter, pose a fresh question and time the answer.
- A decision log that records whether internal data was used and how.
- An audit trail of vendor data export requests: how many made, how many fulfilled, how long they took.

**Bands**

- **Green:** any operationally-relevant question can be answered from entity-controlled data within days; cross-source joins are routine; insight-to-action loops are a normal part of operations.
- **Yellow:** some sources locked behind vendors or in incompatible formats; common questions take weeks; insights occasionally drive action.
- **Red:** data is largely held by vendors and not extractable on demand; analytics depend on vendor-supplied reports; the insight-to-action loop is rare or absent.

**Mixed-footprint rule:** if a vendor will not return your data to you in usable form on demand, that is a procurement defect, not a feature request. Data export, format documentation, and bulk extraction are contracting requirements. The exit path from any vendor system runs through this metric. The [Data Services Provider Charter](../vendor-templates/data-services-provider-charter.md) is the contracting expression of this rule.

**Motifs from industry**

- **Netflix's content decisions.** Programming and recommendation choices are conditioned on viewing data the company controls end-to-end. The data isn't a reporting byproduct — it's the input to the next decision. Adopt the motif: data is an operating input, not a quarterly artifact.
- **Airbnb's Knowledge Repo.** An internal system for sharing reproducible analyses across the company, so insight is durable and reusable rather than locked in one analyst's notebook. Adopt the motif: insights are organizational assets and need their own infrastructure.
- **Stripe's Sigma.** Lets customers run SQL directly against their own Stripe data. Stripe productized externally what most vendors bury behind dashboards. Adopt the motif: the right test of data access is "can I run an arbitrary query," not "is there a dashboard."
- **Uber's Michelangelo.** End-to-end internal ML platform that compresses the path from data to deployed model. The motif is about closing the insight-to-action loop fast enough that the loop itself becomes a competitive surface.
- **Capital One's cloud migration.** A core driver was breaking out of legacy data silos that prevented the company from using its own data. Adopt the motif: an inability to leverage your data is a legitimate strategic justification for re-platforming.
- **Spotify Wrapped.** Internal listening data became a viral product feature. The data closed the loop all the way from instrumentation to user-visible value. Adopt the motif: the highest expression of data leverage is when your own data shows up in the experience you deliver.

---

## The Scorecard

Per service, per quarter:

| Metric | Value | Band | Trend | Owner (entity-side) |
|---|---|---|---|---|
| Latency (p99 + tail) | | G / Y / R | ↑ → ↓ | |
| Velocity mix | | G / Y / R | ↑ → ↓ | |
| Uptime / conformance | | G / Y / R | ↑ → ↓ | |
| Carrying cost | | G / Y / R | ↑ → ↓ | |
| Data leverage | | G / Y / R | ↑ → ↓ | |

Roll up across the portfolio. One red on a service is a review item. Two reds is a portfolio-level escalation.

---

## Cadence

- **Continuous:** latency probes, uptime monitoring, paging telemetry, data export audit log.
- **Monthly:** metric collection, owner review.
- **Quarterly:** portfolio scorecard, data drill, posture review (build / buy / maintain / move beyond).
- **Annual:** contract and SLA renegotiation informed by the prior year's data, including data export performance.

---

## Posture Decisions Driven by the Metrics

The five numbers feed the lifecycle posture of each service:

- **Build** is justified when the entity sustains green metrics with in-house effort and the capability is differentiating.
- **Buy** is justified when a vendor produces green metrics at lower carrying cost than building — *and* the data leverage metric is green, meaning the entity can still get its data out.
- **Maintain** is justified when metrics are green and the capability is not differentiating enough to invest further.
- **Move beyond** — sunset, replace, migrate — is the correct answer when carrying cost rises, velocity mix collapses toward maintenance, data leverage is red, or foundational health cannot be restored at acceptable cost.

Sunset is a first-class option. A foundational engineering function that cannot leave things behind will eventually drown in its own carrying cost.

A note on the data leverage metric specifically: a vendor system that scores green on the first four but red on the fifth is a trap. It works today, it's affordable today, and it will be impossible to leave when you need to.

---

## What This Framework Does Not Do

These five metrics deliberately do not assess strategic fit, requirements alignment, customer satisfaction with capability, or whether the system is solving the right problem. Those questions are real and important, and they require their own management mechanism. Loading them onto these five numbers corrupts all five.

A clean scorecard on a system solving the wrong problem is still a system solving the wrong problem. This framework will not catch that. It is not designed to.

---

## Adoption Checklist

Use this to stand up the assessment from a cold start:

1. Define the service inventory. Every service in scope, with a named entity-side owner per metric.
2. Stand up independent measurement. Synthetic probes for latency and uptime that do not depend on any vendor's cooperation.
3. Publish the time-tracking taxonomy. Make it a contractual reporting requirement on every active vendor and contractor instrument.
4. Build the toil log per team. Review quarterly. Treat it as a leading indicator of carrying-cost decay.
5. Build the data source inventory and assign an extraction posture to each. Treat any "none" as an open contracting issue.
6. Run the first quarterly scorecard and the first data drill with whatever data you have. Subsequent quarters fill the gaps.
7. Tie posture decisions (build / buy / maintain / move beyond) to scorecard trends, not to anecdote.
8. Reconcile vendor self-reports against entity-observed reality every cycle. Where they diverge, the entity's number wins.

---

## Goat as worked example

Goat is small and mostly-build today. The framework's full power is for the larger mixed-footprint operating environment goat sits inside, but goat scoring itself against these five numbers does three things: validates that the framework is operationally feasible at small scale, surfaces our own gaps, and gives adopters a real reference instance.

This section names the goat-side artifacts that already exist for each metric and what is missing. It is not the scorecard itself — that's a recurring artifact, see [§ Cadence](#cadence). It's the wiring map.

| Metric | What exists | What's missing | Owner-equivalent today |
|---|---|---|---|
| **Latency** | NTP-health daemon ([`ops/time-hygiene/`](https://github.com/usareur-af/goatcore/tree/main/ops/time-hygiene)), Prometheus + alert rules ([`ops/monitoring/`](https://github.com/usareur-af/goatcore/tree/main/ops/monitoring)), per-site OpenTelemetry collector + OpenObserve (Block 27) | No design-budget published per user-facing operation; no continuous synthetic probe from a representative-user network path; tail-latency motif (p99.9 + hedged-request pattern) not yet in use | Distributed across Block 17 / 18 / 27 owners; no single named owner per service |
| **Velocity mix** | Implementation-plan blocks distinguish new-capability work (e.g., Block 20 phoenix, Block 27 wide events) from sustainment (e.g., Block 6D OS migration, Block 22 silent control plane) | No time-tracking taxonomy; no quarterly velocity-mix number; no contractor / vendor reporting against a shared taxonomy | None — gap |
| **Uptime / conformance** | `docs/project/validation-state.md`, soak-testing discipline ([ADR 1008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1008-soak-testing-discipline.md)), findings register (`docs/findings/`), Wave 3 §3.1 canonical 72h soak, isitup status page | No quarterly portfolio rollup; no MTTD / MTTR tracking against contractual SLA (we don't have customers with SLAs yet, but adopters will); no functional-conformance probe distinct from liveness | Validation-state tracker is owned per entry; rollup is unowned |
| **Carrying cost** | Cloud-env-lifecycle tracker (`docs/operations/cloud-env-lifecycle.md`), service inventory implicit in [`ops/serve/services.yaml`](https://github.com/usareur-af/goatcore/blob/main/ops/serve/services.yaml), archival pattern (`emplace`/`explain`/`efforts` archived 2026-04-25) | No FTE-per-service number; no toil log; no on-call burden tracking (no on-call rotation yet); no team-to-service ratio metric | None — gap |
| **Data leverage** | Queryable-by-default discipline ([`docs/design/ai-rapid-adaptation.md`](ai-rapid-adaptation.md)), data dictionary ([`docs/design/data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md)), lineage materialized on RocksDB ([`docs/design/lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md)), Vendor Data Services Provider Charter ([`docs/vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md)) | No quarterly data drill; no time-to-answer benchmark; no data-source extraction-posture inventory; no decision log | The discipline is owned by Block 23; the *measurement* of leverage is unowned |

**The honest read.** Goat scores green on data-leverage discipline (the design exists and is opinionated) but has no operational measurement loop closed for any of the five metrics. Stand-up is what [§ Tracking](#tracking) below sequences.

The existing `tech-strategy.md` Report Card is a one-shot self-assessment with letter grades against capability requirements. It is not the same artifact as this framework's scorecard. The Report Card stays as the historical anchor and as the *capability* assessment; this framework is the *operating-health* assessment, recurring quarterly, against the five numbers above.

---

## Tracking

Stand-up of the goat-side scorecard is tracked in `docs/project/implementation-plan.md` Block 32.

Publishing the framework as a goat-external artifact (severable, ecosystem-shaped, manifesto-adjacent) is tracked under Block 29B (manifesto series) as a candidate fifth essay. The framework is operationally heavier than the four current manifesto essays, so it ships as a `docs/design/` doc first and a derivative manifesto piece second, not the other way around.

---

## Cross-references

- `tech-strategy.md` — governs *what we pick* (Decision Framework, §Engineering Principles — Earned Complexity). This framework governs *how we measure ongoing health* of what we picked. The two compose; neither replaces the other.
- [`vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md) — the contracting expression of the Ownership Principle and the Data Leverage metric. The charter has teeth because this framework gives those teeth a measurement system.
- `project/oss-strategy.md` — the framework is one of the receipts the project ships outward. Quarterly published scorecards are unusual in this category.
- `project/validation-state.md` — the operational artifact closest to a scorecard goat already maintains. Uptime / conformance evidence flows in here today.
- [`adr/1008-soak-testing-discipline.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1008-soak-testing-discipline.md) — the soak driver pattern is one of the ways uptime / conformance evidence gets generated.
- [`adr/1011-findings-register.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1011-findings-register.md) — the findings register is where vendor / external-system gotchas land; many of those are the "things you didn't know you'd be measuring around" that the mixed-footprint rules anticipate.
