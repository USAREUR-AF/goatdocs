# Mesh Overlay Technology Comparison

Evaluation of self-hostable zero-trust overlay networking technologies for tactical deployment. Every technology is assessed against the same criteria derived from operational requirements: offline survivability, server dependency, crypto hardening path, NAT traversal, resource footprint, and identity model.

## Evaluation Criteria

| # | Criterion | Why it matters |
|---|---|---|
| 1 | **Self-hostable** | No SaaS dependency. Entire control plane runs on operator hardware. |
| 2 | **Island Mode** | Mesh operates with zero internet. Existing connections survive. New peers can enroll locally. |
| 3 | **Post-provisioning server dependency** | Can peers operate indefinitely without checking in to a management server? |
| 4 | **NAT traversal** | STUN/TURN/hole punching. Works behind CGNAT and satellite-terminal NAT. |
| 5 | **FIPS / PQC path** | Can the crypto layer be swapped to FIPS 140-3 validated modules? Is there a post-quantum migration path? |
| 6 | **Footprint** | Binary size, memory, CPU. Must run on RPi 5 (arm64, 8GB) and AGX Orin. |
| 7 | **Identity model** | How peers authenticate. Certificates, keys, OIDC, setup keys. |
| 8 | **Tunnel protocol** | WireGuard (kernel), Noise (userspace), custom, or other. |
| 9 | **Relay capability** | Built-in relay for peers that can't hole-punch. |
| 10 | **Policy model** | How access rules are defined and distributed. Runtime (server push) vs build-time (baked in). |
| 11 | **DPI resistance** | Can the protocol be fingerprinted? Is obfuscation available? |
| 12 | **Maturity** | Production use, community size, maintenance cadence. |
| 13 | **HA / clustering** | Does the management plane support native clustering, documented failover, or at minimum not obstruct standard HA patterns? Mature server software either clusters natively or documents the HA path. Gating HA behind an enterprise license or leaving it undocumented forces operators to roll unsupported failover — unacceptable for tactical deployment. |

---

## Quick Verdict

| Technology | Role in goat | Status |
|---|---|---|
| **Netbird** | Primary mesh | In use — production with HA failover |
| **Nebula** | Island Mode contingency | Deferred — revisit if offline enrollment becomes a hard requirement |
| **iroh** | Longer-term candidate | Deferred — library, not shovel-ready (Phase 4+) |
| **stunmesh-go** | Supplemental NAT traversal | Deferred with Nebula |
| **WireGuard (standalone)** | Fallback / PACE Contingency | Pre-shared bootstrap (Block 2C) |
| **IPsec (IKEv2 / strongSwan)** | Cross-boundary FIPS layer, not the mesh | In design — boundary node (ADR 0601) |
| **ZeroTier** | Considered, not selected | Dropped — procurement burden, vendor moving away from self-hosting |
| **Headscale** | Considered, not selected | Ruled out |
| **OpenZiti** | Considered, not selected | Ruled out |
| **Innernet** | Considered, not selected | Ruled out |
| **Tinc** | Considered, not selected | Ruled out |
| **Yggdrasil** | Considered, not selected | Ruled out |

### Strategy Update (2026-03)

The original plan called for three overlays: Netbird (dev), ZeroTier (near-term tactical), Nebula (production). Operating experience and infrastructure investment have changed the picture:

**Netbird is now the primary mesh.** What started as a dev/admin mesh has been hardened into a production architecture: PostgreSQL backend enables streaming replication, VRRP failover with keepalived gives ~60-second local recovery, three VPS relays across three regions provide geographic redundancy, and a cloud standby covers site-loss scenarios. The HA work (see `docs/design/ha-failover.md`) directly addresses the management server SPOF that originally disqualified Netbird from production use.

**ZeroTier has been dropped.** Its original value was as a stepping stone to gain operational experience before building Nebula. That rationale no longer holds — we have deep operational experience from running Netbird. Meanwhile, ZeroTier's burdens have increased: the network controller moved to a commercial license for gov/mil use (v1.16+, 2025), the vendor is actively deprecating self-hosted root documentation, and there is no tunnel-layer forward secrecy. Adding a second overlay network with procurement friction and a deteriorating self-hosting story is not justified.

**Nebula is deferred, not abandoned.** Its architectural advantages are real — no server dependency post-provisioning, true Island Mode with offline enrollment, certificate-based identity, MIT license. These matter if we reach a phase where peers must enroll and operate with zero internet access (Phase 4 Island Mode). However, Nebula's development pace has stagnated, mobile client support is poor (iOS cannot import configs, has no relay support, no always-on VPN, no firewall rules — all critical gaps for end-user devices), and the upfront engineering cost (CA pipeline, cert distribution, per-node config generation) is significant. Revisit when Island Mode becomes a hard operational requirement.

---

## Group 1: WireGuard-Based Managed Meshes

**Netbird, Headscale (Tailscale open-source), Innernet**

All three use the kernel WireGuard module for data-plane tunnels and add a management layer on top for peer coordination, key distribution, and policy.

### Netbird

Open-source mesh VPN with self-hosted management server, signal server, relay, and STUN/TURN. Embedded IdP or external OIDC. Web dashboard for policy and peer management.

**Strengths:** Full-featured out of the box. Self-hosted with no SaaS dependency. Built-in relay and STUN. Docker-based deployment. Active development (500+ contributors). Good documentation. Uses native kernel WireGuard (not userspace) — and has done the hard eBPF work to move sockets from under WireGuard, which is the genuinely difficult engineering problem. The control plane is comparatively straightforward; the data-plane socket management is where Netbird's implementation stands out.

