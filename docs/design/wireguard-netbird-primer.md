# WireGuard, Netbird, and What Makes This Different

What WireGuard actually is, what Netbird does on top of it, and what about our mesh is standard versus bespoke.

## WireGuard: the protocol

WireGuard is a kernel-level network tunnel. It is not a VPN product, not a mesh network, and not a management system. It is a single primitive: given two endpoints that each hold the other's public key, establish an encrypted UDP tunnel between them. That is the entire scope of what WireGuard does.

### What WireGuard handles

**Cryptography.** Every packet is encrypted with ChaCha20-Poly1305 (or AES-256-GCM on FIPS-configured kernels). Key exchange uses Curve25519 with a Noise protocol handshake. Session keys are ephemeral and rotate automatically. There is no cipher negotiation — both sides use the same algorithms, always. This eliminates the downgrade attacks that plague IPSec and TLS-based VPNs.

**Stealth.** WireGuard silently drops any packet not signed by a known peer. No response, no ICMP rejection, no error message. To a port scanner, a WireGuard endpoint looks like a dead IP address. Compare this to IPSec, where IKE on UDP 500 responds to unauthenticated probes with enough metadata to identify the vendor, model, and firmware version.

**Simplicity.** The Linux kernel module is approximately 4,000 lines of code. OpenVPN is roughly 100,000. IPSec (strongSwan) is roughly 500,000. Smaller attack surface, faster audit, fewer bugs.

**Performance.** WireGuard operates in kernel space with zero-copy data paths where possible. Throughput routinely exceeds 1 Gbps on commodity hardware. Handshakes complete in a single round trip (~1 RTT). Roaming is automatic — if a peer's IP address changes (mobile device moves between networks), WireGuard updates the endpoint after the next authenticated packet. No reconnection, no session renegotiation.

### What WireGuard does not handle

WireGuard has no concept of:

- **Discovery.** Peers do not find each other. You must manually configure each peer's public key, allowed IPs, and endpoint address in the WireGuard configuration file on every other peer that needs to talk to it.

- **NAT traversal.** WireGuard sends UDP packets to whatever endpoint address you configured. If that address is behind NAT, WireGuard has no mechanism to punch through it. You need an external STUN server or a relay.

- **Key distribution.** There is no enrollment flow, no certificate authority, no key server. You generate a keypair on each machine, then manually distribute the public keys to every peer that should trust it.

- **Access control.** WireGuard's only access model is the `AllowedIPs` field per peer, which controls what IP ranges a peer is allowed to send from. It is a routing/anti-spoofing mechanism, not a policy engine. There is no concept of "peer A can reach peer B on port 443 but not port 22."

- **Peer lifecycle.** No enrollment, no revocation, no expiry. To remove a peer, you edit the configuration file on every other peer to remove its public key. There is no central authority to push that change.

- **DNS.** WireGuard knows nothing about hostnames or service discovery.

- **Monitoring.** `wg show` gives you current peers, their last handshake, and bytes transferred. That is the extent of the observability.

In a two-node setup, this is fine. You generate two keypairs, exchange public keys, configure endpoints, and you have an encrypted tunnel. The problem arrives at scale. A mesh of N nodes requires N*(N-1)/2 unique tunnel configurations, all manually maintained. Add a node, and you must update every existing node's config. Remove a node, same. Change a key, same. This is the operational problem that WireGuard deliberately ignores and that every WireGuard management layer exists to solve.

## Netbird: WireGuard management done sanely

Netbird is not a separate VPN protocol. It is a management layer that automates the configuration, distribution, and lifecycle of standard WireGuard tunnels. Every byte of mission traffic flows through a normal WireGuard tunnel using normal WireGuard cryptography. Netbird's contribution is getting those tunnels set up and keeping them updated without manual configuration.

### What Netbird adds

**Enrollment.** Netbird's own enrollment is a single command:

```
sudo netbird up --management-url <management-endpoint> --setup-key <KEY>
```

The peer contacts the management server, presents its setup key, receives its WireGuard configuration (assigned IP, peer list, allowed IPs), and joins the mesh. No manual key exchange, no config file editing.

In our deployment an operator never runs that by hand. The peer boots with a signed enrollment bundle, brings up the control-plane tunnel to a relay listed in it, and a validator returns a one-time setup key over that tunnel — so the management endpoint above is a private address on the mesh, never a public URL. The command is the same; where its two arguments come from is the difference.

