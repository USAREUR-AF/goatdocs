# Partner Reference Architecture (PRA) — minimal Zenoh-on-ZTOL recipe

> **Scope: a nation's own environment is the operational path.** Operationally, each nation runs its own environment and shares only by release across boundary nodes that federate the environments ([ADR 1157](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1157-cross-sovereign-federation-edge-terminated.md), [ADR 1208](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1208-sovereign-environments-release-namespaces-and-grant-encryption.md)). This recipe is a minimal stack for such an environment. Tier-0 below is the moon pod, a learning tool for the exercise environment, not the operational path.


| Field | Value |
|---|---|
| Status | Draft (Phase 2D-late / Phase 3 commitment); recommendation, not requirement |
| ADR anchor | [`../adr/0821-mission-partner-sharing-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md) §"Partner Reference Architecture" |
| Companions | [`mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md), [`moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md), [`goat-moon-pod.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/goat-moon-pod.md), [`../partner-templates/data-sharing-charter.md`](../partner-templates/data-sharing-charter.md) |

## What this is

A **recommended-not-required** minimal Zenoh-on-ZTOL stack a mission partner can stand up in days to interop cleanly with **GOAT-Net** (the project's externally-facing data backbone — the substrate name goat realizes). The PRA is deliberately stripped of everything in our stack that exists for *our* reasons (active-active multi-site, island-mode-by-construction, paired pgBackRest, three-tier NTP, phoenix-native rebuild discipline, FIPS PQC boundary node). Partners adopting the PRA get a clean interop starting point; partners with a more elaborate stack adopt as little or as much as they want; partners with no fabric infrastructure get a working baseline.

## Tier-0 partner integration (added 2026-05-04)

The PRA presumes a partner with engineering capacity to stand up zenohd + WireGuard + an OIDC IdP + an audit sink. Many plausible mission partners do not have that capacity in any reasonable timeframe.

For those partners, **Tier-0** is a turnkey pattern: the partner runs a `goat-moon-pod` — a containerized appliance that bundles all six required pieces and deploys in 24 hours by a non-engineer. The contract any moon-pod must meet is at [`moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md) (the seven requirements). The architectural shape is at [`goat-moon-pod.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/goat-moon-pod.md). Our reference implementation is at `moon-pod` (separate repo, Apache 2.0 — private during MVP, public at GA, per [ADR 0223](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0223-goat-moon-pod-repo-containment.md)).

Vendor moon-pods are explicitly invited; per-vendor cookbooks live at `../integrations/moon-pods/`. Builder guide for vendors at [`goat-moon-pod-builder-guide.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/goat-moon-pod-builder-guide.md).

**The PRA is Tier-0-aligned.** Both paths conform to the same seven-requirement contract; the PRA is a partner-side-deeper-engagement variant, the moon-pod is the easy-button variant. A partner can transition between them without re-onboarding (requirement 7 — reversibility).

## Maturity caveat

GOAT-Net is at proof-of-concept stage. We are in uncharted territory — sovereign tactical-edge data backbones at this shape and scope do not have established operational precedent at theater scale. The direction is sound and anchored in mainstream distributed-systems patterns; specific scaling, performance, and operational characteristics will be discovered, not asserted. A viable scaling plan exists (ADR [`../adr/0216-goat-net-federation-and-site-planes.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0216-goat-net-federation-and-site-planes.md)) and becomes operative *if* GOAT-Net earns it through the early phases. Partners adopting the PRA today are entering an early-phase relationship — the recipe is sound, but specific operational scale will be measured rather than promised.

Critical framing: **a partner does not need to look like us** to share data with us. They need to be standards-compliant on the four facets (security, functionality, performance, reciprocity) declared in ADR [`0821`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md). The PRA is one *concrete* way to achieve standards compliance — there are others, and partners are free to take them.

## Architecture sketch

