# Does a WireGuard mesh keep working when the management server is down?

Yes, for peers that are already connected. In a managed WireGuard mesh (NetBird, Tailscale, Headscale and similar), the management server distributes keys, peer lists and policy. It does not carry traffic. Peers that hold each other's keys and endpoints keep exchanging traffic directly while the management server is unreachable. What stops is every change: a new peer cannot enroll, a policy change does not reach the peers, a peer cannot be revoked, and peers do not learn about a peer whose address changed.

## What works and what does not

| During a management outage | Result |
|---|---|
| Traffic between peers with an established tunnel | Continues |
| Access rules already delivered to a peer | Still enforced, because each peer enforces them locally |
| Enrolling a new peer | Does not work |
| Changing or revoking access | Does not reach the peers until the server returns |
| Peers that reach each other only through a relay | Depends on the relay, which is a separate service from the management server |

If the management server is lost permanently and has no backup, the existing peers keep their tunnels, and the peer registry and policy have to be restored or rebuilt before anything can change again.

## How goat handles it

goat's mesh is WireGuard managed by a self-hosted NetBird. The management server is needed at enrollment; enrolled peers exchange traffic peer to peer, or through a relay when no direct path exists.

- The peer registry and policy are in a Postgres database that is replicated between sites, so a second site holds the state the management server needs.
- A watchdog on each mesh host restarts the NetBird client once when the management server is reachable and the client's count of connected peers stays low after a boot. It is implemented in the `netbird-boot-selfheal` role.
- Enrolling a device while the management server is unreachable, with a signed bundle the device carries, is designed and not built.

## Read more

- [WireGuard and NetBird primer](../design/wireguard-netbird-primer.md): what WireGuard does, what the management layer adds, and what is replaceable
- [Offline enrollment bundles](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/offline-enrollment.md)
- [NetBird boot self-heal](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/netbird-boot-selfheal.md)
- [Mesh technology comparison](../reference/mesh-technology-comparison.md)
