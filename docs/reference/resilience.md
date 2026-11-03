# Mesh Resilience: What Happens When the Server Goes Down

> **60-second summary:** Existing direct P2P tunnels survive a server outage — WireGuard doesn't need a server once peers are connected. But if connections drop while the server is down, peers cannot find each other again until the server returns. Relayed connections (peers behind strict NAT) are less resilient and may require manual client restart after a server restart. Island Mode (Phase 4) addresses this by running a local management/signal server in the field.

---

## Three Scenarios

### 1. Server goes down, connections stay up

**What happens:** Nothing. Traffic keeps flowing.

WireGuard tunnels are point-to-point. Once two peers have exchanged public keys and discovered each other's endpoint (IP:port), the tunnel operates independently. The management server, signal server, and relay are not in the data path. A keepalive packet every 25 seconds maintains NAT mappings.

This is the best case and the most common one for peers on stable connections (wired, static IP, same LAN).

### 2. Server goes down, then a connection drops

**What happens:** The broken connection cannot be re-established until the server comes back.

When a peer changes IP (laptop roams to a new network, Starlink reassigns an IP, 5G handoff), the other peer doesn't know where it went. Normally, the Netbird signal server coordinates this — both peers report their new candidates, signal brokers the introduction, and ICE/STUN punches through NAT. Without the signal server, this process can't happen.

The Netbird client keeps a local cache of peer information and will show stale peers as "Connecting," but it cannot complete the handshake without signal.

**When the server comes back:** Peers reconnect to management and signal, receive updated peer lists, and re-establish tunnels. In practice, this usually works automatically but [may sometimes require a manual client restart][issue-4540] (`netbird down && netbird up`).

### 3. Server goes down, ALL connections go down

**What happens:** The mesh is partitioned. No peer can reach any other peer until the server returns or a local management instance is available.

This is the worst case. Even though each client has cached peer information locally, the Netbird client currently depends on the signal server to coordinate new connections. Without signal, peers that have lost contact cannot find each other again — even if they're on the same LAN.

**This is the gap that Island Mode (Phase 4) fills.** A network host running local management + signal in the field means the mesh can self-heal without reaching the cloud.

---

## What Each Server Component Does

| Component | Role | Impact when down |
|:---|:---|:---|
| **Management** | Peer enrollment, policy distribution, key management | Can't add new peers. Can't change access policy. Existing peers unaffected. |
| **Signal** | Peer-to-peer connection brokering (ICE candidate exchange) | Can't establish *new* connections or re-establish broken ones. Active tunnels unaffected. |
| **Relay** | Fallback traffic forwarding for peers that can't connect directly | Relayed peers lose connectivity. Direct P2P peers unaffected. |
| **STUN** | NAT type discovery and public endpoint detection | Peers behind NAT can't discover their own public endpoint for new connections. |

Management and Signal run on the network host (Docker Compose). STUN (Coturn) and data relay (Netbird relay containers) run locally on each of 3 VPS relays (three notional cloud regions). This means STUN and relay have geographic redundancy — if one VPS goes down, peers can reach the others. Only management/signal are a single point of failure (until Phase 2 warm standby).

### Data flow by scenario

| Scenario | Path | Ports | What must be up |
|---|---|---|---|
| **P2P succeeds** | Peer A ↔ Peer B (WireGuard direct) | UDP 51820 | Nothing — pure P2P |
| **P2P fails** | Peer A → nearest VPS Netbird relay → Peer B | TCP 33073 | Any 1 of 3 VPS relays |
| **Enrollment** | Peer → VPS rathole → network host management | TCP 443 | Any 1 of 3 VPS relays + network host |
| **NAT traversal** | Peer → nearest VPS Coturn (STUN) | UDP 3478 | Any 1 of 3 VPS relays |
| **Signal** | Peer → VPS rathole → network host signal (WebSocket) | TCP 443 | Any 1 of 3 VPS relays + network host |
| **DNS** | Peer → network host dnsmasq (over mesh) | UDP 53 | Network host mesh connectivity |

---

## Known Issues