**Peer discovery and signaling.** The management server maintains the current peer registry. When a new peer enrolls or an existing peer's endpoint changes, the management server pushes the update to all relevant peers. This is the WireGuard configuration file generation that you would otherwise do by hand, automated and distributed in real time.

**NAT traversal (ICE/STUN/TURN).** Netbird implements the ICE protocol to establish direct peer-to-peer connections through NAT. It uses STUN servers to discover public IP/port mappings and falls back to TURN relays when direct connectivity is impossible. The tunnels it establishes are still standard WireGuard — the ICE negotiation is just the mechanism for figuring out where to point the WireGuard endpoint.

**Data relay.** When two peers cannot establish a direct WireGuard tunnel (double NAT, restrictive firewalls, symmetric NAT), Netbird routes their encrypted WireGuard packets through a relay server. The relay is an opaque forwarder — it cannot decrypt the traffic. This is the equivalent of a WireGuard hub-and-spoke relay, automated by the management layer.

**Access control lists.** Netbird distributes ACL policies from the management server to every peer. Policies define which peers (or groups of peers) can communicate, on which ports. Under the hood, these translate to iptables/nftables rules on each peer and to the WireGuard `AllowedIPs` configuration. The enforcement is at the kernel level, not at the management server — the management server distributes the policy, but each peer enforces it locally.

**DNS.** Netbird pushes DNS resolver configuration to peers. A "nameserver group" tells peers to resolve specific domains through specific DNS servers. In our deployment, queries for the mesh zone route over the WireGuard tunnel to the mesh DNS instance. This is what makes service names work without `/etc/hosts` entries.

**Peer groups.** Peers can be organized into groups for policy purposes. Rather than writing a rule per peer, you write a rule per group: "sensors can talk to fusion engines on port 5000." This is the equivalent of firewall zones, implemented as WireGuard configuration management.

### What Netbird does not change

The data plane is pure WireGuard. No proprietary protocol, no additional encryption layer, no traffic inspection. If you capture packets between two Netbird peers, you see standard WireGuard UDP packets indistinguishable from a manually configured WireGuard tunnel.

The management server is not in the data path. Once peers have exchanged their WireGuard configurations, they communicate directly. If the management server goes down, existing tunnels persist indefinitely. New peers cannot enroll, and policy updates cannot propagate, but the mesh continues operating on cached state. This is not a Netbird feature — it is how WireGuard works. Netbird's contribution is not inserting itself into the path in the first place.

The cryptographic properties are WireGuard's properties. The stealth behavior, the cipher suite, the key exchange mechanism, the handshake protocol — all WireGuard. Netbird's management traffic uses standard TLS/gRPC, but that is separate from the data tunnels.

## What is bespoke versus standard

Understanding what is Netbird-specific (and could be replaced) versus what is standard WireGuard (and is universal) matters for risk assessment, vendor independence, and interoperability.

### Standard WireGuard (universal, replaceable management layer)

These properties are intrinsic to WireGuard and remain true regardless of the management layer:

| Property | Standard |
|---|---|
| Peer-to-peer encrypted tunnels | WireGuard kernel module |
| ChaCha20-Poly1305 / AES-256-GCM encryption | WireGuard cryptographic suite |
| Curve25519 key exchange | WireGuard Noise protocol |
| Silent packet drop (stealth) | WireGuard behavior |
| Automatic roaming on endpoint change | WireGuard behavior |
| Kernel-space performance | WireGuard kernel module |
| Cached tunnels survive management outage | WireGuard stateless design |

If we replaced Netbird with Tailscale, Headscale, Nebula, or manual WireGuard configuration, every property above would remain identical. The tunnels are the same tunnels.

### Netbird management layer (replaceable, not unique)

These are Netbird's implementation of standard mesh management functions. Every serious WireGuard management layer provides equivalents:

| Function | Netbird implementation | Tailscale/Headscale equivalent | Nebula equivalent |
|---|---|---|---|
| Enrollment | Setup key + management API | Auth key + coordination server | Certificate signing |
| Peer discovery | Management server push | Coordination server (DERP) | Lighthouse nodes |
| NAT traversal | ICE/STUN/TURN (Coturn) | DERP relay servers | Built-in UDP hole punching |
| Access control | ACL policies via management | ACL tags via coordination | Firewall rules in cert |
| DNS | Nameserver groups | MagicDNS | N/A (use external) |
| Peer groups | Groups in management server | Tags/ACLs | Groups in CA |
| Dashboard | Netbird Dashboard (web UI) | Tailscale admin console | N/A (CLI only) |