**Weaknesses:** Management server is single-writer (no clustering). HA is gated behind an enterprise commercial license — the open-source server has no built-in leader election, health-check failover, or clustering, and community attempts to run multiple management instances behind a load balancer report connection failures. This is the core reason Netbird cannot be the production mesh: most mature server software either clusters natively or documents the HA pattern. Netbird does neither in its open-source tier, forcing operators to roll unsupported failover around a single-writer server. Island Mode is partial — existing tunnels survive but new enrollment requires the server. gRPC management protocol breaks through HTTP proxies (Cloudflare Tunnel). Docker stack is heavy for edge nodes (~6 containers). Managed WireGuard interface (`wt0`) prevents stunmesh-go integration.

**Why it is the primary mesh:** Fastest path to a working mesh with dashboard, policy, and relay — and the HA gap that originally limited it to dev use has been addressed. PostgreSQL backend enables streaming replication, VRRP failover with keepalived provides ~60-second local recovery, three VPS relays provide geographic redundancy, and a cloud standby covers site-loss scenarios. Good mobile client support (iOS/Android). See `docs/design/ha-failover.md`.

**Remaining limitations:** Server dependency for enrollment and policy updates (mitigated by HA, not eliminated). No native offline enrollment (Island Mode). Docker overhead on constrained hardware. State reconciliation for Island Mode is unsolved.

### Headscale (open-source Tailscale control server)

Reimplements Tailscale's coordination server. Peers run the stock Tailscale client. Headscale handles key exchange, peer registration, and ACL distribution.

**Strengths:** Tailscale client is polished and well-tested. DERP relay infrastructure is robust. MagicDNS, subnet routing, exit nodes. Large user community. ACL model is expressive (JSON policy).

**Weaknesses:** Tailscale client is open-source but dual-licensed — some features require Tailscale commercial. DERP relays are Tailscale-operated by default (self-hosting possible but less documented). No built-in IdP — requires external OIDC. Headscale itself is a community project, not Tailscale-supported. Same server dependency problem as Netbird: peers need the control server for re-keying and new enrollment.

**Why not selected:** Same fundamental limitation as Netbird (server-dependent), without the built-in dashboard and embedded IdP that make Netbird faster to deploy. Tailscale client's dual licensing adds procurement complexity. No advantage over Netbird for our use case, and Netbird's self-hosted story is more complete.

### Innernet

Minimal WireGuard network manager built by Tonari (Rust). Central server stores peer list and CIDRs. Clients pull config and update WireGuard interfaces.

**Strengths:** Simple. Rust binary, small footprint. Easy to understand codebase.

**Weaknesses:** No NAT traversal (no STUN, no relay, no hole punching). No built-in identity beyond WireGuard keys. No access policy beyond CIDR-based groups. No dashboard. Designed for single-office LANs, not tactical deployment. Minimal community (maintenance slowed significantly since 2023).

**Why not selected:** No NAT traversal makes it unusable behind any CGNAT. Too minimal for tactical requirements.

### Group 1 Summary

| | Netbird | Headscale | Innernet |
|---|---|---|---|
| Self-hostable | Yes | Yes | Yes |
| Island Mode | Partial (tunnels survive, no new enrollment) | Partial (same limitation) | Partial (same limitation) |
| Server dependency | Required for enrollment + policy | Required for enrollment + re-keying | Required for peer list updates |
| NAT traversal | STUN + TURN + relay | DERP relay + STUN | None |
| FIPS path | WireGuard kernel → FIPS module swap | Same | Same |
| Footprint | Heavy (Docker stack for server) | Medium (single Go binary for server) | Light (Rust binary) |
| Identity | Embedded IdP or OIDC + setup keys | External OIDC | WireGuard keys only |
| Relay | Built-in | DERP (self-hostable) | None |
| DPI resistance | WireGuard fingerprint (AmneziaWG possible) | Same | Same |
| HA / clustering | **Enterprise-only.** Open-source is single-writer, no documented HA path. Community multi-instance attempts fail. | Single server, no clustering. DERP relays scale independently. | Single server, no clustering. |

**Bottom line:** All three share the same structural limitation — a management server must be reachable for enrollment, re-keying, and policy updates, and none offer open-source HA for that server. This is acceptable for development but disqualifying for production tactical deployment where the server may be unreachable for days and failover must be reliable.

---

## Group 2: Custom Protocol Overlays

**ZeroTier, Tinc, Yggdrasil**

These implement their own tunnel protocols rather than using WireGuard.

### ZeroTier

Peer-to-peer overlay network with a central controller for network configuration and peer authorization. Custom protocol (not WireGuard). Virtual L2 Ethernet — peers get addresses on a shared virtual switch.

**Strengths:** Easy setup (one command join). Virtual L2 means broadcast/multicast work. Built-in NAT traversal with relay fallback (root servers). Cross-platform. Self-hostable controller via API.