```
┌─────────────────────────────────────────────────────────────────────────┐
│   Partner site (PRA — minimal recommended stack)                        │
│                                                                         │
│   Operators ─▶ OIDC IdP (Dex / Kanidm / Zitadel / Keycloak / Ory)       │
│       │                  │                                              │
│       │                  │ (federation via OIDC discovery)              │
│       ▼                  │                                              │
│   Partner UI ──────▶ Zenoh router ──── WireGuard ZTOL ───▶ to GOAT-Net  │
│   / agents           (single node)     (commercial internet)            │
│       │                  │                                              │
│       │                  ▼                                              │
│       │           Audit sink (Loki / journald / partner SIEM, 90d)      │
│       │                                                                 │
│       └──────────────▶ Health endpoint (health/partner/<partner>/…)     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ release/<partner>/…
                                    │ release/goat/… (reciprocal)
                                    │
                                    ▼
                          GOAT-Net (goat-side)
```

Eight components. Single-node. No replication. Stand up in days.

## The eight pieces

### 1. One Zenoh router (single node)

Run **`zenohd`** as a single instance. No multi-master, no Spock, no active-active. Joins our fabric over WireGuard via the GOAT-Net-provided endpoint configuration in the partner's signed charter (Appendix B).

Recommended image: stock `eclipse/zenoh` (upstream) or build-from-source per ADR [`../adr/0708-build-zenoh-from-source.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0708-build-zenoh-from-source.md) if the partner wants supply-chain ownership. Either works — wire protocol compatibility is the contract, not a specific image.

### 2. WireGuard ZTOL over commercial internet

WireGuard tunnel from the partner's site to one or more GOAT-Net-side relay endpoints. **No MPLS. No fiat-government wires. No SCS expected.** Commercial internet is the assumed transport.

The PRA deliberately commits to commercial internet because (a) most partners can stand up commercial internet faster than fiat/MPLS, (b) WireGuard's properties (silent control plane, sovereign keys, no public-side fingerprint per ADRs [`0313`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0313-silent-control-plane-outer-wg-wrap.md) / [`0314`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0314-no-public-dns-for-control-plane.md)) hold the same way over commercial transport, and (c) performance expectations are calibrated to commercial internet realities (see ADR 0821 §3c).

If a partner has IPsec or a different ZTOL technology already in production, that is acceptable — what matters is that the wire-protocol path between the partner's Zenoh router and our fabric is encrypted, sovereign-keyed, and silent at the network boundary.

### 3. One OIDC IdP

Any standards-compliant OIDC provider with a discovery endpoint we can reach. Common choices:

- **Dex** — minimal CNCF-graduated.
- **Kanidm** — Rust-native, what we use for some of our roles.
- **Zitadel** — Go-native, multi-tenant.
- **Keycloak** — most-deployed in DoD / coalition contexts.
- **Ory** — same stack as GOAT-Net-side (ADR [`../adr/0411-ory-idp-mvp.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0411-ory-idp-mvp.md)).

The partner runs whichever they're comfortable with (or already operate). We accept identity assertions for partner end-users within the partner's `release/<partner>/` namespace scope only.

End-user identity assurance: NIST SP 800-63 IAL2 / AAL2 or above. The PRA doesn't prescribe which authenticators (FIDO2, certificates, MFA) — only the assurance level.

### 4. TLS 1.3 on non-WireGuard hops

Any partner-side hop that touches `release/<partner>/...` data outside the WireGuard tunnel uses TLS 1.3 minimum. No plaintext.

### 5. Release-namespace discipline

Mirroring our convention:

- **Outbound (partner → us):** partner publishes releasable topics under `release/<partner>/...`. Default-deny baseline at the partner's router; explicit allowlist for what crosses.
- **Inbound (us → partner):** partner subscribes to `release/goat/...` for topics we expose. Same shape from our side.
- **Schema declaration applies.** Released topics carry `attest/schema/<topic>` (or `attest/schema-declaration/<topic>` for binary) — the partner's data-dictionary discipline mirrors ours per [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md).