The point: Netbird's management functions are not exotic. They are the standard set of problems every WireGuard overlay must solve. The specific implementation differs, but the architecture — centralized management, decentralized data plane — is the same across all of them.

### Netbird-specific characteristics (things to be aware of)

These are areas where Netbird's specific design choices diverge from alternatives in ways that affect operations:

**Self-hosted management server.** Netbird is designed to be self-hosted. The management server, signal server, and dashboard all run in our Docker stack. Tailscale's primary model is SaaS (Tailscale operates the coordination server); Headscale is the self-hosted alternative but is a third-party reimplementation, not Tailscale's own code. Our self-hosted Netbird means we control the management plane end-to-end but also own all the operational burden (availability, backup, upgrades, failover).

**Signal server for peer coordination.** Netbird uses a dedicated signal server for peers to exchange connection offers (ICE candidates, relay assignments) before the WireGuard tunnel is established. This is a WebSocket/gRPC service that peers maintain a persistent connection to. Tailscale uses DERP servers for this function. Nebula does not have a dedicated signal service — lighthouses serve this role. The signal server is a component that must be available for new tunnel establishment but is not in the data path once tunnels are up.

**Embedded IdP.** Netbird can run with an embedded identity provider (no external OAuth/OIDC dependency). Our deployment uses this mode. Tailscale requires an external IdP (Google, Microsoft, Okta, etc.). This is an advantage for disconnected/tactical environments where reaching an external IdP is unreliable or impossible, but it means we manage authentication ourselves.

**Relay protocol.** Netbird's data relay uses a TLS WebSocket transport (`rels://` scheme). This is Netbird-specific — it is not a standard TURN relay. The relay authenticates peers using HMAC tokens derived from a shared `authSecret`. If we switched management layers, we would need to replace the relay infrastructure. The relayed traffic itself is still encrypted WireGuard packets (the relay cannot decrypt them), but the relay transport protocol is Netbird's own.

**gRPC management protocol.** Communication between the Netbird client and the management/signal servers uses gRPC over HTTP/2. This has operational implications: gRPC requires HTTP/2, which means any reverse proxy or tunnel in front of the management server must support it. Standard HTTP-only proxies (some Cloudflare configurations, basic nginx without h2c) will break management traffic. In our deployment, this is why Traefik is configured with explicit `h2c` backend schemes and why rathole (a protocol-blind TCP forwarder) works where Cloudflare Tunnel's HTTP proxy did not.

**Agent-based model.** The Netbird client is an agent (daemon) that maintains persistent connections to the management and signal servers. It manages the local WireGuard interface, applies ACL rules as iptables/nftables rules, and handles DNS configuration. Removing or replacing Netbird requires replacing this agent, not just swapping a config file. The agent creates and manages a `wt0` interface (userspace WireGuard) rather than using the kernel's `wg0` interface directly in most deployments.

**Userspace WireGuard.** Netbird defaults to a userspace WireGuard implementation (`wt0` interface) rather than the kernel module (`wg0`). This simplifies deployment (no kernel module loading, works on more platforms including macOS and Windows without admin kernel extensions) but has a performance cost compared to kernel WireGuard. For our throughput requirements (tactical sensor data, not bulk data transfer), this is not a bottleneck. Be aware of it if throughput requirements change.

**Setup key enrollment model.** Enrollment uses pre-generated setup keys — either one-time-use or reusable. This is simpler than certificate-based enrollment (Nebula) or SSO-gated enrollment (Tailscale) but has different security properties. A leaked reusable setup key allows anyone to enroll. There is no device posture check, no hardware attestation, no MFA at enrollment time. The security of enrollment is exactly as strong as the secrecy of the setup key. See `security-architecture.md` for our enrollment security analysis.

**Management server as single point of failure for state changes.** The management server stores the peer registry, ACL policies, DNS configuration, and setup keys in PostgreSQL. If the management server is permanently lost without backup, all peer configurations continue working (WireGuard tunnels are cached), but no new peers can enroll, no policies can change, and no peer can be revoked. Recovery requires restoring the database. This is architecturally identical to losing an Active Directory domain controller — existing sessions persist, but the control plane is gone. Our mitigation is Postgres streaming replication to a standby.

