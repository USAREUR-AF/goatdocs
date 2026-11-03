# NetBird Feature Usage — What We Use, Why, and How

**Purpose.** NetBird's management dashboard exposes a broad feature surface (the left-nav sections and the per-group usage columns on the Groups page). We use a deliberately small slice of it. This doc makes that slice explicit: for every NetBird capability, whether we use it, the reason, and where it is wired. It exists so that "column X reads 0" is read as a **decision**, not a gap.

This is a companion to [deliberate-deltas.md §2](deliberate-deltas.md) (how our NetBird deployment diverges from vanilla). Where deltas describes *how we run NetBird differently*, this doc catalogs *which of its features we touch at all*.

## Conclusion first

We use NetBird for exactly three jobs: **carry WireGuard peers**, **enroll them (setup keys)**, and **segment them (groups + access-control policies)**, plus **one nameserver group** to point peers at mesh CoreDNS. Everything else NetBird offers — user/team management, network routes, network resources, reverse proxy, posture checks, DNS record management — we deliberately do **not** use, because that responsibility lives in another plane of the architecture (Ory for humans, CoreDNS for names, full-mesh P2P for reachability, cryptographic attestation for trust).

Two load-bearing reasons explain almost every "don't use":

1. **Split-plane identity.** NetBird is the *machine* plane only. Humans and services authenticate through Ory (Kratos/Hydra); machines are WireGuard peers. So NetBird groups carry peers, setup keys, and ACL policies — never human user memberships. See identity-architecture.md, mesh-and-ory-roles.md.
2. **NetBird routes traffic, it does not resolve names or advertise subnets for us.** The mesh is full-mesh WireGuard P2P; names come from mesh CoreDNS (dns-service-discovery.md); the network host forwards via kernel routing. NetBird's own routing/DNS-record features would duplicate or fight those.

## Feature catalog

Grouped by the dashboard's left-nav. "Column" notes which per-group usage column on the Groups page the feature drives.