The partner's allowlist + namespace conventions are typically maintained in the partner's own configuration management (Ansible, Terraform, whatever they use). We don't push configuration to the partner; we accept what they expose at the boundary.

### 6. One audit sink (90d-capable)

Anything that can retain access logs for 90 days minimum:

- **Loki + Grafana** — common open-source choice.
- **journald** with retention configured.
- **Partner's existing SIEM** (Splunk, Elastic, etc.).
- **OpenSearch + dashboards.**

What matters is the retention duration and that the audit covers `release/<partner>/...` access events — not that the format matches ours. **We do not require partners to ship audit logs to us by default;** symmetric audit federation is a separate negotiation per partnership.

### 7. Health endpoint

Partner publishes liveness at `health/partner/<partner>/...` so we have a coarse signal that the partner side is running. Standard structured-health schema; payload is small (timestamp, version, last-emission-counter). Lets our observability stack flag a partner-side outage without requiring us to monitor the partner's internals.

We do not push monitoring agents to the partner. Health is partner-emit, our-subscribe.

### 8. Optional — phoenix-native discipline

Recommended for the partner's own resilience but **not required** for interop. A partner running ephemeral / rebuild-from-scratch infrastructure is more resilient under their own threats; their fabric-interop posture is unaffected by which choice they make.

If a partner adopts phoenix-native, ADR [`../adr/0208-phoenix-native-peer-discipline.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0208-phoenix-native-peer-discipline.md) is a reasonable starting point. We don't require following our specific patterns.

## What the PRA explicitly omits

These exist in our stack for *our* reasons (sovereignty under attack, scope envelope, multi-site continuity) — they are *not* required for partner interop. A partner can adopt them if they have reasons of their own; the PRA doesn't.

- **Active-active multi-site management plane** (ADR [`../adr/0204-multi-site-active-active.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0204-multi-site-active-active.md)) — single-node is fine for partner interop.
- **Spock multi-master replication** (ADR [`../adr/0801-postgresql-spock-multi-master.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0801-postgresql-spock-multi-master.md)) — partner can run any database, replicated or not, as long as their audit retention is met.
- **Paired pgBackRest stanzas** (ADR [`../adr/0802-pgbackrest-paired-stanzas.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0802-pgbackrest-paired-stanzas.md)) — partner backup is partner's choice.
- **Three-tier NTP** ([`ntp-strategy.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/ntp-strategy.md)) — partner uses their existing time discipline; standard NTP / NTS at the partner side is sufficient.
- **FIPS 140-3 + PQ boundary node** (ADR [`../adr/0601-fips-pqc-boundary-node.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0601-fips-pqc-boundary-node.md)) — required only for cross-classification work; not in scope at unclass.
- **Sovereign per-site PKI** (ADR `../adr/0400-sovereign-per-site-pki.md`) — partner uses their own PKI.
- **Offline CA on YubiKey PIV** (ADR `../adr/0406-offline-ca-yubikey-piv.md`) — partner key custody is their choice.
- **Specific hardware** — partner runs whatever hardware works for them.
- **LUKS + NBDE** for data-at-rest (ADR [`../adr/0604-luks-data-at-rest.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0604-luks-data-at-rest.md)) — partner's own DAR posture.
- **CGNAT-aware validation** (ADR [`../adr/1003-cgnat-aware-validation-default.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1003-cgnat-aware-validation-default.md)) — internal validation discipline only.

## Performance expectations (commercial-internet-realistic)

What "working" looks like over commercial internet:

- **Round-trip latency** to mutual relay: typical < 500ms; episodic spikes acceptable.
- **Sustainable throughput**: typed per partnership (declared in charter Appendix A); not absolute. A partnership focused on low-rate position reports might commit to 50 Kbps; a partnership covering wide-area video might commit to 50 Mbps.
- **Monthly availability**: ≥ 99% (≈7h downtime/month). Calibrated to commercial internet.