**Island Mode — more viable than initially assessed.** ZeroTier can operate fully disconnected from the internet if you replace the default "planet" (ZeroTier's public root servers) with a custom planet file pointing to local root servers, and self-host the network controller on the LAN. New peers can join over LAN if they have the custom planet file installed before starting ZeroTier. This requires distributing the planet file to every node at provisioning time — added friction but workable.

**Caveats on self-hosting:** ZeroTier Inc. is actively moving away from supporting self-hosted roots. Private moons are officially deprecated and no longer covered under their SLA. Documentation for custom planet/moon setup has been reduced. The community reports this path still works but the vendor trajectory is toward managed service, not self-hosted infrastructure.

**Crypto — updated assessment (v1.6+, 2020).** ZeroTier moved from Salsa20/12 to AES-GMAC-SIV (AES-256 + GMAC + CTR, audited by Trail of Bits) for symmetric encryption. Key exchange remains Curve25519. The underlying primitives are individually FIPS-certifiable (AES-256, GMAC), but ZeroTier itself has no FIPS 140-3 validated module and no roadmap for one. Forward secrecy is not implemented — the lead developer explicitly argued against it (GitHub #204, closed without implementation), recommending layering SSH/TLS on top instead.

**Application-layer crypto as mitigation.** The tunnel-level crypto gap could be addressed by enforcing FIPS-validated encryption at the application and data layers: mTLS with a FIPS-validated TLS library (e.g., AWS-LC, BoringSSL) for all service-to-service traffic, FIPS-validated data-at-rest encryption on each node. This is a defense-in-depth argument — the tunnel provides confidentiality using strong (but uncertified) crypto, while compliance obligations are met at the application layer where FIPS modules are mature and available. This approach adds implementation complexity but is a legitimate architecture pattern.

**Burdens and concerns** (to be weighed against ZeroTier's ease of deployment and operational simplicity):

- **License (v1.16+, 2025).** The network controller moved to a Commercial Source-Available License. Gov/mil use requires a commercial license from ZeroTier Inc. Client code is MPL-2.0 (open source), but self-hosting the controller requires procurement. Default builds no longer include the controller — requires `make ZT_NONFREE=1`. Not a technical barrier — government buys commercial software routinely — but adds procurement timeline and cost that don't exist with MIT-licensed Nebula.
- **No forward secrecy at tunnel layer.** Compromise of a node's static key exposes past captured tunnel traffic. Mitigatable: if all services use TLS 1.3 (ephemeral keys, forward secrecy), the tunnel-layer gap reduces to metadata exposure (who talks to whom, when, volume). Payload stays protected. Defense in depth prefers forward secrecy at every layer, but this is a gap you can engineer around, not a disqualifier. ZSSP (post-quantum session protocol with Kyber1024) exists in a separate repo but is unaudited and unshipped.
- **L2 emulation.** ARP, broadcast storms on large networks. We need L3 routing, not a virtual switch. Manageable at our scale but unnecessary overhead.
- **Protocol fingerprint-able.** No obfuscation equivalent to AmneziaWG.
- **Vendor direction on self-hosting.** Self-hosted roots are deprecated in docs but still functional. For a tactical deployment you pin the version and don't take vendor updates in the field. The MPL-2.0 client code is forkable if needed. Matters more for a 5-year platform bet than a deployment with a defined mission timeline.

**Why dropped (was: selected for near-term tactical mesh):** ZeroTier was originally selected as a stepping stone — deploy it quickly, gain operational experience, then inform the Nebula build. That rationale no longer holds. We now have deep operational experience from running Netbird, and the HA failover architecture (VRRP + Postgres replication) addresses the availability concerns that motivated looking beyond Netbird in the first place. Meanwhile, ZeroTier's burdens have increased: the controller license went commercial for gov/mil (v1.16+, 2025), the vendor is deprecating self-hosted root documentation, and there is no tunnel-layer forward secrecy. Adding a second overlay network with procurement friction and a deteriorating self-hosting story provides no value that the current Netbird deployment doesn't already deliver.

### Tinc

Long-running (since 1998) mesh VPN. Automatic full-mesh topology. Custom protocol. Supports relaying through intermediate nodes.

**Strengths:** Fully decentralized after initial config exchange. Automatic mesh routing — any node can relay for any other. Proven stability (25+ years). No management server needed post-setup.

**Weaknesses:** Custom crypto (RSA + legacy ciphers in 1.0; 1.1 pre-release has modern crypto but has been in beta since 2013). No FIPS path. No built-in NAT traversal (requires port forwarding or manual relay). No identity model beyond RSA keys and host files. No policy engine. No dashboard. Development is effectively stalled (1.1 never shipped stable). Not suitable for modern hardened deployments.

**Why not selected:** Stalled development, legacy crypto, no NAT traversal, no FIPS path. Does not meet any modern security requirement.

### Yggdrasil

Experimental encrypted IPv6 overlay network. Fully decentralized — no servers, no coordinators. DHT-based routing. Addresses derived from ed25519 public keys.

**Strengths:** Truly serverless — no infrastructure at all. Self-organizing topology. Any node can reach any other if there's a path. Interesting research project for mesh routing algorithms.

**Weaknesses:** Experimental (developers explicitly state "do not rely on this for production"). No access control (any Yggdrasil node can reach any other). No policy model. Custom protocol with no FIPS path. No relay infrastructure (relies on mesh connectivity). IPv6-only overlay complicates integration with IPv4 services. Performance unpredictable on large networks. No identity model beyond key-derived addresses.

**Why not selected:** Experimental, no access control, no policy, no FIPS path. Cannot enforce who talks to whom — every node is reachable by every other node. Fundamentally incompatible with zero-trust.

### Group 2 Summary

| | ZeroTier | Tinc | Yggdrasil |
|---|---|---|---|
| Self-hostable | Yes (custom planet + controller), but controller requires commercial license for gov/mil | Yes | Yes (no server needed) |
| Island Mode | Yes (custom planet + local controller + planet file distribution) | Yes (after initial config) | Yes (fully decentralized) |
| Server dependency | Controller for auth; custom planet roots for discovery (both self-hostable) | None post-setup | None |
| NAT traversal | Built-in (root-mediated) | None | None (mesh routing only) |
| FIPS path | **No certified module** (AES-GMAC-SIV uses FIPS primitives; app-layer mitigation viable) | **No** (legacy crypto) | **No** (custom crypto) |
| Footprint | Medium (~30 MB) | Light (~1 MB) | Light (~10 MB) |
| Identity | Network ID + node ID | RSA keys + host files | ed25519-derived IPv6 |
| Access control | Network-level (join/deny) | None | **None** |
| DPI resistance | Fingerprint-able | Fingerprint-able | Fingerprint-able |
| HA / clustering | Controller is a single process, but state is lightweight JSON — standard DB replication or cold standby is straightforward. No native clustering. | N/A (no server) | N/A (no server) |

**Bottom line:** All three use custom crypto with no FIPS-validated module at the tunnel layer. Tinc is effectively abandoned. Yggdrasil has no access control. ZeroTier is the strongest of this group — island mode is achievable, crypto uses FIPS-compatible primitives (AES-256, GMAC), and application-layer FIPS encryption could address compliance. However, the commercial controller license, lack of forward secrecy, and vendor direction away from self-hosting are significant concerns.

---

## Group 3: Noise Protocol / Userspace Mesh

**Nebula**

### Nebula

Open-source overlay network created by Slack. Uses Noise Protocol framework in userspace. Certificate-based identity with group memberships and firewall rules embedded in certificates. Optional lighthouse for peer discovery. Single static binary per node.

**Strengths:**
- **No management server post-provisioning.** Certificates carry all identity, group membership, and policy. Once a node has its cert and config, it never needs to phone home.
- **Native Island Mode.** Peers authenticate by certificate. No server check-in required. Mesh operates fully offline.
- **Single binary, ~15 MB.** No Docker, no database, no dashboard runtime dependency.
- **Certificate-based policy.** Groups and firewall rules are embedded at build time. No runtime policy server.
- **Lighthouse is optional.** Helps with peer discovery but is not required — peers can be configured with static endpoints or discover each other via DNS (stunmesh-go).
- **Noise Protocol.** Modern, audited, well-understood crypto framework.
- **Used in production at Slack** for years before being open-sourced. Active community.

**Weaknesses:**
- **No runtime policy changes.** Firewall rules are in certificates — changing policy means re-issuing certs. Acceptable for tactical (policy is fixed per mission) but limiting for enterprise.
- **No built-in dashboard.** Command-line only. (Acceptable for tactical; operators don't need a GUI in the field.)
- **Noise Protocol is userspace** — not FIPS-validated. However, the crypto primitives (Curve25519, ChaCha20-Poly1305) are the same as WireGuard, and a FIPS kernel module could wrap the tunnel at the transport layer.
- **No built-in relay.** If two peers can't hole-punch, they need an intermediary Nebula node (any node can relay, but it must be reachable by both peers).
- **Certificate management is manual.** No automated CA rotation or cert distribution — must be built into the provisioning pipeline (`build.sh`).
- **Mobile client support is poor.** The iOS client cannot import configurations (must be entered manually), does not support firewall rules (GitHub #61), does not support relay servers (#146), and has no always-on VPN (#49). Certificate enrollment on mobile requires manually exporting public keys, signing them externally, and uploading — unworkable for end-user devices. These are not edge cases; they are fundamental gaps for any deployment with mobile peers.
- **Development pace has stagnated.** Four years after open-sourcing, basic features present in competitors (centralized config, usable mobile clients, built-in relay infrastructure) remain missing. The project is oriented toward large enterprises with automation expertise, not toward operational simplicity.

**Why deferred (was: selected for production):** Nebula is the only technology evaluated that meets all three hard requirements simultaneously: (1) no server dependency post-provisioning, (2) native offline operation, (3) crypto framework with a viable FIPS migration path. These advantages are real and matter for Island Mode. However, the HA failover architecture built around Netbird (VRRP + Postgres streaming replication) addresses the management server SPOF that originally drove the Nebula selection. Combined with Nebula's stagnant development, poor mobile client support, and significant upfront engineering cost (CA pipeline, cert distribution, per-node config generation), deploying Nebula is not justified unless Island Mode — specifically offline enrollment with no internet at all — becomes a hard operational requirement.

### stunmesh-go (supplemental)

Not a mesh overlay. A NAT traversal helper that publishes encrypted STUN-discovered endpoints to DNS TXT records, enabling peers to find each other's external addresses without a coordination server.

**Why paired with Nebula:** Nebula's lighthouse handles peer discovery, but stunmesh-go adds a DNS-based discovery layer for transports where STUN alone isn't sufficient. It manages standalone WireGuard interfaces — incompatible with Netbird's managed `wt0` interface, but works with Nebula where the interface is user-controlled.

---

## Group 4: Zero-Trust SDK Platform

**OpenZiti**

### OpenZiti

Full zero-trust networking platform by NetFoundry. Not just a mesh overlay — it's an application-embedded SDK that moves networking into the application layer. Includes its own controller, edge routers, fabric routers, and client SDKs.

**Strengths:** True application-embedded zero trust — services are invisible to the network. No listening ports. Strong identity model (x509 certificates, enrollment tokens). Sophisticated policy engine. Built-in smart routing through a fabric of routers.

**Weaknesses:**
- **Extreme complexity.** Minimum deployment requires a controller, at least one edge router, and SDK integration into every application. This is an enterprise platform, not a tactical tool.
- **Custom protocol** (not WireGuard, not Noise). No FIPS-validated crypto module available.
- **Heavy footprint.** Controller + router + SDK per app. Not viable on RPi.
- **Application integration required.** Every service must embed the OpenZiti SDK or use a tunneler. Cannot transparently overlay existing applications.
- **Small community** relative to WireGuard-based tools. NetFoundry commercial backing, but open-source adoption is limited.
- **No Island Mode path.** Controller is required for all operations.

**Why not selected:** Complexity and footprint are disqualifying. Requires SDK integration into every application — we need transparent overlay, not application rewrites. Custom protocol with no FIPS path. Controller dependency eliminates Island Mode.

---

## Group 5: Content-Addressed Connectivity

**iroh**

### iroh

Rust library (by n0/Number Zero) for direct connections between nodes. Uses QUIC for transport and NAT traversal inspired by Tailscale's DERP protocol. Content-addressed data sync. ed25519 identity.

**Strengths:** Modern Rust implementation. Excellent NAT traversal (QUIC hole punching + relay fallback). Content-addressed data model fits tactical sync use cases (mission data, config distribution, partial sync over intermittent links). Small, embeddable library. Active development with strong engineering team.

**Why it's promising for later phases:**

- Content-addressed sync is a natural fit for distributing certificates, configs, and mission data across a mesh — exactly the problem we need to solve for Nebula certificate rotation and Island Mode provisioning.
- QUIC transport with relay fallback handles the NAT traversal problem elegantly.
- Embeddable Rust library means it could be integrated into our provisioning tooling rather than requiring a separate daemon.
- The connectivity primitives (direct connections, relay fallback, discovery) could supplement Nebula's lighthouse for peer discovery in complex network topologies.

**Why deferred (not shovel-ready):**

- **It is a library, not a mesh overlay.** Does not create network interfaces or route IP traffic. It provides application-level connectivity primitives that developers build on top of. Standing up a tactical net in one to two weeks requires a turnkey mesh, not building one from components.
- **No access control or policy engine.** Application must implement its own authorization.
- **QUIC-based** — not WireGuard or Noise. No FIPS validation path for the tunnel protocol (same app-layer mitigation argument as ZeroTier applies here).
- **API is still evolving.** Not yet stable enough for production infrastructure dependencies.
- **Relay servers required for initial discovery.** Self-hostable, but adds infrastructure.

**Bottom line:** Wrong tool for Phase 1-3 where we need a working mesh now. Right tool to watch for Phase 4+ where we need to solve data sync, certificate distribution, and offline provisioning at the application layer. The library approach becomes an advantage once we have a running mesh and need to build smart tooling on top of it.

---

## Standalone WireGuard

Not a mesh technology — included because a raw WireGuard tunnel to a known peer is the transport layer inside the PACE Contingency fallback (Block 2C: offline enrollment bundles). The bundle format carries this static WG config as one field, wrapped in a signed capability that lets any reachable management server auto-provision the peer without an operator-issued setup key. See [`docs/design/offline-enrollment.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/offline-enrollment.md).

**Role:** Static point-to-point tunnels derived from a CBOR bundle signed by the offline CA. The bundle is baked into the boot image via Ubuntu cloud-init (on both x86 and Orin) or delivered on a USB for air-gapped provisioning. No dependency on the management server being reachable at enrollment time — a validator sidecar on any reachable management host handles auto-provisioning.

**Strengths:** Zero dependencies. Kernel-level. FIPS path via kernel crypto module swap. Survives anything.

**Weaknesses:** No mesh — just point-to-point. No dynamic peer discovery. Manual key management. Does not scale beyond a handful of pre-configured peers.

**Role in PACE:** Emergency connectivity when all overlay technologies are unavailable.

---

## IPsec (IKEv2 / strongSwan)

Not a mesh technology — included because IPsec is the incumbent VPN standard this architecture is most often measured against, and because the verdict is not a rejection. IPsec is deliberately used where it is strongest: the boundary node terminates IKEv2/IPsec with a FIPS-validated module for cross-boundary and inter-site traffic ([ADR 0601](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0601-fips-pqc-boundary-node.md), `docs/design/fips-pqc-path.md`), while WireGuard carries the intra-mesh data plane under a documented waiver (ADR 0854). This is the crypto-boundary-discipline split ([ADR 0103](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0103-crypto-boundary-discipline.md)): each protocol where its properties are required, neither universal. The question this section answers is why IPsec is not the *mesh data plane*.

**What it is:** A protocol suite, not a product — ESP for the encrypted tunnel, IKEv2 for key exchange and SA negotiation. strongSwan is the open-source implementation we use. It is the most widely deployed site-to-site VPN technology in government and enterprise networks.

### Where IPsec beats the WireGuard approach

- **FIPS validation exists today.** strongSwan can be built against a FIPS 140-3 validated crypto module, and commercial IPsec gateways carry validations. WireGuard's ciphers (ChaCha20-Poly1305, BLAKE2s) are outside the validated set, hence the ADR 0854 waiver. For any flow where FIPS validation is mandatory rather than waivable, IPsec is the answer — which is exactly the boundary-node role.
- **PQC path is ahead.** IKEv2 supports hybrid post-quantum key exchange via multiple key exchanges (RFC 9370); strongSwan 6.x ships ML-KEM (`ke1_mlkem768`). This is the FIPS-track PQC mechanism in `fips-pqc-path.md`. WireGuard's PQ posture is the Rosenpass pre-shared-key wrap (ADR 0602) — commercial-grade, not a FIPS claim.
- **Universal interop.** Every partner, coalition, and government gateway speaks IKEv2. Peering with an external organization's existing infrastructure requires no agent install and no shared mesh stack — the boundary node speaks the protocol they already run.

### Why it is not the mesh data plane

- **No mesh layer.** IPsec defines pairwise tunnels and nothing above them: no peer discovery, no key distribution, no policy engine, no roster. A full mesh of N peers means on the order of N² tunnel configurations, each with its own SA negotiation and credential pairing. At the scope envelope (100–1000 peers per site), that is operationally unmanageable without a controller — and the controllers that manage IPsec meshes at scale are the proprietary SD-WAN platforms rejected in the next section. WireGuard has the same gap at the protocol level, which is why the comparison above is between *managed WireGuard meshes* and raw IPsec: the WireGuard ecosystem produced open-source, self-hostable management layers (Netbird, Headscale); the IPsec ecosystem produced vendor appliances.
- **Negotiation is attack surface.** IKE negotiates ciphers, modes, and parameters, which creates the downgrade-attack and misconfiguration class of vulnerabilities that has dominated IPsec's CVE history. WireGuard has no negotiation — one cipher suite, both sides, always.
- **Code size.** strongSwan is roughly 500,000 lines; the WireGuard kernel module is roughly 4,000. Smaller surface to audit, fewer places for bugs.
- **Probe response.** IKE on UDP 500/4500 answers unauthenticated probes, and the responses are detailed enough to fingerprint vendor and version. WireGuard silently drops unauthenticated packets — a node looks like a dead IP to a scanner. For tactical emissions discipline this difference matters.
- **NAT traversal is encapsulation, not coordination.** IPsec NAT-T (UDP 4500) lets a tunnel cross a NAT, but there is no discovery or hole-punching machinery — when both peers sit behind CGNAT (the common satellite-terminal case), one side must still be publicly addressable. The managed mesh solves this with STUN, coordinated hole-punching, and relay fallback.
- **Roaming.** WireGuard sessions float across IP changes natively — a peer that moves networks keeps its tunnel. IPsec needs MOBIKE (RFC 4555), which is unevenly implemented across clients and gateways.

### Division of labor

| Flow | Protocol | Why |
|---|---|---|
| Intra-mesh peer-to-peer | WireGuard (Netbird-managed) | Mesh coordination, NAT traversal, roaming, silence, small surface; FIPS gap carried as ADR 0854 waiver |
| Inter-site / cross-boundary | IPsec IKEv2 (strongSwan, boundary node) | FIPS-validated module mandatory; ML-KEM hybrid KEX; partner interop |

---

## Why Proprietary ZTOL / SASE Vendors Were Not Evaluated

Juniper (Session Smart Router, Mist), Zscaler (ZPA), Palo Alto (Prisma Access), Cisco (SD-WAN, Meraki), Fortinet (FortiSASE), and similar commercial ZTOL/SASE platforms were excluded from this evaluation. Not because they lack features — many are technically sophisticated — but because they fail structurally at the requirements level in ways that no feature set can compensate for.

### The vendor is not in the fight

Every technology in this evaluation can be deployed, operated, diagnosed, and fixed by the team that uses it. Proprietary ZTOL vendors deliver a product and leave. Their engineering team is not on your network when it breaks at 0200 in a denied environment. Their support portal is not reachable when the internet is down. Their escalation path assumes connectivity to their cloud, access to their ticketing system, and response times measured in business days.

When a self-hosted mesh breaks, you read the logs, read the source, and fix it. When a vendor mesh breaks, you file a ticket and wait. In a tactical environment, waiting is not an option.

### Their control plane must be the sole authority

Every proprietary ZTOL platform requires that its control plane be the authoritative decision-maker for all network access. This is not a configuration choice — it is the architecture. Zscaler routes all traffic through its cloud for inspection. Palo Alto's Prisma Access brokers every connection. Juniper's Mist requires cloud-managed policies. The platform does not participate in your network — it *becomes* your network.

The consequence: any time the vendor's control plane is unreachable, disagrees with your routing, or enforces a policy you did not anticipate, your network segments. You do not control the decision. The vendor does — from a cloud data center that has no awareness of your operational context.

This is the inverse of the design principle that drives this project. A tactical mesh must run itself at the edge. The cloud helps it find itself (enrollment, key exchange, initial configuration). After that, the mesh operates autonomously. Proprietary ZTOL inverts this: the cloud doesn't help — the cloud *is* the mesh. Remove it and the mesh dies.

### No disconnected operation

Every ZTOL/SASE vendor assumes persistent cloud connectivity. Some offer "local breakout" or "private service edge" modes, but these are degraded states — reduced policy enforcement, no new connections, no re-authentication. None support the operational model this project requires: full mesh operation, including new peer enrollment, with zero internet access for days or weeks.

This alone is disqualifying. A technology that stops working when the internet goes down cannot be the foundation of a tactical data fabric designed to operate in denied, degraded, intermittent, and limited (DDIL) environments.

### No federation, no interoperability

If your network runs Zscaler and a partner's network runs Palo Alto, the two cannot peer. One must place the other's agent inside its network, subordinating its own security model. There is no standard federation protocol between ZTNA vendors, no equivalent of BGP peering. Each vendor's network is a walled garden.

In coalition or joint operations, this means every organization must adopt the same vendor — or one organization must cede control of its network security to another organization's vendor. Neither is acceptable.

Open-source mesh overlays do not have this problem. WireGuard speaks WireGuard. IP routes to IP. Two organizations running different mesh overlays can still route traffic between them because the tunnel layer produces standard interfaces on standard protocols.

### You cannot audit what you cannot read

When a ZTOL vendor claims FIPS 140-3 compliance, you trust their certification. You cannot verify that the validated crypto module is in the actual code path for your traffic. You cannot audit for backdoors, side channels, or supply chain compromises. History says this matters: Juniper ScreenOS had an unauthorized backdoor for years (2015 disclosure). Cisco's ArcaneDoor campaign exploited ASA/FTD zero-days. SolarWinds' build pipeline was compromised for months. These were not hypothetical risks — they were operational realities in products used by governments worldwide.

With open-source, you can run static analysis, fuzz testing, and formal verification on every component. You can verify the FIPS crypto code path yourself. The security posture is auditable, not asserted.

### Vendor risk compounds over time

Licensing changes (ZeroTier's controller going commercial is a mild example — enterprise ZTOL licenses cost $50-$200/user/year), acquisitions (Juniper acquired by HPE, VMware by Broadcom — both resulted in product direction changes), feature deprecation, and end-of-life decisions are all risks you absorb but do not control. A 5-year tactical program built on a vendor platform is a bet that the vendor's business decisions will remain aligned with your operational needs for the entire program. That bet has a poor track record.

### Summary

Proprietary ZTOL/SASE platforms are designed for enterprise networks with reliable internet, centralized IT, and a single organizational boundary. They solve a real problem in that context. They do not solve the problem this project addresses: a self-healing, identity-based mesh that uses the cloud to find itself and the tactical edge to run itself. The structural dependency on a vendor's cloud control plane, the inability to operate disconnected, the lack of federation, and the opacity of the implementation are not feature gaps that a future release will fix. They are architectural choices that are fundamentally incompatible with tactical deployment.

For a detailed comparison of open-source vs proprietary approaches to the broader tactical data fabric problem, see Open-Source vs Proprietary Tactical Data Fabric.

---

## Full Comparison Matrix

| | Netbird | Headscale | Nebula | ZeroTier | OpenZiti | iroh | Innernet | Tinc | Yggdrasil |
|---|---|---|---|---|---|---|---|---|---|
| **Self-hostable** | Yes | Yes | Yes | Yes (custom planet + controller; controller requires commercial license for gov/mil) | Yes | N/A (library) | Yes | Yes | Yes (serverless) |
| **Island Mode** | Partial | Partial | **Native** | Yes (custom planet + local controller) | No | N/A | Partial | Yes | Yes |
| **Server-free post-provision** | No | No | **Yes** | No (controller needed for auth) | No | N/A | No | Yes | Yes |
| **NAT traversal** | STUN+TURN+relay | DERP+STUN | STUN+lighthouse | Root-mediated | Fabric routers | QUIC+relay | None | None | Mesh routing |
| **FIPS path** | Yes (WG kernel) | Yes (WG kernel) | Viable (Noise primitives) | No certified module (FIPS primitives; app-layer mitigation viable) | **No** | **No** (app-layer mitigation viable) | Yes (WG kernel) | **No** | **No** |
| **PQC path** | PSK rotation | PSK rotation | PSK rotation | ZSSP (unshipped, unaudited) | **None** | **None** | PSK rotation | **None** | **None** |
| **Footprint** | Heavy (Docker) | Medium | **Light (~15 MB)** | Medium | Heavy | Light | Light | Light | Light |
| **Identity** | IdP + setup keys | OIDC | **X.509 certs** | Network+node ID | X.509 | ed25519 | WG keys | RSA keys | ed25519 |
| **Tunnel protocol** | WireGuard (kernel) | WireGuard (kernel) | Noise (userspace) | Custom (AES-GMAC-SIV + Curve25519) | Custom | QUIC | WireGuard (kernel) | Custom | Custom |
| **Built-in relay** | Yes | DERP | Any node can relay | Root servers | Fabric routers | Yes | No | Any node | Mesh relay |
| **Policy model** | Runtime (dashboard) | Runtime (ACL JSON) | **Build-time (certs)** | Network-level | Runtime (controller) | None | CIDR groups | None | **None** |
| **DPI resistance** | AmneziaWG option | AmneziaWG option | Noise fingerprint | Fingerprint-able | Fingerprint-able | QUIC (common) | AmneziaWG option | Fingerprint-able | Fingerprint-able |
| **Access control** | Group + policy rules | ACL tags + rules | Cert groups + FW rules | Join/deny | SDK-enforced | None (app layer) | CIDR-based | None | **None** |
| **License** | BSD-3 | BSD-3 | MIT | MPL-2.0 (client) / Commercial (controller) | Apache 2.0 | Apache/MIT | MIT | GPL-2.0 | LGPL-3.0 |
| **Active development** | Yes (high) | Yes (medium) | Yes (medium) | Yes (medium) | Yes (low-medium) | Yes (high) | Slowed | Stalled | Experimental |
| **HA / clustering** | **Enterprise-only** (open-source single-writer, no documented HA) | Single server, no clustering | **N/A** (no server post-provisioning) | Single controller, standard replication viable | Controller required, no documented HA | N/A (library) | Single server, no clustering | N/A (no server) | N/A (no server) |

---

## Decision Logic

Three requirements are hard gates. Fail any one and the technology is eliminated:

```
1. FIPS crypto path exists (tunnel-layer or viable app-layer mitigation)?
   NO  → Eliminated (OpenZiti, Tinc, Yggdrasil)
   PARTIAL (app-layer only) → Flag as risk, continue (ZeroTier, iroh)
   YES → Continue (Netbird, Headscale, Innernet, Nebula)

2. Operates without management server post-provisioning?
   NO  → Acceptable if HA mitigates the SPOF (Netbird, Headscale, Innernet)
   YES → Continue (Nebula, ZeroTier with custom planet)

3. Native Island Mode (offline enrollment + operation)?
   NO  → Acceptable if not yet an operational requirement
   YES → Candidate for Island Mode phases (Nebula, ZeroTier)
```

**Updated assessment (2026-03):** The original gate logic assumed that server dependency (gate 2) and lack of Island Mode (gate 3) were disqualifying for production. Operating experience has shown that gate 2 can be addressed with HA engineering (VRRP failover, Postgres replication, multi-region relays), and gate 3 is not yet an operational requirement. This changes the calculus.

**Netbird** passes gate 1 and now addresses gate 2 through HA failover architecture. Provides dashboard, policy management, built-in relay, and good mobile client support. Selected as the primary mesh.

**Nebula** passes all three gates cleanly on paper. However, practical concerns have emerged: stagnant development pace, poor mobile client support (iOS cannot import configs, no relay, no always-on VPN, no firewall rules), and significant upfront engineering cost. Deferred — revisit when Island Mode (gate 3) becomes a hard operational requirement.

**ZeroTier** passes gates 2 and 3 with configuration effort, but the commercial controller license (v1.16+), vendor deprecation of self-hosted roots, and lack of forward secrecy add procurement and operational burdens. Dropped — no value over Netbird with HA.

**iroh** is deferred — it is a library, not a turnkey mesh. Promising for later phases (data sync, certificate distribution, provisioning tooling) but not shovel-ready for standing up a tactical net in one to two weeks.

---

## Common Questions

**"Why not Tailscale/Headscale? It's the most popular."**
Same structural limitation as Netbird: peers depend on the control server for re-keying and enrollment. Tailscale's client is dual-licensed, adding procurement complexity. No advantage over Netbird for self-hosted tactical use — and Netbird's HA failover architecture (VRRP + Postgres replication) now mitigates the server dependency concern that all WireGuard-managed meshes share.

**"Why not ZeroTier? It's simpler."**
Was considered and initially selected as a near-term tactical mesh. Dropped in 2026-03. The original value was as a stepping stone to gain operational experience before building Nebula — that rationale no longer holds given deep operational experience from running Netbird. Meanwhile, the network controller moved to a commercial license for gov/mil use (v1.16+, 2025), the vendor is actively deprecating self-hosted root documentation, and there is no tunnel-layer forward secrecy. These burdens add procurement friction and vendor risk with no compensating value that Netbird doesn't already provide.

**"Why not OpenZiti? It's true zero trust."**
Correct — it is architecturally the most zero-trust option. But it requires SDK integration into every application, a controller for all operations, and uses custom crypto with no FIPS path. The complexity and footprint are orders of magnitude beyond what fits on tactical hardware. Designed for enterprise data centers, not field deployment on RPis.

**"Why not iroh? It's modern and Rust."**
iroh is a connectivity library, not a mesh overlay — it does not create network interfaces or route IP traffic. That makes it wrong for standing up a tactical net in one to two weeks. But it is promising for later phases: content-addressed sync fits certificate distribution, mission data, and offline provisioning. The library approach becomes an advantage once we have a running mesh and need smart tooling on top of it. Deferred to Phase 4+, not ruled out.

**"Why not IPsec? It's the FIPS-validated government standard."**
We use it — at the boundary. The boundary node terminates IKEv2/IPsec with a FIPS-validated module for cross-boundary and inter-site flows (ADR 0601), and IKEv2's ML-KEM hybrid key exchange is our FIPS-track PQC mechanism. What IPsec cannot be is the intra-mesh data plane: it has no peer discovery, no key distribution, and no policy layer, so a full mesh means N² hand-managed tunnel configs — and the controllers that solve that at scale are the proprietary SD-WAN platforms ruled out below. Add the negotiation attack surface, the probe-responsive IKE daemon versus WireGuard's silent drop, and NAT-T's inability to connect two CGNAT-bound peers without a public responder, and IPsec loses the mesh role on operational grounds while keeping the boundary role on compliance grounds. See the IPsec section above for the full comparison.

**"Why not standalone WireGuard? It's the simplest."**
WireGuard provides the tunnel but not the mesh. No peer discovery, no dynamic routing, no policy distribution, no identity management beyond static keys. It's the PACE Contingency fallback (pre-shared configs baked into boot images) but cannot serve as the primary mesh technology.

**"Why not Tinc? It's been around forever."**
Development stalled (tinc 1.1 has been in beta since 2013). Legacy crypto with no FIPS path. No NAT traversal. Does not meet modern security requirements.

**"Why not Yggdrasil? It's fully decentralized."**
No access control. Any Yggdrasil node can reach any other — fundamentally incompatible with zero trust. Custom crypto with no FIPS path. Developers explicitly mark it experimental.

**"Nebula uses Noise Protocol in userspace, not kernel WireGuard. Isn't that a FIPS problem?"**
The crypto primitives are the same (Curve25519, ChaCha20-Poly1305). FIPS compliance can be achieved by: (a) replacing the userspace crypto with calls to a FIPS-validated library (e.g., AWS-LC, BoringCrypto), or (b) wrapping Nebula tunnels in a FIPS-validated kernel module at the transport layer. Both are viable engineering paths. Nebula's clean Noise implementation makes this substitution straightforward compared to technologies with custom or legacy crypto. Note: this is moot while Nebula is deferred — but the FIPS path remains viable if Nebula is revisited for Island Mode.

**"Why was Nebula deferred? It passed all three hard gates."**
On paper, yes. In practice, three concerns emerged: (1) development pace has stagnated — four years after open-sourcing, basic features present in competitors remain missing, (2) mobile client support is poor — the iOS client cannot import configurations, has no relay support, no always-on VPN, and no firewall rules, all critical gaps for end-user devices, and (3) the HA failover architecture built around Netbird addresses the management server SPOF that originally drove the Nebula selection. The upfront engineering cost (CA pipeline, cert distribution, per-node config generation) is not justified unless offline enrollment with zero internet becomes a hard operational requirement.

**"What about WireGuard obfuscation (AmneziaWG)?"**
AmneziaWG is available for WireGuard-based tools (Netbird, Headscale, Innernet, standalone WG). It randomizes handshake sizes and obfuscates headers to defeat DPI. Nebula's Noise Protocol has a different fingerprint but the same exposure — a purpose-built obfuscation layer would need to be developed or the tunnel wrapped in an obfuscation transport (VLESS+Reality, Shadowsocks-2022). This is on the roadmap (Block 5C) regardless of which mesh technology is used.