## Comparison to non-WireGuard ZTNA

Some context on how WireGuard-based meshes (Netbird, Tailscale, Nebula) differ from traditional VPNs and from non-WireGuard zero-trust products (Zscaler, Cloudflare Access, BeyondCorp). For the IPsec comparison specifically — including where IPsec wins and why we deliberately run it at the boundary node — see the IPsec section of [`docs/reference/mesh-technology-comparison.md`](../reference/mesh-technology-comparison.md):

**Kernel-level versus proxy-level.** WireGuard operates at Layer 3 in the kernel. Any IP traffic works — TCP, UDP, ICMP, multicast. Traditional ZTNA (Zscaler Private Access, Cloudflare Access) operates at Layer 7 — they proxy specific application protocols (HTTP, SSH, RDP). This means WireGuard meshes can carry arbitrary protocols (CoT over UDP, gRPC streams, raw sensor feeds) without the ZTNA vendor supporting each protocol explicitly. For tactical systems that speak dozens of specialized protocols, this is the difference between works and doesn't.

**No central data path.** WireGuard traffic goes directly between peers. Traditional VPNs (OpenVPN, Cisco AnyConnect, Palo Alto GlobalProtect) route all traffic through a central concentrator. ZTNA proxies route all traffic through their cloud edge. A WireGuard mesh has no single point that sees all traffic, no bandwidth bottleneck at a hub, and no single node whose failure disconnects everyone. For contested environments where any single node might be destroyed, this is a survival property.

**Offline operation.** A WireGuard mesh with cached peer state operates indefinitely without any cloud service. ZTNA products that authenticate every connection through a cloud policy engine stop working when the cloud is unreachable. For tactical edge deployments behind SATCOM with intermittent connectivity, offline operation is not optional.

**No traffic inspection.** WireGuard is an encrypted tunnel. The management layer does not inspect, log, or filter traffic content. Enterprise ZTNA products typically include DLP, traffic inspection, and logging as core features. This is a tradeoff: we gain privacy and simplicity but lose centralized traffic visibility. For tactical military traffic, centralized inspection by a third-party cloud service is not desirable anyway.

**Identity model.** WireGuard identity is a Curve25519 public key. Period. There is no username, no email address, no device inventory, no posture check built into the protocol. The management layer (Netbird) adds peer names, groups, and policies on top, but the cryptographic identity is just the key. This is simpler and more robust than LDAP/SAML/OIDC-based identity, but it means device identity is only as strong as key management practices.

## Implications for GOAT-Net

**We are not locked into Netbird.** The data plane is standard WireGuard. If Netbird's development stalls, if a better management layer emerges, or if requirements change, we can migrate the management layer without touching the underlying tunnels. The migration cost is in the management and automation layer (Ansible playbooks, Terraform modules, enrollment scripts), not in the mesh itself.

**The management server is a convenience, not a dependency.** During normal operations, the management server handles enrollment, policy distribution, and peer discovery. But the mesh's operational resilience comes from WireGuard's cached-state design, not from the management server's availability. This is why Island Mode works: once peers have their WireGuard configurations, they do not need the management server to communicate.

**Netbird's relay is the one bespoke component to watch.** If P2P fails and peers must relay through the Netbird relay servers, that is Netbird-specific infrastructure. We mitigate this with geographically distributed relays and by ensuring most peers can establish direct P2P tunnels (proper STUN configuration). If we ever migrated away from Netbird, the relay infrastructure would need to be replaced.

**Userspace WireGuard is a known performance ceiling.** If a future requirement demands line-rate WireGuard throughput (bulk classified data transfer, high-bandwidth sensor fusion), we would need to either configure Netbird to use the kernel WireGuard module or bypass Netbird for those specific high-throughput links. This is not an issue at current scale.

**The gRPC management protocol constrains the ingress architecture.** Any proxy, tunnel, or relay in front of the management server must pass HTTP/2 (gRPC) cleanly. This ruled out Cloudflare Tunnel (which rewrites HTTP/2 as HTTP/1.1 internally) and informed the rathole design (protocol-blind TCP forwarding). Changes to the ingress architecture must preserve gRPC passthrough.