**Relayed peers don't auto-reconnect after server restart.** When signal and relay services restart, peers that were using the relay (couldn't establish direct P2P) may get stuck in "Connecting" state. The client reconnects to management and relay but fails to re-establish the relay path, attempting ICE instead. Workaround: `netbird down && netbird up` on both peers. ([netbird#4540][issue-4540])

**Client caches management server DNS and doesn't refresh.** If the management server's IP changes (e.g., dynamic IP on the network host), clients continue trying the old IP. Workaround: restart the client, or use a stable DNS name via Cloudflare. ([netbird#5113][issue-5113])

**Peers show stale after extended offline.** A peer that has been offline for a long time may remain in the local peer list as "Connecting" indefinitely. The management server doesn't aggressively prune stale entries. ([netbird#4743][issue-4743])

---

## Resilience by Connection Type

| Scenario | Direct P2P (both peers have stable IPs) | Direct P2P (one peer roams) | Relayed (behind strict NAT) |
|:---|:---|:---|:---|
| **Server down, tunnel active** | Tunnel survives | Tunnel survives until IP changes | Tunnel survives until relay session expires |
| **Server down, tunnel breaks** | Cannot re-establish | Cannot re-establish | Cannot re-establish |
| **Server returns** | Auto-reconnects | Auto-reconnects (usually) | May need manual restart |
| **Server down + Island Mode (Ph4)** | Local signal re-establishes | Local signal re-establishes | Local relay re-establishes |

---

## What This Means for goat

**Phase 1 (current):** The mesh is resilient to short server outages on stable connections. Peers on the same LAN with stable IPs will keep talking through a server restart. Peers that roam or use relay are vulnerable to extended outages. STUN and data relay have geographic redundancy across 3 VPS relays — if one goes down, peers use another. Management/signal on the network host are the remaining SPOF.

**Phase 2 (warm standby):** Postgres 16 is deployed (migrated from SQLite). Next: streaming replication to a local standby network host and a cloud VM. If the active management server fails, either standby can be promoted in minutes: promote the Postgres replica, start the Netbird management service, update DNS. Peers reconnect automatically. STUN and relay already have redundancy via VPS relays — only management enrollment and policy require the failover.

**Phase 4 (Island Mode):** Extends the warm standby into independent operation. The local standby network host promotes itself when it detects the active is unreachable, and operates independently: enrolls new peers locally, serves as local signal/relay, and bridges back to global management when connectivity returns. The difference between Phase 2 and Phase 4 is that Phase 2 is "failover to a standby" while Phase 4 is "operate autonomously in isolation and reconcile later."

**Signal limitation (confirmed 2026-04-13):** A local signal server alone is insufficient for Island Mode. The management server controls which signal URI peers use (`server.signalUri` — a single global value, no per-site assignment), so the local site must also run its own management server to redirect peers to the local signal. There is no signal federation protocol that would allow a local signal to relay to the global one. This confirms the Phase 4 design: full local stack (management + signal + relay), not a partial deployment. See `docs/design/relay-architecture.md` § "Signal server limitations" for the full technical analysis.

This progression — from single server, to warm standby, to island mode — is why Island Mode isn't optional for tactical deployment. Each step reduces the blast radius of losing the active management server.

---

## How to Test

Verify resilience on your own deployment:

```bash
# On the network host (server), stop all Netbird services
ssh <operator>@<network-host-mesh-ip>
cd /opt/netbird && sudo docker compose down

# On the Mac (client), check tunnel status
sudo netbird status
# → Peers should show "Connected" if tunnel was active

# Ping the network host's mesh IP
ping <network-host-mesh-ip>
# → Should work (direct tunnel still up)

# Wait 5 minutes, then restart services
ssh <operator>@<network-host-mesh-ip>
cd /opt/netbird && sudo docker compose up -d

# On the Mac, verify reconnection
sudo netbird status
```

If peers don't auto-reconnect after server restart:

```bash
sudo netbird down && sudo netbird up
```

---

## PACE Enrollment: Joining Without Cloudflare

The scenarios above cover existing peers. But what about a **new device** that has never been on the mesh? It needs to reach the Netbird management server to enroll. If Cloudflare is down and the device is remote, enrollment is impossible through the normal path.

goat uses a PACE (Primary, Alternate, Contingency, Emergency) enrollment plan — four independent paths to management:

| Path | How | Depends on |
|---|---|---|
| **Primary** | VPS relay — 3 VPS relays with DNS round-robin on `netbird.legacy.example`. Rathole forwards TCP 443 to the network host. | Any 1 of 3 VPS relays + internet |
| **Alternate** | Physical LAN — plug in next to the network host, connect to management on LAN IP | Physical presence |
| **Contingency** | Offline enrollment bundle — device ships with a CBOR bundle signed by the offline CA (contains pre-shared WG config + signed ACL capability + 90-day expiry). A validator sidecar on any reachable management host auto-provisions the peer. See [`docs/design/offline-enrollment.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/offline-enrollment.md). | IP connectivity to any known peer |
| **Emergency** | Existing tunnels persist — cannot enroll new devices but mesh keeps running | Existing enrollment |

The enrollment wrapper on each device tries each path in order. The first one that reaches management wins.

**Key design point:** The network host initiates the rathole tunnel to each VPS (outbound), so no port forwarding is needed on the upstream link. The VPS forwards enrollment traffic through the rathole tunnel to the network host. The VPS never sees unencrypted management traffic (rathole uses Noise Protocol encryption on the control channel, and TLS terminates at Traefik on the network host).

**DNS resilience:** Mesh-internal dnsmasq on the network host resolves `netbird.legacy.example` → VPS IPs directly. Enrolled peers don't depend on Cloudflare DNS for re-enrollment or management access.

See Roadmap — Phase 2A: PACE enrollment for implementation details.

---

## Further Reading

- [How NetBird Works](https://docs.netbird.io/about-netbird/how-netbird-works) — architecture overview, role of management/signal/relay
- [Why WireGuard with NetBird](https://docs.netbird.io/about-netbird/why-wireguard-with-netbird) — WireGuard's design properties (silent, stateless, roaming)
- [WireGuard Protocol](https://www.wireguard.com/protocol/) — formal specification of the tunnel protocol
- [WireGuard Roaming](https://github.com/pirate/wireguard-docs) — unofficial docs covering endpoint roaming and persistent keepalive
- [Netbird Troubleshooting](https://docs.netbird.io/help/troubleshooting-client) — client-side diagnostic commands
- [Self-Hosted Troubleshooting](https://docs.netbird.io/selfhosted/troubleshooting) — server-side issues

### Referenced Issues

- [netbird#4540][issue-4540] — Relayed peers don't reconnect after signal/relay restart
- [netbird#5113][issue-5113] — Management DNS cache not auto-refreshing
- [netbird#4743][issue-4743] — Stale peers not pruned from local configuration
- [netbird#1542][issue-1542] — Client cannot reconnect to management/signal after server outage

[issue-4540]: https://github.com/netbirdio/netbird/issues/4540
[issue-5113]: https://github.com/netbirdio/netbird/issues/5113
[issue-4743]: https://github.com/netbirdio/netbird/issues/4743
[issue-1542]: https://github.com/netbirdio/netbird/issues/1542
