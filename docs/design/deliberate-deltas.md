# Deliberate Deltas — How goat Diverges From a Vanilla Netbird / WireGuard ZTOL Deployment

> **Read this first if you're new to this repo, alongside [engineering-baseline.md](engineering-baseline.md).** A vanilla self-hosted Netbird mesh on a single VM with the default supply chain, default identity model, default backup posture, and default egress posture is a perfectly reasonable starting point — and it is *not* what we run. This document is the master index of every place we deliberately diverged. If a topic appears here, the bespoke choice is load-bearing and you must read the linked design doc or ADR before changing it. If a topic does not appear here, the answer is in one of two places: (a) [engineering-baseline.md](engineering-baseline.md) catalogs the load-bearing standard practices we deliberately follow; or (b) if it's in neither doc, assume canonical Netbird / WireGuard / Linux / Postgres / Docker / Ansible / Terraform behavior applies and the topic is not load-bearing here.
>
> The two-doc split is deliberate: this doc tells you what's bespoke and load-bearing-because-it's-different; the baseline doc tells you what's standard and load-bearing-because-it's-done-well. Both views matter — emphasizing only the deltas creates the misread that "if it's not exotic, it must not matter."
>
> Companion docs: collaborator-overview.md (architecture end-state), [wireguard-netbird-primer.md](wireguard-netbird-primer.md) (what WG/Netbird actually do under the hood). Decision rationale lives in [adr/](https://github.com/usareur-af/goatcore/tree/main/docs/adr) — every entry here points at one or more.

## How entries are structured

Each entry has the same four fields:

- **Choice** — what we run.
- **Vanilla** — what a default deployment would do.
- **Why** — the load-bearing reason (often a constraint, threat model, or sovereignty rule).
- **Read more** — the canonical design doc, ADR, or module.

Entries are grouped by layer, top-to-bottom: sovereignty → mesh → state → backups → identity → time → egress → OS / supply chain → orchestration → data fabric → crypto → architectural disciplines.

## What we DO NOT diverge from (assume vanilla here)

If a topic is not in the sections below, default behavior applies. In particular:

- **WireGuard cryptography and data path** — ChaCha20-Poly1305 / AES-256-GCM, Curve25519 key exchange, Noise handshake, silent drop of unauthenticated packets. Standard kernel WireGuard (or userspace `wt0` where the Netbird agent is in control). No proprietary encapsulation, no traffic inspection. See [wireguard-netbird-primer.md](wireguard-netbird-primer.md) §"Standard WireGuard".
- **Postgres semantics** — standard PG 16 SQL, transactions, MVCC. Spock layers replication on top; it does not change PG semantics.
- **Docker Compose semantics** — standard Compose v2. systemd unit wrappers add boot discipline; nothing exotic in the Compose files themselves.
- **Ansible / Terraform semantics** — standard roles, inventories, playbooks, HCL, providers. The bespoke pattern is the bootstrap-vs-refresh split (§9.2), not Ansible itself.
- **Let's Encrypt / ACME** — standard DNS-01 via the Cloudflare provider, Traefik handles renewal.
- **systemd, chrony, nftables** — stock Linux. Our bespoke layers (NTP hygiene daemon, default-deny egress, etc.) build on top, not in place of.

---

## 1. Sovereignty & cloud usage

### 1.1 Cloud is acceptable for in-flight transit, forbidden for data-at-rest

**Choice:** Cloud (AWS, Cloudflare) is acceptable for relays, bridges, public DNS, ACME DNS-01, and SSM bootstrap access. Cloud is *not* acceptable for the mgmt-plane database, backups, observability stores, hosted services, or any other data-at-rest. Sovereign hardware (x86 and arm64 hosts at each site) holds all "No"-row layers.

**Vanilla:** A self-hosted Netbird typically runs the entire stack on one cloud VM, including Postgres.

**Why:** Mission and user data must remain on hardware we control; commercial cloud is opaque to us legally and operationally. Encrypted in-flight traffic through cloud relays is fine — relays see only WireGuard ciphertext.

**Read more:** collaborator-overview.md §"The Sovereignty Split".

### 1.2 PagerDuty (third-party SaaS) for alert paging — a bounded exception

**Choice:** The critical-alert **paging** channel is PagerDuty (cloud SaaS), a deliberate exception to §1.1. The notification path must live *off* our infra — a pager hosted on the box it watches cannot report that box's death. The exception is bounded by a strict data boundary: PagerDuty sees only alert *metadata* (alertname / severity / site / component labels + the summary, e.g. "relay root disk 96%"), never data-at-rest, fabric payloads, identities, or WireGuard content.

**Vanilla:** alerting, if present, typically pages from the same box that runs everything.

**Why:** a self-hosted notifier dies *with* the host it watches. PagerDuty (cloud) survives the failure domain it watches. Sovereign-aligned ntfy remains available as a *peer* (run both) and may be **required** on a relay VPS for higher-sensitivity sites.

**Read more:** ADR 1059, `failure-isolation.md` §9.

---

## 2. Mesh management (Netbird-specific deltas)

> **Which Netbird features we use at all** (positive catalog — use / don't use, why, how): [netbird-feature-usage.md](netbird-feature-usage.md). This section covers *how we run the features we use differently*; that doc covers *which of Netbird's features we touch*.

### 2.1 Multi-site active-active (not single mgmt-server)

**Choice:** Each site runs its own mgmt + signal + Postgres pair. Spock multi-master replicates state across sites. A federated signal server handles cross-site peer discovery.

**Vanilla:** Netbird's reference deployment is a single mgmt-server backed by a single Postgres.

**Why:** No single site can be a single point of failure. A partitioned site must continue accepting enrollments and policy changes locally and reconcile when the WAN returns.

**Read more:** ha-multi-site.md, federation-security.md.

### 2.2 Three-tier relay (rathole + Coturn + Netbird relay)

**Choice:** VPS relays each run rathole (mgmt 443), Coturn (UDP 3478 STUN), and Netbird relay (TCP 33073 data-relay fallback). DNS round-robin on `netbird.legacy.example`.

**Vanilla:** Netbird's relay is a single Coturn + signal endpoint. Rathole is not part of the canonical stack.

**Why:** The site gateway has no port forwarding — VPS relays provide public ingress. Rathole tunnels mgmt-plane traffic from the public internet to the sovereign mgmt-host without exposing the host directly to the internet.

**Read more:** relay-architecture.md; [terraform/modules/relay/](https://github.com/usareur-af/goatcore/tree/main/terraform/modules/relay).

### 2.3 Bridge VPSes are separate from relay VPSes

**Choice:** Bridge VPSes (separate from the relay VPSes) handle traffic between the mesh and external partner networks (partner TAK federation, etc.). Elastic IPs for partner whitelisting. Forwarded ports locked down by default.

**Vanilla:** Most Netbird deployments have no partner-network egress concern; if they do, they expose services through a single ingress.

**Why:** Partner networks require IP whitelisting. Separating bridge from relay keeps mgmt-plane and partner-egress concerns isolated and lets each be sized and rotated independently.

**Read more:** tak-federation.md, bridge-peering.md, [terraform/modules/bridge/](https://github.com/usareur-af/goatcore/tree/main/terraform/modules/bridge).

### 2.4 Pinned, locally-built `netbird-mgmt` image

**Choice:** We run `netbird-mgmt:patched-53b04e5` (or a successor pinned SHA) built from our fork, not the upstream `latest` tag.

**Vanilla:** Pull `netbirdio/netbird-mgmt:latest`.

**Why:** Pinning is required for coordinated multi-site upgrades — every node in the mesh must run the same schema-compatible build before the new container starts. Local patching lets us carry urgent fixes without waiting on upstream release cadence.

**License posture (added 2026-04-27).** Upstream relicensed `management/` / `signal/` / `relay/` / `combined/` to AGPLv3 in Aug 2025; our fork base post-dates the relicense and we modify `./management`, so AGPLv3 §13 (the Affero clause) applies. We accept AGPL downstream and codify the discipline that keeps compliance cheap: in-tree patches at `ops/netbird/patches/`, public repo, process-boundary aggregation only (no linking AGPL code into our own Go services). Escape valves (rebase to pre-AGPL `v0.52.2` + clean-room CVE backports per the openzro pattern, or ride openzro as upstream) are named with explicit triggers. Full rationale: ADR 0110. Finding: F-010.

**Read more:** [goat-ha-dev-validation.md](https://github.com/usareur-af/goatcore/blob/main/docs/operations/goat-ha-dev-validation.md) §2.1 (coordinated-upgrade playbook), [`../adr/0110-license-posture-agplv3-forked-components.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0110-license-posture-agplv3-forked-components.md), `../findings/F-010-netbird-agplv3-relicense-aug-2025.md`.

### 2.4a Peer-side verification of WireGuard pubkeys against an offline-CA trust root (Phase 3 deferred)

**Choice:** Every peer's WireGuard pubkey is signed by the offline CA at enrollment; receiving peers verify the signature against a locally-cached trust-root set before building a tunnel. Mgmt-host is **not** the sole peer-identity authority. Even a fully-compromised mgmt-host cannot mint a peer the rest of the mesh will accept. Phase 3 deferred (Block 22H, sequenced after Block 22 main work); ADR 0315.

**Vanilla:** Netbird (and most mesh control planes) treat the management server's mgmt-API sync as the sole authority for peer-pubkey distribution. Receiving peers do not verify against any external trust root.

**Why:** Host hardening (LUKS, STIG, FIPS, supply chain, runtime detection) is preventive and reduces the probability of mgmt-host compromise but does not change what a compromised mgmt-host can do. Peer-side cryptographic verification rooted at the offline CA is the architectural complement — same shape as Tailscale's Tailnet Lock, adapted to our offline-CA-on-YubiKey-PIV custody pattern. We already have the trust anchor (ADR 0406); Block 22B already runs an analogous pubkey-into-allowlist pipeline for the outer control plane; Block 22H extends the pattern to the data-plane mesh.

**Read more:** [`../adr/0315-peer-key-attestation-via-offline-ca.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0315-peer-key-attestation-via-offline-ca.md), `../findings/F-011-netbird-mgmt-sole-peer-identity-authority.md`, `../project/implementation-plan.md` Block 22H.

### 2.5 Setup keys are short-lived, role-scoped, and being phased out

**Choice:** Setup keys are role-scoped (bootstrap 1d / admin 7d / operator 30d / peer 7d — peer cut from 90d on 2026-08-18), auto-revoked daily, kill-switchable. Block 21 Go CLI `mgmt-host-bootstrap` will replace operator-issued setup keys with sovereign account-and-key creation directly against Postgres.

**Vanilla:** Netbird setup keys are typically long-lived strings checked into config-management.

**Why:** A leaked setup key = mesh enrollment by anyone. Short TTL + role scope + auto-revoke bound the blast radius. Block 21 removes the IdP from the peer-enrollment path entirely.

**Read more:** [setup-key-rotation.md](https://github.com/usareur-af/goatcore/blob/main/docs/operations/setup-key-rotation.md), identity-architecture.md, ADR 0410.

### 2.6 Offline CBOR enrollment bundles (PACE Contingency)

**Choice:** Devices ship with a CBOR bundle signed by an offline CA (Ed25519 on YubiKey PIV), carrying pre-shared WG config + signed ACL capability + 90-day expiry. A validator sidecar on each mgmt-host auto-provisions the peer without an operator-issued setup key.

**Vanilla:** No equivalent in canonical Netbird.

**Why:** Devices may deploy into environments where mgmt-server reachability is not guaranteed at enrollment time. Offline bundles preserve enrollment under PACE-Contingency conditions.

**Read more:** [offline-enrollment.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/offline-enrollment.md), [enrollment-bundle-runbook.md](https://github.com/usareur-af/goatcore/blob/main/docs/operations/enrollment-bundle-runbook.md).

### 2.7 Do not seed setup keys directly into Postgres

**Choice:** Setup keys must be created via the netbird API or the Block 21 Go CLI — never via direct DB insert.

**Vanilla:** Direct DB insert appears to work in any test env.

**Why:** Modern netbird hashes the presented key, so DB-direct seeded rows produce silent authentication failures. The DB-direct shortcut was used in attempt-1, attempt-2, Wave 3, and hadev bootstrap before the failure mode was identified (2026-04-25). Wave 3 §3.4 federation-load harness was never actually validated against real-protocol peers as a result.

**Read more:** identity-architecture.md.

---

## 3. Mgmt-plane state & replication

### 3.1 PostgreSQL 16 + Spock multi-master (not SQLite, not single-Postgres)

**Choice:** Spock multi-master logical replication across all sites' Postgres pairs.

**Vanilla:** Netbird's default backend is SQLite; many self-hosted deployments use a single Postgres.

**Why:** Multi-site active-active is impossible without it. A partitioned site must accept enrollments and policy changes against its local replica and reconcile after reconnect.

**Read more:** ha-multi-site.md, pg-spock-security.md.

### 3.2 Per-site VRRP failover (Router-A/B + keepalived)

**Choice:** Each site runs Router-A and Router-B with a keepalived VIP. Active-passive within the site, active-active across sites.

**Vanilla:** Single mgmt-host per site.

**Why:** Intra-site failure must not require operator intervention; failover is automatic. Keepalived provides sub-second VIP migration without involving the mgmt-plane DB.

**Read more:** ha-failover.md.

---

## 4. Backup strategy

### 4.1 Per-site paired pgBackRest stanzas; no cloud in the backup path

**Choice:** Two independent stanzas per site (`<site>-a-netbird` on Router-A, `<site>-b-netbird` on Router-B), each with a local NVMe repo at `/opt/docker-data/pgbackrest/`. Cross-site site-loss durability carried by Spock replication, not by a cloud backup tier.

**Vanilla:** pgBackRest typically writes to one stanza with one repo, often S3.

**Why:** Sovereignty rule — backups are data-at-rest. Local NVMe + Spock replication delivers the required RPO and RTO without commercial cloud. Trade-off accepted: no cross-site PITR.

**Read more:** [pgbackrest.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/pgbackrest.md).

---

## 5. Identity & access

### 5.1 Four-domain identity model

**Choice:** Humans + service accounts via OIDC IdP (Ory Kratos + Hydra per-site, Postgres-backed); machines via WireGuard / netbird; workloads via SPIFFE/SPIRE (Phase 3+); RBAC at MVP, Keto/OpenFGA when role-spaghetti hits. Common audit pipeline (Block 17D integrity tier).

**Vanilla:** Netbird's embedded IdP, no SPIFFE/SPIRE, no separate workload identity domain.

**Why:** Each domain has distinct lifecycle, attestation, and revocation needs; collapsing them into one IdP is a future-pain-deferred decision.

**Read more:** identity-architecture.md, idp-strategy-spike-2026-04-25.md, ADRs 0410 / 0411 / 0412.

### 5.2 Per-site Ory Kratos + Hydra (not external SaaS IdP)

**Choice:** Ory MVP per-site, Postgres-backed, behind keepalived VIP. Standard OIDC claims (`sub`, `email`, `groups`) only — switching IdPs is one config field.

**Vanilla:** Most self-hosted Netbird deployments use an external SaaS IdP (Google, Okta, Auth0).

**Why:** Sovereignty + Island Mode — a partitioned site must still authenticate humans. SaaS IdP is unreachable when the WAN is down.

**Read more:** identity-architecture.md, ADR 0411.

---

## 6. Time hygiene

### 6.1 Three-tier time strategy (multi-GNSS + NTS + drift model)

**Choice:** Per-site multi-GNSS + a GPS-disciplined time server + public NTS + peer NTS, blended via chrony with NTS-only ZTOL ingestion. Per-node adaptive drift-model daemon that reports honest uncertainty when self-clocking.

**Vanilla:** Default chrony pointed at a public NTP pool.

**Why:** Time is a security primitive — cert validity windows, audit ordering, replication conflict resolution all assume bounded skew. Tactical edge cannot trust public NTP exclusively.

**Read more:** [ntp-strategy.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/ntp-strategy.md), [universal-ntp-hygiene.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/universal-ntp-hygiene.md).

### 6.2 Admit-audit sidecar gates enrollment on time-health

**Choice:** A sidecar (`ntp-admit-sidecar`, h2c reverse proxy on :8080 → mgmt-container :8081) refuses enrollment when local time-health is degraded.

**Vanilla:** Netbird does not gate enrollment on clock skew.

**Why:** A peer enrolling with a degraded clock will produce certs with wrong validity windows and replication rows with wrong timestamps. Cheaper to refuse at the door than to debug later.

**Read more:** [universal-ntp-hygiene.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/universal-ntp-hygiene.md), [ops/time-hygiene/](https://github.com/usareur-af/goatcore/tree/main/ops/time-hygiene).

---

## 7. Egress & policy enforcement

### 7.1 Five-tier cascading egress (Block 17)

**Choice:** Tier 0 DNS egress control (blocks DoH/DoT, forces mesh resolver) → Tier 1 default-deny nftables on Router-A/B → Tier 2 Squid HTTP/HTTPS forward proxy with SNI allowlist (no TLS MITM) → Tier 3 dante SOCKS5 for narrow non-HTTP flows → Tier 4 time-bounded direct CIDR allowlist with auto-expiry.

**Vanilla:** Once enrolled, a mesh peer can freely navigate the public internet.

**Why:** Closes the back-door before Phase 3 production. Default-deny is the operating posture; every allow is auditable.

**Read more:** [egress-proxy.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md), [egress-runbook.md](https://github.com/usareur-af/goatcore/blob/main/docs/operations/egress-runbook.md).

### 7.2 Per-site Policy Engine (Block 17A.5) — sovereign, not GitHub

**Choice:** A Go service `db-policy-engine` per mgmt-host (active-passive behind keepalived VIP). Spock-replicated `egress_policy` + `egress_approval` + `egress_request_event` tables. OIDC auth via per-site Ory. Three notification adapters (email + Matrix + isitup widget). Dual-path approval: normal (single role-holder + 24h SLA, auto-escalates on breach) and fast (two-of-N, immediate). CRDT-style conflict resolution under partition.

**Vanilla:** Initial Block 17 design used GitHub CODEOWNERS for two-of-N approval; reversed same-day on review (violated Island Mode — partitioned site cannot reach GitHub).

**Why:** Approval workflows must operate when the site is partitioned. The same engine also services Block 18A microsegmentation, 18D credential rotations, and 18F tamper-response config.

**Read more:** [egress-proxy.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md) §6.

### 7.3 Audit-log integrity tier with cross-mounted MinIO + tamper detection

**Choice:** Per-site MinIO with Object Lock, cross-mounted peer-mgmt-host storage, integrity ledger, daily tamper-detection CI.

**Vanilla:** Audit logs write to local disk or to a centralized SIEM.

**Why:** Defense in depth — assume the host is compromised; the audit trail must be tamper-evident even to root.

**Read more:** [egress-proxy.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md) §5.6.

---

## 8. OS, supply chain, runtime hardening

### 8.1 Hardened base OS — Ubuntu 24.04 + LUKS (x86), Ubuntu-for-Tegra 22.04 + Ubuntu Pro FIPS+STIG (Jetson-class arm64); Kairos rejected

**Choice:** x86 mgmt-hosts run Ubuntu 24.04 + LUKS (TPM 2.0 key custody). Jetson-class arm64 hosts run Ubuntu-for-Tegra 22.04 with Ubuntu Pro FIPS + STIG, mutable root, LUKS on NVMe with OP-TEE (Tegra SE-backed) key custody where feasible on JetPack. Three-tier storage, NBDE, CSfC DAR framing, FIDO2 break-glass.

**Vanilla:** Stock Ubuntu cloud-image with no LUKS, no TPM, no FIPS, no STIG.

**Why:** FIPS 140-3 + DISA STIG are hard compliance requirements. Kairos was evaluated and dropped — could not deliver FIPS + STIG.

**Read more:** [os-baseline-and-luks.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/os-baseline-and-luks.md).

### 8.2 Chainguard-first containers in the team's goatnets, redistributable bases in public; Iron Bank is not a standalone trust signal

**Choice:** The goat team's goatnets run third-party containers from Chainguard where an equivalent exists, and build goat's own images on Chainguard bases. Iron Bank presence is used only after per-image audit when Chainguard has no equivalent. The public repositories build on base images anyone may redistribute (Debian official images, distroless Debian 13), named by role; an environment's overlay names its own images for those roles, which is how the team's goatnets get Chainguard.

**Vanilla:** Pull from Docker Hub.

**Why:** Supply-chain provenance is a Block 13 requirement. Iron Bank hosts many insecure containers — its catalog presence is not a security guarantee. Public images cannot carry a paid catalogue's layers, and naming bases by role lets any environment choose its own without forking a Dockerfile.

**Read more:** [ADR 0700](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0700-chainguard-first.md), [ADR 1220](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1220-public-base-images-by-role-overlay-supplies-its-own.md), [base images by role](https://github.com/usareur-af/goatcore/blob/main/docs/design/base-images.md), [build goat images on your own base images](https://github.com/usareur-af/goatcore/blob/main/docs/operations/build-on-your-own-base-images.md).

### 8.3 Open-source EDR + continuous vuln scanning (Block 18G + 18H)

**Choice:** Falco (container runtime) + osquery/Fleet (host state) + auditd (syscall) ship to the integrity tier. Trivy + grype + osquery config-drift drives continuous vuln scanning.

**Vanilla:** Closed-source DoD-approved EDR (CrowdStrike, etc.).

**Why:** Sovereignty + cost + transparency.

**Read more:** implementation-plan.md Block 18.

### 8.4 Block 18 security gap closeouts (microsegmentation, PAM, boot chain, credential hygiene, IR, tamper response)

**Choice:** 18A internal mesh microsegmentation. 18B PAM (sudo audit + session recording + JIT elevation). 18C boot chain integrity (UEFI Secure Boot + signed shim + dm-verity). 18D credential hygiene (systematic WG/SSH/TLS rotation). 18E incident response runbook + quarterly drills. 18F tamper response (chassis intrusion → key zeroization).

**Vanilla:** None of these are present in a default Netbird deployment.

**Why:** Caught during adversarial review. Each closes a categorical gap that LUKS + WireGuard alone do not address.

**Read more:** implementation-plan.md Block 18.

---

## 9. Container orchestration & deployment workflow

### 9.1 Docker Compose now, Podman + Quadlet next (not Swarm / Nomad / K8s / k3s / Spin)

**Choice:** Docker Compose on mgmt-hosts today. Systemd-native binaries on relay + bridge VPSes. **Active successor track:** Podman + Quadlet — one-service spike in Phase 2D against an archive-trimmed inventory; full migration gated on the spike. The previously-planned "Compose-wrapped-by-systemd" formalization is paused (it duplicates Quadlet's native systemd integration).

**Vanilla:** Many "production" deployments default to k3s or full Kubernetes.

**Why:** At our scale, the operational tax of K8s outweighs its benefit. Podman + Quadlet was originally framed as a Phase 3+ watchlist item; pulled forward 2026-04-25 because (a) the §4.2 wrapper work would have built Quadlet-but-worse, and (b) Cosign signature verification at container-start time is already operationally relevant given Chainguard-first.

**Read more:** container-orchestration.md, [ADR 0207](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0207-docker-compose-orchestration.md), implementation-plan §Block 16.

### 9.2 Two-phase Ansible: bootstrap (SSM) → refresh (SSH-over-mesh)

**Choice:** Every new mgmt-host env ships both `<env>-bootstrap.yml` (SSM, runs once, slow) and `<env>-refresh.yml` (SSH-over-mesh, routine, fast). Inventory split: `inventory/mgmt-hosts.ini` (SSM) + `inventory/mgmt-hosts-mesh.ini` (SSH override loaded after).

**Vanilla:** Ansible against a single inventory with one connection method.

**Why:** A new host has no mesh IP yet — bootstrap must use SSM. Once enrolled, SSH-over-mesh is faster and removes the aws-vault dependency for routine drift fixes.

**Read more:** CLAUDE.md §"Bootstrap vs refresh".

### 9.2a Fleet management without a fleet agent or a fleet controller

**Choice:** No central fleet controller and no always-on privileged fleet agent. Nodes converge by **pulling** signed, versioned intent from a *site-local* replica on a jittered interval, and what the pull re-triggers is the existing idempotent Ansible play — so there is exactly one convergence engine, and what is new is the trigger and the transport, not the actuator. Push survives only for operations needing coordinated ordering across hosts (today `coordinated-upgrade.yml`), and those are explicitly unavailable in island mode. Inventory is derived from what nodes declare, never from a maintained registry.

**Vanilla:** A control plane that is the authority — Rancher Fleet, Balena, Azure IoT Edge, Greengrass, Foundries, Mender, or an agent reporting to a SaaS console. All of them degrade at the edge to *operating on last-known intent*.

**Why:** [ADR 0206](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0206-island-mode-by-construction.md) requires a partitioned site to manage its own nodes for 30 days, so a controller the site must reach is disqualified rather than merely inconvenient. Three further constraints point the same way: the fabric has no delivery lifecycle, so a push cannot know it landed; fleet loop load must *decay* under failure or it becomes the M-085 storm shape ([ADR 1081](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1081-control-plane-storm-resilience.md)); and a push converges only the set reachable during the run, which at the denied edge is the wrong set. The cost is real and named: pull loses cross-host orchestration ordering and is harder to debug.

**Read more:** [fleet-management.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/fleet-management.md), [ADR 1109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1109-fleet-management-dimension-and-pull-convergence.md), environment-parity.md (the config-alignment half).

### 9.3 Cloud envs are tracked and ephemeral

**Choice:** Every cloud env has explicit teardown criteria and destroy commands tracked centrally. New cloud envs add a row in the same PR that provisions them.

**Vanilla:** Cloud envs persist until someone notices them on the bill.

**Why:** Cost discipline + drift discipline. Ephemeral envs cannot accumulate snowflake state.

**Read more:** cloud-env-lifecycle.md.

### 9.4 CGNAT-aware validation is the default cloud-env topology

**Choice:** Every multi-host cloud validation env emulates symmetric NAT (CGNAT) by default. Peers route through NAT gateways, not public EIPs. Stock netbird as a systemd service, not nested containers. Cloud-init self-enrollment with retry loop, not Ansible-over-SSM enrollment.

**Vanilla:** EC2 hosts get public EIPs and short-circuit signal-server-mediated discovery.

**Why:** Production can run behind CGNAT. A validation env without CGNAT produces misleading evidence — hadev recorded only 1 Forward RPC over 5 days because peers found each other directly.

**Read more:** [cgnat-validation-env.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/cgnat-validation-env.md), reports/2026-04-24-cgnat-validation-attempt-1-findings.md.

---

## 10. Data fabric & service architecture

### 10.1 Tactical data fabric on Zenoh (Phase 2D pilot, Phase 3+ universal substrate)

**Choice:** Zenoh router pair per site, Rust interceptors in `zenoh-plugins/`, RocksDB storage. Phase 3+ commits Zenoh as the universal peer-interaction substrate (data pub/sub, service discovery, control/command, configuration distribution, identity attestation, health/observability, partner federation) — contingent on the Phase 2 gate.

**Vanilla:** Application-layer protocols spoken peer-to-peer over plain WireGuard; no shared data fabric.

**Why:** A unified substrate lets us absorb vendor cruft into one-per-class shims, supports Island-Mode storage consistency, and gives us PQ-ready transport via Rosenpass.

**Read more:** zenoh-data-fabric.md, zenoh-implementation.md, [phoenix-architecture.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/phoenix-architecture.md), shim-pattern.md.

### 10.2 Service registry as single source of truth (`ops/serve/services.yaml`)

**Choice:** `services.yaml` → `generate.py` produces Caddyfile, Caddy docker-compose, and health-check targets. Traefik terminates TLS (Let's Encrypt DNS-01 via Cloudflare); Caddy reverse-proxies to static apps or mesh peers.

**Vanilla:** Hand-edited reverse-proxy configs, separate health-check config, separate service inventory.

**Why:** One file edit propagates to all consumers; drift between proxy, health checks, and inventory is structurally impossible.

**Read more:** hosting-services.md, service-onboarding-plan.md.

### 10.3 Two-tier DNS: Cloudflare (public, enrollment) + mesh-internal (CoreDNS + dnsmasq)

**Choice:** Cloudflare hosts `legacy.example` (DNSSEC active, signed). CoreDNS on the network host + native dnsmasq on each VPS relay serve `*.netbird.legacy.example` to mesh peers via the Netbird DNS nameserver group. Same `mesh-hosts` zone file on all four resolvers.

**Vanilla:** Single public DNS zone with all records.

**Why:** Mesh-internal hostnames must not appear in public DNS. Service discovery must keep working in Island Mode when Cloudflare is unreachable.

**Read more:** dns-service-discovery.md.

### 10.4 Per-site Matrix (tuwunel + hedwig) for sovereign secure messaging

**Choice:** Per-site **tuwunel** homeserver (Rust, Apache-2.0) per [ADR 0835](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0835-secure-messaging-substrate-tuwunel.md), supersedes the prior Dendrite-pager pick in superseded ADR 0812. Scope expanded from "policy-engine notification adapter" to **secure messaging for all peers, up to 1000 users per site, ~6000 fleet-wide**. Federation across sites over wg-cp0 silent control plane only. Push gateway via UnifiedPush + ntfy (sovereign Android default) and **hedwig** (Famedly's Rust push gateway) for stock-Element + iOS via FCM-proxied APNs per [ADR 0836](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0836-matrix-push-gateway-hedwig.md), with named iOS metadata-leak waiver. OIDC SSO via Ory Kratos.

**Vanilla:** Slack, Mattermost, or no chat layer at all. Synapse + Sygnal would be the conservative Matrix-protocol pick but is excluded by the no-Python-for-load-bearing rule.

**Why:** Messaging must work in Island Mode. Federation control protects against partner-site leakage. Per-site authority over the user roster matches the per-site sovereignty posture. tuwunel-over-Dendrite picked on production-reference evidence (Swiss government citizen-facing deployment) at the 1000-user scale; Dendrite kept as the named fallback if federation soak fails.

**Read more:** CLAUDE.md §"Secure messaging substrate"; [`secure-messaging.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/secure-messaging.md) (canonical design); notification adapter pattern in [`egress-proxy.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md) §6.

### 10.5 Rapid adaptation with AI — agent-class peers + queryable-by-default fabric (anti-platform)

**Choice:** Two-shape agent platform on the existing Zenoh substrate — preplanned specialists (Tipper) + ad-hoc human-defined agents (Scout) — sharing one durable convention (agent-class peers, queryable-by-default, citation discipline, ephemeral lifecycle, mandatory data-dictionary, materialized lineage). Anti-platform posture: explicitly reject the big-platform shape; provide primitives + conventions + contracts, not a platform that owns the semantics. Externally branded as **GOAT-Net**.

**Vanilla:** Vendor agent platform (AgentSpace, Bedrock Agents) + vendor data fabric (Foundry, Lattice). Agent toolchains, ontologies, and lineage live inside the vendor product.

**Why:** Sovereignty, island-mode-correctness, and substrate reuse — agent peers ride identity / audit / observability that already exist for other reasons; the convention prevents per-agent cruft accumulation; anti-platform discipline prevents vendor lock-in.

**Read more:** [ai-rapid-adaptation.md](ai-rapid-adaptation.md), [tipper.md](https://github.com/usareur-af/goatstuff/blob/main/docs/design/tipper.md), [scout.md](scout.md), [data-dictionary.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md), [lineage.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md), [entity-vocabulary.md](entity-vocabulary.md); ADR [`../adr/0512-rapid-adaptation-with-ai.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md).

### 10.6 Mission partner sharing — `release/` namespace + bring-your-own-OIDC + Partner Reference Architecture + Charter

**Choice:** Reserved `release/<partner>/...` namespace with default-deny baseline; partners use any standards-compliant OIDC IdP (examples for Dex / Kanidm / Zitadel / Keycloak / Ory); four-facet expectations (security + functionality + performance + reciprocity); Partner Reference Architecture as a recommended-not-required minimal stack; Partner Data Sharing Charter as the formal memo basis ("necessary but not compelling").

**Vanilla:** One-bridge-per-partner with bespoke per-partner code paths; or vendor data-sharing platform that mediates the partnership.

**Why:** Partners adopt our patterns when integration is easy and our complexity is not pushed onto them. The PRA + charter + four-facet expectations + bring-your-own-OIDC make partnership formation contract-shaped, not architecture-shaped.

**Read more:** [mission-partner-sharing.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md), [partner-reference-architecture.md](partner-reference-architecture.md), [`../partner-templates/data-sharing-charter.md`](../partner-templates/data-sharing-charter.md); ADR [`../adr/0821-mission-partner-sharing-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md).

### 10.7 Vendor Data Services Provider Charter — schema declaration + GOAT-Net ingestion mandate + anti-lock-in

**Choice:** Every commercial vendor providing data services into GOAT-Net signs the Data Services Provider Charter as a precondition of procurement. Mandatory schema declaration; binary formats require explanation + remediation plan; data lands in GOAT-Net (no vendor-portal-only canonical stores); 30-day bulk export at contract end; data ownership stays with us.

**Vanilla:** Vendor data lives in vendor portal / vendor cloud / behind vendor API. Vendor schema documentation is out-of-band Word doc. Lock-in is the default.

**Why:** Virtually no commercial vendor today operates as a true data services provider. The charter is the discipline that turns vendors into ones, with explicit teeth.

**Read more:** [`../vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md); composes with [`data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) discipline.

### 10.8 GOAT-Net scaling — federation plane / site plane separation

**Choice:** Two-plane architecture for GOAT-Net as it scales beyond Phase 3 baseline. **Federation plane** (small, Spock-replicated theater-wide) carries identity / policy / schema declarations / audit metadata + digests / lineage edges. **Site plane** (locally scalable, decoupled from peer-site coordination) carries bulk sensor payloads / audit-log payload bodies / agent state / vector embeddings; HA sibling-only within a site. Data is mobile through deliberate audited operations (topic-level federation, content-addressable fetch, batch transfer) — same shape as the partner release-namespace pattern. GovCloud is a federation participant, not a centralizer. Phase 3 codifies the boundary; Phase 4+ implementation deferred to load-driven triggers.

**Vanilla:** Replicate everything across all sites (won't scale at theater) or centralize in cloud (breaks sovereignty + island-mode).

**Why:** Mainstream control-plane / data-plane separation pattern (K8s federation, Citus, Pulsar, Cassandra, IPFS shapes). Bounded replication cost + failure isolation + tactical primacy + composes with existing partner-release pattern. **Maturity caveat:** GOAT-Net is at proof-of-concept stage; the direction is sound, specific scaling characteristics will be discovered, the plan becomes operative *if* GOAT-Net earns it through the early phases.

**Read more:** goat-net-scaling.md; ADR [`../adr/0216-goat-net-federation-and-site-planes.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0216-goat-net-federation-and-site-planes.md).

### 10.9 Zenoh node identity — cert is the trust anchor; the ZID stays an opaque, pinned label

**Choice:** Routers pin a deterministic per-host Zenoh ID (`id` = truncated SHA-256 of the inventory hostname + realm) so identity is stable across restarts; owned plain publishers attach native `SourceInfo` so a sample traces to its origin node. But the ZID is **never** an authz input and is **not** structured — trust stays anchored on the X.509 cert (CN + URI-SAN), and site/region is encoded in the namespace + cert URI-SAN, not in a ZID prefix. The ZID is derived (never baked into an image, never from `machine-id`). The disposable sandbox router stays random.

**Vanilla:** Random ZID per session (Zenoh default), no source provenance attached, and — where federation best-practice is followed — a structured ZID prefix encoding site/region used as an operational discriminator.

**Why:** Pinning gives routing-graph, audit-dedup, and provenance continuity across restarts without making identity forgeable-as-trust. We decline the structured-prefix convention deliberately: with random/hashed 16-byte ZIDs cross-site collision is already negligible, and encoding site in the ZID would be a parallel, unauthenticated copy of a fact the cert already states under signature. Image-baked ZIDs collide at scale; `machine-id`-derived ZIDs collide on cloned VMs — both avoided.

**Read more:** [`../adr/1041-zenoh-router-zid-pinning-and-source-provenance.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1041-zenoh-router-zid-pinning-and-source-provenance.md), [zenoh-capability-adoption.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/zenoh-capability-adoption.md), [`../adr/0844-zenoh-deployment-topology-and-acl-v1.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0844-zenoh-deployment-topology-and-acl-v1.md).

---

## 11. PQC / FIPS posture

### 11.1 Two distinct PQ paths — not interchangeable

**Choice:** (1) **Intra-mesh real-PQ** via Rosenpass hybrid rekey of WireGuard session keys — not CMVP-validated, not a FIPS claim, tracked as Block 19. (2) **Cross-boundary FIPS PQC** via x86 boundary node with strongSwan + wolfSSL/AWS-LC FIPS + ML-KEM.

**Vanilla:** Standard WireGuard session keys (X25519), no PQC, no boundary node.

**Why:** Different threat models. Real-PQ today (harvest-now-decrypt-later resistance) cannot wait for CMVP. FIPS posture is required for cross-boundary partner traffic.

**Read more:** fips-pqc-path.md, waivers/wireguard-fips-validation.md.

---

## 12. Architectural disciplines

### 12.1 Phoenix-native peer discipline (Block 20)

**Choice:** Every peer class self-attests via persistent cryptographic identity, declares its role via Zenoh key expressions, discovers collaborators via capability-based addressing, and runs supply-chain-delivered code. Optional operational practice: scheduled teardown + rebuild cadence (per-site operator choice).

**Vanilla:** Bespoke auth setup, hardcoded discovery, per-peer integration modules, mediating config files.

**Why:** Eliminates the accumulated cruft that blocks full-system rebuild. The discipline is strictly stronger than the practice — phoenix-native peers are operationally resilient regardless of whether rebuilds are ever scheduled.

**Read more:** [phoenix-architecture.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/phoenix-architecture.md).

### 12.2 Shim pattern absorbs vendor cruft into one-per-class stateless bridges

**Choice:** Five conventions codified for shim implementations (TAK ↔ Zenoh is the reference implementation in Block 20D). Per-shim review checklist, anti-patterns documented.

**Vanilla:** Direct application-to-vendor integrations that propagate vendor coupling throughout the codebase.

**Why:** Vendor coupling has a way of metastasizing. Stateless shims contain the blast radius of any one vendor's design choices.

**Read more:** shim-pattern.md.

### 12.3 ADRs are the single source of truth for "why"

**Choice:** Every load-bearing decision lands as an ADR in `docs/adr/`. Three audiences per ADR (technical contributor, layperson sponsor, SCA-R). ADRs supersede embedded-decision-in-design-doc patterns.

**Vanilla:** Decisions live in commit messages, PR descriptions, or in someone's head.

**Why:** Procurement resilience — if the team turns over, the ADR series carries the rationale. Also an auditor-readable submission artifact.

**Read more:** [adr/INDEX.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), [adr/0000-why-adrs-and-procurement-resilience.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0000-why-adrs-and-procurement-resilience.md), [adr/0005-decision-log-vs-design-doc.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0005-decision-log-vs-design-doc.md).

### 12.4 Trunk-based, PR-gated, signed-commit git workflow

**Choice:** Branch off `main`, PR, automated tests, ≥1 review, then merge. No direct pushes to `main`. Commits cryptographically signed.

**Vanilla:** Anything from "push straight to main" through "GitFlow long-lived branches."

**Why:** Code provenance + change control are auditor expectations and a procurement-resilience requirement.

**Read more:** [adr/0109-git-collaboration-trunk-based.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md).

### 12.5 We write more original software than the original posture suggested

**Choice:** We maintain ~14 first-party binaries (Go + Rust) on top of the OSS substrate. As of this writing they group as:

- **Data plane / wire path** — [goat-relay-protocol/](https://github.com/usareur-af/goatcore/tree/main/goat-relay-protocol), [goat-relay/](https://github.com/usareur-af/goatcore/tree/main/goat-relay) (Rust; Block 33 clean-room relay).
- **Identity & enrollment** — [signal-server/](https://github.com/usareur-af/goatcore/tree/main/signal-server) (federated signal RPC), [ops/enrollment/](https://github.com/usareur-af/goatcore/tree/main/ops/enrollment) (offline-CA + bundle tooling), [ops/mgmt-host-bootstrap/](https://github.com/usareur-af/goatcore/tree/main/ops/mgmt-host-bootstrap) (sovereign account/key seed).
- **Observability / fleet health** — [ops/snitch/](https://github.com/usareur-af/goatcore/tree/main/ops/snitch), [ops/admit-audit/](https://github.com/usareur-af/goatcore/tree/main/ops/admit-audit), ops/gatewatch/, [ops/time-hygiene/](https://github.com/usareur-af/goatcore/tree/main/ops/time-hygiene) (NTP health agent + admit sidecar), [ops/signal-federation-probe/](https://github.com/usareur-af/goatcore/tree/main/ops/signal-federation-probe), zenoh-plugins/audit-logger/ (Rust).
- **Hosted apps** — ops/serve/demogame/.
- **Operator / dev tooling** — [ops/smoketest/](https://github.com/usareur-af/goatcore/tree/main/ops/smoketest), ops/secwatch/, ops/work/ (concurrency-governance CLI).

**Vanilla:** Deploy upstream Netbird + supporting OSS as-is, with only Ansible / Terraform / Compose glue authored in-repo. The original posture in tech-strategy.md §"Stay focused on the network" was *"if it rides on the mesh, don't build it ourselves"*; ha-multi-site.md committed to *"exactly TWO sanctioned upstream Netbird modifications, no more."*

**Why:** That posture covers apps and upstream-Netbird forking. It does not cover the gap between vanilla-upstream's surface and what a sovereign multi-site mesh actually needs. Concretely: upstream has no federated signal-server, no offline-enrollment path, no fleet-health telemetry surface, no NTP-quality admit guard, no admit-audit sidecar, no Zenoh interceptors, and the Go relay is below the data-plane envelope F-017 measured. Each binary above closes one of those gaps; collectively they're the substrate code, not apps that ride on the mesh — so they don't violate the "mesh-not-apps" rule, but they do contradict any reading of "we'll only do configuration work."

**Snapshot caveat:** This list will go stale. The live source of truth is `find . -name go.mod -o -name Cargo.toml -not -path '*/target/*' -not -path '*/vendor/*'` (and the workspace members in the repo-root `Cargo.toml`). Treat the list above as the shape as of the entry date; trust the filesystem for current state. The categories and the "why we wrote it" reasoning age slower than the file list.

**Read more:** Each binary's own `README.md` / package doc gives the per-component "what it does + what gap it closes." The category framing lives here.

---

## How this doc evolves

When a new bespoke choice lands (new ADR moves to *Accepted*, new architectural pattern is adopted, new compliance posture is taken), add an entry here in the same PR. Conversely, if we ever converge back to a vanilla default, remove the entry.

The shape of an entry is fixed — Choice / Vanilla / Why / Read more. Keep entries tight; depth lives in the linked design doc or ADR.

## Where to start reading

If you have time for three docs, read in this order:

1. collaborator-overview.md — shareable end-state architecture and sovereignty split.
2. architecture.md — detailed architecture, diagrams, phase plan.
3. [wireguard-netbird-primer.md](wireguard-netbird-primer.md) — what WG / Netbird actually do under the hood.

After those, follow the "Read more" links above based on the area you're working in.