| NetBird feature | Use? | Why | How / where wired |
|---|---|---|---|
| **Peers** (column: peers) | **Yes** | The mesh itself — every enrolled node is a WireGuard peer. | Enrolled via `netbird up`; P2P after enrollment, relay fallback. [wireguard-netbird-primer.md](wireguard-netbird-primer.md) |
| **Setup Keys** (column: setup keys) | **Yes, constrained** | Peer enrollment credential. Role-scoped TTLs (bootstrap 1d / admin 7d / operator 30d / peer 7d, cut from 90d 2026-08-18), auto-revoked daily, kill-switchable; being phased out for sovereign account-and-key creation. | [deliberate-deltas.md §2.5](deliberate-deltas.md), [setup-key-rotation.md](https://github.com/usareur-af/goatcore/blob/main/docs/operations/setup-key-rotation.md), ADR 0410. Never DB-direct seeded (§2.7). |
| **Groups** | **Yes** | The anchor for ACL policies, setup-key scoping, and the nameserver-group attachment. Machine-plane only. | `netbird_acl_taxonomy.yml` / `netbird_acl_matrix.yml`; role/affiliation grammar in identity-grammar.md — note: **affiliation is never a NetBird group**. |
| **Access Control → Policies** (column: policies) | **Yes** | Mesh segmentation, enforced. Default policy plus a scoped rule set (peers→infra on specific ports, admins any-port, etc.). | mesh-acl.md, rbac-adherence.md; seeded/managed by the `netbird_acl_*` playbooks. |
| **Access Control → Posture Checks** | **No (open candidate)** | Currently unused — seeded policies carry `source_posture_checks: '[]'`. Our trust posture is cryptographic (peer-key attestation, ADR 0315) and our health/OS-state story is a reveal-only bus surface, not a connection-time gate. Posture checks *could* add OS/version enforcement; see "Open candidate" below. | Not wired. Evidence: `ops/mgmt-host-bootstrap/main.go`, `ops/wave-33/tier-4b/inchworm.sh` insert policies with an empty `source_posture_checks`. |
| **DNS → Nameservers** (column: nameservers) | **Yes, one** | A single mesh-DNS nameserver group pushes the per-site CoreDNS resolver (`mesh_ip:5353`) to peers, so `*.<site>` names resolve on the mesh. Attached to `All`, not per-group — which is why only the `All` row shows a nameserver count. | `ops/ansible/goat-netbird-account-init.yml` seeds it; resolver is mesh CoreDNS (dns-service-discovery.md). |
| **DNS → record management** | **No** | Service/name records are owned by mesh CoreDNS (hand-kept goat zone + per-site generated zones), plus a signed name-fallback snapshot for DNS-down. NetBird's DNS records would be a second, competing source of truth. | dns-service-discovery.md, [name-fallback-resolver.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/name-fallback-resolver.md). |
| **Networks / Network Routes** (columns: resources / routes) | **No** | The mesh is full-mesh P2P; peers reach each other directly and the network host forwards via kernel routing. We do not advertise subnets *through* a NetBird peer, so there are no network-resource or route objects. | Not wired — no `api/networks` or `api/routes` objects exist in the codebase. |
| **Reverse Proxy** (Beta) | **No** | Ingress and service fronting are Traefik / haproxy / Caddy, chosen before NetBird shipped this. Adopting a Beta overlay for a solved problem adds surface for no gain. | Traefik/haproxy/Caddy per dns-service-discovery.md, relay-ingress-dispatch.md. |
| **Team → Users** (column: users) | **No directory sync** | We run NetBird with its IdP-manager integration disabled — `IdpManagerConfig.ManagerType` is `"none"` on every mgmt-host, a deliberate decision, not an unset default. So Ory's user directory is never mirrored into NetBird's Users list, and peer enrollment (setup keys) needs no NetBird user. One exception: an admin operator who mints a per-person access token needs an individually-created NetBird *user*. See "Users / IdP sync" below. | identity-architecture.md §4.3; admin-user gap F-238. |
| **Activity** (audit log) | **Read-only reference** | NetBird's activity log is a convenience view. It is **not** our audit source of truth — operator actions, wide events, and the three-tier audit store are. | [operator-action-audit.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/operator-action-audit.md), [observability-wide-events.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/observability-wide-events.md). |
| **Control Center** (Beta) | **No** | Aggregate dashboard we don't rely on; our fleet COP is `goat top` / panoscope / the environment-health surface. | [goat-top.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/goat-top.md), panoscope.md. |

## Why the empty columns are correct, restated

The Groups page shows counts only for **peers**, **policies**, and **setup keys** per group, plus a **nameserver** count on `All`. Every other column is 0 because the corresponding feature is owned by another plane:

- **Users = 0** → NetBird's IdP-directory sync is off by design (`ManagerType: "none"`); Ory is never mirrored in. Only individually-created admin users ever appear (see below).
- **Resources / Routes = 0** → P2P mesh, no subnet advertisement.
- **Nameservers = 0 on most rows, 1 on `All`** → one nameserver group, attached fleet-wide rather than per-group. Correct, not missing.

## Users / IdP sync — off by design, with one exception

NetBird's IdP-manager integration is disabled: `IdpManagerConfig.ManagerType` is `"none"` on every mgmt-host. This is a deliberate decision (formalized 2026-04-25), not a placeholder — NetBird's IdP requirement was *artifactual*, a side-effect of the dashboard-mediated admin flow rather than a property of the gRPC peer-enrollment path. Two consequences:

- **Peer enrollment needs no NetBird user** — setup keys don't use OIDC.
- **Human web-UI auth** (including the NetBird dashboard itself) points *directly* at Ory Hydra's OIDC endpoints, not through NetBird's adapter layer.

So Ory stays the single user directory, is never mirrored into NetBird, and an IdP outage can't block peer enrollment. Canonical reasoning: identity-architecture.md §4.3.

**The one exception.** An admin operator who mints a per-person NetBird access token (the `*_NB_API_TOKEN` that `goat admin onboard` uses) still needs a NetBird *user* — a dashboard OIDC login. Because nothing syncs the directory, that user is created individually, not pulled from Ory. Onboarding automation currently omitting this step is a tracked gap that has caused an accidental ownership transfer: F-238. This is *not* the IdP sync coming back — it is a handful of individually-provisioned admin logins, still with Ory as the directory of record.

## Open candidate — Posture Checks

Posture Checks is the one NetBird capability that is unused *and* not clearly ruled out by the architecture. NetBird posture checks gate a peer's connection on client-reported attributes (OS/version, NetBird version, geo, running processes). We currently rely on cryptographic peer-key attestation (ADR 0315) for *trust* and the environment-health bus surface for *observability*, neither of which enforces a minimum client version at connect time.

If minimum-version or basic client-hygiene enforcement becomes a requirement, posture checks are the native place to do it — but note they trust client self-report, so they complement rather than replace attestation. Until there is a concrete driver, this stays deliberately off. Any adoption should update this doc's row and the `source_posture_checks` handling in the `netbird_acl_*` playbooks.

## Read more

- [deliberate-deltas.md §2](deliberate-deltas.md) — how our NetBird deployment diverges from vanilla (multi-site, relay tiers, pinned image, setup-key discipline).
- mesh-acl.md — access-control policy model and enforcement.
- identity-architecture.md / mesh-and-ory-roles.md — the split-plane identity model.
- dns-service-discovery.md / [name-fallback-resolver.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/name-fallback-resolver.md) — name resolution ownership.
- [wireguard-netbird-primer.md](wireguard-netbird-primer.md) — NetBird/WireGuard basics.