These are **expectations**, not SLAs. Hard SLAs require contractual basis the charter does not provide.

## Implementation surface (partner side)

The partner's deployment artifacts. What we provide as templates:

| Path (in partner's repo, suggested) | Purpose |
|---|---|
| `deploy/zenoh/` | Zenoh router config + container compose |
| `deploy/wireguard/` | WireGuard tunnel config |
| `deploy/oidc/<idp>/` | IdP deployment (one of Dex/Kanidm/Zitadel/Keycloak/Ory) |
| `deploy/audit/` | Audit sink config |
| `deploy/health/` | Health endpoint script |
| `deploy/policy/release-allowlist.yml` | Per-topic release allowlist (their default-deny baseline) |
| `schemas/release/<partner>/` | `attest/schema/...` declarations for outbound topics |

Examples for each piece live in `docs/operations/partner-idp-integration/<idp>.md` and partner-onboarding runbook.

## Migration path — small partner → larger partner

A partner that starts with the PRA single-node stack can grow incrementally:

- **Add a second router** at a different site for redundancy → no impact on us; their internal multi-site discipline is theirs.
- **Add Spock or similar replication** for partner-side databases → still no impact on us.
- **Adopt phoenix-native discipline** → strengthens their resilience; our boundary unchanged.
- **Add CDS conditioning** for cross-classification work → that's a new conversation, governed by ADR [`../adr/0504-cds-conditioning.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0504-cds-conditioning.md).

The PRA scales gracefully because it doesn't lock in opinionated choices.

## Trigger conditions to revise the PRA

- **Performance expectations break under commercial internet.** If commercial transport becomes too unreliable for typical partnerships, revisit transport assumptions.
- **A partner consistently can't meet a four-facet expectation.** Revisit calibration.
- **CDS becomes a partner requirement.** PRA gains a CDS-conditioning section.
- **Our stack changes in ways that affect partner interop.** Update the "what the PRA omits" list and the example configs.
- **Partner volume crosses ~5.** Revisit whether the example-config catalog needs broader IdP coverage or whether a partner-side helper tool would reduce onboarding friction.

## What the PRA is NOT

- **Not required.** Partners may run any stack that meets the four-facet expectations.
- **Not certified by us.** Partners adopting the PRA are not "certified" — they are simply running a configuration we know interops cleanly. Compliance attestation is per the charter, not per the PRA.
- **Not exhaustive.** Domain-specific partner configurations (e.g., for sensor-data partners, video-data partners) live as PRA *extensions* — additional documents that build on the eight-piece base. Not in scope for the initial PRA.
- **Not a product.** It is a recipe. Partners cannot "buy" the PRA from us; we provide the recipe in the open.

## References

- ADR [`0821`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md) — anchor decision
- ADR [`0223`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0223-goat-moon-pod-repo-containment.md) — goat-moon-pod repo-containment + naming-pattern decision
- [`mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md) — design companion
- [`moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md) — Tier-0 seven-requirement contract
- [`goat-moon-pod.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/goat-moon-pod.md) — abstract spec for moon-pods
- [`goat-moon-pod-builder-guide.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/goat-moon-pod-builder-guide.md) — for vendors building their own moon-pods
- [`../partner-templates/data-sharing-charter.md`](../partner-templates/data-sharing-charter.md) — formal memo
- `zenoh-data-fabric.md` — substrate
- [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) — schema discipline at the boundary
- ADR [`0411`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0411-ory-idp-mvp.md) — Ory IdP MVP (our side of OIDC)
- ADR [`0309`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0309-bridge-cidr-allowlist.md) — bridge CIDR allowlist (our side of conditioning)
- `../integrations/moon-pods/` — per-vendor cookbooks
- `docs/operations/partner-idp-integration/` — per-IdP example configs
